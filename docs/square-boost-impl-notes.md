## Square Boost Integration — Implementation Notes and Action Items

This document summarizes what’s implemented in the repo, what you need to do in Square, and how to wire your frontend to complete the Boost flow using Square Web Payments SDK. It’s intended as a handoff/reference for engineers (or GPT) to finish or troubleshoot production rollout.

### What’s implemented (server)
- Environment-driven configuration for Square:
  - `config.py` now uses `AHOY_ENV` (sandbox|production) to select credentials automatically.
  - Exposes `SQUARE_ENV`, `SQUARE_APPLICATION_ID`, `SQUARE_ACCESS_TOKEN`, `SQUARE_LOCATION_ID` from env vars.
- Square Client helper:
  - `services/square_client.py:get_square_client()` constructs the Square `Client` with the correct `environment` and access token based on `AHOY_ENV`.
- Payments blueprint additions:
  - `POST /payments/sq/charge`:
    - Body: `{ "sourceId": string, "artist_id": string, "boost_amount": number|string }`
    - Creates a Square payment using the configured Location ID and stores associated boost in the `tips` table immediately (with fee breakdown reused from Stripe logic).
    - Returns `{ status, payment_id, breakdown }` on success.
- CORS enabled for the target origins:
  - `extensions.py:init_cors()` allows:
    - `https://app.ahoy.ooo`
    - `https://api.ahoy.ooo`
    - `http://localhost:5173`
    - `http://localhost:5000`
  - Preflight OPTIONS handled automatically.
- Dependencies/docs:
  - `requirements.txt` includes `squareup` SDK.
  - `docs/square-setup.md`: Square Dashboard setup (Allowed Origins, Apple Pay, common errors).
  - `docs/square-boost-integration-plan.md`: Technical plan with current Stripe flow references and Square steps.
  - `README.md` documents `AHOY_ENV` and Square env vars.

### Required environment variables (production)
Set these on your production server (do NOT commit secrets):
- `AHOY_ENV=production`
- `SQUARE_APPLICATION_ID_PRODUCTION=<your prod app id>`
- `SQUARE_ACCESS_TOKEN_PRODUCTION=<your rotated prod access token>`
- `SQUARE_LOCATION_ID_PRODUCTION=<your Square production location id>`
Optional:
- `SQUARE_WEBHOOK_SIGNATURE_KEY_PRODUCTION=<for webhook verification if you add it>`

For sandbox testing (optional), mirror the above with `_SANDBOX` variables and `AHOY_ENV=sandbox`.

### Square Dashboard setup (production)
1. Allowed Origins under Web Payments SDK:
   - `https://app.ahoy.ooo`
   - `https://api.ahoy.ooo`
   - `http://localhost:5173`
   - `http://localhost:5000`
2. Apple Pay (optional, recommended):
   - Verify `https://app.ahoy.ooo` domain and host the file at:
     - `https://app.ahoy.ooo/.well-known/apple-developer-merchantid-domain-association`
3. Location ID:
   - Confirm the production Location ID (the repo expects it via `SQUARE_LOCATION_ID_PRODUCTION`).
4. Webhook (optional for reconciliation):
   - Point to `https://api.ahoy.ooo/payments/sq/webhook` and capture a signature key.

### Frontend integration (Web Payments SDK)
1. Initialize the SDK with the Production Application ID.
2. Tokenize the card/wallet to obtain `sourceId`.
3. POST to `/payments/sq/charge`:
   - JSON:
     ```json
     {
       "sourceId": "<from Square SDK>",
       "artist_id": "<slug-or-id>",
       "boost_amount": 5.00
     }
     ```
4. On success, you’ll receive:
   ```json
   {
     "status": "success",
     "payment_id": "xxx",
     "breakdown": {
       "boost_amount": 5.0,
       "processing_fee": 0.45,
       "platform_fee": 0.38,
       "total_charge": 5.83
     }
   }
   ```
5. Optionally, show a success page or toast. Data is already persisted server-side.

Notes:
- The server reuses existing fee math (artist receives 100%; tipper pays processing + platform fee).
- The server stores the Square `payment.id` in the existing `Tip.stripe_payment_intent_id` field to avoid schema changes.

### API reference
- `POST /payments/sq/charge`
  - Request:
    - `sourceId`: string (required)
    - `artist_id`: string (required)
    - `boost_amount`: number|string (required, >= 0.50)
  - Responses:
    - 200: `{ status: "success", payment_id, breakdown }`
    - 200: `{ status: "payment_success_persist_error", error, payment_id }` (payment succeeded; DB persist failed)
    - 400: `{ error: "..." }` (validation or Square API error)
    - 500: `{ error: "..." }` (misconfiguration)

### Testing checklist (production)
1. Set env vars and restart app with `AHOY_ENV=production`.
2. Verify `/healthz` and `/readyz`.
3. Make a small boost (e.g., $1.00) from the frontend:
   - Confirm `POST /payments/sq/charge` returns 200.
   - Check server logs for the created payment ID and persisted `Tip`.
   - Verify the record exists in DB (table `tips`).
4. Confirm funds and timeline in Square Dashboard → Payments.

### Optional: Webhook reconciliation
If you want double-entry verification:
1. Create `POST /payments/sq/webhook` endpoint that:
   - Verifies Square signature using `SQUARE_WEBHOOK_SIGNATURE_KEY_*`.
   - On `payment.UPDATED` or `payment.COMPLETED`, upsert the `Tip` (idempotent).
2. Configure webhook in Square Dashboard to call that URL.

### Common pitfalls
- Disallowed origin: origins must match scheme/host/port exactly in Dashboard.
- Sandbox/production mismatch: ensure `AHOY_ENV` and credentials align.
- Apple Pay: requires domain verification and HTTPS on a compatible device/browser.
- Missing `sourceId`: ensure frontend awaits tokenization and handles errors.


