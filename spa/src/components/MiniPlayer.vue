<template>
  <div class="spa-mini-player" v-if="playerStore.currentTrack">
    <img
      :src="playerStore.currentTrack.cover_art || playerStore.currentTrack.thumbnail || '/static/img/default-cover.jpg'"
      :alt="playerStore.currentTrack.title"
      class="cover"
    />
    <div class="track-info">
      <div class="track-title">{{ playerStore.currentTrack.title }}</div>
      <div class="track-artist">{{ playerStore.currentTrack.artist || '' }}</div>
    </div>
    <div class="controls">
      <button @click="playerStore.previous()" aria-label="Previous">
        <i class="fas fa-backward-step"></i>
      </button>
      <button @click="playerStore.togglePlay()" aria-label="Play/Pause">
        <i :class="playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
      </button>
      <button @click="playerStore.next()" aria-label="Next">
        <i class="fas fa-forward-step"></i>
      </button>
    </div>
    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: playerStore.progress + '%' }"></div>
    </div>
  </div>
</template>

<script setup>
import { usePlayerStore } from '../stores/player'
const playerStore = usePlayerStore()
</script>
