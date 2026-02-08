<template>
  <div class="mini-player" v-if="playerStore.currentTrack">
    <img
      :src="playerStore.currentTrack.cover_art || playerStore.currentTrack.artwork || '/static/img/default-cover.jpg'"
      :alt="playerStore.currentTrack.title"
      class="cover"
    />
    <div class="track-info">
      <div class="track-title">{{ playerStore.currentTrack.title }}</div>
      <div class="track-artist">{{ playerStore.currentTrack.artist || '' }}</div>
    </div>
    <div class="controls">
      <button @click="playerStore.previous()">&#9664;</button>
      <button @click="playerStore.togglePlay()">
        {{ playerStore.isPlaying ? '&#10074;&#10074;' : '&#9654;' }}
      </button>
      <button @click="playerStore.next()">&#9654;</button>
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
