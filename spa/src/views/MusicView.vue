<template>
  <div>
    <div class="page-header">
      <h1>Music</h1>
      <p>{{ tracks.length }} tracks</p>
    </div>

    <div class="track-list" v-if="tracks.length">
      <div
        v-for="track in tracks"
        :key="track.id"
        class="track-item"
        :class="{ playing: playerStore.currentTrack?.id === track.id }"
        @click="playTrack(track)"
      >
        <img :src="track.cover_art" :alt="track.title" class="cover" loading="lazy" />
        <div class="info">
          <div class="title">{{ track.title }}</div>
          <div class="artist">{{ track.artist }} &middot; {{ track.album }}</div>
        </div>
        <div class="duration">{{ formatDuration(track.duration_seconds) }}</div>
      </div>
    </div>

    <!-- Loading skeletons -->
    <div class="track-list" v-else>
      <div class="track-item" v-for="i in 8" :key="i">
        <div class="cover skeleton"></div>
        <div class="info">
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

function formatDuration(seconds) {
  if (!seconds) return ''
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

onMounted(async () => {
  const data = await apiFetchCached('/api/music').catch(() => ({ tracks: [] }))
  tracks.value = data.tracks || []
})
</script>
