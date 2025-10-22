#!/usr/bin/env bash
# Desktop build script for Ahoy Indie Media
# Builds platform-specific executables using PyInstaller

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect OS
OS=$(uname -s)
ARCH=$(uname -m)

echo -e "${GREEN}Building Ahoy Indie Media Desktop App${NC}"
echo "OS: $OS"
echo "Architecture: $ARCH"
echo ""

# Clean previous builds
if [ -d "dist" ]; then
    echo -e "${YELLOW}Cleaning previous builds...${NC}"
    rm -rf dist
fi

# Install PyInstaller if not present
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${YELLOW}Installing PyInstaller...${NC}"
    pip install pyinstaller
fi

# Build based on OS
case "$OS" in
    "Darwin")
        echo -e "${GREEN}Building macOS .app bundle...${NC}"
        pyinstaller packaging/ahoy.spec --clean --noconfirm
        ;;
    "Linux")
        echo -e "${GREEN}Building Linux binary...${NC}"
        pyinstaller packaging/ahoy.spec --clean --noconfirm --onefile
        ;;
    "MINGW"*|"CYGWIN"*|"MSYS"*)
        echo -e "${GREEN}Building Windows .exe...${NC}"
        pyinstaller packaging/ahoy.spec --clean --noconfirm --onefile
        ;;
    *)
        echo -e "${RED}Unsupported OS: $OS${NC}"
        exit 1
        ;;
esac

# Generate build summary
echo ""
echo -e "${GREEN}Build Summary:${NC}"
echo "{"

# Find built files and generate JSON
files_found=false

if [ -d "dist" ]; then
    for file in dist/*; do
        if [ -f "$file" ] || [ -d "$file" ]; then
            if [ "$files_found" = true ]; then
                echo ","
            fi
            
            filename=$(basename "$file")
            if [ -f "$file" ]; then
                size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
                size_mb=$(echo "scale=2; $size / 1024 / 1024" | bc 2>/dev/null || echo "0")
                echo "  \"$filename\": {"
                echo "    \"path\": \"$file\","
                echo "    \"size_bytes\": $size,"
                echo "    \"size_mb\": $size_mb,"
                echo "    \"type\": \"file\""
                echo -n "  }"
            else
                echo "  \"$filename\": {"
                echo "    \"path\": \"$file\","
                echo "    \"type\": \"directory\""
                echo -n "  }"
            fi
            files_found=true
        fi
    done
fi

echo ""
echo "}"

if [ "$files_found" = false ]; then
    echo -e "${RED}No build artifacts found in dist/${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Build completed successfully!${NC}"
echo "Files are available in the dist/ directory"
