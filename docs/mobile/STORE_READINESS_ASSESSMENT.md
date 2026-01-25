# 📱 Mobile Store Readiness Assessment

**Date:** January 23, 2026  
**App:** Ahoy Indie Media  
**Current Status:** ~60% Ready for Android, ~20% Ready for iOS

---

## 🎯 Executive Summary

You have a **solid foundation** for Android store submission, but **iOS is not yet set up**. Here's what you have and what's missing:

### Android: ~60% Ready ✅
- ✅ Capacitor configured
- ✅ Android project structure complete
- ✅ Build system configured
- ✅ Icons and splash screens
- ✅ CI/CD workflow for APK builds
- ⚠️ Missing: iOS setup, store metadata, signing certificates, testing

### iOS: ~20% Ready ❌
- ✅ Capacitor config exists (but no iOS platform)
- ❌ No iOS project directory
- ❌ No iOS Capacitor package installed
- ❌ No iOS build configuration

---

## ✅ What You Have (Android)

### 1. **Capacitor Configuration** ✅
- `capacitor.config.ts` properly configured
- App ID: `com.ahoy.app`
- App Name: `Ahoy Indie Media`
- Web directory: `static`
- Server URL configured

### 2. **Android Project Structure** ✅
- Complete Android project in `/android/`
- Proper Gradle configuration
- AndroidManifest.xml with permissions
- App icons in all required densities
- Splash screens configured
- MainActivity.java exists

### 3. **Build System** ✅
- Gradle build files configured
- Version: `1.0` (versionCode: 1, versionName: "1.0")
- Min SDK: 22 (Android 5.1)
- Target SDK: 33 (Android 13)
- Compile SDK: 33

### 4. **CI/CD** ✅
- GitHub Actions workflow for Android APK builds
- Automated signing support (via secrets)
- Release automation on tags

### 5. **Legal Documents** ✅
- Privacy Policy exists (`/templates/privacy.html`)
- Terms of Service exists (`/templates/terms.html`)

---

## ❌ What's Missing

### Android Store (Google Play)

#### Critical (Required for Submission)
1. **App Signing Certificate** ❌
   - No keystore file found
   - Need to generate: `keytool -genkey -v -keystore ahoy-release-key.jks`
   - Store securely (GitHub Secrets for CI/CD)

2. **App Bundle (AAB)** ⚠️
   - Currently building APK only
   - Google Play requires AAB format
   - Update build.gradle to generate AAB

3. **Store Listing Assets** ❌
   - App screenshots (phone, tablet, TV)
   - Feature graphic (1024x500)
   - App icon (512x512)
   - Short description (80 chars)
   - Full description (4000 chars)
   - Category selection
   - Content rating questionnaire

4. **Privacy Policy URL** ⚠️
   - Need publicly accessible URL
   - Currently only in templates
   - Deploy to production URL

5. **Version Management** ⚠️
   - Version code still at 1
   - Need versioning strategy
   - Update for each release

6. **Testing** ❌
   - No device testing documented
   - Need to test on multiple Android versions
   - Test on different screen sizes

#### Important (For Better Submission)
7. **App Store Optimization** ❌
   - Keywords research
   - Localized descriptions
   - Promotional graphics

8. **Permissions Justification** ⚠️
   - Currently only INTERNET and WAKE_LOCK
   - May need additional permissions for media playback
   - Document why each permission is needed

9. **Content Rating** ❌
   - Complete Google Play content rating questionnaire
   - May need to adjust based on content

10. **Data Safety Section** ❌
    - Complete Google Play Data Safety form
    - Document data collection practices

### iOS Store (App Store)

#### Critical (Required to Start)
1. **iOS Platform Setup** ❌
   ```bash
   npm install @capacitor/ios
   npx cap add ios
   ```

2. **iOS Project Directory** ❌
   - No `/ios/` directory exists
   - Need to generate with Capacitor

3. **Xcode Configuration** ❌
   - Bundle identifier: `com.ahoy.app`
   - Version and build numbers
   - Signing certificates
   - Provisioning profiles

4. **Apple Developer Account** ❌
   - Need paid Apple Developer account ($99/year)
   - App ID registration
   - Certificates and provisioning profiles

5. **Info.plist Configuration** ❌
   - Privacy descriptions (NSCameraUsageDescription, etc.)
   - App Transport Security settings
   - Required device capabilities

6. **App Icons** ⚠️
   - Need iOS-specific icon sizes
   - App Store icon (1024x1024)

7. **Splash Screens** ⚠️
   - iOS-specific launch screens
   - Storyboard or image assets

#### Important
8. **Store Listing** ❌
   - App screenshots (all required sizes)
   - App preview videos (optional)
   - Description and keywords
   - Category selection
   - Age rating

9. **App Store Connect Setup** ❌
   - Create app record
   - Configure in-app purchases (if needed)
   - Set up TestFlight for beta testing

10. **Testing** ❌
    - Test on physical iOS devices
    - Test on different iOS versions
    - Test on iPhone and iPad

---

## 📋 Action Plan

### Phase 1: Android Store Submission (2-3 weeks)

#### Week 1: Setup & Configuration
- [ ] Generate Android signing keystore
- [ ] Configure AAB build (instead of APK)
- [ ] Update version code/name strategy
- [ ] Test build locally
- [ ] Update CI/CD to build AAB

#### Week 2: Store Assets & Metadata
- [ ] Create app screenshots (phone, tablet)
- [ ] Design feature graphic (1024x500)
- [ ] Write store description
- [ ] Complete content rating questionnaire
- [ ] Complete Data Safety form
- [ ] Deploy privacy policy to public URL

#### Week 3: Testing & Submission
- [ ] Test on multiple Android devices
- [ ] Test on different Android versions
- [ ] Internal testing track
- [ ] Submit to Google Play
- [ ] Address review feedback

### Phase 2: iOS Store Submission (3-4 weeks)

#### Week 1: iOS Setup
- [ ] Install @capacitor/ios
- [ ] Generate iOS project (`npx cap add ios`)
- [ ] Configure Xcode project
- [ ] Set up Apple Developer account
- [ ] Configure signing certificates

#### Week 2: iOS Configuration
- [ ] Configure Info.plist
- [ ] Add iOS app icons
- [ ] Create iOS splash screens
- [ ] Test build in Xcode
- [ ] Test on physical device

#### Week 3: Store Assets
- [ ] Create iOS screenshots (all sizes)
- [ ] Write App Store description
- [ ] Complete App Store Connect setup
- [ ] Set up TestFlight beta

#### Week 4: Submission
- [ ] TestFlight internal testing
- [ ] Submit for App Store review
- [ ] Address review feedback

---

## 🔧 Technical Tasks

### Android

1. **Generate Signing Keystore**
   ```bash
   keytool -genkey -v -keystore android/app/ahoy-release-key.jks \
     -keyalg RSA -keysize 2048 -validity 10000 \
     -alias ahoy-key
   ```

2. **Update build.gradle for AAB**
   ```gradle
   // In android/app/build.gradle
   buildTypes {
       release {
           signingConfig signingConfigs.release
           // ...
       }
   }
   ```

3. **Update Version**
   ```gradle
   // In android/app/build.gradle
   defaultConfig {
       versionCode 2
       versionName "1.0.1"
   }
   ```

### iOS

1. **Install iOS Platform**
   ```bash
   npm install @capacitor/ios
   npx cap add ios
   ```

2. **Open in Xcode**
   ```bash
   npx cap open ios
   ```

3. **Configure in Xcode**
   - Set bundle identifier
   - Configure signing
   - Add app icons
   - Configure Info.plist

---

## 📊 Readiness Checklist

### Android (Google Play)
- [x] Capacitor configured
- [x] Android project exists
- [x] Build system configured
- [x] Icons and splash screens
- [x] CI/CD workflow
- [ ] Signing keystore generated
- [ ] AAB build configured
- [ ] Store listing assets
- [ ] Privacy policy URL
- [ ] Content rating completed
- [ ] Data Safety form completed
- [ ] Testing on devices
- [ ] Google Play Developer account

### iOS (App Store)
- [x] Capacitor config exists
- [ ] iOS platform installed
- [ ] iOS project generated
- [ ] Xcode configured
- [ ] Apple Developer account
- [ ] Signing certificates
- [ ] App icons (iOS sizes)
- [ ] Splash screens
- [ ] Info.plist configured
- [ ] Store listing assets
- [ ] App Store Connect setup
- [ ] Testing on devices

---

## 🎯 Estimated Timeline

- **Android Store Submission:** 2-3 weeks
- **iOS Store Submission:** 3-4 weeks (after Android)
- **Total:** 5-7 weeks to both stores

---

## 💡 Recommendations

1. **Start with Android** - You're closer to ready
2. **Use TestFlight for iOS** - Easier beta testing
3. **Automate versioning** - Use scripts to bump version codes
4. **Store assets in repo** - Create `/store-assets/` directory
5. **Document testing** - Keep notes on tested devices/versions
6. **Prepare for rejections** - Both stores may request changes

---

## 📚 Resources

- [Google Play Console](https://play.google.com/console)
- [App Store Connect](https://appstoreconnect.apple.com)
- [Capacitor iOS Guide](https://capacitorjs.com/docs/ios)
- [Capacitor Android Guide](https://capacitorjs.com/docs/android)
- [Google Play Policy](https://play.google.com/about/developer-content-policy/)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)

---

**Last Updated:** January 23, 2026
