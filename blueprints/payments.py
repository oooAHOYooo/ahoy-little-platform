from flask import Blueprint, request, jsonify, session, url_for, current_app
from flask_login import current_user
import os
import json
import stripe
from decimal import Decimal
from datetime import datetime
from db import get_session
from models import Tip, User, UserArtistPosition
from services.user_resolver import resolve_db_user_id
import uuid

bp = Blueprint("payments", __name__, url_prefix="/payments")

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

# ==========================================
# BOOSTING SYSTEM - FEE CALCULATION
# New Logic: Artist receives 100% of boostAmount
# Tipper pays: boostAmount + stripeFee + platformFee
# ==========================================

# Fee Constants
PLATFORM_FEE_PERCENT = Decimal("0.075")  # 7.5%
STRIPE_PERCENTAGE = Decimal("0.029")     # 2.9%
STRIPE_FIXED = Decimal("0.30")           # $0.30


def calculate_boost_fees(boost_amount: Decimal):
    """
    Calculate all fees for a boost.
    
    New Logic:
    - Artist receives 100% of boostAmount
    - Tipper pays: boostAmount + stripeFee + platformFee
    
    Returns:
        tuple: (stripe_fee, platform_fee, total_charge, artist_payout, platform_revenue)
    """
    # Round boost amount to 2 decimals
    boost_amount = round(boost_amount, 2)
    
    # Calculate Stripe fee: (boostAmount * 2.9%) + $0.30
    stripe_fee = round((boost_amount * STRIPE_PERCENTAGE) + STRIPE_FIXED, 2)
    
    # Calculate platform fee: boostAmount * 7.5%
    platform_fee = round(boost_amount * PLATFORM_FEE_PERCENT, 2)
    
    # Total charge to tipper
    total_charge = round(boost_amount + stripe_fee + platform_fee, 2)
    
    # Artist receives 100% of boost amount
    artist_payout = boost_amount
    
    # Platform revenue is the platform fee
    platform_revenue = platform_fee
    
    return stripe_fee, platform_fee, total_charge, artist_payout, platform_revenue


# Legacy function for backward compatibility
def calculate_fee_and_net(amount: Decimal):
    """Legacy: Calculate platform fee (7.5%) and net amount after fee."""
    fee = amount * PLATFORM_FEE_PERCENT
    net = amount - fee
    return fee, net


def update_user_artist_position(user_id: int, artist_id: str, boost_amount: Decimal, boost_datetime: datetime, db_session):
    """
    Update or create a user's position for an artist after a boost.
    
    Args:
        user_id: The user ID who made the boost
        artist_id: The artist ID/slug
        boost_amount: The boost amount
        boost_datetime: When the boost was made
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
        position.total_contributed += boost_amount
        position.last_tip = boost_datetime
        position.updated_at = datetime.utcnow()
    else:
        # Create new position
        position = UserArtistPosition(
            user_id=user_id,
            artist_id=str(artist_id),
            total_contributed=boost_amount,
            last_tip=boost_datetime,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(position)
    
    db_session.flush()  # Flush to ensure position is saved


@bp.route("/boost-session", methods=["POST"])
def create_boost_session():
    """
    Create a Stripe Checkout session for boosting an artist.
    
    New Logic:
    - Artist receives 100% of boostAmount
    - Tipper pays: boostAmount + stripeFee + platformFee
    - Stripe Checkout shows 3 line items
    """
    if not stripe.api_key:
        return jsonify({"error": "Stripe not configured"}), 500

    data = request.get_json(silent=True) or {}
    artist_id = data.get("artist_id")
    boost_amount = data.get("boost_amount") or data.get("amount")  # Support both field names

    if not artist_id:
        return jsonify({"error": "artist_id required"}), 400

    try:
        boost_amount_decimal = Decimal(str(boost_amount))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid boost amount"}), 400

    if boost_amount_decimal < 0.50:  # Stripe minimum
        return jsonify({"error": "Minimum boost amount is $0.50"}), 400

    # Get user ID if logged in
    user_id = resolve_db_user_id()

    # Calculate all fees
    stripe_fee, platform_fee, total_charge, artist_payout, platform_revenue = calculate_boost_fees(boost_amount_decimal)

    # Create Stripe Checkout Session with 3 line items
    try:
        # Mock mode for development/preview
        if stripe.api_key and "placeholder" in stripe.api_key:
            import uuid
            mock_id = f"cs_test_{uuid.uuid4()}"
            return jsonify({
                "checkout_url": f"{request.host_url.rstrip('/')}/payments/success?session_id={mock_id}&mock=true&artist_id={artist_id}&amount={boost_amount_decimal}&user_id={user_id or ''}",
                "session_id": mock_id,
                "breakdown": {
                    "boost_amount": float(boost_amount_decimal),
                    "stripe_fee": float(stripe_fee),
                    "platform_fee": float(platform_fee),
                    "total_charge": float(total_charge),
                }
            }), 200

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Boost Amount",
                            "description": "100% goes directly to the artist",
                        },
                        "unit_amount": int(boost_amount_decimal * 100),  # Convert to cents
                    },
                    "quantity": 1,
                },
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Stripe Processing Fee",
                            "description": "2.9% + $0.30",
                        },
                        "unit_amount": int(stripe_fee * 100),
                    },
                    "quantity": 1,
                },
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Ahoy Indie Media Platform Fee",
                            "description": "7.5% platform fee",
                        },
                        "unit_amount": int(platform_fee * 100),
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
                "boost_amount": str(boost_amount_decimal),
                "stripe_fee": str(stripe_fee),
                "platform_fee": str(platform_fee),
                "total_paid": str(total_charge),
                "artist_payout": str(artist_payout),
                "platform_revenue": str(platform_revenue),
            },
        )

        return jsonify({
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
            "breakdown": {
                "boost_amount": float(boost_amount_decimal),
                "stripe_fee": float(stripe_fee),
                "platform_fee": float(platform_fee),
                "total_charge": float(total_charge),
            }
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
        
        # New metadata fields
        boost_amount_str = metadata.get("boost_amount") or metadata.get("amount")
        stripe_fee_str = metadata.get("stripe_fee")
        platform_fee_str = metadata.get("platform_fee")
        total_paid_str = metadata.get("total_paid")
        artist_payout_str = metadata.get("artist_payout")
        platform_revenue_str = metadata.get("platform_revenue")
        
        # Legacy fallback for old tips
        if not boost_amount_str:
            amount_str = metadata.get("amount")
            fee_str = metadata.get("fee")
            net_amount_str = metadata.get("net_amount")
            if amount_str and fee_str and net_amount_str:
                boost_amount_str = amount_str
                stripe_fee_str = "0.00"
                platform_fee_str = fee_str
                total_paid_str = amount_str
                artist_payout_str = net_amount_str
                platform_revenue_str = fee_str

        if not all([artist_id, boost_amount_str, stripe_fee_str, platform_fee_str, total_paid_str]):
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
                    amount=Decimal(boost_amount_str),  # This is the boost amount (artist receives 100%)
                    fee=Decimal(platform_fee_str),  # Legacy: platform fee
                    platform_fee=Decimal(platform_fee_str),
                    net_amount=Decimal(artist_payout_str),  # Artist receives 100% of tip
                    stripe_fee=Decimal(stripe_fee_str) if stripe_fee_str else Decimal("0.00"),
                    total_paid=Decimal(total_paid_str),
                    artist_payout=Decimal(artist_payout_str),
                    platform_revenue=Decimal(platform_revenue_str) if platform_revenue_str else Decimal(platform_fee_str),
                    stripe_checkout_session_id=session_data.get("id"),
                    stripe_payment_intent_id=session_data.get("payment_intent"),
                    created_at=tip_datetime,
                )
                db_session.add(tip)
                
                # Update or create user artist position (use boost_amount, not net)
                if user_id:
                    update_user_artist_position(
                        user_id=user_id,
                        artist_id=str(artist_id),
                        boost_amount=Decimal(boost_amount_str),  # Full boost amount
                        boost_datetime=tip_datetime,
                        db_session=db_session
                    )
                
                db_session.commit()

                print(f"✅ Boost recorded: ${boost_amount_str} to artist {artist_id} (artist receives: ${artist_payout_str}, total paid: ${total_paid_str})")
                return jsonify({"status": "success"}), 200

        except Exception as e:
            print(f"❌ Error recording boost: {e}")
            return jsonify({"error": str(e)}), 500

    elif event["type"] == "payment_intent.succeeded":
        # Additional handling if needed
        pass

    return jsonify({"status": "received"}), 200


@bp.route("/success")
def payment_success():
    """Payment success page."""
    session_id = request.args.get("session_id")
    is_mock = request.args.get("mock") == "true"
    
    if is_mock:
        # In mock mode, record the boost directly since there's no webhook
        try:
            artist_id = request.args.get("artist_id")
            amount_str = request.args.get("amount")
            user_id_str = request.args.get("user_id")
            user_id = int(user_id_str) if user_id_str else None
            
            if artist_id and amount_str:
                from datetime import datetime
                from models import Tip
                from blueprints.payments import update_user_artist_position
                
                boost_amount = Decimal(amount_str)
                stripe_fee, platform_fee, total_charge, artist_payout, platform_revenue = calculate_boost_fees(boost_amount)
                
                with get_session() as db_session:
                    # Check if already recorded (simple check by session_id)
                    existing = db_session.query(Tip).filter(Tip.stripe_checkout_session_id == session_id).first()
                    if not existing:
                        tip = Tip(
                            user_id=user_id,
                            artist_id=str(artist_id),
                            amount=boost_amount,
                            platform_fee=platform_fee,
                            stripe_fee=stripe_fee,
                            total_paid=total_charge,
                            artist_payout=artist_payout,
                            platform_revenue=platform_revenue,
                            stripe_checkout_session_id=session_id,
                            stripe_payment_intent_id=f"pi_mock_{session_id}",
                            created_at=datetime.utcnow(),
                        )
                        db_session.add(tip)
                        
                        if user_id:
                            update_user_artist_position(
                                user_id=user_id,
                                artist_id=str(artist_id),
                                boost_amount=boost_amount,
                                boost_datetime=datetime.utcnow(),
                                db_session=db_session
                            )
                        db_session.commit()
        except Exception:
            pass
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
            <p>Your boost was processed successfully.</p>
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



@bp.route("/user/total-boosts", methods=["GET"])
def get_user_total_boosts():
    """Get total amount a user has boosted (for supporter badge eligibility)."""
    user_id = resolve_db_user_id()
    if not user_id:
        return jsonify({"total_boosts": 0, "is_supporter": False}), 200

    try:
        with get_session() as db_session:
            tips = db_session.query(Tip).filter(Tip.user_id == user_id).all()
            total = sum(float(tip.amount) for tip in tips)
            is_supporter = total >= 10.0

            return jsonify({
                "total_boosts": round(total, 2),
                "is_supporter": is_supporter,
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/artist/<artist_id>/boosts", methods=["GET"])
def get_artist_boosts(artist_id):
    """Get boost statistics for an artist."""
    try:
        with get_session() as db_session:
            tips = db_session.query(Tip).filter(Tip.artist_id == str(artist_id)).all()
            total_amount = sum(float(tip.amount) for tip in tips)
            total_net = sum(float(tip.net_amount) for tip in tips)
            boost_count = len(tips)

            return jsonify({
                "artist_id": artist_id,
                "total_boosts": round(total_amount, 2),
                "total_net": round(total_net, 2),
                "boost_count": boost_count,
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

