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
  },
  {
    path: '/shows/:id',
    name: 'show-detail',
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
  // Catch-all
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
