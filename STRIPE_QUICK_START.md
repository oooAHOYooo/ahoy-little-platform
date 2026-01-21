# ⚡ Stripe Quick Start - 20 Minutes

## ✅ What You're Seeing (GOOD!)

The webhook listener is **RUNNING CORRECTLY**:
```
> Ready! Your webhook signing secret is whsec_7e138734ecd0cdd56e502275a64bbc8f14ae4ca84bffb8c0798cb40709265dad
```

**This means:**
- ✅ Stripe CLI is working
- ✅ Webhook listener is forwarding to your server
- ✅ Ready to receive webhooks

**⚠️ KEEP THIS TERMINAL OPEN** - Don't close it!

---

## 🎯 Next Steps (Do These Now)

### Step 1: Open Webhook Monitor (Browser)

Visit: **https://app.ahoy.ooo/ops/webhooks/monitor**

This shows all webhook activity in real-time.

### Step 2: Test a Webhook (New Terminal)

**Open a NEW terminal** (keep the listener running):

```bash
cd /Users/agworkywork/ahoy-little-platform
./scripts/test_wallet_funding.sh
```

### Step 3: Watch It Work

**In Browser (monitor page):**
- Should see new transaction appear
- Auto-refreshes every 5 seconds

**In Terminal 1 (listener):**
- Should show: `--> checkout.session.completed [200 OK]`

---

## 🔧 If Webhook Not Received

### Check 1: Is Server Running?

```bash
# Check if Flask server is running on port 5000
curl http://localhost:5000/healthz
```

If not running, start it:
```bash
cd /Users/agworkywork/ahoy-little-platform
python app.py
```

### Check 2: Webhook Secret Match?

The listener shows: `whsec_7e138734ecd0cdd56e502275a64bbc8f14ae4ca84bffb8c0798cb40709265dad`

**For LOCAL testing only:** This is a test secret from Stripe CLI. Your server should accept it automatically when using `stripe listen`.

**For PRODUCTION:** You need the webhook secret from Stripe Dashboard.

### Check 3: Server Logs

Check your Flask server terminal for:
- Webhook received messages
- Any errors processing webhooks

---

## ✅ Success Checklist

- [ ] Terminal 1: Listener running (✅ You have this!)
- [ ] Browser: Monitor page open (`/ops/webhooks/monitor`)
- [ ] Terminal 2: Test script executed (`./scripts/test_wallet_funding.sh`)
- [ ] Browser: See transaction appear
- [ ] Terminal 1: See `[200 OK]` in listener output

---

## 🚀 Quick Test Commands

```bash
# Test wallet funding
./scripts/test_wallet_funding.sh

# Test merch checkout
./scripts/test_merch_checkout.sh

# Test boost
./scripts/test_boost.sh
```

---

## 📊 Debug Endpoints

If something's not working:

- `/ops/debug/payments` - Check payment system status
- `/ops/debug/checkout` - Check checkout system status
- `/ops/webhooks/monitor` - See all webhook activity

---

## ⚠️ Important Notes

1. **Keep listener terminal open** - It must stay running
2. **Server must be running** - Flask app on port 5000
3. **Use test mode** - Stripe Dashboard → Toggle to "Test mode"
4. **Monitor page auto-refreshes** - Just watch it update

---

**You're 90% there! Just test a webhook and watch it work!**
