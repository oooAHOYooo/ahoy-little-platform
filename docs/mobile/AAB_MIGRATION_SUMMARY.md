# Android AAB Migration Summary

## What Was Changed

The Android build pipeline has been successfully migrated from **APK** to **AAB** (Android App Bundle) format, which is now required by Google Play Store.

### Files Modified

1. **`.github/workflows/android-apk.yml`**
   - Workflow renamed from "Build Android APK" to "Build Android AAB"
   - Build command changed from `./gradlew assembleRelease` to `./gradlew bundleRelease`
   - Artifact paths updated to: `android/app/build/outputs/bundle/release/*.aab`
   - Signing and upload steps updated to handle AAB format

2. **`scripts/sign_apk.sh`**
   - Updated to handle both APK and AAB files
   - Automatically detects file type
   - AAB files are signed but don't require zipalign (APK-specific)

### Current Build Configuration

- **Build Command**: `./gradlew bundleRelease` (runs in `android/` directory)
- **Output Location**: `android/app/build/outputs/bundle/release/app-release.aab`
- **Signing**: Uses existing keystore credentials (if provided via GitHub secrets)
- **CI/CD**: Workflow triggers on:
  - Manual workflow dispatch
  - Push of version tags (e.g., `v1.0.0`)

## Next Steps for Google Play Console Setup

### 1. Google Play Console Access
- Navigate to [Google Play Console](https://play.google.com/console)
- Ensure you have a developer account (one-time $25 fee)
- Create a new app or select existing app

### 2. App Signing Setup
**Important**: Google Play now manages app signing automatically. You have two options:

#### Option A: Let Google Play Manage Signing (Recommended)
- Upload an unsigned AAB
- Google Play will generate and manage the signing key
- You'll need to upload a "Play App Signing" key certificate for future updates

#### Option B: Use Your Own Upload Key
- Generate an upload keystore (if you haven't already)
- Configure the upload key in Google Play Console
- Sign your AAB with the upload key before uploading
- Google Play will re-sign with the app signing key

### 3. App Information Required
Before uploading, ensure you have:
- **App name**: "Ahoy Indie Media" (or your preferred name)
- **Default language**: English (or your primary language)
- **App category**: Music & Audio
- **Content rating**: Complete the questionnaire
- **Privacy policy URL**: Required for apps that collect user data
- **App icon**: 512x512px PNG (no transparency)
- **Feature graphic**: 1024x500px
- **Screenshots**: At least 2, up to 8 per device type (phone, tablet, TV, etc.)

### 4. Build Configuration Details
- **Package name**: `com.ahoy.app` (from `android/app/build.gradle`)
- **Version code**: Currently `1` (increment for each release)
- **Version name**: Currently `1.0` (in `android/app/build.gradle`)

### 5. Upload Process
1. Build the AAB locally or wait for CI/CD to build it
2. Go to Google Play Console → Your App → Production (or Testing track)
3. Click "Create new release"
4. Upload the `.aab` file
5. Fill in release notes
6. Review and publish

### 6. Testing Tracks (Recommended First Steps)
Before going to Production:
- **Internal testing**: Test with up to 100 testers
- **Closed testing**: Test with specific groups
- **Open testing**: Public beta testing

## Current State

✅ **Completed**:
- GitHub Actions workflow updated to build AAB
- Signing script updated to handle AAB
- Changes committed and pushed to repository

⏳ **Pending**:
- First AAB build (will happen on next workflow run or tag push)
- Google Play Console app creation/configuration
- Upload first AAB to Google Play
- Complete app store listing information

## Key Files Reference

- **Workflow**: `.github/workflows/android-apk.yml`
- **Build config**: `android/app/build.gradle`
- **Signing script**: `scripts/sign_apk.sh`
- **Package config**: `package.json` (Capacitor dependencies)

## Important Notes

1. **Version Management**: Remember to increment `versionCode` in `android/app/build.gradle` for each release
2. **Signing Keys**: If using your own upload key, keep the keystore secure and backed up
3. **Testing**: Always test AAB builds before uploading to production
4. **Size Optimization**: AAB format automatically generates optimized APKs per device, reducing download size

## Local Build Commands

To build AAB locally for testing:
```bash
npm install
npx cap sync android
cd android
./gradlew bundleRelease
```

The AAB will be at: `android/app/build/outputs/bundle/release/app-release.aab`
