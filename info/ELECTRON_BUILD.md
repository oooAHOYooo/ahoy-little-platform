# 🚀 Electron Build Guide for macOS

## Overview

This project now supports building macOS desktop apps using **Electron** in addition to the existing PyInstaller approach. Electron provides better cross-platform support and a more native macOS experience.

## 🎯 Why Electron?

- ✅ **Better macOS integration**: Native look and feel
- ✅ **Cross-platform**: Same codebase for macOS, Windows, Linux
- ✅ **Modern**: Uses web technologies you're already familiar with
- ✅ **Easier distribution**: Better app signing and notarization support
- ✅ **No Python runtime bundled**: Uses system Python (or can bundle later)

## 📋 Prerequisites

### Required
- **Node.js** 16+ and npm (check: `node --version`)
- **Python 3** with pip (check: `python3 --version`)
- **macOS** 10.13 or later
- **Xcode Command Line Tools**: `xcode-select --install`

### Python Dependencies
```bash
pip3 install -r requirements.txt
```

### Node.js Dependencies
```bash
npm install
```

## 🚀 Quick Build

### Option 1: Using the build script (Recommended)
```bash
cd packaging
./electron-build-mac.sh
```

### Option 2: Using npm directly
```bash
# Build DMG for macOS
npm run electron:build:mac:dmg

# Build all formats (DMG + ZIP)
npm run electron:build:mac
```

## 📦 Build Output

Builds are placed in `dist-electron/`:
- `Ahoy Indie Media-0.2.0.dmg` - macOS disk image installer
- `Ahoy Indie Media-0.2.0-mac.zip` - ZIP archive (for direct distribution)

## 🔧 Development

### Run in Development Mode
```bash
npm run electron:dev
```

This will:
1. Start the Electron window
2. Launch the Flask server automatically
3. Open DevTools for debugging

### Testing the App
1. Run `npm run electron:dev`
2. The app will automatically start Flask on port 17600
3. Electron window opens with your Flask app loaded

## 📝 How It Works

1. **Electron Main Process** (`electron/main.js`):
   - Spawns Python Flask server via `desktop_main.py`
   - Creates native BrowserWindow
   - Handles app lifecycle (quit, window management)

2. **Flask Server** (`desktop_main.py`):
   - Runs on localhost (default: port 17600)
   - Serves your Flask app as usual
   - Uses local SQLite database in `~/.ahoy-indie-media/`

3. **Electron Window**:
   - Loads `http://127.0.0.1:17600`
   - Provides native macOS window chrome
   - Handles external links (opens in browser)

## 🎨 Customization

### Change App Icon
Replace `packaging/icons/ahoy.icns` with your icon.

### Change Build Settings
Edit `package.json` → `build` section:
- App ID: `com.ahoyindiemedia.desktop`
- Product name: `Ahoy Indie Media`
- DMG settings: window size, layout, etc.

### Change Window Size
Edit `electron/main.js`:
```javascript
mainWindow = new BrowserWindow({
  width: 1200,  // Change these
  height: 800,
  // ...
});
```

## 🔐 Code Signing & Notarization

### Code Signing (Optional but Recommended)
```bash
# Sign the app
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  dist-electron/mac/Ahoy\ Indie\ Media.app

# Notarize (requires Apple Developer account)
xcrun notarytool submit dist-electron/*.dmg \
  --apple-id your@email.com \
  --team-id YOUR_TEAM_ID \
  --password YOUR_APP_SPECIFIC_PASSWORD \
  --wait
```

### Automatic Signing
Set environment variables:
```bash
export CSC_IDENTITY_AUTO_DISCOVERY=true
export APPLE_ID=your@email.com
export APPLE_APP_SPECIFIC_PASSWORD=your-password
export APPLE_TEAM_ID=your-team-id
```

Then build:
```bash
npm run electron:build:mac:dmg
```

## 🐛 Troubleshooting

### "Python not found" error
- Ensure Python 3 is installed: `python3 --version`
- Add Python to PATH if needed

### "Flask server failed to start"
- Check if port 17600 is available: `lsof -i :17600`
- Ensure all Python dependencies are installed: `pip3 install -r requirements.txt`

### Build fails with "ENOENT"
- Run `npm install` to ensure all dependencies are installed
- Check that all files referenced in `package.json` → `build.files` exist

### App opens but shows blank screen
- Check DevTools (Cmd+Option+I) for errors
- Verify Flask server is running: `curl http://127.0.0.1:17600`
- Check Console.app for Python errors

### DMG won't mount/open
- Rebuild: `npm run electron:build:mac:dmg`
- Check disk space
- Verify icon file exists: `packaging/icons/ahoy.icns`

## 📊 Comparison: Electron vs PyInstaller

| Feature | Electron | PyInstaller |
|---------|----------|-------------|
| Bundle Size | ~120MB | ~100MB |
| macOS Integration | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Cross-platform | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Development Experience | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Startup Time | Fast | Fast |
| Python Runtime | System/Bundled | Bundled |
| Distribution | DMG/ZIP | DMG/APP |

## 🔄 Migration from PyInstaller

If you're currently using PyInstaller builds:

1. **Keep both**: You can use both build systems
   - PyInstaller: `./packaging/macos-build.sh`
   - Electron: `./packaging/electron-build-mac.sh`

2. **Gradual transition**: Test Electron builds alongside PyInstaller

3. **Same backend**: Both use `desktop_main.py` for Flask server

## 📚 Additional Resources

- [Electron Documentation](https://www.electronjs.org/docs)
- [electron-builder Documentation](https://www.electron.build/)
- [macOS Code Signing Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)

## 🎉 Next Steps

1. **Build your first Electron app**: `./packaging/electron-build-mac.sh`
2. **Test the DMG**: Open and install on a test Mac
3. **Customize**: Adjust icons, window size, menu items
4. **Sign & distribute**: Set up code signing for production builds

Happy building! 🚀

