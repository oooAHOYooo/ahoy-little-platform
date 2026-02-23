#!/bin/bash
# Production Audit Script for Ahoy Indie Media

echo "--- App Store Readiness Audit ---"

# 1. Icons & Assets (iOS)
echo "[1/4] Checking iOS Assets..."
IOS_ICON="ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png"
if [ -f "$IOS_ICON" ]; then
    echo "✅ iOS App Icon exists."
else
    echo "❌ MISSING: iOS App Icon ($IOS_ICON)"
fi

# 2. Icons & Assets (Android)
echo -e "\n[2/4] Checking Android Assets..."
ANDROID_RES="android/app/src/main/res"
if [ -d "$ANDROID_RES/mipmap-xhdpi" ]; then
    echo "✅ Android mipmap resources found."
else
    echo "❌ MISSING: Android mipmap resources in $ANDROID_RES"
fi

# 3. Legal Documents
echo -e "\n[3/4] Checking Legal Views..."
if grep -q "Information We Collect" spa/src/views/PrivacyView.vue && grep -q "Acceptance of Terms" spa/src/views/TermsView.vue; then
    echo "✅ Privacy and Terms views expanded."
else
    echo "❌ WARNING: Privacy or Terms views seem minimal."
fi

# 4. Account Deletion (REQUIRED)
echo -e "\n[4/4] Checking Account Deletion Flow..."
if grep -q "delete-account" blueprints/api/auth.py && grep -q "onDeleteAccount" spa/src/views/AccountView.vue; then
    echo "✅ Account deletion logic found in backend and frontend."
else
    echo "❌ MISSING: Account deletion logic!"
fi

echo -e "\n--- Audit Complete ---"
