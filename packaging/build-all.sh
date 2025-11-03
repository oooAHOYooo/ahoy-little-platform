#!/bin/bash
# Master Build Script for Ahoy Indie Media Desktop Apps
# Builds platform-specific installers for macOS and Windows

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Ahoy Indie Media - Desktop App Builder${NC}"
echo ""

# Detect OS
OS=$(uname -s)
ARCH=$(uname -m)

echo -e "${GREEN}Detected: ${OS} (${ARCH})${NC}"
echo ""

# Create dist directory
mkdir -p "$DIST_DIR"

# Platform-specific builds
case "$OS" in
    "Darwin")
        echo -e "${GREEN}🍎 Building for macOS...${NC}"
        echo ""
        
        # Build macOS app
        "$SCRIPT_DIR/macos-build.sh"
        
        # Create DMG
        echo ""
        echo -e "${GREEN}💿 Creating macOS DMG installer...${NC}"
        "$SCRIPT_DIR/make_dmg.sh"
        
        echo ""
        echo -e "${GREEN}✅ macOS build complete!${NC}"
        echo -e "${BLUE}Files created in: $DIST_DIR${NC}"
        ls -lh "$DIST_DIR"/*.app "$DIST_DIR"/*.dmg 2>/dev/null || true
        ;;
        
    "Linux")
        echo -e "${YELLOW}🐧 Linux detected. Building Linux binary...${NC}"
        echo ""
        
        # Check if running in WSL (for Windows builds)
        if grep -qEi "(Microsoft|WSL)" /proc/version &> /dev/null; then
            echo -e "${YELLOW}⚠️  Detected WSL. For Windows builds, use Windows PowerShell or install NSIS.${NC}"
            echo ""
        fi
        
        # Build Linux binary (basic, no installer)
        echo "Building Linux standalone binary..."
        cd "$PROJECT_ROOT"
        pyinstaller \
            --clean \
            --noconfirm \
            --onefile \
            --windowed \
            --name="AhoyIndieMedia" \
            --icon="$SCRIPT_DIR/icons/ahoy.ico" \
            --add-data="templates:templates" \
            --add-data="static:static" \
            --add-data="data:data" \
            --add-data="ahoy:ahoy" \
            desktop_main.py
        
        echo ""
        echo -e "${GREEN}✅ Linux build complete!${NC}"
        ;;
        
    "MINGW"*|"CYGWIN"*|"MSYS"*)
        echo -e "${GREEN}🪟 Building for Windows...${NC}"
        echo ""
        "$SCRIPT_DIR/windows-build.sh"
        echo ""
        echo -e "${GREEN}✅ Windows build complete!${NC}"
        ;;
        
    *)
        echo -e "${RED}❌ Unsupported OS: $OS${NC}"
        echo ""
        echo "Supported platforms:"
        echo "  - macOS (Darwin): Creates .app bundle and .dmg installer"
        echo "  - Windows: Creates .exe and NSIS installer"
        echo "  - Linux: Creates standalone binary"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Build process complete!${NC}"
echo ""
echo -e "${BLUE}📦 Artifacts location: $DIST_DIR${NC}"

