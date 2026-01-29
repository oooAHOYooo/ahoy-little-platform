# CLAUDE.md

**This file is loaded as workspace context.** When the user starts a session, read the "Quick Reference" and "User's current focus" below first so you know where we left off.

---

## Quick Reference (Read First)

**Current Issues:** None active

**User's current focus (pick up from here):**
- **Music player and toggle play/pause** — User asked to get music playing reliably and to fix toggle play/pause. We did: (1) fix Illegal invocation (safe `getBoundingClientRect.call(el)` in base.html seek/scrub), (2) suppress AbortError on resume and use bound `element.play.bind(element)` everywhere in `player.js`, (3) make all toggle play/pause use `window.mediaPlayer.isPlaying` and `window.mediaPlayer.currentTrack` as single source of truth (base.html mini player, music.html, player.js playerData, player.html). (4) `pause()` now sets `isPlaying = false` immediately. (5) Token-light prompt for new sessions added at `.claude/PROMPT_LIGHT.md`. When the user asks for "anything else" or "check again," assume they want to continue from this player/music work unless they say otherwise.

**Recent Changes (2026-01-29):**
- Music playback: instant play after `load()`, bound `play()`, AbortError suppressed, loading state cleared
- Toggle play/pause: all UIs use `mediaPlayer.isPlaying` / `mediaPlayer.currentTrack`; `pause()` sets `isPlaying = false` up front
- Illegal invocation fix: `getBoundingClientRect.call(element)` in base.html seekTo/scrubMove
- Token-light prompt: `.claude/PROMPT_LIGHT.md` for copy-paste into new Claude sessions
- Cache: `css_version` → v20260129i in `templates/base.html` (~line 144)

**Previous (2026-01-28):**
- Spotify-style persistent mini player, service worker v9, mobile scroll freeze fix

**Key Paths:**
- App entry: `app.py` (Flask factory `create_app()`)
- Routes: `blueprints/`, `routes/`
- Frontend: `static/js/`, `static/css/`, `templates/`
- Data: `static/data/*.json`
- Mobile scroll fixes: `templates/base.html:500-585`, `static/js/loader.js`

**Cache Busting:** Increment `css_version` in `templates/base.html` (~line 141) when changing CSS/JS

**Cache strategy (always fresh):**
- **HTML:** `no-cache, no-store` via `utils/security_headers.py` and meta tags in `base.html`. Never cached by service worker.
- **On every load:** First script in body unregisters all service workers and clears all Cache API caches.
- **Service worker:** Registration is disabled. If an old SW is still active, it never caches HTML (fetch with `cache: 'no-store'`).
- **Static CSS/JS:** Long cache + versioned URLs (`?v=css_version`); bump version on deploy for fresh assets.
- **Escape hatch:** `/refresh` clears SW + caches and redirects to `/`.

**Mobile app shows old version (not what `python app.py` serves):**
- The **native app (Capacitor)** loads from the **deployed** URL (`capacitor.config.ts` → `server.url`: e.g. `https://ahoy-indie-media.onrender.com` or whatever `app.ahoy.ooo` points to). It does **not** load from your local `python app.py`. So mobile will always show whatever is deployed at that URL.
- **Fix:** (1) **Deploy** your latest code to the host that serves `app.ahoy.ooo` (e.g. Render). (2) **Force fresh content on the device:** In the app, go to **app.ahoy.ooo/refresh** (use in-app browser/URL if available, or open that URL in the phone’s browser and log in again), or **Settings → Apps → Ahoy Indie Media → Storage → Clear cache** (or Clear data), then reopen the app. After deploy, `/refresh` or clearing cache ensures the WebView gets new HTML instead of cached old UI.

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

**If mobile won't scroll or update:** HTML is now no-cache so users get latest. Stuck users can open `/refresh` (or tap the red sync icon in the status bar) to clear SW + caches and reload.

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

### 2026-01-29: Toggle play/pause + session context
- **User requests:** Make sure music plays, toggle play/pause works, "check again," then a token-light request for Claude and update CLAUDE.md so when they log in Claude "automatically goes" (picks up context).
- **Toggle:** All toggle logic (base mini player, music.html, player.js playerData, player.html) now uses `window.mediaPlayer.isPlaying` and `window.mediaPlayer.currentTrack` as source of truth so play/pause and icons stay in sync. `pause()` sets `this.isPlaying = false` before calling element.pause().
- **Session context:** CLAUDE.md now has "User's current focus" at the top so new sessions know we've been on player/music work; added `.claude/PROMPT_LIGHT.md` for token-light copy-paste into new sessions.
- **Files:** `templates/base.html`, `templates/music.html`, `templates/player.html`, `static/js/player.js`, `CLAUDE.md`, `.claude/PROMPT_LIGHT.md`

### 2026-01-29: Instant Audio Playback + Mobile Mini Player
- **Issue:** Audio didn't play immediately when clicking tracks/podcasts
- **Cause:** `player.js` waited for `canplay` event before calling `play()`
- **Fix:** Call `load()` then `play()` immediately; browser streams as data arrives
- **Also:** Added `_playAborted` flag for rapid track switching; fixed loading state clearing
- **Mobile:** Mini player shows prev/play/next/boost/bookmark/share/queue (hides shuffle, repeat)
- **Mobile CSS:** Compact buttons (32px→28px on small phones), boost hidden under 480px
- **Cache:** Added version param to `player.js` and `loader.js` script tags
- **Files:** `static/js/player.js`, `static/css/main.css`, `templates/base.html` (css_version → v20260129g)

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
