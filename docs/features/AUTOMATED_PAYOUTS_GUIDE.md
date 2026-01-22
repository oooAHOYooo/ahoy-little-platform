# Automated Daily Payout System

## 🎯 Overview

The automated payout system scans daily for artists who need payouts, automatically processes Stripe Connect transfers, and sends you an email summary.

## ✨ Features

- **Daily automatic scan** - Checks all artists for pending payouts
- **Automatic Stripe transfers** - Sends money via Stripe Connect if configured
- **Email summary** - Daily email with all pending payouts
- **Manual payout records** - Creates records for artists needing manual transfers
- **Smart processing** - Only processes payouts above minimum threshold

## 🚀 Setup

### 1. Configure Render Cron Job

The cron job is already configured in `render.yaml`. After deploying, it will run daily at 9 AM UTC.

**Manual Setup (if needed):**
1. Go to Render Dashboard → New → Cron Job
2. Name: `daily-payout-processor`
3. Schedule: `0 9 * * *` (9 AM UTC daily)
4. Command: `python scripts/daily_payout_processor.py --auto-process --min-amount 1.00`
5. Environment: Copy from web service

### 2. Configure Artist Stripe Connect Accounts (Optional)

For automatic transfers, set environment variables for artists with Stripe Connect:

```bash
# In Render Dashboard → Environment Variables
ARTIST_STRIPE_ACCOUNT_ROB_MEGLIO=acct_xxxxx
ARTIST_STRIPE_ACCOUNT_AHOY_INDIE_MEDIA=acct_yyyyy
```

### 3. Verify Email Configuration

Make sure email is configured (for daily summaries):
- `RESEND_API_KEY` or `SMTP_*` variables
- `SUPPORT_EMAIL`
- `AHOY_ADMIN_EMAIL=alex@ahoy.ooo` (already set)

## 📧 Daily Email Summary

You'll receive an email at `alex@ahoy.ooo` every day with:

1. **Summary Statistics**
   - Total pending amount
   - Number of artists needing payouts
   - Number of tips pending

2. **Automatically Processed**
   - Artists paid via Stripe Connect
   - Transfer IDs for reference

3. **Failed Transfers**
   - Artists where Stripe transfer failed
   - Error messages
   - Needs manual review

4. **Manual Payouts Needed**
   - Artists without Stripe Connect
   - Payout IDs
   - Commands to mark as completed

5. **Complete List**
   - All artists with pending payouts
   - Amounts and tip counts
   - Payment methods

## 🔄 How It Works

### Daily Process (9 AM UTC)

1. **Scan** - Finds all artists with pending tips
2. **Process** - For each artist:
   - If Stripe Connect configured → Automatic transfer
   - If no Stripe Connect → Create pending payout record
3. **Email** - Sends summary to admin
4. **Track** - All payouts recorded in database

### Automatic Processing

**With Stripe Connect:**
```
Artist has Stripe Connect → Automatic Transfer → Completed Payout Record
```

**Without Stripe Connect:**
```
No Stripe Connect → Pending Payout Record → You transfer manually → Mark as completed
```

## 🛠️ Manual Usage

You can also run the script manually:

### Preview (Dry Run)
```bash
python scripts/daily_payout_processor.py --dry-run
```
Shows what would be processed without actually doing it.

### Process with Auto-Transfer
```bash
python scripts/daily_payout_processor.py --auto-process
```
Automatically processes Stripe Connect transfers.

### Set Minimum Amount
```bash
python scripts/daily_payout_processor.py --auto-process --min-amount 50.00
```
Only processes payouts of $50 or more.

## 📊 What Gets Processed

### Automatically (Stripe Connect)
- Artists with `ARTIST_STRIPE_ACCOUNT_*` environment variable set
- Transfers money directly to artist's Stripe account
- Creates completed payout record
- Includes transfer ID for tracking

### Manually (No Stripe Connect)
- Artists without Stripe Connect account
- Creates pending payout record
- You transfer money via bank/PayPal/etc.
- Mark as completed after transfer

## ✅ After Automatic Processing

### For Stripe Connect Artists
- ✅ Money automatically transferred
- ✅ Payout record marked as completed
- ✅ Transfer ID recorded
- ✅ Email notification sent

### For Manual Artists
- 📋 Payout record created (status: pending)
- 📧 Email with payout ID and instructions
- 💸 You transfer money manually
- ✅ Mark as completed: `python scripts/send_artist_payout.py --payout-id 123 --mark-completed --reference "YOUR_REFERENCE"`

## 🔍 Monitoring

### Check Cron Job Status
- Render Dashboard → Cron Jobs → daily-payout-processor
- View logs to see daily runs
- Check for errors

### Verify Processing
```bash
# Check pending payouts
python scripts/send_artist_payout.py --list-pending

# Scan all artists
python scripts/scan_artist_payouts.py
```

### Check Email
- Daily email should arrive at `alex@ahoy.ooo`
- Check spam folder if missing
- Verify email service is configured

## 🚨 Troubleshooting

### Cron Job Not Running
1. Check Render Dashboard → Cron Jobs
2. Verify schedule: `0 9 * * *`
3. Check logs for errors
4. Verify environment variables are set

### Stripe Transfers Failing
1. Check Stripe account is active
2. Verify account ID is correct
3. Check Stripe Dashboard for errors
4. Review error messages in email

### Email Not Received
1. Verify email service configured
2. Check `AHOY_ADMIN_EMAIL` is set
3. Check spam folder
4. Run manually to test: `python scripts/daily_payout_processor.py`

### No Artists Found
- This is normal if no pending tips exist
- Script will still send email (empty summary)
- Check database for tips: `SELECT * FROM tips WHERE artist_id = 'artist-id'`

## 📝 Configuration Options

### Environment Variables

**Required:**
- `STRIPE_SECRET_KEY` - For Stripe transfers
- `AHOY_ADMIN_EMAIL` - For email summaries (already set)

**Optional:**
- `ARTIST_STRIPE_ACCOUNT_<ARTIST_ID>` - For automatic transfers
- `ARTIST_EMAIL_<ARTIST_ID>` - For artist notifications

### Command Line Options

- `--dry-run` - Preview without processing
- `--auto-process` - Enable automatic Stripe transfers
- `--min-amount X.XX` - Minimum amount to process

## 🎉 Benefits

1. **Time Saving** - No manual scanning needed
2. **Automatic Processing** - Stripe Connect artists paid automatically
3. **Complete Tracking** - All payouts recorded
4. **Daily Updates** - Know exactly what needs attention
5. **Error Handling** - Failed transfers flagged for review

## 📚 Related Scripts

- `scripts/daily_payout_processor.py` - Main automation script
- `scripts/scan_artist_payouts.py` - Manual scan tool
- `scripts/send_artist_payout.py` - Manual payout processor
- `scripts/schedule_daily_payouts.sh` - Cron wrapper (optional)

## 🔐 Security

- Stripe keys stored as environment variables
- Artist Stripe account IDs in environment variables
- All transfers logged in database
- Email summaries for audit trail
