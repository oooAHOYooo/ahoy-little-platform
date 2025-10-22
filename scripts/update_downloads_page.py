#!/usr/bin/env python3
"""
Downloads page updater for Ahoy Indie Media
Fetches latest release assets and updates downloads template
"""

import os
import sys
import json
import re
import urllib.request
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any


def fetch_latest_release(repo: str, token: str = None) -> Dict[str, Any]:
    """Fetch latest release data from GitHub API"""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AhoyIndieMedia-DownloadsUpdater"
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    request = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.HTTPError as e:
        print(f"Error fetching release: {e}")
        sys.exit(1)


def parse_checksums(checksums_content: str) -> Dict[str, str]:
    """Parse SHA256SUMS.txt content into filename -> checksum mapping"""
    checksums = {}
    for line in checksums_content.strip().split('\n'):
        if line.strip():
            parts = line.strip().split()
            if len(parts) >= 2:
                checksum = parts[0]
                filename = parts[1]
                checksums[filename] = checksum
    return checksums


def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def render_download_rows(assets: List[Dict[str, Any]], checksums: Dict[str, str], include_apk: bool = False) -> str:
    """Render HTML table rows for download assets"""
    rows = []
    
    # Sort assets by platform preference
    platform_order = {"macOS": 0, "Windows": 1, "Linux": 2, "Android": 3}
    
    def sort_key(asset):
        name = asset["name"].lower()
        for platform, order in platform_order.items():
            if platform.lower() in name:
                return (order, name)
        return (999, name)
    
    # Filter assets based on include_apk flag
    filtered_assets = []
    for asset in assets:
        name = asset["name"].lower()
        if any(platform in name for platform in ["macos", "windows", "linux"]):
            filtered_assets.append(asset)
        elif "android" in name and include_apk:
            filtered_assets.append(asset)
    
    sorted_assets = sorted(filtered_assets, key=sort_key)
    
    # Limit to 3 desktop assets + 1 Android if enabled
    max_assets = 4 if include_apk else 3
    for asset in sorted_assets[:max_assets]:
        filename = asset["name"]
        size_mb = asset["size"] / (1024 * 1024)
        checksum = checksums.get(filename, "N/A")
        
        # Determine platform and icon
        platform = "Desktop"
        icon = "💻"
        if "macos" in filename.lower():
            platform = "macOS"
            icon = "🍎"
        elif "windows" in filename.lower():
            platform = "Windows"
            icon = "🪟"
        elif "linux" in filename.lower():
            platform = "Linux"
            icon = "🐧"
        elif "android" in filename.lower():
            platform = "Android (APK)"
            icon = "🤖"
        
        # Create download link
        download_url = asset["browser_download_url"]
        
        row = f"""
        <tr>
            <td>{icon} {platform}</td>
            <td><a href="{download_url}" class="download-link">{filename}</a></td>
            <td>{size_mb:.1f} MB</td>
            <td><code class="checksum">{checksum[:16]}...</code></td>
        </tr>"""
        rows.append(row)
    
    return "\n".join(rows)


def update_downloads_template(html_content: str) -> None:
    """Update downloads template with new content"""
    template_path = Path("templates/downloads.html")
    
    if not template_path.exists():
        # Create basic template if it doesn't exist
        template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Downloads - Ahoy Indie Media</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px; }
        table { border-collapse: collapse; width: 100%; max-width: 800px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f5f5f5; }
        .download-link { color: #007AFF; text-decoration: none; }
        .download-link:hover { text-decoration: underline; }
        .checksum { font-family: monospace; background: #f5f5f5; padding: 2px 4px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>Ahoy Indie Media - Downloads</h1>
    <p>Download the desktop app for your platform:</p>
    
    <table>
        <thead>
            <tr>
                <th>Platform</th>
                <th>File</th>
                <th>Size</th>
                <th>SHA256</th>
            </tr>
        </thead>
        <tbody>
            <!-- Downloads will be inserted here -->
        </tbody>
    </table>
    
    <p><em>Last updated: {{ timestamp }}</em></p>
</body>
</html>"""
        template_path.write_text(template_content)
    
    # Replace the downloads section
    updated_content = re.sub(
        r'<tbody>.*?</tbody>',
        f'<tbody>\n{html_content}\n        </tbody>',
        template_path.read_text(),
        flags=re.DOTALL
    )
    
    template_path.write_text(updated_content)


def main():
    """Main function"""
    repo = os.getenv("GITHUB_REPOSITORY", "agworkywork/ahoy-little-platform")
    token = os.getenv("GITHUB_TOKEN")
    include_apk = os.getenv("INCLUDE_APK", "false").lower() == "true"
    
    print(f"Fetching latest release for {repo}")
    if include_apk:
        print("Android APK inclusion enabled")
    
    # Fetch release data
    release_data = fetch_latest_release(repo, token)
    
    # Get assets and checksums
    assets = release_data.get("assets", [])
    checksums = {}
    
    # Find and parse SHA256SUMS.txt
    for asset in assets:
        if "SHA256SUMS" in asset["name"]:
            download_url = asset["browser_download_url"]
            try:
                with urllib.request.urlopen(download_url) as response:
                    checksums_content = response.read().decode()
                    checksums = parse_checksums(checksums_content)
                    break
            except Exception as e:
                print(f"Warning: Could not fetch checksums: {e}")
    
    # Filter non-checksum assets
    download_assets = [asset for asset in assets if "SHA256SUMS" not in asset["name"]]
    
    if not download_assets:
        print("No download assets found")
        sys.exit(1)
    
    # Render HTML rows
    html_rows = render_download_rows(download_assets, checksums, include_apk)
    
    # Update template
    try:
        update_downloads_template(html_rows)
        print("Downloads template updated successfully")
    except Exception as e:
        print(f"Error updating template: {e}")
        sys.exit(1)
    
    # If running in CI with write permissions, commit the change
    if os.getenv("CI") and token and os.getenv("GITHUB_ACTIONS"):
        print("Running in CI - attempting to commit changes")
        # This would require additional git setup in the workflow
        print("Note: Auto-commit requires additional workflow configuration")


if __name__ == "__main__":
    main()
