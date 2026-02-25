# CLAUDE.md

**This file is loaded as workspace context.** When the user starts a session, read the "Quick Reference" and "User's current focus" below first so you know where we left off.

**For Claude Code / heavy coding sessions:** Read this file first to understand the repo and avoid re-explaining architecture. High-impact, copy-paste prompts that assume CLAUDE.md context are in `.claude/PROMPTS_CLAUDE_CODE.md`.

---

## Quick Reference (Read First)

**Current Issues:**
- Waiting: Google Search Console DNS verification for `littlemarket.org` (added TXT record, awaiting propagation)

**User's current focus (pick up from here):**
- **Android release pipeline** — Set up automated CI/CD with GitHub Actions. Builds on every push; releases only on manual trigger or git tags. Waiting for DNS verification to complete service account setup.

**Recent Changes (2026-02-25):**
- **Android release pipeline:** Set up GitHub Actions CI/CD with two-stage workflow (build + deploy)
- **Automated builds:** Every push builds SPA + signed AAB/APK, artifacts kept 30 days
- **Controlled releases:** Deploy only via manual trigger or git tags (fail-safe, no auto-uploads)
- **Service account automation:** Created `scripts/setup-play-console-ci.sh` to automate GCP setup
- **Release methods:** Manual (UI), git tags (v1.0.1), optional scheduled (weekly)
- **Documentation:** Added `info/RELEASE_PIPELINE.md` with full setup and release instructions
- **Files:** `.github/workflows/android-release.yml`, `scripts/setup-play-console-ci.sh`, `info/RELEASE_PIPELINE.md`
- **Status:** Signed keystore working, builds succeeding, waiting for DNS verification to complete service account setup
- **Emulator testing:** Android emulator (Pixel 7 Pro, Android 35) running on Linux with signed builds tested

**Previous (2026-02-15):**
- **Mobile collapse feature:** Added collapsible functionality to mobile dock and now-playing bar
- **Swipe gestures:** Swipe down/up or tap handle bar to collapse/expand both components
- **Persistent state:** Collapse preferences saved to localStorage (survives page reloads)
- **Smooth animations:** 300ms cubic-bezier transitions with adaptive body padding
- **Files:** Created `spa/src/composables/useMobileCollapse.js`, updated `MiniPlayer.vue`, `NavBar.vue`, `App.vue`, and CSS files

**Previous (2026-02-02):**
- Android: Gradle upgraded 8.0.2→8.11.1, AGP 8.0.0→8.7.3 (Java 21 compat)
- Android: Signing config wired into `build.gradle` via `keystore/sign.properties`
- Android: Signed AAB + APK built and ready for Play Store upload
- iOS: Archive built (`ios/App/build/App.xcarchive`), needs team signing in Xcode

**Previous (2026-01-29):**
- Music playback, toggle play/pause, instant audio, mobile mini player

**Previous (2026-01-28):**
- Spotify-style persistent mini player, service worker v9, mobile scroll freeze fix

**Key Paths:**
- App entry: `app.py` (Flask factory `create_app()`)
- Routes: `blueprints/`, `routes/`
- Frontend: `static/js/`, `static/css/`, `templates/`
- Data: `static/data/*.json`
- Mobile scroll fixes: `templates/base.html:500-585`, `static/js/loader.js`

**Cache Busting:** Increment `css_version` in `templates/base.html` (~line 141) when changing CSS/JS

**Web UI: SPA is the main app.** The **Vue SPA** (`spa/` → `spa-dist/`) is the primary web UI. When you run `npm start`, Flask builds the SPA and then serves it for `/`, `/music`, `/podcasts`, etc. **Edit the SPA** (`spa/src/`) for UI changes (e.g. `MiniPlayer.vue`, `NowPlayingView.vue`, views, components). The **Flask templates** (`templates/`, e.g. `base.html`, `music.html`) are legacy server-rendered pages; they are only used for routes in `_server_path_prefixes` (e.g. API, static, auth) or when `spa-dist` is missing.

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
python help.py                   # Dev helper: status + help (start, status, todos)
python help.py start             # Start dev server (runs dev.py)
python help.py status            # Check server, git, env
python help.py todos             # List TODOS.md
python help.py todos add "task"  # Add todo (auto-updates TODOS.md)
python help.py todos done 1      # Mark item 1 done
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
**Sync with Android Studio / Xcode:** Run `npx cap sync` (or `npx cap sync android` / `npx cap sync ios`), then `npx cap open android` or `npx cap open ios`. See `packaging/IDE_SYNC.md`.

**Android signed build (terminal):**
```bash
npx cap sync android
cd android && ./gradlew bundleRelease assembleRelease   # builds signed AAB + APK
```
- Signing config: `android/app/build.gradle` reads from `android/keystore/sign.properties`
- Keystore: `android/keystore/ahoy-release.jks` (password: `26trustdaL0RD`, alias: `ahoy`)
- **AAB** (Play Store): `android/app/build/outputs/bundle/release/app-release.aab`
- **APK** (direct install): `android/app/build/outputs/apk/release/app-release-unsigned.apk`
- Upload AAB to Google Play Console → Testing → Internal testing
- Keystore is gitignored — back it up somewhere safe; same keystore required for all future uploads
- Gradle 8.11.1 + AGP 8.7.3 (requires Java 21)

**iOS build (TestFlight):**
```bash
./packaging/build-ios.sh          # archive → opens Xcode Organizer for manual upload
./packaging/build-ios.sh upload   # archive + auto-upload to App Store Connect
```
- Requires Apple Developer Program ($99/yr) enrollment
- Bundle ID `com.ahoy.app` must be registered in Apple Developer portal
- Xcode must have your Apple ID signed in (Xcode → Settings → Accounts)
- ExportOptions: `ios/App/ExportOptions.plist` (team ID `Y8654K535L`, automatic signing)
- In Xcode Organizer: Distribute App → TestFlight & App Store → select team → Upload
- App icon: `ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png` (needs real 1024x1024)

## Env Vars (Required in Production)
`SECRET_KEY`, `DATABASE_URL`, `STRIPE_SECRET_KEY`, `RESEND_API_KEY`, `AHOY_ADMIN_EMAIL`

---

## Session Log

### 2026-02-25: Android Release Pipeline & CI/CD Automation
- **Goal:** Set up automated, controlled release pipeline for Google Play Store
- **Achievements:**
  - ✅ Installed Java 21, Android SDK, emulator (Pixel 7 Pro, Android 35)
  - ✅ Created signing keystore (`android/keystore/ahoy-release.jks`)
  - ✅ Built and tested signed AAB + APK on emulator
  - ✅ Created GitHub Actions workflow with two-stage deployment
  - ✅ Implemented fail-safes: builds on every push, deploys only on manual trigger or git tags
  - ✅ Automated service account setup script
  - ✅ Created comprehensive release pipeline documentation
  - ⏳ Waiting: Google Search Console DNS verification for `littlemarket.org`
- **Workflow Design:**
  - **Build stage:** Every push → builds SPA, syncs to Android, builds signed AAB/APK, artifacts saved 30 days
  - **Deploy stage:** Manual/tag-based only → uploads to Play Console (internal testing, draft status)
  - **Release methods:** (1) Manual via GitHub UI, (2) Git tags (v1.0.1), (3) Optional scheduled
- **Files Created:**
  - `android/keystore/ahoy-release.jks` (signing key)
  - `android/keystore/sign.properties` (Gradle signing config)
  - `android/local.properties` (Android SDK path)
  - `.github/workflows/android-release.yml` (CI/CD workflow)
  - `scripts/setup-play-console-ci.sh` (service account automation)
  - `info/RELEASE_PIPELINE.md` (user guide)
- **Next Steps:**
  1. DNS verification completes (~15 min wait)
  2. Run `bash scripts/setup-play-console-ci.sh` to create service account
  3. Add Play Console permissions to service account
  4. Test manual release from GitHub Actions
  5. Review in Play Console → Internal testing

### 2026-02-15: Mobile Collapse Feature
- **Request:** Make mobile dock and now-playing bar collapsible for cleaner UX
- **Implementation:**
  - Created `spa/src/composables/useMobileCollapse.js` - shared state management with localStorage persistence
  - Updated `MiniPlayer.vue` - added collapse handle bar with swipe/tap gestures
  - Updated `NavBar.vue` - added collapse handle bar with swipe/tap gestures
  - Updated `App.vue` - added body class watchers to adjust padding when collapsed
  - Updated `spa/src/assets/main.css` - added collapse animations and responsive padding
  - Updated `static/css/combined.css` - added legacy support for Flask templates
- **Features:**
  - Swipe down/up (>50px in <300ms) or tap handle to collapse/expand
  - Independent collapse state for dock and player
  - Smooth 300ms cubic-bezier animations
  - Persistent state in localStorage (`ahoy.ui.playerCollapsed`, `ahoy.ui.dockCollapsed`)
  - Adaptive body padding based on collapsed state
  - Desktop-hidden (handles only visible <769px)
- **Docs:** Created `.claude/MOBILE_COLLAPSE_FEATURE.md` with full implementation details and testing checklist
- **Build:** SPA builds successfully with no errors (140 modules, 4.39s)

### 2026-02-02: Android & iOS beta build setup
- **Goal:** Set up native builds for Play Store internal testing and TestFlight
- **Android:** Upgraded Gradle 8.0.2→8.11.1 and AGP 8.0.0→8.7.3 for Java 21 compatibility. Created release keystore (`android/keystore/ahoy-release.jks`, password `26trustdaL0RD`, alias `ahoy`). Wired signing config into `build.gradle` via `keystore/sign.properties`. Built signed AAB + APK from terminal.
- **iOS:** Built archive from terminal with `xcodebuild` (unsigned). Opens in Xcode Organizer for team signing. User needs Apple Developer team account to sign and upload to TestFlight.
- **Gradle fix:** Android Studio showed "incompatible Java 21 and Gradle 8.0.2" — upgraded wrapper + AGP from terminal.
- **Gitignore:** Uncommented `*.jks`, `*.keystore`, added `keystore/` to `android/.gitignore`
- **Files:** `android/gradle/wrapper/gradle-wrapper.properties`, `android/build.gradle`, `android/app/build.gradle`, `android/keystore/ahoy-release.jks`, `android/keystore/sign.properties`, `android/.gitignore`, `ios/App/build/App.xcarchive`

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
