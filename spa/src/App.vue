<template>
  <div class="app">
    <!-- Toast notifications -->
    <Toast ref="toastRef" />

    <!-- Offline banner (matches base.html) -->
    <Transition name="slide-down">
      <div v-if="!online" class="offline-banner">
        <i class="fas fa-wifi" style="opacity:0.7"></i>
        You're offline — showing saved content
        <button @click="online = true" class="dismiss">&times;</button>
      </div>
    </Transition>

    <!-- Mini player (persistent across pages, hidden on Now Playing) -->
    <MiniPlayer v-if="playerStore.currentTrack && route.name !== 'now-playing'" />

    <!-- Main content: same structure as base.html (app-shell + left sidebar + app-main) -->
    <main class="main-content">
      <div class="app-shell">
        <AppSidebar />
        <div class="app-main">
          <div class="content-area content-pad-bottom app-content spa-main" :class="{ 'has-player': playerStore.currentTrack && route.name !== 'now-playing' }">
            <router-view v-slot="{ Component, route: viewRoute }">
              <Transition :name="transitionName" mode="out-in">
                <keep-alive :include="['HomeView', 'MusicView', 'ShowsView', 'ArtistsView', 'PodcastsView']">
                  <component :is="Component" :key="viewRoute.path" />
                </keep-alive>
              </Transition>
            </router-view>
          </div>
        </div>
      </div>
    </main>

    <!-- Bottom navigation — mobile only (desktop uses left sidebar) -->
    <NavBar v-if="route.name !== 'now-playing'" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { usePlayerStore } from './stores/player'
import { useWakeLock } from './composables/useNative'
import { restoreSession } from './composables/useAuth'
import AppSidebar from './components/AppSidebar.vue'
import NavBar from './components/NavBar.vue'
import MiniPlayer from './components/MiniPlayer.vue'
import Toast from './components/Toast.vue'

const playerStore = usePlayerStore()
const route = useRoute()
const wakeLock = useWakeLock()

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

// Re-acquire wake lock if tab returns to foreground while playing
onMounted(() => {
  restoreSession()
  window.addEventListener('online', onOnline)
  window.addEventListener('offline', onOffline)
  wakeLock.autoReacquire()
})

onUnmounted(() => {
  window.removeEventListener('online', onOnline)
  window.removeEventListener('offline', onOffline)
})
</script>
