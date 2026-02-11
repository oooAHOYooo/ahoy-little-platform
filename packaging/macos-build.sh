#!/bin/bash
set -e

# macOS Build Script for Ahoy Indie Media
# Builds a macOS .app bundle using PyInstaller

echo "🍎 Building Ahoy Indie Media for macOS..."

# Get absolute paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
APP_PATH="$DIST_DIR/AhoyIndieMedia.app"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# Change to project root
cd "$PROJECT_ROOT"

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Check if required dependencies are installed
echo "📦 Checking dependencies..."
python -c "import webview" 2>/dev/null || {
    echo "📦 Installing pywebview..."
    pip install pywebview
}

# Build the app using PyInstaller with simplified configuration
# Note: omit --icon if ahoy.icns is invalid for Pillow; app will use default icon
echo "🔨 Building .app bundle with PyInstaller..."
ICON_ARG=""
if [ -f "$SCRIPT_DIR/icons/ahoy.icns" ] && python3 -c "
from PIL import Image
import sys
try:
    with Image.open('$SCRIPT_DIR/icons/ahoy.icns') as im:
        pass
except Exception:
    sys.exit(1)
" 2>/dev/null; then
    ICON_ARG="--icon=$SCRIPT_DIR/icons/ahoy.icns"
else
    # Remove spec so PyInstaller regenerates without icon (avoids BUNDLE icon error)
    rm -f "$PROJECT_ROOT/AhoyIndieMedia.spec"
fi
pyinstaller \
    --clean \
    --noconfirm \
    --distpath "$DIST_DIR" \
    --workpath "$PROJECT_ROOT/build" \
    --onedir \
    --windowed \
    $ICON_ARG \
    --name="AhoyIndieMedia" \
    --add-data="templates:templates" \
    --add-data="static:static" \
    --add-data="data:data" \
    --add-data="ahoy:ahoy" \
    --hidden-import="flask" \
    --hidden-import="webview" \
    --hidden-import="pywebview" \
    --hidden-import="structlog" \
    --hidden-import="bcrypt" \
    --hidden-import="flask_limiter" \
    --hidden-import="flask_cors" \
    --hidden-import="flask_login" \
    --hidden-import="flask_bcrypt" \
    --hidden-import="flask_wtf" \
    --hidden-import="sqlalchemy" \
    --hidden-import="alembic" \
    --hidden-import="psycopg" \
    --hidden-import="sentry_sdk" \
    --hidden-import="werkzeug" \
    --hidden-import="jinja2" \
    --hidden-import="markupsafe" \
    --hidden-import="itsdangerous" \
    --hidden-import="click" \
    --hidden-import="python_dotenv" \
    --hidden-import="gunicorn" \
    --hidden-import="requests" \
    --hidden-import="marshmallow" \
    --hidden-import="pyjwt" \
    --hidden-import="email_validator" \
    --hidden-import="limits" \
    --hidden-import="python_json_logger" \
    "desktop_main.py"

# Create .app bundle from the directory
echo "📦 Creating .app bundle..."
EXECUTABLE_DIR="$DIST_DIR/AhoyIndieMedia"
if [ -d "$EXECUTABLE_DIR" ]; then
    # Create the .app bundle structure
    mkdir -p "$APP_PATH/Contents/MacOS"
    mkdir -p "$APP_PATH/Contents/Resources"
    
    # Copy the executable and all files
    cp -R "$EXECUTABLE_DIR"/* "$APP_PATH/Contents/MacOS/"
    
    # Create Info.plist
    cat > "$APP_PATH/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>AhoyIndieMedia</string>
    <key>CFBundleIdentifier</key>
    <string>com.ahoyindiemedia.desktop</string>
    <key>CFBundleName</key>
    <string>Ahoy Indie Media</string>
    <key>CFBundleDisplayName</key>
    <string>Ahoy Indie Media</string>
    <key>CFBundleVersion</key>
    <string>0.1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>0.1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
</dict>
</plist>
EOF
    
    # Copy icon
    cp "$SCRIPT_DIR/icons/ahoy.icns" "$APP_PATH/Contents/Resources/"
    
    # Clean up the directory
    rm -rf "$EXECUTABLE_DIR"
    
    echo "✅ Created .app bundle from directory"
else
    echo "❌ Executable directory not found at $EXECUTABLE_DIR"
    exit 1
fi

# Verify the app was created
if [ ! -d "$APP_PATH" ]; then
    echo "❌ Failed to create .app bundle"
    exit 1
fi

# Get app info
APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)
echo "✅ Successfully built AhoyIndieMedia.app"
echo "📁 App path: $APP_PATH"
echo "📏 App size: $APP_SIZE"

# Calculate SHA256
echo "🔐 Calculating SHA256 checksum..."
APP_SHA256=$(find "$APP_PATH" -type f -exec shasum -a 256 {} \; | shasum -a 256 | cut -d' ' -f1)
echo "🔑 App SHA256: $APP_SHA256"

echo "🎉 macOS build complete!"
