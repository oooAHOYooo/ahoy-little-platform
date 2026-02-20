<template>
  <div class="app">
    <!-- Toast notifications -->
    <Toast ref="toastRef" />
    <!-- Add to playlist modal (global) -->
    <AddToPlaylistModal />
    <!-- Guest save prompt: "Create account to sync" when guest bookmarks -->
    <GuestSavePrompt />

    <!-- Offline banner (matches base.html) -->
    <Transition name="slide-down">
      <div v-if="!online" class="offline-banner">
        <i class="fas fa-wifi" style="opacity:0.7"></i>
        You're offline — showing saved content
        <button @click="online = true" class="dismiss">&times;</button>
      </div>
    </Transition>

    <!-- Top bar: mobile status bar + mobile-top-nav (8 tabs) + navbar (Flask layout order) -->
    <AppNavbar :mobile-menu-open="mobileMenuOpen" @toggle-mobile-menu="mobileMenuOpen = !mobileMenuOpen" />
    <!-- Mobile hamburger menu (offcanvas drawer, same as Flask _nav_main.html) -->
    <MobileMenuDrawer :open="mobileMenuOpen" @close="mobileMenuOpen = false" />

    <!-- Mobile footer logo + secondary nav (5 tabs) + bottom nav (6 tabs) — same class names as base.html -->
    <NavBar v-if="route.name !== 'now-playing'" />

    <!-- Main content: app-shell + left sidebar + app-main (Flask: main.main-content) -->
    <main class="main-content">
      <div class="app-shell">
        <AppSidebar />
        <div class="app-main">
          <div class="content-area content-pad-bottom app-content spa-main" :class="{ 'has-player': route.name !== 'now-playing', 'flush-content': route.name === 'music' }">
            <router-view v-slot="{ Component, route: viewRoute }">
              <Transition :name="transitionName" mode="out-in">
                <keep-alive :include="['HomeView', 'MusicView', 'ShowsView', 'ArtistsView', 'PodcastsView', 'LiveTVView']">
                  <component :is="Component" :key="viewRoute.path" />
                </keep-alive>
              </Transition>
            </router-view>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer (same structure as Flask base.html app-footer) -->
    <AppFooter />

    <!-- Mini player (always visible like Flask; hidden on full Now Playing page) -->
    <MiniPlayer v-if="route.name !== 'now-playing' && playerStore.mode === 'audio'" />

    <!-- Global Video Player (TV / Shows) -->
    <GlobalTvPlayer />

    <!-- Compact fixed footer (time, ticker, quicklinks — same as Flask base.html) -->
    <CompactFooter />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { usePlayerStore } from './stores/player'
import { useTheme } from './composables/useTheme'
import { useWakeLock } from './composables/useNative'
import { restoreSession } from './composables/useAuth'
import { useMobileCollapse } from './composables/useMobileCollapse'
import { playTapChime } from './composables/useSaveChime'
import AppNavbar from './components/AppNavbar.vue'
import AppSidebar from './components/AppSidebar.vue'
import NavBar from './components/NavBar.vue'
import MiniPlayer from './components/MiniPlayer.vue'
import GlobalTvPlayer from './components/GlobalTvPlayer.vue'
import Toast from './components/Toast.vue'
import AddToPlaylistModal from './components/AddToPlaylistModal.vue'
import GuestSavePrompt from './components/GuestSavePrompt.vue'
import AppFooter from './components/AppFooter.vue'
import CompactFooter from './components/CompactFooter.vue'
import MobileMenuDrawer from './components/MobileMenuDrawer.vue'

const playerStore = usePlayerStore()
const mobileMenuOpen = ref(false)
const route = useRoute()
const wakeLock = useWakeLock()
const collapse = useMobileCollapse()

const toastRef = ref(null)
const online = ref(navigator.onLine)
const transitionName = ref('fade')

function onOnline() {
  online.value = true
  window.dispatchEvent(new CustomEvent('ahoy:toast', {
    detail: { message: 'Back online', type: 'success' }
  }))
}
function onOffline() { online.value = false }

// Keep screen on while playing
watch(() => playerStore.isPlaying, async (playing) => {
  if (playing) {
    await wakeLock.request()
  } else {
    await wakeLock.release()
  }
})

// Body class for Flask-style padding when mini player bar is visible
watch(() => route.name, (name) => {
  if (name === 'now-playing') document.body.classList.remove('has-player')
  else document.body.classList.add('has-player')
}, { immediate: true })

// Adjust body padding when UI is collapsed
watch([collapse.isPlayerCollapsed, collapse.isDockCollapsed], ([playerCollapsed, dockCollapsed]) => {
  if (playerCollapsed) document.body.classList.add('player-collapsed')
  else document.body.classList.remove('player-collapsed')

  if (dockCollapsed) document.body.classList.add('dock-collapsed')
  else document.body.classList.remove('dock-collapsed')
}, { immediate: true })

// Tiny tap chime on button/link click (optional: add data-no-tap-chime to opt out)
const TAP_CHIME_SELECTOR = [
  'button:not([disabled])',
  '[role="button"]:not([disabled])',
  'a[href]',
  'input[type="submit"]:not([disabled])',
  'input[type="button"]:not([disabled])',
  '.mobile-tab',
  '.neu-btn',
  '.episode-btn',
  '.bm-btn',
  '.action-btn',
  '.podcast-cta',
  '.settings-link',
  '.app-sidebar-item',
  '.experimental-card',
  '.download-table-link',
  '.quicklink',
  '.dismiss',
].join(', ')

function onGlobalClick(e) {
  const el = e.target?.closest?.(TAP_CHIME_SELECTOR)
  if (!el || el.closest('[data-no-tap-chime]')) return
  playTapChime()
}

onMounted(() => {
  restoreSession()
  useTheme().initTheme()
  window.addEventListener('online', onOnline)
  window.addEventListener('offline', onOffline)
  document.addEventListener('click', onGlobalClick, true)
  window.addEventListener('ahoy:session-expired', () => {
    // Prevent redirect loop if already on login page
    if (route.path !== '/login') {
      router.push('/login')
      window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Session expired', type: 'error' } }))
    }
  })
  wakeLock.autoReacquire()
})

onUnmounted(() => {
  document.body.classList.remove('has-player')
  document.removeEventListener('click', onGlobalClick, true)
  window.removeEventListener('online', onOnline)
  window.removeEventListener('offline', onOffline)
})
</script>
