# Add after existing debug/health routes, around line 3800+

@app.route('/ops/debug/payments', methods=['GET'])
def debug_payments():
    """Debug endpoint for payment system status"""
    from flask_login import current_user
    from db import get_session
    from models import User, WalletTransaction, Purchase, Tip
    import stripe
    
    debug_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "stripe": {},
        "database": {},
        "user": {},
        "errors": []
    }
    
    # Check Stripe configuration
    try:
        stripe_key = app.config.get("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY_TEST")
        debug_info["stripe"]["configured"] = bool(stripe_key)
        debug_info["stripe"]["key_prefix"] = stripe_key[:7] + "..." if stripe_key else None
        debug_info["stripe"]["webhook_secret_set"] = bool(app.config.get("STRIPE_WEBHOOK_SECRET") or os.getenv("STRIPE_WEBHOOK_SECRET") or os.getenv("STRIPE_WEBHOOK_SECRET_TEST"))
        
        # Test Stripe API connection
        if stripe_key:
            try:
                stripe.api_key = stripe_key
                # Try to list customers (lightweight operation)
                customers = stripe.Customer.list(limit=1)
                debug_info["stripe"]["api_connection"] = "ok"
                debug_info["stripe"]["api_version"] = stripe.api_version if hasattr(stripe, 'api_version') else "unknown"
            except Exception as e:
                debug_info["stripe"]["api_connection"] = "error"
                debug_info["stripe"]["api_error"] = str(e)
                debug_info["errors"].append(f"Stripe API error: {e}")
        else:
            debug_info["stripe"]["api_connection"] = "not_configured"
            debug_info["errors"].append("Stripe secret key not configured")
    except Exception as e:
        debug_info["stripe"]["error"] = str(e)
        debug_info["errors"].append(f"Stripe check error: {e}")
    
    # Check database connectivity and wallet tables
    try:
        with get_session() as s:
            # Check if wallet_balance column exists
            from sqlalchemy import inspect
            inspector = inspect(s.bind)
            users_columns = [col['name'] for col in inspector.get_columns('users')]
            debug_info["database"]["wallet_balance_column"] = 'wallet_balance' in users_columns
            
            # Check if wallet_transactions table exists
            tables = inspector.get_table_names()
            debug_info["database"]["wallet_transactions_table"] = 'wallet_transactions' in tables
            
            # Get counts
            user_count = s.query(User).count()
            wallet_tx_count = s.query(WalletTransaction).count() if 'wallet_transactions' in tables else 0
            purchase_count = s.query(Purchase).count()
            tip_count = s.query(Tip).count()
            
            debug_info["database"]["counts"] = {
                "users": user_count,
                "wallet_transactions": wallet_tx_count,
                "purchases": purchase_count,
                "tips": tip_count
            }
            
            # Check current user's wallet if logged in
            if current_user.is_authenticated:
                user = s.query(User).filter(User.id == current_user.id).first()
                if user:
                    debug_info["user"]["logged_in"] = True
                    debug_info["user"]["user_id"] = user.id
                    debug_info["user"]["wallet_balance"] = float(user.wallet_balance or 0)
                    debug_info["user"]["stripe_customer_id"] = user.stripe_customer_id or None
                    
                    # Get recent wallet transactions
                    if 'wallet_transactions' in tables:
                        recent_tx = s.query(WalletTransaction).filter(
                            WalletTransaction.user_id == user.id
                        ).order_by(WalletTransaction.created_at.desc()).limit(5).all()
                        debug_info["user"]["recent_transactions"] = [
                            {
                                "type": tx.type,
                                "amount": float(tx.amount),
                                "balance_after": float(tx.balance_after),
                                "description": tx.description,
                                "created_at": tx.created_at.isoformat()
                            } for tx in recent_tx
                        ]
            else:
                debug_info["user"]["logged_in"] = False
    except Exception as e:
        debug_info["database"]["error"] = str(e)
        debug_info["errors"].append(f"Database error: {e}")
    
    # Overall status
    debug_info["status"] = "ok" if len(debug_info["errors"]) == 0 else "errors"
    
    return jsonify(debug_info), 200 if debug_info["status"] == "ok" else 500

@app.route('/ops/debug/checkout', methods=['GET'])
def debug_checkout():
    """Debug endpoint for checkout system"""
    from storage import read_json
    
    debug_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "merch_catalog": {},
        "errors": []
    }
    
    # Check merch catalog
    try:
        merch_catalog = read_json("data/merch.json", {"items": []})
        if isinstance(merch_catalog, dict):
            items = merch_catalog.get("items", [])
            debug_info["merch_catalog"]["exists"] = True
            debug_info["merch_catalog"]["item_count"] = len(items) if isinstance(items, list) else 0
            debug_info["merch_catalog"]["items"] = [
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "price_usd": item.get("price_usd"),
                    "available": item.get("available", True)
                } for item in (items[:10] if isinstance(items, list) else [])  # First 10 items
            ]
        else:
            debug_info["merch_catalog"]["exists"] = False
            debug_info["errors"].append("Merch catalog is not a valid dictionary")
    except FileNotFoundError:
        debug_info["merch_catalog"]["exists"] = False
        debug_info["errors"].append("Merch catalog file not found: data/merch.json")
    except Exception as e:
        debug_info["merch_catalog"]["error"] = str(e)
        debug_info["errors"].append(f"Error reading merch catalog: {e}")
    
    debug_info["status"] = "ok" if len(debug_info["errors"]) == 0 else "errors"
    
    return jsonify(debug_info), 200 if debug_info["status"] == "ok" else 500
