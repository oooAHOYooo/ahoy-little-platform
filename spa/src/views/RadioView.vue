<template>
  <div class="home-page">
    <div class="unified-header">
      <div class="header-content">
        <h1>Radio</h1>
      </div>
    </div>

    <div class="live-dashboard">
      <div class="dashboard-sidebar" style="max-width:100%">
        <div class="sidebar-header">
          <h2>Live Radio</h2>
        </div>

        <div class="dash-item radio-item" v-if="currentTrack">
          <div class="dash-thumb">
            <img :src="currentTrack.cover_art || '/static/img/default-cover.jpg'" alt="Now Playing" />
          </div>
          <div class="dash-info">
            <div class="dash-title">{{ currentTrack.title }}</div>
            <div class="dash-artist">{{ currentTrack.artist }}</div>
          </div>
          <button class="dash-action-btn" @click="toggleRadio">
            <i :class="isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'

const currentTrack = ref(null)
const isPlaying = ref(false)

function toggleRadio() {
  isPlaying.value = !isPlaying.value
}

onMounted(async () => {
  const data = await apiFetchCached('/api/radio').catch(() => ({ now_playing: null }))
  currentTrack.value = data.now_playing || null
})
</script>
