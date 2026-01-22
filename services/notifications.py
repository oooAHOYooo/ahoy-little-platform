"""
Notification service for boosts and merch purchases.
Sends email notifications to admins and optionally to artists.

Unified notification system with rate limiting and retry logic.
"""
import os
import time
import random
import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Any
from services.emailer import send_email, can_send_email

log = logging.getLogger(__name__)


def _get_admin_email() -> Optional[str]:
    """Get admin email from environment variable."""
    email = (os.getenv("AHOY_ADMIN_EMAIL") or os.getenv("SUPPORT_EMAIL") or "").strip()
    if email:
        return email
    # Fallback to alex@ahoy.ooo if not set (for production)
    return "alex@ahoy.ooo"


def _get_env_label() -> str:
    """Get environment label for email subjects."""
    env = (os.getenv("AHOY_ENV") or os.getenv("FLASK_ENV") or "prod").strip().lower()
    if env == "production" or env == "prod":
        return ""  # No label for production
    return f"[{env}] "


def send_email_with_retry(
    to_email: str,
    subject: str,
    text: str,
    html: Optional[str] = None,
    max_retries: int = 5
) -> Dict[str, Any]:
    """
    Send email with retry logic for rate limiting (429 errors).
    
    Implements exponential backoff with jitter:
    - Retry delays: 0.7s, 1.2s, 2.0s, 3.5s, 5.0s
    - Adds random jitter +/- 0.2s to avoid thundering herd
    - Never throws exceptions; returns ok=False on failure
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        text: Plain text email body
        html: Optional HTML email body
        max_retries: Maximum number of retry attempts (default: 5)
    
    Returns:
        Dict with keys: ok (bool), provider (str), detail (str|dict)
    """
    retry_delays = [0.7, 1.2, 2.0, 3.5, 5.0]
    
    for attempt in range(max_retries + 1):
        result = send_email(to_email, subject, text, html)
        
        # Success - return immediately
        if result.get("ok"):
            if attempt > 0:
                log.info(f"Email sent successfully after {attempt} retry(ies)")
            return result
        
        # Check if it's a rate limit error (429)
        detail = result.get("detail", {})
        is_rate_limit = False
        
        if isinstance(detail, dict):
            status = detail.get("status")
            body = detail.get("body", "")
            if status == 429 or "rate_limit" in str(body).lower() or "429" in str(body):
                is_rate_limit = True
        
        # If not rate limit or last attempt, return error
        if not is_rate_limit or attempt >= max_retries:
            if attempt > 0:
                log.warning(f"Email send failed after {attempt} retries: {result}")
            return result
        
        # Calculate delay with jitter
        base_delay = retry_delays[min(attempt, len(retry_delays) - 1)]
        jitter = random.uniform(-0.2, 0.2)
        delay = max(0.1, base_delay + jitter)  # Ensure at least 0.1s
        
        log.info(f"Rate limit hit (429), retrying in {delay:.2f}s (attempt {attempt + 1}/{max_retries})")
        time.sleep(delay)
    
    # Should never reach here, but return last result
    return result


def notify_admin(
    subject: str,
    text: str,
    tags: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send email notification to admin.
    
    Args:
        subject: Email subject (will be prefixed with environment label)
        text: Plain text email body
        tags: Optional metadata tags (for future use)
    
    Returns:
        Dict with keys: ok (bool), provider (str), detail (str|dict)
    """
    if not can_send_email():
        log.warning("Email not configured, skipping admin notification")
        return {"ok": False, "provider": "none", "detail": "email_not_configured"}
    
    admin_email = _get_admin_email()
    if not admin_email:
        log.warning("AHOY_ADMIN_EMAIL not set, skipping admin notification")
        return {"ok": False, "provider": "none", "detail": "admin_email_not_set"}
    
    # Add environment label to subject
    env_label = _get_env_label()
    prefixed_subject = f"{env_label}{subject}"
    
    # Generate HTML from text (simple conversion)
    html = text.replace("\n", "<br>\n")
    
    result = send_email_with_retry(admin_email, prefixed_subject, text, html)
    
    if not result.get("ok"):
        log.error(f"Failed to notify admin: {result}")
    
    return result


def notify_user(
    to_email: str,
    subject: str,
    text: str,
    tags: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send email notification to user.
    
    Args:
        to_email: User's email address
        subject: Email subject (environment label added only for non-prod)
        text: Plain text email body
        tags: Optional metadata tags (for future use)
    
    Returns:
        Dict with keys: ok (bool), provider (str), detail (str|dict)
    """
    if not can_send_email():
        log.warning("Email not configured, skipping user notification")
        return {"ok": False, "provider": "none", "detail": "email_not_configured"}
    
    to_email = (to_email or "").strip()
    if not to_email or "@" not in to_email:
        log.warning(f"Invalid email address: {to_email}")
        return {"ok": False, "provider": "none", "detail": "invalid_email"}
    
    # Add environment label only for non-production
    env_label = _get_env_label()
    prefixed_subject = f"{env_label}{subject}" if env_label else subject
    
    # Generate HTML from text (simple conversion)
    html = text.replace("\n", "<br>\n")
    
    result = send_email_with_retry(to_email, prefixed_subject, text, html)
    
    if not result.get("ok"):
        log.warning(f"Failed to notify user {to_email}: {result}")
    
    return result


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
    results = {"admin_notified": False, "user_notified": False, "artist_notified": False}
    
    if not can_send_email():
        log.warning("Email not configured, skipping boost notification")
        return results
    
    # Format amounts
    boost_str = f"${boost_amount:.2f}"
    payout_str = f"${artist_payout:.2f}"
    total_str = f"${total_paid:.2f}"
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Notify admin
    admin_subject = f"💰 New Boost: ${boost_amount:.2f} to {artist_name or artist_id}"
    admin_text = f"""New boost received!

Artist: {artist_name or artist_id}
Boost Amount: {boost_str}
Artist Payout: {payout_str}
Total Paid: {total_str}
Tipper: {tipper_email or 'Guest'}
Stripe Session: {stripe_session_id or 'N/A'}

You can process the payout using the script:
python scripts/send_artist_payout.py --artist-id "{artist_id}" --amount {artist_payout}
"""
    admin_result = notify_admin(admin_subject, admin_text)
    results["admin_notified"] = admin_result.get("ok", False)
    
    # Notify user (tipper) - receipt confirmation
    if tipper_email:
        user_subject = f"✅ Boost Confirmation: ${boost_amount:.2f} to {artist_name or artist_id}"
        user_text = f"""Thank you for your boost!

Boost Details:
Artist: {artist_name or artist_id}
Boost Amount: {boost_str}
Total Paid: {total_str}
Date: {timestamp}

100% of your boost (${boost_str}) goes directly to {artist_name or artist_id}.

Thank you for supporting independent artists! 🎵
"""
        user_result = notify_user(tipper_email, user_subject, user_text)
        results["user_notified"] = user_result.get("ok", False)
    
    # Notify artist (optional)
    artist_email = _get_artist_email(artist_id)
    if artist_email:
        artist_subject = f"🎉 You received a ${boost_amount:.2f} boost!"
        artist_text = f"""Great news! You received a boost of {boost_str}!

The funds will be processed and sent to you soon.

Thank you for creating amazing content!
"""
        artist_result = notify_user(artist_email, artist_subject, artist_text)
        results["artist_notified"] = artist_result.get("ok", False)
    
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
    
    # Notify admin
    admin_subject = f"🛍️ New Merch Purchase: ${total:.2f}"
    admin_text = f"""New merch purchase!

Purchase ID: {purchase_id}
Item: {item_name or item_id or 'Unknown'}
Quantity: {quantity}
Amount: ${amount:.2f}
Total: ${total:.2f}
Buyer: {buyer_email or 'Guest'}
Stripe Session: {stripe_session_id or 'N/A'}
"""
    admin_result = notify_admin(admin_subject, admin_text)
    results["admin_notified"] = admin_result.get("ok", False)
    
    # Notify user (receipt)
    if buyer_email:
        user_subject = f"🛍️ Order Confirmation: {item_name or 'Merch Purchase'}"
        user_text = f"""Thank you for your purchase!

Order Details:
Item: {item_name or item_id or 'Merch Item'}
Quantity: {quantity}
Amount: ${amount:.2f}
Total: ${total:.2f}
Purchase ID: {purchase_id}

Your order has been confirmed and will be processed soon.

Thank you for supporting independent artists!
"""
        user_result = notify_user(buyer_email, user_subject, user_text)
        results["user_notified"] = user_result.get("ok", False)
    
    return results


def notify_user_registered(
    user_id: int,
    email: str,
    username: Optional[str] = None,
    display_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send email notification when a new user registers.
    Sends to both admin and user.
    
    Returns dict with notification results.
    """
    results = {"admin_notified": False, "user_notified": False}
    
    if not can_send_email():
        log.warning("Email not configured, skipping user registration notification")
        return results
    
    # Notify admin
    admin_subject = f"👤 New User Registration: {email or username or 'Unknown'}"
    admin_text = f"""New user registered!

User ID: {user_id}
Email: {email}
Username: {username or 'N/A'}
Display Name: {display_name or 'N/A'}
Registered: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
    admin_result = notify_admin(admin_subject, admin_text)
    results["admin_notified"] = admin_result.get("ok", False)
    
    # Notify user (welcome email)
    if email:
        base_url = os.getenv("BASE_URL") or "https://app.ahoy.ooo"
        user_subject = "Welcome to Ahoy Indie Media ✨"
        user_text = f"""Welcome to Ahoy Indie Media!

You just created your account — we're excited to have you!

Your username: @{username or 'user'}

Get started:
- Discover new music and shows
- Create playlists
- Support your favorite artists
- Build your profile

Visit us: {base_url}

Thank you for joining the Ahoy community!
"""
        user_result = notify_user(email, user_subject, user_text)
        results["user_notified"] = user_result.get("ok", False)
    
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
    Sends to both admin and user.
    
    Returns dict with notification results.
    """
    results = {"admin_notified": False, "user_notified": False}
    
    if not can_send_email():
        log.warning("Email not configured, skipping wallet funding notification")
        return results
    
    # Notify admin
    admin_subject = f"💰 Wallet Funded: ${amount:.2f} by {user_email}"
    admin_text = f"""User funded their wallet!

User: {user_email} (ID: {user_id})
Amount Added: ${amount:.2f}
Balance Before: ${balance_before:.2f}
Balance After: ${balance_after:.2f}
Stripe Session: {stripe_session_id or 'N/A'}
"""
    admin_result = notify_admin(admin_subject, admin_text)
    results["admin_notified"] = admin_result.get("ok", False)
    
    # Notify user (confirmation)
    if user_email:
        user_subject = f"💰 Wallet Funded: ${amount:.2f} Added"
        user_text = f"""Your wallet has been funded!

Amount Added: ${amount:.2f}
Previous Balance: ${balance_before:.2f}
New Balance: ${balance_after:.2f}

You can now use your wallet balance for instant checkout on boosts and merch purchases.

Thank you for supporting independent artists!
"""
        user_result = notify_user(user_email, user_subject, user_text)
        results["user_notified"] = user_result.get("ok", False)
    
    return results
