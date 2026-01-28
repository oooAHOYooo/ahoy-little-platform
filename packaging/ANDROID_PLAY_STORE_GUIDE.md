# Android / Play Store Guide

What you need to build and submit the Ahoy Indie Media Android app (Capacitor) to Google Play.

## Prerequisites

1. **JDK 17** (or the version your project uses) – required for Gradle.
2. **Android SDK** – either via [Android Studio](https://developer.android.com/studio) or command-line tools.  
   - If the build already succeeded on your machine, you’re set.
3. **Google Play Developer account** – [register](https://play.google.com/console/signup) (one-time fee, ~$25).

## Build the release AAB

From the project root:

```bash
./packaging/android-build.sh
```

Or manually:

```bash
npx cap sync android
cd android && ./gradlew bundleRelease
```

Output: `android/app/build/outputs/bundle/release/app-release.aab` (unsigned).

## Signing for Play Store

Google Play requires a signed app. You have two approaches.

### Option 1: Play App Signing (recommended)

Google holds the **app signing key** and you use an **upload key** to upload builds.

1. **Create an upload keystore** (once, keep it safe):

   ```bash
   keytool -genkey -v -keystore ahoy-upload-key.keystore -alias ahoy-upload -keyalg RSA -keysize 2048 -validity 10000
   ```

   Store the keystore file and passwords somewhere safe (e.g. password manager). You’ll need them for every release.

2. **Sign the AAB** with your upload key:

   ```bash
   jarsigner -keystore ahoy-upload-key.keystore \
     android/app/build/outputs/bundle/release/app-release.aab \
     ahoy-upload
   ```

   (Use the alias you set with `-alias` when creating the keystore.)

3. **Upload to Play Console**  
   Create your app (if needed), then upload the signed AAB. When you enroll in **Play App Signing**, Google will use your first upload to set up the app signing key; later you keep signing with your upload key only.

### Option 2: Sign in Gradle (optional)

For repeat builds, you can configure release signing in the Android project so `bundleRelease` produces a signed AAB:

1. Create a keystore (as above) and put it somewhere safe (e.g. `packaging/ahoy-upload-key.keystore` – **do not commit it**; add to `.gitignore`).

2. Create `android/keystore.properties` (do not commit; add to `.gitignore`):

   ```properties
   storePassword=YOUR_STORE_PASSWORD
   keyPassword=YOUR_KEY_PASSWORD
   keyAlias=ahoy-upload
   storeFile=../packaging/ahoy-upload-key.keystore
   ```

3. In `android/app/build.gradle`, add a `signingConfigs` block and use it in `buildTypes.release`. (See [Android docs](https://developer.android.com/studio/publish/app-signing#gradle-sign).)

Then `./gradlew bundleRelease` will output a signed AAB.

## What you need to do in Play Console

- **Create the app** (if you haven’t), with package name `com.ahoy.app`.
- **Store listing:** title, short/full description, screenshots, icon, etc.
- **Content rating:** complete the questionnaire.
- **Pricing & distribution:** free/paid, countries.
- **Upload** the signed AAB (Release → Create new release → Upload).
- **Privacy policy URL** if required for your app type.

## Summary checklist

| Item | Status |
|------|--------|
| JDK + Android SDK (or Android Studio) | Needed for build |
| `./packaging/android-build.sh` or `npx cap sync android` + `./gradlew bundleRelease` | Produces unsigned AAB |
| Upload keystore (create once, keep safe) | Needed to sign AAB |
| Sign AAB with `jarsigner` (or Gradle signingConfig) | Required before upload |
| Google Play Developer account | Required to publish |
| Play Console: app, store listing, content rating, upload signed AAB | Required for release |

## Troubleshooting

- **Build fails (SDK not found):** Install Android Studio or set `ANDROID_HOME` to your SDK path.
- **jarsigner not found:** Use the JDK’s `jarsigner` (e.g. `$(/usr/libexec/java_home)/bin/jarsigner` on macOS).
- **Play Console asks for app signing key:** Enroll in Play App Signing and use your upload key for future uploads.
