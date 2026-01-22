#!/usr/bin/env python3
"""
Test script to send a test email directly to alex@ahoy.ooo.
This verifies the email system is working and emails are being sent.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.emailer import send_email, can_send_email
from services.notifications import (
    notify_boost_received,
    notify_merch_purchase,
    notify_user_registered,
    notify_wallet_funded,
    _get_admin_email
)
from decimal import Decimal

def main():
    # Force alex@ahoy.ooo as the recipient
    target_email = "alex@ahoy.ooo"
    
    print("📧 Testing Email to alex@ahoy.ooo\n")
    print(f"Target Email: {target_email}")
    print(f"Email Service Available: {can_send_email()}\n")
    
    if not can_send_email():
        print("⚠️  Email service not configured locally!")
        print("   This is expected - email will work on Render when configured.")
        print("   Setting RESEND_API_KEY or SMTP_* environment variables is required.\n")
        print("   For now, showing what would be sent:\n")
        
        # Show what would be sent
        print("=" * 60)
        print("EMAIL PREVIEW (would be sent to alex@ahoy.ooo):")
        print("=" * 60)
        print("\nSubject: 🧪 Test Email - Ahoy Notifications")
        print("\nBody:")
        print("This is a test email to verify email notifications are working!")
        print("\n" + "=" * 60)
        return
    
    # Test 1: Simple test email
    print("📧 Test 1: Sending simple test email...")
    result = send_email(
        to_email=target_email,
        subject="🧪 Test Email - Ahoy Notifications System",
        text="""This is a test email to verify the Ahoy notification system is working!

If you receive this email, the notification system is properly configured.

You will receive emails for:
- New user registrations
- Wallet funding
- Artist boosts
- Merch purchases
- Daily payout summaries

Best regards,
Ahoy Platform
""",
        html="""
<h2>🧪 Test Email - Ahoy Notifications System</h2>
<p>This is a test email to verify the Ahoy notification system is working!</p>
<p>If you receive this email, the notification system is properly configured.</p>
<h3>You will receive emails for:</h3>
<ul>
    <li>New user registrations</li>
    <li>Wallet funding</li>
    <li>Artist boosts</li>
    <li>Merch purchases</li>
    <li>Daily payout summaries</li>
</ul>
<p>Best regards,<br>Ahoy Platform</p>
"""
    )
    
    if result.get("ok"):
        print(f"✅ Test email sent successfully via {result.get('provider')}")
        print(f"   Check {target_email} for the email")
    else:
        print(f"❌ Failed to send test email: {result.get('detail')}")
        return
    
    print()
    
    # Test 2: Boost notification
    print("📧 Test 2: Sending boost notification...")
    boost_result = notify_boost_received(
        artist_id="rob-meglio",
        artist_name="Rob Meglio",
        boost_amount=Decimal("25.00"),
        artist_payout=Decimal("25.00"),
        total_paid=Decimal("27.50"),
        tipper_email="test@example.com",
        stripe_session_id="test_session_123"
    )
    if boost_result.get("admin_notified"):
        print(f"✅ Boost notification sent to {target_email}")
    else:
        print("⚠️  Boost notification not sent")
    
    print()
    
    # Test 3: User registration
    print("📧 Test 3: Sending user registration notification...")
    reg_result = notify_user_registered(
        user_id=999,
        email="newuser@example.com",
        username="newuser",
        display_name="New User"
    )
    if reg_result.get("admin_notified"):
        print(f"✅ User registration notification sent to {target_email}")
    else:
        print("⚠️  User registration notification not sent")
    
    print()
    
    # Test 4: Wallet funding
    print("📧 Test 4: Sending wallet funding notification...")
    wallet_result = notify_wallet_funded(
        user_id=999,
        user_email="user@example.com",
        amount=Decimal("50.00"),
        balance_before=Decimal("0.00"),
        balance_after=Decimal("50.00"),
        stripe_session_id="test_session_789"
    )
    if wallet_result.get("admin_notified"):
        print(f"✅ Wallet funding notification sent to {target_email}")
    else:
        print("⚠️  Wallet funding notification not sent")
    
    print()
    print("=" * 60)
    print("✅ All email tests completed!")
    print(f"   Check {target_email} for test emails")
    print("=" * 60)
    
    # Verify admin email function
    admin_email = _get_admin_email()
    print(f"\n📋 Admin Email Configuration:")
    print(f"   _get_admin_email() returns: {admin_email or 'None (will use alex@ahoy.ooo as fallback)'}")
    print(f"   Target email: {target_email}")

if __name__ == "__main__":
    main()
