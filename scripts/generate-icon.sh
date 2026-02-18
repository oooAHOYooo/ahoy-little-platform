#!/bin/bash
# Generate .icns file for macOS from a PNG logo
# Usage: ./scripts/generate-icon.sh path/to/logo.png output_directory

SRC_IMAGE=${1:-"static/img/ahoy-fall2025-favicon.png"}
OUTPUT_DIR=${2:-"packaging/icons"}
ICONSET_DIR="${OUTPUT_DIR}/ahoy.iconset"

if [ ! -f "$SRC_IMAGE" ]; then
    echo "❌ Source image not found: $SRC_IMAGE"
    exit 1
fi

mkdir -p "$ICONSET_DIR"

echo "🎨 Generating iconset from $SRC_IMAGE..."

# Generate various sizes using sips
sips -z 16 16     "$SRC_IMAGE" --out "${ICONSET_DIR}/icon_16x16.png"
sips -z 32 32     "$SRC_IMAGE" --out "${ICONSET_DIR}/icon_16x16@2x.png"
sips -z 32 32     "$SRC_IMAGE" --out "${ICONSET_DIR}/icon_32x32.png"
sips -z 64 64     "$SRC_IMAGE" --out "${ICONSET_DIR}/icon_32x32@2x.png"
sips -z 128 128   "$SRC_IMAGE" --out "${ICONSET_DIR}/icon_128x128.png"
sips -z 256 256   "$SRC_IMAGE" --out "${ICONSET_DIR}/icon_128x128@2x.png"
sips -z 256 256   "$SRC_IMAGE" --out "${ICONSET_DIR}/icon_256x256.png"
sips -z 512 512   "$SRC_IMAGE" --out "${ICONSET_DIR}/icon_256x256@2x.png"
sips -z 512 512   "$SRC_IMAGE" --out "${ICONSET_DIR}/icon_512x512.png"
sips -z 1024 1024 "$SRC_IMAGE" --out "${ICONSET_DIR}/icon_512x512@2x.png"

echo "📦 Converting iconset to .icns..."
iconutil -c icns "$ICONSET_DIR" -o "${OUTPUT_DIR}/ahoy.icns"

# Clean up iconset
# rm -rf "$ICONSET_DIR"

echo "✅ Generated ${OUTPUT_DIR}/ahoy.icns"
ls -lh "${OUTPUT_DIR}/ahoy.icns"
