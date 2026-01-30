#!/usr/bin/env bash
# Android APK/AAB signing script for Ahoy Indie Media
# Signs and aligns APK or signs AAB for release distribution

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Android APK/AAB Signing Script${NC}"

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
    echo -e "${YELLOW}Skipping signing - will output unsigned file${NC}"
    exit 0
fi

# Input file path
INPUT_FILE="${1:-android/app/build/outputs/apk/release/app-release-unsigned.apk}"

if [[ ! -f "$INPUT_FILE" ]]; then
    echo -e "${RED}Error: Input file not found: $INPUT_FILE${NC}"
    echo "Please build the APK first with: ./gradlew assembleRelease"
    echo "Or build the AAB with: ./gradlew bundleRelease"
    exit 1
fi

# Detect file type
if [[ "$INPUT_FILE" == *.aab ]]; then
    FILE_TYPE="AAB"
    OUTPUT_FILE="AhoyIndieMedia-Android-release.aab"
    echo -e "${GREEN}Signing AAB: $INPUT_FILE${NC}"
else
    FILE_TYPE="APK"
    OUTPUT_FILE="AhoyIndieMedia-Android-release.apk"
    echo -e "${GREEN}Signing APK: $INPUT_FILE${NC}"
fi

# Decode keystore from base64
echo "Decoding keystore..."
echo "$ANDROID_KEYSTORE_BASE64" | base64 -d > keystore.jks

# Sign the file
echo "Signing $FILE_TYPE with jarsigner..."
jarsigner \
    -verbose \
    -sigalg SHA256withRSA \
    -digestalg SHA-256 \
    -keystore keystore.jks \
    -storepass "$ANDROID_KEYSTORE_PASSWORD" \
    -keypass "$ANDROID_KEY_PASSWORD" \
    "$INPUT_FILE" \
    "$ANDROID_KEY_ALIAS"

# Align the APK (AABs don't need alignment)
if [[ "$FILE_TYPE" == "APK" ]]; then
    echo "Aligning APK with zipalign..."
    zipalign -v 4 "$INPUT_FILE" "$OUTPUT_FILE"
else
    # For AAB, just copy the signed file
    cp "$INPUT_FILE" "$OUTPUT_FILE"
fi

# Verify the signed file
echo "Verifying signed $FILE_TYPE..."
jarsigner -verify -verbose -certs "$OUTPUT_FILE"

# Clean up
rm -f keystore.jks

echo -e "${GREEN}✅ $FILE_TYPE signed successfully: $OUTPUT_FILE${NC}"
echo -e "${GREEN}File size: $(du -h "$OUTPUT_FILE" | cut -f1)${NC}"
