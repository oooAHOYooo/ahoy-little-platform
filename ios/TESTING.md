# iOS Testing Guide

## 🎯 The Reality: iOS Needs Xcode (Mostly)

Unlike Android, iOS development is more locked down. Here's what you CAN and CAN'T do via terminal:

### ✅ **Terminal CAN Do:**
- Sync web assets: `npx cap sync ios`
- List simulators: `xcrun simctl list devices`
- Boot simulator: `xcrun simctl boot <device-id>`
- Install app on simulator: `xcrun simctl install <device-id> <app-path>`
- Launch app: `xcrun simctl launch <device-id> <bundle-id>`
- View logs: `xcrun simctl spawn booted log stream --predicate 'process == "App"'`

### ❌ **Terminal CANNOT Do (Easily):**
- Build the app without Xcode (CocoaPods sandboxing issues)
- Sign for device deployment (requires Xcode + Apple Developer account)
- Submit to App Store (TestFlight requires Xcode or Transporter app)

### 💡 **Best Approach: Hybrid**
Use terminal for quick tasks, Xcode for building/running.

---

## 🚀 Quick Start Options

### Option 1: Capacitor CLI (Recommended - One Command!)

```bash
# Sync and run in one command
npx cap run ios

# Choose a specific simulator
npx cap run ios --target="iPhone 16 Pro"

# List available devices first
npx cap run ios --list
```

**This will:**
1. ✅ Sync web assets
2. ✅ Build the app
3. ✅ Launch simulator
4. ✅ Install and run app

### Option 2: Xcode GUI (Full Control)

```bash
# 1. Sync assets
npx cap sync ios

# 2. Open in Xcode
open ios/App/App.xcworkspace

# In Xcode:
# - Select simulator (top toolbar): iPhone 16
# - Press ▶️ or Cmd+R
```

### Option 3: Terminal + Xcode Hybrid

```bash
# Terminal: Sync assets
npx cap sync ios

# Terminal: Open Xcode
open ios/App/App.xcworkspace

# Xcode: Build and run (Cmd+R)
```

---

## 📱 Available Simulators

You have these iOS simulators:
- **iPhone 16** ← Recommended
- **iPhone 16 Pro**
- **iPhone 16 Pro Max**
- **iPhone 17, 17 Pro, 17 Pro Max**
- **iPhone SE (3rd generation)**
- **iPad Pro, iPad Air, iPad mini**

---

## 🎮 Simulator Commands (Terminal)

### Start/Stop Simulator

```bash
# List all simulators
xcrun simctl list devices

# Boot specific simulator
xcrun simctl boot "iPhone 16"

# Or boot by ID
xcrun simctl boot 42FEF628-1AE0-4199-BA64-FA644D941C5C

# Open Simulator app
open -a Simulator

# Shutdown simulator
xcrun simctl shutdown "iPhone 16"

# Shutdown all simulators
xcrun simctl shutdown all
```

### App Management

```bash
# Install app (after building in Xcode)
xcrun simctl install booted /path/to/App.app

# Launch app
xcrun simctl launch booted com.ahoy.app

# Uninstall app
xcrun simctl uninstall booted com.ahoy.app

# Clear app data (like "Reset Content and Settings")
xcrun simctl erase booted
```

### Debugging

```bash
# View logs (shows all output)
xcrun simctl spawn booted log stream --predicate 'process == "App"'

# View logs with level filter
xcrun simctl spawn booted log stream --level debug

# View console logs only
xcrun simctl spawn booted log stream --predicate 'eventMessage contains "console"'

# Take screenshot
xcrun simctl io booted screenshot screenshot.png

# Record video
xcrun simctl io booted recordVideo recording.mp4
# Press Ctrl+C to stop
```

### Simulator Settings

```bash
# Get device info
xcrun simctl getenv booted

# Set timezone
xcrun simctl spawn booted defaults write com.apple.preferences.timezone TimeZone "America/New_York"

# Enable dark mode
xcrun simctl ui booted appearance dark

# Enable light mode
xcrun simctl ui booted appearance light

# Increase/decrease contrast
xcrun simctl ui booted increase_contrast enabled
```

---

## 🔧 Development Workflow

### Quick Iteration (Web Changes Only)

```bash
# Make changes to Flask templates/static files

# Sync to iOS (copies web assets)
npx cap sync ios

# Restart app in simulator
# (Press Home → tap app icon)

# Or use Capacitor CLI to rebuild
npx cap run ios
```

### Live Reload (Advanced)

```bash
# 1. Run Flask locally
python app.py
# Note the URL: http://localhost:5001

# 2. Get your Mac's local IP
ipconfig getifaddr en0
# Example: 192.168.1.100

# 3. Update capacitor.config.ts
# Change server.url to "http://192.168.1.100:5001"

# 4. Sync and rebuild
npx cap sync ios
npx cap run ios

# Now the app loads from your local server!
# Changes to templates reflect immediately (no rebuild needed)
```

---

## 🐛 Debugging with Safari Web Inspector

iOS apps use WKWebView, which you can debug with Safari:

```bash
# 1. Run app in simulator
npx cap run ios

# 2. Open Safari on Mac
# 3. Safari → Settings → Advanced → Show Develop menu
# 4. Develop menu → Simulator → iPhone 16 → localhost
# 5. Web Inspector opens with full DevTools!
```

Now you have:
- Console logs
- Network inspector
- DOM inspector
- JavaScript debugger
- Performance profiler

---

## 📦 Building for Distribution

### TestFlight (App Store Beta Testing)

#### Option 1: Xcode (Easier)

```bash
# 1. Open project
open ios/App/App.xcworkspace

# In Xcode:
# 2. Product → Archive
# 3. Organizer opens → Distribute App
# 4. TestFlight & App Store → Upload
# 5. Select team → Upload
```

#### Option 2: Command Line (Advanced)

```bash
# 1. Sync assets
npx cap sync ios

# 2. Archive (requires proper signing setup)
cd ios/App
xcodebuild archive \
  -workspace App.xcworkspace \
  -scheme App \
  -configuration Release \
  -archivePath build/App.xcarchive

# 3. Export for App Store
xcodebuild -exportArchive \
  -archivePath build/App.xcarchive \
  -exportOptionsPlist ExportOptions.plist \
  -exportPath build/

# 4. Upload to App Store Connect
xcrun altool --upload-app \
  --type ios \
  --file build/App.ipa \
  --username "your@email.com" \
  --password "@keychain:AC_PASSWORD"
```

**Reality:** Option 1 (Xcode) is WAY easier for iOS. Command line works but requires more setup.

---

## 🧪 Testing Checklist

Before submitting to TestFlight:

**Simulator Testing:**
- [ ] App launches without crashes
- [ ] All core features work
- [ ] UI looks good on iPhone and iPad
- [ ] Dark mode works
- [ ] Landscape orientation works (if applicable)
- [ ] No console errors in Safari Web Inspector

**Device Testing (if available):**
- [ ] Test on real iPhone via USB
- [ ] Touch interactions work smoothly
- [ ] Camera/microphone permissions (if used)
- [ ] Background audio works (if applicable)
- [ ] App doesn't drain battery excessively

---

## 🚨 Common Issues

### "No simulators found"
```bash
# Reinstall simulators
xcodebuild -downloadPlatform iOS
```

### "Operation not permitted" during build
- This is a sandboxing issue with CocoaPods
- **Solution:** Use Xcode GUI or `npx cap run ios`

### "Code signing required"
- Simulator builds don't need signing
- Device builds require Apple Developer account
- **Solution:** Use simulator for testing, Xcode for device builds

### "App crashes on launch"
```bash
# View crash logs
xcrun simctl spawn booted log stream --level error
```

### "Can't connect Safari Web Inspector"
1. Simulator → Settings → Safari → Advanced → Web Inspector (ON)
2. Restart simulator
3. Try again

### "Slow simulator performance"
```bash
# Shutdown all simulators
xcrun simctl shutdown all

# Boot only the one you need
xcrun simctl boot "iPhone 16"

# Allocate more RAM in Xcode:
# Window → Devices and Simulators → Simulators → Edit
```

---

## 🎯 What Terminal CAN'T Do (But Xcode Can)

| Task | Terminal | Xcode |
|------|----------|-------|
| Sync web assets | ✅ Easy | ✅ Auto |
| Build for simulator | ⚠️ Complex | ✅ Easy |
| Build for device | ❌ Hard | ✅ Easy |
| Code signing | ❌ Manual | ✅ Auto |
| TestFlight upload | ⚠️ Possible | ✅ Easy |
| Debug with breakpoints | ❌ No | ✅ Yes |
| UI debugging | ❌ No | ✅ Yes |
| Performance profiling | ❌ Limited | ✅ Full |

**Verdict:** For iOS, Xcode is your friend. Use terminal for quick syncs and simulator management, but build/deploy in Xcode.

---

## 🔄 Auto-Deploy to TestFlight (GitHub Actions)

Yes, you can auto-deploy iOS too! But it requires:
1. Apple Developer account ($99/year)
2. App Store Connect API key
3. Signing certificates in GitHub Secrets
4. More complex setup than Android

See `.github/workflows/SETUP-INSTRUCTIONS.md` for full guide (coming soon).

**Reality check:** iOS auto-deploy is complex. Most teams just use Xcode for iOS deploys.

---

## 📚 Quick Reference

```bash
# Fastest way to test
npx cap run ios

# Sync only
npx cap sync ios

# Open in Xcode
open ios/App/App.xcworkspace

# List simulators
xcrun simctl list devices | grep iPhone

# Boot iPhone 16
xcrun simctl boot "iPhone 16"
open -a Simulator

# View logs
xcrun simctl spawn booted log stream --predicate 'process == "App"'

# Uninstall app
xcrun simctl uninstall booted com.ahoy.app

# Reset simulator
xcrun simctl erase booted
```

---

**Bottom line:** Use `npx cap run ios` for quick testing. Use Xcode for serious development and deployment. Terminal alone can't easily build iOS apps (thanks, Apple! 😅)
