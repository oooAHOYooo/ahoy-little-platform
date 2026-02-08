<template>
  <div class="app">
    <!-- Offline banner -->
    <div v-if="!online" class="offline-banner">
      You're offline &mdash; showing saved content
      <button @click="online = true" class="dismiss">&times;</button>
    </div>

    <!-- Mini player (persistent across pages) -->
    <MiniPlayer v-if="playerStore.currentTrack" />

    <!-- Main content area -->
    <main class="spa-main" :class="{ 'has-player': playerStore.currentTrack }">
      <router-view v-slot="{ Component }">
        <keep-alive :include="['HomeView', 'MusicView', 'ShowsView']">
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </main>

    <!-- Bottom navigation -->
    <NavBar />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { usePlayerStore } from './stores/player'
import NavBar from './components/NavBar.vue'
import MiniPlayer from './components/MiniPlayer.vue'

const playerStore = usePlayerStore()
const online = ref(navigator.onLine)

function onOnline() { online.value = true }
function onOffline() { online.value = false }

onMounted(() => {
  window.addEventListener('online', onOnline)
  window.addEventListener('offline', onOffline)
})
onUnmounted(() => {
  window.removeEventListener('online', onOnline)
  window.removeEventListener('offline', onOffline)
})
</script>
