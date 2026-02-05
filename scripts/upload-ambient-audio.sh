#!/bin/bash
#
# Upload ambient audio files to Google Cloud Storage
# Usage: ./upload-ambient-audio.sh <source-folder> <bucket-name>
#
# Example:
#   ./upload-ambient-audio.sh ~/Downloads/ambient-audio ahoy-media-bucket
#
# Expected folder structure:
#   source-folder/
#     jazz/
#       Jazz Flow Track 1.mp3
#       Another Song.mp3
#     ambient/
#       Deep Space.mp3
#     lofi/
#       ...
#
# Output:
#   - Renames files to slugs (lowercase, hyphens)
#   - Uploads to gs://bucket/bg/<collection>/
#   - Prints URLs for ambient-modes.json

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 2 ]; then
    echo -e "${RED}Usage: $0 <source-folder> <bucket-name>${NC}"
    echo "Example: $0 ~/Downloads/ambient-audio ahoy-media-bucket"
    exit 1
fi

SOURCE_DIR="$1"
BUCKET="$2"
DEST_PREFIX="bg"

# Check if source exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}Error: Source folder '$SOURCE_DIR' not found${NC}"
    exit 1
fi

# Check if gsutil is available
if ! command -v gsutil &> /dev/null; then
    echo -e "${RED}Error: gsutil not found. Install Google Cloud SDK first.${NC}"
    echo "  brew install google-cloud-sdk"
    echo "  gcloud auth login"
    exit 1
fi

echo -e "${GREEN}=== Ambient Audio Upload Script ===${NC}"
echo "Source: $SOURCE_DIR"
echo "Bucket: gs://$BUCKET/$DEST_PREFIX/"
echo ""

# Function to slugify a filename
slugify() {
    local name="$1"
    # Remove extension, slugify, add back extension
    local base="${name%.*}"
    local ext="${name##*.}"

    # Convert to lowercase, replace spaces/underscores with hyphens, remove special chars
    local slug=$(echo "$base" | \
        tr '[:upper:]' '[:lower:]' | \
        sed 's/[_ ]/-/g' | \
        sed 's/[^a-z0-9-]//g' | \
        sed 's/--*/-/g' | \
        sed 's/^-//' | \
        sed 's/-$//')

    echo "${slug}.${ext}"
}

# Track URLs for JSON output
declare -a ALL_URLS

# Process each collection folder
for collection_dir in "$SOURCE_DIR"/*/; do
    if [ ! -d "$collection_dir" ]; then
        continue
    fi

    collection=$(basename "$collection_dir")
    collection_slug=$(echo "$collection" | tr '[:upper:]' '[:lower:]' | sed 's/[_ ]/-/g' | sed 's/[^a-z0-9-]//g')

    echo -e "${YELLOW}Processing collection: $collection -> $collection_slug${NC}"

    # Create temp dir for renamed files
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT

    file_count=0
    collection_urls=()

    # Process each MP3 in the collection
    for mp3 in "$collection_dir"*.mp3 "$collection_dir"*.MP3; do
        if [ ! -f "$mp3" ]; then
            continue
        fi

        original_name=$(basename "$mp3")
        slug_name=$(slugify "$original_name")

        # Copy with new name to temp dir
        cp "$mp3" "$TEMP_DIR/$slug_name"

        # Build URL
        url="https://storage.googleapis.com/$BUCKET/$DEST_PREFIX/$collection_slug/$slug_name"
        collection_urls+=("$url")
        ALL_URLS+=("$collection_slug|$url")

        echo "  $original_name -> $slug_name"
        ((file_count++))
    done

    if [ $file_count -eq 0 ]; then
        echo "  (no MP3 files found)"
        continue
    fi

    # Upload to GCS
    echo -e "  ${GREEN}Uploading $file_count files to gs://$BUCKET/$DEST_PREFIX/$collection_slug/${NC}"
    gsutil -m cp "$TEMP_DIR"/*.mp3 "gs://$BUCKET/$DEST_PREFIX/$collection_slug/"

    # Make public (optional - comment out if bucket has uniform access)
    # gsutil -m acl ch -u AllUsers:R "gs://$BUCKET/$DEST_PREFIX/$collection_slug/*.mp3"

    echo ""
done

# Output JSON snippet
echo -e "${GREEN}=== URLs for ambient-modes.json ===${NC}"
echo ""
echo "Copy these URLs into your ambient-modes.json audioPool sections:"
echo ""

current_collection=""
for item in "${ALL_URLS[@]}"; do
    collection="${item%%|*}"
    url="${item#*|}"

    if [ "$collection" != "$current_collection" ]; then
        if [ -n "$current_collection" ]; then
            echo ""
        fi
        echo "// $collection"
        current_collection="$collection"
    fi
    echo "\"$url\","
done

echo ""
echo -e "${GREEN}Done!${NC}"
