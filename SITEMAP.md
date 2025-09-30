# Ahoy Indie Media - Complete Sitemap & API Reference

## 📋 Table of Contents

1. [Main Pages](#main-pages)
2. [User Pages](#user-pages)
3. [Utility Pages](#utility-pages)
4. [API Endpoints](#api-endpoints)
5. [Data Structure](#data-structure)
6. [File Organization](#file-organization)

---

## Main Pages

### 🏠 Discovery & Content
| Route | Page | Description | Features |
|-------|------|-------------|----------|
| `/` | **Home** | Main discovery page with Now Playing feed | • TikTok-style carousel<br>• Weather widget<br>• Daily playlist<br>• Quick actions<br>• Bookmarks widget |
| `/music` | **Music Library** | Browse and play music tracks | • Grid/List view toggle<br>• Search & filtering<br>• Like & bookmark<br>• Add to playlist<br>• Play previews |
| `/shows` | **Shows & Videos** | Video content and live shows | • Video player<br>• Show categories<br>• Host information<br>• Save & like<br>• Full-screen mode |
| `/artists` | **Artists Directory** | Browse independent artists | • Artist profiles<br>• Music & shows<br>• Social links<br>• Follow artists<br>• Content discovery |
| `/performances` | **Performances** | Live performance listings | • Event calendar<br>• Venue information<br>• Ticket links<br>• Performance details |
| `/player` | **Full-Screen Player** | Dedicated media player | • Full-screen playback<br>• Queue management<br>• Playback controls<br>• Visualizer |

### 🔍 Search & Discovery
| Route | Page | Description | Features |
|-------|------|-------------|----------|
| `/search` | **Search Results** | Universal search interface | • Cross-content search<br>• Filter by type<br>• Sort options<br>• Recent searches |

---

## User Pages

### 👤 Account & Settings
| Route | Page | Description | Features |
|-------|------|-------------|----------|
| `/auth` | **Authentication** | Login and registration | • User login<br>• Account creation<br>• Password reset<br>• Guest mode |
| `/account` | **User Profile** | Account management | • Profile settings<br>• Avatar upload<br>• Statistics<br>• Data migration |
| `/settings` | **App Settings** | Application preferences | • Dark mode toggle<br>• Auto-play settings<br>• Notification preferences<br>• Privacy controls |

### 💾 User Content
| Route | Page | Description | Features |
|-------|------|-------------|----------|
| `/my-saves` | **My Saves** | Saved content management | • Saved tracks<br>• Saved shows<br>• Playlists<br>• Export/Sync |
| `/bookmarks` | **Bookmarks** | Bookmarked content | • All bookmarks<br>• Filter by type<br>• Quick access<br>• Bulk actions |

---

## Utility Pages

### 📚 Documentation & Support
| Route | Page | Description | Features |
|-------|------|-------------|----------|
| `/sitemap` | **App Structure** | Complete documentation | • Page hierarchy<br>• API reference<br>• Data schemas<br>• Architecture overview |
| `/feedback` | **Feedback** | User feedback system | • Bug reports<br>• Feature requests<br>• User suggestions<br>• Contact form |

### 🛠️ Development & Debug
| Route | Page | Description | Features |
|-------|------|-------------|----------|
| `/debug` | **Debug Console** | Development tools | • System status<br>• User management<br>• Data viewer<br>• API testing |
| `/debug_hero` | **Hero Debug** | Hero carousel testing | • Carousel testing<br>• Data validation<br>• Performance metrics |
| `/admin` | **Admin Panel** | User management | • User list<br>• Account management<br>• System monitoring<br>• Feedback review |

### 📄 Legal & Policies
| Route | Page | Description | Features |
|-------|------|-------------|----------|
| `/privacy` | **Privacy Policy** | Data privacy information | • Data collection<br>• Usage policies<br>• User rights<br>• Contact information |
| `/security` | **Security Policy** | Security measures | • Data protection<br>• Security practices<br>• Incident reporting<br>• Best practices |
| `/terms` | **Terms of Service** | Usage terms and conditions | • Service terms<br>• User agreements<br>• Liability<br>• Dispute resolution |

---

## API Endpoints

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
| `POST` | `/api/auth/login` | User login | `username`, `password` | Auth token |
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

### 🛠️ Debug & Admin APIs
| Method | Endpoint | Description | Parameters | Response |
|--------|----------|-------------|------------|----------|
| `GET` | `/api/debug/status` | System status | None | System health |
| `GET` | `/api/debug/users` | User list | None | All users |
| `GET` | `/api/admin/users` | Admin user list | None | User management data |
| `DELETE` | `/api/admin/users/<username>` | Delete user | `username` | Success status |
| `POST` | `/api/feedback` | Submit feedback | `message`, `type` | Success status |

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

---

## File Organization

### 🏗️ Backend Structure
```
ahoy-little-platform/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── storage.py                      # Thread-safe JSON storage
├── user_manager.py                 # User management utilities
├── extensions.py                   # Flask extensions
├── wsgi.py                        # WSGI entry point
├── run.py                         # Development runner
├── start.py                       # Production starter
├── requirements.txt               # Python dependencies
├── gunicorn.conf.py              # Gunicorn configuration
├── Procfile                       # Heroku deployment
├── render.yaml                    # Render deployment config
└── blueprints/                    # Modular route organization
    ├── __init__.py
    ├── activity.py                # User activity APIs
    ├── auth.py                    # Authentication APIs
    ├── bookmarks.py               # Bookmark management
    └── playlists.py               # Playlist management
```

### 🎨 Frontend Structure
```
static/
├── css/
│   ├── main.css                   # Main stylesheet
│   └── components.css             # Component styles
├── js/
│   ├── app.js                     # Main application logic
│   ├── player.js                  # Media player
│   ├── playlist-manager.js        # Playlist management
│   ├── bookmarks.js               # Bookmark functionality
│   ├── guest-bootstrap.js         # Guest user setup
│   └── unified-hero.js            # Hero carousel system
├── img/                           # Images and assets
└── data/                          # JSON data files
    ├── music.json
    ├── shows.json
    └── artists.json
```

### 📄 Template Structure
```
templates/
├── base.html                      # Base template
├── home.html                      # Discovery page
├── music.html                     # Music library
├── shows.html                     # Shows & videos
├── artists.html                   # Artist directory
├── player.html                    # Full-screen player
├── sitemap.html                   # App documentation
├── auth.html                      # Authentication
├── account.html                   # User profile
├── settings.html                  # App settings
├── my_saves.html                  # User saves
├── bookmarks.html                 # Bookmarks page
├── admin.html                     # Admin panel
├── debug.html                     # Debug console
├── feedback.html                  # Feedback form
├── privacy.html                   # Privacy policy
├── security.html                  # Security policy
├── terms.html                     # Terms of service
└── 404.html                       # Error page
```

---

## 🚀 Quick Navigation

### For Users
- **Start Here**: [Home](/)
- **Browse Music**: [Music Library](/music)
- **Watch Shows**: [Shows & Videos](/shows)
- **Discover Artists**: [Artists](/artists)
- **My Content**: [My Saves](/my-saves)

### For Developers
- **API Reference**: [API Endpoints](#api-endpoints)
- **Data Structure**: [Data Structure](#data-structure)
- **File Organization**: [File Organization](#file-organization)
- **Debug Tools**: [Debug Console](/debug)

### For Administrators
- **User Management**: [Admin Panel](/admin)
- **System Status**: [Debug Console](/debug)
- **User Feedback**: [Feedback Review](/feedback)

---

*Last Updated: December 2024*
*Version: 1.0.0*
