#!/usr/bin/env python3
"""Print how many videos/shows are returned by /api/shows (local or Render)."""
import os
import sys

# Optional: hit production instead of local
BASE = os.environ.get('AHOY_API_BASE', 'http://127.0.0.1:5001').rstrip('/')

def main():
    import json
    try:
        import urllib.request
        req = urllib.request.Request(
            f'{BASE}/api/shows',
            headers={'Accept': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode()
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        print("Usage: python scripts/count_shows.py")
        print("  Local (default): ensure app is running, then run this script.")
        print("  Render: AHOY_API_BASE=https://ahoy-indie-media.onrender.com python scripts/count_shows.py")
        sys.exit(1)
    out = json.loads(data)
    shows = out.get('shows') or []
    n = len(shows)
    print(f"API: {BASE}/api/shows")
    print(f"Videos (shows): {n}")
    if n and n <= 20:
        for i, s in enumerate(shows):
            print(f"  {i+1}. {s.get('title', '?')}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
