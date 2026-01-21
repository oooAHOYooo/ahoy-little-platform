import os
import json
from decimal import Decimal
from flask import Blueprint, request, jsonify, current_app
import stripe
from db import get_session
from models import Tip, User, WalletTransaction
from datetime import datetime
from decimal import Decimal
from urllib import request as urlrequest
from urllib.error import URLError, HTTPError

bp = Blueprint("stripe_webhooks", __name__, url_prefix="/webhooks")

def _notify_admin(event_type: str, payload: dict) -> None:
    """
    Best-effort admin notification.
    Set ADMIN_NOTIFY_WEBHOOK to a Slack/Discord webhook URL to receive purchase alerts.
    """
    webhook = os.getenv("ADMIN_NOTIFY_WEBHOOK")
    if not webhook:
        return
    try:
        body = json.dumps({"event": event_type, **payload}).encode("utf-8")
        req = urlrequest.Request(
            webhook,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urlrequest.urlopen(req, timeout=5)  # nosec - user-provided webhook URL
    except (URLError, HTTPError, Exception):
        # Never fail the webhook handler because notifications failed.
        return


def _configure_stripe_from_config():
    cfg = getattr(current_app, "config", {})
    api_key = cfg.get("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY_TEST")
    stripe.api_key = api_key


@bp.route("/stripe", methods=["POST"])
def handle_stripe_webhook():
    """
    Stripe webhook endpoint. No auth required.
    Focus on payment_intent.succeeded to record Boost.
    """
    _configure_stripe_from_config()
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    cfg = getattr(current_app, "config", {})
    webhook_secret = cfg.get("STRIPE_WEBHOOK_SECRET") or os.getenv("STRIPE_WEBHOOK_SECRET") or os.getenv("STRIPE_WEBHOOK_SECRET_TEST")

    if not webhook_secret:
        # Fallback: allow in development without verification
        try:
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)  # type: ignore
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    else:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except ValueError:
            return jsonify({"error": "Invalid payload"}), 400
        except stripe.error.SignatureVerificationError:
            return jsonify({"error": "Invalid signature"}), 400

    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]
        metadata = session_data.get("metadata", {}) or {}

        # Handle wallet funding
        if metadata.get("type") == "wallet_fund":
            user_id_str = metadata.get("user_id")
            amount_str = metadata.get("amount")
            
            if user_id_str and amount_str:
                try:
                    user_id = int(user_id_str)
                    amount = Decimal(str(amount_str))
                    
                    with get_session() as db_session:
                        user = db_session.query(User).filter(User.id == user_id).first()
                        if user:
                            balance_before = Decimal(str(user.wallet_balance or 0))
                            balance_after = balance_before + amount
                            user.wallet_balance = balance_after
                            
                            # Create transaction record
                            transaction = WalletTransaction(
                                user_id=user_id,
                                type="fund",
                                amount=amount,
                                balance_before=balance_before,
                                balance_after=balance_after,
                                description=f"Wallet funding via Stripe",
                                reference_id=session_data.get("id"),
                                reference_type="stripe_checkout",
                                created_at=datetime.utcnow(),
                            )
                            db_session.add(transaction)
                            db_session.commit()
                except Exception as e:
                    # Log error but don't fail webhook
                    print(f"Error processing wallet funding: {e}")
            
            return jsonify({"status": "ok"}), 200

        purchase_id = metadata.get("purchase_id")
        purchase_type = (metadata.get("type") or "").strip()

        # Mark Purchase as paid if present
        if purchase_id:
            try:
                from models import Purchase
                with get_session() as db_session:
                    p = db_session.query(Purchase).filter(Purchase.id == int(purchase_id)).first()
                    if p:
                        # Idempotent update
                        if p.status != "paid":
                            p.status = "paid"
                        if not p.stripe_id:
                            p.stripe_id = session_data.get("id")
                        db_session.commit()
                        # Notify admins for non-tip purchases (merch, tickets, etc.)
                        if str(p.type or "").strip() == "merch":
                            _notify_admin("purchase.paid", {
                                "purchase_id": p.id,
                                "type": p.type,
                                "item_id": p.item_id,
                                "qty": p.qty,
                                "amount": p.amount,
                                "total": p.total,
                                "stripe_session": session_data.get("id"),
                            })
            except Exception:
                # Non-fatal for webhook: still allow boost record to proceed if applicable
                pass

        # If this checkout session was a boost/tip, also record it as a Tip ledger entry
        # (idempotent by stripe_checkout_session_id, which is unique)
        if purchase_type in ["boost", "tip"] or metadata.get("boost_amount"):
            artist_id = metadata.get("artist_id")
            boost_amount_str = metadata.get("boost_amount") or metadata.get("amount")
            stripe_fee_str = metadata.get("stripe_fee")
            platform_fee_str = metadata.get("platform_fee")
            total_paid_str = metadata.get("total_paid") or metadata.get("total")
            artist_payout_str = metadata.get("artist_payout") or boost_amount_str
            platform_revenue_str = metadata.get("platform_revenue") or platform_fee_str
            user_id_str = metadata.get("user_id") or ""
            user_id = int(user_id_str) if user_id_str.isdigit() else None

            if all([artist_id, boost_amount_str, platform_fee_str, total_paid_str]):
                try:
                    with get_session() as db_session:
                        existing = db_session.query(Tip).filter(Tip.stripe_checkout_session_id == session_data.get("id")).first()
                        if existing:
                            return jsonify({"status": "ok"}), 200

                        tip_datetime = datetime.utcnow()
                        tip = Tip(
                            user_id=user_id,
                            artist_id=str(artist_id),
                            amount=Decimal(boost_amount_str),
                            fee=Decimal(platform_fee_str),
                            platform_fee=Decimal(platform_fee_str),
                            net_amount=Decimal(artist_payout_str),
                            stripe_fee=Decimal(stripe_fee_str) if stripe_fee_str else Decimal("0.00"),
                            total_paid=Decimal(total_paid_str),
                            artist_payout=Decimal(artist_payout_str),
                            platform_revenue=Decimal(platform_revenue_str) if platform_revenue_str else Decimal(platform_fee_str),
                            stripe_checkout_session_id=session_data.get("id"),
                            stripe_payment_intent_id=session_data.get("payment_intent"),
                            created_at=tip_datetime,
                        )
                        db_session.add(tip)

                        if user_id:
                            from blueprints.payments import update_user_artist_position
                            update_user_artist_position(
                                user_id=user_id,
                                artist_id=str(artist_id),
                                boost_amount=Decimal(boost_amount_str),
                                boost_datetime=tip_datetime,
                                db_session=db_session,
                            )
                        db_session.commit()
                except Exception as e:
                    return jsonify({"error": str(e)}), 500

        return jsonify({"status": "ok"}), 200

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        metadata = intent.get("metadata", {}) or {}

        artist_id = metadata.get("artist_id")
        boost_amount_str = metadata.get("boost_amount")
        stripe_fee_str = metadata.get("stripe_fee")
        platform_fee_str = metadata.get("platform_fee")
        total_paid_str = metadata.get("total_paid")
        artist_payout_str = metadata.get("artist_payout") or boost_amount_str
        platform_revenue_str = metadata.get("platform_revenue") or platform_fee_str
        user_id_str = metadata.get("user_id") or ""
        user_id = int(user_id_str) if user_id_str.isdigit() else None

        if not all([artist_id, boost_amount_str, platform_fee_str, total_paid_str]):
            # Missing metadata; nothing to persist
            return jsonify({"error": "Missing metadata"}), 400

        try:
            with get_session() as db_session:
                # Idempotency by PaymentIntent id
                existing = db_session.query(Tip).filter(Tip.stripe_payment_intent_id == intent.get("id")).first()
                if existing:
                    return jsonify({"status": "ok"}), 200

                tip_datetime = datetime.utcnow()
                tip = Tip(
                    user_id=user_id,
                    artist_id=str(artist_id),
                    amount=Decimal(boost_amount_str),
                    fee=Decimal(platform_fee_str),
                    platform_fee=Decimal(platform_fee_str),
                    net_amount=Decimal(artist_payout_str),
                    stripe_fee=Decimal(stripe_fee_str) if stripe_fee_str else Decimal("0.00"),
                    total_paid=Decimal(total_paid_str),
                    artist_payout=Decimal(artist_payout_str),
                    platform_revenue=Decimal(platform_revenue_str) if platform_revenue_str else Decimal(platform_fee_str),
                    stripe_payment_intent_id=intent.get("id"),
                    created_at=tip_datetime,
                )
                db_session.add(tip)

                if user_id:
                    from blueprints.payments import update_user_artist_position
                    update_user_artist_position(
                        user_id=user_id,
                        artist_id=str(artist_id),
                        boost_amount=Decimal(boost_amount_str),
                        boost_datetime=tip_datetime,
                        db_session=db_session,
                    )
                db_session.commit()
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"}), 200


