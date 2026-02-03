#!/bin/bash
# Quick test on emulator (assumes emulator is already running)
set -e

echo "🚀 Quick test on Android emulator..."

# Check if emulator is running
if ! adb devices | grep -q "emulator"; then
    echo "❌ No emulator detected!"
    echo ""
    echo "Start emulator first with one of these commands:"
    echo "  emulator -avd Pixel_9_Pro &"
    echo "  emulator -avd Pixel_3a_API_34_extension_level_7_arm64-v8a &"
    echo ""
    echo "Or open Android Studio → Device Manager → Run an emulator"
    exit 1
fi

echo "✅ Emulator detected"

# Sync and build
echo "📦 Syncing assets..."
cd ..
npx cap sync android > /dev/null
cd android

echo "🔨 Building..."
./gradlew assembleRelease --quiet

echo "📲 Installing..."
adb install -r app/build/outputs/apk/release/app-release.apk

echo "🚀 Launching app..."
adb shell am start -n com.ahoy.app/.MainActivity

echo ""
echo "✅ Done! App is running"
echo ""
echo "📱 View logs: adb logcat | grep -i ahoy"
echo "🧹 Clear data: adb shell pm clear com.ahoy.app"
echo ""
