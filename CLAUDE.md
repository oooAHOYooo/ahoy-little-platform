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

## Desktop/Mobile Builds

See `packaging/` directory:
- `packaging/build-all.sh` - Master build script
- `packaging/DESKTOP_BUILD_GUIDE.md` - Full documentation
- Electron app in `electron/`
- Capacitor for iOS/Android in `android/`
