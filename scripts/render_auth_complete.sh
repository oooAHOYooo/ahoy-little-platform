#!/usr/bin/env bash
# Complete Render CLI authentication
# Usage: ./scripts/render_auth_complete.sh

set -euo pipefail

echo "🔐 Render CLI Authentication"
echo "============================"
echo ""
echo "Step 1: Complete browser authentication"
echo "Visit: https://dashboard.render.com/device-authorization/T20H-Q8YW-BOUQ-2XC9"
echo ""
echo "Step 2: After authorizing in browser, press Enter here..."
read -p "Press Enter after you've authorized in the browser..."

echo ""
echo "Step 3: Verifying authentication..."
if render whoami &> /dev/null; then
    echo "✅ Successfully authenticated!"
    echo "   User: $(render whoami --output text 2>/dev/null || echo 'Authenticated')"
    echo ""
    echo "Next steps:"
    echo "1. Check environment variables: render services"
    echo "2. Or use dashboard: https://dashboard.render.com"
else
    echo "❌ Authentication failed. Please try: render login"
    exit 1
fi
