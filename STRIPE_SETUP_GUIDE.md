# Stripe Setup Guide: Terminal vs Dashboard

This guide explains what can be automated via terminal/CLI vs what requires the Stripe Dashboard (website).

## ✅ Can Be Automated (Terminal/CLI)

### 1. **Creating Webhook Endpoints**
- ✅ **Automated**: Use Stripe CLI or API to create webhook endpoints
- ✅ **Automated**: Configure which events to listen for
- ✅ **Automated**: Get webhook signing secret automatically

**Commands:**
```bash
# Via Stripe CLI
stripe webhook_endpoints create \
  --url "https://yourdomain.com/webhooks/stripe" \
  --enabled-events checkout.session.completed \
  --enabled-events payment_intent.succeeded \
  --api-key sk_live_...

# Or use our automation script
python scripts/setup_stripe.py
# or
bash scripts/setup_stripe.sh
```

### 2. **Setting Environment Variables**
- ✅ **Automated**: Script can generate `.env` file with all keys
- ✅ **Automated**: Can export variables directly to shell

### 3. **Testing Webhooks Locally**
- ✅ **Automated**: Use `stripe listen` to forward events to local server
- ✅ **Automated**: Use `stripe trigger` to send test events

**Commands:**
```bash
# Forward webhooks to local server
stripe listen --forward-to localhost:5000/webhooks/stripe

# Trigger test event
stripe trigger checkout.session.completed
```

### 4. **Listing/Managing Webhooks**
- ✅ **Automated**: List all webhook endpoints
- ✅ **Automated**: Delete webhook endpoints
- ✅ **Automated**: Update webhook endpoints

**Commands:**
```bash
# List all webhooks
stripe webhook_endpoints list

# Delete a webhook
stripe webhook_endpoints delete we_xxx
```

### 5. **Viewing API Logs**
- ✅ **Automated**: Stream API request/response logs in real-time

**Commands:**
```bash
stripe logs tail
```

## ❌ Must Use Dashboard (Website)

### 1. **Getting Live API Keys (Initial Setup)**
- ❌ **Manual**: Must go to Dashboard to view/copy live API keys
- ❌ **Manual**: Live keys are only visible in Dashboard (security)
- ✅ **Note**: Once you have them, you can store them in env vars

**Where to go:**
- https://dashboard.stripe.com/apikeys
- Switch to "Live mode" (toggle in top right)
- Copy Publishable key (`pk_live_...`) and Secret key (`sk_live_...`)

### 2. **Activating Live Mode**
- ❌ **Manual**: Must complete business verification in Dashboard
- ❌ **Manual**: Must provide business information, bank account, etc.

**Where to go:**
- https://dashboard.stripe.com/settings/account
- Complete "Activate account" flow

### 3. **Viewing Webhook Delivery Logs**
- ❌ **Manual**: Dashboard provides best UI for viewing delivery history
- ❌ **Manual**: See retry attempts, failures, response codes
- ⚠️ **Partial**: CLI can show some logs, but Dashboard is better for debugging

**Where to go:**
- https://dashboard.stripe.com/webhooks
- Click on your webhook endpoint
- View "Event deliveries" tab

### 4. **Verifying SSL/TLS**
- ❌ **Manual**: Dashboard shows SSL status for webhook endpoints
- ❌ **Manual**: Must ensure your domain has valid HTTPS certificate

**Where to go:**
- https://dashboard.stripe.com/webhooks
- Check that webhook shows green checkmark for SSL

### 5. **Monitoring & Alerts**
- ❌ **Manual**: Set up email alerts for failed webhooks in Dashboard
- ❌ **Manual**: Configure notification preferences

**Where to go:**
- https://dashboard.stripe.com/settings/notifications

## 🚀 Quick Start: Automated Setup

We've created automation scripts to handle what can be automated:

### Option 1: Python Script (Recommended)
```bash
python scripts/setup_stripe.py
```

### Option 2: Bash Script
```bash
bash scripts/setup_stripe.sh
```

Both scripts will:
1. ✅ Check if Stripe CLI is installed
2. ✅ Prompt for API keys (or try to get from CLI config)
3. ✅ Create webhook endpoint automatically
4. ✅ Extract webhook signing secret
5. ✅ Generate `.env.stripe.{mode}` file with all variables

### Prerequisites
1. Install Stripe CLI:
   ```bash
   # macOS
   brew install stripe/stripe-cli/stripe
   
   # Linux/Windows
   # Download from: https://github.com/stripe/stripe-cli/releases
   ```

2. Login to Stripe CLI:
   ```bash
   stripe login
   ```

## 📋 Manual Steps Checklist

After running the automation script, you still need to:

1. **Get Live API Keys** (if using live mode):
   - [ ] Go to https://dashboard.stripe.com/apikeys
   - [ ] Switch to Live mode
   - [ ] Copy Publishable key and Secret key
   - [ ] Run script again with these keys

2. **Verify Webhook Endpoint**:
   - [ ] Go to https://dashboard.stripe.com/webhooks
   - [ ] Confirm webhook endpoint exists
   - [ ] Verify URL is correct
   - [ ] Check SSL status (green checkmark)
   - [ ] Verify events: `checkout.session.completed`, `payment_intent.succeeded`

3. **Test Webhook Delivery**:
   - [ ] Send test event from Dashboard
   - [ ] Check your server logs to confirm receipt
   - [ ] Verify webhook is processed correctly

4. **Set Environment Variables in Production**:
   - [ ] Add variables to Render/Heroku/etc.
   - [ ] Or export from generated `.env.stripe.live` file

## 🔍 Verification Commands

After setup, verify everything works:

```bash
# Check webhook endpoint exists
stripe webhook_endpoints list

# Test webhook locally
stripe listen --forward-to localhost:5000/webhooks/stripe

# Trigger test event
stripe trigger checkout.session.completed

# View API logs
stripe logs tail
```

## 📝 Summary

| Task | Automated? | Method |
|------|------------|--------|
| Create webhook endpoint | ✅ Yes | CLI/API |
| Get webhook secret | ✅ Yes | CLI/API |
| Set environment variables | ✅ Yes | Script |
| Test webhooks | ✅ Yes | CLI |
| Get live API keys | ❌ No | Dashboard only |
| Activate live mode | ❌ No | Dashboard only |
| View delivery logs | ⚠️ Partial | Dashboard (better) |
| Verify SSL | ❌ No | Dashboard |
| Monitor alerts | ❌ No | Dashboard |

## 🆘 Troubleshooting

**Webhook creation fails:**
- Ensure your domain has valid HTTPS
- Check that Stripe CLI is logged in: `stripe config --list`
- Verify API key has correct permissions

**Can't get API keys from CLI:**
- CLI config may not have keys stored
- Manually enter keys when script prompts

**Webhook not receiving events:**
- Check webhook endpoint is active in Dashboard
- Verify SSL certificate is valid
- Check your server is accessible from internet
- Review webhook delivery logs in Dashboard
