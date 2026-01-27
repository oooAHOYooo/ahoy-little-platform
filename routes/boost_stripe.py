import os
from decimal import Decimal
from flask import Blueprint, jsonify, request, current_app
import stripe
from db import get_session
from models import Tip
from datetime import datetime
from services.user_resolver import resolve_db_user_id
from utils.fees import calculate_boost_fees

bp = Blueprint("boost_stripe", __name__, url_prefix="/api/boost/stripe")
# Back-compat/alias blueprint to expose /api/boost/confirm as requested
boost_api_bp = Blueprint("boost_api", __name__, url_prefix="/api/boost")


def _configure_stripe_from_config():
    # Prefer Flask config if set, else environment variables
    cfg = getattr(current_app, "config", {})
    api_key = cfg.get("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY_TEST")
    stripe.api_key = api_key


@bp.route("/create-intent", methods=["POST"])
def create_payment_intent():
    """
    Create a Stripe PaymentIntent for an artist boost.
    Body:
    {
      "artist_id": string,
      "boost_amount": number (dollars)
    }
    """
    _configure_stripe_from_config()
    if not stripe.api_key:
        return jsonify({"error": "Stripe not configured"}), 500

    data = request.get_json(silent=True) or {}
    artist_id = data.get("artist_id")
    boost_amount = data.get("boost_amount") or data.get("amount")

    if not artist_id:
        return jsonify({"error": "artist_id required"}), 400

    try:
        boost_amount_decimal = Decimal(str(boost_amount))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid boost amount"}), 400

    if boost_amount_decimal < Decimal("0.50"):
        return jsonify({"error": "Minimum boost amount is $0.50"}), 400

    # Resolve user if logged in (optional)
    user_id = resolve_db_user_id()

    # Calculate fee breakdown (for metadata or post-processing)
    stripe_fee, platform_fee, total_charge, artist_payout, platform_revenue = calculate_boost_fees(boost_amount_decimal)

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(boost_amount_decimal * 100),  # cents
            currency="usd",
            automatic_payment_methods={"enabled": True},
            metadata={
                "artist_id": str(artist_id),
                "user_id": str(user_id or ""),
                "boost_amount": str(boost_amount_decimal),
                "stripe_fee": str(stripe_fee),
                "platform_fee": str(platform_fee),
                "total_paid": str(total_charge),
                "artist_payout": str(artist_payout),
                "platform_revenue": str(platform_revenue),
            },
        )
        return jsonify({"client_secret": intent.client_secret}), 200
    except stripe.error.StripeError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/confirm", methods=["POST"])
def confirm_boost_record():
    """
    Optional: Client can call after successful payment to ensure ledger is updated.
    Body: { "payment_intent_id": string }
    This endpoint is idempotent; if a record already exists, it returns success.
    """
    _configure_stripe_from_config()
    if not stripe.api_key:
        return jsonify({"error": "Stripe not configured"}), 500

    data = request.get_json(silent=True) or {}
    payment_intent_id = data.get("payment_intent_id")
    if not payment_intent_id:
        return jsonify({"error": "payment_intent_id required"}), 400

    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.status != "succeeded":
            return jsonify({"error": "Payment not succeeded"}), 400

        metadata = intent.metadata or {}
        artist_id = metadata.get("artist_id")
        boost_amount_str = metadata.get("boost_amount")
        stripe_fee_str = metadata.get("stripe_fee")
        platform_fee_str = metadata.get("platform_fee")
        total_paid_str = metadata.get("total_paid")
        artist_payout_str = metadata.get("artist_payout")
        platform_revenue_str = metadata.get("platform_revenue") or platform_fee_str
        user_id_str = metadata.get("user_id") or ""
        user_id = int(user_id_str) if user_id_str.isdigit() else None

        if not all([artist_id, boost_amount_str, platform_fee_str, total_paid_str]):
            return jsonify({"error": "Missing metadata to record boost"}), 400

        with get_session() as db_session:
            # Idempotency: if we already recorded this PI, return success
            existing = db_session.query(Tip).filter(Tip.stripe_payment_intent_id == payment_intent_id).first()
            if existing:
                return jsonify({"status": "ok", "recorded": True}), 200

            tip_datetime = datetime.utcnow()
            tip = Tip(
                user_id=user_id,
                artist_id=str(artist_id),
                amount=Decimal(boost_amount_str),
                fee=Decimal(platform_fee_str),
                platform_fee=Decimal(platform_fee_str),
                net_amount=Decimal(artist_payout_str) if artist_payout_str else Decimal(boost_amount_str),
                stripe_fee=Decimal(stripe_fee_str) if stripe_fee_str else Decimal("0.00"),
                total_paid=Decimal(total_paid_str),
                artist_payout=Decimal(artist_payout_str) if artist_payout_str else Decimal(boost_amount_str),
                platform_revenue=Decimal(platform_revenue_str) if platform_revenue_str else Decimal(platform_fee_str),
                stripe_payment_intent_id=payment_intent_id,
                created_at=tip_datetime,
            )
            db_session.add(tip)
            if user_id:
                # Update portfolio position
                from blueprints.payments import update_user_artist_position
                update_user_artist_position(
                    user_id=user_id,
                    artist_id=str(artist_id),
                    boost_amount=Decimal(boost_amount_str),
                    boost_datetime=tip_datetime,
                    db_session=db_session,
                )
            db_session.commit()

        return jsonify({"status": "ok", "recorded": True}), 200
    except stripe.error.StripeError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Alias route: /api/boost/confirm
@boost_api_bp.route("/confirm", methods=["POST"])
def confirm_boost_record_alias():
    return confirm_boost_record()

