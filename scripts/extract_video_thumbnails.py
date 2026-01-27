#!/usr/bin/env python3
"""
Extract thumbnails from videos that don't have them or have broken (404) thumbnails.
Downloads a small portion of the video, extracts a frame, and caches it locally.

Usage:
    python scripts/extract_video_thumbnails.py              # Only process empty thumbnails
    python scripts/extract_video_thumbnails.py --check-urls # Also check if existing thumbnails are 404
    python scripts/extract_video_thumbnails.py --force      # Regenerate ALL thumbnails
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path
import hashlib

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SHOWS_JSON = PROJECT_ROOT / "static" / "data" / "shows.json"
VIDEOS_JSON = PROJECT_ROOT / "static" / "data" / "videos.json"
THUMBNAILS_DIR = PROJECT_ROOT / "static" / "thumbnails"


def ensure_thumbnails_dir():
    """Create thumbnails directory if it doesn't exist"""
    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
    return THUMBNAILS_DIR


def check_thumbnail_accessible(thumbnail_url, timeout=10):
    """
    Check if a thumbnail URL is accessible (not 404).

    Args:
        thumbnail_url: URL to check (or local path starting with /static/)
        timeout: Request timeout in seconds

    Returns:
        True if accessible, False if 404 or unreachable
    """
    if not thumbnail_url:
        return False

    # Handle local paths
    if thumbnail_url.startswith("/static/"):
        local_path = PROJECT_ROOT / thumbnail_url.lstrip("/")
        return local_path.exists() and local_path.stat().st_size > 0

    # Handle remote URLs
    if not REQUESTS_AVAILABLE:
        # Can't check remote URLs without requests library
        return True  # Assume valid if we can't check

    try:
        response = requests.head(thumbnail_url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException:
        return False


def get_video_hash(video_url):
    """Generate a hash from video URL for consistent naming"""
    return hashlib.md5(video_url.encode()).hexdigest()[:12]


def extract_thumbnail_from_video(video_url, output_path, seek_seconds=5):
    """
    Extract a thumbnail from a video URL using ffmpeg.
    Downloads a small portion and extracts a frame.
    
    Args:
        video_url: URL to the video
        output_path: Path where thumbnail should be saved
        seek_seconds: How many seconds into the video to extract (default 5)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Use ffmpeg to extract a frame from the video
        # -ss: seek to position
        # -i: input URL
        # -vframes 1: extract only 1 frame
        # -q:v 2: high quality JPEG
        # -y: overwrite output file
        cmd = [
            "ffmpeg",
            "-ss", str(seek_seconds),  # Seek to 5 seconds (or 10% if we know duration)
            "-i", video_url,
            "-vframes", "1",  # Extract only 1 frame
            "-q:v", "2",  # High quality (2 is best quality for JPEG)
            "-vf", "scale=1280:-1",  # Scale to max width 1280, maintain aspect ratio
            "-y",  # Overwrite output file
            str(output_path)
        ]
        
        # Run ffmpeg, capturing stderr for error messages
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        if result.returncode == 0 and output_path.exists():
            file_size = output_path.stat().st_size
            if file_size > 0:
                print(f"✓ Extracted thumbnail: {output_path.name} ({file_size} bytes)")
                return True
            else:
                print(f"✗ Thumbnail file is empty: {output_path}")
                return False
        else:
            print(f"✗ ffmpeg failed for {video_url}")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout extracting thumbnail from {video_url}")
        return False
    except FileNotFoundError:
        print("✗ ffmpeg not found. Please install ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Linux: apt-get install ffmpeg or yum install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"✗ Error extracting thumbnail: {e}")
        return False


def process_shows_json(check_urls=False, force=False):
    """
    Process shows.json and extract thumbnails for videos without them.

    Args:
        check_urls: If True, also check if existing thumbnail URLs are 404
        force: If True, regenerate ALL thumbnails regardless of existing ones
    """
    if not SHOWS_JSON.exists():
        print(f"✗ {SHOWS_JSON} not found")
        return False

    with open(SHOWS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated = False
    thumbnails_dir = ensure_thumbnails_dir()
    checked_count = 0
    broken_count = 0

    for show in data.get("shows", []):
        video_url = show.get("video_url") or show.get("trailer_url")
        thumbnail = show.get("thumbnail", "").strip()
        show_id = show.get("id", "unknown")
        title = show.get("title", show_id)[:50]

        # Skip if no video URL
        if not video_url:
            continue

        needs_thumbnail = False

        if force:
            # Force mode: regenerate all
            needs_thumbnail = True
            print(f"[FORCE] {title}")
        elif not thumbnail:
            # No thumbnail defined
            needs_thumbnail = True
            print(f"[EMPTY] {title}")
        elif check_urls:
            # Check if existing thumbnail is accessible
            checked_count += 1
            print(f"Checking [{show_id}] {title}...", end=" ", flush=True)
            if check_thumbnail_accessible(thumbnail):
                print("OK")
                continue
            else:
                print("BROKEN (404)")
                broken_count += 1
                needs_thumbnail = True

        if not needs_thumbnail:
            continue

        # Generate thumbnail filename
        video_hash = get_video_hash(video_url)
        thumbnail_filename = f"{show_id}_{video_hash}.jpg"
        thumbnail_path = thumbnails_dir / thumbnail_filename
        relative_path = f"/static/thumbnails/{thumbnail_filename}"

        # Skip if local thumbnail already exists (unless force mode)
        if thumbnail_path.exists() and not force:
            print(f"  ⊘ Local thumbnail exists: {thumbnail_filename}")
            if show.get("thumbnail") != relative_path:
                show["thumbnail"] = relative_path
                updated = True
            continue

        # Extract thumbnail
        print(f"  Extracting from: {video_url[:80]}...")

        if extract_thumbnail_from_video(video_url, thumbnail_path):
            show["thumbnail"] = relative_path
            updated = True
        else:
            print(f"  Failed to extract thumbnail")

    if check_urls and checked_count > 0:
        print(f"\nChecked {checked_count} thumbnails, {broken_count} broken")

    # Save updated JSON
    if updated:
        with open(SHOWS_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Updated {SHOWS_JSON}")
        return True

    return False


def process_videos_json(check_urls=False, force=False):
    """
    Process videos.json and extract thumbnails for videos without them.

    Args:
        check_urls: If True, also check if existing thumbnail URLs are 404
        force: If True, regenerate ALL thumbnails regardless of existing ones
    """
    if not VIDEOS_JSON.exists():
        print(f"⊘ {VIDEOS_JSON} not found, skipping")
        return False

    with open(VIDEOS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated = False
    thumbnails_dir = ensure_thumbnails_dir()
    checked_count = 0
    broken_count = 0

    for video in data.get("videos", []):
        video_url = video.get("url")
        thumbnail = video.get("thumbnail", "").strip()
        video_id = video.get("id", "unknown")
        title = video.get("title", video_id)[:50]

        # Skip if no video URL or status is not available
        if not video_url or video.get("status") != "available":
            continue

        needs_thumbnail = False

        if force:
            needs_thumbnail = True
            print(f"[FORCE] {title}")
        elif not thumbnail:
            needs_thumbnail = True
            print(f"[EMPTY] {title}")
        elif check_urls:
            checked_count += 1
            print(f"Checking [{video_id}] {title}...", end=" ", flush=True)
            if check_thumbnail_accessible(thumbnail):
                print("OK")
                continue
            else:
                print("BROKEN (404)")
                broken_count += 1
                needs_thumbnail = True

        if not needs_thumbnail:
            continue

        # Generate thumbnail filename
        video_hash = get_video_hash(video_url)
        thumbnail_filename = f"{video_id}_{video_hash}.jpg"
        thumbnail_path = thumbnails_dir / thumbnail_filename
        relative_path = f"/static/thumbnails/{thumbnail_filename}"

        # Skip if local thumbnail already exists (unless force mode)
        if thumbnail_path.exists() and not force:
            print(f"  ⊘ Local thumbnail exists: {thumbnail_filename}")
            if video.get("thumbnail") != relative_path:
                video["thumbnail"] = relative_path
                updated = True
            continue

        # Extract thumbnail
        print(f"  Extracting from: {video_url[:80]}...")

        if extract_thumbnail_from_video(video_url, thumbnail_path):
            video["thumbnail"] = relative_path
            updated = True
        else:
            print(f"  Failed to extract thumbnail")

    if check_urls and checked_count > 0:
        print(f"\nChecked {checked_count} thumbnails, {broken_count} broken")

    # Save updated JSON
    if updated:
        with open(VIDEOS_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Updated {VIDEOS_JSON}")
        return True

    return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Extract thumbnails from videos that don't have them or have broken thumbnails"
    )
    parser.add_argument(
        "--check-urls",
        action="store_true",
        help="Check if existing thumbnail URLs are accessible (404 detection)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate ALL thumbnails, even existing ones"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Video Thumbnail Extractor")
    print("=" * 60)

    if args.check_urls:
        print("Mode: Check URLs for broken thumbnails")
        if not REQUESTS_AVAILABLE:
            print("⚠ Warning: 'requests' library not installed.")
            print("  Install with: pip install requests")
            print("  Skipping URL checks for remote thumbnails.")
    elif args.force:
        print("Mode: Force regenerate ALL thumbnails")
    else:
        print("Mode: Process empty thumbnails only")
        print("  Tip: Use --check-urls to also find broken (404) thumbnails")

    print()

    # Check if ffmpeg is available
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ ffmpeg is not installed or not in PATH")
        print("  Please install ffmpeg to use this script:")
        print("    macOS: brew install ffmpeg")
        print("    Linux: apt-get install ffmpeg")
        sys.exit(1)

    print("✓ ffmpeg found")
    print()

    # Process both JSON files
    print("Processing shows.json...")
    print("-" * 40)
    shows_updated = process_shows_json(check_urls=args.check_urls, force=args.force)

    print()
    print("Processing videos.json...")
    print("-" * 40)
    videos_updated = process_videos_json(check_urls=args.check_urls, force=args.force)

    print()
    print("=" * 60)
    if shows_updated or videos_updated:
        print("✓ Thumbnail extraction complete!")
        print("  Local thumbnails saved to: static/thumbnails/")
        print("  These load instantly for end users.")
    else:
        print("⊘ No thumbnails needed extraction")
        if not args.check_urls:
            print("  Tip: Run with --check-urls to find broken (404) thumbnails")
    print("=" * 60)


if __name__ == "__main__":
    main()
