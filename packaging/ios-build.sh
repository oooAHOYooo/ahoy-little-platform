#!/bin/bash
# Build iOS app archive for App Store submission.
# Prerequisite: Xcode → Settings → Platforms → install "iOS 18.2" (required for "Any iOS Device").
# Signing: run from Xcode (npx cap open ios) and use Product → Archive, then Distribute App.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
IOS_APP="$PROJECT_ROOT/ios/App"
ARCHIVE_PATH="$IOS_APP/build/App.xcarchive"
EXPORT_PATH="$PROJECT_ROOT/dist/ios"
EXPORT_OPTIONS="$SCRIPT_DIR/ExportOptions-ios-appstore.plist"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "Syncing Capacitor iOS..."
cd "$PROJECT_ROOT"
npx cap sync ios

echo ""
echo "Archiving iOS app (Release) for App Store..."
cd "$IOS_APP"
mkdir -p build

if ! xcodebuild -workspace App.xcworkspace -scheme App -configuration Release \
  -destination 'generic/platform=iOS' \
  archive -archivePath "$ARCHIVE_PATH" \
  -allowProvisioningUpdates 2>&1; then
  echo ""
  echo -e "${RED}Archive failed. If you see 'iOS 18.2 is not installed':${NC}"
  echo "  Xcode → Settings → Platforms → download iOS 18.2"
  echo ""
  echo "For code signing and App Store upload, use Xcode:"
  echo "  npx cap open ios"
  echo "  Then: Signing & Capabilities → select your Team, Product → Archive, Distribute App → App Store Connect"
  exit 1
fi

echo ""
echo -e "${GREEN}Archive created: $ARCHIVE_PATH${NC}"
echo ""
echo "Next: open in Xcode to sign and upload to App Store Connect:"
echo "  npx cap open ios"
echo "  Window → Organizer → select archive → Distribute App → App Store Connect"
echo ""
