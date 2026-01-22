# Artist Payouts & Notifications Guide

This guide explains how to handle artist payouts and receive notifications when boosts or merch purchases occur.

## Overview

When someone boosts an artist or purchases merch:
1. **Email notifications** are sent to you (admin) and optionally to the artist
2. **Payout records** are created to track what needs to be paid out
3. **Payout script** helps you send money to artists via Stripe or manual transfer

## Email Notifications

### Setup

Email notifications require email to be configured. Set one of:

**Option 1: Resend (Recommended)**
```bash
export RESEND_API_KEY=your_resend_api_key
export SUPPORT_EMAIL=support@yourdomain.com
```

**Option 2: SMTP**
```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your-email@gmail.com
export SMTP_PASS=your-app-password
export SUPPORT_EMAIL=support@yourdomain.com
```

**Admin Email (Required for notifications)**
```bash
export AHOY_ADMIN_EMAIL=alex@ahoy.ooo
```

**Note:** This is already configured in `render.yaml` for production deployments.

### What You'll Receive

**Boost Notifications:**
- Artist name and ID
- Boost amount
- Artist payout amount (100% of boost)
- Total paid (including fees)
- Tipper email (if logged in)
- Stripe session ID

**Merch Purchase Notifications:**
- Purchase ID
- Item details
- Quantity and amount
- Buyer email (if logged in)
- Stripe session ID

**User Registration Notifications:**
- User ID
- Email address
- Username
- Display name
- Registration timestamp

**Wallet Funding Notifications:**
- User email and ID
- Amount added to wallet
- Balance before funding
- Balance after funding
- Stripe session ID

### Artist Email Notifications (Optional)

To notify artists when they receive boosts, set environment variables:

```bash
# Format: ARTIST_EMAIL_<ARTIST_ID>=email@example.com
export ARTIST_EMAIL_ROB_MEGLIO=rob@example.com
export ARTIST_EMAIL_AHOY_INDIE_MEDIA=alex@ahoy.ooo
```

Or add `email` field to artist entries in `static/data/artists.json`:
```json
{
  "id": "artist_17",
  "name": "Rob Meglio",
  "slug": "rob-meglio",
  "email": "rob@example.com",
  ...
}
```

## Payout System

### Database Migration

First, create the `artist_payouts` table:

```bash
alembic upgrade head
```

This creates the `artist_payouts` table to track all payouts.

### Sending Money to Artists

#### Option 1: Single Payout

Send a specific amount to an artist:

```bash
python scripts/send_artist_payout.py --artist-id "rob-meglio" --amount 25.00
```

#### Option 2: Auto Payout (All Pending Tips)

Automatically calculate and create payout for all unpaid tips:

```bash
python scripts/send_artist_payout.py --artist-id "rob-meglio" --auto
```

#### Option 3: Stripe Connect (Automatic)

If the artist has a Stripe Connect account connected:

1. Set environment variable:
```bash
export ARTIST_STRIPE_ACCOUNT_ROB_MEGLIO=acct_xxxxx
```

2. Run payout with Stripe Connect:
```bash
python scripts/send_artist_payout.py --artist-id "rob-meglio" --amount 25.00 --method stripe_connect
```

The script will automatically transfer funds to the artist's Stripe account.

#### Option 4: Manual Transfer

If using manual transfer (bank transfer, PayPal, etc.):

1. Create the payout record:
```bash
python scripts/send_artist_payout.py --artist-id "rob-meglio" --amount 25.00 --method manual
```

2. Transfer the money manually

3. Mark as completed:
```bash
python scripts/send_artist_payout.py --payout-id 123 --mark-completed --reference "BANK_TRANSFER_12345"
```

### Listing Pending Payouts

View all pending payouts:

```bash
python scripts/send_artist_payout.py --list-pending
```

Or for a specific artist:

```bash
python scripts/send_artist_payout.py --list-pending --artist-id "rob-meglio"
```

## Example Workflow

### Scenario: Someone boosts Rob Meglio $25

1. **Boost happens** → Stripe webhook fires
2. **Email sent** → You receive notification:
   ```
   Subject: 💰 New Boost: $25.00 to Rob Meglio
   
   Artist: Rob Meglio
   Boost Amount: $25.00
   Artist Payout: $25.00
   Total Paid: $27.XX (includes fees)
   ```

3. **Create payout** (when ready to pay):
   ```bash
   python scripts/send_artist_payout.py --artist-id "rob-meglio" --amount 25.00
   ```

4. **Transfer money** (if manual):
   - Transfer $25.00 to Rob's payment method
   - Record the reference number

5. **Mark completed**:
   ```bash
   python scripts/send_artist_payout.py --payout-id 123 --mark-completed --reference "PAYPAL_TXN_ABC123"
   ```

### Scenario: Multiple boosts, batch payout

1. **Multiple boosts accumulate** over time
2. **Auto payout all at once**:
   ```bash
   python scripts/send_artist_payout.py --artist-id "rob-meglio" --auto
   ```
   
   This will:
   - Find all unpaid tips for Rob Meglio
   - Calculate total amount
   - Create a single payout record
   - Provide instructions for transfer

## Environment Variables Summary

```bash
# Required for email notifications
AHOY_ADMIN_EMAIL=your-email@example.com
SUPPORT_EMAIL=support@yourdomain.com

# Email service (choose one)
RESEND_API_KEY=your_key  # OR
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-password

# Optional: Artist email notifications
ARTIST_EMAIL_ROB_MEGLIO=rob@example.com
ARTIST_EMAIL_AHOY_INDIE_MEDIA=alex@ahoy.ooo

# Optional: Stripe Connect accounts (for automatic transfers)
ARTIST_STRIPE_ACCOUNT_ROB_MEGLIO=acct_xxxxx

# Required for Stripe operations
STRIPE_SECRET_KEY=sk_live_xxxxx
```

## Troubleshooting

### No email notifications received

1. Check email is configured:
   ```bash
   python -c "from services.emailer import can_send_email; print(can_send_email())"
   ```

2. Check admin email is set:
   ```bash
   echo $AHOY_ADMIN_EMAIL
   ```

3. Check webhook logs for notification errors

### Payout script errors

1. **"STRIPE_SECRET_KEY not set"**: Set your Stripe secret key
2. **"Artist not found"**: Check artist ID matches slug/name in artists.json
3. **"No pending tips"**: All tips for that artist have been paid out

### Stripe Connect not working

1. Verify account ID is correct
2. Check account is active in Stripe Dashboard
3. Ensure you have permission to create transfers

## Database Schema

The `artist_payouts` table tracks:

- `id`: Payout ID
- `artist_id`: Artist identifier
- `amount`: Payout amount
- `status`: pending, processing, completed, failed
- `stripe_transfer_id`: Stripe Transfer ID (if using Stripe Connect)
- `payment_method`: manual, stripe_connect, etc.
- `payment_reference`: Reference for manual payments
- `related_tip_ids`: Array of Tip IDs included in this payout
- `created_at`, `processed_at`, `completed_at`: Timestamps

## Next Steps

1. **Set up email** (Resend or SMTP)
2. **Set admin email** (`AHOY_ADMIN_EMAIL`)
3. **Run migration** (`alembic upgrade head`)
4. **Test notifications** (make a test boost)
5. **Configure artist emails** (optional, for artist notifications)
6. **Set up Stripe Connect** (optional, for automatic transfers)
