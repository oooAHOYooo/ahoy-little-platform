# 🔄 When You Come Back - Stripe Testing Guide

## 📋 Current Status

**✅ Webhook Listener:** Running and ready
- Terminal shows: `> Ready! Your webhook signing secret is whsec_...`
- This means Stripe CLI is forwarding webhooks to your server
- **Keep this terminal open!**

---

## 🎯 What To Do Next (5 Minutes)

### Step 1: Check Server Status

**Is your Flask server running?**

```bash
# Check if server is running
curl http://localhost:5000/healthz
```

**If you see:** `{"ok":true,"version":"..."}` → ✅ Server is running

**If you see:** `Connection refused` → Start server:
```bash
cd /Users/agworkywork/ahoy-little-platform
python app.py
```

---

### Step 2: Open Webhook Monitor

**In Browser:**
Visit: **https://app.ahoy.ooo/ops/webhooks/monitor**

**What you should see:**
- Recent Wallet Transactions table (may be empty if no transactions yet)
- Recent Purchases table
- Recent Tips/Boosts table
- Page auto-refreshes every 5 seconds
- Liquid glass design

---

### Step 3: Test a Webhook

**Open a NEW terminal** (keep the listener running in Terminal 1):

```bash
cd /Users/agworkywork/ahoy-little-platform
./scripts/test_wallet_funding.sh
```

**Expected output:**
```
🧪 Testing wallet funding webhook...
User ID: 1
Amount: $10.00

Setting up fixture for: product
Running fixture for: product
...
Trigger succeeded! Check dashboard for event details.

✅ Test event triggered!
📊 Check /ops/webhooks/monitor to see the result
```

---

### Step 4: Watch It Work

**In Browser (Monitor Page):**
- Wait 5-10 seconds (page auto-refreshes)
- **You should see:**
  - New row in "Recent Wallet Transactions" table
  - Type: `fund`
  - Amount: `$10.00`
  - Balance After: `$10.00` (or higher if you had balance)
  - Timestamp: Just now

**In Terminal 1 (Listener):**
- **You should see:**
  ```
  2025-01-22 12:00:00   --> checkout.session.completed [200 OK]
  ```
- Green `[200 OK]` means webhook was received successfully

---

## ✅ Success Indicators

### Everything Working:
- ✅ Terminal 1: Listener shows `[200 OK]`
- ✅ Browser: New transaction appears in monitor
- ✅ Browser: Transaction shows correct amount and type
- ✅ Browser: Timestamp is recent (within last minute)

### If You See This, It's Working:
```
Terminal 1 (Listener):
  --> checkout.session.completed [200 OK]

Browser (Monitor):
  Recent Wallet Transactions:
  [New Row] fund | $10.00 | $10.00 | Just now
```

---

## ❌ Troubleshooting

### Problem: No transaction appears in monitor

**Check 1: Is server running?**
```bash
curl http://localhost:5000/healthz
```
If not, start it: `python app.py`

**Check 2: Is listener still running?**
- Terminal 1 should show "Ready!" message
- If closed, restart: `./scripts/start_stripe_listen.sh`

**Check 3: Check server logs**
- Look at Flask server terminal for errors
- Should see webhook processing messages

**Check 4: Verify webhook endpoint**
- Visit: `/ops/debug/payments`
- Should show Stripe configuration status

---

### Problem: Listener shows error

**Error: "Connection refused"**
- Server not running → Start with `python app.py`

**Error: "Invalid signature"**
- Webhook secret mismatch
- For local testing with `stripe listen`, this should work automatically
- Check `/ops/debug/payments` for configuration status

**Error: "404 Not Found"**
- Webhook endpoint not found
- Check server is running on correct port (5000)
- Verify route exists: `/webhooks/stripe`

---

### Problem: Transaction appears but wallet balance not updated

**Check database:**
```bash
# If you have database access
SELECT wallet_balance FROM users WHERE id = 1;
```

**Check webhook processing:**
- Visit `/ops/debug/payments`
- Check "recent_transactions" array
- Verify transaction was created

**Check server logs:**
- Look for webhook processing errors
- Check for database connection issues

---

## 🧪 Other Test Scripts

Once wallet funding works, try these:

```bash
# Test merch checkout
./scripts/test_merch_checkout.sh

# Test boost/tip
./scripts/test_boost.sh
```

Each should:
1. Trigger webhook event
2. Show in listener terminal as `[200 OK]`
3. Appear in monitor page within 5-10 seconds

---

## 📊 Debug Endpoints

If something's not working, check these:

### `/ops/debug/payments`
- Stripe configuration status
- Database wallet tables
- Current user wallet balance
- Recent transactions

### `/ops/debug/checkout`
- Merch catalog status
- Item count and details

### `/ops/webhooks/monitor`
- All recent webhook activity
- Real-time transaction view

---

## 🎯 Quick Checklist

When you come back, verify:

- [ ] Terminal 1: Listener running (`> Ready!`)
- [ ] Server: Running on port 5000 (`curl http://localhost:5000/healthz`)
- [ ] Browser: Monitor page open (`/ops/webhooks/monitor`)
- [ ] Test: Run `./scripts/test_wallet_funding.sh`
- [ ] Verify: Transaction appears in monitor
- [ ] Verify: Listener shows `[200 OK]`

---

## 💡 Pro Tips

1. **Keep listener running** - Don't close Terminal 1
2. **Monitor auto-refreshes** - Just watch it update
3. **Check both places** - Terminal 1 (listener) AND Browser (monitor)
4. **Test one at a time** - Run one test, verify, then next
5. **Use debug endpoints** - `/ops/debug/payments` shows everything

---

## 🚀 Expected Flow

```
1. Run test script
   ↓
2. Stripe CLI triggers event
   ↓
3. Listener forwards to server
   ↓
4. Server processes webhook
   ↓
5. Database updated
   ↓
6. Monitor page shows transaction (auto-refresh)
```

**Total time:** 5-10 seconds from test to visible result

---

## 📝 Notes

- **Webhook secret shown in listener** is for LOCAL testing only
- **Production webhook secret** is different (from Stripe Dashboard)
- **Monitor page refreshes automatically** - no need to manually refresh
- **All test scripts are in** `./scripts/` directory
- **All scripts are executable** - just run them directly

---

## 🔗 Quick Links

- **Monitor:** https://app.ahoy.ooo/ops/webhooks/monitor
- **Debug Payments:** https://app.ahoy.ooo/ops/debug/payments
- **Debug Checkout:** https://app.ahoy.ooo/ops/debug/checkout
- **Stripe Dashboard:** https://dashboard.stripe.com

---

**Everything is set up! Just test and watch it work! 🎉**
