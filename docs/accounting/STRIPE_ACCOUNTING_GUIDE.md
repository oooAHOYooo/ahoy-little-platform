# Stripe Accounting & Tax-Ready Records

## 🏦 How Stripe Organizes Money

### Stripe Account Structure

```
Customer Payment ($100)
    ↓
Stripe Platform Account
    ├── Charge: $100 (money received)
    ├── Stripe Fee: -$2.90 (Stripe's processing fee)
    └── Net: $97.10 (available in your Stripe balance)
        │
        ├── Platform Fee: $7.50 (your revenue)
        └── Artist Payout: $90.00 (to be paid to artist)
```

### Stripe Concepts

1. **Charges** - Money coming IN from customers
   - Stored in: `tips.stripe_checkout_session_id` / `tips.stripe_payment_intent_id`
   - Total amount customer paid: `tips.total_paid`

2. **Transfers** - Money going OUT to connected accounts (Stripe Connect)
   - Stored in: `artist_payouts.stripe_transfer_id`
   - Amount: `artist_payouts.amount`
   - Only for artists with Stripe Connect accounts

3. **Payouts** - Stripe automatically sends money from your Stripe balance to your bank
   - Happens daily/weekly automatically
   - Not stored in our database (check Stripe Dashboard)
   - Your bank receives: All charges minus Stripe fees minus transfers

4. **Fees** - Stripe processing fees
   - Stored in: `tips.stripe_fee`
   - Calculated: 2.9% + $0.30 per transaction

## 📊 What We Track in Database

### Revenue (Money Coming In)

**Tips/Boosts:**
- `tips.total_paid` - Total customer payment
- `tips.amount` - Boost amount (artist receives 100%)
- `tips.platform_revenue` - Your platform fee (7.5%)
- `tips.stripe_fee` - Stripe processing fee
- `tips.created_at` - Transaction date
- `tips.stripe_checkout_session_id` - Stripe reference

**Merch Purchases:**
- `purchases.total` - Total purchase amount
- `purchases.stripe_id` - Stripe session ID
- `purchases.created_at` - Transaction date

**Wallet Funding:**
- `wallet_transactions` (type='fund') - Money added to wallets
- `wallet_transactions.reference_id` - Stripe session ID

### Expenses (Money Going Out)

**Artist Payouts:**
- `artist_payouts.amount` - Amount paid to artist
- `artist_payouts.stripe_transfer_id` - Stripe Transfer ID (if Stripe Connect)
- `artist_payouts.payment_reference` - Manual payment reference (if manual)
- `artist_payouts.completed_at` - Payment date
- `artist_payouts.related_tip_ids` - Which tips were included

**Stripe Fees:**
- `tips.stripe_fee` - Per-transaction fee
- Sum all `tips.stripe_fee` for total Stripe fees

### Platform Revenue

**Your Income:**
- `tips.platform_revenue` - Platform fee from each boost
- Merch purchases: `purchases.total` (if you keep 100% of merch sales)

## 📈 Tax-Ready Accounting Reports

### 1. Revenue Report (Schedule C / 1099-K)

**What to Report:**
- Total gross receipts from customers
- All `tips.total_paid` + all `purchases.total` + all wallet funding

**Export:**
```bash
python scripts/export_accounting.py --type revenue --year 2024 --format csv
```

### 2. Expense Report (Schedule C)

**What to Report:**
- Artist payouts: All `artist_payouts.amount` where status='completed'
- Stripe fees: Sum of all `tips.stripe_fee`
- Other expenses (hosting, etc.) - manual entry

**Export:**
```bash
python scripts/export_accounting.py --type expenses --year 2024 --format csv
```

### 3. Artist 1099-NEC Report

**What to Report:**
- Total paid to each artist in calendar year
- Sum of `artist_payouts.amount` grouped by artist, where status='completed'

**Export:**
```bash
python scripts/export_accounting.py --type artist-1099 --year 2024 --format csv
```

### 4. Platform Revenue Report

**What to Report:**
- Your net income (platform fees)
- Sum of `tips.platform_revenue` + merch revenue

**Export:**
```bash
python scripts/export_accounting.py --type platform-revenue --year 2024 --format csv
```

## 🔗 Stripe Dashboard Integration

### Viewing in Stripe Dashboard

1. **Charges:**
   - Stripe Dashboard → Payments → All payments
   - Match with: `tips.stripe_checkout_session_id`

2. **Transfers:**
   - Stripe Dashboard → Connect → Transfers
   - Match with: `artist_payouts.stripe_transfer_id`

3. **Payouts:**
   - Stripe Dashboard → Balance → Payouts
   - These are automatic transfers to your bank
   - Not stored in our database (Stripe handles automatically)

4. **Fees:**
   - Stripe Dashboard → Payments → Fees
   - Match with: Sum of `tips.stripe_fee`

### Reconciliation

**Monthly Reconciliation:**
1. Stripe Dashboard → Balance → Transactions
2. Compare with database exports
3. Verify all charges match `tips` and `purchases`
4. Verify all transfers match `artist_payouts` with `stripe_transfer_id`

## 📋 Database Tables for Accounting

### `tips` Table
- **Revenue:** `total_paid` (gross receipts)
- **Expense:** `stripe_fee` (Stripe processing fee)
- **Revenue (Platform):** `platform_revenue` (your income)
- **Expense (Artist):** `artist_payout` (paid to artist)
- **Date:** `created_at`
- **Stripe ID:** `stripe_checkout_session_id`, `stripe_payment_intent_id`

### `artist_payouts` Table
- **Expense:** `amount` (paid to artist)
- **Date:** `completed_at` (when paid)
- **Method:** `payment_method` (stripe_connect, manual)
- **Stripe ID:** `stripe_transfer_id` (if Stripe Connect)
- **Reference:** `payment_reference` (if manual)
- **Related Tips:** `related_tip_ids` (which tips were paid out)

### `purchases` Table
- **Revenue:** `total` (merch sales)
- **Date:** `created_at`
- **Stripe ID:** `stripe_id`

### `wallet_transactions` Table
- **Revenue:** `amount` where `type='fund'` (wallet funding)
- **Date:** `created_at`
- **Stripe ID:** `reference_id` where `reference_type='stripe_checkout'`

## 💡 Best Practices

### 1. Monthly Reconciliation
- Export all transactions monthly
- Compare with Stripe Dashboard
- Verify all amounts match

### 2. Quarterly Tax Estimates
- Calculate platform revenue quarterly
- Set aside estimated taxes
- Use accounting exports for calculations

### 3. Year-End Reporting
- Export full year data
- Generate 1099-NEC for artists (if required)
- Prepare Schedule C for your taxes

### 4. Record Keeping
- Keep all Stripe IDs in database
- Store payment references for manual transfers
- Maintain audit trail with `related_tip_ids`

## 🚨 Important Tax Notes

### 1099-K Threshold
- Stripe will send you a 1099-K if you receive >$20,000 and >200 transactions
- Use accounting exports to verify Stripe's numbers

### 1099-NEC for Artists
- You may need to send 1099-NEC to artists if you pay them >$600/year
- Use `export_accounting.py --type artist-1099` to generate

### Business Expenses
- Stripe fees are deductible business expenses
- Artist payouts are cost of goods sold (COGS)
- Platform revenue is your taxable income

## 📚 Related Scripts

- `scripts/export_accounting.py` - Generate tax-ready reports
- `scripts/batch_process_payouts.py` - Process payouts (creates records)
- `scripts/send_artist_payout.py` - Individual payout processing
