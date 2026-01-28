#!/bin/bash
# Build Android release AAB for Play Store.
# Output: android/app/build/outputs/bundle/release/app-release.aab (unsigned).
# Sign with your upload key before uploading (see ANDROID_PLAY_STORE_GUIDE.md).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Syncing Capacitor Android..."
cd "$PROJECT_ROOT"
npx cap sync android

echo ""
echo "Building release AAB..."
cd "$PROJECT_ROOT/android"
./gradlew bundleRelease

echo ""
echo "Done. AAB: android/app/build/outputs/bundle/release/app-release.aab"
echo "Sign for Play Store (see packaging/ANDROID_PLAY_STORE_GUIDE.md):"
echo "  jarsigner -keystore your.keystore android/app/build/outputs/bundle/release/app-release.aab your-alias"
echo ""
