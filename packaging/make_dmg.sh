#!/bin/bash
set -e

# DMG Creation Script for Ahoy Indie Media
# Creates a macOS DMG with proper volume name and Applications alias

echo "💿 Creating DMG for Ahoy Indie Media..."

# Get absolute paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
APP_PATH="$DIST_DIR/AhoyIndieMedia.app"
DMG_PATH="$DIST_DIR/AhoyIndieMedia.dmg"
TEMP_DMG_PATH="$DIST_DIR/temp.dmg"
VOLUME_NAME="Ahoy Indie Media"
MOUNT_POINT="/Volumes/$VOLUME_NAME"

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo "❌ App bundle not found at $APP_PATH"
    echo "   Run packaging/macos-build.sh first"
    exit 1
fi

# Clean up any existing DMG and temp files
echo "🧹 Cleaning up previous DMG files..."
rm -f "$DMG_PATH" "$TEMP_DMG_PATH"
if [ -d "$MOUNT_POINT" ]; then
    hdiutil detach "$MOUNT_POINT" -force 2>/dev/null || true
fi

# Create temporary directory for DMG contents
TEMP_DMG_DIR="$DIST_DIR/dmg_contents"
rm -rf "$TEMP_DMG_DIR"
mkdir -p "$TEMP_DMG_DIR"

# Copy app to temp directory
echo "📦 Copying app to temporary directory..."
cp -R "$APP_PATH" "$TEMP_DMG_DIR/"

# Create Applications alias
echo "🔗 Creating Applications alias..."
ln -s /Applications "$TEMP_DMG_DIR/Applications"

# Copy background image if it exists
BACKGROUND_IMAGE="$SCRIPT_DIR/dmg_background.png"
if [ -f "$BACKGROUND_IMAGE" ]; then
    echo "🎨 Copying background image..."
    cp "$BACKGROUND_IMAGE" "$TEMP_DMG_DIR/.background.png"
fi

# Calculate size needed for DMG (add 20% buffer)
SIZE_MB=$(du -sm "$TEMP_DMG_DIR" | cut -f1)
SIZE_MB=$((SIZE_MB + SIZE_MB / 5))  # Add 20% buffer
echo "📏 DMG size will be approximately ${SIZE_MB}MB"

# Create temporary DMG
echo "🔨 Creating temporary DMG..."
hdiutil create \
    -srcfolder "$TEMP_DMG_DIR" \
    -volname "$VOLUME_NAME" \
    -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" \
    -format UDRW \
    -size ${SIZE_MB}m \
    "$TEMP_DMG_PATH"

# Mount the temporary DMG
echo "📂 Mounting temporary DMG..."
hdiutil attach "$TEMP_DMG_PATH" -readwrite -noverify -noautoopen

# Set up DMG appearance (optional, requires osascript)
if command -v osascript &> /dev/null; then
    echo "🎨 Setting up DMG appearance..."
    osascript <<EOF
tell application "Finder"
    tell disk "$VOLUME_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 600, 400}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 128
        set background picture of viewOptions to file ".background.png"
        set position of item "AhoyIndieMedia.app" of container window to {150, 200}
        set position of item "Applications" of container window to {350, 200}
        close
        open
        update
    end tell
end tell
EOF
fi

# Unmount the temporary DMG
echo "📤 Unmounting temporary DMG..."
hdiutil detach "$MOUNT_POINT"

# Convert to final compressed DMG
echo "🗜️  Creating final compressed DMG..."
hdiutil convert "$TEMP_DMG_PATH" \
    -format UDZO \
    -imagekey zlib-level=9 \
    -o "$DMG_PATH"

# Clean up temporary files
echo "🧹 Cleaning up temporary files..."
rm -f "$TEMP_DMG_PATH"
rm -rf "$TEMP_DMG_DIR"

# Verify DMG was created
if [ ! -f "$DMG_PATH" ]; then
    echo "❌ Failed to create DMG"
    exit 1
fi

# Get DMG info
DMG_SIZE=$(du -sh "$DMG_PATH" | cut -f1)
echo "✅ Successfully created DMG"
echo "📁 DMG path: $DMG_PATH"
echo "📏 DMG size: $DMG_SIZE"

# Calculate SHA256
echo "🔐 Calculating SHA256 checksum..."
DMG_SHA256=$(shasum -a 256 "$DMG_PATH" | cut -d' ' -f1)
echo "🔑 DMG SHA256: $DMG_SHA256"

echo "🎉 DMG creation complete!"

