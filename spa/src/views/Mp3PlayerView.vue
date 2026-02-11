<template>
  <div class="mp3-page">
    <section class="podcasts-hero mp3-hero">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-compact-disc" aria-hidden="true"></i> MP3 Player</h1>
        <p>Import &amp; play your local files · Experimental</p>
      </div>
    </section>

    <!-- Winamp-style player window (fills remaining space) -->
    <div class="winamp-window">
      <!-- Title bar -->
      <div class="winamp-titlebar">
        <span class="winamp-title-text">Ahoy MP3</span>
        <div class="winamp-title-buttons">
          <span class="winamp-btn winamp-min"></span>
          <span class="winamp-btn winamp-max"></span>
          <span class="winamp-btn winamp-close"></span>
        </div>
      </div>

      <!-- Main player area -->
      <div class="winamp-main">
        <!-- Equalizer display (visual flair) -->
        <div class="winamp-eq">
          <div
            v-for="(_, i) in 20"
            :key="i"
            class="winamp-eq-bar"
            :style="{ height: eqHeights[i] + '%' }"
          ></div>
        </div>

        <!-- Time & info -->
        <div class="winamp-info">
          <span class="winamp-time">{{ formatTime(localTime) }}</span>
          <span class="winamp-sep"> / </span>
          <span class="winamp-time">{{ formatTime(localDuration) }}</span>
        </div>
        <div class="winamp-now" v-if="currentEntry">
          {{ currentEntry.name }}
        </div>
        <div class="winamp-now winamp-now-empty" v-else>
          No file loaded
        </div>

        <!-- Progress bar -->
        <div class="winamp-progress-wrap" @click="onSeek" ref="seekRef">
          <div class="winamp-progress-track">
            <div class="winamp-progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
        </div>

        <!-- Transport controls -->
        <div class="winamp-controls">
          <button type="button" class="winamp-ctrl" @click="prev" :disabled="!canPrev" title="Previous">
            <i class="fas fa-backward-step"></i>
          </button>
          <button type="button" class="winamp-ctrl winamp-play" @click="togglePlay" :disabled="playlist.length === 0" :title="isPlaying ? 'Pause' : 'Play'">
            <i :class="isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
          </button>
          <button type="button" class="winamp-ctrl" @click="next" :disabled="!canNext" title="Next">
            <i class="fas fa-forward-step"></i>
          </button>
        </div>

        <!-- Volume -->
        <div class="winamp-volume-wrap">
          <i class="fas fa-volume-high winamp-vol-icon"></i>
          <input
            type="range"
            class="winamp-volume"
            min="0"
            max="100"
            v-model.number="volume"
            @input="onVolumeInput"
          />
        </div>
      </div>

      <!-- Playlist panel -->
      <div class="winamp-playlist-panel">
        <div class="winamp-playlist-header">
          <span>Playlist</span>
          <label class="winamp-add-files">
            <input type="file" accept="audio/mpeg,.mp3" multiple ref="fileInputRef" @change="onFilesSelected" />
            <i class="fas fa-folder-plus"></i> Add MP3s
          </label>
        </div>
        <div class="winamp-playlist-list" ref="playlistRef">
          <div
            v-for="(entry, idx) in playlist"
            :key="entry.id"
            class="winamp-playlist-item"
            :class="{ active: currentIndex === idx, playing: currentIndex === idx && isPlaying }"
            @dblclick="playIndex(idx)"
          >
            <span class="winamp-pl-index">{{ idx + 1 }}</span>
            <span class="winamp-pl-name">{{ entry.name }}</span>
            <span class="winamp-pl-duration">{{ entry.duration != null ? formatTime(entry.duration) : '…' }}</span>
          </div>
          <div v-if="playlist.length === 0" class="winamp-playlist-empty">
            Drop MP3 files or click “Add MP3s” to import from your computer.
          </div>
        </div>
      </div>
    </div>

    <p class="mp3-disclaimer">Files stay on your device. Nothing is uploaded. Experimental feature.</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const fileInputRef = ref(null)
const seekRef = ref(null)
const playlistRef = ref(null)

const playlist = ref([])
const currentIndex = ref(-1)
const isPlaying = ref(false)
const localTime = ref(0)
const localDuration = ref(0)
const volume = ref(80)
const eqHeights = ref(Array(20).fill(20))

let audio = null
let nextId = 1
let eqAnimationId = null

const currentEntry = computed(() => {
  if (currentIndex.value < 0 || currentIndex.value >= playlist.value.length) return null
  return playlist.value[currentIndex.value]
})

const progressPercent = computed(() => {
  if (!localDuration.value) return 0
  return (localTime.value / localDuration.value) * 100
})

const canPrev = computed(() => playlist.value.length > 0)
const canNext = computed(() => playlist.value.length > 0)

function formatTime(seconds) {
  if (!seconds || !isFinite(seconds)) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function getAudio() {
  if (!audio) {
    audio = new Audio()
    audio.addEventListener('timeupdate', () => { localTime.value = audio.currentTime })
    audio.addEventListener('loadedmetadata', () => { localDuration.value = audio.duration })
    audio.addEventListener('ended', () => next())
    audio.addEventListener('play', () => { isPlaying.value = true })
    audio.addEventListener('pause', () => { isPlaying.value = false })
    audio.addEventListener('error', () => { isPlaying.value = false })
  }
  return audio
}

function loadEntry(entry) {
  const a = getAudio()
  a.src = entry.url
  a.volume = volume.value / 100
  a.load()
  localDuration.value = entry.duration ?? 0
  localTime.value = 0
  a.play().catch(() => {})
}

function playIndex(idx) {
  if (idx < 0 || idx >= playlist.value.length) return
  currentIndex.value = idx
  loadEntry(playlist.value[idx])
}

function togglePlay() {
  if (playlist.value.length === 0) return
  const a = getAudio()
  if (currentIndex.value < 0) {
    playIndex(0)
    return
  }
  if (isPlaying.value) {
    a.pause()
  } else {
    a.play().catch(() => {})
  }
}

function prev() {
  if (playlist.value.length === 0) return
  const idx = currentIndex.value <= 0 ? playlist.value.length - 1 : currentIndex.value - 1
  playIndex(idx)
}

function next() {
  if (playlist.value.length === 0) return
  const idx = currentIndex.value < 0 ? 0 : (currentIndex.value + 1) % playlist.value.length
  playIndex(idx)
}

function onSeek(e) {
  const el = seekRef.value
  if (!el || !localDuration.value) return
  const rect = el.getBoundingClientRect()
  const x = e.clientX - rect.left
  const pct = Math.max(0, Math.min(1, x / rect.width))
  const a = getAudio()
  a.currentTime = pct * localDuration.value
  localTime.value = a.currentTime
}

function onVolumeInput() {
  getAudio().volume = volume.value / 100
}

function onFilesSelected(e) {
  const files = Array.from(e.target.files || [])
  e.target.value = ''
  if (!files.length) return
  files.forEach((file) => {
    if (!file.type.includes('audio') && !file.name.toLowerCase().endsWith('.mp3')) return
    const url = URL.createObjectURL(file)
    const name = file.name.replace(/\.mp3$/i, '')
    const entry = { id: nextId++, file, name, url, duration: null }
    playlist.value.push(entry)
    const a = new Audio()
    a.addEventListener('loadedmetadata', () => {
      entry.duration = a.duration
      a.src = ''
      a.load()
    })
    a.src = url
  })
  if (currentIndex.value < 0 && playlist.value.length > 0) {
    playIndex(0)
  }
}

function animateEq() {
  const h = eqHeights.value.slice()
  for (let i = 0; i < h.length; i++) {
    const base = isPlaying.value ? 15 + Math.sin(Date.now() / 80 + i * 0.5) * 35 + Math.random() * 20 : 12 + Math.random() * 8
    h[i] = Math.max(8, Math.min(95, base))
  }
  eqHeights.value = h
  eqAnimationId = requestAnimationFrame(animateEq)
}

onMounted(() => {
  animateEq()
})

onUnmounted(() => {
  if (eqAnimationId) cancelAnimationFrame(eqAnimationId)
  playlist.value.forEach((e) => URL.revokeObjectURL(e.url))
  if (audio) {
    audio.pause()
    audio.src = ''
  }
})
</script>

<style scoped>
.mp3-page {
  display: flex;
  flex-direction: column;
  min-height: 0;
  min-width: 0;
  flex: 1;
  background: #0e0e10;
  padding: 12px 12px 80px;
}

@media (min-width: 640px) {
  .mp3-page {
    padding: 20px 20px 80px;
  }
}

.mp3-hero.podcasts-hero {
  flex-shrink: 0;
}
.mp3-hero.podcasts-hero .podcasts-hero-inner h1 {
  margin: 0 0 6px 0;
  font-size: 22px;
  font-weight: 700;
}
@media (min-width: 640px) {
  .mp3-hero.podcasts-hero .podcasts-hero-inner h1 {
    font-size: 28px;
  }
}
.mp3-hero.podcasts-hero .podcasts-hero-inner p {
  margin: 0;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
}
@media (min-width: 640px) {
  .mp3-hero.podcasts-hero .podcasts-hero-inner p {
    font-size: inherit;
  }
}

/* Winamp-style window — responsive, fills parent */
.winamp-window {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: min(520px, 100%);
  margin: 0 auto 16px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 0 0 2px #1a1a1a, 0 8px 32px rgba(0, 0, 0, 0.6), 0 0 40px rgba(255, 153, 0, 0.08);
  font-family: 'Segoe UI', system-ui, sans-serif;
}

@media (min-width: 640px) {
  .winamp-window {
    max-width: min(560px, 100%);
    margin-bottom: 24px;
    border-radius: 8px;
  }
}

.winamp-titlebar {
  background: linear-gradient(180deg, #2d6a8a 0%, #1e4d63 50%, #163a4a 100%);
  color: #fff;
  padding: 6px 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.02em;
  border-bottom: 1px solid rgba(0, 0, 0, 0.3);
}

.winamp-title-buttons {
  display: flex;
  gap: 6px;
}
.winamp-btn {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(0, 0, 0, 0.2);
}
.winamp-close { background: #c43c3c; }
.winamp-max { background: #3c8c3c; }
.winamp-min { background: #c4a43c; }

.winamp-main {
  background: linear-gradient(180deg, #1a1a1e 0%, #0f0f12 100%);
  padding: 16px;
  border-left: 1px solid rgba(255, 153, 0, 0.15);
  border-right: 1px solid rgba(255, 153, 0, 0.15);
  border-bottom: 1px solid rgba(0, 0, 0, 0.4);
}

/* Equalizer bars */
.winamp-eq {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 3px;
  height: 32px;
  margin-bottom: 12px;
}
.winamp-eq-bar {
  width: 8px;
  min-height: 4px;
  background: linear-gradient(180deg, #ff9900 0%, #cc7a00 50%, #995c00 100%);
  border-radius: 2px;
  transition: height 0.08s ease-out;
  box-shadow: 0 0 6px rgba(255, 153, 0, 0.4);
}

.winamp-info {
  font-size: 12px;
  color: #ff9900;
  margin-bottom: 4px;
  font-variant-numeric: tabular-nums;
}
.winamp-sep { color: rgba(255, 153, 0, 0.5); }
.winamp-now {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 10px;
}
.winamp-now-empty {
  color: rgba(255, 255, 255, 0.35);
  font-style: italic;
}

.winamp-progress-wrap {
  height: 12px;
  margin-bottom: 14px;
  cursor: pointer;
  border-radius: 4px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.4);
}
.winamp-progress-track {
  height: 100%;
  background: rgba(255, 153, 0, 0.2);
  position: relative;
}
.winamp-progress-fill {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  background: linear-gradient(90deg, #ff9900, #ffbb44);
  border-radius: 4px;
  transition: width 0.1s linear;
}

.winamp-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}
.winamp-ctrl {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(180deg, #2a2a2e 0%, #1a1a1e 100%);
  color: rgba(255, 255, 255, 0.85);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06), 0 2px 8px rgba(0, 0, 0, 0.5);
  transition: background 0.15s, color 0.15s;
}
.winamp-ctrl:hover:not(:disabled) {
  background: linear-gradient(180deg, #333338 0%, #222226 100%);
  color: #ff9900;
}
.winamp-ctrl:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.winamp-play {
  width: 52px;
  height: 52px;
  font-size: 20px;
  background: linear-gradient(180deg, #ff9900 0%, #cc7a00 50%, #995c00 100%);
  color: #0f0f12;
  box-shadow: 0 0 20px rgba(255, 153, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.25);
}
.winamp-play:hover:not(:disabled) {
  background: linear-gradient(180deg, #ffaa22 0%, #dd8a00 50%, #aa6c00 100%);
  color: #0f0f12;
  box-shadow: 0 0 24px rgba(255, 153, 0, 0.5);
}

.winamp-volume-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}
.winamp-vol-icon {
  color: rgba(255, 153, 0, 0.7);
  font-size: 14px;
}
.winamp-volume {
  flex: 1;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 3px;
}
.winamp-volume::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #ff9900;
  cursor: pointer;
  box-shadow: 0 0 8px rgba(255, 153, 0, 0.5);
}
.winamp-volume::-moz-range-thumb {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #ff9900;
  cursor: pointer;
  border: none;
}

/* Playlist panel — fills remaining space, scrolls */
.winamp-playlist-panel {
  background: linear-gradient(180deg, #141418 0%, #0c0c0e 100%);
  border-top: 1px solid rgba(255, 153, 0, 0.12);
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

@media (min-width: 640px) {
  .winamp-playlist-panel {
    max-height: 360px;
  }
}

.winamp-playlist-header {
  padding: 10px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.winamp-add-files {
  cursor: pointer;
  color: #ff9900;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.winamp-add-files input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
}
.winamp-add-files:hover {
  color: #ffaa22;
}

.winamp-playlist-list {
  overflow-y: auto;
  flex: 1;
  min-height: 120px;
}
.winamp-playlist-item {
  display: grid;
  grid-template-columns: 28px 1fr auto;
  gap: 8px;
  align-items: center;
  padding: 8px 14px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  transition: background 0.12s;
}
.winamp-playlist-item:hover {
  background: rgba(255, 153, 0, 0.08);
}
.winamp-playlist-item.active {
  background: rgba(255, 153, 0, 0.15);
  color: #ff9900;
}
.winamp-playlist-item.playing {
  color: #ffbb44;
  font-weight: 600;
}
.winamp-pl-index {
  font-variant-numeric: tabular-nums;
  color: rgba(255, 255, 255, 0.4);
  font-size: 11px;
}
.winamp-pl-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.winamp-pl-duration {
  font-variant-numeric: tabular-nums;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.winamp-playlist-empty {
  padding: 24px 16px;
  text-align: center;
  color: rgba(255, 255, 255, 0.35);
  font-size: 13px;
  line-height: 1.5;
}

.mp3-disclaimer {
  flex-shrink: 0;
  text-align: center;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  margin: 0 0 8px;
}

@media (min-width: 640px) {
  .mp3-disclaimer {
    font-size: 12px;
    margin-bottom: 0;
  }
}
</style>
