#!/usr/bin/env python3
"""
Test script to send a test email notification for boosts/merch.
This verifies that email notifications are working correctly.
"""
import os
import sys
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.notifications import notify_boost_received, notify_merch_purchase
from services.emailer import can_send_email, send_email

def main():
    admin_email = os.getenv("AHOY_ADMIN_EMAIL") or os.getenv("SUPPORT_EMAIL") or "alex@ahoy.ooo"
    
    print("🧪 Testing Email Notifications\n")
    print(f"Admin Email: {admin_email}")
    print(f"Email Service Available: {can_send_email()}\n")
    
    if not can_send_email():
        print("❌ Email service not configured!")
        print("   Set RESEND_API_KEY or SMTP_* environment variables")
        sys.exit(1)
    
    # Test 1: Simple email test
    print("📧 Test 1: Sending simple test email...")
    result = send_email(
        to_email=admin_email,
        subject="🧪 Test Email - Ahoy Notifications",
        text="This is a test email to verify email notifications are working!",
        html="<h2>🧪 Test Email</h2><p>This is a test email to verify email notifications are working!</p>"
    )
    if result.get("ok"):
        print(f"✅ Test email sent successfully via {result.get('provider')}")
    else:
        print(f"❌ Failed to send test email: {result.get('detail')}")
        sys.exit(1)
    
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
        print("✅ Boost notification sent to admin")
    else:
        print("⚠️  Boost notification not sent (check logs)")
    
    print()
    
    # Test 3: Merch purchase notification
    print("📧 Test 3: Sending merch purchase notification...")
    merch_result = notify_merch_purchase(
        purchase_id=999,
        item_id="merch_123",
        item_name="Test T-Shirt",
        quantity=1,
        amount=Decimal("20.00"),
        total=Decimal("22.00"),
        buyer_email="test@example.com",
        stripe_session_id="test_session_456"
    )
    if merch_result.get("admin_notified"):
        print("✅ Merch purchase notification sent to admin")
    else:
        print("⚠️  Merch purchase notification not sent (check logs)")
    
    print()
    print("✅ All tests completed!")
    print(f"   Check {admin_email} for test emails")

if __name__ == "__main__":
    main()
