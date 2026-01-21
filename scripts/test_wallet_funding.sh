#!/bin/bash
# Test wallet funding webhook
# Usage: ./scripts/test_wallet_funding.sh [user_id] [amount]

USER_ID=${1:-1}
AMOUNT=${2:-10.00}

echo "🧪 Testing wallet funding webhook..."
echo "User ID: $USER_ID"
echo "Amount: \$$AMOUNT"
echo ""

stripe trigger checkout.session.completed \
  --override metadata:type=wallet_fund \
  --override metadata:user_id=$USER_ID \
  --override metadata:amount=$AMOUNT

echo ""
echo "✅ Test event triggered!"
echo "📊 Check /ops/webhooks/monitor to see the result"
