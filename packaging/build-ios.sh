#!/bin/bash
set -e

# ──────────────────────────────────────────────
# Ahoy Indie Media — iOS Build for TestFlight
# ──────────────────────────────────────────────
#
# Usage:
#   ./packaging/build-ios.sh          # archive only (then open Xcode to upload)
#   ./packaging/build-ios.sh upload   # archive + export + upload to App Store Connect
#
# Prerequisites:
#   - Apple Developer account ($99/yr)
#   - Xcode with your Apple ID signed in (Xcode → Settings → Accounts)
#   - Bundle ID "com.ahoy.app" registered in Apple Developer portal
#   - Run from project root: ./packaging/build-ios.sh

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IOS_DIR="$PROJECT_ROOT/ios/App"
BUILD_TS=$(date +%Y%m%d%H%M)
ARCHIVE_PATH="$IOS_DIR/build/App-$BUILD_TS.xcarchive"
EXPORT_PATH="$IOS_DIR/build/export-$BUILD_TS"
EXPORT_OPTIONS="$IOS_DIR/ExportOptions.plist"

echo "═══════════════════════════════════════════"
echo "  Ahoy Indie Media — iOS Build"
echo "  Build timestamp: $BUILD_TS"
echo "═══════════════════════════════════════════"

# So Capacitor/Xcode clean can manage the build dir
mkdir -p "$IOS_DIR/build"
xattr -w com.apple.xcode.CreatedByBuildSystem true "$IOS_DIR/build" 2>/dev/null || true

# Step 1: Sync Capacitor
echo ""
echo "▸ Syncing Capacitor..."
cd "$PROJECT_ROOT"
npx cap sync ios

# Step 2: Install CocoaPods (in case of changes)
echo ""
echo "▸ Installing CocoaPods..."
cd "$IOS_DIR"
pod install

# Step 3: Remove this build's outputs (keep other timestamped builds)
echo ""
echo "▸ Cleaning this build's outputs..."
rm -rf "$ARCHIVE_PATH" "$EXPORT_PATH"

# Step 4: Archive (build number = timestamp for TestFlight)
echo ""
echo "▸ Building archive (version 1.0 / build $BUILD_TS)..."
XC_LOG="$PROJECT_ROOT/ios/App/xcodebuild-$$.log"
if ! xcodebuild \
    -workspace "$IOS_DIR/App.xcworkspace" \
    -scheme App \
    -configuration Release \
    -archivePath "$ARCHIVE_PATH" \
    -destination "generic/platform=iOS" \
    CURRENT_PROJECT_VERSION="$BUILD_TS" \
    archive \
    > "$XC_LOG" 2>&1; then
    echo ""
    echo "❌ Archive failed. Last 30 lines:"
    tail -30 "$XC_LOG"
    echo ""
    echo "Full log: $XC_LOG"
    echo "If you see 'Sandbox: ... Operation not permitted', run this script from the macOS Terminal app (not Cursor) or grant Full Disk Access to Terminal in System Preferences → Privacy & Security."
    rm -f "$XC_LOG"
    exit 1
fi
tail -20 "$XC_LOG"
rm -f "$XC_LOG"

# Write build info (build dir exists after a successful archive)
echo "Build: $BUILD_TS | Version: 1.0 | $(date '+%Y-%m-%dT%H:%M:%S%z')" > "$IOS_DIR/build/build-$BUILD_TS.txt"
echo ""
echo "✅ Archive built: $ARCHIVE_PATH"

# Step 5: Export or open Xcode
if [ "$1" = "upload" ]; then
    echo ""
    echo "▸ Exporting and uploading to App Store Connect..."
    xcodebuild \
        -exportArchive \
        -archivePath "$ARCHIVE_PATH" \
        -exportOptionsPlist "$EXPORT_OPTIONS" \
        -exportPath "$EXPORT_PATH" \
        | tail -10

    echo "Build: $BUILD_TS | Version: 1.0 | $(date '+%Y-%m-%dT%H:%M:%S%z')" > "$EXPORT_PATH/build-info.txt"
    echo ""
    echo "✅ Upload complete! Check App Store Connect → TestFlight"
    echo "   Build $BUILD_TS — https://appstoreconnect.apple.com"
else
    echo ""
    echo "▸ Opening archive in Xcode Organizer..."
    echo "  From there: Distribute App → TestFlight & App Store → Upload"
    open "$ARCHIVE_PATH"
fi

echo ""
echo "═══════════════════════════════════════════"
echo "  Done!"
echo "═══════════════════════════════════════════"
