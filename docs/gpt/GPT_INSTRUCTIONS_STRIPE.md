# Stripe Integration Instructions for AI Assistant

## Your Role

You are working on behalf of the user on the **Ahoy Indie Media Platform**, a Flask-based web application that allows users to "boost" (tip) artists using Stripe for payment processing.

**Your Mission**: Maintain, debug, enhance, or set up the Stripe payment integration. The integration is implemented and functional, but may need your assistance.

**Act on behalf of the user**: Make decisions, test changes, and implement solutions. Be thorough and document your work.

---

## Critical Business Rules

### Fee Structure (DO NOT CHANGE WITHOUT USER APPROVAL)

**Artists receive 100% of the boost amount. Fees are added on top.**

- **Boost Amount**: What the artist receives (100% goes to artist)
- **Stripe Fee**: (boostAmount × 2.9%) + $0.30
- **Platform Fee**: boostAmount × 7.5%
- **Total Customer Pays**: boostAmount + stripeFee + platformFee

**Example**: $10 boost
- Artist receives: $10.00
- Stripe fee: $0.59
- Platform fee: $0.75
- Customer pays: $11.34

**Implementation**: See `blueprints/payments.py` → `calculate_boost_fees()`

---

## System Architecture

### Payment Flows

**Primary Flow: Stripe Checkout Session**
1. User initiates boost via frontend
2. Backend creates Stripe Checkout Session with 3 line items (boost + fees)
3. User redirected to Stripe-hosted checkout
4. After payment, Stripe sends webhook to `/webhooks/stripe`
5. Webhook handler records Tip in database

**Alternative Flow: Payment Intent**
1. Backend creates PaymentIntent via `/api/boost/stripe/create-intent`
2. Frontend uses Stripe.js to confirm payment
3. Webhook processes `payment_intent.succeeded` event

### Key Files

| File | Purpose |
|------|---------|
| `blueprints/payments.py` | Main payment blueprint, fee calculation, Checkout Session creation |
| `routes/stripe_webhooks.py` | **Primary webhook handler** - processes payment events |
| `routes/boost_stripe.py` | Payment Intent API endpoints |
| `app.py` | Main Flask app, registers blueprints |
| `config.py` | Stripe key selection based on `AHOY_ENV` |
| `models.py` | Database models: `Tip`, `Purchase`, `UserArtistPosition` |

### Database Models

**`Tip` Model** (records all boosts/tips):
- `user_id` (optional - guest tips allowed)
- `artist_id` (required)
- `amount` (boost amount - artist receives 100% of this)
- `stripe_fee`, `platform_fee`, `total_paid`
- `artist_payout` (equals `amount`)
- `platform_revenue` (equals `platform_fee`)
- `stripe_payment_intent_id` (unique, indexed)
- `stripe_checkout_session_id` (unique, indexed)

**`Purchase` Model** (for merch, tickets, etc.):
- `type`: "boost", "tip", "merch", "ticket"
- `stripe_id`: Stripe Checkout Session ID
- `status`: "pending", "paid"

**`UserArtistPosition` Model** (tracks user portfolio):
- `total_contributed`: Total amount user boosted this artist
- `last_tip`: Last boost datetime

---

## Implementation Requirements

### Idempotency (CRITICAL)

**All webhook handlers MUST be idempotent:**

```python
# Always check for existing record first
existing = db_session.query(Tip).filter(
    Tip.stripe_checkout_session_id == session_id
).first()
if existing:
    return jsonify({"status": "ok"}), 200
```

**Why**: Prevents duplicate charges if Stripe retries webhook delivery.

### Webhook Event Handling

**`routes/stripe_webhooks.py`** handles:

1. **`checkout.session.completed`**
   - Updates `Purchase.status` if `purchase_id` in metadata
   - Creates `Tip` record if `type=boost` or `type=tip`
   - Updates `UserArtistPosition` if `user_id` present

2. **`payment_intent.succeeded`**
   - Creates `Tip` record from PaymentIntent metadata
   - Updates `UserArtistPosition` if `user_id` present

### Required Metadata

Stripe Checkout Sessions and PaymentIntents MUST include:

```python
metadata = {
    "artist_id": str,
    "user_id": str (or "" for guests),
    "boost_amount": str,
    "stripe_fee": str,
    "platform_fee": str,
    "total_paid": str,
    "artist_payout": str,
    "platform_revenue": str,
    "purchase_id": str (optional),
    "type": str ("boost", "tip", "merch", "ticket")
}
```

### Guest Payments

- Users can boost without logging in
- `user_id` will be `None` or empty string
- Tip record is created, but `UserArtistPosition` is NOT updated

---

## Configuration

### Environment Variables

Stripe keys are selected based on `AHOY_ENV`:

- `AHOY_ENV=development` (or `sandbox`) → Uses `*_TEST` keys
- `AHOY_ENV=production` → Uses live keys

**Required Variables:**

```bash
# Development
AHOY_ENV=development
STRIPE_PUBLISHABLE_KEY_TEST="pk_test_..."
STRIPE_SECRET_KEY_TEST="sk_test_..."
STRIPE_WEBHOOK_SECRET_TEST="whsec_..."

# Production
AHOY_ENV=production
STRIPE_PUBLISHABLE_KEY="pk_live_..."
STRIPE_SECRET_KEY="sk_live_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
```

**Configuration Logic** (`config.py`):
```python
_USE_TEST_KEYS = _AHOY_ENV in ("development", "sandbox")
STRIPE_SECRET_KEY = os.environ.get(
    "STRIPE_SECRET_KEY_TEST" if _USE_TEST_KEYS else "STRIPE_SECRET_KEY",
    ""
)
```

---

## Production Setup Checklist

### Step 1: Get API Keys from Stripe Dashboard

1. Navigate to: **https://dashboard.stripe.com/apikeys**
2. Ensure you're in **Live mode** (toggle in top right)
3. Copy:
   - **Publishable key** (`pk_live_...`)
   - **Secret key** (`sk_live_...`) - Click "Reveal" to view full key

### Step 2: Create Webhook Endpoint

1. Navigate to: **https://dashboard.stripe.com/webhooks**
2. Click **"Add endpoint"**
3. Enter webhook URL: `https://yourdomain.com/webhooks/stripe`
   - Replace `yourdomain.com` with actual production domain
4. Select events:
   - ✅ `checkout.session.completed`
   - ✅ `payment_intent.succeeded`
5. Click **"Add endpoint"**
6. **Copy the Signing secret** (`whsec_...`)

### Step 3: Verify Webhook Settings

- ✅ Webhook shows **green SSL checkmark** (HTTPS required)
- ✅ Correct events are enabled
- ✅ Optionally send test event to verify delivery

### Step 4: Set Environment Variables in Deployment

In your deployment platform (Render, Heroku, Vercel, etc.):

```bash
AHOY_ENV=production
STRIPE_PUBLISHABLE_KEY="pk_live_..."  # From Step 1
STRIPE_SECRET_KEY="sk_live_..."       # From Step 1
STRIPE_WEBHOOK_SECRET="whsec_..."     # From Step 2
```

**Security**: Never commit these keys to version control.

### Step 5: Repository Setup (Local Development)

**Create or update `.env` file in repository:**

```bash
AHOY_ENV=production
STRIPE_PUBLISHABLE_KEY=<your pk_live key>
STRIPE_SECRET_KEY=<your sk_live key>
STRIPE_WEBHOOK_SECRET=<your webhook signing secret>
```

**CRITICAL**: Ensure `.env` files are listed in `.gitignore` so they aren't committed to version control.

**Note**: The repository's `.gitignore` already includes `.env`, `.env.*`, and `*.env` patterns, but always verify before committing sensitive files.

### Step 6: Verify config.py

Confirm that `config.py` correctly reads live keys when `AHOY_ENV=production`:

```python
_USE_TEST_KEYS = _AHOY_ENV in ("development", "sandbox")
STRIPE_SECRET_KEY = os.environ.get(
    "STRIPE_SECRET_KEY_TEST" if _USE_TEST_KEYS else "STRIPE_SECRET_KEY",
    ""
)
STRIPE_PUBLISHABLE_KEY = os.environ.get(
    "STRIPE_PUBLISHABLE_KEY_TEST" if _USE_TEST_KEYS else "STRIPE_PUBLISHABLE_KEY",
    ""
)
STRIPE_WEBHOOK_SECRET = os.environ.get(
    "STRIPE_WEBHOOK_SECRET_TEST" if _USE_TEST_KEYS else "STRIPE_WEBHOOK_SECRET",
    ""
)
```

**Note**: No code changes should be necessary if this logic is already implemented (it should be).

### Step 7: Deploy with Environment Variables

When deploying to your platform (Render, Heroku, Vercel, etc.), set these environment variables:

```bash
AHOY_ENV=production
STRIPE_PUBLISHABLE_KEY=<your pk_live key from Step 1>
STRIPE_SECRET_KEY=<your sk_live key from Step 1>
STRIPE_WEBHOOK_SECRET=<your webhook signing secret from Step 2>
```

**Platform-specific instructions:**
- **Render**: Environment → Environment Variables
- **Heroku**: Settings → Config Vars
- **Vercel**: Settings → Environment Variables

### Step 8: Test Live Flow

After deployment, perform a small live boost to confirm:

1. ✅ **Checkout Session/Payment Intent created successfully**
   - Verify in Stripe Dashboard → Payments
   - Check that charge appears correctly

2. ✅ **Webhook fires and creates Tip record**
   - Check server logs for webhook receipt
   - Verify Tip record created in database
   - Check `stripe_checkout_session_id` or `stripe_payment_intent_id` matches

3. ✅ **Idempotency prevents duplicates**
   - Try triggering webhook again (or wait for retry)
   - Verify no duplicate Tip records created

4. ✅ **Check Stripe webhook delivery logs**
   - Go to: https://dashboard.stripe.com/webhooks
   - Click on your endpoint → "Event deliveries"
   - Verify successful delivery (200 status)

**These steps will fully integrate live Stripe credentials without exposing secrets.**

---

## Code Patterns

### Creating Stripe Checkout Session

```python
from blueprints.payments import calculate_boost_fees
from decimal import Decimal

boost_amount_decimal = Decimal(str(boost_amount))
stripe_fee, platform_fee, total_charge, artist_payout, platform_revenue = calculate_boost_fees(boost_amount_decimal)

checkout_session = stripe.checkout.Session.create(
    payment_method_types=["card"],
    line_items=[
        {
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Boost Amount", "description": "100% goes directly to the artist"},
                "unit_amount": int(boost_amount_decimal * 100),
            },
            "quantity": 1,
        },
        {
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Stripe Processing Fee", "description": "2.9% + $0.30"},
                "unit_amount": int(stripe_fee * 100),
            },
            "quantity": 1,
        },
        {
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Ahoy Indie Media Platform Fee", "description": "7.5% platform fee"},
                "unit_amount": int(platform_fee * 100),
            },
            "quantity": 1,
        }
    ],
    mode="payment",
    success_url=request.host_url.rstrip("/") + "/payments/success?session_id={CHECKOUT_SESSION_ID}",
    cancel_url=request.host_url.rstrip("/") + "/payments/cancel",
    metadata={
        "artist_id": str(artist_id),
        "user_id": str(user_id or ""),
        "boost_amount": str(boost_amount_decimal),
        "stripe_fee": str(stripe_fee),
        "platform_fee": str(platform_fee),
        "total_paid": str(total_charge),
        "artist_payout": str(artist_payout),
        "platform_revenue": str(platform_revenue),
    },
)
```

### Recording Tip from Webhook

```python
from models import Tip
from decimal import Decimal
from datetime import datetime

# CRITICAL: Check idempotency first
existing = db_session.query(Tip).filter(
    Tip.stripe_checkout_session_id == session_id
).first()
if existing:
    return jsonify({"status": "ok"}), 200

# Create Tip record
tip = Tip(
    user_id=user_id,
    artist_id=str(artist_id),
    amount=Decimal(boost_amount_str),
    stripe_fee=Decimal(stripe_fee_str) if stripe_fee_str else Decimal("0.00"),
    platform_fee=Decimal(platform_fee_str),
    total_paid=Decimal(total_paid_str),
    artist_payout=Decimal(artist_payout_str),
    platform_revenue=Decimal(platform_revenue_str) if platform_revenue_str else Decimal(platform_fee_str),
    stripe_checkout_session_id=session_id,
    stripe_payment_intent_id=payment_intent_id,
    created_at=datetime.utcnow(),
)
db_session.add(tip)

# Update portfolio if user logged in
if user_id:
    from blueprints.payments import update_user_artist_position
    update_user_artist_position(
        user_id=user_id,
        artist_id=str(artist_id),
        boost_amount=Decimal(boost_amount_str),
        boost_datetime=datetime.utcnow(),
        db_session=db_session,
    )

db_session.commit()
```

---

## Testing & Debugging

### Test Webhooks Locally

```bash
# Forward webhooks to local server
stripe listen --forward-to localhost:5000/webhooks/stripe

# Trigger test event
stripe trigger checkout.session.completed
```

### Verify Webhook Configuration

```bash
# Check webhook endpoint exists
stripe webhook_endpoints list

# Or verify in Dashboard
# https://dashboard.stripe.com/webhooks
```

### Debugging Checklist

1. **Payment not recorded?**
   - Check webhook delivery logs in Stripe Dashboard
   - Verify webhook endpoint URL is correct
   - Check server logs for errors

2. **Duplicate records?**
   - Shouldn't happen due to idempotency
   - Check unique constraints on `stripe_checkout_session_id` and `stripe_payment_intent_id`

3. **Missing metadata?**
   - Verify Checkout Session/PaymentIntent creation includes all required metadata
   - Check webhook handler logs

4. **Fee calculation errors?**
   - Check `calculate_boost_fees()` in `blueprints/payments.py`
   - Verify Decimal precision (never use float for money)

---

## Critical Rules to Follow

1. **Never modify fee calculation logic** without user approval
2. **Always check idempotency** before creating Tip records
3. **Preserve metadata** - it's critical for webhook processing
4. **Test in test mode first** before touching live keys
5. **Use Decimal for money** - never use float
6. **Verify webhook signature** in production (fallback allowed in dev)

---

## When Starting Work

1. ✅ Check webhook endpoint: `stripe webhook_endpoints list` or verify in Dashboard
2. ✅ Verify environment variables are set correctly
3. ✅ Test payment flow in test mode first
4. ✅ Check webhook delivery logs in Stripe Dashboard
5. ✅ Review recent Tip records in database

---

## Questions to Ask User

If you need clarification:
- What specific issue are you experiencing with Stripe?
- Are you in test mode or live mode?
- What error messages are you seeing?
- Have you checked the Stripe Dashboard webhook delivery logs?
- Are payments being charged but not recorded in the database?

---

**Remember**: Act on behalf of the user. Be thorough, test changes, and document modifications.
