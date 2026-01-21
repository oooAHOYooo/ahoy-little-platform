#!/usr/bin/env bash
# Quick script to check Render environment variables
# Usage: ./scripts/render_check_env.sh

set -euo pipefail

SERVICE_NAME="ahoy-little-platform"
WEBHOOK_SECRET="whsec_fIVkv7yyR1GTBfmZOSLjVZ6cwPwRhluV"

echo "🔍 Checking Render Environment Variables"
echo "========================================"
echo ""

# Check authentication
if ! render auth whoami &> /dev/null; then
    echo "❌ Not authenticated. Run: render login"
    exit 1
fi

echo "✅ Authenticated as: $(render auth whoami)"
echo ""

# Try to get service by name or ID
SERVICE_ID=$(render services list --format json 2>/dev/null | jq -r ".[] | select(.name == \"$SERVICE_NAME\") | .id" 2>/dev/null || echo "")

if [ -z "$SERVICE_ID" ]; then
    echo "⚠️  Service not found by name. Listing all services:"
    render services list --format table
    exit 1
fi

echo "📋 Service: $SERVICE_NAME (ID: $SERVICE_ID)"
echo ""

# Check webhook secret
echo "🔑 STRIPE_WEBHOOK_SECRET:"
CURRENT_SECRET=$(render env get --service "$SERVICE_ID" STRIPE_WEBHOOK_SECRET 2>/dev/null || echo "NOT SET")

if [ "$CURRENT_SECRET" = "NOT SET" ]; then
    echo "   ❌ NOT SET"
    echo "   Expected: $WEBHOOK_SECRET"
    echo ""
    echo "   To set it, run:"
    echo "   render env set --service $SERVICE_ID STRIPE_WEBHOOK_SECRET='$WEBHOOK_SECRET'"
elif [ "$CURRENT_SECRET" != "$WEBHOOK_SECRET" ]; then
    echo "   ⚠️  MISMATCH"
    echo "   Current:  ${CURRENT_SECRET:0:30}..."
    echo "   Expected: ${WEBHOOK_SECRET:0:30}..."
    echo ""
    echo "   To update, run:"
    echo "   render env set --service $SERVICE_ID STRIPE_WEBHOOK_SECRET='$WEBHOOK_SECRET'"
else
    echo "   ✅ Correct: ${WEBHOOK_SECRET:0:30}..."
fi
echo ""

# Check other Stripe vars
echo "🔑 STRIPE_SECRET_KEY:"
STRIPE_SECRET=$(render env get --service "$SERVICE_ID" STRIPE_SECRET_KEY 2>/dev/null || echo "NOT SET")
if [ "$STRIPE_SECRET" = "NOT SET" ]; then
    echo "   ❌ NOT SET"
else
    echo "   ✅ Set: ${STRIPE_SECRET:0:15}..."
fi
echo ""

echo "🔑 STRIPE_PUBLISHABLE_KEY:"
STRIPE_PUB=$(render env get --service "$SERVICE_ID" STRIPE_PUBLISHABLE_KEY 2>/dev/null || echo "NOT SET")
if [ "$STRIPE_PUB" = "NOT SET" ]; then
    echo "   ❌ NOT SET"
else
    echo "   ✅ Set: ${STRIPE_PUB:0:15}..."
fi
echo ""

echo "🔑 AHOY_ENV:"
AHOY_ENV=$(render env get --service "$SERVICE_ID" AHOY_ENV 2>/dev/null || echo "NOT SET")
if [ "$AHOY_ENV" = "NOT SET" ]; then
    echo "   ❌ NOT SET"
else
    echo "   ✅ Set: $AHOY_ENV"
fi
echo ""

echo "📊 Migration Status:"
echo "   Migrations run automatically on deploy via: ./scripts/migrate_and_start.sh"
echo "   To trigger deploy (runs migrations):"
echo "   render deploys create --service $SERVICE_ID"
echo ""
