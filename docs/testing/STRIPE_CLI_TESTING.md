# Stripe CLI Testing Guide

## 🚀 Quick Start

### 1. Install Stripe CLI

**macOS:**
```bash
brew install stripe/stripe-cli/stripe
```

**Linux:**
```bash
# Download from https://github.com/stripe/stripe-cli/releases
# Or use package manager
```

**Windows:**
```bash
# Download from https://github.com/stripe/stripe-cli/releases
# Or use Scoop: scoop install stripe
```

### 2. Login to Stripe

```bash
stripe login
```

This will open your browser to authenticate with Stripe.

---

## 🔍 Testing Wallet Funding

### Step 1: Forward Webhooks to Your Server

**For Local Development:**
```bash
stripe listen --forward-to localhost:5000/webhooks/stripe
```

**For Production (if you have access):**
```bash
stripe listen --forward-to https://app.ahoy.ooo/webhooks/stripe
```

**Output:**
```
> Ready! Your webhook signing secret is whsec_... (^C to quit)
```

**⚠️ Important:** Copy the webhook signing secret shown. You'll need it if testing locally.

### Step 2: Test Wallet Funding Webhook

**Trigger a test checkout session completion:**
```bash
stripe trigger checkout.session.completed
```

**With specific metadata (wallet funding):**
```bash
stripe trigger checkout.session.completed \
  --override metadata:type=wallet_fund \
  --override metadata:user_id=1 \
  --override metadata:amount=10.00
```

**What to check:**
- ✅ Webhook is received by your server
- ✅ Wallet balance is updated in database
- ✅ WalletTransaction record is created
- ✅ Server logs show successful processing

### Step 3: Verify in Database

**Check wallet balance:**
```sql
SELECT id, wallet_balance FROM users WHERE id = 1;
```

**Check transactions:**
```sql
SELECT * FROM wallet_transactions WHERE user_id = 1 ORDER BY created_at DESC LIMIT 5;
```

---

## 🛒 Testing Checkout Flow

### Test Merch Checkout

**1. Create a test checkout session:**
```bash
stripe checkout sessions create \
  --success-url "https://app.ahoy.ooo/checkout/success" \
  --cancel-url "https://app.ahoy.ooo/checkout" \
  --mode payment \
  --line-items price_data[currency]=usd,price_data[unit_amount]=2000,price_data[product_data][name]="Test Merch Item" \
  --metadata type=merch \
  --metadata purchase_id=123 \
  --metadata item_id=sample_merch1 \
  --metadata user_id=1
```

**2. Complete the checkout:**
- Copy the checkout URL from the output
- Open in browser
- Use test card: `4242 4242 4242 4242`
- Complete payment

**3. Verify webhook:**
```bash
# Watch webhook events
stripe events list --limit 5
```

### Test Boost/Tip Checkout

```bash
stripe checkout sessions create \
  --success-url "https://app.ahoy.ooo/checkout/success" \
  --cancel-url "https://app.ahoy.ooo/checkout" \
  --mode payment \
  --line-items price_data[currency]=usd,price_data[unit_amount]=1000,price_data[product_data][name]="Boost Amount" \
  --metadata type=boost \
  --metadata artist_id=alex-figueroa \
  --metadata user_id=1 \
  --metadata boost_amount=10.00
```

---

## 🧪 Testing Scenarios

### Scenario 1: Wallet Funding Flow

**1. Start webhook listener:**
```bash
stripe listen --forward-to localhost:5000/webhooks/stripe
```

**2. In browser:**
- Go to `/account`
- Click "Add $5 (Optional)"
- Complete Stripe checkout with test card

**3. Verify:**
- Check `/ops/debug/payments` endpoint
- Verify wallet balance updated
- Check transaction history

### Scenario 2: Wallet Payment Flow

**1. Fund wallet first (see Scenario 1)**

**2. Buy merch with wallet:**
- Go to `/merch`
- Click "Checkout" on an item
- Check "Pay instantly from wallet"
- Complete purchase

**3. Verify:**
- Wallet balance decreased
- Purchase marked as paid
- No Stripe redirect occurred

### Scenario 3: Direct Stripe Payment

**1. Start webhook listener:**
```bash
stripe listen --forward-to localhost:5000/webhooks/stripe
```

**2. In browser:**
- Go to `/merch`
- Click "Checkout" on an item
- **Don't** check wallet checkbox
- Complete Stripe checkout

**3. Verify:**
- Webhook received
- Purchase marked as paid
- Tip record created (if boost)

---

## 📊 Monitoring Webhook Events

### View Recent Events

```bash
# List last 10 events
stripe events list --limit 10

# Filter by event type
stripe events list --type checkout.session.completed

# Get specific event details
stripe events retrieve evt_1234567890
```

### Stream Events in Real-Time

```bash
# Watch all events
stripe events listen

# Watch specific event types
stripe events listen --events checkout.session.completed,payment_intent.succeeded
```

### Check Webhook Delivery Status

```bash
# List webhook endpoints
stripe webhook_endpoints list

# Get endpoint details
stripe webhook_endpoints retrieve we_1234567890

# View event deliveries for an endpoint
stripe webhook_endpoints retrieve we_1234567890 --expand data.event
```

---

## 🐛 Debugging Failed Webhooks

### Check Webhook Logs

**In Stripe Dashboard:**
1. Go to: https://dashboard.stripe.com/webhooks
2. Click your endpoint
3. Check "Event deliveries" tab
4. Look for failed deliveries (red status)

**Common Issues:**
- ❌ **400 Bad Request**: Invalid webhook signature (check `STRIPE_WEBHOOK_SECRET`)
- ❌ **500 Internal Server Error**: Server-side error (check server logs)
- ❌ **Timeout**: Server not responding (check server is running)

### Test Webhook Signature

**Get webhook secret:**
```bash
# From Stripe CLI output when running `stripe listen`
# Or from Stripe Dashboard → Webhooks → Your endpoint → Signing secret
```

**Verify signature in code:**
```python
import stripe

# Verify webhook signature
event = stripe.Webhook.construct_event(
    payload=request.data,
    sig_header=request.headers.get('Stripe-Signature'),
    secret=webhook_secret
)
```

### Test Webhook Manually

**1. Get webhook payload:**
```bash
# Trigger event and capture payload
stripe trigger checkout.session.completed --print-secret
```

**2. Send to your server:**
```bash
# Use curl to send webhook
curl -X POST http://localhost:5000/webhooks/stripe \
  -H "Stripe-Signature: t=...,v1=..." \
  -H "Content-Type: application/json" \
  -d @webhook_payload.json
```

---

## 🔧 Common Test Cards

### Success Cards

```bash
# Visa (success)
4242 4242 4242 4242

# Mastercard (success)
5555 5555 5555 4444

# Amex (success)
3782 822463 10005
```

### Decline Cards

```bash
# Card declined
4000 0000 0000 0002

# Insufficient funds
4000 0000 0000 9995

# Expired card
4000 0000 0000 0069
```

### 3D Secure Cards

```bash
# Requires authentication
4000 0025 0000 3155

# Authentication fails
4000 0000 0000 3055
```

---

## 📝 Testing Checklist

### Before Testing

- [ ] Stripe CLI installed and logged in
- [ ] Webhook listener running (`stripe listen`)
- [ ] Server is running and accessible
- [ ] `STRIPE_WEBHOOK_SECRET` matches CLI output
- [ ] Test user account exists

### Wallet Funding Test

- [ ] Click "Add $5" on account page
- [ ] Redirected to Stripe Checkout
- [ ] Complete payment with test card
- [ ] Webhook received (check CLI output)
- [ ] Wallet balance updated (check `/ops/debug/payments`)
- [ ] Transaction record created

### Wallet Payment Test

- [ ] Wallet has sufficient balance
- [ ] Go to merch checkout
- [ ] Check "Pay with wallet" checkbox
- [ ] Complete purchase
- [ ] Wallet balance decreased
- [ ] Purchase marked as paid
- [ ] No Stripe redirect occurred

### Direct Stripe Payment Test

- [ ] Go to merch checkout
- [ ] Don't check wallet checkbox
- [ ] Complete Stripe checkout
- [ ] Webhook received
- [ ] Purchase marked as paid

---

## 🎯 Quick Reference

### Essential Commands

```bash
# Start webhook listener
stripe listen --forward-to localhost:5000/webhooks/stripe

# Trigger test event
stripe trigger checkout.session.completed

# View events
stripe events list

# Stream events
stripe events listen

# Test checkout session
stripe checkout sessions create --mode payment --line-items ...
```

### Debug Endpoints

- `/ops/debug/payments` - Payment system status
- `/ops/debug/checkout` - Checkout system status
- `/ops/selftest` - Overall system health

### Browser Console

```javascript
// Load debug helpers
// (Copy from docs/debugging/DEBUG_CONSOLE_GUIDE.md)

// Run all checks
await ahoyDebug.runAll()

// Check payments
await ahoyDebug.checkPayments()

// Check checkout
await ahoyDebug.checkCheckout()
```

---

## 💡 Pro Tips

1. **Always run `stripe listen` first** - You need the webhook secret
2. **Use test mode** - Switch Stripe Dashboard to test mode
3. **Check server logs** - Watch for webhook processing errors
4. **Verify database** - Check that records are created/updated
5. **Test both flows** - Wallet payment AND direct Stripe payment
6. **Use debug endpoints** - `/ops/debug/payments` shows everything

---

## 🔗 Related Documentation

- **Troubleshooting:** `docs/troubleshooting/WALLET_TROUBLESHOOTING.md`
- **Debug Console:** `docs/debugging/DEBUG_CONSOLE_GUIDE.md`
- **Wallet Guide:** `docs/features/WALLET_COMPLETE_GUIDE.md`
