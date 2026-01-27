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

from services.notifications import (
    notify_boost_received, 
    notify_merch_purchase,
    notify_user_registered,
    notify_wallet_funded
)
from services.emailer import can_send_email, send_email

def main():
    admin_email = os.getenv("AHOY_ADMIN_EMAIL") or os.getenv("SUPPORT_EMAIL")

    print("🧪 Testing Email Notifications\n")

    if not admin_email:
        print("❌ AHOY_ADMIN_EMAIL or SUPPORT_EMAIL not set!")
        print("   Set one of these environment variables to run this test")
        sys.exit(1)

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
    
    # Test 4: User registration notification
    print("📧 Test 4: Sending user registration notification...")
    reg_result = notify_user_registered(
        user_id=999,
        email="test@example.com",
        username="testuser",
        display_name="Test User"
    )
    if reg_result.get("admin_notified"):
        print("✅ User registration notification sent to admin")
    else:
        print("⚠️  User registration notification not sent (check logs)")
    
    print()
    
    # Test 5: Wallet funding notification
    print("📧 Test 5: Sending wallet funding notification...")
    wallet_result = notify_wallet_funded(
        user_id=999,
        user_email="test@example.com",
        amount=Decimal("25.00"),
        balance_before=Decimal("0.00"),
        balance_after=Decimal("25.00"),
        stripe_session_id="test_session_789"
    )
    if wallet_result.get("admin_notified"):
        print("✅ Wallet funding notification sent to admin")
    else:
        print("⚠️  Wallet funding notification not sent (check logs)")
    
    print()
    print("✅ All tests completed!")
    print(f"   Check {admin_email} for test emails")

if __name__ == "__main__":
    main()
