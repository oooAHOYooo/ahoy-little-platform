# ✅ Render Setup - Complete Checklist

## 🎯 What's Already Done

✅ **Code is pushed to git** - All notification code is in `main` branch  
✅ **render.yaml configured** - `AHOY_ADMIN_EMAIL=alex@ahoy.ooo` is set  
✅ **Migration script ready** - Will run automatically on deploy  
✅ **All notification handlers** - User registration, wallet funding, boosts, merch  

## 🔧 What You Need to Do on Render (5 minutes)

### Step 1: Set Email Service (Required)

Go to **Render Dashboard → ahoy-little-platform → Environment** and add:

**Option A: Resend (Recommended - Easiest)**
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

### Step 2: Deploy (Automatic or Manual)

**Automatic:** Push to main triggers auto-deploy (already done if you just pushed)

**Manual:** Go to Render Dashboard → Manual Deploy → Deploy latest commit

The migration (`0018_create_artist_payouts`) will run automatically via `migrate_and_start.sh`

### Step 3: Test (After Deploy)

**Via Render Shell:**
```bash
python scripts/test_email_notification.py
```

This sends test emails to `alex@ahoy.ooo` for all notification types.

## 📧 What You'll Receive

Once email is configured, you'll get emails at `alex@ahoy.ooo` for:

1. **👤 New User Registration**
   - User ID, email, username, display name

2. **💰 Wallet Funding**
   - User email, amount added, balance before/after

3. **🎵 Artist Boosts**
   - Artist name, boost amount, payout details

4. **🛍️ Merch Purchases**
   - Purchase ID, item details, buyer info

## ✅ Verification

After setting email and deploying:

1. **Check deployment logs** - Should see migration running
2. **Run test script** - `python scripts/test_email_notification.py`
3. **Check your email** - `alex@ahoy.ooo` should receive test emails
4. **Test real events** - Create account, fund wallet, make boost/purchase

## 🚨 Important Notes

- **Email is required** - Notifications won't work without RESEND_API_KEY or SMTP configured
- **Migration is automatic** - Runs on every deploy via `migrate_and_start.sh`
- **Admin email is set** - `alex@ahoy.ooo` is already in `render.yaml`
- **No code changes needed** - Everything is already in the codebase

## 📚 Documentation

- **Quick Start**: `QUICK_START_PAYOUTS.md`
- **Full Guide**: `docs/features/ARTIST_PAYOUTS_GUIDE.md`
- **Render Setup**: `docs/deployment/RENDER_PAYOUT_SETUP.md`

## 🎉 That's It!

Once you set the email environment variables in Render and deploy, everything will work automatically!
