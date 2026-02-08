<template>
  <PullRefresh @refresh="onRefresh">
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
          v-for="(track, idx) in tracks"
          :key="track.id"
          class="track-card"
          :class="{ playing: playerStore.currentTrack?.id === track.id }"
        >
          <div class="track-cover" @click="playTrack(idx)">
            <img :src="track.cover_art" :alt="track.title" loading="lazy" />
            <div class="track-overlay">
              <button class="play-btn" @click.stop="playTrack(idx)">
                <i :class="playerStore.currentTrack?.id === track.id && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
              </button>
              <button
                type="button"
                class="track-overlay-btn add-to-playlist-btn"
                title="Add to playlist"
                @click.stop="openAddToPlaylist(track)"
              >
                <i class="fas fa-plus"></i>
              </button>
            </div>
          </div>
          <router-link :to="`/music/${track.id}`" class="track-info" style="text-decoration:none;color:inherit">
            <div class="track-title">{{ track.title }}</div>
            <div class="track-artist">{{ track.artist }}</div>
          </router-link>
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
  </PullRefresh>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '../composables/useApi'
import { apiFetchCached } from '../composables/useApi'
import { usePlayerStore } from '../stores/player'
import { useAddToPlaylist } from '../composables/useAddToPlaylist'
import PullRefresh from '../components/PullRefresh.vue'

const playerStore = usePlayerStore()
const addToPlaylist = useAddToPlaylist()
function openAddToPlaylist(track) {
  addToPlaylist.open(track)
}
const tracks = ref([])

function playTrack(idx) {
  if (playerStore.currentTrack?.id === tracks.value[idx].id && playerStore.isPlaying) {
    playerStore.pause()
  } else {
    playerStore.setQueue(tracks.value, idx)
  }
}

async function loadTracks() {
  const data = await apiFetchCached('/api/music').catch(() => ({ tracks: [] }))
  tracks.value = data.tracks || []
}

async function onRefresh(done) {
  // Force fresh fetch (bypass cache)
  try {
    const data = await apiFetch('/api/music')
    tracks.value = data.tracks || []
    // Update cache
    localStorage.setItem('ahoy:/api/music', JSON.stringify({ data, ts: Date.now() }))
  } catch { /* keep existing */ }
  done()
}

onMounted(loadTracks)
</script>

<style scoped>
.track-overlay {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.add-to-playlist-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
}
.add-to-playlist-btn:hover {
  background: rgba(0, 0, 0, 0.8);
}
</style>
