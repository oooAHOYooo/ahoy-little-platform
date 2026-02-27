# Apple Developer — Little Market LLC Zero-Hour Runbook

**Status:** Enrollment **In Review**. Do not change configs or run cleanup until Apple approves.

---

## Enrolled Account (do not use until approved)

| Item | Value |
|------|--------|
| **Legal entity** | Little Market LLC |
| **Apple ID** | alex@littlemarket.org |
| **Enrollment ID** | 5A8M5QU9GP |
| **Public-facing app name** | Ahoy Indie Media (DBA) |
| **Bundle ID** | com.ahoy.app |

**Goal:** Publish under brand **Ahoy Indie Media** (DBA) with **Little Market LLC** as the legal seller of record.

---

## 1. Identity Update (after approval)

When Apple provides your **Team ID**:

### 1.1 Xcode / Export options
- **File:** `ios/App/ExportOptions.plist`  
- **Change:** Replace the `<string>Y8654K535L</string>` (or current placeholder) with your new **Team ID** inside the `teamID` key.

### 1.2 Xcode project (if needed)
- Open **`ios/App/App.xcworkspace`** in Xcode.
- Select the **App** target → **Signing & Capabilities**.
- Set **Team** to the team for **Little Market LLC** (alex@littlemarket.org).
- Confirm **Bundle Identifier** is **`com.ahoy.app`**.

### 1.3 Apple Developer portal
- **Certificates, Identifiers & Profiles → Identifiers → App IDs**
- Register (or confirm) an App ID with **Bundle ID: `com.ahoy.app`** and assign it to **Little Market LLC**.

### 1.4 Capacitor
- Capacitor does not store Team ID or Apple credentials; it uses the Xcode project and ExportOptions.plist. No Capacitor config changes required for Team ID—only the iOS project and ExportOptions above.

---

## 2. Code Signing Cleanup (run only after approval, from macOS Terminal)

Use these to remove old provisioning profiles and certificates from a **previous** Apple Developer account so they don’t conflict with Little Market LLC.

```bash
# 2.1 List current provisioning profiles (inspect before delete)
ls -la ~/Library/MobileDevice/Provisioning\ Profiles/

# 2.2 Remove all local provisioning profiles (Xcode will re-download for the new account)
rm -rf ~/Library/MobileDevice/Provisioning\ Profiles/*

# 2.3 Clear Xcode’s derived data for this project (avoids stale signing artifacts)
rm -rf ~/Library/Developer/Xcode/DerivedData/App-*

# 2.4 Optional: clear Xcode caches for signing (if you still see wrong team/cert)
# default delete com.apple.dt.Xcode in ~/Library/Caches/com.apple.dt.Xcode 2>/dev/null
# Prefer: In Xcode → Settings → Accounts → select old account → Remove (-). Then add alex@littlemarket.org.

# 2.5 After adding alex@littlemarket.org in Xcode → Settings → Accounts, download manual profiles:
# Xcode → Settings → Accounts → [Little Market LLC] → Download Manual Profiles
```

**Order:** Sign in with **alex@littlemarket.org** in Xcode first, then run 2.1–2.3. Remove the old account from Xcode Accounts if it’s still present.

---

## 3. App Store Connect — Company Name / Legal Entity Verification

If Apple asks why the **App Name** (“Ahoy Indie Media”) differs from the **Legal Entity** (“Little Market LLC”), use this draft:

---

**Draft response (Company Name / Legal Entity):**

> Little Market LLC is our legal entity. “Ahoy Indie Media” is our public-facing brand name (DBA). We want the app to appear in the App Store under the brand name “Ahoy Indie Media” while the seller and billing entity remains Little Market LLC. This is a standard DBA (doing business as) setup.

---

**Where it may be needed:** App Store Connect app creation (e.g. “Company Name” or “Legal Entity” vs “App Name”), or in response to a review note asking about the name mismatch.

---

## 4. Shell Script — Build and Troubleshooting

After the new Team ID is set and code signing is cleaned up:

1. **Run from macOS Terminal** (not Cursor), from repo root:
   ```bash
   cd /Users/agworkywork/ahoy-little-platform
   ./packaging/build-ios.sh
   ```

2. **If you see “Sandbox: … Operation not permitted”**  
   You’re likely still in a restricted environment. Use the same command in the **Terminal** app (outside Cursor). Optionally grant **Full Disk Access** to **Terminal** (and/or **Xcode**) in **System Preferences → Privacy & Security**.

3. **If signing errors mention “team” or “provisioning profile”**  
   - Confirm **ExportOptions.plist** has the correct **Team ID** for Little Market LLC.  
   - In Xcode, open **ios/App/App.xcworkspace** → App target → **Signing & Capabilities** → set **Team** to Little Market LLC and ensure **Automatically manage signing** is on.  
   - Run the cleanup commands in **Section 2** if you haven’t yet.

4. **If “No such module” or CocoaPods errors**  
   From repo root:
   ```bash
   cd ios/App && pod install && cd ../..
   ```
   Then run **`./packaging/build-ios.sh`** again.

5. **Successful run**  
   The script will open Xcode Organizer with the archive. Use **Distribute App → TestFlight & App Store → Upload**.

---

## 5. Quick Reference After Approval

1. Get **Team ID** from [developer.apple.com](https://developer.apple.com) → Membership.
2. Update **`ios/App/ExportOptions.plist`** → `teamID` = your Team ID.
3. In **Xcode → Settings → Accounts**, add **alex@littlemarket.org** (and remove old account if desired).
4. Run **Section 2** cleanup commands in Terminal.
5. In Xcode, open **ios/App/App.xcworkspace**, set App target **Team** to Little Market LLC.
6. In **App Store Connect**, create app with **com.ahoy.app**, name **Ahoy Indie Media**; use **Section 3** draft if asked about company name vs app name.
7. Run **`./packaging/build-ios.sh`** from Terminal and upload the archive to TestFlight.

---

*Document created for zero-hour execution once Apple Developer Program enrollment (5A8M5QU9GP) is approved. Last updated: 2026-02-27.*
