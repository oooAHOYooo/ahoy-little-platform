# Stripe Payment Security - How It Works

## Overview
Ahoy uses **Stripe Checkout** for all payment processing, which is the most secure and PCI-compliant way to handle credit card payments.

## How Credit Card Entry Works

### 1. User Initiates Payment
- User clicks "Add $5 to get started" or "Fund Wallet"
- Your app creates a Stripe Checkout Session
- User is redirected to Stripe's secure, hosted checkout page

### 2. Stripe's Secure Checkout Page
- **User enters credit card details on Stripe's website** (not on your site)
- Stripe's URL: `https://checkout.stripe.com/...`
- This is PCI-DSS Level 1 compliant (the highest security standard)
- Your server never sees or stores credit card numbers

### 3. Payment Processing
- Stripe processes the payment securely
- Stripe sends a webhook to your server when payment succeeds
- Your server adds funds to the user's wallet

### 4. Return to Your Site
- User is redirected back to `/payments/wallet/success`
- Wallet balance is updated via webhook

## Security Benefits

### ✅ PCI Compliance
- **You never handle credit card data** - Stripe does
- No PCI compliance burden on your infrastructure
- Stripe is PCI-DSS Level 1 certified

### ✅ Secure by Default
- Stripe Checkout uses HTTPS and secure protocols
- Card data is encrypted in transit and at rest
- Stripe handles all security updates and patches

### ✅ Fraud Protection
- Stripe's built-in fraud detection (Radar)
- 3D Secure authentication when required
- Automatic chargeback protection

### ✅ User Trust
- Users see Stripe's trusted brand
- Familiar checkout experience
- Clear security indicators

## What You Store

### ✅ Safe to Store
- Stripe Customer ID (e.g., `cus_ABC123`)
- Stripe Payment Intent ID (e.g., `pi_XYZ789`)
- Transaction amounts and metadata
- Wallet balances

### ❌ Never Store
- Credit card numbers
- CVV codes
- Expiration dates
- Full cardholder names (unless needed for business)

## Testing

### Test Cards (Stripe Test Mode)
```
Card Number: 4242 4242 4242 4242
Expiry: Any future date (e.g., 12/25)
CVC: Any 3 digits (e.g., 123)
ZIP: Any 5 digits (e.g., 12345)
```

### Test Scenarios
1. **Successful payment**: Use test card `4242 4242 4242 4242`
2. **Declined payment**: Use test card `4000 0000 0000 0002`
3. **3D Secure**: Use test card `4000 0025 0000 3155`

## Flow Diagram

```
User clicks "Fund Wallet"
    ↓
Your server: POST /payments/wallet/fund
    ↓
Create Stripe Checkout Session
    ↓
Return checkout_url to frontend
    ↓
Frontend redirects to: checkout.stripe.com
    ↓
[USER ENTERS CARD DETAILS HERE - ON STRIPE'S SECURE PAGE]
    ↓
Stripe processes payment
    ↓
Stripe webhook → Your server: /webhooks/stripe
    ↓
Your server adds funds to wallet
    ↓
User redirected to: /payments/wallet/success
```

## Best Practices

1. **Always use Stripe Checkout** for card entry (never collect cards directly)
2. **Verify webhook signatures** to ensure requests are from Stripe
3. **Use idempotency keys** to prevent duplicate processing
4. **Store minimal payment data** - only what you need
5. **Handle webhook failures** gracefully with retries

## Resources

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Security Guide](https://stripe.com/docs/security)
- [PCI Compliance](https://stripe.com/docs/security/guide)
