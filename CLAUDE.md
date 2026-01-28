# CLAUDE.md

## Quick Reference (Read First)

**Current Issues:** None active

**Recent Changes (2026-01-28):**
- Fixed mobile scroll freeze: `static/js/loader.js` now skips ALL code on mobile (exits at line 25)
- Files: `loader.js`, `loader.css`

**Key Paths:**
- App entry: `app.py` (Flask factory `create_app()`)
- Routes: `blueprints/`, `routes/`
- Frontend: `static/js/`, `static/css/`, `templates/`
- Data: `static/data/*.json`
- Mobile scroll fixes: `templates/base.html:500-585`, `static/js/loader.js`

**Cache Busting:** Increment `css_version` in `templates/base.html` (~line 186) when changing CSS/JS

---

## Project Overview

Flask-based media platform (music, shows, artists) with Stripe payments, auth, playlists, bookmarks.

## Commands
```bash
python app.py                    # Run (auto-finds port 5001-5010)
pytest tests/                    # All tests
pytest tests/test_smoke.py -v    # Single file
alembic upgrade head             # Apply migrations
```

## Architecture

| Layer | Location | Notes |
|-------|----------|-------|
| Entry | `app.py`, `wsgi.py` | Flask factory pattern |
| DB | `db.py`, `models.py` | SQLAlchemy, `get_session()` context manager |
| Routes | `blueprints/`, `routes/` | API in `blueprints/api/` |
| Services | `services/` | Business logic (emailer, notifications) |
| Config | `config.py`, `extensions.py` | `AHOY_ENV` switches test/live Stripe |
| Static | `static/data/*.json` | Music, shows, artists JSON |

## Key Patterns

**DB Session:**
```python
with get_session() as session:
    user = session.query(User).filter_by(email=email).first()
```

**Auth:** Flask-Login, `@login_required`, `@admin_required` (from `utils/auth.py`)

**API Response:** `{"success": true, "data": {...}}` or `{"error": "msg"}`

## Mobile / Scroll Issues

**If scroll breaks on mobile, check:**
1. `touch-action: none` in CSS → change to `pan-y`
2. `event.preventDefault()` in touch handlers → remove
3. `overflow: hidden` on body/html → remove
4. Loader script initialization → should exit early on mobile
5. Service worker cache → increment version

**Loader (fixed 2026-01-28):** `loader.js` checks mobile at TOP of IIFE and exits before any code runs. No fetch interceptor or event listeners on mobile. Loader is purely cosmetic.

**Key mobile files:**
- `templates/base.html` - scroll fix script at lines 500-585
- `static/js/loader.js` - mobile exit at line 25
- `static/css/loader.css` - hides loader on mobile via CSS

## Builds

**Desktop (Electron):** `packaging/build-all.sh`, `electron/`

**Mobile (Capacitor):** Remote URL mode - loads from `https://ahoy-indie-media.onrender.com`
```bash
npx cap sync && npx cap open ios   # or android
```

## Env Vars (Required in Production)
`SECRET_KEY`, `DATABASE_URL`, `STRIPE_SECRET_KEY`, `RESEND_API_KEY`, `AHOY_ADMIN_EMAIL`

---

## Session Log

### 2026-01-28: Mobile Scroll Freeze Fix
- **Issue:** Screen froze after loading popup finished
- **Cause:** `loader.js` ran fetch interceptor before mobile check
- **Fix:** Mobile check at TOP of IIFE, exits immediately
- **Files:** `static/js/loader.js`, `static/css/loader.css`
- **Safe:** Loader is cosmetic only, no functionality impact
