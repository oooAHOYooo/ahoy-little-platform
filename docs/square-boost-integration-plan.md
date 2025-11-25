## Square Boost Integration Plan (Server + Dashboard)

Goal: Switch the “Boost” flow from Stripe Checkout to Square Web Payments SDK with server-side verification and webhooks, working in both sandbox and production via `AHOY_ENV`.

### Current State (as of this commit)
- Env/config
  - `config.py`: class-based config driven by `AHOY_ENV` (`sandbox` or `production`), exposing `SQUARE_ENV`, `SQUARE_APPLICATION_ID`, `SQUARE_ACCESS_TOKEN`.
  - `services/square_client.py`: `get_square_client()` returns a configured Square `Client` using correct `environment` and access token.
  - CORS: `extensions.py:init_cors()` now allows origins:
    - `https://app.ahoy.ooo`
    - `https://api.ahoy.ooo`
    - `http://localhost:5173`
    - `http://localhost:5000`
    and preflights are handled.
  - Docs: `docs/square-setup.md` explains Square Dashboard steps (Allowed Origins, Apple Pay domain verification, common errors).

- Payments implementation (Stripe, to be replaced with Square):

```110:223:blueprints/payments.py
@bp.route("/boost-session", methods=["POST"])
def create_boost_session():
    """
    Create a Stripe Checkout session for boosting an artist.
    ...
    """
    if not stripe.api_key:
        return jsonify({"error": "Stripe not configured"}), 500
    ...
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[ ... three line items ... ],
        mode="payment",
        success_url=request.host_url.rstrip("/") + "/payments/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.host_url.rstrip("/") + "/payments/cancel",
        metadata={ ... artist_id, user_id, fees ... },
    )
    return jsonify({"checkout_url": checkout_session.url, ...}), 200
```

```228:338:blueprints/payments.py
@bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events."""
    ...
    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]
        metadata = session_data.get("metadata", {})
        ...
        with get_session() as db_session:
            tip = Tip(... )  # persists boost result
            db_session.add(tip)
            update_user_artist_position(... )
            db_session.commit()
    return jsonify({"status": "received"}), 200
```

The boost records are created when Stripe confirms via webhook, and fee breakdown is already calculated server-side in this blueprint. Square needs to mirror this behavior.

### What we will implement for Square
1) Client-side (Web Payments SDK)
   - On the frontend (outside this repo), initialize Web Payments with the Application ID matching `AHOY_ENV`.
   - Tokenize card (or wallets like Apple Pay once domain is verified) to obtain a payment token (sourceId).
   - POST token and `artist_id`/`amount` to our new Square endpoint.

2) Server-side endpoints (Flask)
   - Create a new route (e.g., `POST /payments/sq/charge`) to:
     - Validate payload (artist_id, amount, sourceId).
     - Use `get_square_client()` to call Payments API:
       - Create Payment with idempotency key, amount, currency “USD”, and metadata (artist_id, user_id, fee breakdown).
     - On success, persist `Tip` similarly to the Stripe path (or let webhook do it and return success early).
     - On failure, return a 400/402 with error detail.
   - Add a Square webhook endpoint (e.g., `POST /payments/sq/webhook`) to:
     - Verify Square signature (if configured).
     - On payment `COMPLETED` event, persist `Tip` and update user artist position identical to Stripe logic.

3) Fee handling
   - Reuse existing fee calculation:

```30:59:blueprints/payments.py
def calculate_boost_fees(boost_amount: Decimal):
    # 7.5% platform fee, Stripe-like fee (2.9% + $0.30) currently modeled
    # We can keep this breakdown for Square charges (the math is independent of provider)
```

   - Store the same metadata fields, so the UI and analytics remain consistent.

4) Environment and credentials
   - Backend uses `AHOY_ENV` to pick tokens automatically.
   - Frontend must also pick the correct Application ID per environment.
   - Allowed Origins configured in Square Dashboard must match:
     - `https://app.ahoy.ooo`, `https://api.ahoy.ooo`, `http://localhost:5173`, `http://localhost:5000`

5) Apple Pay
   - Verify the `app.ahoy.ooo` domain in Square Dashboard and host verification file at:
     - `https://app.ahoy.ooo/.well-known/apple-developer-merchantid-domain-association`

### Milestones
1. Add Square endpoints (`/payments/sq/charge`, `/payments/sq/webhook`) that mirror existing Stripe behaviors.
2. Frontend: integrate Square Web Payments SDK to tokenize and POST `sourceId` to our charge endpoint.
3. Verify sandbox flow end-to-end with `AHOY_ENV=sandbox`.
4. Switch to production by setting `AHOY_ENV=production` and providing Production credentials.

### Env Vars (documented in README and .env.example)
- `AHOY_ENV`: `sandbox` or `production`
- Sandbox:
  - `SQUARE_APPLICATION_ID_SANDBOX`
  - `SQUARE_ACCESS_TOKEN_SANDBOX`
- Production:
  - `SQUARE_APPLICATION_ID_PRODUCTION`
  - `SQUARE_ACCESS_TOKEN_PRODUCTION`

### Common pitfalls
- Disallowed origin: Dashboard Allowed Origins must exactly match schemes/hosts/ports.
- Using Sandbox creds in Production (or vice versa): Ensure `AHOY_ENV` matches.
- Apple Pay not showing: Domain not verified or testing on unsupported browser/device.
- Missing sourceId / tokenization: Client did not await tokenize() or failed silently on origin mismatch.


