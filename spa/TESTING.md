# SPA v2 + Native Testing Guide

Quick smoke-tests and car setup for Ahoy Indie Media (SPA v2, Capacitor, Android Auto, CarPlay).

---

## 1. Auth (session cookies)

- **Login:** Open app → go to Login (or `/login`) → enter email + password → submit. Should see “Welcome back!” toast and land on home. Nav/UI can show logged-in state when you add it.
- **Signup:** Same screen, switch to Sign Up → email, password, optional username → submit. “Account created!” and redirect.
- **Session restore:** After login, close app and reopen (or refresh in browser). User should still be logged in (session restored via `GET /api/auth/me`).
- **Logout:** If you add a logout control, it should call `logout()` and clear user; next API call should not send the session cookie.

**Note:** In the native app, the WebView origin is `capacitor://localhost` and the API is `https://app.ahoy.ooo`, so it’s cross-origin. If login works in the browser but not in the built app:
1. Ensure the backend allows `capacitor://localhost` and `ionic://localhost` in CORS origins (`extensions.py`).
2. If the session cookie still isn’t sent, the server may need to set the session cookie with `SameSite=None; Secure` (e.g. `SESSION_COOKIE_SAMESITE=None` and `SESSION_COOKIE_SECURE=True` in production).

---

## 2. Background audio (iOS & Android)

1. Build and run the app on a **real device** (simulator/emulator may not reflect real background behavior).
2. Play any track (Music or Podcast).
3. **Lock the phone** (or send app to background).
4. **Expected:** Playback continues; lock screen shows Ahoy controls (play/pause, skip).
5. Use lock screen or control center to pause/play/skip and confirm it works.

**If it stops when backgrounded:**

- **iOS:** Check `Info.plist` has `UIBackgroundModes` → `audio`, and that `AppDelegate` sets up `AVAudioSession` for playback.
- **Android:** Check `AndroidManifest.xml` has `FOREGROUND_SERVICE` and `FOREGROUND_SERVICE_MEDIA_PLAYBACK`; the app uses a media-style flow (mini player / Media Session), not necessarily a foreground service for the SPA WebView. Background audio in the WebView is usually allowed when the page keeps the session; if not, consider keeping playback in a native layer (e.g. same as Android Auto service).

---

## 3. Android Auto

### Prerequisites

- Android Studio with **Android Auto Desktop Head Unit (DHU)** installed (SDK Manager → SDK Tools → “Android Auto Desktop Head Unit Emulator”).
- Physical Android device or emulator with the app installed.

### Option A: Desktop Head Unit (no car)

1. On device: **Settings → Developer options** (enable if needed).
2. Open **Android Auto** app → **Settings** → scroll to bottom → tap version number **10 times** to enable developer mode.
3. In Android Auto: **⋮** menu → **Start head unit server**.
4. Connect device to Mac via USB.
5. On Mac:
   ```bash
   adb forward tcp:5277 tcp:5277
   cd ~/Library/Android/sdk/extras/google/auto/
   ./desktop-head-unit
   ```
6. DHU window opens. In the media apps list, open **Ahoy Indie Media**.
7. **Expected:** Root shows **All Music**, **Artists**, **Podcasts**. Drill in → pick a track/episode → play. Play/pause/skip on DHU (and steering wheel if you later test in a car) should work.

### Option B: Real car

1. Build a **signed release** APK (or use debug for testing).
2. Install on your Android phone.
3. Connect phone to car via USB (Android Auto enabled).
4. **Ahoy Indie Media** should appear as a media source; browse and play as above.

### What you see in Android Auto

- **Ahoy Indie Media** (media app)
  - **All Music** → list of tracks → tap to play
  - **Artists** → list of artists → tap artist → list of tracks → tap to play
  - **Podcasts** → list of shows → tap show → list of episodes → tap to play  
- Play/pause/skip on head unit and steering wheel.

---

## 4. CarPlay (iOS)

### Prerequisites

- **CarPlay entitlement** from Apple (required for app to show in CarPlay, including simulator).
- Apply at: https://developer.apple.com/contact/carplay/  
  - App type: **Audio**  
  - Bundle ID: `com.ahoy.app`  
  - Approval can take **1–4 weeks**.

### While waiting for entitlement: Simulator

1. Open iOS project: `npx cap open ios`.
2. Select an **iPhone** simulator (e.g. iPhone 15), build and run.
3. In Simulator menu: **I/O → External Displays → CarPlay**.
4. CarPlay window opens. **If entitlement is not yet approved**, your app may not appear; the code is ready and will show once the entitlement is active.

### After entitlement is approved

1. Build and run on a **real iPhone** (or simulator with CarPlay).
2. Connect to CarPlay (simulator: I/O → External Displays → CarPlay; or real car with CarPlay).
3. **Expected:** **Ahoy Indie Media** appears as an audio app with:
   - **Music** tab → list of tracks → tap to play
   - **Artists** tab → artists → tap for tracks → tap to play
   - **Podcasts** tab → shows → tap for episodes → tap to play
4. Now Playing shows artwork, title, artist; play/pause/skip work.

---

## 5. Car readiness checklist

Use this to confirm both platforms are ready for car testing.

### Android Auto

- [ ] `android/app/src/main/AndroidManifest.xml`: `<service android:name=".AhoyMediaService" ... />` with `MediaBrowserService` intent-filter; `automotive_app_desc` meta-data.
- [ ] `android/app/src/main/res/xml/automotive_app_desc.xml`: `<uses name="media" />`.
- [ ] `AhoyMediaService.java`: implements browse tree (ROOT → Music / Artists / Podcasts) and playback; uses `https://app.ahoy.ooo` for `/api/music`, `/api/artists`, `/api/podcasts`.
- [ ] Permissions: `INTERNET`, `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_MEDIA_PLAYBACK`, `WAKE_LOCK`.

### CarPlay (iOS)

- [ ] `Info.plist`: `UIBackgroundModes` includes `audio`; `UIApplicationSceneManifest` includes `CPTemplateApplicationScene` with scene delegate `AhoyCarPlaySceneDelegate`.
- [ ] `App.entitlements`: `com.apple.developer.carplay-audio` = true (effective after Apple approves the entitlement).
- [ ] `AhoyCarPlaySceneDelegate.swift`: Tab bar (Music, Artists, Podcasts), fetches from `https://app.ahoy.ooo/api/*`, plays with AVPlayer, pushes Now Playing template.

### Backend

- [ ] `https://app.ahoy.ooo/api/music` returns `{ "tracks": [...] }`.
- [ ] `https://app.ahoy.ooo/api/artists` returns `{ "artists": [...] }`.
- [ ] `https://app.ahoy.ooo/api/podcasts` returns `{ "shows": [...] }` (each show can have `episodes[]` with `audio_url` or `url`).

---

## Build commands (recap)

```bash
# SPA
cd spa && npm run build

# Sync to native
npx cap sync

# Android (release AAB)
cd android && ./gradlew bundleRelease

# iOS (archive for TestFlight)
# Xcode: Product → Archive, or:
xcodebuild -workspace ios/App/App.xcworkspace -scheme App -archivePath build/App.xcarchive archive

# Open IDEs
npx cap open android
npx cap open ios
```
