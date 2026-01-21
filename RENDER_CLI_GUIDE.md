# Render CLI Quick Guide

## 🚀 Setup

1. **Install Render CLI** (already done):
   ```bash
   brew install render
   ```

2. **Authenticate**:
   ```bash
   render login
   ```
   This opens a browser for authentication.

## ✅ Verify Environment Variables

### Option 1: Interactive Mode (Easiest)
```bash
render services
```
Then:
- Select `ahoy-little-platform`
- Choose "Environment Variables"
- Verify `STRIPE_WEBHOOK_SECRET = whsec_fIVkv7yyR1GTBfmZOSLjVZ6cwPwRhluV`

### Option 2: Dashboard
- Go to: https://dashboard.render.com
- Navigate to: **ahoy-little-platform** → **Environment**
- Check/update variables there

## 🔄 Run Migration

Migrations run **automatically** on deploy via `./scripts/migrate_and_start.sh`

### Trigger Deploy (runs migrations):

**Option 1: Auto-deploy (easiest)**
```bash
git push origin main
```
Render auto-deploys on push to main.

**Option 2: Manual deploy via CLI**
```bash
render services
# Select: ahoy-little-platform
# Choose: Deploy
```

**Option 3: Dashboard**
- Go to: https://dashboard.render.com
- Navigate to: **ahoy-little-platform** → **Manual Deploy**

## 📊 Check Status

After deploy, check:
- Status Dashboard: https://app.ahoy.ooo/ops/status
- Webhook Monitor: https://app.ahoy.ooo/ops/webhooks/monitor

## 🔑 Required Environment Variables

Make sure these are set in Render:

```bash
AHOY_ENV=production
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_... (or mk_live_...)
STRIPE_WEBHOOK_SECRET=whsec_fIVkv7yyR1GTBfmZOSLjVZ6cwPwRhluV
```

## 🛠️ Helper Scripts

- `./scripts/render_quick_check.sh` - Quick status check
- `./scripts/render_setup.sh` - Full setup (if CLI supports it)

## 📝 Notes

- Render CLI uses **interactive mode** by default
- Environment variables can be managed via dashboard or CLI
- Migrations run automatically on every deploy
- Auto-deploy is enabled for `main` branch
