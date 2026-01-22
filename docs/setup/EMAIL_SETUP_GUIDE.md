# Email Setup Guide - Resend API

## 📧 Email System Overview

The Ahoy platform uses **Resend API** (preferred) or **SMTP** (fallback) to send emails.

### Email Service: Resend API

**Resend** is a modern email API service that makes sending transactional emails easy.

- **API Endpoint:** `https://api.resend.com/emails`
- **Documentation:** https://resend.com/docs
- **Free Tier:** 3,000 emails/month
- **Pricing:** Free for development, paid plans for production

## 🚀 Quick Setup (Resend - Recommended)

### Step 1: Sign Up for Resend

1. Go to **https://resend.com**
2. Sign up for a free account
3. Verify your email address

### Step 2: Get Your API Key

1. Go to **Resend Dashboard** → **API Keys**
2. Click **"Create API Key"**
3. Name it (e.g., "Ahoy Production")
4. Copy the API key (starts with `re_`)

### Step 3: Add Domain (Required for Production)

1. Go to **Resend Dashboard** → **Domains**
2. Click **"Add Domain"**
3. Enter your domain: `ahoy.ooo`
4. Add DNS records (Resend will show you what to add)
5. Verify domain (can take a few minutes)

### Step 4: Configure on Render

Go to **Render Dashboard** → **ahoy-little-platform** → **Environment** and add:

```
RESEND_API_KEY=re_xxxxx_your_api_key_here
SUPPORT_EMAIL=support@ahoy.ooo
```

**Important:** The `SUPPORT_EMAIL` must be from your verified domain (e.g., `support@ahoy.ooo`)

### Step 5: Test

After deploying, test with:

```bash
# On Render Shell
python scripts/test_send_email_to_alex.py
```

## 🔧 Alternative: SMTP Setup

If you prefer to use SMTP (Gmail, SendGrid, etc.):

### Gmail Example

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Set environment variables on Render:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SUPPORT_EMAIL=your-email@gmail.com
```

### SendGrid Example

```
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=your-sendgrid-api-key
SUPPORT_EMAIL=your-email@yourdomain.com
```

## ✅ Verification

### Check Email Configuration

```bash
# On Render Shell
python -c "from services.emailer import can_send_email; print('Email configured:', can_send_email())"
```

### Test Email Sending

```bash
# On Render Shell
python scripts/test_send_email_to_alex.py
```

### Check Environment Variables

```bash
# On Render Shell
echo $RESEND_API_KEY
echo $SUPPORT_EMAIL
echo $AHOY_ADMIN_EMAIL
```

## 🚨 Troubleshooting

### "Email service not configured"

**Problem:** `can_send_email()` returns `False`

**Solution:**
1. Check `RESEND_API_KEY` is set in Render
2. Check `SUPPORT_EMAIL` is set
3. Verify API key is valid (starts with `re_`)

### "Email sent but not received"

**Possible causes:**
1. **Domain not verified** - Check Resend dashboard
2. **Spam folder** - Check spam/junk folder
3. **Wrong email address** - Verify `AHOY_ADMIN_EMAIL=alex@ahoy.ooo`
4. **Domain DNS not configured** - Add DNS records in Resend

### "Resend API error"

**Common errors:**
- `401 Unauthorized` - Invalid API key
- `422 Unprocessable Entity` - Domain not verified
- `429 Too Many Requests` - Rate limit exceeded

**Solutions:**
1. Verify API key is correct
2. Check domain is verified in Resend
3. Check Resend dashboard for error details

## 📋 Resend Setup Checklist

- [ ] Signed up for Resend account
- [ ] Created API key
- [ ] Added domain `ahoy.ooo` to Resend
- [ ] Added DNS records (SPF, DKIM, DMARC)
- [ ] Verified domain in Resend dashboard
- [ ] Set `RESEND_API_KEY` in Render
- [ ] Set `SUPPORT_EMAIL=support@ahoy.ooo` in Render
- [ ] Tested email sending
- [ ] Received test email at `alex@ahoy.ooo`

## 🔗 Resources

- **Resend Dashboard:** https://resend.com/overview
- **Resend Docs:** https://resend.com/docs
- **Resend API Reference:** https://resend.com/docs/api-reference/emails/send-email
- **Domain Setup:** https://resend.com/docs/dashboard/domains/introduction

## 💡 Why Resend?

- ✅ **Easy Setup** - Just API key, no complex SMTP config
- ✅ **Reliable** - Built for transactional emails
- ✅ **Free Tier** - 3,000 emails/month free
- ✅ **Good Deliverability** - Emails reach inbox
- ✅ **Simple API** - RESTful, easy to use
- ✅ **Dashboard** - See all sent emails

## 📧 Email Addresses Used

- **Admin Notifications:** `alex@ahoy.ooo` (set in `render.yaml`)
- **From Address:** `SUPPORT_EMAIL` (must be from verified domain)
- **Artist Notifications:** Optional, set via `ARTIST_EMAIL_*` env vars
