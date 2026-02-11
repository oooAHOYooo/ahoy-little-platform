# Desktop App Build Guide

This guide explains how to build standalone desktop applications for macOS and Windows with proper installers.

## 🎯 Overview

**Electron is the primary distribution method** for desktop builds. PyInstaller is kept for optional offline/legacy builds.

### Electron (primary)
- **Electron** + **electron-builder**: macOS DMG, Windows installer, Linux.
- Runs the bundled Flask app in a native window; DMG is linked to `/downloads` after build.
- **Quick build:** `./packaging/electron-build-mac.sh` (then open the app or install from DMG).

### PyInstaller (optional)
- **PyInstaller** + **PyWebview**: Single-binary style; more packaging quirks (icons, deps).
- Use only if you need a non-Electron path or hit Electron limits.

## 🚀 Quick Start

### macOS (Electron — recommended)
```bash
./packaging/electron-build-mac.sh
```
Output: `dist-electron/*.dmg` and `dist-electron/mac/*.app`; DMG is also copied to `dist/` for the /downloads page.

### macOS (PyInstaller)
```bash
./packaging/build-all.sh
```
Output: `dist/AhoyIndieMedia.app` and `dist/AhoyIndieMedia.dmg`

## 📋 Prerequisites

### All Platforms
```bash
pip install -r requirements.txt pyinstaller pywebview
```

### macOS
- macOS 10.13 or later
- Xcode Command Line Tools: `xcode-select --install`
- `hdiutil` (built-in, used for DMG creation)

### Windows
- Windows 10/11
- **NSIS** (for installer creation):
  - Download from: https://nsis.sourceforge.io/
  - Install to default location: `C:\Program Files (x86)\NSIS\`
  - Or add to PATH

## 🚀 Quick Build

### macOS (Electron)
```bash
./packaging/electron-build-mac.sh
```
Builds the `.app`, `.dmg`, and `.zip`; copies DMG and ZIP to `dist/` for /downloads. Then run: `open dist-electron/mac/Ahoy\ Indie\ Media.app` or install from the DMG.

### Publish so others can download (app.ahoy.ooo/downloads)
To make the zip and DMG available at **https://app.ahoy.ooo/downloads**, create a GitHub release and upload the assets:

1. Install [GitHub CLI](https://cli.github.com/): `brew install gh` then `gh auth login`
2. Build and create release (uploads zip + DMG to GitHub):
   ```bash
   ./packaging/release-desktop.sh --build
   ```
   Or upload existing build: `./packaging/release-desktop.sh`
3. The site’s /downloads page pulls the latest release from GitHub, so the new assets will appear there automatically.

### macOS (PyInstaller)
```bash
./packaging/build-all.sh
```
Output: `dist/AhoyIndieMedia.app` and `dist/AhoyIndieMedia.dmg`

### Windows
```bash
cd packaging
./windows-build.sh
```

This will:
1. Build the Windows `.exe` executable
2. Create an installer EXE (if NSIS is installed)

Output: `dist/AhoyIndieMedia.exe` and `dist/Ahoy Indie Media-Setup.exe`

### Manual Build Steps

#### macOS
```bash
# 1. Build app bundle
./packaging/macos-build.sh

# 2. Create DMG installer
./packaging/make_dmg.sh
```

#### Windows
```bash
# 1. Build executable
./packaging/windows-build.sh

# 2. Create installer (if NSIS installed)
makensis packaging/windows-installer.nsi
```

## 📦 Build Output

### macOS
- **`AhoyIndieMedia.app`**: Application bundle (can be run directly)
- **`AhoyIndieMedia.dmg`**: Disk image installer (drag app to Applications folder)

### Windows
- **`AhoyIndieMedia.exe`**: Standalone executable (can be run directly)
- **`Ahoy Indie Media-Setup.exe`**: NSIS installer (installer with Start Menu shortcuts)

## 🔧 Configuration

### Version Information
Version is automatically read from `ahoy/version.py`:
```python
__version__ = "0.2.0"
```

### Icons
Icons are located in `packaging/icons/`:
- `ahoy.icns` - macOS icon
- `ahoy.ico` - Windows icon

### Build Options

Edit `packaging/ahoy.spec` to customize:
- Included files/data
- Hidden imports
- Compression settings
- Bundle metadata

## 🛠️ Troubleshooting

### macOS

**"No such file or directory" errors:**
- Ensure you're running from project root or packaging directory
- Check that all paths in scripts are correct

**DMG creation fails:**
- Ensure app bundle exists first: `./packaging/macos-build.sh`
- Check disk space (DMG needs ~150MB free)

**App doesn't start:**
- Check Console.app for error messages
- Verify PyWebview is installed: `pip install pywebview`

### Windows

**NSIS not found:**
- Install NSIS from https://nsis.sourceforge.io/
- Or add NSIS to PATH
- Build will succeed but skip installer creation

**PyInstaller errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Try cleaning build: `rm -rf build dist`

**EXE doesn't start:**
- Check Event Viewer for errors
- Run with console enabled (edit spec: `console=True`)

## 📝 Customization

### Change App Name
1. Edit `ahoy/version.py` (version info)
2. Edit `packaging/windows-installer.nsi` (installer name)
3. Edit `packaging/ahoy.spec` (bundle name)

### Add Files to Build
Edit `packaging/ahoy.spec`:
```python
datas=[
    ('../templates', 'templates'),
    ('../static', 'static'),
    ('../data', 'data'),
    ('../ahoy', 'ahoy'),
    ('../your_folder', 'your_folder'),  # Add here
],
```

### Windows Installer Customization
Edit `packaging/windows-installer.nsi`:
- Change installer name/version
- Modify Start Menu folder name
- Add custom registry keys
- Customize installer pages

### macOS DMG Customization
Edit `packaging/make_dmg.sh`:
- Change volume name
- Add background image
- Adjust window size/position

## 🔐 Code Signing (Optional but Recommended)

### macOS
```bash
# Sign the app
codesign --deep --force --verify --verbose \
    --sign "Developer ID Application: Your Name" \
    dist/AhoyIndieMedia.app

# Notarize (requires Apple Developer account)
xcrun notarytool submit dist/AhoyIndieMedia.dmg \
    --apple-id your@email.com \
    --team-id YOUR_TEAM_ID \
    --password YOUR_APP_SPECIFIC_PASSWORD \
    --wait
```

### Windows
Use `signtool.exe` (requires code signing certificate):
```cmd
signtool sign /f certificate.pfx /p password dist/AhoyIndieMedia.exe
```

## 🚀 Distribution

### macOS
1. Create DMG: `./packaging/make_dmg.sh`
2. Test DMG on clean macOS system
3. Upload DMG to your distribution platform
4. Consider notarization for Gatekeeper compatibility

### Windows
1. Create installer: `makensis packaging/windows-installer.nsi`
2. Test installer on clean Windows system
3. Upload installer EXE to your distribution platform
4. Consider code signing for Windows SmartScreen

## 📊 Build Sizes

Typical build sizes:
- **macOS .app**: ~80-120 MB
- **macOS .dmg**: ~50-70 MB (compressed)
- **Windows .exe**: ~80-120 MB
- **Windows Setup.exe**: ~70-90 MB (compressed)

## 🔄 Automated Builds

See `.github/workflows/release-desktop.yml` for GitHub Actions automation.

## 📚 Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/)
- [PyWebview Documentation](https://pywebview.flowrl.com/)
- [NSIS Documentation](https://nsis.sourceforge.io/Docs/)
- [macOS Code Signing Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)

