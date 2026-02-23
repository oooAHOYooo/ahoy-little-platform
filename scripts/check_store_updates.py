#!/usr/bin/env python3
import os
import sys
import requests
import re
import json
from typing import Dict, Optional

def get_local_version() -> str:
    """Read version from package.json in the project root."""
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pkg_path = os.path.join(root_dir, 'package.json')
        with open(pkg_path, 'r') as f:
            data = json.load(f)
            return data.get('version', '0.1.0')
    except Exception as e:
        print(f"Error reading local version: {e}")
        return "0.1.0"

def get_ios_version(bundle_id: str) -> Optional[str]:
    """Fetch the latest version from Apple App Store via iTunes Search API."""
    url = f"https://itunes.apple.com/lookup?bundleId={bundle_id}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data["resultCount"] > 0:
            return data["results"][0].get("version")
    except Exception as e:
        print(f"Error fetching iOS version: {e}")
    return None

def get_android_version(package_id: str) -> Optional[str]:
    """Fetch the latest version from Google Play Store. 
    Note: This is a best-effort scrape as Play Store doesn't have a simple public version API.
    """
    url = f"https://play.google.com/store/apps/details?id={package_id}"
    try:
        response = requests.get(url, timeout=10)
        # Play Store HTML often contains the version in a specific pattern
        # This regex is a common heuristic but may break if Google updates their UI.
        match = re.search(r'\[\[\["([\d\.]+)"\]', response.text)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Error fetching Android version: {e}")
    return None

def main():
    bundle_id = "com.ahoy.app"
    local_v = get_local_version()
    
    print(f"--- Ahoy Store Update Checker ---")
    print(f"Local App Version: {local_v}")
    print(f"Checking stores for {bundle_id}...")
    
    ios_v = get_ios_version(bundle_id)
    android_v = get_android_version(bundle_id)
    
    print(f"iOS (App Store):    {ios_v or 'Not found (likely not published)'}")
    print(f"Android (Play Store): {android_v or 'Not found (likely not published)'}")
    
    if ios_v and ios_v != local_v:
        print(f"\n[!] Update available on iOS App Store: {ios_v}")
    
    if android_v and android_v != local_v:
        print(f"\n[!] Update available on Google Play Store: android_v")
        
    if not ios_v and not android_v:
        print("\nNote: App might not be public in stores yet.")

if __name__ == "__main__":
    main()
