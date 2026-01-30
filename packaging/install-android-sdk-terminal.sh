#!/usr/bin/env bash
# Install Android SDK from terminal (no Android Studio). Uses official command-line tools.
# Run from repo root or any dir. SDK goes to ~/Library/Android/sdk on macOS.

set -e

SDK_ROOT="${HOME}/Library/Android/sdk"
CMD_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-mac-13114758_latest.zip"
CMD_TOOLS_ZIP="${TMPDIR:-/tmp}/cmdline-tools.zip"

echo "Android SDK will be installed to: $SDK_ROOT"
mkdir -p "$SDK_ROOT"
cd "$SDK_ROOT"

if [[ -d "cmdline-tools/latest" && -x "cmdline-tools/latest/bin/sdkmanager" ]]; then
  echo "Command-line tools already present. Skipping download."
else
  echo "Downloading command-line tools..."
  curl -L -o "$CMD_TOOLS_ZIP" "$CMD_TOOLS_URL"
  echo "Unzipping..."
  unzip -q -o "$CMD_TOOLS_ZIP"
  rm -f "$CMD_TOOLS_ZIP"
  # sdkmanager expects cmdline-tools/latest/ (with bin, lib, etc. inside)
  if [[ -d "cmdline-tools" && ! -d "cmdline-tools/latest" ]]; then
    mkdir -p cmdline-tools/latest
    mv cmdline-tools/bin cmdline-tools/lib cmdline-tools/NOTICE.txt cmdline-tools/source.properties cmdline-tools/latest/ 2>/dev/null || true
  fi
  if [[ ! -d "cmdline-tools/latest" ]]; then
    # zip might have created cmdline-tools-X.X.X/ with bin, lib inside
    for d in cmdline-tools-*; do
      if [[ -d "$d" ]]; then
        mkdir -p cmdline-tools/latest
        mv "$d"/* cmdline-tools/latest/ 2>/dev/null || true
        rm -rf "$d"
        break
      fi
    done
  fi
fi

export ANDROID_HOME="$SDK_ROOT"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

echo "Installing platform-tools, platforms;android-33, build-tools;33.0.2..."
echo "(Requires JDK 17. If you see 'requires JDK 17', run: brew install openjdk@17 && export JAVA_HOME=\$(/usr/libexec/java_home -v 17) then run this script again.)"
yes | sdkmanager --sdk_root="$ANDROID_HOME" --install "platform-tools" "platforms;android-33" "build-tools;33.0.2" 2>/dev/null || true
echo "Accepting all licenses..."
yes | sdkmanager --sdk_root="$ANDROID_HOME" --licenses 2>/dev/null || true

echo ""
echo "Done. Add to ~/.zshrc (or ~/.bash_profile):"
echo "  export ANDROID_HOME=\"\$HOME/Library/Android/sdk\""
echo "  export PATH=\"\$PATH:\$ANDROID_HOME/platform-tools:\$ANDROID_HOME/cmdline-tools/latest/bin\""
echo ""
echo "Then run: source ~/.zshrc"
echo "Verify: adb version && sdkmanager --list | head -5"
