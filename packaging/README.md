# Packaging Directory

This directory contains all scripts and configuration files for building standalone desktop applications.

## Files

- **`ahoy.spec`** - PyInstaller specification file (handles both macOS and Windows)
- **`macos-build.sh`** - macOS build script (creates .app bundle)
- **`make_dmg.sh`** - macOS DMG creation script (creates installer)
- **`windows-build.sh`** - Windows build script (creates .exe)
- **`windows-installer.nsi`** - NSIS installer script (creates Windows Setup.exe)
- **`build-all.sh`** - Master build script (auto-detects platform)
- **`DESKTOP_BUILD_GUIDE.md`** - Comprehensive build documentation
- **`icons/`** - Application icons (ahoy.icns, ahoy.ico)

## Quick Build

### macOS
```bash
./build-all.sh
```

### Windows
```bash
./windows-build.sh
```

## Documentation

See `DESKTOP_BUILD_GUIDE.md` for complete instructions.

