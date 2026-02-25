# iOS Testing & Deployment Quick Start 🍎

## 🎯 TL;DR: What Terminal CAN and CAN'T Do

### ✅ Terminal CAN Do:
```bash
# Sync web assets
npx cap sync ios

# Run in simulator (one command!)
npx cap run ios

# Manage simulators
xcrun simctl boot "iPhone 16"
open -a Simulator
```

### ❌ Terminal CAN'T Do (Need Xcode):
- Build reliably (CocoaPods sandboxing issues)
- Code signing for devices
- Upload to TestFlight easily

### 💡 Best Practice:
**Use hybrid approach:** Terminal for syncing, Xcode for building/deploying

---

## 🚀 Fastest Way to Test (ONE COMMAND)

```bash
npx cap run ios
```

That's it! This will:
1. ✅ Sync web assets
2. ✅ Build the app
3. ✅ Launch iPhone 16 simulator
4. ✅ Install and run

**Choose a specific simulator:**
```bash
npx cap run ios --target="iPhone 16 Pro"

# See all available
npx cap run ios --list
```

---

## 📱 Alternative: Use Xcode GUI

```bash
# 1. Sync assets
npx cap sync ios

# 2. Open Xcode
open ios/App/App.xcworkspace

# 3. In Xcode:
#    - Select "iPhone 16" from device dropdown (top left)
#    - Press ▶️ or Cmd+R to build and run
```

---

## 🐛 Debug with Safari Web Inspector

```bash
# 1. Run app
npx cap run ios

# 2. Open Safari → Develop → Simulator → iPhone 16 → localhost
# Now you have full DevTools!
```

- Console logs
- Network requests
- DOM inspector
- JavaScript debugger

---

## 🧪 Available Simulators

You have:
- **iPhone 16, 16 Pro, 16 Pro Max** ← Use these
- **iPhone 17, 17 Pro, 17 Pro Max**
- **iPhone SE (3rd generation)**
- **iPad Pro, iPad Air, iPad mini**

```bash
# List all
npx cap run ios --list
```

---

## 📦 Deploy to TestFlight

### Step 1: Prepare for Archive

```bash
# 1. Ensure you have Apple Developer account ($99/year)
# 2. Open Xcode
open ios/App/App.xcworkspace

# 3. In Xcode:
#    - Select "Any iOS Device" (not simulator)
#    - Product → Archive (Cmd+Shift+B)
```

### Step 2: Upload to TestFlight

```bash
# Xcode Organizer opens automatically after archive
# 1. Click "Distribute App"
# 2. Select "TestFlight & App Store"
# 3. Select your team
# 4. Click "Upload"
# 5. Wait for processing (~10-20 minutes)
```

### Step 3: Add Testers

```bash
# Go to App Store Connect
# https://appstoreconnect.apple.com/

# 1. My Apps → Your App → TestFlight
# 2. Click "+" to add testers
# 3. Enter email addresses
# 4. Testers receive email with TestFlight link
```

---

## 🤖 Auto-Deploy to TestFlight (Advanced)

Unlike Android, iOS auto-deploy is more complex:

**Requirements:**
- Apple Developer account ($99/year)
- App Store Connect API key
- Signing certificates & provisioning profiles
- Fastlane (deployment tool)
- GitHub Actions setup

**Reality:** Most teams just use Xcode manually for iOS. It's easier and more reliable.

**Want to set it up anyway?** See detailed guide: `.github/workflows/IOS-DEPLOY-SETUP.md` (coming soon)

---

## 🔧 Quick Commands

```bash
# Test in simulator (fastest)
npx cap run ios

# Sync assets only
npx cap sync ios

# Open in Xcode
open ios/App/App.xcworkspace

# Boot simulator manually
xcrun simctl boot "iPhone 16"
open -a Simulator

# View simulator logs
xcrun simctl spawn booted log stream --predicate 'process == "App"'

# Reset simulator
xcrun simctl erase booted

# Take screenshot
xcrun simctl io booted screenshot screenshot.png
```

---

## 🆚 iOS vs Android: Terminal Power

| Task | Android Terminal | iOS Terminal |
|------|------------------|--------------|
| Sync assets | ✅ `npx cap sync` | ✅ `npx cap sync` |
| Build AAB/IPA | ✅ `./gradlew bundleRelease` | ⚠️ Need Xcode |
| Run on emulator | ✅ Full auto | ⚠️ `npx cap run ios` (uses Xcode) |
| Install APK/IPA | ✅ `adb install` | ⚠️ `xcrun simctl install` |
| View logs | ✅ `adb logcat` | ✅ `xcrun simctl spawn` |
| Auto-deploy | ✅ Easy (GitHub Actions) | ⚠️ Complex (Fastlane required) |
| Code signing | ✅ Gradle config | ❌ Need Xcode |

**Verdict:** Android is WAY more terminal-friendly than iOS.

---

## 💡 Development Workflow

### Quick iteration (web changes only):

```bash
# 1. Make changes to Flask templates/static files

# 2. Sync
npx cap sync ios

# 3. Rerun
npx cap run ios
```

### Live reload (advanced):

```bash
# 1. Get your Mac's IP
ipconfig getifaddr en0
# Example: 192.168.1.100

# 2. Run Flask locally
python app.py
# Running on http://localhost:5001

# 3. Update capacitor.config.ts
# Change server.url to "http://192.168.1.100:5001"

# 4. Rebuild
npx cap sync ios
npx cap run ios

# Now app loads from local server!
# Changes reflect immediately (no rebuild)
```

---

## 🚨 Common Issues

### "`npx cap run ios` fails"
```bash
# Clean build folder
rm -rf ios/App/build

# Clean CocoaPods
cd ios/App && pod deintegrate && pod install
cd ../..

# Try again
npx cap run ios
```

### "No simulators available"
```bash
# Open Xcode → Settings → Platforms
# Download iOS simulator runtimes
```

### "Code signing failed"
- You're trying to build for device (not simulator)
- **Solution:** Select a simulator in Xcode, not "Any iOS Device"

### "Simulator is slow"
```bash
# Shutdown all simulators
xcrun simctl shutdown all

# Boot only one
xcrun simctl boot "iPhone 16"
```

---

## 📚 Files Created

- `ios/quick-test-sim.sh` - Simplified test script
- `ios/TESTING.md` - Complete iOS testing guide
- `IOS-QUICKSTART.md` - This file (quick reference)

---

## 🎯 Next Steps

1. **Test locally:**
   ```bash
   npx cap run ios
   ```

2. **Debug with Safari:**
   - Safari → Develop → Simulator → localhost

3. **Deploy to TestFlight:**
   - Xcode → Product → Archive
   - Distribute to TestFlight

4. **Add testers:**
   - App Store Connect → TestFlight → Add testers

---

## 🔄 Platform Comparison

**Android:** Terminal can do almost everything
**iOS:** Terminal for quick tasks, Xcode for builds/deploys

**Recommendation:**
- **Android:** Use terminal scripts + GitHub Actions
- **iOS:** Use `npx cap run ios` for testing, Xcode for deploys

---

**Bottom line:** iOS isn't as terminal-friendly as Android, but `npx cap run ios` makes testing easy. For production builds, just use Xcode. 🍎
