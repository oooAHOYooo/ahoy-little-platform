#!/usr/bin/env python3
"""
Check email configuration and test sending.

This script helps diagnose email configuration issues.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.emailer import can_send_email, send_email, _from_email
from services.notifications import _get_admin_email

def main():
    print("📧 Email Configuration Check\n")
    print("=" * 60)
    
    # Check Resend
    resend_key = os.getenv("RESEND_API_KEY")
    print(f"\n🔑 Resend API Key:")
    if resend_key:
        masked = resend_key[:8] + "..." + resend_key[-4:] if len(resend_key) > 12 else "***"
        print(f"   ✅ Found: {masked}")
        print(f"   Provider: Resend API")
    else:
        print(f"   ❌ Not set")
    
    # Check SMTP
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS") or os.getenv("SMTP_PASSWORD")
    print(f"\n📮 SMTP Configuration:")
    if smtp_host and smtp_user:
        print(f"   ✅ Host: {smtp_host}")
        print(f"   ✅ User: {smtp_user}")
        print(f"   ✅ Password: {'Set' if smtp_pass else 'Not set'}")
        print(f"   Provider: SMTP")
    else:
        print(f"   ❌ Not configured")
    
    # Check support email
    support_email = os.getenv("SUPPORT_EMAIL")
    print(f"\n📬 Support Email (From Address):")
    if support_email:
        print(f"   ✅ {support_email}")
    else:
        print(f"   ❌ Not set")
        print(f"   ⚠️  Emails will use placeholder: support@localhost")
    
    # Check admin email
    admin_email = _get_admin_email()
    print(f"\n👤 Admin Email (To Address):")
    if admin_email:
        print(f"   ✅ {admin_email}")
    else:
        print(f"   ❌ Not set")
        print(f"   ⚠️  Will use fallback: alex@ahoy.ooo")
    
    # Check if email can be sent
    print(f"\n✅ Can Send Email:")
    can_send = can_send_email()
    if can_send:
        print(f"   ✅ YES - Email service is configured")
        print(f"   Provider: {'Resend' if resend_key else 'SMTP'}")
    else:
        print(f"   ❌ NO - Email service not configured")
        print(f"\n   To fix:")
        if not resend_key and not (smtp_host and smtp_user):
            print(f"   - Set RESEND_API_KEY (recommended)")
            print(f"   - OR set SMTP_HOST, SMTP_USER, SMTP_PASS")
        if not support_email:
            print(f"   - Set SUPPORT_EMAIL")
    
    # Test email if configured
    if can_send:
        print(f"\n🧪 Testing Email Send...")
        test_email = admin_email or "alex@ahoy.ooo"
        result = send_email(
            to_email=test_email,
            subject="🧪 Email Configuration Test",
            text="This is a test email to verify your email configuration is working correctly.",
            html="<h2>🧪 Email Configuration Test</h2><p>This is a test email to verify your email configuration is working correctly.</p>"
        )
        
        if result.get("ok"):
            print(f"   ✅ Test email sent successfully!")
            print(f"   Provider: {result.get('provider')}")
            print(f"   To: {test_email}")
            print(f"   Check your inbox (and spam folder)")
        else:
            print(f"   ❌ Failed to send test email")
            print(f"   Provider: {result.get('provider')}")
            print(f"   Error: {result.get('detail')}")
    
    print(f"\n" + "=" * 60)
    print(f"\n📚 Next Steps:")
    if not can_send:
        print(f"   1. Sign up for Resend: https://resend.com")
        print(f"   2. Get API key from Resend dashboard")
        print(f"   3. Add domain and verify DNS")
        print(f"   4. Set RESEND_API_KEY in Render")
        print(f"   5. Set SUPPORT_EMAIL in Render")
        print(f"   6. Run this script again to test")
    else:
        print(f"   ✅ Email is configured and working!")
        print(f"   You should receive notifications at: {admin_email or 'alex@ahoy.ooo'}")

if __name__ == "__main__":
    main()
