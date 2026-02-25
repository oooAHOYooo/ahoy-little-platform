#!/bin/bash
# Build Ahoy Indie Media for Linux (Ubuntu, Garuda, and other distros)
# Creates AppImage (universal) and DEB (Ubuntu/Debian) packages

set -e

echo "🚀 Building Ahoy Indie Media for Linux..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "${BLUE}📋 Checking prerequisites...${NC}"

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Install Node.js first."
    exit 1
fi

if ! command -v electron-builder &> /dev/null; then
    echo "📦 Installing electron-builder..."
    npm install --save-dev electron-builder
fi

# For DEB building, we need dpkg tools
if ! command -v dpkg-deb &> /dev/null; then
    echo "⚠️  dpkg-deb not found. DEB builds will be skipped."
    echo "   To build DEB files, install: sudo apt-get install dpkg"
fi

echo "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Build the SPA first
echo "${BLUE}📦 Building Vue SPA...${NC}"
cd spa
npm install --legacy-peer-deps > /dev/null 2>&1 || npm install
npm run build
cd ..
echo "${GREEN}✓ SPA built${NC}"
echo ""

# Run prebuild to generate build info
echo "${BLUE}🔨 Running prebuild...${NC}"
npm run prebuild
echo "${GREEN}✓ Prebuild complete${NC}"
echo ""

# Build for Linux
echo "${BLUE}🐧 Building Linux packages...${NC}"
echo "   - AppImage (universal, no installation needed)"
echo "   - DEB (Ubuntu/Debian)"
echo ""

npm run electron:build:all -- --linux

echo ""
echo "${GREEN}✓ Build complete!${NC}"
echo ""

# Show output location
echo "${BLUE}📁 Output location: dist-electron/${NC}"
ls -lh dist-electron/

echo ""
echo "${YELLOW}📦 Linux Packages:${NC}"
echo "   AppImage: dist-electron/*.AppImage (universal, works on any Linux)"
echo "   DEB:      dist-electron/*.deb (Ubuntu/Debian)"
echo ""

# Installation instructions
echo "${YELLOW}📋 How to install:${NC}"
echo ""
echo "   Option 1: AppImage (recommended, no installation needed)"
echo "   -  chmod +x dist-electron/Ahoy*.AppImage"
echo "   -  ./dist-electron/Ahoy*.AppImage"
echo ""
echo "   Option 2: DEB (Ubuntu/Debian-based, like Garuda)"
echo "   -  sudo apt install ./dist-electron/ahoy-indie-media*.deb"
echo "   -  Launch from Applications menu or: ahoy-indie-media"
echo ""

# On Garuda (Arch-based), suggest building AUR package
if [ -f /etc/os-release ]; then
    if grep -q "Garuda" /etc/os-release || grep -q "Arch" /etc/os-release; then
        echo "${YELLOW}🎉 Garuda/Arch Linux detected!${NC}"
        echo "   You can convert the AppImage to AUR or install directly:"
        echo "   chmod +x dist-electron/Ahoy*.AppImage && ./dist-electron/Ahoy*.AppImage"
        echo ""
    fi
fi

echo "${GREEN}✅ Done!${NC}"
