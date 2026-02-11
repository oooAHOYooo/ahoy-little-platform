#!/bin/bash
# Build macOS desktop app and create a GitHub release so app.ahoy.ooo/downloads can serve the zip/DMG.
#
# Prerequisites:
#   - GitHub CLI: brew install gh   (or https://cli.github.com/)
#   - gh auth login  (or set GITHUB_TOKEN)
#
# Usage:
#   ./packaging/release-desktop.sh           # upload existing dist-electron/*.dmg and *.zip
#   ./packaging/release-desktop.sh --build   # build first, then upload
#
# After running, the latest release assets appear at:
#   https://app.ahoy.ooo/downloads
#   https://github.com/oooAHOYooo/ahoy-little-platform/releases

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_ELECTRON="$PROJECT_ROOT/dist-electron"
BUILD_FIRST=false

for arg in "$@"; do
  [ "$arg" = "--build" ] && BUILD_FIRST=true
done

cd "$PROJECT_ROOT"

VERSION=$(node -p "require('./package.json').version")
TAG="v${VERSION}"

if [ "$BUILD_FIRST" = true ]; then
  echo "🔨 Building macOS app first..."
  "$SCRIPT_DIR/electron-build-mac.sh"
fi

if [ ! -d "$DIST_ELECTRON" ]; then
  echo "❌ No dist-electron/ directory. Run with --build or run ./packaging/electron-build-mac.sh first."
  exit 1
fi

# Collect installers (exclude blockmaps)
ASSETS=()
for f in "$DIST_ELECTRON"/*.dmg "$DIST_ELECTRON"/*.zip; do
  [ -f "$f" ] && [[ "$f" != *.blockmap ]] && ASSETS+=("$f")
done

if [ ${#ASSETS[@]} -eq 0 ]; then
  echo "❌ No .dmg or .zip found in dist-electron/. Run with --build first."
  exit 1
fi

echo "📦 Release tag: $TAG"
echo "📎 Assets to upload:"
printf '   %s\n' "${ASSETS[@]}"

if ! command -v gh &>/dev/null; then
  echo ""
  echo "❌ GitHub CLI (gh) not found. Install: brew install gh  then  gh auth login"
  echo "   Then create the release manually:"
  echo "   gh release create $TAG \\"
  for f in "${ASSETS[@]}"; do echo "     \"$f\" \\"; done
  echo "     --title \"Ahoy Indie Media $VERSION\" --notes \"Desktop release $VERSION\""
  exit 1
fi

# Create or reuse release and upload assets
if gh release view "$TAG" &>/dev/null; then
  echo "📤 Uploading to existing release $TAG..."
  gh release upload "$TAG" "${ASSETS[@]}" --clobber
else
  echo "📤 Creating release $TAG and uploading..."
  gh release create "$TAG" "${ASSETS[@]}" \
    --title "Ahoy Indie Media $VERSION" \
    --notes "Desktop app for macOS. Download the DMG (installer) or ZIP (drag to Applications)."
fi

echo ""
echo "✅ Done. Downloads will appear at:"
echo "   https://app.ahoy.ooo/downloads"
echo "   https://github.com/oooAHOYooo/ahoy-little-platform/releases/tag/$TAG"
