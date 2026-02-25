# Linux Build Guide

This guide explains how to build Ahoy Indie Media for Linux (Ubuntu, Garuda, and other distributions).

---

## Quick Start

### Build with one command:

```bash
bash packaging/linux-build.sh
```

This will:
1. Build the Vue SPA
2. Compile the Electron app
3. Generate AppImage (universal) and DEB (Ubuntu/Debian) packages
4. Display installation instructions

---

## Output Files

After building, you'll find packages in `dist-electron/`:

- **`Ahoy Indie Media*.AppImage`** — Universal Linux package (works on any Linux distro)
- **`ahoy-indie-media*.deb`** — Ubuntu/Debian package

---

## Installation

### Option 1: AppImage (Recommended - No Installation)

Works on **any** Linux distribution (Ubuntu, Garuda, Fedora, etc.):

```bash
chmod +x dist-electron/Ahoy\ Indie\ Media*.AppImage
./dist-electron/Ahoy\ Indie\ Media*.AppImage
```

The AppImage will run directly without installation. You can also:
- Create a launcher: Copy to `~/.local/bin/` for easy access
- Make it a desktop shortcut: Right-click → Properties → Make executable

### Option 2: DEB Package (Ubuntu/Debian-based, like Garuda)

For Ubuntu, Linux Mint, Garuda, and other Debian-based distros:

```bash
sudo apt install ./dist-electron/ahoy-indie-media*.deb
```

Then launch from:
- Applications menu (search "Ahoy")
- Terminal: `ahoy-indie-media`

### Option 3: Manual NPM Build

If you want more control:

```bash
npm run electron:build:linux
```

---

## Building for Garuda Linux

Garuda is Arch-based but uses pacman. The simplest approach:

1. **Use AppImage** (recommended):
   ```bash
   bash packaging/linux-build.sh
   ./dist-electron/Ahoy\ Indie\ Media*.AppImage
   ```

2. **Or install via DEB** (Garuda can install DEB files):
   ```bash
   sudo pacman -S debtap  # one-time install
   debtap dist-electron/ahoy-indie-media*.deb
   sudo pacman -U ahoy-indie-media*.pkg.tar.zst
   ```

3. **Or use AppImage as shortcut**:
   ```bash
   mkdir -p ~/.local/bin
   cp dist-electron/Ahoy\ Indie\ Media*.AppImage ~/.local/bin/ahoy-indie-media
   chmod +x ~/.local/bin/ahoy-indie-media
   ahoy-indie-media  # run from anywhere
   ```

---

## Architecture Support

Builds include both:
- **x64** (Intel/AMD 64-bit) — Standard for most machines
- **arm64** (ARM 64-bit) — For Raspberry Pi 4+, Apple Silicon via Parallels, etc.

---

## Dependencies

The DEB package automatically installs required libraries:
- `gconf2`, `gconf-service` — Configuration
- `libnotify4` — Notifications
- `libappindicator1` — System tray integration
- `libxss1`, `libxtst6` — Input handling

---

## Troubleshooting

**AppImage won't run:**
```bash
chmod +x ./Ahoy\ Indie\ Media*.AppImage
# Then run it again
```

**DEB installation fails:**
```bash
sudo apt install -f  # Fix missing dependencies
sudo apt install ./ahoy-indie-media*.deb
```

**Need to rebuild:**
```bash
rm -rf dist-electron spa-dist
bash packaging/linux-build.sh
```

**Build is slow:**
First build takes longer (~5-10 min). Subsequent builds are faster due to caching.

---

## CI/CD Integration

For automated Linux builds in GitHub Actions, you can use the same script:

```yaml
- name: Build Linux packages
  run: bash packaging/linux-build.sh
```

---

## What's Inside

Each package includes:
- Electron app wrapper (Chromium-based)
- Flask backend (Python)
- Vue SPA frontend
- Database (SQLite for offline support)
- All necessary assets and data

The app runs as a standalone desktop application with no external dependencies (except standard Linux libraries).

---

## Icons & Branding

Icons are located in `packaging/icons/`:
- `ahoy.icns` — macOS
- `ahoy.ico` — Windows
- Linux uses generic app icon (can be customized in package.json)

To update the Linux icon:
1. Create a PNG file: `packaging/icons/ahoy-512.png` (512x512)
2. Rebuild: `bash packaging/linux-build.sh`

---

## Further Reading

- [Electron Builder Linux docs](https://www.electron.build/linux)
- [AppImage docs](https://appimage.org/)
- [Debian packaging guide](https://wiki.debian.org/DebianPackaging)
