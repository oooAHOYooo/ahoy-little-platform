<template>
  <header class="app-header">
    <!-- 1. Mobile status bar (Flask: mobile-status-bar mobile-only) -->
    <div class="mobile-status-bar mobile-only">
      <div class="status-bar-content">
        <div class="status-left">
          <span class="status-time">{{ statusTime }}</span>
          <span class="status-breadcrumb" :title="breadcrumbText">{{ breadcrumbText }}</span>
        </div>
        <div class="status-right">
          <router-link to="/search" class="status-action-btn" aria-label="Search" title="Search">
            <i class="fas fa-search"></i>
          </router-link>
        </div>
      </div>
    </div>

    <!-- 2. Mobile top nav — 8 tabs (Flask: mobile-nav-root > mobile-top-nav mobile-only) -->
    <div class="mobile-nav-root mobile-only">
      <nav class="mobile-top-nav mobile-only" role="navigation" aria-label="Primary">
        <router-link to="/music" class="mobile-tab" :class="{ active: route.path === '/music' }">
          <i class="fas fa-music" aria-hidden="true"></i>
          <span>Music</span>
        </router-link>
        <router-link to="/shows" class="mobile-tab" :class="{ active: route.path === '/shows' }">
          <i class="fas fa-video" aria-hidden="true"></i>
          <span>Videos</span>
        </router-link>
        <router-link to="/live-tv" class="mobile-tab" :class="{ active: route.path === '/live-tv' }">
          <i class="fas fa-tv" aria-hidden="true"></i>
          <span>Live TV</span>
        </router-link>
        <router-link to="/artists" class="mobile-tab" :class="{ active: route.path === '/artists' }">
          <i class="fas fa-users" aria-hidden="true"></i>
          <span>Artists</span>
        </router-link>
        <router-link to="/podcasts" class="mobile-tab" :class="{ active: route.path.startsWith('/podcasts') }">
          <i class="fas fa-podcast" aria-hidden="true"></i>
          <span>Podcasts</span>
        </router-link>
        <router-link to="/merch" class="mobile-tab" :class="{ active: route.path === '/merch' }">
          <i class="fas fa-shopping-bag" aria-hidden="true"></i>
          <span>Merch</span>
        </router-link>
        <router-link to="/radio" class="mobile-tab" :class="{ active: route.path === '/radio' }">
          <i class="fas fa-broadcast-tower" aria-hidden="true"></i>
          <span>Radio</span>
        </router-link>
        <router-link to="/my-saves" class="mobile-tab" :class="{ active: route.path === '/my-saves' }">
          <i class="fas fa-bookmark" aria-hidden="true"></i>
          <span>Saved</span>
        </router-link>
      </nav>
    </div>

    <!-- 3. Navbar (desktop: breadcrumbs + account; mobile: logo + hamburger + breadcrumbs + Explore + account) -->
    <nav class="navbar desktop-nav">
      <div class="nav-container ds-statusbar max-w-7xl mx-auto px-4">
        <!-- Mobile logo (Flask: nav-logo mobile-only) -->
        <div class="nav-logo mobile-only" style="display: flex;">
          <router-link to="/" aria-label="Ahoy Home">
            <img :src="logoUrl" alt="Ahoy Indie Media" />
          </router-link>
        </div>
        <!-- Mobile hamburger (opens offcanvas drawer) -->
        <button
          type="button"
          class="mobile-hamburger mobile-only"
          title="Menu"
          aria-label="Open Menu"
          @click="$emit('toggle-mobile-menu')"
        >
          <i class="fas fa-bars"></i>
        </button>
        <div class="ds-statusbar__left">
          <div class="nav-history desktop-only" aria-label="History navigation">
            <button type="button" class="nav-history-btn" title="Back" aria-label="Back" @click="goBack">
              <i class="fas fa-chevron-left" aria-hidden="true"></i>
            </button>
            <button type="button" class="nav-history-btn" title="Forward" aria-label="Forward" @click="goForward">
              <i class="fas fa-chevron-right" aria-hidden="true"></i>
            </button>
          </div>
          <nav class="ds-crumbs" aria-label="Location">
            <template v-for="(c, idx) in breadcrumbs" :key="idx">
              <span class="ds-crumbs__item">
                <router-link v-if="c.href && idx < breadcrumbs.length - 1" :to="c.href" class="ds-crumbs__link">{{ c.label }}</router-link>
                <span v-else :class="idx === breadcrumbs.length - 1 ? 'ds-crumbs__current' : 'ds-crumbs__muted'">{{ c.label }}</span>
              </span>
              <span v-if="idx < breadcrumbs.length - 1" class="ds-crumbs__sep">›</span>
            </template>
          </nav>
        </div>
        <div class="ds-statusbar__right">
          <span class="account-username desktop-only">{{ auth.isLoggedIn.value ? auth.username.value : 'guest' }}</span>
          <router-link to="/account" class="account-icon-btn desktop-only" aria-label="Account" title="Account">
            <i class="fas fa-user-circle"></i>
          </router-link>
          <!-- Mobile right: Explore + Account (Flask: mobile-only) -->
          <div class="mobile-only" style="display:flex; gap:8px; align-items:center;">
            <router-link to="/" class="nav-item" style="min-width:44px;height:40px;border-radius:10px;border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.06);color:#e5e7eb;display:flex;align-items:center;justify-content:center;text-decoration:none;font-size:13px;">
              Explore
            </router-link>
            <router-link to="/account" class="ds-iconbtn ds-iconbtn--account nav-item" aria-label="Profile" title="Profile" style="min-width:40px;height:40px;display:flex;align-items:center;justify-content:center;color:inherit;text-decoration:none;">
              <i class="fas fa-user"></i>
            </router-link>
          </div>
        </div>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

defineProps({
  mobileMenuOpen: { type: Boolean, default: false },
})
defineEmits(['toggle-mobile-menu'])

const route = useRoute()
const auth = useAuth()

const logoUrl = '/static/img/ahoy_logo.png'
const statusTime = ref('')

const breadcrumbs = computed(() => {
  const name = route.name || 'home'
  const slug = (route.params.slug || '').replace(/-/g, ' ')
  const slugLabel = slug ? slug.charAt(0).toUpperCase() + slug.slice(1) : ''
  const map = {
    home: [{ label: 'Explore', href: '/' }, { label: 'Home', href: null }],
    music: [{ label: 'Music', href: '/music' }, { label: 'Browse', href: null }],
    'music-detail': [{ label: 'Music', href: '/music' }, { label: 'Track', href: null }],
    shows: [{ label: 'Videos', href: '/shows' }, { label: 'Browse', href: null }],
    'show-detail': [{ label: 'Videos', href: '/shows' }, { label: slugLabel || 'Show', href: null }],
    'live-tv': [{ label: 'Live TV', href: '/live-tv' }, { label: 'Watch', href: null }],
    artists: [{ label: 'Artists', href: '/artists' }, { label: 'Browse', href: null }],
    'artist-detail': [{ label: 'Artists', href: '/artists' }, { label: slugLabel || 'Artist', href: null }],
    podcasts: [{ label: 'Podcasts', href: '/podcasts' }, { label: 'Browse', href: null }],
    'podcast-detail': [{ label: 'Podcasts', href: '/podcasts' }, { label: slugLabel || 'Show', href: null }],
    events: [{ label: 'Events', href: '/events' }, { label: 'Upcoming', href: null }],
    'event-detail': [{ label: 'Events', href: '/events' }, { label: 'Event', href: null }],
    merch: [{ label: 'Merch', href: '/merch' }, { label: 'Shop', href: null }],
    radio: [{ label: 'Radio', href: '/radio' }, { label: 'Live', href: null }],
    'my-saves': [{ label: 'Saved', href: '/my-saves' }, { label: 'Library', href: null }],
    login: [{ label: 'Profile', href: null }],
    'now-playing': [{ label: 'Now Playing', href: null }],
    account: [{ label: 'Account', href: '/account' }, { label: 'Profile', href: null }],
    settings: [{ label: 'Settings', href: '/settings' }, { label: 'Preferences', href: null }],
    search: [{ label: 'Search', href: null }],
    dashboard: [{ label: 'Dashboard', href: null }],
    playlists: [{ label: 'Playlists', href: '/playlists' }, { label: 'Browse', href: null }],
    'playlist-detail': [{ label: 'Playlists', href: '/playlists' }, { label: 'Playlist', href: null }],
  }
  const crumb = map[name]
  if (crumb) return crumb
  const path = route.path
  if (path === '/') return [{ label: 'Explore', href: '/' }, { label: 'Home', href: null }]
  const parts = path.split('/').filter(Boolean)
  const out = []
  let href = ''
  parts.forEach((p, i) => {
    href += '/' + p
    const label = (p.replace(/-/g, ' ') || (i === parts.length - 1 ? 'Page' : '')).replace(/^\w/, w => w.toUpperCase())
    out.push({ label, href: i < parts.length - 1 ? href : null })
  })
  return out.length ? out : [{ label: 'Explore', href: '/' }, { label: 'Home', href: null }]
})

const breadcrumbText = computed(() => breadcrumbs.value.map(c => c.label).join(' › '))

function updateTime() {
  const now = new Date()
  statusTime.value = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })
}

function goBack() {
  window.history.back()
}
function goForward() {
  window.history.forward()
}

let timeInterval
onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})
onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
})
</script>
