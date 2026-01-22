# Render Setup for Artist Payouts & Notifications

## ✅ What's Already Configured

The following is already set in `render.yaml`:
- `AHOY_ADMIN_EMAIL=alex@ahoy.ooo` (automatically set)

## 🔧 What You Need to Do on Render

### 1. Set Email Service Environment Variables

Go to **Render Dashboard → Your Web Service → Environment** and set:

**Option A: Resend (Recommended)**
```
RESEND_API_KEY=re_xxxxx
SUPPORT_EMAIL=support@ahoy.ooo
```

**Option B: SMTP**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SUPPORT_EMAIL=support@ahoy.ooo
```

### 2. Run Database Migration

The migration will run automatically on next deploy (via `migrate_and_start.sh`), but you can also run it manually:

**Via Render Shell:**
1. Go to Render Dashboard → Your Web Service → Shell
2. Run: `alembic upgrade head`

**Or via Render CLI:**
```bash
render exec -s ahoy-little-platform -- alembic upgrade head
```

### 3. Verify Email Configuration

After deployment, you can test email notifications:

**Via Render Shell:**
```bash
python scripts/test_email_notification.py
```

This will send test emails to `alex@ahoy.ooo` to verify everything is working.

## 📧 Email Notifications

Once configured, you'll automatically receive emails at `alex@ahoy.ooo` when:
- **New user registers** - User ID, email, username, display name
- **User funds wallet** - Amount added, balance before/after
- **Someone boosts an artist** - Artist name, amount, payout details
- **Someone purchases merch** - Purchase details, item info

## 💰 Payout Script

The payout script is available in production. You can run it via Render Shell:

```bash
# List pending payouts
python scripts/send_artist_payout.py --list-pending

# Send payout to artist
python scripts/send_artist_payout.py --artist-id "rob-meglio" --amount 25.00

# Auto payout all pending tips
python scripts/send_artist_payout.py --artist-id "rob-meglio" --auto
```

## 🔍 Verification Checklist

### Required Setup
- [ ] Email service configured (RESEND_API_KEY or SMTP_*)
- [ ] SUPPORT_EMAIL set in Render dashboard
- [ ] AHOY_ADMIN_EMAIL already set to `alex@ahoy.ooo` (in render.yaml)
- [ ] Database migration will run automatically on next deploy

### Testing
- [ ] Deploy completes successfully (migration runs automatically)
- [ ] Test email sent successfully: `python scripts/test_email_notification.py`
- [ ] Webhook endpoint accessible (for Stripe webhooks)

### Verify Notifications Work
- [ ] Create a test user account → Should receive registration email
- [ ] Fund a test wallet → Should receive wallet funding email
- [ ] Make a test boost → Should receive boost notification
- [ ] Make a test purchase → Should receive merch notification

## 🚨 Important Notes

1. **Email Service Required**: Notifications won't work without email configured
2. **Migration Required**: The `artist_payouts` table must exist before using payout features
3. **Stripe Webhooks**: Make sure your Stripe webhook URL points to your Render service
4. **Admin Email**: Already set to `alex@ahoy.ooo` in `render.yaml`

## 📚 Additional Resources

- Quick Start: `QUICK_START_PAYOUTS.md`
- Full Guide: `docs/features/ARTIST_PAYOUTS_GUIDE.md`
