<template>
  <div class="now-playing-page" v-if="playerStore.currentTrack">
    <!-- Album art — large, centered -->
    <div class="np-artwork-container">
      <img
        :src="playerStore.currentTrack.cover_art || playerStore.currentTrack.thumbnail || playerStore.currentTrack.artwork || '/static/img/default-cover.jpg'"
        :alt="playerStore.currentTrack.title"
        class="np-artwork"
      />
    </div>

    <!-- Track info -->
    <div class="np-info">
      <h1 class="np-title">{{ playerStore.currentTrack.title }}</h1>
      <p class="np-artist">{{ playerStore.currentTrack.artist || '' }}</p>
    </div>

    <!-- Seek bar -->
    <div class="np-seek">
      <div class="np-seek-bar" @click="onSeek" ref="seekBar">
        <div class="np-seek-fill" :style="{ width: playerStore.progress + '%' }"></div>
        <div class="np-seek-thumb" :style="{ left: playerStore.progress + '%' }"></div>
      </div>
      <div class="np-times">
        <span>{{ formatTime(playerStore.currentTime) }}</span>
        <span>{{ formatTime(playerStore.duration) }}</span>
      </div>
    </div>

    <!-- Controls -->
    <div class="np-controls">
      <button class="np-btn np-btn-secondary" @click="playerStore.previous()" aria-label="Previous">
        <i class="fas fa-backward-step"></i>
      </button>
      <button class="np-btn np-btn-play" @click="playerStore.togglePlay()" aria-label="Play/Pause">
        <i :class="playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'" style="margin-left:2px"></i>
      </button>
      <button class="np-btn np-btn-secondary" @click="playerStore.next()" aria-label="Next">
        <i class="fas fa-forward-step"></i>
      </button>
    </div>

    <!-- Actions row -->
    <div class="np-actions">
      <button class="np-action-btn" @click="onBookmark" :title="bookmarks.isBookmarked(playerStore.currentTrack) ? 'Saved' : 'Save'">
        <i :class="bookmarks.isBookmarked(playerStore.currentTrack) ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
      </button>
      <button class="np-action-btn" @click="onSpeedCycle" :title="`Speed: ${playbackSpeed}x`">
        <span class="np-speed-label">{{ playbackSpeed }}x</span>
      </button>
      <button class="np-action-btn" @click="onSleepTimer" :title="sleepActive ? 'Sleep timer on' : 'Sleep timer'">
        <i class="fas fa-moon" :style="{ color: sleepActive ? 'var(--accent-primary, #6ddcff)' : '' }"></i>
      </button>
      <button class="np-action-btn" @click="onShare">
        <i class="fas fa-share-alt"></i>
      </button>
    </div>

    <!-- Queue preview -->
    <div class="np-queue" v-if="upNext.length">
      <h3 class="np-queue-title">Up Next</h3>
      <div class="np-queue-list">
        <div
          v-for="(track, idx) in upNext"
          :key="track.id"
          class="np-queue-item"
          @click="playFromQueue(idx)"
        >
          <img :src="track.cover_art || track.artwork || '/static/img/default-cover.jpg'" class="np-queue-art" />
          <div class="np-queue-info">
            <div class="np-queue-track">{{ track.title }}</div>
            <div class="np-queue-artist">{{ track.artist }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- No track -->
  <div class="now-playing-page" v-else style="display:flex;align-items:center;justify-content:center;min-height:60vh">
    <div style="text-align:center;color:rgba(255,255,255,0.4)">
      <i class="fas fa-music" style="font-size:48px;margin-bottom:16px;display:block"></i>
      <p>No track playing</p>
      <router-link to="/music" style="color:var(--accent-primary, #6ddcff);margin-top:12px;display:inline-block">Browse Music</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { usePlayerStore } from '../stores/player'
import { useBookmarks } from '../composables/useBookmarks'
import { useShare, useHaptics, useSleepTimer, usePlaybackSpeed } from '../composables/useNative'

const playerStore = usePlayerStore()
const bookmarks = useBookmarks()
const { shareTrack } = useShare()
const haptics = useHaptics()
const sleepTimer = useSleepTimer()

const playbackSpeed = ref(1)
const sleepActive = ref(false)

// Get the raw Audio element for speed control
const speedCtrl = usePlaybackSpeed(() => playerStore.getAudioElement())

const upNext = computed(() => {
  if (!playerStore.currentTrack || !playerStore.queue.length) return []
  const idx = playerStore.queue.findIndex(t => t.id === playerStore.currentTrack.id)
  return playerStore.queue.slice(idx + 1, idx + 6)
})

function formatTime(seconds) {
  if (!seconds || !isFinite(seconds)) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function onSeek(e) {
  const rect = e.currentTarget.getBoundingClientRect()
  const percent = ((e.clientX - rect.left) / rect.width) * 100
  playerStore.seek(Math.max(0, Math.min(100, percent)))
}

function onBookmark() {
  haptics.onBookmark()
  bookmarks.toggle({ ...playerStore.currentTrack, _type: 'track' })
  const saved = bookmarks.isBookmarked(playerStore.currentTrack)
  window.dispatchEvent(new CustomEvent('ahoy:toast', {
    detail: { message: saved ? 'Saved to library' : 'Removed from library', type: 'bookmark' }
  }))
}

function onShare() {
  haptics.light()
  shareTrack(playerStore.currentTrack)
}

function onSpeedCycle() {
  haptics.light()
  playbackSpeed.value = speedCtrl.cycle(playbackSpeed.value)
  window.dispatchEvent(new CustomEvent('ahoy:toast', {
    detail: { message: `Speed: ${playbackSpeed.value}x`, type: 'info' }
  }))
}

function onSleepTimer() {
  haptics.light()
  if (sleepTimer.isActive()) {
    sleepTimer.clear()
    sleepActive.value = false
    window.dispatchEvent(new CustomEvent('ahoy:toast', {
      detail: { message: 'Sleep timer off', type: 'info' }
    }))
  } else {
    // 30-minute sleep timer
    sleepTimer.start(30, () => {
      playerStore.pause()
      sleepActive.value = false
      window.dispatchEvent(new CustomEvent('ahoy:toast', {
        detail: { message: 'Sleep timer: pausing playback', type: 'info' }
      }))
    })
    sleepActive.value = true
    window.dispatchEvent(new CustomEvent('ahoy:toast', {
      detail: { message: 'Sleep timer: 30 minutes', type: 'info' }
    }))
  }
}

function playFromQueue(idx) {
  const currentIdx = playerStore.queue.findIndex(t => t.id === playerStore.currentTrack?.id)
  playerStore.setQueue(playerStore.queue, currentIdx + 1 + idx)
}
</script>
