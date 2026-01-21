# Render CLI Authentication - Quick Guide

## 🔐 Authentication Issue

The Render CLI uses browser-based authentication. The token `T20H-Q8YW-BOUQ-2XC9` is a **device authorization code** that needs to be authorized in your browser.

## ✅ Quick Solution: Use Dashboard Instead

**For now, use the Render Dashboard** (faster and easier):

1. **Go to:** https://dashboard.render.com
2. **Navigate to:** `ahoy-little-platform` → **Environment**
3. **Verify/Update:**
   - `STRIPE_WEBHOOK_SECRET = whsec_fIVkv7yyR1GTBfmZOSLjVZ6cwPwRhluV`
   - `STRIPE_SECRET_KEY` (should be set)
   - `STRIPE_PUBLISHABLE_KEY` (should be set)
   - `AHOY_ENV = production`

## 🔄 Run Migration

**Migrations run automatically on deploy!**

Your `migrate_and_start.sh` script runs `alembic upgrade heads` on every deploy.

**To trigger deploy (runs migration):**
- **Option 1:** Push to main (auto-deploys) ✅ Already done!
- **Option 2:** Manual deploy in dashboard
- **Option 3:** After CLI auth: `render services` → Deploy

## 📊 Check Status After Deploy

After deployment completes:
- **Status Dashboard:** https://app.ahoy.ooo/ops/status
- **Webhook Monitor:** https://app.ahoy.ooo/ops/webhooks/monitor

## 🔧 Complete CLI Auth Later (Optional)

If you want to use CLI later:

1. **Run:** `render login`
2. **Copy the code** (e.g., `T20H-Q8YW-BOUQ-2XC9`)
3. **Visit:** `https://dashboard.render.com/device-authorization/[CODE]`
4. **Authorize** in browser
5. **Verify:** `render whoami`

**Note:** Authorization codes expire quickly. If expired, run `render login` again.

## ✅ What's Done

- ✅ Render CLI installed
- ✅ Migration created (`0017_add_tip_fee_columns.py`)
- ✅ Helper scripts created
- ✅ All code committed and pushed
- ✅ Auto-deploy enabled (migrations run on deploy)

## 🎯 Next Steps

1. **Verify env vars** in Render dashboard
2. **Wait for deploy** to complete (or trigger manual deploy)
3. **Check status** at `/ops/status` after deploy
4. **Migration will run automatically** ✅
