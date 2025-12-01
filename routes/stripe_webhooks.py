import os
import json
from decimal import Decimal
from flask import Blueprint, request, jsonify, current_app
import stripe
from db import get_session
from models import Tip
from datetime import datetime

bp = Blueprint("stripe_webhooks", __name__, url_prefix="/webhooks")


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


