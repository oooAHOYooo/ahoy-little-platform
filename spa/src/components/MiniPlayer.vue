<template>
  <div class="spa-mini-player" v-if="playerStore.currentTrack">
    <router-link to="/now-playing" style="flex-shrink:0">
      <img
        :src="playerStore.currentTrack.cover_art || playerStore.currentTrack.thumbnail || playerStore.currentTrack.artwork || '/static/img/default-cover.jpg'"
        :alt="playerStore.currentTrack.title"
        class="cover"
      />
    </router-link>
    <router-link to="/now-playing" class="track-info" style="text-decoration:none;color:inherit">
      <div class="track-title">{{ playerStore.currentTrack.title }}</div>
      <div class="track-artist">
        {{ playerStore.currentTrack.artist || '' }}
        <span class="track-time" v-if="playerStore.duration">
          {{ formatTime(playerStore.currentTime) }} / {{ formatTime(playerStore.duration) }}
        </span>
      </div>
    </router-link>
    <div class="controls">
      <button @click="playerStore.previous()" aria-label="Previous">
        <i class="fas fa-backward-step"></i>
      </button>
      <button @click="onTogglePlay" aria-label="Play/Pause" class="play-pause-btn">
        <i v-if="playerStore.loading" class="fas fa-spinner fa-spin"></i>
        <i v-else :class="playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
      </button>
      <button @click="playerStore.next()" aria-label="Next">
        <i class="fas fa-forward-step"></i>
      </button>
    </div>
    <div class="progress-bar" @click="onSeek">
      <div class="progress-fill" :style="{ width: playerStore.progress + '%' }"></div>
    </div>
  </div>
</template>

<script setup>
import { usePlayerStore } from '../stores/player'
import { useHaptics } from '../composables/useNative'

const playerStore = usePlayerStore()
const haptics = useHaptics()

function formatTime(seconds) {
  if (!seconds || !isFinite(seconds)) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function onTogglePlay() {
  haptics.onPlay()
  playerStore.togglePlay()
}

function onSeek(e) {
  const rect = e.currentTarget.getBoundingClientRect()
  const percent = ((e.clientX - rect.left) / rect.width) * 100
  playerStore.seek(Math.max(0, Math.min(100, percent)))
}
</script>
