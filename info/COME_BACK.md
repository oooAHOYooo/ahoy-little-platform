# Come back list – Android build & Play Store

Use this when you return to build the app again (sync, AAB, run, upload).

**All commands below are from the repo root:** `ahoy-little-platform/`

---

## 1. Sync web assets

Get the latest Vue SPA into the Android app:

```bash
npx cap sync android
```

Updates `android/app/src/main/assets/public` from `spa-dist`.  
If you changed the Vue app, build the SPA first: `cd spa && npm run build && cd ..`

---

## 2. Build signed release AAB (for Play Store)

```bash
cd android && ./gradlew bundleRelease
```

- **Output:** `android/app/build/outputs/bundle/release/app-release.aab`
- Signing is already configured via `android/keystore/sign.properties` (and `app/build.gradle`). No UI needed for signing.

---

## 3. Run on device or emulator

**Option A – Gradle (any connected device):**

```bash
cd android && ./gradlew installRelease
```

**Option B – Start emulator and run (Pixel 9 Pro):**

```bash
cd android && ./run-emulator.sh
```

Starts the emulator if needed, syncs, builds release APK, installs, launches.

**Option C – Emulator already running (quick test):**

```bash
cd android && ./quick-test.sh
```

---

## 4. Upload to Play Console (you do this in the browser)

1. Open [Play Console](https://play.google.com/console) → your app **Ahoy Indie Media**.
2. **Release** → **Testing** → **Internal testing** (or your chosen track).
3. **Create new release** → upload `android/app/build/outputs/bundle/release/app-release.aab`.
4. Add release notes if needed → **Review release** → **Start rollout**.

---

## 5. Optional: Open in Android Studio

```bash
npx cap open android
```

Use the IDE for: Run configurations, Device Manager / AVDs, Logcat, or changing signing. For routine sync + AAB + run, the terminal commands above are enough.

---

## Quick copy-paste (from repo root)

```bash
# Full flow: build SPA → sync → AAB
cd spa && npm run build && cd .. && npx cap sync android && cd android && ./gradlew bundleRelease
```

Then upload `android/app/build/outputs/bundle/release/app-release.aab` in Play Console.
