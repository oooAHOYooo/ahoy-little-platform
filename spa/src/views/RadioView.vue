<template>
  <div class="home-page">
    <div class="unified-header">
      <div class="header-content">
        <h1>Radio</h1>
        <span class="header-count" v-if="allTracks.length">{{ allTracks.length }} tracks</span>
      </div>
    </div>

    <div class="live-dashboard">
      <div class="dashboard-sidebar" style="max-width:100%">
        <div class="sidebar-header">
          <h2>Now Playing</h2>
        </div>

        <!-- Now playing card -->
        <div class="dash-item radio-item" v-if="playerStore.currentTrack">
          <div class="dash-thumb">
            <img :src="playerStore.currentTrack.cover_art || playerStore.currentTrack.artwork || '/static/img/default-cover.jpg'" alt="Now Playing" />
          </div>
          <div class="dash-info">
            <div class="dash-title">{{ playerStore.currentTrack.title }}</div>
            <div class="dash-artist">{{ playerStore.currentTrack.artist }}</div>
          </div>
          <button class="dash-action-btn" @click="playerStore.togglePlay()">
            <i :class="playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
          </button>
        </div>

        <div class="dash-item radio-item" v-else-if="allTracks.length">
          <div class="dash-thumb">
            <img :src="allTracks[0].cover_art || '/static/img/default-cover.jpg'" alt="Radio" />
          </div>
          <div class="dash-info">
            <div class="dash-title">Tap to start radio</div>
            <div class="dash-artist">{{ allTracks.length }} tracks · Shuffle play</div>
          </div>
          <button class="dash-action-btn" @click="startRadio">
            <i class="fas fa-play"></i>
          </button>
        </div>

        <div class="dash-item radio-item" v-else>
          <div class="dash-thumb skeleton" style="width:60px;height:60px"></div>
          <div class="dash-info">
            <div class="skeleton" style="height:14px;width:60%;margin-bottom:6px"></div>
            <div class="skeleton" style="height:12px;width:40%"></div>
          </div>
        </div>
      </div>

      <!-- Up Next -->
      <div class="podcasts-section" v-if="playerStore.queue.length > 1" style="margin-top:16px">
        <div class="podcasts-section-header">
          <h2>Up Next</h2>
        </div>
        <div class="episode-list">
          <article
            v-for="(track, idx) in upNext"
            :key="track.id"
            class="episode-row"
            @click="playerStore.setQueue(playerStore.queue, playerStore.queue.indexOf(track))"
          >
            <img class="episode-art" :src="track.cover_art || '/static/img/default-cover.jpg'" :alt="track.title" loading="lazy" />
            <div class="episode-meta">
              <div class="episode-title">{{ track.title }}</div>
              <div class="episode-show">{{ track.artist }}</div>
            </div>
          </article>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'
import { usePlayerStore } from '../stores/player'

const playerStore = usePlayerStore()
const allTracks = ref([])

const upNext = computed(() => {
  if (!playerStore.currentTrack || !playerStore.queue.length) return []
  const idx = playerStore.queue.findIndex(t => t.id === playerStore.currentTrack.id)
  return playerStore.queue.slice(idx + 1, idx + 6)
})

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function startRadio() {
  const shuffled = shuffle(allTracks.value)
  playerStore.setQueue(shuffled, 0)
}

onMounted(async () => {
  const data = await apiFetchCached('/api/music').catch(() => ({ tracks: [] }))
  allTracks.value = data.tracks || []
})
</script>
