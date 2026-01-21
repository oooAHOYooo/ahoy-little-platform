#!/usr/bin/env python3
"""
Stripe Setup Automation Script (Python version)
Automates what can be done via terminal/API vs what requires Dashboard
"""
import os
import sys
import json
import subprocess
import requests
from typing import Optional, Dict, List

def run_command(cmd: List[str], capture_output: bool = True) -> tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_stripe_cli() -> bool:
    """Check if Stripe CLI is installed"""
    code, _, _ = run_command(["stripe", "--version"])
    return code == 0

def get_stripe_api_key(mode: str = "test") -> Optional[str]:
    """Get Stripe API key from CLI config"""
    key_name = f"{mode}_mode_api_key" if mode == "test" else "live_mode_api_key"
    code, stdout, _ = run_command(["stripe", "config", "--get", key_name])
    if code == 0 and stdout.strip():
        return stdout.strip()
    return None

def create_webhook_via_api(secret_key: str, webhook_url: str) -> Optional[Dict]:
    """Create webhook endpoint via Stripe API"""
    url = "https://api.stripe.com/v1/webhook_endpoints"
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "url": webhook_url,
        "enabled_events[]": ["checkout.session.completed", "payment_intent.succeeded"]
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return None

def create_webhook_via_cli(secret_key: str, webhook_url: str) -> Optional[Dict]:
    """Create webhook endpoint via Stripe CLI"""
    cmd = [
        "stripe", "webhook_endpoints", "create",
        "--url", webhook_url,
        "--enabled-events", "checkout.session.completed",
        "--enabled-events", "payment_intent.succeeded",
        "--api-key", secret_key,
        "--format", "json"
    ]
    
    code, stdout, stderr = run_command(cmd)
    if code == 0:
        try:
            return json.loads(stdout)
        except:
            return {"raw_output": stdout}
    else:
        print(f"CLI error: {stderr}")
        return None

def main():
    print("🔧 Stripe Setup Automation (Python)")
    print()
    
    # Check Stripe CLI
    if not check_stripe_cli():
        print("❌ Stripe CLI not found!")
        print()
        print("Install it:")
        print("  macOS: brew install stripe/stripe-cli/stripe")
        print("  Linux: https://github.com/stripe/stripe-cli/releases")
        print("  Windows: https://github.com/stripe/stripe-cli/releases")
        sys.exit(1)
    
    # Get mode
    mode = input("Environment (test/live) [test]: ").strip().lower() or "test"
    if mode not in ["test", "live"]:
        mode = "test"
    
    is_live = mode == "live"
    env_prefix = "" if is_live else "_TEST"
    
    print()
    print("📋 Step 1: Getting API Keys")
    print()
    
    # Try to get from CLI config
    secret_key = get_stripe_api_key(mode)
    publishable_key = get_stripe_api_key(mode)  # Note: CLI doesn't expose publishable easily
    
    if not secret_key:
        print("⚠️  Could not get API key from CLI config")
        print()
        print("You need to get these from Stripe Dashboard:")
        print(f"  1. Go to https://dashboard.stripe.com/apikeys")
        print(f"  2. Switch to {mode.upper()} mode")
        print(f"  3. Copy the keys")
        print()
        secret_key = input(f"Enter Secret Key (sk_{mode[0]}_...): ").strip()
        publishable_key = input(f"Enter Publishable Key (pk_{mode[0]}_...): ").strip()
    
    if not secret_key or not publishable_key:
        print("❌ API keys are required!")
        sys.exit(1)
    
    print("✅ API Keys retrieved")
    print()
    
    # Get webhook URL
    base_url = input("Enter your production BASE_URL (e.g., https://app.ahoy.ooo): ").strip()
    if not base_url:
        print("❌ BASE_URL is required!")
        sys.exit(1)
    
    webhook_url = f"{base_url.rstrip('/')}/webhooks/stripe"
    
    print()
    print("📋 Step 2: Creating Webhook Endpoint")
    print()
    print(f"Creating webhook: {webhook_url}")
    
    # Try CLI first, then API
    webhook_result = create_webhook_via_cli(secret_key, webhook_url)
    
    if not webhook_result:
        print("⚠️  CLI method failed, trying API...")
        webhook_result = create_webhook_via_api(secret_key, webhook_url)
    
    if not webhook_result:
        print("❌ Failed to create webhook endpoint")
        print()
        print("Create it manually:")
        print(f"  1. Go to https://dashboard.stripe.com/webhooks")
        print(f"  2. Click 'Add endpoint'")
        print(f"  3. URL: {webhook_url}")
        print(f"  4. Events: checkout.session.completed, payment_intent.succeeded")
        sys.exit(1)
    
    # Extract webhook secret
    webhook_secret = webhook_result.get("secret") or webhook_result.get("signing_secret")
    
    if not webhook_secret:
        print("⚠️  Could not extract webhook secret automatically")
        print(f"Response: {json.dumps(webhook_result, indent=2)}")
        print()
        webhook_secret = input("Enter Webhook Secret (whsec_...): ").strip()
    
    if not webhook_secret:
        print("❌ Webhook secret is required!")
        sys.exit(1)
    
    print("✅ Webhook endpoint created")
    print(f"  URL: {webhook_url}")
    print(f"  Secret: {webhook_secret[:20]}...")
    print()
    
    # Generate env file
    print("📋 Step 3: Generating Environment Variables")
    print()
    
    env_file = f".env.stripe.{mode}"
    ajoy_env = "production" if is_live else "development"
    
    env_content = f"""# Stripe Configuration ({mode} mode)
# Generated by setup_stripe.py

AHOY_ENV={ajoy_env}
STRIPE_PUBLISHABLE_KEY{env_prefix}={publishable_key}
STRIPE_SECRET_KEY{env_prefix}={secret_key}
STRIPE_WEBHOOK_SECRET{env_prefix}={webhook_secret}
"""
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print(f"✅ Environment variables saved to {env_file}")
    print()
    print("To use these variables:")
    print(f"  export $(cat {env_file} | xargs)")
    print()
    print("Or add them to your deployment platform (Render, Heroku, etc.)")
    print()
    
    # Summary
    print("✅ Stripe setup complete!")
    print()
    print("Summary:")
    print(f"  Mode: {mode}")
    print(f"  Webhook URL: {webhook_url}")
    print(f"  Env file: {env_file}")
    print()
    print("⚠️  Next steps (must be done on Stripe Dashboard):")
    print("  1. Verify webhook endpoint: https://dashboard.stripe.com/webhooks")
    print("  2. Check SSL/TLS is valid for your domain")
    print("  3. Monitor webhook deliveries in the Dashboard")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(1)
