#!/usr/bin/env python3
"""
Test script to send a test email directly to alex@ahoy.ooo.
This verifies the email system is working and emails are being sent.

Tests both notify_admin and notify_user functions with rate limiting.
"""
import os
import sys
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.emailer import can_send_email
from services.notifications import (
    notify_admin,
    notify_user,
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
    
    # Test 1: notify_admin
    print("📧 Test 1: Testing notify_admin()...")
    time.sleep(0.6)  # Space out sends to avoid rate limits
    admin_result = notify_admin(
        "🧪 Test Email - Admin Notification",
        """This is a test of the notify_admin() function.

If you receive this email, admin notifications are working correctly.

The system uses rate limiting with retry logic to handle Resend's 2 requests/second limit.
"""
    )
    
    if admin_result.get("ok"):
        print(f"✅ Admin notification sent successfully via {admin_result.get('provider')}")
    else:
        print(f"❌ Failed to send admin notification: {admin_result.get('detail')}")
        if not can_send_email():
            print("   Email service not configured - this is expected locally")
            return
    
    # Test 2: notify_user
    print("\n📧 Test 2: Testing notify_user()...")
    time.sleep(0.6)  # Space out sends
    user_result = notify_user(
        target_email,
        "🧪 Test Email - User Notification",
        """This is a test of the notify_user() function.

If you receive this email, user notifications are working correctly.

The system includes:
- Rate limiting with exponential backoff
- Automatic retry on 429 errors
- Environment labels for non-production
"""
    )
    
    if user_result.get("ok"):
        print(f"✅ User notification sent successfully via {user_result.get('provider')}")
    else:
        print(f"❌ Failed to send user notification: {user_result.get('detail')}")
    
    # Test 3: Boost notification (sends to admin + user)
    print("\n📧 Test 3: Testing boost notification (admin + user)...")
    time.sleep(0.6)
    boost_result = notify_boost_received(
        artist_id="rob-meglio",
        artist_name="Rob Meglio",
        boost_amount=Decimal("25.00"),
        artist_payout=Decimal("25.00"),
        total_paid=Decimal("27.50"),
        tipper_email=target_email,  # Send to target email as user
        stripe_session_id="test_session_123"
    )
    print(f"   Admin notified: {'✅' if boost_result.get('admin_notified') else '❌'}")
    print(f"   User notified: {'✅' if boost_result.get('user_notified') else '❌'}")
    
    # Test 4: User registration (sends to admin + user)
    print("\n📧 Test 4: Testing user registration (admin + user)...")
    time.sleep(0.6)
    reg_result = notify_user_registered(
        user_id=999,
        email=target_email,
        username="testuser",
        display_name="Test User"
    )
    print(f"   Admin notified: {'✅' if reg_result.get('admin_notified') else '❌'}")
    print(f"   User notified: {'✅' if reg_result.get('user_notified') else '❌'}")
    
    # Test 5: Wallet funding (sends to admin + user)
    print("\n📧 Test 5: Testing wallet funding (admin + user)...")
    time.sleep(0.6)
    wallet_result = notify_wallet_funded(
        user_id=999,
        user_email=target_email,
        amount=Decimal("50.00"),
        balance_before=Decimal("0.00"),
        balance_after=Decimal("50.00"),
        stripe_session_id="test_session_789"
    )
    print(f"   Admin notified: {'✅' if wallet_result.get('admin_notified') else '❌'}")
    print(f"   User notified: {'✅' if wallet_result.get('user_notified') else '❌'}")
    
    # Test 6: Merch purchase (sends to admin + user)
    print("\n📧 Test 6: Testing merch purchase (admin + user)...")
    time.sleep(0.6)
    merch_result = notify_merch_purchase(
        purchase_id=999,
        item_id="merch_123",
        item_name="Test T-Shirt",
        quantity=1,
        amount=Decimal("20.00"),
        total=Decimal("22.00"),
        buyer_email=target_email,
        stripe_session_id="test_session_456"
    )
    print(f"   Admin notified: {'✅' if merch_result.get('admin_notified') else '❌'}")
    print(f"   User notified: {'✅' if merch_result.get('user_notified') else '❌'}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("=" * 60)
    
    tests = [
        ("notify_admin", admin_result.get("ok")),
        ("notify_user", user_result.get("ok")),
        ("Boost (admin)", boost_result.get("admin_notified")),
        ("Boost (user)", boost_result.get("user_notified")),
        ("Registration (admin)", reg_result.get("admin_notified")),
        ("Registration (user)", reg_result.get("user_notified")),
        ("Wallet (admin)", wallet_result.get("admin_notified")),
        ("Wallet (user)", wallet_result.get("user_notified")),
        ("Merch (admin)", merch_result.get("admin_notified")),
        ("Merch (user)", merch_result.get("user_notified")),
    ]
    
    passed = sum(1 for _, ok in tests if ok)
    total = len(tests)
    
    for name, ok in tests:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"   {status}: {name}")
    
    print(f"\n   Results: {passed}/{total} tests passed")
    print(f"   Check {target_email} for test emails")
    print("=" * 60)
    
    # Verify admin email function
    admin_email = _get_admin_email()
    print(f"\n📋 Configuration:")
    print(f"   Admin Email: {admin_email}")
    print(f"   Target Email: {target_email}")
    print(f"   Email Service: {'✅ Configured' if can_send_email() else '❌ Not configured'}")

if __name__ == "__main__":
    main()
