# Start Scripts for Ahoy Indie Media

## Quick Start

Choose the appropriate script for your operating system:

### macOS / Linux
```bash
python start.py
```
or
```bash
./start.py
```

### Windows
```cmd
start.bat
```

### Alternative Shell Script (Unix/Linux/macOS)
```bash
./start_browser.sh
```

## What These Scripts Do

All scripts will:
1. ✅ Start the Flask application on http://localhost:5000
2. ✅ Wait 2-3 seconds for the server to initialize
3. ✅ Automatically open your default browser
4. ✅ Show the Ahoy Indie Media homepage

## Features

- **Auto-opens browser** - No need to manually navigate to the URL
- **Cross-platform** - Works on macOS, Linux, and Windows
- **Colored output** - Easy to read status messages
- **Error handling** - Graceful shutdown with Ctrl+C

## Port Configuration

Default port is **5000**. To use a different port:

```bash
PORT=3000 python start.py
```

## Stopping the Server

Press **Ctrl+C** in the terminal where the server is running.

## Troubleshooting

### Port Already in Use
If you get an error that port 5000 is already in use:
1. Either stop the other application using that port
2. Or use a different port: `PORT=5001 python start.py`

### Browser Not Opening
The scripts attempt to automatically open the browser, but if it doesn't work:
- Manually navigate to: http://localhost:5000

### Python Not Found
Make sure Python 3.11+ is installed and in your PATH:
```bash
python --version
```

## Files

- `start.py` - Python start script (cross-platform, recommended)
- `start.bat` - Windows batch file
- `start_browser.sh` - Bash script for Unix systems


