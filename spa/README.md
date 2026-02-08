# Ahoy SPA (v2 Frontend)

Vue 3 + Vite single-page app that replaces the Flask-rendered templates for the mobile app.
Shares the same API backend (`https://app.ahoy.ooo/api/*`).

## Architecture

```
spa/                    ← Vue 3 + Vite source
  src/
    views/              ← Page components (Home, Music, Shows, etc.)
    components/         ← Shared components (NavBar, MiniPlayer)
    stores/             ← Pinia stores (player state)
    composables/        ← Shared logic (API client)
    assets/             ← CSS
spa-dist/               ← Build output (what Capacitor bundles into the native app)
```

## Development

```bash
cd spa
npm install
npm run dev          # starts Vite dev server on localhost:5173
                     # API calls proxy to https://app.ahoy.ooo
```

## Build for Capacitor

```bash
cd spa
npm run build                          # outputs to ../spa-dist
cp capacitor.config.spa.ts ../capacitor.config.ts   # switch to local mode
npx cap sync android && npx cap sync ios
# Then build in Android Studio / Xcode
```

## Switching between remote (v1) and local (v2)

- **v1 (current/main branch):** `capacitor.config.ts` has `server.url: 'https://app.ahoy.ooo'`
  → app loads website in a WebView
- **v2 (this branch):** `capacitor.config.ts` has `webDir: 'spa-dist'`, no `server.url`
  → app loads locally-built SPA, fetches data from API

## What's Working
- Home page with music/shows/artists sections
- Music page with track list + playback
- Shows, Podcasts, Artists, Events, Merch pages
- Mini player with play/pause/next/previous
- Offline-capable (API responses cached in localStorage)
- Bottom navigation

## TODO (Future Sessions)
- [ ] Match CSS exactly to production site (import main.css + combined.css)
- [ ] Search functionality
- [ ] User authentication (login/signup)
- [ ] Bookmarks/saves (sync with server)
- [ ] Podcast episode player
- [ ] Video player for shows
- [ ] Full player view (expanded from mini player)
- [ ] Settings page
- [ ] Push notifications (Firebase + APNs)
- [ ] Background audio (Capacitor plugin)
- [ ] Lock screen controls
- [ ] CarPlay / Android Auto media integration
- [ ] Offline downloads (Cache API for audio files)
