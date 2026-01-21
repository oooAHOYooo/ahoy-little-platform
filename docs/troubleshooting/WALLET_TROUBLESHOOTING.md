# Wallet Feature Troubleshooting Guide

## 🔍 How to Collect Logs

### 1. Browser Console Logs (Frontend)

**How to access:**
1. Open your browser's Developer Tools:
   - **Chrome/Edge**: `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
   - **Firefox**: `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
   - **Safari**: `Cmd+Option+I` (need to enable Developer menu first)

2. Go to the **Console** tab

3. **Before testing:**
   - Click the "Clear console" button (🚫 icon) or press `Cmd+K` / `Ctrl+L`
   - This ensures you only see new errors

4. **Reproduce the issue:**
   - Try to fund wallet, or use wallet for purchase
   - Watch for red error messages

5. **Copy the logs:**
   - Right-click in console → "Save as..." OR
   - Select all (`Cmd+A` / `Ctrl+A`) → Copy (`Cmd+C` / `Ctrl+C`)
   - Paste into a text file

**What to look for:**
- ❌ Red errors (especially `400`, `401`, `500` status codes)
- ❌ `TypeError`, `ReferenceError`, `Illegal invocation`
- ❌ Failed network requests (check Network tab too)
- ⚠️ Yellow warnings (usually less critical)

---

### 2. Server Logs (Render.com)

**How to access:**

#### Option A: Render Dashboard (Easiest)
1. Go to: https://dashboard.render.com
2. Click on your service: **ahoy-little-platform**
3. Click **"Logs"** in the left sidebar
4. **Filter by time:** Use the time selector to see recent logs
5. **Copy logs:**
   - Select text in the log viewer
   - Copy (`Cmd+C` / `Ctrl+C`)
   - Or use the "Download logs" button if available

#### Option B: Render Shell (Advanced)
1. In Render dashboard → Your service → **Shell**
2. Run: `tail -f /var/log/app.log` (if logs are written to file)
3. Or check: `journalctl -u your-service` (if using systemd)

**What to look for:**
- ❌ `ERROR` or `Exception` messages
- ❌ `500 Internal Server Error`
- ❌ `AttributeError`, `KeyError`, `TypeError`
- ❌ Database connection errors
- ⚠️ `WARNING` messages
- ✅ `INFO` messages showing successful operations

---

### 3. Network Tab (Browser)

**How to access:**
1. Open Developer Tools (`F12`)
2. Go to **Network** tab
3. **Before testing:** Click "Clear" (🚫 icon)
4. **Reproduce the issue**
5. **Look for failed requests:**
   - Red entries = failed requests
   - Click on failed request → Check "Response" tab

**Key endpoints to check:**
- `POST /payments/wallet/fund` - Wallet funding
- `POST /checkout/process` - Checkout processing
- `GET /payments/wallet` - Get wallet balance
- `POST /webhooks/stripe` - Webhook processing (if you can see it)

**What to check:**
- **Status code:** Should be `200` (success) or `400` (client error)
- **Response body:** Click on request → "Response" tab → See error message
- **Request payload:** Click on request → "Payload" tab → Verify data sent

---

## 🐛 Common Issues & Solutions

### Issue 1: "400 Bad Request" when funding wallet

**Symptoms:**
- Browser console: `POST /payments/wallet/fund 400 (Bad Request)`
- User sees error message

**Debug steps:**
1. **Check browser console:**
   ```javascript
   // Look for the error response
   // Should show: { error: "..." }
   ```

2. **Check server logs:**
   ```
   # Look for:
   Wallet funding request: user_id=..., amount=...
   # Or:
   ERROR: Invalid amount / Authentication required
   ```

3. **Common causes:**
   - ❌ User not logged in → Check `user_id` in request
   - ❌ Invalid amount → Check amount is between $1.00 - $1000.00
   - ❌ Missing CSRF token → Check if endpoint is exempted

**Solution:**
- Verify user is logged in
- Check amount is valid number
- Check `app.py` has CSRF exemption: `_csrf_ext.exempt(fund_wallet)`

---

### Issue 2: Wallet balance not showing

**Symptoms:**
- Wallet shows $0.00 even after funding
- Or wallet section doesn't appear

**Debug steps:**
1. **Check browser console:**
   ```javascript
   // Look for:
   GET /payments/wallet 401 (Unauthorized)
   // Or:
   TypeError: Cannot read property 'wallet_balance' of undefined
   ```

2. **Check server logs:**
   ```
   # Look for:
   ERROR: User not found
   # Or database errors
   ```

3. **Check database:**
   ```sql
   -- Verify wallet_balance column exists
   SELECT wallet_balance FROM users WHERE id = <user_id>;
   
   -- Check if migration ran
   SELECT * FROM alembic_version;
   ```

**Solution:**
- Verify migrations ran: `alembic current` should show `0016_add_stripe_customer_id`
- Check user is logged in
- Verify `wallet_balance` column exists in database

---

### Issue 3: Wallet payment fails silently

**Symptoms:**
- User checks "Pay with wallet" but nothing happens
- Or shows error after clicking

**Debug steps:**
1. **Check browser console:**
   ```javascript
   // Look for form submission errors
   // Check if useWalletHidden value is set correctly
   console.log(document.getElementById('useWalletHidden').value);
   ```

2. **Check server logs:**
   ```
   # Look for:
   Wallet payment: user_id=..., amount=...
   # Or:
   ERROR: Insufficient wallet balance
   ERROR: Purchase record not found
   ```

3. **Check Network tab:**
   - Verify `POST /checkout/process` is sent
   - Check request payload has `use_wallet: "true"`
   - Check response status code

**Solution:**
- Verify wallet balance is sufficient
- Check checkbox is updating hidden field correctly
- Verify `deduct_wallet_balance()` is being called

---

### Issue 4: Webhook not processing wallet funding

**Symptoms:**
- User completes Stripe payment but wallet balance doesn't update
- Payment shows in Stripe but not in app

**Debug steps:**
1. **Check Stripe Dashboard:**
   - Go to: https://dashboard.stripe.com/webhooks
   - Click your endpoint → "Event deliveries"
   - Check if events show `200` (success) or `500` (error)

2. **Check server logs:**
   ```
   # Look for:
   Webhook received: checkout.session.completed
   # Or:
   ERROR: Error processing wallet funding: ...
   ```

3. **Check webhook signature:**
   ```
   # Look for:
   ERROR: Invalid webhook signature
   # This means STRIPE_WEBHOOK_SECRET is wrong
   ```

**Solution:**
- Verify `STRIPE_WEBHOOK_SECRET` matches Stripe Dashboard
- Check webhook endpoint URL is correct
- Verify `metadata.type == "wallet_fund"` is being checked

---

## 📋 Systematic Debugging Checklist

When reporting an issue, include:

### 1. What you were trying to do:
```
Example: "Trying to fund wallet with $5 from account page"
```

### 2. What happened:
```
Example: "Got 400 Bad Request error"
```

### 3. Browser Console Logs:
```
Copy all red errors and relevant warnings
```

### 4. Network Tab:
```
Screenshot or copy of failed request:
- URL: POST /payments/wallet/fund
- Status: 400
- Response: { "error": "Invalid amount" }
```

### 5. Server Logs (from Render):
```
Copy relevant ERROR or WARNING lines from last 5 minutes
```

### 6. Steps to reproduce:
```
1. Go to /account
2. Click "Add $5 (Optional)"
3. See error
```

### 7. Environment:
```
- URL: https://app.ahoy.ooo
- Browser: Chrome 120
- User: logged in as [username]
```

---

## 🔧 Quick Diagnostic Commands

### Check if migrations ran:
```bash
# In Render Shell or local terminal
alembic current
# Should show: 0016_add_stripe_customer_id (head)
```

### Check database schema:
```sql
-- Check if wallet_balance exists
\d users  -- PostgreSQL
.schema users  -- SQLite

-- Check if wallet_transactions table exists
\d wallet_transactions  -- PostgreSQL
.schema wallet_transactions  -- SQLite
```

### Check environment variables:
```bash
# In Render Shell
echo $STRIPE_SECRET_KEY  # Should show key (not empty)
echo $STRIPE_WEBHOOK_SECRET  # Should show webhook secret
echo $AHOY_ENV  # Should show "production"
```

### Test wallet endpoint directly:
```bash
# In browser console (while logged in)
fetch('/payments/wallet', { credentials: 'include' })
  .then(r => r.json())
  .then(console.log)
# Should return: { balance: 0.00, balance_cents: 0 }
```

---

## 🚨 Critical Errors to Watch For

### 1. Database Migration Errors
```
ERROR: relation "wallet_transactions" does not exist
```
**Fix:** Run `alembic upgrade head`

### 2. Missing Environment Variables
```
ERROR: Stripe not configured (missing STRIPE_SECRET_KEY)
```
**Fix:** Set environment variables in Render dashboard

### 3. Webhook Signature Mismatch
```
ERROR: Invalid webhook signature
```
**Fix:** Update `STRIPE_WEBHOOK_SECRET` in Render to match Stripe Dashboard

### 4. CSRF Token Errors
```
ERROR: CSRF validation failed
```
**Fix:** Verify `_csrf_ext.exempt(fund_wallet)` in `app.py`

### 5. Authentication Errors
```
ERROR: Authentication required
```
**Fix:** Verify user is logged in, check session

---

## 📞 When to Share Logs

**Share logs when:**
- ❌ Error persists after checking common issues
- ❌ Error message is unclear
- ❌ Multiple users experiencing same issue
- ❌ Production issue affecting real users

**What to share:**
1. ✅ Browser console errors (red text only)
2. ✅ Server log errors (last 50 lines, filter for ERROR)
3. ✅ Network tab (failed request details)
4. ✅ Steps to reproduce
5. ✅ What you expected vs what happened

**Don't share:**
- ❌ Full server logs (too much noise)
- ❌ Personal information (user IDs, emails)
- ❌ API keys or secrets (even if redacted)

---

## 🎯 Quick Reference: Log Locations

| Log Type | Where to Find | What to Look For |
|----------|---------------|------------------|
| **Browser Console** | DevTools → Console tab | JavaScript errors, failed API calls |
| **Network Tab** | DevTools → Network tab | HTTP status codes, request/response data |
| **Server Logs** | Render Dashboard → Logs | Python exceptions, database errors |
| **Stripe Logs** | Stripe Dashboard → Webhooks → Event deliveries | Webhook delivery status |

---

## 💡 Pro Tips

1. **Clear logs before testing** - Makes it easier to see new errors
2. **Test in incognito mode** - Rules out browser extension issues
3. **Check multiple browsers** - Some issues are browser-specific
4. **Test with different users** - Rules out user-specific data issues
5. **Check time zone** - Log timestamps help correlate browser/server events

---

## 🔗 Related Documentation

- **Deployment Guide:** `docs/deployment/PRODUCTION_WALLET_DEPLOYMENT.md`
- **Complete Guide:** `docs/features/WALLET_COMPLETE_GUIDE.md`
- **Integration Check:** `docs/features/WALLET_INTEGRATION_VERIFICATION.md`
