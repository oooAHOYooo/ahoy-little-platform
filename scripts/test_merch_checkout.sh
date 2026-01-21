#!/bin/bash
# Test merch checkout webhook
# Usage: ./scripts/test_merch_checkout.sh [purchase_id] [item_id] [amount]

PURCHASE_ID=${1:-123}
ITEM_ID=${2:-sample_merch1}
AMOUNT=${3:-20.00}

echo "🧪 Testing merch checkout webhook..."
echo "Purchase ID: $PURCHASE_ID"
echo "Item ID: $ITEM_ID"
echo "Amount: \$$AMOUNT"
echo ""

stripe trigger checkout.session.completed \
  --override metadata:type=merch \
  --override metadata:purchase_id=$PURCHASE_ID \
  --override metadata:item_id=$ITEM_ID \
  --override metadata:amount=$AMOUNT

echo ""
echo "✅ Test event triggered!"
echo "📊 Check /ops/webhooks/monitor to see the result"
