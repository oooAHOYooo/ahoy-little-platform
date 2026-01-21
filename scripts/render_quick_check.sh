#!/usr/bin/env bash
# Quick Render environment check
# First run: render login

set -euo pipefail

echo "🔍 Render Environment Check"
echo "==========================="
echo ""

# Check authentication
if ! render whoami &> /dev/null; then
    echo "❌ Not authenticated!"
    echo ""
    echo "Please run: render login"
    echo "This will open a browser for authentication."
    exit 1
fi

echo "✅ Authenticated: $(render whoami --output text 2>/dev/null || echo 'User')"
echo ""

# List services (interactive mode will show menu)
echo "📋 Your Render Services:"
echo "   Run: render services"
echo "   Then select 'ahoy-little-platform' to manage it"
echo ""

# For environment variables, Render CLI uses interactive mode
echo "🔑 To check/update environment variables:"
echo "   1. Run: render services"
echo "   2. Select: ahoy-little-platform"
echo "   3. Choose: Environment Variables"
echo "   4. Verify STRIPE_WEBHOOK_SECRET = whsec_fIVkv7yyR1GTBfmZOSLjVZ6cwPwRhluV"
echo ""

echo "📊 To trigger a deploy (runs migrations automatically):"
echo "   1. Run: render services"
echo "   2. Select: ahoy-little-platform"
echo "   3. Choose: Deploy"
echo ""

echo "💡 Alternative: Push to main branch (auto-deploys)"
echo "   git push origin main"
echo ""
