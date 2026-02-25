# Android Testing & Auto-Deploy Quick Start 🚀

## 📱 Test in Emulator (RIGHT NOW)

### Simplest Way:

```bash
# 1. Start emulator
emulator -avd Pixel_9_Pro &

# 2. Wait 30-60 seconds for boot, then:
cd android
./quick-test.sh
```

That's it! The app will build, install, and launch automatically.

---

## 🤖 Auto-Deploy to Play Store (One-Time Setup)

### TL;DR
Once set up, every `git push` to `main` automatically builds and uploads to Play Store Internal Testing.

### Setup (30 minutes, one time):

1. **Encode your keystore:**
   ```bash
   cd android/keystore
   base64 -i ahoy-release.jks | pbcopy
   # Now copied to clipboard
   ```

2. **Create Google Cloud Service Account:**
   - Go to https://console.cloud.google.com/
   - Create project → Enable "Google Play Android Developer API"
   - Create service account → Download JSON key

3. **Grant service account access to Play Console:**
   - Go to https://play.google.com/console
   - Setup → API access → Link project
   - Grant "Release to testing tracks" permission

4. **Add GitHub Secrets:**
   - Go to your repo → Settings → Secrets → Actions
   - Add these secrets:

   | Secret | Value |
   |--------|-------|
   | `ANDROID_KEYSTORE_BASE64` | Output from step 1 |
   | `KEYSTORE_PASSWORD` | `26trustdaL0RD` |
   | `KEY_ALIAS` | `ahoy` |
   | `KEY_PASSWORD` | `26trustdaL0RD` |
   | `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` | Paste entire JSON from step 2 |

5. **Done! Now test:**
   ```bash
   # Make a change
   echo "# Test" >> README.md
   git add .
   git commit -m "Test auto-deploy"
   git push origin main

   # Watch it deploy at:
   # https://github.com/YOUR_USERNAME/ahoy-little-platform/actions
   ```

Full instructions: `.github/workflows/SETUP-INSTRUCTIONS.md`

---

## 📚 Useful Files Created

- `android/quick-test.sh` - Quick test on running emulator
- `android/run-emulator.sh` - Start emulator + test (full auto)
- `android/TESTING.md` - Complete testing guide
- `.github/workflows/android-deploy.yml` - Auto-deploy workflow
- `.github/workflows/SETUP-INSTRUCTIONS.md` - Detailed setup guide

---

## 🎯 Common Commands

### Testing

```bash
# Quick test (emulator already running)
cd android && ./quick-test.sh

# Full automated test (starts emulator)
cd android && ./run-emulator.sh

# Manual build + install
cd android
./gradlew assembleRelease
adb install -r app/build/outputs/apk/release/app-release.apk

# View logs
adb logcat | grep -i ahoy

# Clear app data
adb shell pm clear com.ahoy.app
```

### Building

```bash
# Build signed AAB (for Play Store)
cd android && ./gradlew bundleRelease

# Build signed APK (for direct install)
cd android && ./gradlew assembleRelease

# Sync web assets first
npx cap sync android
```

### Deploy

```bash
# Auto-deploy (once GitHub Actions is set up)
git push origin main
# That's it! Check GitHub Actions tab

# Manual deploy
# 1. Build AAB: cd android && ./gradlew bundleRelease
# 2. Go to https://play.google.com/console
# 3. Upload: android/app/build/outputs/bundle/release/app-release.aab
```

---

## 🐛 Troubleshooting

### Emulator won't start
```bash
# List available emulators
emulator -list-avds

# Start specific emulator
emulator -avd Pixel_9_Pro -no-snapshot-load &
```

### App won't install
```bash
# Uninstall first
adb uninstall com.ahoy.app

# Kill and restart adb
adb kill-server && adb start-server

# Try again
adb install -r app/build/outputs/apk/release/app-release.apk
```

### Build fails
```bash
# Clean build
cd android
./gradlew clean
./gradlew bundleRelease

# Check Java version (needs Java 21)
java -version
```

### GitHub Actions fails
- Check secrets are added correctly
- Verify service account has Play Console access
- Wait 5-10 minutes after granting permissions
- Check logs in GitHub Actions tab

---

## 🎬 Next Steps

1. **Test locally:**
   ```bash
   emulator -avd Pixel_9_Pro &
   cd android && ./quick-test.sh
   ```

2. **Upload first version to Play Store manually:**
   - Build: `cd android && ./gradlew bundleRelease`
   - Upload AAB to Play Console (first version must be manual)
   - Create Internal Testing track

3. **Set up auto-deploy:**
   - Follow `.github/workflows/SETUP-INSTRUCTIONS.md`
   - Test with `git push`

4. **Add testers:**
   - Play Console → Testing → Internal testing → Testers
   - Share testing link with users

---

## 📊 What You Have Now

✅ **Signed AAB ready for Play Store**
- `/Users/agworkywork/ahoy-little-platform/android/app/build/outputs/bundle/release/app-release.aab`

✅ **Signed APK for local testing**
- `/Users/agworkywork/ahoy-little-platform/android/app/build/outputs/apk/release/app-release.apk`

✅ **Auto-deploy workflow ready**
- Just needs GitHub secrets configured

✅ **Testing scripts**
- Quick test on emulator
- Full automated emulator testing
- Comprehensive testing guide

---

**Need help?** Check these files:
- Testing: `android/TESTING.md`
- Auto-deploy: `.github/workflows/SETUP-INSTRUCTIONS.md`
