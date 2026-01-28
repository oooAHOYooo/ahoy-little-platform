# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ahoy Indie Media is a Flask-based media platform for independent music, shows, and artists. It features a wallet/payment system (Stripe), user authentication, playlists, bookmarks, and artist payouts.

## Development Commands

```bash
# Run the app (auto-finds available port 5001-5010)
python app.py

# Run tests
pytest tests/

# Run a single test file
pytest tests/test_smoke.py -v

# Run a specific test
pytest tests/test_payments.py::test_wallet_boost -v

# Database migrations
alembic upgrade head              # Apply all migrations
alembic revision -m "description" # Create new migration

# Production server
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Architecture

### Entry Points
- `app.py` - Main Flask application with `create_app()` factory pattern
- `wsgi.py` - WSGI entry point for production
- `gunicorn.conf.py` - Gunicorn configuration

### Database Layer
- `db.py` - SQLAlchemy engine, session management with `get_session()` context manager
- `models.py` - SQLAlchemy ORM models (User, Playlist, Bookmark, Tip, Purchase, etc.)
- `alembic/versions/` - Database migrations
- Uses PostgreSQL in production, SQLite locally (auto-detected via `DATABASE_URL`)

### Route Organization
- `blueprints/` - Flask blueprints for modular routes
  - `blueprints/api/` - API endpoints (auth, playlists, bookmarks, tips)
  - `blueprints/payments.py` - Wallet and payment handling
  - `blueprints/activity.py` - User activity tracking
- `routes/` - Additional route modules
  - `routes/stripe_webhooks.py` - Stripe webhook handler
  - `routes/boost_stripe.py` - Artist boost/tip checkout

### Services Layer
- `services/` - Business logic separated from routes
  - `services/listening.py` - Listening session tracking
  - `services/emailer.py` - Email sending (Resend API)
  - `services/notifications.py` - Admin/user notifications
  - `services/user_resolver.py` - User ID resolution

### Configuration
- `config.py` - Flask configuration with environment-based settings
- `extensions.py` - Flask extensions (bcrypt, login_manager, limiter, CORS)
- Environment detection: `AHOY_ENV` (production/development)
- Stripe keys auto-switch between test/live based on `AHOY_ENV`

### Static Content
- `static/data/*.json` - Content data (music, shows, artists, etc.)
- `templates/` - Jinja2 templates
- `static/css/`, `static/js/` - Frontend assets

## Key Patterns

### Database Sessions
```python
from db import get_session

with get_session() as session:
    user = session.query(User).filter_by(email=email).first()
    # session auto-commits on success, rolls back on exception
```

### Authentication
- Flask-Login for session management
- `@login_required` decorator for protected routes
- `@admin_required` from `utils/auth.py` for admin-only routes
- Guest mode uses localStorage (client-side)

### API Response Format
Most API endpoints return JSON with consistent structure:
- Success: `{"success": true, "data": {...}}`
- Error: `{"error": "message"}` with appropriate HTTP status

### Environment Variables
Key variables (see `.env.example`):
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask session secret (required in production)
- `AHOY_ENV` - Environment (production/development)
- `STRIPE_*` - Stripe API keys
- `RESEND_API_KEY` - Email service

## Testing

Tests use pytest with fixtures in `tests/conftest.py`:
- `app` - Test Flask application
- `client` - Test client
- `db_session` - Clean database session per test
- `test_user` - User with $100 wallet balance
- `authenticated_client` - Client with logged-in session

Test environment auto-uses SQLite in-memory database.

## Shared Utilities

### Fee Calculations (`utils/fees.py`)
```python
from utils.fees import calculate_boost_fees, PLATFORM_FEE_PERCENT
# All payment fee logic is centralized here
```

### API Helpers (`utils/api_helpers.py`)
```python
from utils.api_helpers import parse_pagination, ALLOWED_MEDIA_TYPES
# Shared pagination, media type validation
```

## Required Environment Variables

Production requires these (validated at startup):
- `SECRET_KEY` - Flask session secret (fails if missing)
- `AHOY_ADMIN_EMAIL` - Admin notification recipient (warnings if missing)
- `STRIPE_SECRET_KEY` - Stripe API key
- `RESEND_API_KEY` - Email service

## Video/Show URLs

Shows use human-readable slugs for sharing:
```
/player?id=palbot-causes-tension&type=show
/player?id=justin-arena-space-cadet&type=show
```

Show IDs are in `static/data/shows.json`. Thumbnails extracted via `scripts/extract_video_thumbnails.py`.

## Desktop/Mobile Builds

### Electron (Desktop)
See `packaging/` directory:
- `packaging/build-all.sh` - Master build script
- `packaging/DESKTOP_BUILD_GUIDE.md` - Full documentation
- Electron app in `electron/`

### Capacitor (iOS/Android)
Mobile apps use Capacitor with **remote URL mode** - they load the website from `https://ahoy-indie-media.onrender.com` rather than bundling assets. This means web updates deploy instantly without app store releases.

```bash
# Sync web assets and native plugins
npx cap sync

# Open in Android Studio
npx cap open android

# Open in Xcode
npx cap open ios

# After making changes, sync again
npx cap sync android
npx cap sync ios
```

Configuration: `capacitor.config.ts`
- Android: `android/` folder
- iOS: `ios/` folder

## CSS Architecture

### Main Files
- `static/css/main.css` - Primary styles (large file, all components)
- `static/css/combined.css` - Contains global reset, base styles, and mobile overrides
- `static/css/loader.css` - Loading screen styles
- `static/css/design-tokens.css` - CSS variables (colors, spacing, etc.)

### Cache Busting
CSS files use version query parameters in `templates/base.html`:
```jinja
{% set css_version = 'v20260128i' %}
<link rel="stylesheet" href="/static/css/combined.css?{{ css_version }}">
```
**Important:** Increment the version when making CSS changes to bust browser cache.

## Service Worker

`static/service-worker.js` caches static assets for offline use.
- Cache name: `ahoy-indie-media-v8` (increment when updating cached files)
- Updates `STATIC_CACHE_URLS` array when adding/removing CSS/JS files
- Currently **disabled** in `base.html` to prevent caching issues during development

**Note:** If users report seeing old styles, the service worker may be serving cached files. Clear caches by incrementing `CACHE_NAME` in service-worker.js.

## Mobile Considerations

### Scroll Issues
If vertical scroll stops working on mobile:
1. Check for `touch-action: none` in CSS (should use `manipulation` or `pan-y`)
2. Check for `event.preventDefault()` in touch handlers (remove from scroll handlers)
3. Check for `overflow: hidden` on `body` or `html` elements
4. Service worker may be serving old cached CSS - increment cache version
5. Modals/overlays may have `pointer-events` blocking scroll

### Touch Handlers
Touch event handlers in `static/js/unified-hero.js` and templates should NOT call `preventDefault()` during touch move events - this blocks native scrolling.

### Key Files for Mobile
- `templates/base.html` - Viewport meta, scroll fix script, cache clearing
- `static/css/combined.css` - Mobile-specific overrides at bottom
- `static/js/unified-hero.js` - Carousel touch handling
- `static/js/mobile.js` - Mobile menu interactions
