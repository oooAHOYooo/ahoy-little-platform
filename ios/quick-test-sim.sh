#!/bin/bash
# Quick test on iOS Simulator - Using Capacitor CLI (easier than xcodebuild)
set -e

echo "🍎 Testing Ahoy on iOS Simulator..."

# Sync assets
echo "📦 Syncing web assets..."
cd ..
npx cap sync ios

# The easiest way: let Capacitor open Xcode, then you build from there
echo ""
echo "✅ Synced! Now you have 2 options:"
echo ""
echo "Option 1 (Easiest - uses Xcode GUI):"
echo "  npx cap run ios"
echo "  → This opens Xcode and runs automatically"
echo ""
echo "Option 2 (Pure terminal - requires manual Xcode build):"
echo "  1. Open Xcode: open ios/App/App.xcworkspace"
echo "  2. Select simulator: iPhone 16 (top toolbar)"
echo "  3. Press Cmd+R to build and run"
echo ""
echo "Want me to open Xcode for you? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "🚀 Opening Xcode..."
    open ios/App/App.xcworkspace
    echo ""
    echo "In Xcode:"
    echo "  1. Select 'iPhone 16' from the device dropdown (top left)"
    echo "  2. Press ▶️ or Cmd+R to run"
    echo ""
fi
