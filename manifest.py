#!/usr/bin/env python3
import sys
import argparse
from scripts.build_merch_json import build_merch_json

def main():
    parser = argparse.ArgumentParser(description="Ahoy Platform Manifest Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Merch command
    merch_parser = subparsers.add_parser("merch", help="Build merch products from images")

    args = parser.parse_args()

    if args.command == "merch":
        print("🛍️  Building merch manifest...")
        build_merch_json()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()


