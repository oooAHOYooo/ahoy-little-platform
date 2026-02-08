<template>
  <header class="app-header">
    <!-- Mobile status bar (time + breadcrumb + search) -->
    <div class="mobile-status-bar mobile-only">
      <div class="status-bar-content">
        <div class="status-left">
          <span class="status-time">{{ statusTime }}</span>
          <span class="status-breadcrumb" :title="breadcrumbText">{{ breadcrumbText }}</span>
        </div>
        <div class="status-right">
          <router-link to="/" class="status-action-btn" aria-label="Home" title="Home">
            <i class="fas fa-compass"></i>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Desktop navbar -->
    <nav class="navbar desktop-nav desktop-only">
      <div class="nav-container ds-statusbar max-w-7xl mx-auto px-4">
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
          <span class="hidden-mobile account-username">{{ auth.isLoggedIn.value ? auth.username.value : 'guest' }}</span>
          <router-link to="/login" class="hidden-mobile account-icon-btn" aria-label="Account" title="Account">
            <i class="fas fa-user-circle"></i>
          </router-link>
        </div>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const route = useRoute()
const auth = useAuth()

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
