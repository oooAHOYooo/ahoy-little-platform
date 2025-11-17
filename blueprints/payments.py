from flask import Blueprint, request, jsonify, session, url_for
from flask_login import current_user
import os
import json
import stripe
from decimal import Decimal
from datetime import datetime
from db import get_session
from models import Tip, User, UserArtistPosition
from services.user_resolver import resolve_db_user_id

bp = Blueprint("payments", __name__, url_prefix="/payments")

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

# Platform fee percentage (7.5%)
PLATFORM_FEE_PERCENT = Decimal("0.075")


def calculate_fee_and_net(amount: Decimal):
    """Calculate platform fee (7.5%) and net amount after fee."""
    fee = amount * PLATFORM_FEE_PERCENT
    net = amount - fee
    return fee, net


def update_user_artist_position(user_id: int, artist_id: str, tip_amount: Decimal, tip_datetime: datetime, db_session):
    """
    Update or create a user's position for an artist after a tip.
    
    Args:
        user_id: The user ID who made the tip
        artist_id: The artist ID/slug
        tip_amount: The tip amount
        tip_datetime: When the tip was made
        db_session: Database session
    """
    if not user_id:
        return  # Skip for guest tips
    
    # Get or create position
    position = db_session.query(UserArtistPosition).filter(
        UserArtistPosition.user_id == user_id,
        UserArtistPosition.artist_id == str(artist_id)
    ).first()
    
    if position:
        # Update existing position
        position.total_contributed += tip_amount
        position.last_tip = tip_datetime
        position.updated_at = datetime.utcnow()
    else:
        # Create new position
        position = UserArtistPosition(
            user_id=user_id,
            artist_id=str(artist_id),
            total_contributed=tip_amount,
            last_tip=tip_datetime,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(position)
    
    db_session.flush()  # Flush to ensure position is saved


@bp.route("/tip-session", methods=["POST"])
def create_tip_session():
    """Create a Stripe Checkout session for tipping an artist."""
    if not stripe.api_key:
        return jsonify({"error": "Stripe not configured"}), 500

    data = request.get_json(silent=True) or {}
    artist_id = data.get("artist_id")
    amount = data.get("amount")

    if not artist_id:
        return jsonify({"error": "artist_id required"}), 400

    try:
        amount_decimal = Decimal(str(amount))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400

    if amount_decimal < 0.50:  # Stripe minimum
        return jsonify({"error": "Minimum tip amount is $0.50"}), 400

    # Get user ID if logged in
    user_id = resolve_db_user_id()

    # Calculate fee and net
    fee, net = calculate_fee_and_net(amount_decimal)

    # Create Stripe Checkout Session
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Tip to Artist",
                            "description": f"Support this artist (Ahoy takes 7.5% platform fee)",
                        },
                        "unit_amount": int(amount_decimal * 100),  # Convert to cents
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=request.host_url.rstrip("/") + "/payments/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.host_url.rstrip("/") + "/payments/cancel",
            metadata={
                "artist_id": str(artist_id),
                "user_id": str(user_id) if user_id else "",
                "amount": str(amount_decimal),
                "fee": str(fee),
                "net_amount": str(net),
            },
        )

        return jsonify({
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
        }), 200

    except stripe.error.StripeError as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events."""
    if not stripe.api_key:
        return jsonify({"error": "Stripe not configured"}), 500

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not webhook_secret:
        # In development, skip signature verification
        # In production, you MUST set STRIPE_WEBHOOK_SECRET
        print("⚠️  STRIPE_WEBHOOK_SECRET not set - skipping signature verification")
        try:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    else:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            return jsonify({"error": "Invalid payload"}), 400
        except stripe.error.SignatureVerificationError:
            return jsonify({"error": "Invalid signature"}), 400

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]
        metadata = session_data.get("metadata", {})

        artist_id = metadata.get("artist_id")
        user_id_str = metadata.get("user_id")
        amount_str = metadata.get("amount")
        fee_str = metadata.get("fee")
        net_amount_str = metadata.get("net_amount")

        if not all([artist_id, amount_str, fee_str, net_amount_str]):
            print(f"⚠️  Missing metadata in webhook: {metadata}")
            return jsonify({"error": "Missing metadata"}), 400

        # Parse user_id (may be empty for guest tips)
        user_id = int(user_id_str) if user_id_str and user_id_str.isdigit() else None

        # Create Tip record and update position
        try:
            with get_session() as db_session:
                tip_datetime = datetime.utcnow()
                tip = Tip(
                    user_id=user_id,
                    artist_id=str(artist_id),
                    amount=Decimal(amount_str),
                    fee=Decimal(fee_str),
                    platform_fee=Decimal(fee_str),  # Set platform_fee
                    net_amount=Decimal(net_amount_str),
                    stripe_checkout_session_id=session_data.get("id"),
                    stripe_payment_intent_id=session_data.get("payment_intent"),
                    created_at=tip_datetime,
                )
                db_session.add(tip)
                
                # Update or create user artist position
                if user_id:
                    update_user_artist_position(
                        user_id=user_id,
                        artist_id=str(artist_id),
                        tip_amount=Decimal(amount_str),
                        tip_datetime=tip_datetime,
                        db_session=db_session
                    )
                
                db_session.commit()

                print(f"✅ Tip recorded: ${amount_str} to artist {artist_id} (net: ${net_amount_str})")
                return jsonify({"status": "success"}), 200

        except Exception as e:
            print(f"❌ Error recording tip: {e}")
            return jsonify({"error": str(e)}), 500

    elif event["type"] == "payment_intent.succeeded":
        # Additional handling if needed
        pass

    return jsonify({"status": "received"}), 200


@bp.route("/success")
def payment_success():
    """Payment success page."""
    session_id = request.args.get("session_id")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Successful - Ahoy Indie Media</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .container {{
                text-align: center;
                padding: 2rem;
            }}
            .success-icon {{
                font-size: 4rem;
                margin-bottom: 1rem;
            }}
            h1 {{
                margin: 0.5rem 0;
            }}
            p {{
                opacity: 0.9;
            }}
            a {{
                color: white;
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success-icon">✅</div>
            <h1>Thank You!</h1>
            <p>Your tip was processed successfully.</p>
            <p><a href="/">Return to Ahoy</a></p>
        </div>
        <script>
            // Close window if opened in popup
            if (window.opener) {{
                setTimeout(() => window.close(), 2000);
            }}
        </script>
    </body>
    </html>
    """


@bp.route("/cancel")
def payment_cancel():
    """Payment cancellation page."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Cancelled - Ahoy Indie Media</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: #f3f4f6;
            }}
            .container {{
                text-align: center;
                padding: 2rem;
            }}
            a {{
                color: #667eea;
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Payment Cancelled</h1>
            <p>Your payment was cancelled.</p>
            <p><a href="/">Return to Ahoy</a></p>
        </div>
    </body>
    </html>
    """


@bp.route("/user/total-tips", methods=["GET"])
def get_user_total_tips():
    """Get total amount a user has tipped (for supporter badge eligibility)."""
    user_id = resolve_db_user_id()
    if not user_id:
        return jsonify({"total_tips": 0, "is_supporter": False}), 200

    try:
        with get_session() as db_session:
            tips = db_session.query(Tip).filter(Tip.user_id == user_id).all()
            total = sum(float(tip.amount) for tip in tips)
            is_supporter = total >= 10.0

            return jsonify({
                "total_tips": round(total, 2),
                "is_supporter": is_supporter,
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/artist/<artist_id>/tips", methods=["GET"])
def get_artist_tips(artist_id):
    """Get tip statistics for an artist."""
    try:
        with get_session() as db_session:
            tips = db_session.query(Tip).filter(Tip.artist_id == str(artist_id)).all()
            total_amount = sum(float(tip.amount) for tip in tips)
            total_net = sum(float(tip.net_amount) for tip in tips)
            tip_count = len(tips)

            return jsonify({
                "artist_id": artist_id,
                "total_tips": round(total_amount, 2),
                "total_net": round(total_net, 2),
                "tip_count": tip_count,
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

