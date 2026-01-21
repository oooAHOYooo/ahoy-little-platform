# Complete User Workflow: Wallet Funding & Merch Purchases

## Overview
This document describes the complete user journey for funding a wallet and purchasing items (merch or boosts) using either wallet balance or direct Stripe payment.

---

## Workflow 1: Fund Wallet → Buy Merch with Wallet

### Step 1: User Funds Wallet

**Starting Point:** User is on `/account` page (Profile)

1. **User sees Wallet section:**
   - Current balance displayed (e.g., "$0.00")
   - "Add $5 to get started" button (if balance is $0)
   - Quick-pick buttons: +$5, +$10, +$25 (if balance > 0)
   - "Add funds" button for custom amounts

2. **User clicks "Add $5 to get started":**
   - Frontend: `fundWallet(5)` function called
   - Shows loading state: "Processing..."
   - POST request to `/payments/wallet/fund` with `{ amount: 5 }`

3. **Server creates Stripe Checkout Session:**
   - Validates user is logged in (401 if not)
   - Validates amount ($1.00 - $1000.00)
   - Creates Stripe Checkout Session
   - Returns `{ checkout_url: "https://checkout.stripe.com/...", session_id: "cs_..." }`

4. **User redirected to Stripe Checkout:**
   - **User enters credit card details on Stripe's secure page** (checkout.stripe.com)
   - Stripe processes payment
   - User completes payment on Stripe's PCI-compliant page

5. **Stripe webhook processes payment:**
   - Event: `checkout.session.completed`
   - Metadata: `type: "wallet_fund"`
   - Server adds funds to user's wallet balance
   - Creates `WalletTransaction` record (type: "fund")
   - User redirected to `/payments/wallet/success`

6. **User returns to account page:**
   - Wallet balance updated (e.g., "$5.00")
   - Transaction visible in "View transactions"

### Step 2: User Buys Merch with Wallet

**Starting Point:** User browses `/merch` page

1. **User selects merch item:**
   - Clicks "Buy" on a merch item
   - Redirected to `/checkout?type=merch&item_id=123&qty=1`

2. **Checkout page displays:**
   - Item details (name, quantity, price)
   - Total amount
   - **Wallet balance section** (if user is logged in):
     - Shows current wallet balance
     - If balance ≥ total: "Pay with wallet balance" checkbox enabled
     - If balance < total: "Insufficient balance" + "Fund Wallet" link

3. **User checks "Pay with wallet balance":**
   - Checkbox updates hidden field: `use_wallet = "true"`
   - User clicks "Complete Checkout" button

4. **Server processes wallet payment:**
   - POST to `/checkout/process` with `use_wallet=true`
   - Server validates CSRF token
   - Creates `Purchase` record (status: "pending")
   - Calls `deduct_wallet_balance()`:
     - Validates sufficient balance
     - Deducts amount from wallet
     - Creates `WalletTransaction` (type: "spend")
   - Marks `Purchase` as "paid"
   - Sets `Purchase.stripe_id = "wallet_{purchase_id}"`

5. **User redirected to success page:**
   - `/checkout/success?pid={purchase_id}`
   - Purchase complete (no Stripe redirect needed)
   - Wallet balance decreased

---

## Workflow 2: Buy Merch Directly with Stripe (No Wallet)

### Step 1: User Buys Merch Directly

**Starting Point:** User browses `/merch` page

1. **User selects merch item:**
   - Clicks "Buy" on a merch item
   - Redirected to `/checkout?type=merch&item_id=123&qty=1`

2. **Checkout page displays:**
   - Item details
   - Total amount
   - Wallet balance section (if logged in)
   - **User does NOT check "Pay with wallet balance"**

3. **User clicks "Complete Checkout":**
   - Form submits with `use_wallet=false` (default)
   - POST to `/checkout/process`

4. **Server creates Stripe Checkout Session:**
   - Validates CSRF token
   - Creates `Purchase` record (status: "pending")
   - Creates Stripe Checkout Session with:
     - Line items (merch item)
     - Metadata: `type: "merch"`, `purchase_id: "123"`
     - Success/cancel URLs
   - Returns redirect to Stripe Checkout URL

5. **User redirected to Stripe Checkout:**
   - **User enters credit card details on Stripe's secure page**
   - Completes payment on Stripe

6. **Stripe webhook processes payment:**
   - Event: `checkout.session.completed`
   - Metadata: `type: "merch"` (not "wallet_fund")
   - Server marks `Purchase` as "paid"
   - Sets `Purchase.stripe_id = checkout_session.id`
   - User redirected to `/checkout/success?pid={purchase_id}`

---

## Workflow 3: Boost Artist with Wallet

### Step 1: User Boosts Artist

**Starting Point:** User on artist page (e.g., `/artist/alex-figueroa`)

1. **User clicks "Boost" button:**
   - Opens boost modal or redirects to `/checkout?type=boost&artist_id=alex-figueroa&amount=10`

2. **Checkout page displays:**
   - Artist name
   - Boost amount breakdown:
     - Boost Amount: $10.00
     - Stripe Fee: $0.59
     - Platform Fee: $0.75
     - **Total: $11.34**
   - Wallet balance section (if logged in)
   - "Pay with wallet balance" checkbox (if sufficient balance)

3. **User checks "Pay with wallet balance":**
   - Submits form with `use_wallet=true`

4. **Server processes wallet payment:**
   - Deducts total ($11.34) from wallet
   - Marks `Purchase` as "paid"
   - Creates `Tip` record:
     - `artist_id: "alex-figueroa"`
     - `amount: $10.00` (boost amount)
     - `artist_payout: $10.00` (100% of boost)
     - `stripe_fee: $0.00` (no Stripe fee for wallet)
     - `platform_fee: $0.75`
     - `total_paid: $11.34`
   - Updates user's portfolio position for artist
   - **Tip goes into "Alex Figueroa bucket"** (queryable by `artist_id`)

5. **User redirected to success page:**
   - Boost complete
   - Wallet balance decreased

---

## Workflow 4: Boost Artist Directly with Stripe

### Step 1: User Boosts Artist

1. **User clicks "Boost" button** → Checkout page

2. **User does NOT check wallet checkbox:**
   - Submits with `use_wallet=false`

3. **Server creates Stripe Checkout Session:**
   - Creates `Purchase` record
   - Creates Stripe Checkout with line items:
     - Boost Amount: $10.00
     - Stripe Fee: $0.59
     - Platform Fee: $0.75
   - Metadata: `type: "boost"`, `artist_id: "alex-figueroa"`

4. **User redirected to Stripe Checkout:**
   - Enters card details
   - Completes payment

5. **Stripe webhook processes:**
   - Creates `Tip` record
   - Updates portfolio
   - **Tip goes into "Alex Figueroa bucket"**

---

## Key Features

### ✅ Dual Payment Options
- **Wallet Payment:** Instant, no redirect, no fees (fees already paid during funding)
- **Direct Stripe:** Traditional checkout flow, user enters card each time

### ✅ Smart Wallet UI
- Shows wallet balance on checkout page
- Enables checkbox only if balance is sufficient
- Provides "Fund Wallet" link if insufficient
- Clear visual distinction between payment methods

### ✅ Artist Earnings Tracking
- All boosts stored in `tips` table with `artist_id`
- Query by artist: `SELECT SUM(artist_payout) FROM tips WHERE artist_id = 'alex-figueroa'`
- Admin page: `/admin/artist-earnings` to view artist buckets

### ✅ Security
- Wallet funding: Stripe Checkout (PCI-compliant)
- Direct payments: Stripe Checkout (PCI-compliant)
- No credit card data stored on your server
- CSRF protection on checkout forms
- Session-based authentication

---

## Missing Features / Enhancements Needed

### 1. Guest Checkout
- Currently requires login to use wallet
- Could allow guest checkout with Stripe only
- Wallet requires account (makes sense)

### 2. Saved Payment Methods
- Could use Stripe Customer ID to save cards
- Future enhancement: "Use saved card" option

### 3. Partial Wallet Payments
- Currently: All or nothing (wallet or Stripe)
- Could allow: Use wallet + pay remainder with Stripe

### 4. Wallet Refunds
- Refund functionality exists in code
- Could add UI for refunds (admin-only)

### 5. Transaction History UI
- `/payments/wallet/transactions` exists
- Could enhance with filters, search, export

---

## Testing Checklist

### Fund Wallet Flow
- [ ] Click "Add $5" → Redirects to Stripe
- [ ] Enter card on Stripe → Payment succeeds
- [ ] Webhook processes → Wallet balance updates
- [ ] Return to account → Balance shows $5.00

### Buy Merch with Wallet
- [ ] Go to merch → Select item → Checkout
- [ ] See wallet balance on checkout
- [ ] Check "Pay with wallet" → Submit
- [ ] Purchase completes instantly (no Stripe redirect)
- [ ] Wallet balance decreases
- [ ] Purchase marked as paid

### Buy Merch with Stripe (No Wallet)
- [ ] Go to merch → Select item → Checkout
- [ ] Don't check wallet checkbox
- [ ] Submit → Redirects to Stripe
- [ ] Enter card → Complete payment
- [ ] Webhook processes → Purchase marked as paid
- [ ] Wallet balance unchanged

### Boost with Wallet
- [ ] Go to artist page → Boost $10
- [ ] Check "Pay with wallet" → Submit
- [ ] Tip record created with `artist_id`
- [ ] Portfolio updated
- [ ] Wallet balance decreased

### Boost with Stripe
- [ ] Go to artist page → Boost $10
- [ ] Don't check wallet → Submit
- [ ] Redirects to Stripe → Complete payment
- [ ] Webhook creates Tip record
- [ ] Portfolio updated

---

## API Endpoints Reference

### Wallet
- `GET /payments/wallet` - Get current balance
- `POST /payments/wallet/fund` - Create Stripe checkout for funding
- `GET /payments/wallet/transactions` - View transaction history
- `GET /payments/wallet/success` - Funding success page
- `GET /payments/wallet/cancel` - Funding cancellation page

### Checkout
- `GET /checkout` - Display checkout page (with wallet option)
- `POST /checkout/process` - Process payment (wallet or Stripe)
- `GET /checkout/success` - Purchase success page

### Artist Earnings
- `GET /payments/artist/<artist_id>/earnings` - View artist payout bucket
- `GET /admin/artist-earnings` - Admin page to search artist earnings

---

## Database Tables

### `users`
- `wallet_balance` - Current wallet balance
- `stripe_customer_id` - Stripe Customer ID (created on registration)

### `wallet_transactions`
- All wallet activity (fund, spend, refund)
- Tracks balance before/after each transaction
- Reference to Stripe session or purchase

### `tips`
- All boosts/tips to artists
- `artist_id` - Artist slug (e.g., "alex-figueroa")
- `artist_payout` - Amount artist receives (100% of boost)
- Query by `artist_id` to get artist's total earnings

### `purchases`
- All purchases (merch, boosts, etc.)
- `status` - "pending" or "paid"
- `stripe_id` - Stripe session ID or "wallet_{purchase_id}"
