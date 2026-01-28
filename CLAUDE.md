# CLAUDE.md

## Quick Reference (Read First)

**Current Issues:** None active

**Recent Changes (2026-01-28):**
- Spotify-style persistent mini player: always visible, no full-screen player
- Service worker v9: network-first for HTML (users always see latest push)
- Fixed mobile scroll freeze: `static/js/loader.js` now skips ALL code on mobile (exits at line 25)
- Files: `base.html`, `main.css`, `combined.css`, `app.py`, `service-worker.js`

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

**Preventive suggestions (so scroll doesn’t break again):**
1. **New touch handlers:** Avoid `event.preventDefault()` on `touchstart`/`touchmove` unless the handler is scoped to a small control (e.g. a dial). Prefer `touch-action: pan-y` (or `manipulation`) in CSS so vertical scroll is allowed.
2. **New CSS:** Never set `touch-action: none` or `overflow: hidden` on `html` or `body`. Use `overflow: hidden` only on components (modals, cards, loader overlay).
3. **Loader / new “loading” scripts:** Any script that runs before first paint should detect mobile early and exit before registering fetch interceptors or global touch/scroll listeners. See `loader.js` (mobile check at top, then `return`).
4. **New full-screen overlays:** Use `pointer-events: none` when hidden so they don’t block touch. The scroll fix in `base.html` already tries to disable blocking overlays; keep that in mind when adding new modals.
5. **Before shipping mobile UX changes:** Manually test vertical scroll on a real device (or Chrome DevTools mobile) after load and after closing any overlay.

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

### 2026-01-28: Spotify-Style Persistent Mini Player
- **Change:** Replaced full-screen player with always-visible mini player
- **Features:** Empty state when no track, disabled buttons, dark glass aesthetic
- **Redirect:** `/player` route now redirects to content pages
- **Files:** `base.html`, `main.css`, `combined.css`, `app.py`

### 2026-01-28: Service Worker Cache Fix
- **Issue:** Users not seeing latest deployments
- **Fix:** Network-first for HTML, stale-while-revalidate for CSS/JS
- **Version:** Bumped to v9
- **Files:** `static/service-worker.js`

### 2026-01-28: Mobile Scroll Freeze Fix
- **Issue:** Screen froze after loading popup finished
- **Cause:** `loader.js` ran fetch interceptor before mobile check
- **Fix:** Mobile check at TOP of IIFE, exits immediately
- **Files:** `static/js/loader.js`, `static/css/loader.css`
- **Safe:** Loader is cosmetic only, no functionality impact

### 2026-01-28: Mobile subheader spacing + scroll-prevention notes
- **Change:** Added 12px top margin on mobile for subheaders so they are not flush with status bar
- **Targets:** `.podcasts-hero`, `.page-header`, `.music-subheader`, `.shows-subheader`, `.bookmarks-subheader`, `.artists-subheader`, `.mobile-search-header` (all @max-width 768px)
- **Docs:** CLAUDE.md "Preventive suggestions" for keeping mobile scroll working (touch handlers, CSS, loader pattern, overlays, manual test)
- **Files:** `static/css/combined.css`, `CLAUDE.md`, `templates/base.html` (css_version → v20260128m)
