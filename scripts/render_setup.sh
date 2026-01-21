#!/usr/bin/env bash
# Render CLI Setup and Environment Variable Management
# This script helps verify and update Render environment variables

set -euo pipefail

SERVICE_NAME="ahoy-little-platform"
WEBHOOK_SECRET="whsec_fIVkv7yyR1GTBfmZOSLjVZ6cwPwRhluV"

echo "🔧 Render CLI Setup"
echo "=================="
echo ""

# Check if render CLI is installed
if ! command -v render &> /dev/null; then
    echo "❌ Render CLI not found. Installing..."
    if command -v brew &> /dev/null; then
        brew install render
    else
        echo "Please install Render CLI manually: https://render.com/docs/cli"
        exit 1
    fi
fi

echo "✅ Render CLI found: $(render --version)"
echo ""

# Check authentication
echo "🔐 Checking authentication..."
if ! render auth whoami &> /dev/null; then
    echo "⚠️  Not authenticated. Please run: render login"
    echo "   This will open a browser for authentication."
    read -p "Press Enter to continue with login, or Ctrl+C to cancel..."
    render login
else
    echo "✅ Authenticated as: $(render auth whoami)"
fi
echo ""

# List services
echo "📋 Available services:"
render services list --format table
echo ""

# Get service details
echo "🔍 Checking service: $SERVICE_NAME"
SERVICE_ID=$(render services list --format json | jq -r ".[] | select(.name == \"$SERVICE_NAME\") | .id" 2>/dev/null || echo "")

if [ -z "$SERVICE_ID" ]; then
    echo "❌ Service '$SERVICE_NAME' not found!"
    echo "Available services:"
    render services list --format table
    exit 1
fi

echo "✅ Service ID: $SERVICE_ID"
echo ""

# Check environment variables
echo "🔑 Current Environment Variables:"
echo "-----------------------------------"
render env list --service "$SERVICE_ID" --format table || render env list --service "$SERVICE_NAME" --format table
echo ""

# Check webhook secret
echo "🔍 Checking STRIPE_WEBHOOK_SECRET..."
CURRENT_SECRET=$(render env get --service "$SERVICE_ID" STRIPE_WEBHOOK_SECRET 2>/dev/null || render env get --service "$SERVICE_NAME" STRIPE_WEBHOOK_SECRET 2>/dev/null || echo "")

if [ -z "$CURRENT_SECRET" ]; then
    echo "⚠️  STRIPE_WEBHOOK_SECRET not set!"
    echo "Setting to: $WEBHOOK_SECRET"
    render env set --service "$SERVICE_ID" STRIPE_WEBHOOK_SECRET="$WEBHOOK_SECRET" || render env set --service "$SERVICE_NAME" STRIPE_WEBHOOK_SECRET="$WEBHOOK_SECRET"
    echo "✅ Webhook secret set!"
elif [ "$CURRENT_SECRET" != "$WEBHOOK_SECRET" ]; then
    echo "⚠️  Webhook secret mismatch!"
    echo "Current: ${CURRENT_SECRET:0:20}..."
    echo "Expected: ${WEBHOOK_SECRET:0:20}..."
    read -p "Update to correct value? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        render env set --service "$SERVICE_ID" STRIPE_WEBHOOK_SECRET="$WEBHOOK_SECRET" || render env set --service "$SERVICE_NAME" STRIPE_WEBHOOK_SECRET="$WEBHOOK_SECRET"
        echo "✅ Webhook secret updated!"
    fi
else
    echo "✅ Webhook secret is correct: ${WEBHOOK_SECRET:0:20}..."
fi
echo ""

# Check other Stripe variables
echo "🔍 Checking other Stripe variables..."
STRIPE_SECRET=$(render env get --service "$SERVICE_ID" STRIPE_SECRET_KEY 2>/dev/null || render env get --service "$SERVICE_NAME" STRIPE_SECRET_KEY 2>/dev/null || echo "")
STRIPE_PUBLISHABLE=$(render env get --service "$SERVICE_ID" STRIPE_PUBLISHABLE_KEY 2>/dev/null || render env get --service "$SERVICE_NAME" STRIPE_PUBLISHABLE_KEY 2>/dev/null || echo "")

if [ -z "$STRIPE_SECRET" ]; then
    echo "⚠️  STRIPE_SECRET_KEY not set!"
else
    echo "✅ STRIPE_SECRET_KEY is set: ${STRIPE_SECRET:0:10}..."
fi

if [ -z "$STRIPE_PUBLISHABLE" ]; then
    echo "⚠️  STRIPE_PUBLISHABLE_KEY not set!"
else
    echo "✅ STRIPE_PUBLISHABLE_KEY is set: ${STRIPE_PUBLISHABLE:0:10}..."
fi
echo ""

# Migration info
echo "📊 Migration Status:"
echo "Migrations run automatically on deploy via: ./scripts/migrate_and_start.sh"
echo "To manually trigger a deploy (which runs migrations), you can:"
echo "  1. Push a commit to main (auto-deploy)"
echo "  2. Or manually deploy: render deploys create --service $SERVICE_ID"
echo ""

# Summary
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Verify all environment variables are set correctly"
echo "2. Check migration status at: https://app.ahoy.ooo/ops/status"
echo "3. Test webhook at: https://app.ahoy.ooo/ops/webhooks/monitor"
echo ""
