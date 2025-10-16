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

### 👁️ Watchlist APIs
| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| `GET` | `/api/activity/watchlist` | List watchlist items (auth) | — |
| `POST` | `/api/activity/watchlist` | Add item to watchlist (auth + CSRF) | `{ id, kind: 'show'|'track' }` |
| `DELETE` | `/api/activity/watchlist` | Remove item from watchlist (auth + CSRF) | `{ id, kind }` |

---

## Watchlist & Queue

### What is Watchlist?
Use Watchlist to mark shows or tracks you want to watch/listen soon. It’s separate from Bookmarks (long-term saves).

### Add/Remove from Watchlist
- Any card or player button with `data-watchlist` toggles Watchlist.
- On Shows and Player pages, click the eye icon to add/remove.

### Bulk from Bookmarks
On the Bookmarks page:
- Play Queue: queues all filtered bookmarks and starts playback.
- Add to Queue: appends all filtered bookmarks to the current queue.
- Add All to Watchlist: adds all filtered bookmarks (tracks/shows) to Watchlist.

### Programmatic usage
- Browser JS automatically sends `X-CSRF-Token` from `window.CSRF_TOKEN`.
- cURL examples:
```bash
# List
curl -b cookie.jar -c cookie.jar http://localhost:5000/api/activity/watchlist
# Add (show)
curl -b cookie.jar -c cookie.jar -X POST -H 'Content-Type: application/json' -H "X-CSRF-Token: $TOKEN" \
  -d '{"id":"show-123","kind":"show"}' http://localhost:5000/api/activity/watchlist
# Remove
curl -b cookie.jar -c cookie.jar -X DELETE -H 'Content-Type: application/json' -H "X-CSRF-Token: $TOKEN" \
  -d '{"id":"show-123","kind":"show"}' http://localhost:5000/api/activity/watchlist
```

### Queue behavior
- Queue stubs are provided in `static/js/player-queue.js` with `replace`, `append`, and `playNext`.
- Bookmarks page emits a `playlist:created` event that the queue listens to. Integrate with your real player later by mapping these events.

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

### Production Setup

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
### Database and Migrations (User State)

This project uses SQLAlchemy and Alembic for user state. In production, set `DATABASE_URL` (Postgres recommended). Locally, the app defaults to SQLite file `sqlite:///local.db` if no database URL is provided.

On Render, wire the database automatically via `render.yaml`:

```yaml
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: ahoy-postgres
      property: connectionString
```

## Desktop wrapper (macOS/Windows/Linux)

Package Ahoy as a desktop app using PyWebview (with a local Flask server).

1) Install build tools:

```bash
pip install -r requirements.txt pyinstaller
```

2) Run in desktop mode (dev):

```bash
python desktop_main.py
```

3) Build binaries:

```bash
pyinstaller --noconfirm --onefile --name "Ahoy Indie Media" desktop_main.py
```

4) Publish downloads:

- Create a `downloads/` folder at repo root and copy `dist/Ahoy Indie Media` builds into it
- Visit `/downloads` to serve artifacts

Environment:
- `PORT` (default 17600)
- `SECRET_KEY` (set for production)
- `LOCAL_DATABASE_URL` optional (e.g., `sqlite:////<user-data-dir>/ahoy.db`)

Locally, set it in your shell or `.env` file.

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
