# Render.com Deployment Update Guide

## 🚨 CRITICAL: Update Production Environment Variables

The webhook secret has been updated locally. You **MUST** update it in Render.com for production to work correctly.

## Step-by-Step: Update Render Environment Variables

### 1. Access Render Dashboard
1. Go to: https://dashboard.render.com
2. Log in to your account
3. Navigate to your web service: **ahoy-little-platform**

### 2. Update Environment Variables

1. In your service, click **"Environment"** in the left sidebar
2. Find or add these variables:

#### Required Stripe Variables (UPDATE THESE):

```bash
AHOY_ENV=production
STRIPE_PUBLISHABLE_KEY=pk_live_51N3kXJGpN1YPCSA4r1jJ0A0RnyP5wREG17Q95CaI3ovFFTnR9TOM3IbDtA8pu155X4YNsB4MFe7k46UvOEXgwS17007xSa1efo
STRIPE_SECRET_KEY=mk_1N3kYFGpN1YPCSA44DdYH7AI
STRIPE_WEBHOOK_SECRET=whsec_fIVkv7yyR1GTBfmZOSLjVZ6cwPwRhluV
```

**⚠️ IMPORTANT:** The `STRIPE_WEBHOOK_SECRET` value has changed from the previous one!

### 3. Save and Redeploy

1. Click **"Save Changes"** at the bottom
2. Render will automatically trigger a new deployment
3. Wait for deployment to complete (check the "Events" tab)

### 4. Verify Deployment

After deployment completes:
1. Check the service logs for any errors
2. Verify the app is running: https://app.ahoy.ooo
3. Test webhook delivery (see testing section below)

---

## 🔍 How Webhooks Work for Merch Store vs Boost System

### Webhook Handler: `routes/stripe_webhooks.py`

The webhook endpoint `/webhooks/stripe` handles **both** merch purchases and boost payments using the same `checkout.session.completed` event, but processes them differently based on metadata.

### Flow Diagram

```
Stripe Checkout Session Completed
         ↓
Webhook: /webhooks/stripe
         ↓
Read metadata from session
         ↓
    ┌────┴────┐
    │         │
Has purchase_id?    Has type=boost/tip?
    │         │
    YES       YES
    │         │
    ↓         ↓
Update Purchase.status = "paid"    Create Tip record
(merch/tickets)                   (boost/tip)
    │                             │
    └─────────┬───────────────────┘
              ↓
        Update UserArtistPosition
        (if user_id present)
```

### 1. Merch Store Purchases

**Metadata includes:**
- `purchase_id`: ID of the Purchase record in database
- `type`: "merch" (or "ticket", etc.)

**Webhook Processing:**
1. Finds the `Purchase` record by `purchase_id`
2. Updates `Purchase.status` from "pending" → "paid"
3. Stores `stripe_id` (checkout session ID) in Purchase record
4. Sends admin notification (if `ADMIN_NOTIFY_WEBHOOK` is set)
5. **Does NOT** create a Tip record

**Code Location:** `routes/stripe_webhooks.py` lines 76-102

### 2. Boost/Tip Payments

**Metadata includes:**
- `artist_id`: Artist receiving the boost
- `user_id`: User making the boost (or "" for guests)
- `boost_amount`: Amount going to artist
- `stripe_fee`, `platform_fee`, `total_paid`: Fee breakdown
- `artist_payout`, `platform_revenue`: Payout amounts
- `type`: "boost" or "tip"

**Webhook Processing:**
1. Creates a `Tip` record with all fee breakdowns
2. Updates `UserArtistPosition` (if `user_id` is present)
   - Increments `total_contributed`
   - Updates `last_tip` timestamp
3. **Does NOT** update Purchase record (unless `purchase_id` is also present)

**Code Location:** `routes/stripe_webhooks.py` lines 104-155

### 3. Payment Intent Events (Backup)

The webhook also listens for `payment_intent.succeeded` events as a backup mechanism. This creates Tip records directly from PaymentIntent metadata.

**Code Location:** `routes/stripe_webhooks.py` lines 157-212

### Idempotency Protection

**Critical Feature:** Both handlers check for existing records before creating new ones:

- **Checkout Sessions:** Checks `stripe_checkout_session_id` uniqueness
- **Payment Intents:** Checks `stripe_payment_intent_id` uniqueness

This prevents duplicate records if Stripe retries webhook delivery.

---

## 🧪 Testing After Deployment

### Option 1: Test with Real Transaction (Recommended)

1. **Deploy with updated environment variables** (see steps above)
2. **Wait for deployment to complete**
3. **Make a small test purchase:**
   - Go to https://app.ahoy.ooo
   - Make a small boost ($1.00) or purchase a merch item
   - Complete checkout
4. **Verify in Stripe Dashboard:**
   - Go to: https://dashboard.stripe.com/webhooks
   - Click on endpoint: `we_1Ss4j3GpN1YPCSA4HSIceaUG`
   - Check "Event deliveries" tab
   - Look for recent `checkout.session.completed` event
   - Verify response code is `200` (green)
5. **Verify in Database:**
   - Check that Tip record was created (for boosts)
   - Check that Purchase.status = "paid" (for merch)
   - Verify no duplicate records

### Option 2: Send Test Event from Stripe Dashboard

1. Go to: https://dashboard.stripe.com/webhooks
2. Click on your webhook endpoint
3. Click "Send test webhook"
4. Select event: `checkout.session.completed`
5. Click "Send test webhook"
6. Check your application logs for webhook processing

### Option 3: Use Stripe CLI (Local Testing)

If testing locally before deploying:

```bash
# Forward live events to local server
stripe listen --forward-to localhost:5000/webhooks/stripe --live

# In another terminal, trigger test event
stripe trigger checkout.session.completed --live
```

---

## ✅ Verification Checklist

After updating Render environment variables:

- [ ] Environment variables saved in Render dashboard
- [ ] Deployment completed successfully
- [ ] Application is accessible at https://app.ahoy.ooo
- [ ] Webhook endpoint shows as active in Stripe Dashboard
- [ ] Test transaction completed successfully
- [ ] Webhook delivery shows `200` response in Stripe Dashboard
- [ ] Database records created correctly (Tip or Purchase)
- [ ] No duplicate records created

---

## 🆘 Troubleshooting

### Webhook Returns 400 "Invalid signature"

**Cause:** Webhook secret doesn't match  
**Fix:** Verify `STRIPE_WEBHOOK_SECRET` in Render matches the secret in Stripe Dashboard

### Webhook Returns 500 Error

**Cause:** Application error processing webhook  
**Fix:** Check Render service logs for error details

### No Webhook Events Received

**Cause:** Webhook endpoint not active or URL incorrect  
**Fix:** 
1. Verify webhook endpoint is enabled in Stripe Dashboard
2. Check webhook URL matches: `https://app.ahoy.ooo/webhooks/stripe`
3. Verify SSL certificate is valid (green checkmark in Dashboard)

### Duplicate Records Created

**Cause:** Idempotency check not working  
**Fix:** Check that `stripe_checkout_session_id` or `stripe_payment_intent_id` fields are properly indexed and unique in database

---

## 📊 Monitoring

### Stripe Dashboard
- **Webhook Deliveries:** https://dashboard.stripe.com/webhooks → [endpoint] → Event deliveries
- **API Logs:** https://dashboard.stripe.com/logs

### Render Dashboard
- **Service Logs:** Render → [service] → Logs
- **Metrics:** Render → [service] → Metrics

---

## 🔗 Quick Links

- **Render Dashboard:** https://dashboard.render.com
- **Stripe Dashboard:** https://dashboard.stripe.com
- **Webhook Endpoint:** https://dashboard.stripe.com/webhooks
- **Production App:** https://app.ahoy.ooo
