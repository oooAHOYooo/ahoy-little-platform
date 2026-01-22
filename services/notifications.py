"""
Notification service for boosts and merch purchases.
Sends email notifications to admins and optionally to artists.
"""
import os
import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Any
from services.emailer import send_email, can_send_email

log = logging.getLogger(__name__)


def _get_admin_email() -> Optional[str]:
    """Get admin email from environment variable."""
    email = (os.getenv("AHOY_ADMIN_EMAIL") or os.getenv("SUPPORT_EMAIL") or "").strip()
    return email if email else None


def _get_artist_email(artist_id: str) -> Optional[str]:
    """
    Get artist email from environment variable mapping.
    Format: ARTIST_EMAIL_<artist_id>=email@example.com
    Or from a JSON file mapping (future enhancement).
    """
    # Try environment variable first (e.g., ARTIST_EMAIL_rob-meglio=rob@example.com)
    env_key = f"ARTIST_EMAIL_{artist_id.upper().replace('-', '_').replace(' ', '_')}"
    email = os.getenv(env_key) or os.getenv(env_key.lower())
    if email:
        return email.strip()
    
    # Try loading from artist data if available
    try:
        import json
        from pathlib import Path
        
        # Load artists.json directly
        artists_file = Path(__file__).parent.parent / 'static' / 'data' / 'artists.json'
        if artists_file.exists():
            with open(artists_file, 'r', encoding='utf-8') as f:
                artists_data = json.load(f)
            
            for artist in artists_data.get('artists', []):
                artist_slug = artist.get('slug', '').lower()
                artist_name = artist.get('name', '').lower()
                artist_id_lower = artist_id.lower()
                
                if (artist_slug == artist_id_lower or 
                    artist_name == artist_id_lower or 
                    str(artist.get('id', '')).lower() == artist_id_lower):
                    # Check if artist has email in their data
                    if 'email' in artist:
                        return artist['email'].strip()
                    # Check environment variable with slug
                    slug_key = f"ARTIST_EMAIL_{artist_slug.upper().replace('-', '_')}"
                    email = os.getenv(slug_key) or os.getenv(slug_key.lower())
                    if email:
                        return email.strip()
    except Exception as e:
        log.debug(f"Could not load artist email for {artist_id}: {e}")
    
    return None


def notify_boost_received(
    artist_id: str,
    artist_name: Optional[str],
    boost_amount: Decimal,
    artist_payout: Decimal,
    total_paid: Decimal,
    tipper_email: Optional[str] = None,
    stripe_session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send email notification when a boost is received.
    
    Returns dict with notification results.
    """
    results = {"admin_notified": False, "artist_notified": False}
    
    if not can_send_email():
        log.warning("Email not configured, skipping boost notification")
        return results
    
    admin_email = _get_admin_email()
    artist_email = _get_artist_email(artist_id)
    
    # Format amounts
    boost_str = f"${boost_amount:.2f}"
    payout_str = f"${artist_payout:.2f}"
    total_str = f"${total_paid:.2f}"
    
    # Notify admin
    if admin_email:
        subject = f"💰 New Boost: ${boost_amount:.2f} to {artist_name or artist_id}"
        text = f"""
New boost received!

Artist: {artist_name or artist_id}
Boost Amount: {boost_str}
Artist Payout: {payout_str}
Total Paid: {total_str}
Tipper: {tipper_email or 'Guest'}
Stripe Session: {stripe_session_id or 'N/A'}

You can process the payout using the script:
python scripts/send_artist_payout.py --artist-id "{artist_id}" --amount {artist_payout}
"""
        html = f"""
<h2>💰 New Boost Received</h2>
<p><strong>Artist:</strong> {artist_name or artist_id}</p>
<p><strong>Boost Amount:</strong> {boost_str}</p>
<p><strong>Artist Payout:</strong> {payout_str}</p>
<p><strong>Total Paid:</strong> {total_str}</p>
<p><strong>Tipper:</strong> {tipper_email or 'Guest'}</p>
<p><strong>Stripe Session:</strong> {stripe_session_id or 'N/A'}</p>
<hr>
<p>You can process the payout using the script:</p>
<pre>python scripts/send_artist_payout.py --artist-id "{artist_id}" --amount {artist_payout}</pre>
"""
        result = send_email(admin_email, subject, text, html)
        results["admin_notified"] = result.get("ok", False)
        if not result.get("ok"):
            log.error(f"Failed to notify admin of boost: {result}")
    
    # Notify artist (optional)
    if artist_email:
        subject = f"🎉 You received a ${boost_amount:.2f} boost!"
        text = f"""
Great news! You received a boost of {boost_str}!

The funds will be processed and sent to you soon.

Thank you for creating amazing content!
"""
        html = f"""
<h2>🎉 You Received a Boost!</h2>
<p>Great news! You received a boost of <strong>{boost_str}</strong>!</p>
<p>The funds will be processed and sent to you soon.</p>
<p>Thank you for creating amazing content!</p>
"""
        result = send_email(artist_email, subject, text, html)
        results["artist_notified"] = result.get("ok", False)
        if not result.get("ok"):
            log.debug(f"Failed to notify artist of boost: {result}")
    
    return results


def notify_merch_purchase(
    purchase_id: int,
    item_id: Optional[str],
    item_name: Optional[str],
    quantity: int,
    amount: Decimal,
    total: Decimal,
    buyer_email: Optional[str] = None,
    stripe_session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send email notification when merch is purchased.
    
    Returns dict with notification results.
    """
    results = {"admin_notified": False}
    
    if not can_send_email():
        log.warning("Email not configured, skipping merch purchase notification")
        return results
    
    admin_email = _get_admin_email()
    
    if admin_email:
        subject = f"🛍️ New Merch Purchase: ${total:.2f}"
        text = f"""
New merch purchase!

Purchase ID: {purchase_id}
Item: {item_name or item_id or 'Unknown'}
Quantity: {quantity}
Amount: ${amount:.2f}
Total: ${total:.2f}
Buyer: {buyer_email or 'Guest'}
Stripe Session: {stripe_session_id or 'N/A'}
"""
        html = f"""
<h2>🛍️ New Merch Purchase</h2>
<p><strong>Purchase ID:</strong> {purchase_id}</p>
<p><strong>Item:</strong> {item_name or item_id or 'Unknown'}</p>
<p><strong>Quantity:</strong> {quantity}</p>
<p><strong>Amount:</strong> ${amount:.2f}</p>
<p><strong>Total:</strong> ${total:.2f}</p>
<p><strong>Buyer:</strong> {buyer_email or 'Guest'}</p>
<p><strong>Stripe Session:</strong> {stripe_session_id or 'N/A'}</p>
"""
        result = send_email(admin_email, subject, text, html)
        results["admin_notified"] = result.get("ok", False)
        if not result.get("ok"):
            log.error(f"Failed to notify admin of merch purchase: {result}")
    
    return results


def notify_user_registered(
    user_id: int,
    email: str,
    username: Optional[str] = None,
    display_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send email notification when a new user registers.
    
    Returns dict with notification results.
    """
    results = {"admin_notified": False}
    
    if not can_send_email():
        log.warning("Email not configured, skipping user registration notification")
        return results
    
    admin_email = _get_admin_email()
    
    if admin_email:
        subject = f"👤 New User Registration: {email}"
        text = f"""
New user registered!

User ID: {user_id}
Email: {email}
Username: {username or 'N/A'}
Display Name: {display_name or 'N/A'}
Registered: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        html = f"""
<h2>👤 New User Registration</h2>
<p><strong>User ID:</strong> {user_id}</p>
<p><strong>Email:</strong> {email}</p>
<p><strong>Username:</strong> {username or 'N/A'}</p>
<p><strong>Display Name:</strong> {display_name or 'N/A'}</p>
<p><strong>Registered:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
"""
        result = send_email(admin_email, subject, text, html)
        results["admin_notified"] = result.get("ok", False)
        if not result.get("ok"):
            log.error(f"Failed to notify admin of user registration: {result}")
    
    return results


def notify_wallet_funded(
    user_id: int,
    user_email: str,
    amount: Decimal,
    balance_before: Decimal,
    balance_after: Decimal,
    stripe_session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send email notification when a user funds their wallet.
    
    Returns dict with notification results.
    """
    results = {"admin_notified": False}
    
    if not can_send_email():
        log.warning("Email not configured, skipping wallet funding notification")
        return results
    
    admin_email = _get_admin_email()
    
    if admin_email:
        subject = f"💰 Wallet Funded: ${amount:.2f} by {user_email}"
        text = f"""
User funded their wallet!

User: {user_email} (ID: {user_id})
Amount Added: ${amount:.2f}
Balance Before: ${balance_before:.2f}
Balance After: ${balance_after:.2f}
Stripe Session: {stripe_session_id or 'N/A'}
"""
        html = f"""
<h2>💰 Wallet Funded</h2>
<p><strong>User:</strong> {user_email} (ID: {user_id})</p>
<p><strong>Amount Added:</strong> ${amount:.2f}</p>
<p><strong>Balance Before:</strong> ${balance_before:.2f}</p>
<p><strong>Balance After:</strong> ${balance_after:.2f}</p>
<p><strong>Stripe Session:</strong> {stripe_session_id or 'N/A'}</p>
"""
        result = send_email(admin_email, subject, text, html)
        results["admin_notified"] = result.get("ok", False)
        if not result.get("ok"):
            log.error(f"Failed to notify admin of wallet funding: {result}")
    
    return results
