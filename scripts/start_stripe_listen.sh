#!/bin/bash
# Start Stripe webhook listener and forward to local server
# Usage: ./scripts/start_stripe_listen.sh [port]

PORT=${1:-5000}
echo "🚀 Starting Stripe webhook listener..."
echo "📡 Forwarding to: http://localhost:${PORT}/webhooks/stripe"
echo ""
echo "⚠️  Keep this terminal open to receive webhooks"
echo "💡 Press Ctrl+C to stop"
echo ""

stripe listen --forward-to "http://localhost:${PORT}/webhooks/stripe"
