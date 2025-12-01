# Ahoy Indie Media - Flask Platform

A comprehensive Flask-based media platform for discovering and organizing independent music, shows, and content. Built as a modern replacement for the original Cordova webapp with enhanced user features and playlist management.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Data Structure](#data-structure)
3. [API Reference](#api-reference)
4. [Features](#features)
5. [Project Structure](#project-structure)
6. [Sitemap & Documentation](#sitemap--documentation)
7. [User Management](#user-management)
8. [Customization](#customization)
9. [Deployment](#deployment)
10. [Development](#development)
11. [Security & Performance](#security--performance)
12. [Development Log](#development-log)

---

## 🤖 GPT Assistant: Next Steps

Follow these exact steps when asked to run/build/package or publish downloads.

1) Run the web app (productionish local)

```bash
export FLASK_ENV=production
export SECRET_KEY=$(python - <<'PY'\nimport secrets;print(secrets.token_urlsafe(32))\nPY)
python app.py
```

Then open the printed localhost URL (or http://127.0.0.1:5000 or chosen port). Health checks: `/healthz`, `/readyz`.

2) Run the desktop wrapper (PyWebview)

```bash
export FLASK_ENV=production
export SECRET_KEY=$(python - <<'PY'\nimport secrets;print(secrets.token_urlsafe(32))\nPY)
export PORT=17600
python desktop_main.py
```

3) Build desktop binaries

```bash
python -m pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --onefile --name "Ahoy Indie Media" desktop_main.py
```

Artifacts appear in `dist/`.

4) Publish downloads on the site

```bash
mkdir -p downloads
cp dist/* downloads/
```

Visit `/downloads` to see and download the files.

5) Commit and push

```bash
git add -A
git commit -m "chore: update builds and docs"
git push origin main
```

If push is blocked on macOS: run `sudo xcodebuild -license` once, then push again.

Troubleshooting
- Internal Server Error: check terminal logs; verify `SECRET_KEY` is set; ensure dependencies `pip install -r requirements.txt`.
- Desktop window not opening: `pip install pywebview`; ensure port 17600 is free.
- Downloads page empty: ensure files exist in `downloads/`.

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd ahoy-little-platform
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the application:**
   ```bash
   python run.py
   ```
   Or directly:
   ```bash
   python app.py
   ```

6. **Visit the application:**
   The application will automatically find an available port between 5001-5010 and display the URL (e.g., `http://localhost:5003`)

### Port Management

The application automatically checks for available ports in the range 5001-5010 to avoid conflicts with other services (like macOS AirPlay Receiver on port 5000).

**Check available ports:**
```bash
python scripts/check_ports.py
```

---

## Data Structure

### 📊 Content Data Files
| File | Location | Description | Schema |
|------|----------|-------------|--------|
| `music.json` | `static/data/` | Music tracks | `{id, title, artist, album, duration, url, cover_art}` |
| `shows.json` | `static/data/` | Video shows | `{id, title, host, description, duration, thumbnail, url}` |
| `artists.json` | `static/data/` | Artist profiles | `{id, name, bio, image, social_links, genre}` |

### 👤 User Data Files
| File | Location | Description | Schema |
|------|----------|-------------|--------|
| `users.json` | `data/` | User accounts | `{username, password_hash, email, created_at, profile}` |
| `user_activity.json` | `data/` | User activity | `{username: {likes, bookmarks, history, playlists}}` |
| `playlists.json` | `data/` | User playlists | `{id, name, description, items, created_by, created_at}` |
| `feedback.json` | `data/` | User feedback | `{id, message, type, status, created_at, user}` |

### 🔄 Data Flow
1. **Content Loading**: JSON files loaded into memory on startup
2. **User Activity**: Stored in `data/` directory with thread-safe operations
3. **Real-time Updates**: Changes persisted immediately to disk
4. **Guest Mode**: LocalStorage for temporary data, migrates on account creation

---

## API Reference

### 🎵 Content APIs
| Method | Endpoint | Description | Parameters | Response |
|--------|----------|-------------|------------|----------|
| `GET` | `/api/now-playing` | Discovery feed | None | Array of content items |
| `GET` | `/api/music` | Music library | `?page=1&limit=20` | Paginated music tracks |
| `GET` | `/api/shows` | Shows library | `?category=live` | Array of shows |
| `GET` | `/api/artists` | Artist directory | `?genre=indie` | Array of artists |
| `GET` | `/api/artist/<name>` | Specific artist | `name` (path) | Artist profile + content |
| `GET` | `/api/search` | Universal search | `?q=query&type=all` | Search results |
| `GET` | `/api/daily-playlist` | Daily playlist | None | Curated playlist |

### 👤 User Management APIs
| Method | Endpoint | Description | Parameters | Response |
|--------|----------|-------------|------------|----------|
| `POST` | `/api/auth/login` | User login | `username`, `password` | Success + session cookie |
| `POST` | `/api/auth/register` | User registration | `username`, `password`, `email` | User profile |
| `POST` | `/api/auth/logout` | User logout | None | Success status |
| `GET` | `/api/user/profile` | Get user profile | None | User data |
| `PUT` | `/api/user/profile` | Update profile | `display_name`, `avatar` | Updated profile |

### 💾 Content Management APIs
| Method | Endpoint | Description | Parameters | Response |
|--------|----------|-------------|------------|----------|
| `GET` | `/api/user/playlists` | Get playlists | None | User playlists |
| `POST` | `/api/user/playlists` | Create playlist | `name`, `description` | New playlist |
| `PUT` | `/api/user/playlists/<id>` | Update playlist | `name`, `description` | Updated playlist |
| `DELETE` | `/api/user/playlists/<id>` | Delete playlist | None | Success status |
| `POST` | `/api/user/playlists/<id>/items` | Add to playlist | `content_id`, `content_type` | Success status |
| `DELETE` | `/api/user/playlists/<id>/items` | Remove from playlist | `content_id` | Success status |

### ❤️ Activity APIs
| Method | Endpoint | Description | Parameters | Response |
|--------|----------|-------------|------------|----------|
| `GET` | `/api/user/likes` | Get liked content | None | Liked items |
| `POST` | `/api/user/likes` | Like content | `content_id`, `content_type` | Success status |
| `DELETE` | `/api/user/likes` | Unlike content | `content_id` | Success status |
| `GET` | `/api/user/history` | Get play history | None | Play history |
| `POST` | `/api/user/history` | Add to history | `content_id`, `content_type` | Success status |
| `GET` | `/api/user/recommendations` | Get recommendations | None | Recommended content |

### 💾 Save/Load APIs (Guest & User)
| Method | Endpoint | Description | Parameters | Response |
|--------|----------|-------------|------------|----------|
| `POST` | `/api/saves/save` | Save content | `content_id`, `content_type` | Success status |
| `POST` | `/api/saves/unsave` | Unsave content | `content_id` | Success status |
| `POST` | `/api/saves/check` | Check if saved | `content_id` | Boolean status |
| `GET` | `/api/saves/<type>` | Get saved content | `type` (tracks/shows/artists) | Saved items |

---

## Features

### 🎵 Media Discovery
- **Now Playing Feed**: TikTok-style horizontal discovery with 30-second previews
- **Music Library**: Full music streaming with advanced filtering and search
- **Shows & Videos**: Video content and live shows with categories
- **Artist Profiles**: Detailed artist pages with content and social links

### 🎧 User Experience
- **Playlist Management**: Create, edit, reorder, and share unlimited playlists
- **Collections**: Organize content into themed folders
- **Likes & History**: Track everything users interact with
- **Personalized Recommendations**: AI-driven content suggestions
- **Universal Search**: Search across all content types

### 🎨 Modern Interface
- **Responsive Design**: Mobile-first approach with desktop optimization
- **Dark Theme**: Eye-friendly dark interface
- **Smooth Animations**: Polished user interactions
- **Keyboard Shortcuts**: Power user features

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd ahoy-little-platform
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the application:**
   ```bash
   python run.py
   ```
   Or directly:
   ```bash
   python app.py
   ```

6. **Visit the application:**
   The application will automatically find an available port between 5001-5010 and display the URL (e.g., `http://localhost:5003`)

### Port Management

The application automatically checks for available ports in the range 5001-5010 to avoid conflicts with other services (like macOS AirPlay Receiver on port 5000).

**Check available ports:**
```bash
python scripts/check_ports.py
```

## Sitemap & Documentation

### 🌐 Complete Site Map

#### Main Pages
| Route | Page | Description | Key Features |
|-------|------|-------------|--------------|
| `/` | **Home** | Discovery page with Now Playing feed | • TikTok-style carousel<br>• Weather widget<br>• Daily playlist<br>• Quick actions<br>• Bookmarks widget |
| `/music` | **Music Library** | Browse and play music tracks | • Grid/List view toggle<br>• Search & filtering<br>• Like & bookmark<br>• Add to playlist |
| `/shows` | **Shows & Videos** | Video content and live shows | • Video player<br>• Show categories<br>• Host information<br>• Save & like |
| `/artists` | **Artists Directory** | Browse independent artists | • Artist profiles<br>• Music & shows<br>• Social links<br>• Follow artists |
| `/performances` | **Performances** | Live performance listings | • Event calendar<br>• Venue information<br>• Ticket links |
| `/player` | **Full-Screen Player** | Dedicated media player | • Full-screen playback<br>• Queue management<br>• Playback controls |

#### User Pages
| Route | Page | Description | Key Features |
|-------|------|-------------|--------------|
| `/auth` | **Authentication** | Login and registration | • User login<br>• Account creation<br>• Password reset<br>• Guest mode |
| `/account` | **User Profile** | Account management | • Profile settings<br>• Avatar upload<br>• Statistics<br>• Data migration |
| `/settings` | **App Settings** | Application preferences | • Dark mode toggle<br>• Auto-play settings<br>• Notification preferences |
| `/my-saves` | **My Saves** | Saved content management | • Saved tracks<br>• Saved shows<br>• Playlists<br>• Export/Sync |
| `/bookmarks` | **Bookmarks** | Bookmarked content | • All bookmarks<br>• Filter by type<br>• Quick access |

#### Utility Pages
| Route | Page | Description | Key Features |
|-------|------|-------------|--------------|
| `/sitemap` | **App Structure** | Complete documentation | • Page hierarchy<br>• API reference<br>• Data schemas<br>• Architecture overview |
| `/feedback` | **Feedback** | User feedback system | • Bug reports<br>• Feature requests<br>• User suggestions |
| `/debug` | **Debug Console** | Development tools | • System status<br>• User management<br>• Data viewer<br>• API testing |
| `/admin` | **Admin Panel** | User management | • User list<br>• Account management<br>• System monitoring |
| `/downloads` | **Downloads** | Desktop build downloads | • Simple links to artifacts |

### 📚 Documentation Access
- **In-app**: Settings menu → "App Structure" 
- **Direct URL**: `/sitemap`
- **Mobile**: User menu → "App Structure"
- **Complete Reference**: [SITEMAP.md](./SITEMAP.md)

---

## Project Structure

```
ahoy-little-platform/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── storage.py                      # Thread-safe JSON storage
├── user_manager.py                 # User management utilities
├── extensions.py                   # Flask extensions
├── wsgi.py                        # WSGI entry point
├── desktop_main.py                # Desktop (PyWebview) entrypoint
├── run.py                         # Development runner
├── start.py                       # Production starter
├── requirements.txt               # Python dependencies
├── gunicorn.conf.py              # Gunicorn configuration
├── Procfile                       # Heroku deployment
├── render.yaml                    # Render deployment config
├── README.md                      # This file
├── SITEMAP.md                     # Complete sitemap reference
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore file
│
├── data/                          # User data storage
│   ├── users.json                 # User accounts (created at runtime)
│   ├── user_activity.json         # User activity logs
│   ├── playlists.json             # User playlists
│   └── feedback.json              # User feedback
│
├── static/                        # Static files
│   ├── css/
│   │   ├── main.css              # Main stylesheet
│   │   └── components.css        # Component-specific styles
│   ├── js/
│   │   ├── app.js                # Main JavaScript
│   │   ├── player.js             # Media player logic
│   │   ├── playlist-manager.js   # Playlist management
│   │   ├── bookmarks.js          # Bookmark functionality
│   │   ├── guest-bootstrap.js    # Guest user setup
│   │   └── unified-hero.js       # Hero carousel system
│   ├── img/                      # Images and assets
│   └── data/                     # JSON data files
│       ├── music.json            # Music tracks
│       ├── shows.json            # Video shows
│       └── artists.json          # Artist profiles
│
├── templates/                     # Jinja2 templates
│   ├── base.html                 # Base template
│   ├── home.html                 # Discovery page
│   ├── music.html                # Music library
│   ├── shows.html                # Shows/video content
│   ├── artists.html              # Artist directory
│   ├── player.html               # Full-screen player
│   ├── sitemap.html              # App structure documentation
│   ├── auth.html                 # Authentication
│   ├── account.html              # User profile
│   ├── settings.html             # App settings
│   ├── my_saves.html             # User saves
│   ├── bookmarks.html            # Bookmarks page
│   ├── admin.html                # Admin panel
│   ├── debug.html                # Debug console
│   ├── downloads.html            # Downloads page
│   ├── feedback.html             # Feedback form
│   ├── privacy.html              # Privacy policy
│   ├── security.html             # Security policy
│   ├── terms.html                # Terms of service
│   └── 404.html                  # Error page
│
├── downloads/                     # Published desktop builds (served at /downloads)
└── blueprints/                    # Modular route organization
    ├── __init__.py
    ├── activity.py               # User activity APIs
    ├── auth.py                   # Authentication APIs
    ├── bookmarks.py              # Bookmark management
    └── playlists.py              # Playlist management
```

## User Management

The platform uses a simple file-based user system with:
- **Registration/Login**: Username and password authentication
- **Password Hashing**: SHA-256 password security
- **Session Management**: Flask session-based authentication
- **User Preferences**: Theme, autoplay, and other settings
- **Activity Tracking**: Listening history and user statistics
- **Guest Mode**: LocalStorage for temporary data, migrates on account creation

## Customization

### Adding New Content
1. **Music**: Add tracks to `static/data/music.json`
2. **Shows**: Add shows to `static/data/shows.json`
3. **Artists**: Add artists to `static/data/artists.json`

### Styling
- **Main styles**: Edit `static/css/main.css`
- **Components**: Edit `static/css/components.css`
- **CSS Variables**: Modify the `:root` section for theme colors

### JavaScript
- **App logic**: Edit `static/js/app.js`
- **Player**: Edit `static/js/player.js`
- **Playlists**: Edit `static/js/playlist-manager.js`

## Deployment

### Environment Variables

| Variable | Description | Example Value | Required |
|----------|-------------|---------------|----------|
| `FLASK_ENV` | Application environment | `production` | Yes |
| `SECRET_KEY` | Flask secret key for sessions | `your-secret-key-here` | Yes |
| `DATABASE_URL` | Database connection string | `postgresql+psycopg://user:pass@host:5432/dbname` | Yes |
| `SENTRY_DSN` | Sentry error tracking URL | `https://key@sentry.io/project` | No |
| `RATE_LIMIT_DEFAULT` | Default rate limit | `60 per minute` | No |
| `RATE_LIMIT_AUTH` | Auth endpoint rate limit | `10 per minute` | No |
| `SESSION_COOKIE_SECURE` | Secure session cookies | `True` | No |
| `SESSION_COOKIE_SAMESITE` | SameSite cookie policy | `Lax` | No |
| `PREFERRED_URL_SCHEME` | URL scheme for redirects | `https` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `REQUEST_ID_HEADER` | Request ID header name | `X-Request-ID` | No |

**⚠️ Security Note:** `SECRET_KEY` and `SENTRY_DSN` contain sensitive information and must not be committed to version control.

### Render.com Deployment

1. **Create a new Web Service** in your Render dashboard
2. **Connect your GitHub repository**
3. **Configure environment variables:**
   - Go to Settings → Environment
   - Add each variable from the table above
   - Set `FLASK_ENV=production`
   - Set `LOG_LEVEL=INFO`
   - Set `DATABASE_URL` to your Render Postgres connection string
   - Add `SENTRY_DSN` if using error tracking

4. **Deploy settings:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `./scripts/migrate_and_start.sh`
   - Health Check Path: `/ops/selftest`

### Production Setup

### Stripe Payments (AHOY_ENV)

Set `AHOY_ENV` to select Stripe keys:
- If `AHOY_ENV=development` (or `sandbox`), the app uses test keys.
- Otherwise, it uses live keys.

Required environment variables (DO NOT paste real keys in this repo):
```bash
# Test (development)
export AHOY_ENV=development
export STRIPE_PUBLISHABLE_KEY_TEST="<your_test_publishable_key>"
export STRIPE_SECRET_KEY_TEST="<your_test_secret_key>"
export STRIPE_WEBHOOK_SECRET_TEST="<your_test_webhook_secret>"

# Production (live)
# export AHOY_ENV=production
# export STRIPE_PUBLISHABLE_KEY="<your_live_publishable_key>"
# export STRIPE_SECRET_KEY="<your_live_secret_key>"
# export STRIPE_WEBHOOK_SECRET="<your_live_webhook_secret>"
```

The app reads `AHOY_ENV` to choose between test and live Stripe keys automatically.

1. **Set environment variables:**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret
   ```

2. **Install production server:**
   ```bash
   pip install gunicorn
   ```

3. **Run with Gunicorn:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

4. **Use a reverse proxy** (Nginx recommended) for static files and SSL

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Development

### Dependency check

Check that all production dependencies are properly installed:

```bash
python scripts/check_deps.py
```

### Render Validation

Validate deployment health and functionality:

```bash
# Local validation
python scripts/render_validate.py

# Remote validation (set BASE_URL)
BASE_URL=https://your-app.onrender.com python scripts/render_validate.py
```

The script checks:
- `/healthz` endpoint returns 200
- `/readyz` endpoint returns 200  
- `/_boom` endpoint (if `SENTRY_TEST_ROUTE=true`) returns 500

### Downloads Auto-refresh

The downloads page automatically updates with the latest release assets:

```bash
# Update downloads page manually
python scripts/update_downloads_page.py

# Set GitHub token for API access
export GITHUB_TOKEN=your_token_here
```

**Workflow Requirements:**
- `GITHUB_TOKEN` with `contents:write` permission
- Runs automatically after each release
- Updates `templates/downloads.html` with latest 3 assets

### Desktop Smoke Test

After building desktop apps, verify they work correctly:

**macOS:**
```bash
# Remove quarantine attributes (if needed)
xattr -dr com.apple.quarantine AhoyIndieMedia.app

# Open the app
open AhoyIndieMedia.app

# Or test with production URL
open AhoyIndieMedia.app --args --url=https://your-app.onrender.com
```

**Windows:**
```cmd
# Run with production URL
AhoyIndieMedia.exe --url=https://your-app.onrender.com

# Or run locally (starts Flask server)
AhoyIndieMedia.exe
```

**Linux:**
```bash
# Make executable and run with production URL
chmod +x AhoyIndieMedia
./AhoyIndieMedia --url=https://your-app.onrender.com

# Or run locally
./AhoyIndieMedia
```

**Expected Behavior:**
- Window opens with "Ahoy Indie Media" title
- App loads the specified URL or starts local server
- Media playback works correctly
- Window is resizable with minimum size 1200×800
- App exits cleanly on window close

### Code Signing (Optional)

For production releases, consider code signing to avoid OS security warnings:

**macOS Developer ID:**
- Obtain Developer ID Application certificate (.p12 file)
- Set environment variables in GitHub Actions:
  - `MACOS_CERT_P12`: Base64-encoded .p12 certificate
  - `MACOS_CERT_PWD`: Certificate password
- PyInstaller will automatically sign the .app bundle

**Windows Authenticode:**
- Obtain code signing certificate (.pfx file)
- Set environment variables:
  - `WINDOWS_SIGNING_CERT`: Base64-encoded .pfx certificate
  - `WINDOWS_SIGNING_PWD`: Certificate password
- Use SignTool in the build process

**⚠️ Warning:** Unsigned binaries will trigger OS security prompts and may be blocked by antivirus software. Code signing is recommended for distribution.

### Android Signing

For production Android releases, sign the APK with your keystore:

```bash
# Set environment variables
export ANDROID_KEYSTORE_BASE64="base64_encoded_keystore_content"
export ANDROID_KEY_ALIAS="your_key_alias"
export ANDROID_KEYSTORE_PASSWORD="keystore_password"
export ANDROID_KEY_PASSWORD="key_password"

# Sign the APK
./scripts/sign_apk.sh android/app/build/outputs/apk/release/app-release-unsigned.apk
```

**Environment Variables:**
- `ANDROID_KEYSTORE_BASE64`: Base64-encoded .jks keystore file
- `ANDROID_KEY_ALIAS`: Key alias in the keystore
- `ANDROID_KEYSTORE_PASSWORD`: Keystore password
- `ANDROID_KEY_PASSWORD`: Key password

### Android Device Smoke Test

After building the APK, verify it works correctly on a physical device:

**Pre-installation:**
1. Enable "Install unknown apps" in Android Settings → Apps → Special access → Install unknown apps
2. For Android 13+: Settings → Apps → Special app access → Install unknown apps → [Your browser/ADB]

**Installation:**
```bash
# Install via ADB
adb install AhoyIndieMedia-Android-release.apk

# Or download APK to device and install manually
```

**First Launch Tests:**
1. **Audio Playback:** Tap play on a track, confirm audio continues with screen off
2. **Media Controls:** Use notification controls (Android OS shows controls via Media Session API)
3. **Headset Controls:** Confirm headset buttons play/pause work correctly
4. **Background Audio:** Switch to another app, verify audio continues playing
5. **Lock Screen:** Lock device, verify media controls appear on lock screen

**Expected Behavior:**
- App loads production URL (https://ahoy-indie-media.onrender.com)
- Audio plays without user gesture requirement
- Media session controls work in notifications and lock screen
- Headset buttons control playback
- App continues playing when backgrounded

### iOS Build (Optional)

For iOS builds, additional setup is required:

```bash
# Install iOS platform
npm install @capacitor/ios@5.7.0
npx cap add ios

# Open in Xcode
open ios/App/App.xcworkspace
```

**Xcode Configuration:**
1. Set bundle identifier: `com.ahoy.app`
2. Select development team
3. Enable "Background Modes" capability:
   - Audio, AirPlay, and Picture in Picture
4. Build to device or simulator

**Background Modes Enabled:**
- Audio, AirPlay, and Picture in Picture

### Database and Migrations (User State)

This project uses SQLAlchemy and Alembic for user state. In production, set `DATABASE_URL` (Postgres recommended). Locally, the app defaults to SQLite file `sqlite:///local.db` if no database URL is provided.

On Render, wire the database automatically via `render.yaml`:

### Database Backups

Automated nightly backups are configured via GitHub Actions:

```bash
# Manual backup
./scripts/backup_db.sh

# Environment variables required:
# DATABASE_URL - PostgreSQL connection string
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET (for S3)
# GOOGLE_APPLICATION_CREDENTIALS, GCS_BUCKET (for GCS)
```

**Manual Restore Steps:**
1. Download backup from S3/GCS: `aws s3 cp s3://bucket/backups/ahoy_backup_YYYYMMDD_HHMMSS.sql.gz .`
2. Decompress: `gunzip ahoy_backup_YYYYMMDD_HHMMSS.sql.gz`
3. Restore: `psql $DATABASE_URL < ahoy_backup_YYYYMMDD_HHMMSS.sql`
4. Verify: `psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"`

**Backup Retention:** 30 days (configurable in script)

### Production Readiness Gate

Before launching publicly, run the production readiness check:

```bash
# Run comprehensive health check
python scripts/prod_gate.py

# Set custom base URL
BASE_URL=https://your-domain.com python scripts/prod_gate.py
```

**What it checks:**
- `/healthz` endpoint responds with correct version
- `/readyz` endpoint confirms database connectivity
- Version matches `ahoy/version.py`
- Downloads page shows 3 assets (macOS/Windows/Linux)
- Email service configuration (Resend/SMTP)
- Test email sending capability

**Sample Output:**
```json
{
  "timestamp": "2025-01-22T17:30:00Z",
  "base_url": "https://ahoy-indie-media.onrender.com",
  "overall_status": "PASS",
  "checks": {
    "health_endpoint": {"status": "pass", "version": "0.1.1"},
    "readiness_endpoint": {"status": "pass", "ready": true},
    "version_match": {"status": "pass", "local_version": "0.1.1"},
    "downloads_page": {"status": "pass", "asset_count": 3},
    "email_configuration": {"status": "pass", "can_send_emails": true}
  },
  "summary": {
    "total_checks": 6,
    "passed": 6,
    "warnings": 0,
    "failed": 0
  }
}
```

**Exit Codes:**
- `0`: All checks passed (ready for production)
- `1`: One or more checks failed (not ready)

```yaml
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: ahoy-postgres
      property: connectionString
```

## 🖥️ Desktop Application (Primary Distribution Method)

Ahoy Indie Media is primarily distributed as **standalone desktop applications** for macOS and Windows with proper installers.

### Quick Start - Build Desktop Apps

#### macOS
```bash
cd packaging
./build-all.sh
```
Creates: `dist/AhoyIndieMedia.app` and `dist/AhoyIndieMedia.dmg`

#### Windows
```bash
cd packaging
./windows-build.sh
```
Creates: `dist/AhoyIndieMedia.exe` and `dist/Ahoy Indie Media-Setup.exe` (installer)

### Development Mode

Run the desktop app in development mode:
```bash
python desktop_main.py
```

Or with production URL:
```bash
python desktop_main.py --url https://your-app.onrender.com
```

### Build System

The desktop app uses:
- **PyInstaller**: Packages Python into standalone executables
- **PyWebview**: Native desktop window wrapper
- **NSIS** (Windows): Creates Windows installer EXE
- **DMG** (macOS): Creates macOS disk image installer

### Detailed Build Guide

See **[`packaging/DESKTOP_BUILD_GUIDE.md`](packaging/DESKTOP_BUILD_GUIDE.md)** for:
- Complete build instructions
- Prerequisites and dependencies
- Troubleshooting
- Code signing and distribution
- Customization options

### App Features

- **Standalone**: No Python installation required
- **Local Database**: Uses SQLite stored in `~/.ahoy-indie-media/`
- **Auto Port Selection**: Finds free port automatically (default 17600)
- **Production Ready**: Configured for production use
- **Native UI**: Native desktop window with proper window controls

### Distribution

Desktop apps are the **primary distribution method**. Web app is secondary.

For publishing:
1. Build installers: `./packaging/build-all.sh`
2. Upload to distribution platform (GitHub Releases, your website, etc.)
3. Serve via `/downloads` page (optional)

Then run:

```bash
alembic revision --autogenerate -m "change"
alembic upgrade head
```

On Render, migrations are applied automatically at startup via `scripts/migrate_and_start.sh`.

### Readiness and Debug

- `GET /readyz`: returns 200 when a DB `SELECT 1` succeeds; 500 with details otherwise.
- `/debug`: shows masked DSN summary and a clear warning if `DATABASE_URL` is missing. Keeps live DB counts and error details on failures.

### Operational Self-Test

- `GET /ops/selftest` runs:
  - `SELECT 1`
  - ORM query to count users
  - Reads Alembic current DB revision
  - Returns `{ "ready": true, "alembic": "<rev>", "counts": { "users": N } }` on success; 500 with `{ "ready": false, "detail": "..." }` on failure
  - Recommended Render `healthCheckPath`: `/ops/selftest`

<!-- Removed outdated JWT Auth section; current app uses session-based auth under /api/auth -->


### Adding New Features

1. **New API endpoints**: Add to `app.py`
2. **New templates**: Add to `templates/`
3. **New styles**: Add to `static/css/`
4. **New JavaScript**: Add to `static/js/`

### Database Migration

For production, consider migrating from JSON files to a database:
- **PostgreSQL**: For robust data storage
- **SQLite**: For simple deployments
- **MongoDB**: For document-based storage

## Security & Performance

### 🔒 Security Considerations
- **Password Security**: SHA-256 hashing (consider upgrading to bcrypt for production)
- **Input Validation**: All API inputs validated and sanitized
- **Rate Limiting**: 60/min for likes/bookmarks, 120/min for history
- **Session Security**: Flask session-based authentication with secure cookies
- **File Operations**: Thread-safe JSON storage with atomic operations
- **CORS**: Configured for API access
- **HTTPS**: Use SSL in production

### ⚡ Performance Optimizations
- **Static File Caching**: Configure web server caching
- **API Response Caching**: 5-minute default cache for content APIs
- **Lazy Loading**: For large libraries and images
- **Pagination**: For large datasets (20 items per page)
- **CDN Integration**: For media files and static assets
- **Thread-Safe Storage**: Prevents data corruption during concurrent writes
- **Memory Management**: Efficient JSON loading and caching

## Browser Support

- **Modern Browsers**: Chrome, Firefox, Safari, Edge
- **Mobile**: iOS Safari, Chrome Mobile
- **Features**: ES6+, CSS Grid, Flexbox

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or support:
- **Issues**: Create a GitHub issue
- **Documentation**: Check this README
- **Community**: Join our Discord server

## Development Log

### December 19, 2024 - Major Feature Implementation: Working Likes/Bookmarks & Playlists

**Problem Identified:**
- Like and bookmark features were not working due to missing API contracts
- Frontend buttons were using local state only, not persisting to backend
- Playlist functionality was incomplete with "boards" vs "playlists" terminology confusion
- No reliable REST endpoints for user activity persistence

**Backend Changes:**

1. **Created `storage.py`** - Thread-safe JSON storage module
   - Implements file locking to prevent data corruption during concurrent writes
   - Provides `read_json()` and `write_json()` functions with atomic operations
   - Ensures data integrity across multiple user sessions

2. **Created `blueprints/activity.py`** - New activity management API
   - `GET /api/activity/me` - Retrieve user's likes, bookmarks, and play history
   - `POST /api/activity/like` - Toggle like status for tracks/shows/artists
   - `POST /api/activity/bookmark` - Toggle bookmark status for content
   - `POST /api/activity/played` - Mark content as played (updates history)
   - Uses session-based authentication with proper error handling

3. **Created `blueprints/playlists.py`** - Complete playlist CRUD API
   - `GET /api/playlists` - List all user playlists
   - `POST /api/playlists` - Create new playlist with name/description
   - `PUT /api/playlists/<id>` - Update playlist metadata
   - `DELETE /api/playlists/<id>` - Delete playlist
   - `POST /api/playlists/<id>/items` - Add content to playlist
   - `DELETE /api/playlists/<id>/items` - Remove content from playlist
   - Full CRUD operations with proper validation

4. **Updated `app.py`** - Registered new blueprints
   - Added blueprint imports and registration
   - Integrated with existing session-based authentication
   - Maintains backward compatibility with existing endpoints

**Frontend Changes:**

1. **Updated `static/js/app.js`** - Enhanced with new API integration
   - Added `api()` helper function for consistent API calls
   - Implemented event delegation for like/bookmark buttons
   - Added automatic UI state updates with CSS class toggling
   - Integrated error handling with user notifications

2. **Replaced `static/js/playlist-manager.js`** - Complete rewrite
   - New modular approach with proper API calls
   - Exported functions for playlist management
   - Added form submission handling for playlist creation
   - Integrated with global notification system

3. **Updated HTML Templates** - Added data attributes for API integration
   - **`templates/music.html`**: Added `data-like`, `data-bookmark`, `data-id`, `data-kind` attributes
   - **`templates/shows.html`**: Added same data attributes for show content
   - All like/save buttons now properly wired to backend APIs

**Data Structure Changes:**

1. **New Data Files:**
   - `data/user_activity.json` - Stores user likes, bookmarks, and play history
   - `data/playlists.json` - Stores user playlists and playlist items
   - Both files use thread-safe JSON operations

2. **Removed Legacy Code:**
   - Eliminated all "boards" terminology and replaced with "playlists"
   - Removed unused board-related functions from `user_manager.py`
   - Cleaned up template references to old board system

**Key Features Now Working:**

✅ **Likes & Bookmarks:**
- Persistent storage across page refreshes
- Works for both tracks and shows
- Immediate visual feedback with CSS classes
- Proper error handling and user notifications

✅ **Playlist Management:**
- Create, edit, delete playlists
- Add/remove content from playlists
- Persistent storage per user
- Full CRUD operations via API

✅ **Data Persistence:**
- Thread-safe JSON file operations
- User-specific data organization
- Atomic write operations prevent data corruption

**Testing:**
- Created `test_likes_playlists.py` for API endpoint testing
- All endpoints properly authenticated and validated
- Data files created and updated correctly

**Technical Improvements:**
- Event delegation for better performance
- Proper error handling throughout
- Consistent API response format
- Thread-safe file operations
- Clean separation of concerns

**Files Modified:**
- `storage.py` (new)
- `blueprints/activity.py` (new)
- `blueprints/playlists.py` (new)
- `blueprints/__init__.py` (new)
- `app.py` (updated)
- `static/js/app.js` (updated)
- `static/js/playlist-manager.js` (replaced)
- `templates/music.html` (updated)
- `templates/shows.html` (updated)
- `test_likes_playlists.py` (new)

**Result:** The platform now has fully functional likes, bookmarks, and playlist management that persists across sessions and provides immediate user feedback.

---

## Changelog

### Version 1.0.0
- Initial Flask application
- Complete media platform
- User management system
- Playlist management
- Responsive design
- API endpoints
- Sample data

---

### 2025-10-17 — Gamification, Listening, DB Migrations, APIs, UI

- Database & Migrations
  - Added SQLAlchemy models: `ListeningSession`, `ListeningTotal`, `Achievement`, `UserAchievement`, `QuestDef`, `UserQuest`, `RadioPrefs`.
  - Alembic migrations:
    - `0004_add_user_profile_fields.py` (display_name, avatar_url, preferences JSON/JSONB, last_active_at, disabled).
    - `0005_create_listening_tables.py` (sessions + totals, indexes, Postgres UUID default).
    - `0006_create_achievements.py` (achievements + user_achievements, unique + indexes).
    - `0007_create_quests.py` (quest_defs + user_quests, unique + indexes, JSONB rules on Postgres).
    - `0008_create_radio_prefs.py` (per-user radio prefs; JSONB on Postgres).

- Services
  - `services/listening.py`: start/end listening sessions; idempotent end with safe tz math; updates totals.
  - `services/gamify.py`: `on_event`, `check_achievements`, `apply_quest_progress`, `ensure_user_daily_quests`.

- CLI
  - `flask gamify seed-defs` (upsert default achievements and daily quests).
  - `flask gamify backfill-totals` (estimate listen totals from play_history).
  - `flask gamify ensure-today` (create today/weekly user quests; idempotent).

- APIs
  - New blueprint `blueprints/api/gamify.py` under `/api`:
    - `GET /api/me/gamification` (badges, listen totals, today’s quests, recent unlocks).
    - `POST /api/debug/gamify` (dev-only; guarded by `AHOY_DEV_GAMIFY_DEBUG`).
  - Minimal listening hooks:
    - `POST /api/listening/start` and `/api/listening/end`.

- Hooks
  - Wired `blueprints/activity.py` to call gamify on `play` and `save`.

- UI
  - Header badge chips partial `templates/_badge_chips.html` (shows up to 3 recent badges); included in `base.html` next to username.
  - Account page mission list describing how to earn badges/merit badges.

- Config & App bootstrap
  - Sessions: `SESSION_TYPE=filesystem`, secure cookie flags; Flask-Session integration (optional if not installed).
  - `app.py` local UX: auto-apply migrations (with PYTHONPATH/DATABASE_URL defaults), pick a free port, prefer gunicorn if available.

- Render/Prod readiness
  - `scripts/migrate_and_start.sh` runs `alembic upgrade head` before gunicorn.
  - Added deploy/seed/test steps to this README.

Notes: Local dev defaults to SQLite if `DATABASE_URL` is unset; Postgres JSONB/UUID features are enabled automatically in migrations when available.

---

## 🚀 Quick Navigation

### For Users
- **Start Here**: [Home](/)
- **Browse Music**: [Music Library](/music)
- **Watch Shows**: [Shows & Videos](/shows)
- **Discover Artists**: [Artists](/artists)
- **Bookmarks**: [Bookmarks](/bookmarks)

### For Developers
- **API Reference**: [API Endpoints](#api-reference)
- **Data Structure**: [Data Structure](#data-structure)
- **File Organization**: [Project Structure](#project-structure)
- **Debug Tools**: [Debug Console](/debug)

### For Administrators
- **User Management**: [Admin Panel](/admin)
- **System Status**: [Debug Console](/debug)
- **User Feedback**: [Feedback Review](/feedback)

---

**Ahoy Indie Media** - Discover, organize, and enjoy independent music and content.

*Last Updated: December 2024 | Version: 1.0.0*

---

## 📦 Repository Cleanup & Archive

As part of repository maintenance, the following files have been moved to `.archive/` folder for reference but are no longer actively used in the codebase:

### Redundant Entry Point Scripts
- **`start.py`** - Redundant production startup script. Production deployments use `gunicorn` with `gunicorn.conf.py` and `scripts/migrate_and_start.sh`. For local development, use `run.py` or `cli.py`.
- **`start.bat`** - Windows-specific startup script. Functionality covered by `cli.py` which works cross-platform.
- **`start_browser.sh`** - Shell script that only starts the app and opens browser. Redundant with `run.py` which handles port detection and startup.

### Redundant Deployment Documentation
- **`DEPLOYMENT.md`** - Basic deployment guide. All deployment information is now consolidated in the main README.md under the "Deployment" section.
- **`PRODUCTION_DEPLOYMENT.md`** - Production-specific deployment guide. Information integrated into README.md.
- **`RENDER_DEPLOYMENT_CHECKLIST.md`** - Deployment checklist. Checked items and process now documented in main README.
- **`RENDER_FIX_GUIDE.md`** - Historical fix guide for Render deployment issues. No longer needed as deployment is stable.

### Redundant Build Configuration
- **`AhoyIndieMedia.spec`** - Duplicate PyInstaller spec file. The canonical spec file is `packaging/ahoy.spec` which is properly maintained.

### Debug/Development Files
- **`cookies.txt`** - Session cookie file from browser testing. Should not be in version control as it contains session data.
- **`debug_config.json`** - Debug configuration snapshot. Outdated and no longer reflects current architecture.
- **`debug_hero.html`** - Standalone HTML file for debugging hero carousel. Debugged issue resolved; no longer needed.

### Unused Templates
- **`templates/bookmark_test.html`** - Test template for bookmark functionality. Bookmark system is fully implemented; test template no longer needed. Route `/bookmark-test` has been removed.
- **`templates/downloads_simple.html`** - Simple version of downloads page. Replaced by `templates/downloads.html` which is actively used.

### Documentation
- **`GPT_COLLABORATION_SUMMARY.md`** - Historical collaboration notes with GPT assistant. Information integrated into main README development log section.
- **`static/data/products.json`** - Duplicate products file. The canonical file is `data/products.json` which is used by `services/plan.py`. Frontend code should reference via API endpoint instead.

**Note:** All archived files are preserved for historical reference. If you need any of these files, they can be found in the `.archive/` directory. However, they are not part of the active codebase and may reference outdated patterns or configurations.
