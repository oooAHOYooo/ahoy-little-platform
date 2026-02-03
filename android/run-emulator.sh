#!/bin/bash
# Run Ahoy app in Android emulator
set -e

echo "🚀 Starting Ahoy on Android Emulator..."

# Choose emulator (Pixel 9 Pro is the most modern)
EMULATOR_NAME="Pixel_9_Pro"

# Check if emulator is already running
if adb devices | grep -q "emulator"; then
    echo "✅ Emulator already running"
else
    echo "📱 Starting emulator: $EMULATOR_NAME"
    echo "   (This will open in a new window, wait 30-60 seconds for boot)"

    # Start emulator in background
    emulator -avd "$EMULATOR_NAME" -no-snapshot-load -wipe-data &

    # Wait for device to be ready
    echo "⏳ Waiting for emulator to boot..."
    adb wait-for-device

    # Wait a bit more for full boot
    sleep 10

    echo "✅ Emulator ready!"
fi

# Sync latest web assets
echo "📦 Syncing web assets..."
cd ..
npx cap sync android
cd android

# Build and install
echo "🔨 Building release APK..."
./gradlew assembleRelease --quiet

echo "📲 Installing app on emulator..."
adb install -r app/build/outputs/apk/release/app-release.apk

echo ""
echo "✅ App installed! Launching..."
echo ""

# Launch app (use your actual package name and activity)
adb shell am start -n com.ahoy.app/.MainActivity

echo ""
echo "🎉 Done! App should be running on emulator"
echo ""
echo "Useful commands:"
echo "  adb logcat | grep -i ahoy     # View app logs"
echo "  adb uninstall com.ahoy.app    # Uninstall app"
echo "  adb shell pm clear com.ahoy.app  # Clear app data"
echo ""
