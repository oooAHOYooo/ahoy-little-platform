# Email Notifications System

## Overview

The Ahoy platform uses a unified notification system with rate limiting and retry logic to handle Resend's 2 requests/second limit reliably.

## Email Service

- **Provider:** Resend API (preferred) or SMTP (fallback)
- **Rate Limit:** 2 requests/second (handled automatically with retry)
- **From Address:** `SUPPORT_EMAIL` environment variable
- **Admin Address:** `AHOY_ADMIN_EMAIL` (defaults to alex@ahoy.ooo)

## Notification Functions

### `notify_admin(subject, text, tags=None)`

Sends email to admin (`AHOY_ADMIN_EMAIL`).

- Automatically prefixes subject with environment label: `[dev]`, `[staging]`, etc. (production has no label)
- Uses `send_email_with_retry()` for rate limit handling
- Returns: `{ok: bool, provider: str, detail: {...}}`

### `notify_user(to_email, subject, text, tags=None)`

Sends email to user.

- Uses `SUPPORT_EMAIL` as From address
- Environment label only added for non-production
- Uses `send_email_with_retry()` for rate limit handling
- Returns: `{ok: bool, provider: str, detail: {...}}`

## Rate Limiting & Retry

The `send_email_with_retry()` function handles Resend 429 errors automatically:

- **Max Retries:** 5 attempts
- **Exponential Backoff:** 0.7s, 1.2s, 2.0s, 3.5s, 5.0s
- **Jitter:** Random +/- 0.2s to avoid thundering herd
- **Never Throws:** Always returns result dict, never crashes

## Email Events

### User Registration

**Triggers:**
- `POST /api/auth/register`

**Emails Sent:**
- **Admin:** "New User Registration: {email}"
- **User:** "Welcome to Ahoy Indie Media ✨" with welcome message and link

### Password Reset Request

**Triggers:**
- `POST /api/auth/password-reset/request`

**Emails Sent:**
- **User:** "Reset your Ahoy password" with reset link
- **Admin:** "Password reset requested for {email}" (optional, non-blocking)

### Wallet Funding

**Triggers:**
- Stripe webhook: `checkout.session.completed` with `type=wallet_fund`

**Emails Sent:**
- **Admin:** "Wallet Funded: ${amount} by {email}" with balance details
- **User:** "Wallet Funded: ${amount} Added" confirmation with new balance

### Artist Boost

**Triggers:**
- Stripe webhook: `checkout.session.completed` with boost metadata

**Emails Sent:**
- **Admin:** "New Boost: ${amount} to {artist}" with payout details
- **User (Tipper):** "Boost Confirmation: ${amount} to {artist}" receipt
- **Artist (Optional):** "You received a ${amount} boost!" if artist email configured

### Merch Purchase

**Triggers:**
- Stripe webhook: `checkout.session.completed` with merch metadata

**Emails Sent:**
- **Admin:** "New Merch Purchase: ${total}" with order details
- **User (Buyer):** "Order Confirmation: {item}" receipt

## Testing

### Test All Notifications

```bash
python scripts/test_send_email_to_alex.py
```

This script:
- Tests `notify_admin()` and `notify_user()`
- Tests all event types (registration, boost, wallet, merch)
- Spaces out sends to avoid rate limits
- Prints summary of passed/failed tests

### Test Email Configuration

```bash
python scripts/check_email_config.py
```

Shows:
- Resend/SMTP configuration status
- Admin and support email addresses
- Sends test email if configured

## Error Handling

- **Email failures never break user actions** - all notifications are non-blocking
- **Rate limit errors automatically retry** with exponential backoff
- **Failures are logged** but don't affect main functionality
- **Missing email config** is handled gracefully (warnings, no crashes)

## Environment Variables

**Required:**
```bash
RESEND_API_KEY=re_xxxxx  # OR SMTP_* variables
SUPPORT_EMAIL=support@ahoy.ooo
AHOY_ADMIN_EMAIL=alex@ahoy.ooo
```

**Optional:**
```bash
AHOY_ENV=production  # For environment labels (dev/staging/prod)
BASE_URL=https://app.ahoy.ooo  # For links in emails
```

## Implementation Details

- All notifications use `send_email_with_retry()` wrapper
- Retry logic handles 429 rate limit errors automatically
- Environment labels added to subjects (except production)
- HTML emails generated from text (simple conversion)
- Failures logged but don't crash the application

## Monitoring

Check Resend Dashboard → Emails to see:
- All sent emails
- Delivery status
- Rate limit events
- Error details
