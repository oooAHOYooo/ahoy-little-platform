# 🎵 Ahoy Indie Media

**A beautiful, modern platform for discovering and supporting independent music, shows, and content.**

Ahoy Indie Media is a comprehensive Flask-based media platform that brings together music discovery, video content, artist profiles, and a complete payment system—all wrapped in a stunning dark liquid glass interface.

---

## ✨ What Makes Ahoy Special?

### 🎨 Beautiful Design
- **Dark Liquid Glass Aesthetic** - Modern glassmorphism design with smooth animations
- **Responsive & Mobile-First** - Works beautifully on phones, tablets, and desktops
- **Smooth Animations** - Polished interactions that feel premium
- **Accessible** - Built with accessibility in mind

### 🎵 Rich Media Experience
- **TikTok-Style Discovery** - Swipe through content with 30-second previews
- **Full Music Library** - Browse, search, and play independent music
- **Video Shows** - Watch live shows and video content
- **Artist Profiles** - Discover artists with music, shows, and social links
- **Live TV & Radio** - Tune into live broadcasts and radio streams

### 💰 Complete Payment System
- **Wallet System** - Pre-fund your wallet for instant checkout
- **Artist Boosts** - Support artists directly with tips/boosts
- **Merch Store** - Buy physical items from artists
- **Stripe Integration** - Secure, PCI-compliant payments
- **Transaction History** - Complete audit trail of all payments

### 👤 Powerful User Features
- **Playlists** - Create unlimited playlists and organize your content
- **Bookmarks** - Save tracks, shows, and artists for later
- **Likes & History** - Track everything you interact with
- **Gamification** - Earn badges and achievements as you listen
- **Personalized Recommendations** - AI-driven content suggestions

### 🎮 Gamification & Engagement
- **Achievements** - Unlock badges for listening milestones
- **Daily Quests** - Complete challenges to earn rewards
- **Listening Stats** - Track your listening time and habits
- **Leaderboards** - See how you compare (coming soon)

### 🛠️ Developer-Friendly
- **RESTful APIs** - Clean, well-documented API endpoints
- **Database Migrations** - Alembic for schema management
- **Desktop Apps** - Standalone apps for macOS, Windows, and Linux
- **Docker Support** - Easy containerization
- **Comprehensive Docs** - Extensive documentation

---

## 🚀 Quick Start

### For Users
Just visit **[app.ahoy.ooo](https://app.ahoy.ooo)** and start exploring!

### For Developers

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/ahoy-little-platform.git
cd ahoy-little-platform
```

**2. Set up Python environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

**4. Run the app:**
```bash
python app.py
```

The app will automatically find an available port (5001-5010) and display the URL.

---

## 📚 Key Features Deep Dive

### 🎵 Media Discovery

**Now Playing Feed** (`/`)
- TikTok-style horizontal carousel
- 30-second previews
- Weather widget
- Daily curated playlist
- Quick actions and bookmarks

**Music Library** (`/music`)
- Grid and list view toggle
- Advanced search and filtering
- Like, bookmark, and add to playlists
- Play previews
- Artist information

**Shows & Videos** (`/shows`)
- Video player with full-screen mode
- Show categories and tags
- Host information
- Save and like functionality
- Playback controls

**Artists Directory** (`/artists`)
- Detailed artist profiles
- Music and shows by artist
- Social media links
- Follow artists
- Content discovery

### 💰 Payment & Wallet System

**Wallet Features:**
- Pre-fund wallet with Stripe
- Instant checkout (no card entry needed)
- Use wallet for boosts and merch
- Transaction history
- Optional convenience feature

**Payment Options:**
1. **Wallet Payment** - Instant, no redirect
2. **Direct Stripe** - Traditional card payment

**Artist Support:**
- Boost artists with tips
- All boosts go into artist "buckets"
- Track artist earnings
- Admin dashboard for payouts

**Merch Store:**
- Physical items from artists
- Secure checkout
- Order tracking
- Purchase history

### 👤 User Management

**Account Features:**
- Profile settings and avatar upload
- Statistics and listening history
- Data migration from guest mode
- Wallet management
- Transaction history

**Authentication:**
- Username/password login
- Guest mode (localStorage)
- Password reset via email
- Session-based security

**Social Features:**
- Follow artists
- Create and share playlists
- Like and bookmark content
- Activity feed

### 🎮 Gamification

**Achievements:**
- Listening milestones
- Content discovery badges
- Social interaction rewards
- Special event achievements

**Quests:**
- Daily challenges
- Weekly goals
- Progress tracking
- Reward system

**Statistics:**
- Total listening time
- Favorite artists
- Most played tracks
- Activity breakdown

### 📱 Platform Support

**Web App:**
- Responsive design
- Progressive Web App (PWA)
- Offline support
- Mobile-optimized

**Desktop Apps:**
- macOS (.app and .dmg)
- Windows (.exe installer)
- Linux (AppImage)
- Standalone (no Python needed)

**Mobile:**
- iOS (via Capacitor)
- Android (APK)
- Native media controls
- Background audio

---

## 🛠️ Development

### Project Structure

```
ahoy-little-platform/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── blueprints/            # Modular route organization
│   ├── api/              # API endpoints
│   └── payments.py       # Payment handling
├── routes/               # Additional routes
│   └── stripe_webhooks.py # Stripe webhook handler
├── templates/            # Jinja2 templates
├── static/               # CSS, JS, images
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript
│   └── data/            # JSON content files
├── alembic/             # Database migrations
└── docs/                # Documentation
```

### API Endpoints

**Content APIs:**
- `GET /api/music` - Music library
- `GET /api/shows` - Video shows
- `GET /api/artists` - Artist directory
- `GET /api/search` - Universal search

**User APIs:**
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/user/profile` - Get profile
- `PUT /api/user/profile` - Update profile

**Activity APIs:**
- `POST /api/activity/like` - Like content
- `POST /api/activity/bookmark` - Bookmark content
- `POST /api/activity/played` - Mark as played

**Playlist APIs:**
- `GET /api/playlists` - List playlists
- `POST /api/playlists` - Create playlist
- `PUT /api/playlists/<id>` - Update playlist
- `DELETE /api/playlists/<id>` - Delete playlist

**Payment APIs:**
- `GET /payments/wallet` - Get wallet balance
- `POST /payments/wallet/fund` - Fund wallet
- `GET /payments/wallet/transactions` - Transaction history

### Database

**Models:**
- `User` - User accounts and profiles
- `Playlist` - User playlists
- `Bookmark` - Saved content
- `Tip` - Artist boosts/tips
- `Purchase` - Merch purchases
- `WalletTransaction` - Wallet activity
- `ListeningSession` - Listening tracking
- `Achievement` - Gamification badges
- `Quest` - Daily/weekly quests

**Migrations:**
- Alembic for schema management
- Automatic migrations on Render
- Manual: `alembic upgrade head`

### Environment Variables

**Required:**
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
AHOY_ENV=production  # or development
```

**Stripe (Production):**
```bash
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

**Email (Password Reset):**
```bash
# Option 1: Resend
RESEND_API_KEY=...
SUPPORT_EMAIL=...

# Option 2: SMTP
SMTP_HOST=...
SMTP_PORT=...
SMTP_USER=...
SMTP_PASS=...
```

**Optional:**
```bash
REDIS_URL=...           # For Redis sessions
SENTRY_DSN=...          # Error tracking
BASE_URL=...            # Production URL
CORS_ORIGINS=...        # CORS settings
```

---

## 🚀 Deployment

### Render.com (Recommended)

**1. Connect Repository:**
- Link GitHub repository
- Render auto-detects `render.yaml`

**2. Environment Variables:**
- Set in Render dashboard
- See `render.yaml` for required vars

**3. Deploy:**
- Automatic on push to `main`
- Migrations run automatically
- Health checks at `/ops/selftest`

**See:** `docs/deployment/PRODUCTION_WALLET_DEPLOYMENT.md`

### Docker

```bash
docker build -t ahoy-indie-media .
docker run -p 5000:5000 ahoy-indie-media
```

### Manual Production

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## 📖 Documentation

### User Guides
- **Wallet System:** `docs/features/WALLET_COMPLETE_GUIDE.md`
- **User Workflows:** `docs/features/WALLET_USER_WORKFLOW.md`
- **Security:** `docs/features/STRIPE_SECURITY.md`

### Developer Guides
- **API Reference:** See `SITEMAP.md`
- **Troubleshooting:** `docs/troubleshooting/WALLET_TROUBLESHOOTING.md`
- **Deployment:** `docs/deployment/PRODUCTION_WALLET_DEPLOYMENT.md`

### In-App Documentation
- Visit `/sitemap` for complete app structure
- Visit `/debug` for system status

---

## 🎯 Key Capabilities

### For Content Creators
- ✅ Artist profiles with music and shows
- ✅ Direct fan support via boosts/tips
- ✅ Merch store integration
- ✅ Earnings tracking and payouts
- ✅ Social media integration

### For Music Fans
- ✅ Discover new independent music
- ✅ Create unlimited playlists
- ✅ Support artists directly
- ✅ Buy merch from artists
- ✅ Track listening history

### For Developers
- ✅ RESTful API
- ✅ Well-documented codebase
- ✅ Database migrations
- ✅ Desktop app builds
- ✅ Docker support

---

## 🔧 Troubleshooting

### Common Issues

**Wallet not showing:**
- Check database migrations ran
- Verify user is logged in
- Check browser console for errors

**Payment fails:**
- Verify Stripe keys are set
- Check webhook endpoint is configured
- Review server logs

**Migrations not running:**
- Run manually: `alembic upgrade head`
- Check `DATABASE_URL` is set
- Verify Alembic is installed

**See:** `docs/troubleshooting/WALLET_TROUBLESHOOTING.md` for detailed help

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/ahoy-little-platform/issues)
- **Documentation:** Check `/sitemap` in-app or `docs/` folder
- **Email:** support@ahoy.ooo

---

## 🎉 What's New

### Recent Updates
- ✅ Wallet system with instant checkout
- ✅ Liquid dark glass design refresh
- ✅ Console error logging for checkout
- ✅ Enhanced payment flows
- ✅ Improved user experience

### Coming Soon
- 🔜 Partial wallet payments
- 🔜 Saved payment methods
- 🔜 Guest checkout
- 🔜 Enhanced analytics

---

**Built with ❤️ for independent creators and music lovers**

*Last Updated: January 2025 | Version: 1.0.0*
