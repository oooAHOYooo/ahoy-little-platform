# Resend API Key Setup Instructions

## ✅ Your Resend API Key

Your Resend API key is configured. Here's how to complete setup:

## 🔧 Setup on Render

### Step 1: Add Environment Variables

Go to **Render Dashboard** → **ahoy-little-platform** → **Environment** and add:

```
RESEND_API_KEY=re_csHQ4MFH_MKH3wsNwtCd7556Toic1NXuG
SUPPORT_EMAIL=support@ahoy.ooo
```

**⚠️ IMPORTANT - Domain Verification Required:**

The API key works, but `ahoy.ooo` domain needs to be verified in Resend. You have two options:

**Option A: Verify Domain (Recommended for Production)**
1. Go to **Resend Dashboard** → **Domains** → **Add Domain**
2. Enter: `ahoy.ooo`
3. Add DNS records (Resend will show you exactly what to add):
   - SPF record
   - DKIM record
   - DMARC record (optional but recommended)
4. Wait for verification (usually 5-15 minutes)
5. Once verified, emails will work!

**Option B: Use Resend Default Domain (Quick Test)**
1. Temporarily use Resend's default domain for testing
2. Set `SUPPORT_EMAIL=onboarding@resend.dev` (or check Resend dashboard for default)
3. This works immediately but shows "onboarding@resend.dev" as sender
4. Later, verify your domain and switch back to `support@ahoy.ooo`

### Step 2: Verify Domain in Resend

1. Go to **Resend Dashboard** → **Domains**
2. Click **"Add Domain"**
3. Enter: `ahoy.ooo`
4. Add the DNS records Resend shows you
5. Wait for verification (usually a few minutes)

### Step 3: Test

After setting the environment variables on Render and deploying:

```bash
# On Render Shell
python scripts/check_email_config.py
python scripts/test_send_email_to_alex.py
```

## 🚨 Security Notes

**DO NOT:**
- ❌ Commit the API key to git
- ❌ Put it in code files
- ❌ Share it publicly

**DO:**
- ✅ Set it as environment variable in Render
- ✅ Keep it secret
- ✅ Rotate it if exposed

## 📧 What Happens Next

Once configured on Render:
- ✅ All notifications will be sent to `alex@ahoy.ooo`
- ✅ Emails will be sent via Resend API
- ✅ You'll receive emails for:
  - User registrations
  - Wallet funding
  - Artist boosts
  - Merch purchases
  - Daily payout summaries

## 🔍 Verify It's Working

After setting on Render, check:

1. **Configuration:**
   ```bash
   python scripts/check_email_config.py
   ```

2. **Test Email:**
   ```bash
   python scripts/test_send_email_to_alex.py
   ```

3. **Check Resend Dashboard:**
   - Go to https://resend.com/emails
   - You should see sent emails there

## 📚 Next Steps

1. Set `RESEND_API_KEY` in Render Dashboard
2. Set `SUPPORT_EMAIL` in Render Dashboard  
3. Verify domain in Resend (if using custom domain)
4. Deploy/Restart service
5. Test with scripts
6. Check `alex@ahoy.ooo` for emails!
