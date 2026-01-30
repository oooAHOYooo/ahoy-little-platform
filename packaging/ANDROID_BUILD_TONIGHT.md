# Android build tonight – runbook

Use this to get an Android build (AAB for Play Store, or APK to install on a device) in one session.

---

## 1. Prerequisites (do once)

| Need | How to check / install |
|------|-------------------------|
| **Node 18+** | `node -v` → should be 18.x or 20.x. Install from [nodejs.org](https://nodejs.org) if needed. |
| **npm deps** | From repo root: `npm install` (installs Capacitor). |
| **JDK 17** | **Required.** `java -version` → must show 17 (Android Gradle plugin does not work with Java 16). Install: macOS `brew install openjdk@17`, or [Adoptium](https://adoptium.net). Then set `export JAVA_HOME=$(/usr/libexec/java_home -v 17)` (macOS) so Gradle uses it. |
| **Android SDK** | Easiest: install [Android Studio](https://developer.android.com/studio). It installs SDK and sets things up. Then run it once and complete setup. **Or** install [command-line tools only](https://developer.android.com/studio#command-tools) and set `ANDROID_HOME`. |

**Set ANDROID_HOME (if not set):**

- **macOS (Android Studio):**  
  `export ANDROID_HOME=$HOME/Library/Android/sdk`  
  Add to `~/.zshrc` so it persists.
- **Linux:**  
  `export ANDROID_HOME=$HOME/Android/Sdk` (or where you installed SDK).

**Path:**  
`export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin`  
(Adjust if your SDK layout is different; Android Studio’s SDK Manager shows the path.)

---

## 2. Build AAB (for Play Store or CI-style build)

From the **repo root**:

```bash
./packaging/android-build.sh
```

If the script is not executable:

```bash
chmod +x packaging/android-build.sh
./packaging/android-build.sh
```

**Success:** You should see:

- `android/app/build/outputs/bundle/release/app-release.aab`

That’s your **unsigned** AAB. You can upload it to Play Console (Google can sign it if you use Play App Signing), or sign it yourself (see [ANDROID_PLAY_STORE_GUIDE.md](./ANDROID_PLAY_STORE_GUIDE.md)).

---

## 3. Build APK (to install on your phone tonight)

AAB is for Play Store. To **install on a device** (e.g. USB or sideload), build an APK:

```bash
npx cap sync android
cd android
./gradlew assembleRelease
cd ..
```

**Output:**  
`android/app/build/outputs/apk/release/app-release-unsigned.apk`

Install:

- **USB:** Enable Developer options and USB debugging on the phone, then:  
  `adb install -r android/app/build/outputs/apk/release/app-release-unsigned.apk`
- Or copy the APK to the phone and open it (you may need to allow “Install from unknown sources” for that app/source).

Note: Unsigned APK is fine for local testing. For Play Store you use the AAB from step 2.

---

## 4. What the app loads

The app is a **Capacitor WebView** that loads your **live site** (see `capacitor.config.ts`):

- **server.url:** `https://ahoy-indie-media.onrender.com`

So the Android build does **not** bundle your local Flask app. It only wraps the deployed URL. To test “tonight”:

1. Your latest frontend/backend should be **deployed** to that URL (e.g. Render), **or**
2. You can temporarily point `server.url` in `capacitor.config.ts` to a tunnel (e.g. `ngrok` / `lt`) to your local `python app.py` and run `npx cap sync android` again, then rebuild.

---

## 5. Build via GitHub Actions (no local Android SDK)

If you don’t want to install Android SDK locally:

1. Push your branch.
2. Go to **Actions** → **Build Android AAB** → **Run workflow** (or push a tag `v*` to trigger it).
3. When the run finishes, download the artifact **AhoyIndieMedia-Android** (unsigned AAB if you didn’t set signing secrets).

You can then upload that AAB to Play Console or use it for testing. To get a **signed** AAB from CI, add the keystore secrets (see [ANDROID_PLAY_STORE_GUIDE.md](./ANDROID_PLAY_STORE_GUIDE.md) and the workflow’s `if: secrets.ANDROID_KEYSTORE_BASE64 != ''`).

---

## 6. Common failures

| Error | What to do |
|-------|------------|
| **SDK not found / ANDROID_HOME** | Install Android Studio (or CLI tools), set `ANDROID_HOME`, and ensure `platform-tools` and `build-tools` are installed (SDK Manager). |
| **Android Gradle plugin requires Java 17** / **Unsupported class file major version** | You must use JDK 17. Run `java -version`. On macOS: `export JAVA_HOME=$(/usr/libexec/java_home -v 17)` then re-run the build. Install JDK 17 with `brew install openjdk@17` if needed. |
| **Permission denied: ./gradlew** | `chmod +x android/gradlew`. |
| **Capacitor / node errors** | From repo root: `rm -rf node_modules package-lock.json && npm install`, then `npx cap sync android` again. |
| **Build fails in Gradle** | Run from repo root: `cd android && ./gradlew clean && ./gradlew bundleRelease` and read the last 30–40 lines of the error. Often it’s SDK version or a missing dependency; paste the error if you need help. |

---

## 7. Quick reference

| Goal | Command (from repo root) |
|------|--------------------------|
| AAB (Play Store) | `./packaging/android-build.sh` |
| APK (install on device) | `npx cap sync android && cd android && ./gradlew assembleRelease` |
| Open Android project in Android Studio | `npx cap open android` |
| Sync after changing config | `npx cap sync android` |
| **Sync and open in Android Studio / Xcode** | See [IDE_SYNC.md](./IDE_SYNC.md) |

After a successful build, use [ANDROID_PLAY_STORE_GUIDE.md](./ANDROID_PLAY_STORE_GUIDE.md) for signing and Play Console upload.
