import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('./views/HomeView.vue'),
  },
  {
    path: '/search',
    name: 'search',
    component: () => import('./views/SearchView.vue'),
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('./views/DashboardView.vue'),
  },
  {
    path: '/music',
    name: 'music',
    component: () => import('./views/MusicView.vue'),
  },
  {
    path: '/music/:id',
    name: 'music-detail',
    component: () => import('./views/MusicDetailView.vue'),
  },
  {
    path: '/shows',
    name: 'shows',
    component: () => import('./views/ShowsView.vue'),
    meta: { title: 'Videos' },
  },
  {
    path: '/videos',
    name: 'videos',
    component: () => import('./views/ShowsView.vue'),
    meta: { title: 'Videos' },
  },
  {
    path: '/shows/:id',
    name: 'show-detail',
    component: () => import('./views/ShowDetailView.vue'),
  },
  {
    path: '/videos/:id',
    name: 'video-detail',
    component: () => import('./views/ShowDetailView.vue'),
  },
  {
    path: '/live-tv',
    name: 'live-tv',
    component: () => import('./views/LiveTVView.vue'),
  },
  {
    path: '/podcasts',
    name: 'podcasts',
    component: () => import('./views/PodcastsView.vue'),
  },
  {
    path: '/podcasts/:slug',
    name: 'podcast-detail',
    component: () => import('./views/PodcastDetailView.vue'),
  },
  {
    path: '/artists',
    name: 'artists',
    component: () => import('./views/ArtistsView.vue'),
  },
  {
    path: '/artists/:slug',
    name: 'artist-detail',
    component: () => import('./views/ArtistDetailView.vue'),
  },
  {
    path: '/events',
    name: 'events',
    component: () => import('./views/EventsView.vue'),
  },
  {
    path: '/events/:id',
    name: 'event-detail',
    component: () => import('./views/EventDetailView.vue'),
  },
  {
    path: '/merch',
    name: 'merch',
    component: () => import('./views/MerchView.vue'),
  },
  {
    path: '/radio',
    name: 'radio',
    component: () => import('./views/RadioView.vue'),
  },
  {
    path: '/my-saves',
    name: 'my-saves',
    component: () => import('./views/SavedView.vue'),
  },
  {
    path: '/recently-played',
    name: 'recently-played',
    component: () => import('./views/SavedView.vue'),
  },
  {
    path: '/playlists',
    name: 'playlists',
    component: () => import('./views/PlaylistsView.vue'),
  },
  {
    path: '/playlists/:id',
    name: 'playlist-detail',
    component: () => import('./views/PlaylistDetailView.vue'),
  },
  {
    path: '/now-playing',
    name: 'now-playing',
    component: () => import('./views/NowPlayingView.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('./views/LoginView.vue'),
  },
  {
    path: '/account',
    name: 'account',
    component: () => import('./views/AccountView.vue'),
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('./views/SettingsView.vue'),
  },
  {
    path: '/focus',
    name: 'focus',
    component: () => import('./views/FocusView.vue'),
  },
  {
    path: '/download',
    name: 'download',
    component: () => import('./views/DownloadView.vue'),
  },
  {
    path: '/mp3-player',
    name: 'mp3-player',
    component: () => import('./views/Mp3PlayerView.vue'),
  },
  {
    path: '/auth/forgot',
    name: 'forgot-password',
    component: () => import('./views/ForgotPasswordView.vue'),
  },
  {
    path: '/auth/reset',
    name: 'reset-password',
    component: () => import('./views/ResetPasswordView.vue'),
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: () => import('./views/CheckoutView.vue'),
  },
  {
    path: '/success',
    name: 'success',
    component: () => import('./views/SuccessView.vue'),
  },
  {
    path: '/downloads',
    name: 'downloads',
    component: () => import('./views/DownloadsView.vue'),
  },
  {
    path: '/offline',
    name: 'offline',
    component: () => import('./views/OfflineView.vue'),
  },
  {
    path: '/privacy',
    name: 'privacy',
    component: () => import('./views/PrivacyView.vue'),
  },
  {
    path: '/terms',
    name: 'terms',
    component: () => import('./views/TermsView.vue'),
  },
  {
    path: '/security',
    name: 'security',
    component: () => import('./views/SecurityView.vue'),
  },
  {
    path: '/performances',
    name: 'performances',
    component: () => import('./views/PerformancesView.vue'),
  },
  {
    path: '/feedback',
    name: 'feedback',
    component: () => import('./views/FeedbackView.vue'),
  },
  {
    path: '/contact',
    name: 'contact',
    component: () => import('./views/ContactView.vue'),
  },
  {
    path: '/cast',
    name: 'cast',
    component: () => import('./views/CastView.vue'),
  },
  {
    path: '/whats-new',
    name: 'whats-new',
    component: () => import('./views/WhatsNewView.vue'),
  },
  {
    path: '/whats-new/:year/:month/:section?',
    name: 'whats-new-archive',
    component: () => import('./views/WhatsNewView.vue'),
  },
  {
    path: '/beta-testers',
    name: 'beta-testers',
    component: () => import('./views/BetaTestersView.vue'),
  },
  {
    path: '/sitemap',
    name: 'sitemap',
    component: () => import('./views/SitemapView.vue'),
  },
  {
    path: '/tip-artist',
    name: 'tip-artist',
    component: () => import('./views/TipArtistView.vue'),
  },
  {
    path: '/wallet',
    name: 'wallet',
    component: () => import('./views/WalletView.vue'),
  },
  // Legacy URL redirects (Flask used these; SPA uses different paths)
  { path: '/bookmarks', redirect: '/my-saves' },
  { path: '/recent', redirect: '/recently-played' },
  { path: '/auth', redirect: '/login' },
  { path: '/player', redirect: '/now-playing' },
  { path: '/artist/:slug', redirect: to => `/artists/${to.params.slug}` },
  // 404 – dedicated page with “Oops” / funny graphic
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('./views/NotFoundView.vue'),
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('./views/AdminDashboardView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true } // Logic handled in component or global guard
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

// Analytics tracking
router.afterEach((to) => {
  try {
    fetch('/api/admin/analytics/event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'page_view',
        path: to.path,
        metadata: { name: to.name, params: to.params }
      })
    }).catch(err => console.error('Analytics error', err))
  } catch (e) {
    // ignore
  }
})

export default router
