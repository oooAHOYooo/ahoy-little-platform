# Syncing with Android Studio and Xcode

You can open the native projects in Android Studio and Xcode, build from there, and keep them in sync with your web app.

---

## 1. Sync first (from repo root)

Before opening in an IDE, sync so the native projects have the latest web assets and Capacitor config:

```bash
# Sync both platforms
npx cap sync

# Or sync one at a time
npx cap sync android
npx cap sync ios
```

This copies:
- `static/` → into the native app’s assets (so the WebView loads your HTML/JS/CSS)
- `capacitor.config.ts` → into the native project as `capacitor.config.json`

---

## 2. Open in the IDEs

From the **repo root**:

```bash
# Android Studio
npx cap open android

# Xcode (macOS only)
npx cap open ios
```

- **Android Studio** opens the `android/` project. You can run the app (device or emulator), build AAB/APK, or edit native code.
- **Xcode** opens the `ios/App/App.xcworkspace` (use the **.xcworkspace**, not the .xcodeproj, if you have CocoaPods). You can run on simulator/device, Archive for App Store, or edit native code.

---

## 3. When to sync again

Run `npx cap sync` (or `npx cap sync android` / `npx cap sync ios`) after you:

- Change **`capacitor.config.ts`** (e.g. `server.url`, `appId`, plugins)
- Add or update **Capacitor plugins** (`npm install @capacitor/…`)
- Change **web assets** that the app loads from `static/` (if you’re bundling local assets; with a remote `server.url` the app loads from the URL, so sync is mainly for config and plugins)

Then in the IDE you can run or build as usual; no need to close and reopen.

---

## 4. Build from the IDE

| Platform | IDE | Build / Run |
|----------|-----|-------------|
| **Android** | Android Studio | **Run** (green play) for device/emulator. **Build → Generate Signed Bundle / APK** for release AAB/APK. |
| **iOS** | Xcode | **Run** (play) for simulator/device. **Product → Archive** for App Store distribution. |

Your app loads the URL set in `capacitor.config.ts` (`server.url`). The Android and iOS projects are just the native shell; the content comes from that URL (or from synced assets if you switch to a bundled setup).

---

## 5. Quick reference

| Goal | Command (repo root) |
|------|---------------------|
| Sync both platforms | `npx cap sync` |
| Sync Android only | `npx cap sync android` |
| Sync iOS only | `npx cap sync ios` |
| Open Android Studio | `npx cap open android` |
| Open Xcode | `npx cap open ios` |

So yes: you can sync and work via Android Studio and Xcode; run `npx cap sync` (or per-platform) first, then `npx cap open android` or `npx cap open ios`.
