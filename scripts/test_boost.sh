#!/bin/bash
# Test boost/tip webhook
# Usage: ./scripts/test_boost.sh [artist_id] [amount]

ARTIST_ID=${1:-alex-figueroa}
AMOUNT=${2:-10.00}

echo "🧪 Testing boost/tip webhook..."
echo "Artist ID: $ARTIST_ID"
echo "Amount: \$$AMOUNT"
echo ""

stripe trigger checkout.session.completed \
  --override metadata:type=boost \
  --override metadata:artist_id=$ARTIST_ID \
  --override metadata:boost_amount=$AMOUNT

echo ""
echo "✅ Test event triggered!"
echo "📊 Check /ops/webhooks/monitor to see the result"
