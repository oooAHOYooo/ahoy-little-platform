# iOS App Store Build Guide

Build and submit the Ahoy Indie Media iOS app (Capacitor) for the App Store.

## Prerequisites

1. **Xcode** with **iOS 18.2 platform** installed  
   - Xcode → Settings → **Platforms** → download **iOS 18.2**  
   - Without this, builds fail with: *"iOS 18.2 is not installed"*

2. **Apple Developer account**  
   - Signed in under Xcode → Settings → Accounts  
   - Team selected for the App target (Signing & Capabilities)

3. **App Store Connect**  
   - App created in [App Store Connect](https://appstoreconnect.apple.com) with matching bundle ID

## Option A: Build archive from terminal, then distribute in Xcode

1. Install the iOS 18.2 platform (Xcode → Settings → Platforms) if not already done.

2. From the project root:
   ```bash
   ./packaging/ios-build.sh
   ```
   This syncs the Capacitor iOS project and creates an archive at  
   `ios/App/build/App.xcarchive`.

3. Open the iOS project in Xcode:
   ```bash
   npx cap open ios
   ```

4. In Xcode:
   - **Window → Organizer** (or **Product → Archive** to create a new archive)
   - Select the **App** archive
   - Click **Distribute App**
   - Choose **App Store Connect** → **Upload**
   - Select your team and options, then **Upload**

## Option B: Build and archive entirely in Xcode

1. Install the iOS 18.2 platform (Xcode → Settings → Platforms).

2. Sync and open:
   ```bash
   npx cap sync ios
   npx cap open ios
   ```

3. In Xcode:
   - Select **Signing & Capabilities** for the **App** target and choose your **Team**
   - Select destination **Any iOS Device**
   - **Product → Archive**
   - In Organizer: **Distribute App** → **App Store Connect** → **Upload**

## Export options (optional)

For command-line export after archiving (e.g. in CI), you can use:

```bash
xcodebuild -exportArchive \
  -archivePath ios/App/build/App.xcarchive \
  -exportPath dist/ios \
  -exportOptionsPlist packaging/ExportOptions-ios-appstore.plist
```

Signing still requires your Apple ID/team; use **-allowProvisioningUpdates** if xcodebuild should manage profiles.

## Troubleshooting

- **"iOS 18.2 is not installed"**  
  Install the platform: Xcode → Settings → Platforms → iOS 18.2 → Get.

- **Code signing errors**  
  In Xcode: select the App target → Signing & Capabilities → choose your Team (Automatic signing).

- **Archive not appearing in Organizer**  
  Ensure you built with destination **Any iOS Device** (not a simulator).
