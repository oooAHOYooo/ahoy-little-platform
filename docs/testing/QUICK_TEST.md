# 🚀 Quick Test Guide - Stripe Webhooks

## Step 1: Start Webhook Listener (REQUIRED)

**In Terminal 1:**
```bash
cd /Users/agworkywork/ahoy-little-platform
./scripts/start_stripe_listen.sh
```

**You should see:**
```
🚀 Starting Stripe webhook listener...
📡 Forwarding to: http://localhost:5000/webhooks/stripe

⚠️  Keep this terminal open to receive webhooks
💡 Press Ctrl+C to stop

> Ready! Your webhook signing secret is whsec_... (^C to quit)
```

**⚠️ IMPORTANT:** Keep this terminal open! This forwards webhooks to your server.

---

## Step 2: Open Webhook Monitor

**In Browser:**
Visit: `https://app.ahoy.ooo/ops/webhooks/monitor`

You'll see:
- Recent wallet transactions
- Recent purchases
- Recent tips/boosts
- Auto-refreshes every 5 seconds

---

## Step 3: Test Webhooks

**In Terminal 2 (new terminal, keep Terminal 1 running):**

```bash
cd /Users/agworkywork/ahoy-little-platform

# Test wallet funding
./scripts/test_wallet_funding.sh

# Test merch checkout
./scripts/test_merch_checkout.sh

# Test boost
./scripts/test_boost.sh
```

---

## Step 4: Watch Results

**In Browser (monitor page):**
- Page auto-refreshes every 5 seconds
- New transactions appear automatically
- Check timestamps to see latest activity

**In Terminal 1 (listener):**
- You'll see webhook delivery logs
- Shows if webhook was received successfully
- Shows any errors

---

## ✅ What Success Looks Like

### Terminal 1 (Listener):
```
2025-01-22 12:00:00   --> checkout.session.completed [200 OK]
```

### Browser (Monitor):
- New transaction appears in "Recent Wallet Transactions"
- Shows type: "fund", amount: $10.00
- Balance after updated

### Terminal 2 (Test Script):
```
✅ Test event triggered!
📊 Check /ops/webhooks/monitor to see the result
```

---

## ❌ Troubleshooting

### "No such file or directory"
**Problem:** Used `/scripts/` instead of `./scripts/`
**Fix:** Use `./scripts/start_stripe_listen.sh` (with `./`)

### Webhook not received
**Check:**
1. Is listener running? (Terminal 1 should show "Ready!")
2. Is server running? (Check `http://localhost:5000`)
3. Check monitor page for errors

### Test event triggered but nothing in monitor
**Check:**
1. Is webhook listener running?
2. Is server running and accessible?
3. Check server logs for webhook processing errors
4. Visit `/ops/debug/payments` to check system status

---

## 🎯 Quick Checklist

- [ ] Terminal 1: `./scripts/start_stripe_listen.sh` running
- [ ] Browser: `/ops/webhooks/monitor` open
- [ ] Terminal 2: `./scripts/test_wallet_funding.sh` executed
- [ ] Browser: See new transaction appear
- [ ] Terminal 1: See webhook delivery log

---

**Everything is set up and ready! Just start the listener first.**
