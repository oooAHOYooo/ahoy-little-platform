from flask import Blueprint, request, jsonify, session, url_for, current_app
from flask_login import current_user
import os
import json
import stripe
from decimal import Decimal
from datetime import datetime
from db import get_session
from models import Tip, User, UserArtistPosition, WalletTransaction
from services.user_resolver import resolve_db_user_id
import uuid

bp = Blueprint("payments", __name__, url_prefix="/payments")

# CSRF exemption will be set up in app.py after blueprint registration

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
        # Idempotency guard (stripe_checkout_session_id is unique)
        try:
            with get_session() as db_session:
                existing = db_session.query(Tip).filter(Tip.stripe_checkout_session_id == session_data.get("id")).first()
                if existing:
                    return jsonify({"status": "received"}), 200
        except Exception:
            pass
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
                
                # Send email notifications
                try:
                    from services.notifications import notify_boost_received
                    from app import _load_artists_flat
                    from models import User
                    
                    # Get artist name
                    artist_name = None
                    artists = _load_artists_flat()
                    for artist in artists:
                        if (str(artist.get('id', '')) == str(artist_id) or
                            artist.get('slug', '').lower() == str(artist_id).lower() or
                            artist.get('name', '').lower() == str(artist_id).lower()):
                            artist_name = artist.get('name')
                            break
                    
                    # Get tipper email if available
                    tipper_email = None
                    if user_id:
                        user = db_session.query(User).filter(User.id == user_id).first()
                        if user:
                            tipper_email = user.email
                    
                    notify_boost_received(
                        artist_id=str(artist_id),
                        artist_name=artist_name,
                        boost_amount=Decimal(boost_amount_str),
                        artist_payout=Decimal(artist_payout_str),
                        total_paid=Decimal(total_paid_str),
                        tipper_email=tipper_email,
                        stripe_session_id=session_data.get("id")
                    )
                except Exception as notify_error:
                    # Don't fail webhook if notification fails
                    import logging
                    logging.error(f"Failed to send boost notification: {notify_error}", exc_info=True)
                
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
            total_net = sum(float(tip.net_amount) for tip in tips if tip.net_amount)
            total_payout = sum(float(tip.artist_payout) for tip in tips if tip.artist_payout)
            boost_count = len(tips)

            return jsonify({
                "artist_id": artist_id,
                "total_boosts": round(total_amount, 2),
                "total_net": round(total_net, 2),
                "total_payout": round(total_payout, 2),  # Total artist should receive
                "boost_count": boost_count,
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/artist/<artist_id>/earnings", methods=["GET"])
def get_artist_earnings(artist_id):
    """
    Get total earnings for an artist (their payout bucket).
    This shows how much money is owed to the artist.
    """
    try:
        with get_session() as db_session:
            tips = db_session.query(Tip).filter(Tip.artist_id == str(artist_id)).all()
            
            total_payout = sum(float(tip.artist_payout) for tip in tips if tip.artist_payout)
            total_boosts = sum(float(tip.amount) for tip in tips)
            boost_count = len(tips)
            
            # Get recent tips
            recent_tips = sorted(tips, key=lambda t: t.created_at or datetime.min, reverse=True)[:10]
            
            return jsonify({
                "artist_id": artist_id,
                "total_earnings": round(total_payout, 2),  # Total amount artist should receive
                "total_boosted": round(total_boosts, 2),  # Total amount users boosted
                "boost_count": boost_count,
                "recent_tips": [
                    {
                        "id": tip.id,
                        "amount": float(tip.amount),
                        "artist_payout": float(tip.artist_payout) if tip.artist_payout else float(tip.amount),
                        "user_id": tip.user_id,
                        "created_at": tip.created_at.isoformat() if tip.created_at else None,
                    }
                    for tip in recent_tips
                ],
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================
# WALLET SYSTEM
# ==========================================

@bp.route("/wallet", methods=["GET"])
def get_wallet_balance():
    """Get current user's wallet balance."""
    user_id = resolve_db_user_id()
    if not user_id:
        return jsonify({"balance": 0, "balance_cents": 0}), 200

    try:
        with get_session() as db_session:
            user = db_session.query(User).filter(User.id == user_id).first()
            if not user:
                return jsonify({"balance": 0, "balance_cents": 0}), 200
            
            balance = float(user.wallet_balance or 0)
            return jsonify({
                "balance": round(balance, 2),
                "balance_cents": int(balance * 100),
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/wallet/fund", methods=["POST"])
def fund_wallet():
    """Create a Stripe Checkout session to fund the wallet."""
    try:
        if not stripe.api_key:
            import logging
            logging.error("Stripe not configured: stripe.api_key is None or empty")
            return jsonify({"error": "Stripe not configured"}), 500

        user_id = resolve_db_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required. Please log in to fund your wallet."}), 401

        data = request.get_json(silent=True) or {}
        amount = data.get("amount")

        if not amount:
            return jsonify({"error": "Amount required"}), 400
        
        # Log for debugging
        import logging
        logging.debug(f"Wallet funding request: user_id={user_id}, amount={amount}, data={data}")

        try:
            amount_decimal = Decimal(str(amount))
        except (ValueError, TypeError) as e:
            logging.error(f"Invalid amount format: {amount}, error: {e}")
            return jsonify({"error": "Invalid amount"}), 400

        if amount_decimal < 1.00:  # Minimum $1.00 to fund
            return jsonify({"error": "Minimum funding amount is $1.00"}), 400

        if amount_decimal > 1000.00:  # Maximum $1000.00 per transaction
            return jsonify({"error": "Maximum funding amount is $1000.00"}), 400

        # Get user's Stripe customer ID if available (normalized signup process)
        stripe_customer_id = None
        try:
            with get_session() as db_session:
                user = db_session.query(User).filter(User.id == user_id).first()
                if user and user.stripe_customer_id:
                    stripe_customer_id = user.stripe_customer_id
        except Exception as e:
            import logging
            logging.warning(f"Could not retrieve Stripe customer ID: {e}")
            # Non-fatal, continue without customer ID

        try:
            checkout_params = {
                "payment_method_types": ["card"],
                "line_items": [{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Ahoy Wallet Funding",
                            "description": f"Add ${amount_decimal:.2f} to your Ahoy wallet",
                        },
                        "unit_amount": int(amount_decimal * 100),  # Convert to cents
                    },
                    "quantity": 1,
                }],
                "mode": "payment",
                "success_url": request.host_url.rstrip("/") + "/payments/wallet/success?session_id={CHECKOUT_SESSION_ID}",
                "cancel_url": request.host_url.rstrip("/") + "/payments/wallet/cancel",
                "metadata": {
                    "user_id": str(user_id),
                    "type": "wallet_fund",
                    "amount": str(amount_decimal),
                },
            }
            
            # Use Stripe customer ID if available (normalized signup)
            if stripe_customer_id:
                checkout_params["customer"] = stripe_customer_id
            
            checkout_session = stripe.checkout.Session.create(**checkout_params)

            return jsonify({
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id,
            }), 200

        except stripe.error.StripeError as e:
            import logging
            logging.error(f"Stripe error in fund_wallet: {e}", exc_info=True)
            return jsonify({"error": f"Payment processing error: {str(e)}"}), 400
        except Exception as e:
            import logging
            logging.error(f"Unexpected error in fund_wallet: {e}", exc_info=True)
            return jsonify({"error": "An unexpected error occurred. Please try again."}), 500
    except Exception as e:
        import logging
        logging.error(f"Critical error in fund_wallet: {e}", exc_info=True)
        return jsonify({"error": "Server error. Please try again later."}), 500


def deduct_wallet_balance(user_id: int, amount: Decimal, description: str = "Payment", reference_id: str = None, reference_type: str = "payment"):
    """
    Helper function to deduct from wallet balance.
    Returns (success: bool, error: str or None, balance_after: Decimal or None)
    """
    try:
        with get_session() as db_session:
            user = db_session.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "User not found", None

            balance_before = Decimal(str(user.wallet_balance or 0))
            
            if balance_before < amount:
                return False, "Insufficient wallet balance", None

            # Deduct from wallet
            balance_after = balance_before - amount
            user.wallet_balance = balance_after

            # Create transaction record
            transaction = WalletTransaction(
                user_id=user_id,
                type="spend",
                amount=amount,
                balance_before=balance_before,
                balance_after=balance_after,
                description=description,
                reference_id=reference_id,
                reference_type=reference_type,
                created_at=datetime.utcnow(),
            )
            db_session.add(transaction)
            db_session.commit()

            return True, None, balance_after

    except Exception as e:
        return False, str(e), None


@bp.route("/wallet/use", methods=["POST"])
def use_wallet():
    """Use wallet balance for a payment. Returns success if sufficient balance."""
    user_id = resolve_db_user_id()
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    data = request.get_json(silent=True) or {}
    amount = data.get("amount")
    description = data.get("description", "Payment")
    reference_id = data.get("reference_id")
    reference_type = data.get("reference_type", "payment")

    if not amount:
        return jsonify({"error": "Amount required"}), 400

    try:
        amount_decimal = Decimal(str(amount))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400

    if amount_decimal <= 0:
        return jsonify({"error": "Amount must be positive"}), 400

    success, error, balance_after = deduct_wallet_balance(user_id, amount_decimal, description, reference_id, reference_type)
    
    if not success:
        if error == "Insufficient wallet balance":
            with get_session() as db_session:
                user = db_session.query(User).filter(User.id == user_id).first()
                balance = float(user.wallet_balance or 0) if user else 0
            return jsonify({
                "error": error,
                "balance": balance,
                "required": float(amount_decimal),
            }), 400
        return jsonify({"error": error or "Unknown error"}), 500

    return jsonify({
        "success": True,
        "balance_after": float(balance_after),
        "amount_used": float(amount_decimal),
    }), 200


@bp.route("/wallet/transactions", methods=["GET"])
def get_wallet_transactions():
    """Get wallet transaction history for current user (HTML page or JSON API)."""
    from flask import render_template
    
    # Check if this is a JSON API request (explicit format=json or Accept: application/json)
    wants_json = (
        request.args.get('format') == 'json' or
        'application/json' in request.headers.get('Accept', '')
    )
    
    if not wants_json:
        # Render HTML page for browser navigation
        return render_template('wallet_transactions.html')
    
    # Return JSON API response
    user_id = resolve_db_user_id()
    if not user_id:
        return jsonify({"transactions": []}), 200

    try:
        limit = int(request.args.get("limit", 50))
        limit = min(limit, 100)  # Max 100
        offset = int(request.args.get("offset", 0))

        with get_session() as db_session:
            transactions = (
                db_session.query(WalletTransaction)
                .filter(WalletTransaction.user_id == user_id)
                .order_by(WalletTransaction.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )

            return jsonify({
                "transactions": [
                    {
                        "id": t.id,
                        "type": t.type,
                        "amount": float(t.amount),
                        "balance_before": float(t.balance_before),
                        "balance_after": float(t.balance_after),
                        "description": t.description,
                        "reference_id": t.reference_id,
                        "reference_type": t.reference_type,
                        "created_at": t.created_at.isoformat() if t.created_at else None,
                    }
                    for t in transactions
                ],
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/wallet/success")
def wallet_fund_success():
    """Wallet funding success page - polls for balance update and redirects."""
    session_id = request.args.get("session_id")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Wallet Funded - Ahoy Indie Media</title>
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
                max-width: 500px;
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
                margin: 0.5rem 0;
            }}
            a {{
                color: white;
                text-decoration: underline;
            }}
            .status {{
                margin: 1rem 0;
                padding: 0.75rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                min-height: 1.5rem;
            }}
            .spinner {{
                display: inline-block;
                width: 1rem;
                height: 1rem;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-top-color: white;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                margin-right: 0.5rem;
            }}
            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}
            .balance-updated {{
                color: #4ade80;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success-icon">💰</div>
            <h1>Wallet Funded!</h1>
            <p>Your payment was processed successfully.</p>
            <div class="status" id="status">
                <span class="spinner"></span>
                <span id="status-text">Updating your wallet balance...</span>
            </div>
            <p id="balance-display" style="display: none; font-size: 1.25rem; font-weight: 600; margin: 1rem 0;"></p>
            <p id="redirect-message" style="display: none; opacity: 0.8;">Redirecting to your account...</p>
            <p id="manual-links" style="margin-top: 1.5rem;">
                <a href="/account">View My Account</a> | <a href="/">Return to Ahoy</a>
            </p>
        </div>
        <script>
            (function() {{
                let initialBalance = 0;
                let pollCount = 0;
                const maxPolls = 30; // 30 seconds max
                const pollInterval = 1000; // 1 second
                
                async function checkBalance() {{
                    try {{
                        const response = await fetch('/payments/wallet', {{ 
                            credentials: 'include',
                            cache: 'no-store'
                        }});
                        
                        if (response.ok) {{
                            const data = await response.json();
                            const currentBalance = parseFloat(data.balance || 0);
                            
                            // First check - record initial balance
                            if (pollCount === 0) {{
                                initialBalance = currentBalance;
                                // If balance is already > 0 on first check, webhook likely already processed
                                if (currentBalance > 0) {{
                                    // Assume webhook already processed, show success immediately
                                    document.getElementById('status').innerHTML = 
                                        '<span class="balance-updated">✓ Balance updated!</span>';
                                    document.getElementById('status-text').textContent = '';
                                    
                                    const balanceDisplay = document.getElementById('balance-display');
                                    balanceDisplay.textContent = `New Balance: ${{currentBalance.toFixed(2)}}`;
                                    balanceDisplay.style.display = 'block';
                                    
                                    document.getElementById('redirect-message').style.display = 'block';
                                    document.getElementById('manual-links').style.display = 'none';
                                    
                                    setTimeout(() => {{
                                        window.location.href = '/account?wallet_funded=true';
                                    }}, 2000);
                                    
                                    return true; // Stop polling
                                }}
                            }}
                            
                            // Check if balance increased (webhook processed)
                            if (currentBalance > initialBalance) {{
                                const addedAmount = currentBalance - initialBalance;
                                document.getElementById('status').innerHTML = 
                                    '<span class="balance-updated">✓ Balance updated!</span>';
                                document.getElementById('status-text').textContent = '';
                                
                                const balanceDisplay = document.getElementById('balance-display');
                                balanceDisplay.textContent = `New Balance: ${{currentBalance.toFixed(2)}}`;
                                balanceDisplay.style.display = 'block';
                                
                                document.getElementById('redirect-message').style.display = 'block';
                                document.getElementById('manual-links').style.display = 'none';
                                
                                // Redirect to account page after 2 seconds with flag to refresh
                                setTimeout(() => {{
                                    window.location.href = '/account?wallet_funded=true';
                                }}, 2000);
                                
                                return true; // Stop polling
                            }}
                            
                            pollCount++;
                            
                            // Update status message
                            if (pollCount < maxPolls) {{
                                document.getElementById('status-text').textContent = 
                                    `Checking balance... ({{pollCount}}/{{maxPolls}})`;
                                setTimeout(checkBalance, pollInterval);
                            }} else {{
                                // Timeout - webhook might be delayed
                                document.getElementById('status').innerHTML = 
                                    '<span>⚠ Balance update may be delayed. Please check your account.</span>';
                                document.getElementById('status-text').textContent = 
                                    'If your balance doesn\'t update within a few minutes, please contact support.';
                            }}
                        }} else {{
                            throw new Error('Failed to fetch balance');
                        }}
                    }} catch (error) {{
                        console.error('Error checking balance:', error);
                        pollCount++;
                        
                        if (pollCount < maxPolls) {{
                            document.getElementById('status-text').textContent = 
                                `Retrying... ({{pollCount}}/{{maxPolls}})`;
                            setTimeout(checkBalance, pollInterval);
                        }} else {{
                            document.getElementById('status').innerHTML = 
                                '<span>⚠ Unable to verify balance. Please check your account.</span>';
                        }}
                    }}
                }}
                
                // Start checking balance immediately
                checkBalance();
                
                // Close window if opened in popup
                if (window.opener) {{
                    setTimeout(() => window.close(), 5000);
                }}
            }})();
        </script>
    </body>
    </html>
    """


@bp.route("/wallet/cancel")
def wallet_fund_cancel():
    """Wallet funding cancellation page."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Funding Cancelled - Ahoy Indie Media</title>
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
            <h1>Funding Cancelled</h1>
            <p>Your wallet funding was cancelled.</p>
            <p><a href="/account">Return to Account</a> | <a href="/">Return to Ahoy</a></p>
        </div>
    </body>
    </html>
    """

