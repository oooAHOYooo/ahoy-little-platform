# Production Wallet Deployment Checklist

## ✅ What Will Work Automatically

Since you've pushed to `main`, Render.com will:
1. ✅ **Auto-deploy** the latest code
2. ✅ **Run migrations automatically** (via `scripts/migrate_and_start.sh`)
   - This runs `alembic upgrade heads` before starting the app
   - Migrations `0015_add_wallet_system` and `0016_add_stripe_customer_id` will be applied

## ⚠️ What You Need to Verify

### 1. Database Migrations (Should Run Automatically)

**Check:** After deployment, verify migrations ran:

1. Go to Render.com → Your service → **Logs**
2. Look for: `"Running database migrations..."` and `"alembic upgrade heads"`
3. Should see: `INFO  [alembic.runtime.migration] Running upgrade ... -> 0015_add_wallet_system`
4. Should see: `INFO  [alembic.runtime.migration] Running upgrade ... -> 0016_add_stripe_customer_id`

**If migrations didn't run:**
- SSH into Render service (if available) or use Render Shell
- Run manually: `alembic upgrade head`

### 2. Environment Variables (Should Already Be Set)

**Verify these are set in Render.com → Environment:**

```bash
AHOY_ENV=production
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_... (or mk_live_...)
STRIPE_WEBHOOK_SECRET=whsec_...
```

**Note:** These should already be set from previous Stripe setup.

### 3. Webhook Endpoint (Should Already Be Configured)

**Verify in Stripe Dashboard:**
- Go to: https://dashboard.stripe.com/webhooks
- Check endpoint: `https://app.ahoy.ooo/webhooks/stripe`
- Events enabled: `checkout.session.completed`, `payment_intent.succeeded`
- Status: ✅ Enabled

## 🧪 Testing After Deployment

### Test 1: Wallet Funding
1. Go to: https://app.ahoy.ooo/account
2. Click "Add $5 (Optional)" in wallet section
3. Should redirect to Stripe Checkout
4. Complete payment with test card: `4242 4242 4242 4242`
5. Should redirect back to `/payments/wallet/success`
6. Wallet balance should show $5.00

### Test 2: Wallet Payment
1. Go to: https://app.ahoy.ooo/merch (or any merch page)
2. Select an item → Checkout
3. Should see wallet balance on checkout page
4. Check "Pay instantly from wallet"
5. Button should say "Pay Instantly with Wallet"
6. Click button → Purchase should complete instantly
7. Wallet balance should decrease

### Test 3: Direct Stripe Payment (No Wallet)
1. Go to: https://app.ahoy.ooo/merch
2. Select item → Checkout
3. **Don't** check wallet checkbox
4. Button should say "Pay $X.XX with Card"
5. Click button → Should redirect to Stripe Checkout
6. Complete payment → Should work normally

## 🔍 Troubleshooting

### Issue: "Wallet balance not showing"
**Check:**
- Database migrations ran successfully
- User is logged in
- Check browser console for errors

### Issue: "Wallet funding fails"
**Check:**
- Stripe keys are set correctly in Render environment
- Webhook endpoint is configured
- Check Render logs for errors

### Issue: "Migrations didn't run"
**Solution:**
1. Go to Render.com → Service → Shell (or SSH)
2. Run: `alembic upgrade head`
3. Check logs for migration output

### Issue: "Wallet payment fails"
**Check:**
- User has sufficient wallet balance
- Check Render logs for error messages
- Verify `deduct_wallet_balance()` function is working

## 📋 Quick Verification Commands

If you have access to Render Shell or database:

```bash
# Check if wallet_balance column exists
psql $DATABASE_URL -c "\d users" | grep wallet_balance

# Check if wallet_transactions table exists
psql $DATABASE_URL -c "\d wallet_transactions"

# Check migration status
alembic current
```

## ✅ Summary

**What happens automatically:**
- ✅ Code deploys (from `main` branch)
- ✅ Migrations run (via `migrate_and_start.sh`)
- ✅ App starts with new wallet features

**What you need to verify:**
- ⚠️ Check Render logs to confirm migrations ran
- ⚠️ Test wallet funding flow
- ⚠️ Test wallet payment flow
- ⚠️ Test direct Stripe payment (should still work)

**If everything is set up correctly, the wallet feature should work immediately after deployment!**
