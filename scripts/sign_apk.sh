#!/usr/bin/env bash
"""
Android APK signing script for Ahoy Indie Media
Signs and aligns APK for release distribution
"""

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Android APK Signing Script${NC}"

# Check required environment variables
required_vars=(
    "ANDROID_KEYSTORE_BASE64"
    "ANDROID_KEY_ALIAS"
    "ANDROID_KEYSTORE_PASSWORD"
    "ANDROID_KEY_PASSWORD"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        missing_vars+=("$var")
    fi
done

if [[ ${#missing_vars[@]} -gt 0 ]]; then
    echo -e "${YELLOW}Warning: Missing environment variables:${NC}"
    printf '%s\n' "${missing_vars[@]}"
    echo -e "${YELLOW}Skipping signing - will output unsigned APK${NC}"
    exit 0
fi

# Input APK path
INPUT_APK="${1:-android/app/build/outputs/apk/release/app-release-unsigned.apk}"
OUTPUT_APK="AhoyIndieMedia-Android-release.apk"

if [[ ! -f "$INPUT_APK" ]]; then
    echo -e "${RED}Error: Input APK not found: $INPUT_APK${NC}"
    echo "Please build the APK first with: ./gradlew assembleRelease"
    exit 1
fi

echo -e "${GREEN}Signing APK: $INPUT_APK${NC}"

# Decode keystore from base64
echo "Decoding keystore..."
echo "$ANDROID_KEYSTORE_BASE64" | base64 -d > keystore.jks

# Sign the APK
echo "Signing APK with jarsigner..."
jarsigner \
    -verbose \
    -sigalg SHA256withRSA \
    -digestalg SHA-256 \
    -keystore keystore.jks \
    -storepass "$ANDROID_KEYSTORE_PASSWORD" \
    -keypass "$ANDROID_KEY_PASSWORD" \
    "$INPUT_APK" \
    "$ANDROID_KEY_ALIAS"

# Align the APK
echo "Aligning APK with zipalign..."
zipalign -v 4 "$INPUT_APK" "$OUTPUT_APK"

# Verify the signed APK
echo "Verifying signed APK..."
jarsigner -verify -verbose -certs "$OUTPUT_APK"

# Clean up
rm -f keystore.jks

echo -e "${GREEN}✅ APK signed successfully: $OUTPUT_APK${NC}"
echo -e "${GREEN}File size: $(du -h "$OUTPUT_APK" | cut -f1)${NC}"
