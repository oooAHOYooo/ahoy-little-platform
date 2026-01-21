# Wallet Feature - Complete Implementation Guide

## Overview

The Ahoy wallet system allows users to fund their account with money via Stripe Checkout and use that balance for all purchases (boosts and merch) throughout the platform. Users can also continue using Stripe directly as an alternative payment method.

**Key Benefits:**
- **Convenience:** Pre-fund wallet once, use for multiple purchases
- **Flexibility:** Choose wallet or Stripe for each purchase
- **Cost Savings:** No Stripe fees on wallet payments (fees paid once during funding)
- **Transaction History:** Complete audit trail of all wallet activity

---

## What Was Implemented

### 1. Database Schema Changes

#### User Model Enhancement
- Added `wallet_balance` field to the `User` model
- Type: `Numeric(10, 2)` (supports up to $99,999,999.99)
- Default: `0.00`
- Stored in the `users` table

**Migration:** `alembic/versions/0015_add_wallet_system.py`

#### New WalletTransaction Model
Created a new table to track all wallet activity:

```python
class WalletTransaction(Base):
    user_id: Integer (FK to users.id)
    type: String(50)  # 'fund', 'spend', 'refund'
    amount: Numeric(10, 2)
    balance_before: Numeric(10, 2)
    balance_after: Numeric(10, 2)
    description: String(255)
    reference_id: String(255)  # Stripe session ID, purchase ID, etc.
    reference_type: String(50)  # 'stripe_checkout', 'purchase', 'boost'
    created_at: DateTime
```

**Transaction Types:**
- `fund`: Money added to wallet
- `spend`: Money used for purchases
- `refund`: Money refunded (future feature)

### 2. API Endpoints

#### GET `/payments/wallet`
Get current user's wallet balance.

**Response:**
```json
{
  "balance": 25.50,
  "balance_cents": 2550
}
```

#### POST `/payments/wallet/fund`
Create a Stripe Checkout session to fund the wallet.

**Request:**
```json
{
  "amount": 10.00
}
```

**Response:**
```json
{
  "checkout_url": "https://checkout.stripe.com/pay/cs_...",
  "session_id": "cs_..."
}
```

**Features:**
- Minimum funding: $1.00
- Maximum funding: $1,000.00 per transaction
- Creates Stripe Checkout session with metadata: `type: "wallet_fund"`, `user_id`, `amount`

#### POST `/payments/wallet/use` (Internal)
Deducts from wallet balance for a payment.

**Request:**
```json
{
  "amount": 5.00,
  "description": "Boost payment",
  "reference_id": "123",
  "reference_type": "boost"
}
```

**Response:**
```json
{
  "success": true,
  "balance_after": 20.50,
  "amount_used": 5.00
}
```

**Features:**
- Validates sufficient balance before deducting
- Creates transaction record
- Returns error if insufficient balance

#### GET `/payments/wallet/transactions`
Get wallet transaction history.

**Query Parameters:**
- `limit`: Number of transactions (default: 50, max: 100)

**Response:**
```json
{
  "transactions": [
    {
      "id": 1,
      "type": "fund",
      "amount": 10.00,
      "balance_before": 0.00,
      "balance_after": 10.00,
      "description": "Wallet funding via Stripe",
      "reference_id": "cs_test_...",
      "reference_type": "stripe_checkout",
      "created_at": "2025-01-22T12:00:00Z"
    }
  ]
}
```

### 3. Webhook Integration

#### Wallet Funding Webhook Handler
Modified `routes/stripe_webhooks.py` to handle wallet funding:

**Flow:**
1. Stripe sends `checkout.session.completed` event
2. Webhook handler checks metadata for `type == "wallet_fund"`
3. If found, extracts `user_id` and `amount` from metadata
4. Updates user's `wallet_balance`
5. Creates `WalletTransaction` record with type `fund`
6. Returns success

**Code Location:** `routes/stripe_webhooks.py` lines 74-104

**Key Features:**
- Idempotent: Won't double-fund if webhook is retried
- Secure: Only processes verified Stripe webhooks
- Atomic: Database transaction ensures consistency

### 4. Checkout Integration

#### Modified Checkout Process
Updated `app.py` checkout handler to support wallet payments:

**Flow:**
1. User initiates checkout (boost or merch)
2. If `use_wallet=true` in form data:
   - Calculates total charge (including fees for boosts)
   - Calls `deduct_wallet_balance()` helper function
   - If successful:
     - Marks purchase as paid
     - Creates Tip record (for boosts)
     - Updates portfolio (for boosts)
     - Returns success
   - If insufficient balance:
     - Returns error, falls back to Stripe payment
3. If wallet not used or insufficient:
   - Proceeds with normal Stripe Checkout flow

**Code Location:** `app.py` lines 958-1008

**Key Features:**
- Seamless fallback to Stripe if wallet insufficient
- No Stripe fees for wallet payments (saves user money)
- Same purchase flow regardless of payment method

### 5. UI Integration

#### Account Page (`/account`)
Added wallet section showing:
- Current wallet balance (large, prominent display)
- "Fund Wallet" button (opens prompt, creates Stripe checkout)
- "History" link (view transaction history)
- Helpful text explaining wallet usage

**Code Location:** `templates/account.html`

#### Checkout Page
Enhanced checkout to show:
- Wallet balance (if user logged in)
- Checkbox: "Pay with wallet balance" (if sufficient balance)
- "Fund Wallet" link (if insufficient balance)
- Falls back to Stripe card payment

**Code Location:** `templates/checkout.html`

**Visual Design:**
- Purple gradient background for wallet section
- Clear balance display
- Intuitive checkbox for wallet payment
- Seamless integration with existing checkout flow

### 6. Helper Functions

#### `deduct_wallet_balance()` Function
Created reusable helper function in `blueprints/payments.py`:

**Purpose:** Deduct from wallet balance atomically

**Parameters:**
- `user_id`: User ID
- `amount`: Amount to deduct (Decimal)
- `description`: Transaction description
- `reference_id`: Purchase ID, etc.
- `reference_type`: Type of purchase

**Returns:**
- `(success: bool, error: str or None, balance_after: Decimal or None)`

**Features:**
- Atomic database transaction
- Balance validation
- Transaction record creation
- Can be called from anywhere in the codebase

**Code Location:** `blueprints/payments.py` lines 538-580

---

## Payment Flow Comparison

### Option 1: Wallet Payment (New)

```
User has wallet balance
    ↓
User initiates boost/merch purchase
    ↓
Checkout page shows wallet balance
    ↓
User checks "Pay with wallet balance"
    ↓
Form submits with use_wallet=true
    ↓
Backend deducts from wallet
    ↓
Purchase marked as paid
    ↓
For boosts: Tip record created, portfolio updated
    ↓
Transaction history updated
    ↓
✅ Complete (no Stripe fees!)
```

### Option 2: Direct Stripe Payment (Existing)

```
User initiates boost/merch purchase
    ↓
Checkout page (no wallet or wallet insufficient)
    ↓
User clicks "Complete Checkout"
    ↓
Redirected to Stripe Checkout
    ↓
User enters card details
    ↓
Stripe processes payment
    ↓
Webhook: checkout.session.completed
    ↓
Backend processes webhook:
  - For boosts: Creates Tip record
  - For merch: Updates Purchase.status
    ↓
✅ Complete (Stripe fees apply)
```

---

## Testing Guide with Stripe CLI

### Quick Start

1. **Run Database Migration:**
   ```bash
   cd /Users/agworkywork/ahoy-little-platform
   alembic upgrade head
   ```
   This adds:
   - `wallet_balance` column to `users` table
   - `wallet_transactions` table

2. **Start Your Flask App:**
   ```bash
   python app.py
   # or
   flask run
   ```

3. **Start Stripe Webhook Listener:**
   ```bash
   # In a separate terminal
   stripe listen --forward-to localhost:5000/webhooks/stripe
   ```
   This will:
   - Forward webhook events to your local app
   - Show webhook events in real-time
   - Provide a webhook signing secret (use this for local testing)

### Testing Wallet Funding

#### Method 1: Via UI (Recommended)

1. **Login to your app:**
   - Go to `http://localhost:5000/account`
   - Login with your account

2. **Fund wallet:**
   - Click "Fund Wallet" button
   - Enter amount (e.g., `10.00`)
   - Click OK

3. **Complete Stripe Checkout:**
   - You'll be redirected to Stripe Checkout
   - Use test card: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., `12/25`)
   - CVC: Any 3 digits (e.g., `123`)
   - Complete payment

4. **Verify in Stripe CLI:**
   - You should see `checkout.session.completed` event
   - Check metadata: `type: "wallet_fund"`

5. **Verify in database:**
   ```sql
   -- Check wallet balance
   SELECT id, email, wallet_balance FROM users WHERE id = <your_user_id>;
   
   -- Check transaction
   SELECT * FROM wallet_transactions WHERE user_id = <your_user_id> ORDER BY created_at DESC LIMIT 1;
   ```

6. **Verify in UI:**
   - Refresh `/account` page
   - Wallet balance should be updated

#### Method 2: Via API

```bash
# 1. Get your session cookie (login first via browser)

# 2. Create funding session
curl -X POST http://localhost:5000/payments/wallet/fund \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<your_session_cookie>" \
  -d '{"amount": 25.00}'

# Response will include checkout_url
# Open that URL in browser and complete payment
```

#### Method 3: Trigger Test Webhook Directly

```bash
# This simulates a wallet funding webhook
stripe trigger checkout.session.completed \
  --add checkout_session:metadata[type]=wallet_fund \
  --add checkout_session:metadata[user_id]=1 \
  --add checkout_session:metadata[amount]=10.00 \
  --add checkout_session:id=cs_test_wallet_123
```

**Note:** This creates a test event. For real funding, use Method 1 or 2.

### Testing Wallet Payments

#### Test Boost with Wallet

1. **Ensure wallet has balance:**
   - Fund wallet first (see above)

2. **Initiate boost:**
   - Go to an artist page
   - Click "Boost" button
   - Enter amount (e.g., `5.00`)

3. **Use wallet payment:**
   - On checkout page, you should see wallet balance
   - Check "Pay with wallet balance" checkbox
   - Click "Complete Checkout"

4. **Verify:**
   - Purchase should complete immediately (no Stripe redirect)
   - Wallet balance should be deducted
   - Tip record should be created
   - Portfolio should be updated

5. **Check database:**
   ```sql
   -- Check wallet balance decreased
   SELECT wallet_balance FROM users WHERE id = <user_id>;
   
   -- Check transaction record
   SELECT * FROM wallet_transactions WHERE user_id = <user_id> AND type = 'spend' ORDER BY created_at DESC LIMIT 1;
   
   -- Check tip record
   SELECT * FROM tips WHERE user_id = <user_id> ORDER BY created_at DESC LIMIT 1;
   ```

#### Test Merch with Wallet

1. **Ensure wallet has balance**

2. **Add merch to cart:**
   - Go to `/merch`
   - Select an item
   - Click "Buy"

3. **Use wallet payment:**
   - On checkout, check "Pay with wallet balance"
   - Submit

4. **Verify:**
   - Purchase marked as paid
   - Wallet balance deducted
   - Transaction record created

### Testing Stripe Direct Payments (Fallback)

#### Test Boost with Stripe (No Wallet)

1. **Initiate boost:**
   - Go to artist page
   - Click "Boost"
   - Enter amount

2. **Use Stripe payment:**
   - On checkout, DON'T check wallet checkbox
   - Click "Complete Checkout"
   - Complete Stripe Checkout with test card

3. **Verify webhook:**
   - Check Stripe CLI for `checkout.session.completed`
   - Metadata should have `type: "boost"` (not "wallet_fund")

4. **Verify:**
   - Tip record created
   - Portfolio updated
   - Wallet balance unchanged

#### Test Merch with Stripe

1. **Add merch to cart**

2. **Complete Stripe checkout:**
   - Don't use wallet
   - Complete payment

3. **Verify:**
   - Purchase marked as paid
   - Webhook processed
   - Wallet unchanged

### Testing Edge Cases

#### Insufficient Wallet Balance

1. **Fund wallet with small amount** (e.g., $1.00)

2. **Try to make larger purchase** (e.g., $10.00 boost)

3. **Expected behavior:**
   - Checkout shows "Insufficient wallet balance"
   - Option to fund wallet or use Stripe
   - If you check wallet checkbox, should show error

#### Wallet Funding Limits

```bash
# Test minimum ($1.00)
curl -X POST http://localhost:5000/payments/wallet/fund \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{"amount": 0.50}'
# Should return error: "Minimum funding amount is $1.00"

# Test maximum ($1,000.00)
curl -X POST http://localhost:5000/payments/wallet/fund \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{"amount": 2000.00}'
# Should return error: "Maximum funding amount is $1,000.00"
```

### Monitoring Webhooks

#### View Webhook Events in Stripe CLI

```bash
# Start listener (shows all events)
stripe listen --forward-to localhost:5000/webhooks/stripe

# You'll see output like:
# > Ready! Your webhook signing secret is whsec_... (^C to quit)
# > 2025-01-22 12:00:00  --> checkout.session.completed [evt_...]
# > 2025-01-22 12:00:01  <-- [200] POST http://localhost:5000/webhooks/stripe [evt_...]
```

#### Check Webhook Delivery Status

```bash
# List recent events
stripe events list --limit 5

# Get specific event
stripe events retrieve evt_...

# View webhook attempts
stripe events retrieve evt_... --expand data.object
```

### Database Queries for Verification

#### Check User Wallet Balance
```sql
SELECT id, email, wallet_balance, created_at 
FROM users 
WHERE id = <user_id>;
```

#### View All Wallet Transactions
```sql
SELECT 
  id,
  type,
  amount,
  balance_before,
  balance_after,
  description,
  reference_id,
  created_at
FROM wallet_transactions
WHERE user_id = <user_id>
ORDER BY created_at DESC;
```

#### Check Recent Tips (Boosts)
```sql
SELECT 
  id,
  user_id,
  artist_id,
  amount,
  total_paid,
  stripe_checkout_session_id,
  created_at
FROM tips
WHERE user_id = <user_id>
ORDER BY created_at DESC
LIMIT 10;
```

#### Check Recent Purchases
```sql
SELECT 
  id,
  type,
  user_id,
  amount,
  total,
  status,
  stripe_id,
  created_at
FROM purchases
WHERE user_id = <user_id>
ORDER BY created_at DESC
LIMIT 10;
```

### Test Cards

Use these Stripe test cards:

- **Success:** `4242 4242 4242 4242`
- **Decline:** `4000 0000 0000 0002`
- **Requires Auth:** `4000 0025 0000 3155`

All test cards:
- Expiry: Any future date (e.g., `12/25`)
- CVC: Any 3 digits (e.g., `123`)
- ZIP: Any 5 digits (e.g., `12345`)

---

## Troubleshooting

### Wallet Balance Not Updating

1. **Check webhook is received:**
   - Look at Stripe CLI output
   - Should see `checkout.session.completed` event

2. **Check webhook metadata:**
   - Event should have `metadata.type == "wallet_fund"`
   - Should have `metadata.user_id` and `metadata.amount`

3. **Check application logs:**
   - Look for errors in Flask console
   - Check for database errors

4. **Verify webhook secret:**
   - Make sure `STRIPE_WEBHOOK_SECRET` is set correctly
   - For local testing, use secret from `stripe listen` output

### Wallet Payment Not Working

1. **Check balance is sufficient:**
   ```sql
   SELECT wallet_balance FROM users WHERE id = <user_id>;
   ```

2. **Check form submission:**
   - Verify `use_wallet=true` is in form data
   - Check browser console for errors

3. **Check application logs:**
   - Look for errors when processing wallet payment
   - Verify `deduct_wallet_balance()` is called

### Webhook Not Received

1. **Check Stripe CLI is running:**
   ```bash
   stripe listen --forward-to localhost:5000/webhooks/stripe
   ```

2. **Check app is accessible:**
   - Test: `curl http://localhost:5000/webhooks/stripe`
   - Should return error (needs POST), but confirms endpoint exists

3. **Check webhook URL in Stripe Dashboard:**
   - Go to https://dashboard.stripe.com/webhooks
   - Verify endpoint URL is correct
   - For local testing, use Stripe CLI forwarding

---

## Key Design Decisions

### 1. Wallet vs. Stripe Choice
**Decision:** Allow both payment methods
**Reason:** 
- Wallet provides convenience for frequent users
- Stripe provides flexibility for one-time purchases
- Users can choose based on their preference

### 2. Wallet Funding via Stripe
**Decision:** Use Stripe Checkout for wallet funding
**Reason:**
- Reuses existing Stripe infrastructure
- Secure payment processing
- No need for separate payment gateway
- Consistent user experience

### 3. No Stripe Fees for Wallet Payments
**Decision:** Wallet payments bypass Stripe fees
**Reason:**
- Wallet already funded via Stripe (fees paid once)
- Encourages wallet usage
- Better user experience

### 4. Transaction History
**Decision:** Record all wallet transactions
**Reason:**
- Audit trail
- User transparency
- Debugging support
- Future refund support

### 5. Idempotency
**Decision:** All wallet operations are idempotent
**Reason:**
- Webhook retries won't cause double-charges
- Safe to retry failed operations
- Database consistency

---

## Security Features

1. **Authentication Required:** All wallet endpoints require user authentication
2. **Balance Validation:** Always check balance before deducting
3. **Webhook Verification:** Only process verified Stripe webhooks
4. **Amount Limits:** Enforce min/max funding amounts
5. **Atomic Transactions:** Database transactions ensure consistency
6. **Reference Tracking:** All transactions linked to source (Stripe session, purchase, etc.)

---

## Files Modified/Created

### New Files
- `alembic/versions/0015_add_wallet_system.py` - Database migration
- `docs/features/WALLET_COMPLETE_GUIDE.md` - This comprehensive guide

### Modified Files
- `models.py` - Added `wallet_balance` to User, created WalletTransaction model
- `blueprints/payments.py` - Added wallet endpoints and helper functions
- `routes/stripe_webhooks.py` - Added wallet funding webhook handler
- `app.py` - Modified checkout to support wallet payments, added wallet balance to account page
- `templates/checkout.html` - Added wallet payment UI
- `templates/account.html` - Added wallet display and funding button

---

## Usage Examples

### Fund Wallet via API
```bash
curl -X POST http://localhost:5000/payments/wallet/fund \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{"amount": 25.00}'
```

### Check Wallet Balance
```bash
curl http://localhost:5000/payments/wallet \
  -H "Cookie: session=..."
```

### View Transaction History
```bash
curl "http://localhost:5000/payments/wallet/transactions?limit=10" \
  -H "Cookie: session=..."
```

---

## Next Steps

1. **Run Migration:**
   ```bash
   alembic upgrade head
   ```

2. **Test Locally:**
   - Start Flask app
   - Start Stripe webhook listener
   - Test wallet funding
   - Test wallet payments
   - Test Stripe fallback

3. **Deploy:**
   - Ensure migration runs on production
   - Update environment variables if needed
   - Test in production with small amounts

---

## Summary

The wallet feature provides a seamless payment experience where users can:
- **Pre-fund their wallet** for convenience
- **Use wallet balance** for all purchases (boosts and merch)
- **Fall back to Stripe** if wallet insufficient or preferred
- **Track all transactions** in their account history

This implementation maintains backward compatibility with existing Stripe payments while adding the convenience of wallet-based payments. All wallet operations are secure, idempotent, and fully integrated with the existing boost and merch systems.

**Status:** ✅ **Complete and Ready for Testing**

Test the complete flow:
1. Fund wallet → 2. Make purchase with wallet → 3. Verify balance updated → 4. Check transaction history
