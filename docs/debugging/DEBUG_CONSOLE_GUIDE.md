# Debug Console Guide

## 🎯 Quick Debug Endpoints

### Payment System Debug
**URL:** `GET /ops/debug/payments`

**What it checks:**
- ✅ Stripe API configuration
- ✅ Stripe API connection
- ✅ Database wallet tables (wallet_balance column, wallet_transactions table)
- ✅ Current user's wallet balance (if logged in)
- ✅ Recent wallet transactions
- ✅ Database counts (users, transactions, purchases, tips)

**Example Response:**
```json
{
  "timestamp": "2025-01-22T12:00:00Z",
  "stripe": {
    "configured": true,
    "key_prefix": "sk_live...",
    "webhook_secret_set": true,
    "api_connection": "ok",
    "api_version": "2023-10-16"
  },
  "database": {
    "wallet_balance_column": true,
    "wallet_transactions_table": true,
    "counts": {
      "users": 10,
      "wallet_transactions": 25,
      "purchases": 15,
      "tips": 8
    }
  },
  "user": {
    "logged_in": true,
    "user_id": 1,
    "wallet_balance": 25.50,
    "stripe_customer_id": "cus_ABC123",
    "recent_transactions": [...]
  },
  "status": "ok",
  "errors": []
}
```

### Checkout System Debug
**URL:** `GET /ops/debug/checkout`

**What it checks:**
- ✅ Merch catalog file exists
- ✅ Merch catalog is valid JSON
- ✅ Item count
- ✅ First 10 items with details

**Example Response:**
```json
{
  "timestamp": "2025-01-22T12:00:00Z",
  "merch_catalog": {
    "exists": true,
    "item_count": 5,
    "items": [
      {
        "id": "sample_merch1",
        "name": "Sample Merch 1",
        "price_usd": 20.00,
        "available": true
      }
    ]
  },
  "status": "ok",
  "errors": []
}
```

---

## 🖥️ Browser Console Debugging

### Add to Browser Console

Copy and paste this into your browser console to enable enhanced debugging:

```javascript
// Enhanced Debug Console for Ahoy
(function() {
  window.ahoyDebug = {
    // Check payment system
    async checkPayments() {
      try {
        const res = await fetch('/ops/debug/payments', { credentials: 'include' });
        const data = await res.json();
        console.log('💰 Payment System Status:', data);
        return data;
      } catch (e) {
        console.error('❌ Payment check failed:', e);
        return null;
      }
    },
    
    // Check checkout system
    async checkCheckout() {
      try {
        const res = await fetch('/ops/debug/checkout', { credentials: 'include' });
        const data = await res.json();
        console.log('🛒 Checkout System Status:', data);
        return data;
      } catch (e) {
        console.error('❌ Checkout check failed:', e);
        return null;
      }
    },
    
    // Get wallet balance
    async getWallet() {
      try {
        const res = await fetch('/payments/wallet', { credentials: 'include' });
        const data = await res.json();
        console.log('💳 Wallet Balance:', data);
        return data;
      } catch (e) {
        console.error('❌ Wallet check failed:', e);
        return null;
      }
    },
    
    // Test wallet funding (dry run - doesn't actually fund)
    async testWalletFund(amount = 5) {
      console.log(`🧪 Testing wallet funding for $${amount}...`);
      try {
        const res = await fetch('/payments/wallet/fund', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ amount: amount })
        });
        const data = await res.json();
        if (res.ok) {
          console.log('✅ Wallet funding test successful:', data);
          console.log('⚠️  This created a real Stripe checkout session. Do not complete payment if this was just a test.');
        } else {
          console.error('❌ Wallet funding test failed:', data);
        }
        return data;
      } catch (e) {
        console.error('❌ Wallet funding test error:', e);
        return null;
      }
    },
    
    // Get checkout error log (if available)
    getCheckoutErrors() {
      if (window.getCheckoutErrorLog) {
        const log = window.getCheckoutErrorLog();
        console.log('📋 Checkout Error Log:', JSON.parse(log));
        return JSON.parse(log);
      } else {
        console.log('ℹ️  Checkout error logging not active');
        return null;
      }
    },
    
    // Run all checks
    async runAll() {
      console.log('🔍 Running all debug checks...');
      const results = {
        payments: await this.checkPayments(),
        checkout: await this.checkCheckout(),
        wallet: await this.getWallet(),
        errors: this.getCheckoutErrors()
      };
      console.log('📊 All Debug Results:', results);
      return results;
    }
  };
  
  console.log('✅ Ahoy Debug Console loaded!');
  console.log('📖 Available commands:');
  console.log('  - ahoyDebug.checkPayments() - Check payment system');
  console.log('  - ahoyDebug.checkCheckout() - Check checkout system');
  console.log('  - ahoyDebug.getWallet() - Get wallet balance');
  console.log('  - ahoyDebug.testWalletFund(5) - Test wallet funding');
  console.log('  - ahoyDebug.getCheckoutErrors() - Get error log');
  console.log('  - ahoyDebug.runAll() - Run all checks');
})();
```

### Usage Examples

**In Browser Console:**

```javascript
// Check payment system
await ahoyDebug.checkPayments()

// Check checkout system
await ahoyDebug.checkCheckout()

// Get wallet balance
await ahoyDebug.getWallet()

// Run all checks
await ahoyDebug.runAll()

// Get checkout errors
ahoyDebug.getCheckoutErrors()
```

---

## 🔧 Stripe CLI Testing

### Install Stripe CLI

```bash
# macOS
brew install stripe/stripe-cli/stripe

# Linux
# Download from https://github.com/stripe/stripe-cli/releases

# Windows
# Download from https://github.com/stripe/stripe-cli/releases
```

### Login to Stripe CLI

```bash
stripe login
```

### Forward Webhooks to Local Server

```bash
# Forward webhooks to local development server
stripe listen --forward-to localhost:5000/webhooks/stripe

# Or for production (if you have access)
stripe listen --forward-to https://app.ahoy.ooo/webhooks/stripe
```

### Test Webhook Events

```bash
# Test wallet funding webhook
stripe trigger checkout.session.completed

# Test payment intent succeeded
stripe trigger payment_intent.succeeded

# Test with specific metadata
stripe trigger checkout.session.completed \
  --override type=wallet_fund \
  --override metadata:user_id=1 \
  --override metadata:amount=10.00
```

### View Webhook Events

```bash
# List recent events
stripe events list

# Get specific event details
stripe events retrieve evt_1234567890

# Stream events in real-time
stripe events listen
```

### Test Payment Flow

```bash
# Create a test checkout session
stripe checkout sessions create \
  --success-url "https://app.ahoy.ooo/payments/wallet/success" \
  --cancel-url "https://app.ahoy.ooo/payments/wallet/cancel" \
  --mode payment \
  --line-items price_data[currency]=usd,price_data[unit_amount]=500,price_data[product_data][name]=Test \
  --metadata user_id=1 \
  --metadata type=wallet_fund \
  --metadata amount=5.00
```

---

## 🐛 Common Issues & Solutions

### Issue: "Stripe not configured"
**Check:**
```javascript
await ahoyDebug.checkPayments()
// Look for stripe.configured: false
```

**Solution:**
- Verify `STRIPE_SECRET_KEY` is set in environment
- Check `AHOY_ENV` is set correctly (production vs development)
- Verify keys match Stripe Dashboard

### Issue: "Merch catalog not found"
**Check:**
```javascript
await ahoyDebug.checkCheckout()
// Look for merch_catalog.exists: false
```

**Solution:**
- Verify `data/merch.json` exists
- Run `python manifest.py merch` to generate catalog
- Check file permissions

### Issue: "Wallet balance column missing"
**Check:**
```javascript
await ahoyDebug.checkPayments()
// Look for database.wallet_balance_column: false
```

**Solution:**
- Run migrations: `alembic upgrade head`
- Check migration `0015_add_wallet_system` ran successfully
- Verify database connection

### Issue: "500 error on wallet funding"
**Check:**
1. Server logs for specific error
2. Browser console: `ahoyDebug.getCheckoutErrors()`
3. Payment system: `await ahoyDebug.checkPayments()`

**Solution:**
- Check Stripe API connection
- Verify user is logged in
- Check amount is valid ($1.00 - $1000.00)
- Review server logs for exceptions

---

## 📊 Debugging Workflow

### Step 1: Check System Status
```javascript
await ahoyDebug.runAll()
```

### Step 2: Check Specific Component
```javascript
// If payment issue
await ahoyDebug.checkPayments()

// If checkout issue
await ahoyDebug.checkCheckout()

// If wallet issue
await ahoyDebug.getWallet()
```

### Step 3: Check Error Logs
```javascript
// Browser errors
ahoyDebug.getCheckoutErrors()

// Server logs (check Render dashboard or terminal)
```

### Step 4: Test with Stripe CLI
```bash
# Forward webhooks
stripe listen --forward-to localhost:5000/webhooks/stripe

# Trigger test event
stripe trigger checkout.session.completed
```

### Step 5: Verify Fix
```javascript
// Re-run checks
await ahoyDebug.runAll()
```

---

## 🔗 Related Documentation

- **Troubleshooting Guide:** `docs/troubleshooting/WALLET_TROUBLESHOOTING.md`
- **Wallet Guide:** `docs/features/WALLET_COMPLETE_GUIDE.md`
- **Stripe Setup:** `docs/setup/STRIPE_SETUP_GUIDE.md`

---

## 💡 Pro Tips

1. **Always check `/ops/debug/payments` first** - It shows the most common issues
2. **Use browser console debug functions** - Faster than checking server logs
3. **Test with Stripe CLI** - Verify webhooks work before production
4. **Check error logs** - Both browser console and server logs
5. **Run all checks** - `ahoyDebug.runAll()` gives you the full picture
