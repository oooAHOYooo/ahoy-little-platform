# Archive Directory

This directory contains files that have been moved from the active codebase during repository cleanup.

## Purpose

These files are preserved for historical reference but are no longer part of the active codebase. They may:
- Reference outdated patterns or configurations
- Be redundant with other files
- Contain debug/test data
- Be superseded by newer implementations

## Files Archived

### Entry Point Scripts
- `start.py` - Redundant production startup script
- `start.bat` - Windows-specific startup script  
- `start_browser.sh` - Shell script for starting app and opening browser

### Documentation
- `DEPLOYMENT.md` - Basic deployment guide (consolidated into main README)
- `PRODUCTION_DEPLOYMENT.md` - Production deployment guide (consolidated into main README)
- `RENDER_DEPLOYMENT_CHECKLIST.md` - Deployment checklist (integrated into main README)
- `RENDER_FIX_GUIDE.md` - Historical Render deployment fix guide
- `GPT_COLLABORATION_SUMMARY.md` - Historical collaboration notes

### Build Configuration
- `AhoyIndieMedia.spec` - Duplicate PyInstaller spec file (canonical version is `packaging/ahoy.spec`)

### Debug/Development Files
- `cookies.txt` - Session cookie file from browser testing
- `debug_config.json` - Outdated debug configuration snapshot
- `debug_hero.html` - Standalone HTML file for debugging hero carousel

### Templates
- `bookmark_test.html` - Test template for bookmark functionality (route removed)
- `downloads_simple.html` - Simple version of downloads page (replaced by `downloads.html`)

### Data Files
- `products.json` - Duplicate products file from `static/data/` (canonical version is `data/products.json`)

## Migration Notes

- The `/bookmark-test` route in `app.py` has been removed
- `themes.js` now uses `/api/products` endpoint instead of `/static/data/products.json`
- All deployment information has been consolidated into the main `README.md`

## Date Archived

November 2, 2024

