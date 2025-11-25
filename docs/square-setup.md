## Square Web Payments SDK setup for Ahoy Indie Media (Production)

This guide walks through the exact Square Dashboard steps required to enable credit card payments for `app.ahoy.ooo` using Square’s Web Payments SDK.

### Before you start
- Ensure you have admin access to the Square Developer Dashboard for the Ahoy Indie Media app.
- Confirm you intend to enable payments in Production (not Sandbox).

### 1) Open the correct app in Square Developer Dashboard (Production)
1. Go to the Square Developer Dashboard: [Square Developer Dashboard](https://developer.squareup.com/apps)
2. Select the app named “Ahoy Indie Media”.
3. Switch the environment to Production (top right environment switcher).
4. On the Credentials page, note the Production Application ID and Production Access Token. These must be used by the web app (client uses Application ID) and backend/API (server uses Access Token).

![Screenshot placeholder — Developer Dashboard Apps list](./images/square/placeholder-apps.png)

![Screenshot placeholder — App overview and environment switch](./images/square/placeholder-app-overview.png)

### 2) Configure Web Payments SDK Allowed Origins
1. In the left navigation, go to: Web → Web Payments SDK (sometimes listed under “Configuration”).
2. Find “Allowed Origins” (may be labeled “Allowed Domains”).
3. Add the following origins exactly as shown (no trailing slashes; include scheme):

```
https://app.ahoy.ooo
https://api.ahoy.ooo
http://localhost:5173
http://localhost:5000
```

4. Save your changes.
5. Wait a minute for settings to propagate, then hard-refresh your browser (or clear cache) when testing.

Notes:
- Production must use `https` origins. Local development often uses `http://localhost` with the port your dev server runs on.
- If you use additional local ports or preview URLs, add each origin explicitly.

![Screenshot placeholder — Web Payments SDK Allowed Origins](./images/square/placeholder-allowed-origins.png)

### 3) Ensure Production credentials are used (not Sandbox)
- Application (client): Use the Production Application ID in the Web Payments SDK initialization.
- Backend/API: Use the Production Access Token for all charge/payment server calls.
- Double-check any environment variables or configuration (e.g., deployment secrets) to ensure Production values are deployed to `app.ahoy.ooo` and `api.ahoy.ooo`.

![Screenshot placeholder — Production credentials](./images/square/placeholder-prod-credentials.png)

### 4) Apple Pay domain verification (Production)
To support Apple Pay on the web, Apple requires domain verification.
1. In the Square Dashboard, navigate to: Web → Digital Wallets → Apple Pay.
2. Add the domain you will serve the checkout from, e.g. `app.ahoy.ooo`.
3. Download the Apple Pay domain verification file provided by Square.
4. Host the file at: `https://app.ahoy.ooo/.well-known/apple-developer-merchantid-domain-association`
   - Ensure the filename and path are exact.
   - The file must be accessible publicly over HTTPS.
5. Return to the Square Dashboard and click Verify for the domain.

Notes:
- Apple Pay generally won’t work on `localhost`; use a secure, publicly accessible domain for testing.
- If you render the payment page on another domain or subdomain, that domain must be verified too.

![Screenshot placeholder — Apple Pay domain verification](./images/square/placeholder-apple-pay.png)

### 5) Common errors and fixes
- “disallowed origin”
  - Cause: The current page’s origin is not in Allowed Origins, or the scheme/host/port mismatch.
  - Fix: Add the exact origin (including scheme and port). Remove trailing slashes. Wait a minute and hard-refresh.

- “card_nonce undefined” or missing token/source
  - Cause: Using legacy variable names (old “nonce”) or tokenization not awaited/handled; or SDK not initialized on an allowed origin.
  - Fix: Ensure you await the Web Payments SDK tokenization call and use the correct property returned by the current SDK version. Confirm the origin is allowed and credentials are Production.

- “payment not enabled”
  - Cause: The Square account or application is not enabled for online card payments, or you’re using Sandbox in Production.
  - Fix: Confirm the Square account supports card payments, you’re using Production Application ID/Access Token, and the environment is set to Production.

- Apple Pay button not showing or failing verification
  - Cause: Domain not verified, not using HTTPS, or not on an Apple Pay–capable device/browser.
  - Fix: Complete Apple Pay domain verification, ensure HTTPS, and test with Safari on a compatible device with Apple Pay set up.

- 401/403 from server during payment
  - Cause: Production Access Token not configured on server, or mismatched app credentials.
  - Fix: Set Production Access Token on the backend and ensure Application ID/Access Token belong to the same Production app.

### 6) Quick validation checklist
- App is selected in Production environment (not Sandbox).
- `https://app.ahoy.ooo` and `https://api.ahoy.ooo` added to Allowed Origins.
- Local dev origins added (`http://localhost:5173`, `http://localhost:5000`).
- Production Application ID used by the client; Production Access Token used by the server.
- Apple Pay domain verification complete for `app.ahoy.ooo` (if using Apple Pay).
- Hard-refresh after changes; consider clearing cache.

### References
- [Square Web Payments SDK](https://developer.squareup.com/docs/web-payments/overview)
- [Apple Pay on the Web with Square](https://developer.squareup.com/docs/web-payments/apple-pay)


