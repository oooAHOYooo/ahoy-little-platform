# How to know if you have the Android SDK and how to install it (terminal)

---

## 1. How to know if you have the Android SDK

Run these in your terminal:

```bash
# Is ANDROID_HOME set and does the folder exist?
echo $ANDROID_HOME
test -d "$ANDROID_HOME" && echo "SDK directory exists" || echo "SDK directory MISSING"

# Can you run the SDK tools? (need cmdline-tools installed)
which adb
which sdkmanager
```

- **You have a working SDK** if:
  - `ANDROID_HOME` is set (e.g. `/Users/ag/Library/Android/sdk` on macOS),
  - That path exists and contains folders like `platform-tools`, `platforms`, and optionally `cmdline-tools` or `build-tools`,
  - And `adb` is on your PATH (often `$ANDROID_HOME/platform-tools/adb`).

- **You do not have a working SDK** if:
  - `ANDROID_HOME` is unset or points to a path that doesn’t exist,
  - Or `adb` / `sdkmanager` are not found.

**On your machine:** `ANDROID_HOME` is set to `/Users/ag/Library/Android/sdk` but that directory does not exist, and `adb`/`sdkmanager` are not found — so the SDK is not installed yet.

---

## 2. Install the latest Android SDK from the terminal

You have two main options.

---

### Option A: Android Studio (easiest, includes SDK)

Installing Android Studio also gives you the SDK (installed on first launch). From the terminal:

**macOS (Homebrew):**

```bash
brew install --cask android-studio
```

Then:

1. Open **Android Studio** (from Applications or `open -a "Android Studio"`).
2. Go through the first-run setup; when it offers to install the **Android SDK**, accept (it will install to `~/Library/Android/sdk` by default).
3. After setup, quit Android Studio.
4. Set your shell to use the SDK (add to `~/.zshrc`):

   ```bash
   export ANDROID_HOME=$HOME/Library/Android/sdk
   export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin
   ```

5. Reload your shell: `source ~/.zshrc`.
6. Check: `adb version` and `sdkmanager --list` (if cmdline-tools were installed).

**If you only use the IDE:** You can build/run the Android project from Android Studio without putting `adb`/`sdkmanager` in PATH; the IDE uses the SDK it installed.

---

### Option B: One script from terminal (this repo)

From the repo root:

```bash
./packaging/install-android-sdk-terminal.sh
```

This downloads the official Android command-line tools and installs `platform-tools`, `platforms;android-33`, and `build-tools;33.0.2` to `~/Library/Android/sdk`. **Requires JDK 17.** If you see "This tool requires JDK 17", install and select JDK 17 then re-run:

```bash
brew install openjdk@17
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
./packaging/install-android-sdk-terminal.sh
```

Then add to `~/.zshrc`:

```bash
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin
```

---

### Option C: Command-line tools only (manual)

Minimal SDK install from the terminal (no Android Studio).

**macOS (Intel or Apple Silicon):**

1. Create the SDK directory:

   ```bash
   mkdir -p $HOME/Library/Android/sdk
   cd $HOME/Library/Android/sdk
   ```

2. Download the latest **command line tools** from:
   - https://developer.android.com/studio#command-tools  
   - Pick “Command line tools only” for your OS (e.g. “Mac”).
   - Or direct (check the page for the latest version and URL):

   ```bash
   cd $HOME/Library/Android/sdk
   # Example (replace with latest URL from the page above):
   curl -o cmdline-tools.zip https://dl.google.com/android/repository/commandlinetools-mac-11076708_latest.zip
   unzip -q cmdline-tools.zip
   mkdir -p cmdline-tools/latest
   mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true
   # Clean up so structure is cmdline-tools/latest/...
   rm -f cmdline-tools.zip
   ```

3. Accept licenses and install platform + build-tools:

   ```bash
   export ANDROID_HOME=$HOME/Library/Android/sdk
   export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
   sdkmanager --sdk_root=$ANDROID_HOME --install "platform-tools" "platforms;android-33" "build-tools;33.0.2"
   yes | sdkmanager --sdk_root=$ANDROID_HOME --licenses
   ```

4. Add to `~/.zshrc`:

   ```bash
   export ANDROID_HOME=$HOME/Library/Android/sdk
   export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin
   ```

5. Reload: `source ~/.zshrc`. Then check: `adb version`, `sdkmanager --list`.

---

## 3. After installing: use the SDK with this project

- **Building from terminal (this repo):**

  ```bash
  export ANDROID_HOME=$HOME/Library/Android/sdk   # if not already set
  cd /path/to/ahoy-little-platform
  npx cap sync android
  cd android && ./gradlew bundleRelease
  ```

- **Building from Android Studio:**  
  Run `npx cap sync android` then `npx cap open android`; Android Studio will use the SDK it installed (or the one at `ANDROID_HOME` if set).

---

## 4. Quick reference

| Check / goal              | Command |
|---------------------------|--------|
| Do I have the SDK?        | `test -d "$ANDROID_HOME" && echo "yes" \|\| echo "no"` |
| Is `adb` available?      | `which adb` |
| Install SDK (easy, with IDE) | `brew install --cask android-studio` then run it once and install SDK |
| Install SDK (CLI only)    | Create `~/Library/Android/sdk`, download cmdline-tools, run `sdkmanager --install ...` and set `ANDROID_HOME` + PATH |

Once `ANDROID_HOME` points to a real SDK directory and (if you use the terminal) `adb`/`sdkmanager` are on your PATH, you have the Android SDK installed and can install the latest components with `sdkmanager --install <package>`.
