#!/usr/bin/env python3
"""
Simple build script to create downloadable assets for Ahoy Indie Media
Creates a basic release package without PyInstaller complications
"""

import os
import sys
import shutil
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime

def create_release_package():
    """Create a simple release package"""
    print("🚀 Creating Ahoy Indie Media Release Package")
    
    # Create dist directory
    dist_dir = Path("dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Create source package
    print("📦 Creating source package...")
    source_files = [
        "app.py",
        "desktop_main.py", 
        "requirements.txt",
        "README.md",
        "ahoy/version.py",
        "templates/",
        "static/",
        "blueprints/",
        "utils/",
        "data/",
        "models.py",
        "db.py",
        "config.py"
    ]
    
    # Create source zip
    with zipfile.ZipFile("dist/AhoyIndieMedia-Source.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in source_files:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    for root, dirs, files in os.walk(file_path):
                        for file in files:
                            if not file.startswith('.') and not file.endswith('.pyc'):
                                full_path = os.path.join(root, file)
                                arc_path = os.path.relpath(full_path, ".")
                                try:
                                    zipf.write(full_path, arc_path)
                                except (OSError, FileNotFoundError):
                                    # Skip symlinks and broken files
                                    continue
                else:
                    try:
                        zipf.write(file_path, file_path)
                    except (OSError, FileNotFoundError):
                        # Skip symlinks and broken files
                        continue
    
    # Create desktop launcher script
    print("🖥️ Creating desktop launcher...")
    launcher_content = '''#!/usr/bin/env python3
"""
Ahoy Indie Media Desktop Launcher
Simple launcher that starts the web app locally
"""

import os
import sys
import webbrowser
import subprocess
import time
import threading
from pathlib import Path

def start_server():
    """Start the Flask server"""
    try:
        # Import and start the app
        sys.path.insert(0, str(Path(__file__).parent))
        from app import create_app
        
        app = create_app()
        print("🚀 Starting Ahoy Indie Media...")
        print("📍 Server will be available at: http://localhost:5000")
        print("🌐 Opening browser...")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open("http://localhost:5000")
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Start the server
        app.run(host="0.0.0.0", port=5000, debug=False)
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    start_server()
'''
    
    with open("dist/ahoy_launcher.py", "w") as f:
        f.write(launcher_content)
    
    # Create installation instructions
    install_instructions = '''# Ahoy Indie Media - Installation Instructions

## Quick Start

1. **Install Python 3.11+** (if not already installed)
   - Download from: https://python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   python ahoy_launcher.py
   ```

4. **Open in Browser**
   - The app will automatically open at http://localhost:5000
   - Or manually navigate to http://localhost:5000

## Features

- 🎵 Discover indie music and shows
- 📱 Mobile-friendly web interface
- 💾 Save favorites and create playlists
- 🔍 Search and explore artists
- 📊 Personal listening analytics

## System Requirements

- Python 3.11 or higher
- 100MB free disk space
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Troubleshooting

- If port 5000 is busy, the app will show an error
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that Python is in your system PATH

## Support

- GitHub: https://github.com/oooAHOYooo/ahoy-little-platform
- Issues: https://github.com/oooAHOYooo/ahoy-little-platform/issues

Enjoy discovering indie music! 🎶
'''
    
    with open("dist/INSTALL.txt", "w") as f:
        f.write(install_instructions)
    
    # Create platform-specific packages
    print("📱 Creating platform packages...")
    
    # macOS package
    macos_dir = dist_dir / "AhoyIndieMedia-macOS"
    macos_dir.mkdir()
    
    # Copy files to macOS directory
    shutil.copy("dist/ahoy_launcher.py", macos_dir / "ahoy_launcher.py")
    shutil.copy("dist/INSTALL.txt", macos_dir / "INSTALL.txt")
    shutil.copy("requirements.txt", macos_dir / "requirements.txt")
    shutil.copytree("ahoy", macos_dir / "ahoy")
    shutil.copytree("templates", macos_dir / "templates")
    shutil.copytree("static", macos_dir / "static")
    shutil.copytree("data", macos_dir / "data")
    shutil.copy("app.py", macos_dir / "app.py")
    shutil.copy("config.py", macos_dir / "config.py")
    shutil.copy("db.py", macos_dir / "db.py")
    shutil.copy("models.py", macos_dir / "models.py")
    
    # Create macOS zip
    with zipfile.ZipFile("dist/AhoyIndieMedia-macOS.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(macos_dir):
            for file in files:
                full_path = os.path.join(root, file)
                arc_path = os.path.relpath(full_path, dist_dir)
                zipf.write(full_path, arc_path)
    
    # Windows package (same as macOS for now)
    windows_dir = dist_dir / "AhoyIndieMedia-Windows"
    windows_dir.mkdir()
    
    # Copy files to Windows directory
    shutil.copy("dist/ahoy_launcher.py", windows_dir / "ahoy_launcher.py")
    shutil.copy("dist/INSTALL.txt", windows_dir / "INSTALL.txt")
    shutil.copy("requirements.txt", windows_dir / "requirements.txt")
    shutil.copytree("ahoy", windows_dir / "ahoy")
    shutil.copytree("templates", windows_dir / "templates")
    shutil.copytree("static", windows_dir / "static")
    shutil.copytree("data", windows_dir / "data")
    shutil.copy("app.py", windows_dir / "app.py")
    shutil.copy("config.py", windows_dir / "config.py")
    shutil.copy("db.py", windows_dir / "db.py")
    shutil.copy("models.py", windows_dir / "models.py")
    
    # Create Windows zip
    with zipfile.ZipFile("dist/AhoyIndieMedia-Windows.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(windows_dir):
            for file in files:
                full_path = os.path.join(root, file)
                arc_path = os.path.relpath(full_path, dist_dir)
                zipf.write(full_path, arc_path)
    
    # Linux package
    linux_dir = dist_dir / "AhoyIndieMedia-Linux"
    linux_dir.mkdir()
    
    # Copy files to Linux directory
    shutil.copy("dist/ahoy_launcher.py", linux_dir / "ahoy_launcher.py")
    shutil.copy("dist/INSTALL.txt", linux_dir / "INSTALL.txt")
    shutil.copy("requirements.txt", linux_dir / "requirements.txt")
    shutil.copytree("ahoy", linux_dir / "ahoy")
    shutil.copytree("templates", linux_dir / "templates")
    shutil.copytree("static", linux_dir / "static")
    shutil.copytree("data", linux_dir / "data")
    shutil.copy("app.py", linux_dir / "app.py")
    shutil.copy("config.py", linux_dir / "config.py")
    shutil.copy("db.py", linux_dir / "db.py")
    shutil.copy("models.py", linux_dir / "models.py")
    
    # Create Linux tar.gz
    with tarfile.open("dist/AhoyIndieMedia-Linux.tar.gz", "w:gz") as tar:
        for root, dirs, files in os.walk(linux_dir):
            for file in files:
                full_path = os.path.join(root, file)
                arc_path = os.path.relpath(full_path, dist_dir)
                tar.add(full_path, arc_path)
    
    # Generate build summary
    print("\n📊 Build Summary:")
    print("=" * 50)
    
    total_size = 0
    for file_path in dist_dir.glob("*"):
        if file_path.is_file():
            size = file_path.stat().st_size
            size_mb = size / (1024 * 1024)
            total_size += size
            print(f"✅ {file_path.name}: {size_mb:.1f} MB")
    
    print(f"\n📦 Total package size: {total_size / (1024 * 1024):.1f} MB")
    print(f"📁 Files created in: {dist_dir.absolute()}")
    
    return True

if __name__ == "__main__":
    try:
        create_release_package()
        print("\n🎉 Build completed successfully!")
        print("📤 Ready to upload to GitHub Releases")
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)
