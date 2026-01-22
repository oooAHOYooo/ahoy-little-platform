# How Artists Get Paid Out - Complete Guide

## 🎯 Overview

Artists get paid out through a **payout script** (not Stripe CLI). The system tracks all boosts/tips and allows you to pay artists via:

1. **Stripe Connect** (automatic - if artist has Stripe account)
2. **Manual Transfer** (bank transfer, PayPal, Venmo, etc.)

## 💰 How It Works

### Step 1: Boost/Tip Happens
- User boosts an artist (e.g., $25 to Rob Meglio)
- Money goes to **your Stripe account** (the platform account)
- Tip is recorded in database with `artist_payout` amount

### Step 2: Track Pending Payouts
- All unpaid tips are tracked in the database
- Each tip has an `artist_payout` amount (100% of boost)
- Script can scan and find all artists who need payouts

### Step 3: Pay Out to Artist
You have two options:

#### Option A: Stripe Connect (Automatic)
If artist has Stripe Connect account:
```bash
# Set artist's Stripe account ID
export ARTIST_STRIPE_ACCOUNT_ROB_MEGLIO=acct_xxxxx

# Pay out automatically
python scripts/send_artist_payout.py --artist-id "rob-meglio" --auto --method stripe_connect
```
Money transfers automatically to artist's Stripe account.

#### Option B: Manual Transfer (Most Common)
```bash
# Create payout record
python scripts/send_artist_payout.py --artist-id "rob-meglio" --auto

# Transfer money manually (bank, PayPal, etc.)
# Then mark as completed:
python scripts/send_artist_payout.py --payout-id 123 --mark-completed --reference "PAYPAL_TXN_ABC123"
```

## 🔍 Finding Artists Who Need Payouts

### Scan All Artists
```bash
python scripts/scan_artist_payouts.py
```

This will show:
- All artists with pending tips
- Total amount pending for each artist
- Number of tips pending
- Commands to pay them out

### Example Output
```
💰 Found 3 artist(s) with pending payouts:

   1. Rob Meglio
      Pending Amount: $75.00
      Number of Tips: 3
      Recent Tips:
         - $25.00 on 2025-01-20
         - $25.00 on 2025-01-18
         - $25.00 on 2025-01-15
      
      💸 To pay out:
         python scripts/send_artist_payout.py --artist-id "rob-meglio" --auto
```

## 📋 Complete Workflow

### 1. Scan for Pending Payouts
```bash
python scripts/scan_artist_payouts.py
```

### 2. Pay Out Each Artist

**For each artist with pending payouts:**

```bash
# Auto payout (calculates total from all pending tips)
python scripts/send_artist_payout.py --artist-id "rob-meglio" --auto
```

This will:
- Find all unpaid tips for Rob Meglio
- Calculate total amount
- Create a payout record
- Give you instructions for manual transfer

### 3. Transfer Money

Transfer the money via:
- Bank transfer
- PayPal
- Venmo
- Zelle
- Check
- Any method you prefer

### 4. Mark as Completed

After transferring, mark the payout as completed:

```bash
python scripts/send_artist_payout.py --payout-id 123 --mark-completed --reference "YOUR_REFERENCE"
```

## 🚫 NOT Using Stripe CLI

**Important:** This is NOT using Stripe CLI features. The payout system uses:

1. **Stripe Connect** (if artist has connected account) - via Stripe API
2. **Manual transfers** - you handle the actual money transfer

Stripe CLI is only for testing webhooks locally, not for payouts.

## 💡 Best Practices

### Regular Payout Schedule
- Scan weekly: `python scripts/scan_artist_payouts.py`
- Pay out monthly or when amount reaches threshold (e.g., $50+)
- Keep records of all payouts

### Minimum Payout Amount
You can set a minimum:
```bash
python scripts/scan_artist_payouts.py --min-amount 10.00
```

### Batch Processing
For multiple artists:
```bash
# Scan first
python scripts/scan_artist_payouts.py

# Then pay out each artist
python scripts/send_artist_payout.py --artist-id "artist-1" --auto
python scripts/send_artist_payout.py --artist-id "artist-2" --auto
# ... etc
```

## 📊 Tracking

All payouts are tracked in the `artist_payouts` table:
- Payout ID
- Artist ID
- Amount
- Status (pending, completed, failed)
- Payment method
- Payment reference
- Related tip IDs

## 🔐 Security Notes

- Never commit Stripe keys or artist payment info to git
- Use environment variables for Stripe Connect account IDs
- Keep payment references for audit trail
- Verify amounts before transferring

## 📚 Related Scripts

- `scripts/scan_artist_payouts.py` - Find artists needing payouts
- `scripts/send_artist_payout.py` - Process payouts
- `scripts/test_email_notification.py` - Test email notifications

## ❓ FAQ

**Q: Can I use Stripe CLI for payouts?**  
A: No, Stripe CLI is for testing webhooks. Use the payout script instead.

**Q: How do I set up Stripe Connect for an artist?**  
A: Artist needs to connect their Stripe account. Then set: `ARTIST_STRIPE_ACCOUNT_<ARTIST_ID>=acct_xxxxx`

**Q: What if artist doesn't have Stripe?**  
A: Use manual transfer (Option B) - most common method.

**Q: How often should I pay out?**  
A: Your choice - weekly, monthly, or when amount reaches threshold.

**Q: Can I pay multiple artists at once?**  
A: Yes, run the payout script for each artist separately.
