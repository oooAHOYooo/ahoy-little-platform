# Quick Start: Artist Payouts & Notifications

## 🚀 Quick Setup (5 minutes)

### 1. Set Admin Email
```bash
export AHOY_ADMIN_EMAIL=alex@ahoy.ooo
```

**Note:** This is already set in `render.yaml` for production. For local testing, set it in your environment.

### 2. Configure Email Service

**Option A: Resend (Easiest)**
```bash
export RESEND_API_KEY=re_xxxxx
export SUPPORT_EMAIL=support@yourdomain.com
```

**Option B: SMTP**
```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your-email@gmail.com
export SMTP_PASS=your-app-password
export SUPPORT_EMAIL=support@yourdomain.com
```

### 3. Run Database Migration
```bash
alembic upgrade head
```

### 4. Test It!

Make a test boost or purchase, and you should receive an email notification!

## 📧 What You'll Get

**When someone boosts an artist:**
- Email with artist name, amount, and payout details
- Instructions on how to process the payout

**When someone buys merch:**
- Email with purchase details

## 💰 Sending Money to Artists

### Quick Example: Send $25 to Rob Meglio

```bash
python scripts/send_artist_payout.py --artist-id "rob-meglio" --amount 25.00
```

This will:
1. Create a payout record
2. Give you instructions for manual transfer
3. Track it in the database

### Auto Payout (All Pending Tips)

```bash
python scripts/send_artist_payout.py --artist-id "rob-meglio" --auto
```

### Mark as Completed (After Manual Transfer)

```bash
python scripts/send_artist_payout.py --payout-id 123 --mark-completed --reference "PAYPAL_TXN_ABC123"
```

## 🔧 Optional: Artist Email Notifications

To notify artists when they receive boosts:

```bash
export ARTIST_EMAIL_ROB_MEGLIO=rob@example.com
```

## 🔧 Optional: Stripe Connect (Automatic Transfers)

For automatic transfers via Stripe:

```bash
export ARTIST_STRIPE_ACCOUNT_ROB_MEGLIO=acct_xxxxx
python scripts/send_artist_payout.py --artist-id "rob-meglio" --amount 25.00 --method stripe_connect
```

## 📚 Full Documentation

See `docs/features/ARTIST_PAYOUTS_GUIDE.md` for complete details.
