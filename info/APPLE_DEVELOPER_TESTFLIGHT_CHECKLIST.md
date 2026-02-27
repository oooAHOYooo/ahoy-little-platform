# Apple Developer + TestFlight — Fast Checklist

Use this when enrolling and uploading your first build. Have these ready so you can move quickly.

---

## 1. Enroll in Apple Developer Program

- **Where:** https://developer.apple.com/programs/enroll/
- **Cost:** $99/year (USD)
- **You need:** Apple ID, payment method, legal name/address (can be individual or organization).

---

## 2. Info to Have Ready (for App Store Connect)

| What | Value to use |
|------|----------------|
| **App name** | `Ahoy Indie Media` |
| **Bundle ID** | `com.ahoy.app` (must match exactly; register in Developer portal) |
| **Primary language** | English (U.S.) or your choice |
| **SKU** | Any unique string (e.g. `ahoy-indie-media-001`) |
| **Category** | e.g. Music or Entertainment |
| **Export compliance** | App uses no custom encryption → answer “No” (we set `ITSAppUsesNonExemptEncryption = false`) |
| **App icon** | 1024×1024 px PNG (no transparency, no rounded corners) |

---

## 3. In Apple Developer Portal (developer.apple.com)

1. **Identifiers → App IDs**  
   - Create App ID with Bundle ID: **`com.ahoy.app`**  
   - Description: e.g. “Ahoy Indie Media iOS”

2. **Membership → Your team**  
   - Note your **Team ID** (e.g. `Y8654K535L`).  
   - In this project we use it in **`ios/App/ExportOptions.plist`** → replace `Y8654K535L` with your Team ID if different.

---

## 4. In Xcode (before building/uploading)

1. **Xcode → Settings → Accounts**  
   - Add your Apple ID (the one with the $99 program).  
   - Select your team.

2. **Signing**  
   - Open `ios/App/App.xcworkspace` in Xcode.  
   - Select the **App** target → **Signing & Capabilities**.  
   - Check “Automatically manage signing” and choose your **Team**.  
   - Bundle Identifier should be **`com.ahoy.app`**.

---

## 5. In App Store Connect (appstoreconnect.apple.com)

1. **My Apps → + → New App**  
   - Platform: iOS  
   - Name: **Ahoy Indie Media**  
   - Primary language  
   - Bundle ID: select **com.ahoy.app**  
   - SKU: (e.g. `ahoy-indie-media-001`)  
   - User access: Full Access (or your choice)

2. **App icon**  
   - In App Information (or in the app’s version), upload **1024×1024** icon if required for the first build.

3. **TestFlight**  
   - After the first upload, build appears under **TestFlight** tab.  
   - Add internal testers (your team) or external testers (need a group + first external build review).

---

## 6. Build and upload (from project root)

```bash
# Archive only (opens Xcode Organizer to upload manually)
./packaging/build-ios.sh

# Or archive + export + upload to App Store Connect
./packaging/build-ios.sh upload
```

Builds are **timestamped** (e.g. `App-202602271430.xcarchive`, build number `202602271430`) so you can tell them apart in TestFlight.

---

## 7. One-page “fill in the blanks” for Apple

Copy this and fill once, then use it everywhere:

```
App name:        Ahoy Indie Media
Bundle ID:       com.ahoy.app
Team ID:         _________________  (from developer.apple.com → Membership)
Apple ID:        _________________  (email you use for $99 program)
SKU:             ahoy-indie-media-001
Category:        Music (or Entertainment)
```

After your first successful upload, check **App Store Connect → TestFlight** for the build; processing usually takes 5–15 minutes.

---

## 8. If archive fails with “Sandbox: … Operation not permitted”

Xcode’s sandbox can block CocoaPods scripts when the build is run from certain environments (e.g. Cursor’s terminal). Do one of:

- Run the build from the **macOS Terminal** app (outside Cursor):  
  `cd /path/to/ahoy-little-platform && ./packaging/build-ios.sh`
- Or grant **Full Disk Access** to **Terminal** (and/or **Xcode**) in **System Preferences → Privacy & Security → Full Disk Access**.
