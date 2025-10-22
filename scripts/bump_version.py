#!/usr/bin/env python3
"""
Version bumping utility for Ahoy Indie Media
Updates ahoy/version.py with semantic versioning
"""

import argparse
import re
import sys
from pathlib import Path


def parse_version(version_str: str) -> tuple[int, int, int]:
    """Parse semantic version string into (major, minor, patch) tuple"""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")
    return tuple(map(int, match.groups()))


def format_version(major: int, minor: int, patch: int) -> str:
    """Format version tuple into semantic version string"""
    return f"{major}.{minor}.{patch}"


def bump_version(current_version: str, bump_type: str) -> str:
    """Bump version based on type (major, minor, patch)"""
    major, minor, patch = parse_version(current_version)
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return format_version(major, minor, patch)


def update_version_file(new_version: str) -> None:
    """Update ahoy/version.py with new version"""
    version_file = Path("ahoy/version.py")
    
    if not version_file.exists():
        print("Error: ahoy/version.py not found")
        sys.exit(1)
    
    # Read current content
    content = version_file.read_text()
    
    # Replace version line
    new_content = re.sub(
        r'__version__ = "[^"]*"',
        f'__version__ = "{new_version}"',
        content
    )
    
    # Write back
    version_file.write_text(new_content)
    print(f"Updated version to {new_version}")


def main():
    """Main version bump function"""
    parser = argparse.ArgumentParser(
        description="Bump version in ahoy/version.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/bump_version.py              # Bump patch version (0.1.0 -> 0.1.1)
  python scripts/bump_version.py --minor     # Bump minor version (0.1.0 -> 0.2.0)
  python scripts/bump_version.py --major     # Bump major version (0.1.0 -> 1.0.0)
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--patch", 
        action="store_const", 
        const="patch", 
        dest="bump_type",
        help="Bump patch version (default)"
    )
    group.add_argument(
        "--minor", 
        action="store_const", 
        const="minor", 
        dest="bump_type",
        help="Bump minor version"
    )
    group.add_argument(
        "--major", 
        action="store_const", 
        const="major", 
        dest="bump_type",
        help="Bump major version"
    )
    
    parser.set_defaults(bump_type="patch")
    
    args = parser.parse_args()
    
    # Read current version
    try:
        from ahoy.version import __version__
        current_version = __version__
    except ImportError:
        print("Error: Could not import current version from ahoy.version")
        sys.exit(1)
    
    # Calculate new version
    try:
        new_version = bump_version(current_version, args.bump_type)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Update version file
    try:
        update_version_file(new_version)
    except Exception as e:
        print(f"Error updating version file: {e}")
        sys.exit(1)
    
    print(f"Version bumped: {current_version} -> {new_version}")


if __name__ == "__main__":
    main()
