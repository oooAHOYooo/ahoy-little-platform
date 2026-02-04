# Password Reset User Journey

This documents the end-to-end user experience and the backend flows for
forgetting and resetting a password.

## Journey Overview

1. User visits `/auth` and clicks "Forgot password?" (inline panel), or visits
   `/auth/forgot` directly.
2. User enters email and submits the request.
3. Backend accepts the request, rate-limits, and always returns success to avoid
   account enumeration.
4. If email is configured and the user exists, the system emails a reset link:
   `/auth/reset?token=...` (token expires in 1 hour).
5. User opens the link, sets a new password, and submits.
6. Backend validates the token and updates the password, then the UI redirects
   to `/auth` to sign in.

## Mermaid Flowchart

```mermaid
flowchart TD
  A[Auth page /auth] -->|Clicks "Forgot password?"| B[Inline forgot panel]
  A -->|Direct visit| C[/auth/forgot]
  B --> D[Enter email + submit]
  C --> D

  D --> E[POST /api/auth/password-reset/request]
  E --> F{Valid email format?}
  F -->|No| G[Return success message]
  F -->|Yes| H{Email config available?}
  H -->|No| G
  H -->|Yes| I{User exists?}
  I -->|No| G
  I -->|Yes| J[Send reset email\n(link expires in 1 hour)]
  J --> G

  G --> K[User receives success message]
  K --> L[User opens reset link]
  L --> M[/auth/reset page reads token]
  M --> N{Token present?}
  N -->|No| O[Show error + ask to request new link]
  N -->|Yes| P[User enters new password]
  P --> Q[POST /api/auth/password-reset/confirm]
  Q --> R{Token valid + unexpired?}
  R -->|No| S[Show error (expired/invalid)]
  R -->|Yes| T[Update password]
  T --> U[Success message + redirect to /auth]
```

## Error States & Safeguards

- **No enumeration:** request endpoint always returns success, even if email
  doesn't exist.
- **Rate limits:** request endpoint is limited to 5/min; confirm is 10/min.
- **Token expiry:** reset token expires after 1 hour.
- **Token invalidation:** token includes a password-hash version; changing the
  password invalidates previous tokens.
- **Missing token:** `/auth/reset` shows a user-facing error if `token` is
  missing in the URL.

## Key Endpoints and Pages

- Page: `/auth` (inline forgot panel)
- Page: `/auth/forgot` (dedicated forgot page)
- API: `POST /api/auth/password-reset/request`
- Page: `/auth/reset?token=...` (password reset form)
- API: `POST /api/auth/password-reset/confirm`
