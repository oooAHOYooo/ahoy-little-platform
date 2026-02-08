<template>
  <div class="music-container">
    <div class="unified-header music-subheader">
      <div class="header-content">
        <h1>Music</h1>
        <span class="header-count">{{ tracks.length }} tracks</span>
      </div>
    </div>

    <!-- Grid view -->
    <div class="music-grid" v-if="tracks.length">
      <div
        v-for="track in tracks"
        :key="track.id"
        class="track-card"
        :class="{ playing: playerStore.currentTrack?.id === track.id }"
        @click="playTrack(track)"
      >
        <div class="track-cover">
          <img :src="track.cover_art" :alt="track.title" loading="lazy" />
          <div class="track-overlay">
            <button class="play-btn">
              <i :class="playerStore.currentTrack?.id === track.id && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
            </button>
          </div>
        </div>
        <div class="track-info">
          <div class="track-title">{{ track.title }}</div>
          <div class="track-artist">{{ track.artist }}</div>
        </div>
      </div>
    </div>

    <!-- Loading skeletons -->
    <div class="music-grid" v-else>
      <div class="track-card" v-for="i in 8" :key="i">
        <div class="track-cover skeleton"></div>
        <div class="track-info">
          <div class="skeleton" style="height:14px;width:60%;margin-bottom:6px"></div>
          <div class="skeleton" style="height:12px;width:40%"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'
import { usePlayerStore } from '../stores/player'

const playerStore = usePlayerStore()
const tracks = ref([])

function playTrack(track) {
  playerStore.setQueue(tracks.value, tracks.value.indexOf(track))
}

onMounted(async () => {
  const data = await apiFetchCached('/api/music').catch(() => ({ tracks: [] }))
  tracks.value = data.tracks || []
})
</script>
