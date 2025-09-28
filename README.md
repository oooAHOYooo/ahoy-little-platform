# Ahoy Indie Media - Flask Platform

A comprehensive Flask-based media platform for discovering and organizing independent music, shows, and content. Built as a modern replacement for the original Cordova webapp with enhanced user features and playlist management.

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
   cd ahoy-super-platform
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

## Project Structure

```
ahoy-super-platform/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore file
│
├── data/                           # User data storage
│   ├── users.json                  # User accounts (created at runtime)
│   └── user_activity.json          # User activity logs
│
├── static/                         # Static files
│   ├── css/
│   │   ├── main.css               # Main stylesheet
│   │   └── components.css         # Component-specific styles
│   ├── js/
│   │   ├── app.js                 # Main JavaScript
│   │   ├── player.js              # Media player logic
│   │   ├── playlist-manager.js    # Playlist management
│   │   └── unified-hero.js        # Hero carousel system
│   ├── img/                       # Images and assets
│   └── data/                      # JSON data files
│       ├── music.json             # Music tracks
│       ├── shows.json             # Video shows
│       └── artists.json           # Artist profiles
│
└── templates/                      # Jinja2 templates
    ├── base.html                  # Base template
    ├── home.html                  # Discovery page
    ├── music.html                 # Music library
    ├── shows.html                 # Shows/video content
    ├── artists.html               # Artist directory
    ├── player.html                # Full-screen player
    ├── sitemap.html               # App structure documentation
    └── artist_profile.html        # Individual artist page
```

## 📋 App Structure & Documentation

For a comprehensive overview of the application's architecture, API endpoints, data structure, and functionality, visit the **[App Structure & Sitemap](/sitemap)** page. This documentation includes:

- **Complete page hierarchy** with features and functionality
- **Detailed API endpoint reference** with parameters and data sources
- **Data structure documentation** with JSON schemas
- **Frontend architecture** including JavaScript modules and CSS organization
- **Technology stack overview** and development information
- **Feature breakdown** and user functionality guides

Access this documentation:
- **In-app**: Settings menu → "App Structure" 
- **Direct URL**: `/sitemap`
- **Mobile**: User menu → "App Structure"

## API Endpoints

### Content
- `GET /api/now-playing` - Discovery feed
- `GET /api/music` - Music library
- `GET /api/shows` - Shows library
- `GET /api/artists` - Artist directory
- `GET /api/artist/<name>` - Specific artist profile
- `GET /api/search?q=query` - Universal search
- `GET /api/daily-playlist` - Seeded daily playlist

### User Management
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `GET /api/user/profile` - Get user profile

### Playlist Management
- `GET /api/user/playlists` - Get user playlists
- `POST /api/user/playlists` - Create new playlist
- `GET /api/user/playlists/<id>` - Get specific playlist
- `PUT /api/user/playlists/<id>` - Update playlist
- `DELETE /api/user/playlists/<id>` - Delete playlist
- `POST /api/user/playlists/<id>/items` - Add item to playlist
- `DELETE /api/user/playlists/<id>/items` - Remove item from playlist
- `POST /api/user/playlists/<id>/reorder` - Reorder playlist items

### User Activity
- `GET /api/user/likes` - Get user likes
- `POST /api/user/likes` - Like an item
- `DELETE /api/user/likes` - Unlike an item
- `GET /api/user/history` - Get listening history
- `POST /api/user/history` - Add to history
- `GET /api/user/recommendations` - Get personalized recommendations
- `GET /api/user/collections` - Get user collections
- `POST /api/user/collections` - Create new collection

## User Management

The platform uses a simple file-based user system with:
- **Registration/Login**: Username and password authentication
- **Password Hashing**: SHA-256 password security
- **Session Management**: Flask session-based authentication
- **User Preferences**: Theme, autoplay, and other settings
- **Activity Tracking**: Listening history and user statistics

## Data Structure

All content is stored in JSON files in `static/data/`:
- **`music.json`**: Track metadata and streaming URLs
- **`shows.json`**: Video content and show information
- **`artists.json`**: Artist profiles and biographical data
- **User data**: Stored in `data/users.json` (created at runtime)

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

## Security Considerations

- **Password Security**: Consider upgrading to bcrypt
- **Input Validation**: Validate all API inputs
- **Rate Limiting**: Implement for production
- **CORS**: Configure for API access
- **HTTPS**: Use SSL in production

## Performance Optimizations

- **Static File Caching**: Configure web server caching
- **API Response Caching**: 5-minute default cache
- **Lazy Loading**: For large libraries
- **Pagination**: For large datasets
- **CDN Integration**: For media files

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

**Ahoy Indie Media** - Discover, organize, and enjoy independent music and content.
