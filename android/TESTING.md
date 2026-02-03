# Android Testing Guide

## 🎮 Run in Emulator

### Option 1: Quick Test (Emulator Already Running)

```bash
# Start emulator first (in Android Studio or terminal)
emulator -avd Pixel_9_Pro &

# Then run quick test
cd android
./quick-test.sh
```

### Option 2: Full Automated Script

```bash
cd android
./run-emulator.sh
# This will start emulator, build, install, and launch
```

### Option 3: Manual Steps

```bash
# 1. List available emulators
emulator -list-avds

# 2. Start emulator (choose one)
emulator -avd Pixel_9_Pro &
# OR
emulator -avd Pixel_3a_API_34_extension_level_7_arm64-v8a &

# 3. Wait for boot (30-60 seconds)
adb wait-for-device

# 4. Build and install
cd android
./gradlew assembleRelease
adb install -r app/build/outputs/apk/release/app-release.apk

# 5. Launch app
adb shell am start -n com.ahoy.app/.MainActivity
```

## 📱 Run on Physical Device

### USB Connection

```bash
# 1. Enable USB debugging on your Android phone:
#    Settings → About phone → Tap "Build number" 7 times
#    Settings → Developer options → Enable "USB debugging"

# 2. Connect phone via USB

# 3. Verify connection
adb devices
# Should show your device

# 4. Build and install
cd android
./gradlew assembleRelease
adb install -r app/build/outputs/apk/release/app-release.apk

# 5. Launch
adb shell am start -n com.ahoy.app/.MainActivity
```

### Wireless Debugging (Android 11+)

```bash
# 1. Enable wireless debugging on phone:
#    Settings → Developer options → Wireless debugging → On

# 2. Tap "Wireless debugging" → "Pair device with pairing code"

# 3. On computer:
adb pair <IP>:<PORT>
# Enter the pairing code shown on phone

# 4. Connect
adb connect <IP>:<PORT>

# 5. Now use adb commands wirelessly!
adb install -r app/build/outputs/apk/release/app-release.apk
```

## 🐛 Debugging

### View Logs

```bash
# All logs
adb logcat

# Filter for your app
adb logcat | grep -i ahoy

# Clear logs first
adb logcat -c && adb logcat | grep -i ahoy

# Save logs to file
adb logcat > android-logs.txt
```

### Clear App Data

```bash
# Clear app data and cache
adb shell pm clear com.ahoy.app

# Uninstall completely
adb uninstall com.ahoy.app

# Reinstall
adb install -r app/build/outputs/apk/release/app-release.apk
```

### Inspect Network Requests

```bash
# Chrome DevTools for WebView
# 1. Open Chrome on desktop
# 2. Go to chrome://inspect
# 3. Your Capacitor app will appear under "Remote Target"
# 4. Click "inspect" to open DevTools
```

### Take Screenshots

```bash
# Take screenshot
adb shell screencap /sdcard/screenshot.png
adb pull /sdcard/screenshot.png

# Record video (max 3 minutes)
adb shell screenrecord /sdcard/demo.mp4
# Press Ctrl+C to stop
adb pull /sdcard/demo.mp4
```

## 🔄 Development Workflow

### Hot Reload Setup

For faster development with live reload:

```bash
# 1. Run Flask backend locally
python app.py
# Note the port (e.g., http://localhost:5001)

# 2. Update capacitor.config.ts to use local server
# Change server.url to "http://YOUR_IP:5001"
# (Use your computer's IP, not localhost)

# 3. Sync and rebuild
npx cap sync android
cd android
./gradlew assembleRelease
adb install -r app/build/outputs/apk/release/app-release.apk

# 4. Now app loads from your local server
# Changes to Flask templates/static files reflect immediately
# No need to rebuild APK for web changes!
```

To find your IP:
```bash
# macOS
ipconfig getifaddr en0

# Linux
hostname -I | awk '{print $1}'
```

### Quick Iteration

```bash
# For web-only changes (no Android code changes):
npx cap sync android
./quick-test.sh

# For Android code changes:
cd android
./gradlew assembleRelease
adb install -r app/build/outputs/apk/release/app-release.apk
```

## 🧪 Testing Checklist

Before uploading to Play Store, test:

- [ ] App launches without crashes
- [ ] Login/authentication works
- [ ] Music playback works
- [ ] Video playback works
- [ ] Queue functionality works
- [ ] Bookmarks sync correctly
- [ ] Network error handling (airplane mode test)
- [ ] App works offline (service worker)
- [ ] Back button navigation works
- [ ] Deep links work (if configured)
- [ ] Notifications work (if implemented)
- [ ] Permissions are requested properly
- [ ] No console errors in chrome://inspect

## 🚀 Performance Testing

```bash
# Monitor app performance
adb shell dumpsys cpuinfo | grep com.ahoy.app
adb shell dumpsys meminfo com.ahoy.app

# Monitor battery usage
adb shell dumpsys batterystats --reset
# Use app for a while
adb shell dumpsys batterystats com.ahoy.app
```

## 📊 Build Variants

### Debug Build (faster builds, but larger file size)

```bash
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

### Release Build (smaller, optimized)

```bash
./gradlew assembleRelease
adb install -r app/build/outputs/apk/release/app-release.apk
```

### Bundle (for Play Store)

```bash
./gradlew bundleRelease
# Output: app/build/outputs/bundle/release/app-release.aab
```

## Available Emulators

You have these emulators installed:
- **Pixel_9_Pro** (recommended for testing)
- **Pixel_3a_API_34_extension_level_7_arm64-v8a**
- **Android_TV_1080p_API_34** (for TV testing)

## Troubleshooting

### "No emulator detected"
- Start emulator: `emulator -avd Pixel_9_Pro &`
- Or open Android Studio → Device Manager

### "Installation failed"
- Uninstall first: `adb uninstall com.ahoy.app`
- Try again: `adb install app/build/outputs/apk/release/app-release.apk`

### "Emulator is slow"
- Close other apps
- Allocate more RAM in AVD settings (Android Studio)
- Use ARM emulator on Apple Silicon Macs

### "App crashes on launch"
- Check logs: `adb logcat | grep -i ahoy`
- Check for WebView errors: chrome://inspect
- Verify server URL in capacitor.config.ts

### "Can't connect to adb"
- Kill and restart: `adb kill-server && adb start-server`
- Check USB cable/connection
- Re-enable USB debugging on phone
