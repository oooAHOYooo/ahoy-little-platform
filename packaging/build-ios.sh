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
ARCHIVE_PATH="$IOS_DIR/build/App.xcarchive"
EXPORT_PATH="$IOS_DIR/build/export"
EXPORT_OPTIONS="$IOS_DIR/ExportOptions.plist"

echo "═══════════════════════════════════════════"
echo "  Ahoy Indie Media — iOS Build"
echo "═══════════════════════════════════════════"

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

# Step 3: Clean previous build
echo ""
echo "▸ Cleaning previous builds..."
rm -rf "$ARCHIVE_PATH" "$EXPORT_PATH"

# Step 4: Archive
echo ""
echo "▸ Building archive..."
xcodebuild \
    -workspace "$IOS_DIR/App.xcworkspace" \
    -scheme App \
    -configuration Release \
    -archivePath "$ARCHIVE_PATH" \
    -destination "generic/platform=iOS" \
    archive \
    | tail -20

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

    echo ""
    echo "✅ Upload complete! Check App Store Connect → TestFlight"
    echo "   https://appstoreconnect.apple.com"
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
