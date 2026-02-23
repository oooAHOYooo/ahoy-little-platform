<template>
  <div
    v-if="playerStore.currentTrack && playerStore.mode === 'video'"
    class="global-tv-player"
    :class="{ 
      'mini': !playerStore.heroBounds && !playerStore.isWidescreenPinned, 
      'docked': !!playerStore.heroBounds,
      'pinned': playerStore.isWidescreenPinned 
    }"
    :style="playerStyle"
  >
    <div class="video-container">
      <video
        ref="videoRef"
        :src="videoSrc"
        autoplay
        playsinline
        :muted="playerStore.isMuted"
        @timeupdate="onTimeUpdate"
        @loadedmetadata="onLoadedMetadata"
        @play="playerStore.isPlaying = true"
        @pause="playerStore.isPlaying = false"
        @ended="onVideoEnded"
        @click="onVideoClick"
      ></video>
      
      <!-- Mini Player Overlay Controls -->
      <div v-if="!playerStore.heroBounds" class="mini-controls">
        <button class="mini-btn close" @click.stop="playerStore.eject">
          <i class="fas fa-times"></i>
        </button>
        <button class="mini-btn pin" @click.stop="playerStore.toggleWidescreenPinned" :title="playerStore.isWidescreenPinned ? 'Unpin' : 'Pin to Top'">
          <i :class="playerStore.isWidescreenPinned ? 'fas fa-thumbtack' : 'fas fa-map-marker-alt'"></i>
        </button>
        <button class="mini-btn expand" @click.stop="maximize">
          <i class="fas fa-expand-arrows-alt"></i>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="playerStore.loading" class="video-loading">
        <i class="fas fa-spinner fa-spin"></i>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePlayerStore } from '../stores/player'

const router = useRouter()
const playerStore = usePlayerStore()
const videoRef = ref(null)

const videoSrc = computed(() => {
  const t = playerStore.currentTrack
  if (!t) return ''
  return t.video_url || t.url || ''
})

const playerStyle = computed(() => {
  const bounds = playerStore.heroBounds
  // Pinned mode (Super Widescreen) - Highest priority
  if (playerStore.isWidescreenPinned) {
    return {
      top: '0',
      left: '0',
      width: '100%',
      aspectRatio: '2.39/1',
      position: 'fixed',
      zIndex: 10001,
      boxShadow: '0 4px 20px rgba(0,0,0,0.8)',
      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
    }
  }

  if (bounds) {
    return {
      top: bounds.top + 'px',
      left: bounds.left + 'px',
      width: bounds.width + 'px',
      height: bounds.height + 'px',
      position: 'fixed',
      zIndex: 1000,
      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
    }
  }
  // Mini mode (Floating PiP)
  return {
    bottom: '90px', // Above the bottom dock
    right: '20px',
    width: '280px',
    aspectRatio: '16/9',
    position: 'fixed',
    zIndex: 10002,
    borderRadius: '12px',
    overflow: 'hidden',
    boxShadow: '0 20px 40px rgba(0,0,0,0.6)',
    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
  }
})

function onTimeUpdate() {
  if (videoRef.value) {
    playerStore.currentTime = videoRef.value.currentTime
  }
}

function onLoadedMetadata() {
  if (videoRef.value) {
    playerStore.duration = videoRef.value.duration
    playerStore.loading = false
  }
}

function onVideoEnded() {
  if (playerStore.mode === 'video') {
    // If it's a Live TV track, we might wait for the store to handle next segment
    // or just let it loop if the store builds the schedule.
  }
}

function maximize() {
  router.push('/live-tv')
}

function onVideoClick() {
  if (!playerStore.heroBounds) {
    maximize()
  }
}

watch(() => playerStore.isPlaying, (playing) => {
  if (!videoRef.value) return
  if (playing && videoRef.value.paused) videoRef.value.play().catch(() => {})
  else if (!playing && !videoRef.value.paused) videoRef.value.pause()
})

onMounted(() => {
  playerStore.setVideoElement(videoRef.value)
})

watch(videoRef, (el) => {
  if (el) playerStore.setVideoElement(el)
})
</script>

<style scoped>
.global-tv-player {
  background: #000;
  pointer-events: auto;
}
.video-container {
  width: 100%;
  height: 100%;
  position: relative;
}
video {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}
.mini-controls {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.3);
  opacity: 0;
  transition: opacity 0.2s;
  display: flex;
  justify-content: space-between;
  padding: 8px;
}
.global-tv-player.mini:hover .mini-controls,
.global-tv-player.pinned:hover .mini-controls {
  opacity: 1;
}
.mini-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(255,255,255,0.2);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(5px);
}
.mini-btn:hover {
  background: rgba(255,255,255,0.4);
}
.video-loading {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.5);
  font-size: 24px;
  color: #fff;
}
.global-tv-player.mini {
  border: 1px solid rgba(255,255,255,0.1);
}
.global-tv-player.pinned {
  border-bottom: 2px solid rgba(255,255,255,0.1);
}
</style>
