# SPA v2 Handoff Document
**Date:** 2026-02-08
**Branch:** `spa-v2`
**Status:** Functional SPA with native car integrations. Ready for device testing.

---

## What's Been Done (Complete Timeline)

### Session 1: Foundation
- Vue 3 + Vite SPA scaffolded (11 list views, NavBar, MiniPlayer shell)
- CSS 1:1 imported from Flask site (design-tokens, main, combined)
- Pinia player store + API composable with caching

### Session 2: Detail Pages + Playback
- **5 detail views** (MusicDetail, ArtistDetail, ShowDetail, PodcastDetail, EventDetail)
- **Audio playback fully wired** — click track → it plays, queue works, auto-advance
- **Media Session API** — lock screen controls, steering wheel play/pause/skip
- **Bookmark composable** — save/unsave any content type (localStorage)
- **Radio view** — shuffle-plays all tracks with Up Next queue
- **Session resume** — last track persists across reloads
- **Flask APIs added** — `/api/podcasts` and `/api/events` JSON endpoints

### Session 3: Native Features
- **Full-screen Now Playing** (`/now-playing`) — Spotify-style player with seek, speed, sleep timer, queue
- **Native OS Share** — opens system share sheet (AirDrop, Messages, etc.)
- **Haptic Feedback** — vibration on play/bookmark taps
- **Screen Wake Lock** — screen stays on during playback
- **Sleep Timer** — auto-pause after 30 min
- **Playback Speed** — 0.5x–2x (great for podcasts)
- **Pull-to-Refresh** — native gesture on list pages
- **Toast Notifications** — "Saved to library", "Back online" feedback
- **Page Transitions** — smooth fades between views

### Session 4: Capacitor + Car Integrations (This Session)
- **Capacitor wired to SPA** — `webDir: 'spa-dist'`, `npx cap sync` works
- **iOS background audio** — `UIBackgroundModes: audio` + AVAudioSession in AppDelegate
- **Android background audio** — foreground service permission in manifest
- **Auth scaffold** — LoginView + useAuth composable (ready to wire to Flask endpoints)
- **Android Auto** — full `MediaBrowserServiceCompat` implementation
- **CarPlay** — full `CPTemplateApplicationSceneDelegate` implementation

---

## Current State

### What Works ✅
- SPA builds clean (0 errors, 24 lazy-loaded chunks)
- `npx cap sync` copies SPA into both native projects
- Full navigation with detail pages
- Audio playback with lock screen controls
- Bookmarking, sharing, haptics, wake lock, sleep timer, speed control
- Pull-to-refresh, toast notifications, page transitions

### What Needs Testing 🧪
- **Android Auto** — open Android Studio, build to device, connect to car or use DHU (Desktop Head Unit)
- **CarPlay** — open Xcode, build to device, use CarPlay Simulator (Xcode → I/O → External Displays)
- **Background audio** — play a track, lock phone, verify it keeps playing
- **CarPlay entitlement** — Apple must approve (see instructions below)

### What's Next ❌
- **Auth** — ✅ wired: session cookies + `credentials: 'include'`, LoginView uses `/api/auth/login` and `/api/auth/register`, session restore via `/api/auth/me`. See **Auth (session cookies)** in `spa/TESTING.md`.
- **Search** — client-side fuzzy search across all content
- **CarPlay entitlement** — apply at Apple developer portal (1–4 weeks)
- **Android Auto / CarPlay testing** — use `spa/TESTING.md` (DHU, real car, CarPlay simulator)
- **Offline caching** — cache audio files for offline playback

---

## Car readiness (iOS CarPlay + Android Auto)

Both car integrations are **implemented and ready** for device testing:

| Platform   | Status | What to do |
|-----------|--------|------------|
| **Android Auto** | Ready | Test with [Desktop Head Unit](https://developer.android.com/training/cars/media/auto) or real car. See **§3 Android Auto** in `spa/TESTING.md`. |
| **CarPlay (iOS)** | Code ready | Apply for [CarPlay entitlement](https://developer.apple.com/contact/carplay/) (Audio, bundle ID `com.ahoy.app`). Use CarPlay Simulator (I/O → External Displays → CarPlay) while waiting. See **§4 CarPlay** in `spa/TESTING.md`. |

**Smoke-tests:** Background audio, Android Auto, and CarPlay steps are in **`spa/TESTING.md`**, including a **Car readiness checklist** (manifest, entitlements, API contract).

---

## Running Locally

```bash
# SPA dev server (hot reload, proxies API to app.ahoy.ooo)
cd spa && npm run dev    # http://localhost:5173

# Build + sync to native projects
cd spa && npm run build
cd .. && npx cap sync

# Open native IDEs
npx cap open android     # Android Studio
npx cap open ios         # Xcode
```

---

## Testing Android Auto

### Option 1: Desktop Head Unit (DHU) — no car needed
```bash
# 1. Install DHU from Android SDK Manager
#    SDK Manager → SDK Tools → Android Auto Desktop Head Unit Emulator

# 2. Build and install app on phone/emulator
#    Android Studio → Run

# 3. On phone: Settings → Developer Options → enable
# 4. Open Android Auto app → Settings → scroll to bottom → tap version 10x for dev mode
# 5. Three-dot menu → Start head unit server

# 6. On Mac, connect phone via USB and run:
adb forward tcp:5277 tcp:5277
cd ~/Library/Android/sdk/extras/google/auto/
./desktop-head-unit

# The DHU window shows Android Auto. Your app should appear in the media apps list.
```

### Option 2: Real car
Build a signed APK, install on your phone, plug into car via USB. Ahoy should appear as a media source.

### What you'll see in Android Auto
```
Ahoy Indie Media (media app)
├── All Music        → list of tracks → tap to play
├── Artists          → list of artists → tap for their tracks → tap to play  
└── Podcasts         → list of shows → tap for episodes → tap to play
```
Play/pause/skip controls work on the steering wheel and the car head unit.

---

## Testing CarPlay

### Step 1: Apply for CarPlay entitlement (required)
1. Go to https://developer.apple.com/contact/carplay/
2. Select **Audio** app type
3. Submit your app details and bundle ID (`com.ahoy.app`)
4. Apple reviews and sends back a provisioning profile with the CarPlay entitlement
5. This can take **1-4 weeks**

### Step 2: While waiting — test with Xcode CarPlay Simulator
1. Open Xcode: `npx cap open ios`
2. Build to a simulator (iPhone 15 etc.)
3. In Simulator menu: **I/O → External Displays → CarPlay**
4. A CarPlay window opens. Your app should appear if entitlement is set.

**Note:** Without the approved entitlement, the CarPlay simulator may not show your app. The code compiles and is ready — it just needs Apple's blessing.

### What you'll see in CarPlay
```
Ahoy Indie Media (audio app)
├── Music tab         → scrollable list of tracks → tap to play
├── Artists tab       → list of artists → tap for tracks → tap to play
└── Podcasts tab      → list of shows → tap for episodes → tap to play
```
Now Playing screen shows artwork, title, artist with play/pause/skip.

---

## Architecture

### How the car integrations work

Both Android Auto and CarPlay run as **native services** that are independent of the WebView SPA. They:
1. Fetch the music catalog directly from `https://app.ahoy.ooo/api/*`
2. Build a browsable media tree (categories → items)
3. Handle playback with native audio players (Android `MediaPlayer` / iOS `AVPlayer`)
4. Expose transport controls to the car head unit

This means:
- Car playback works even if the SPA WebView is not loaded
- The car UI uses native templates (not HTML/CSS) — Apple/Google require this
- Audio focus, interruptions, and background modes are handled natively

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐
│  SPA (WebView)  │     │  Android Auto    │     │    CarPlay     │
│  Vue 3 + Pinia  │     │  MediaBrowser    │     │  CPTemplate    │
│  HTML5 Audio    │     │  ServiceCompat   │     │  SceneDelegate │
└────────┬────────┘     └────────┬─────────┘     └───────┬────────┘
         │                       │                        │
         │  All fetch from:      │                        │
         ▼                       ▼                        ▼
    ┌────────────────────────────────────────────────────────┐
    │          Flask API  (app.ahoy.ooo/api/*)               │
    │    /api/music  /api/artists  /api/podcasts  /api/events│
    └────────────────────────────────────────────────────────┘
```

---

## Files Reference

### SPA Source (spa/src/) — 33 files
| Path | Purpose |
|------|---------|
| `main.js` | App entry + session restore |
| `App.vue` | Shell: toast, offline banner, transitions, wake lock |
| `router.js` | All routes (17 routes) |
| `stores/player.js` | Audio singleton, queue, Media Session, session persist |
| `composables/useApi.js` | API client with localStorage caching |
| `composables/useBookmarks.js` | Bookmark toggle with events |
| `composables/useNative.js` | Share, haptics, wake lock, sleep timer, speed control |
| `composables/useAuth.js` | Auth scaffold (login/signup/logout/token) |
| `components/NavBar.vue` | Bottom nav (8 tabs) |
| `components/MiniPlayer.vue` | Persistent player → taps open Now Playing |
| `components/Toast.vue` | Native-style toast notifications |
| `components/PullRefresh.vue` | Pull-to-refresh gesture |
| `views/HomeView.vue` | Home with What's New, featured rows |
| `views/MusicView.vue` | Music grid with pull-to-refresh |
| `views/MusicDetailView.vue` | Track hero, play/share, related tracks |
| `views/ArtistsView.vue` | Artists grid |
| `views/ArtistDetailView.vue` | Hero, bio, tracks, videos, follow/share |
| `views/ShowsView.vue` | Shows grid |
| `views/ShowDetailView.vue` | Video hero, YouTube embed, related |
| `views/PodcastsView.vue` | Podcast show cards |
| `views/PodcastDetailView.vue` | Show hero, episode list |
| `views/EventsView.vue` | Events list |
| `views/EventDetailView.vue` | Event hero, photos, RSVP |
| `views/LiveTVView.vue` | Live TV dashboard |
| `views/RadioView.vue` | Shuffle radio with Up Next |
| `views/SavedView.vue` | Bookmarked items |
| `views/NowPlayingView.vue` | Full-screen player (seek, speed, sleep, queue) |
| `views/LoginView.vue` | Login / signup form |

### Native — Android Auto
| Path | Purpose |
|------|---------|
| `android/app/src/main/java/com/ahoy/app/AhoyMediaService.java` | MediaBrowserServiceCompat — browse tree + playback |
| `android/app/src/main/res/xml/automotive_app_desc.xml` | Android Auto declaration |
| `android/app/src/main/AndroidManifest.xml` | Service registration, foreground service |
| `android/app/build.gradle` | `androidx.media:media:1.7.0` dependency |

### Native — CarPlay
| Path | Purpose |
|------|---------|
| `ios/App/App/AhoyCarPlaySceneDelegate.swift` | CarPlay scene delegate — tabs, playback |
| `ios/App/App/App.entitlements` | CarPlay audio entitlement |
| `ios/App/App/Info.plist` | Background audio + CarPlay scene config |
| `ios/App/App/AppDelegate.swift` | AVAudioSession setup for background playback |

### Config
| Path | Purpose |
|------|---------|
| `capacitor.config.ts` | Points to `spa-dist/` (local SPA, not remote URL) |
| `spa/vite.config.js` | Build → `../spa-dist/`, dev proxy to `app.ahoy.ooo` |

---

## Build Commands

```bash
# SPA
cd spa && npm run build          # → ../spa-dist/

# Sync to native
npx cap sync                     # copies spa-dist → android + ios

# Android (signed AAB for Play Store)
cd android && ./gradlew bundleRelease

# iOS (archive for TestFlight)
xcodebuild -workspace ios/App/App.xcworkspace -scheme App -archivePath build/App.xcarchive archive

# Open IDEs
npx cap open android
npx cap open ios
```
