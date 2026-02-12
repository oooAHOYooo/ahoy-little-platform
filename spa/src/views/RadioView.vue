<template>
  <div class="radio-page radio-page--v2">
    <!-- Subpage hero (same as Flask subpage_hero) -->
    <section class="podcasts-hero radio-page-header">
      <div class="podcasts-hero-inner">
        <h1>
          <i class="fas fa-broadcast-tower" aria-hidden="true"></i>
          Radio
        </h1>
        <p>Live radio feed and indie discovery.</p>
      </div>
    </section>

    <!-- Big radio hero card – station art, Live Now, primary CTA -->
    <section class="radio-hero">
      <div class="radio-hero-inner">
        <div class="radio-hero-grid">
          <div class="radio-hero-art">
            <img
              :src="currentCover"
              alt="Station artwork"
            />
          </div>
          <div class="radio-hero-copy">
            <div class="radio-live">
              <span class="radio-live-dot" :class="{ 'radio-live-dot--on': playerStore.isPlaying }"></span>
              <span>Live Now</span>
            </div>
            <div class="radio-eq" aria-hidden="true">
              <span></span><span></span><span></span><span></span>
              <span></span><span></span><span></span><span></span>
            </div>
            <h1 class="radio-hero-title desktop-only">{{ stationName }}</h1>
            <p class="radio-hero-subtitle desktop-only">{{ stationTagline }}</p>
            <div class="radio-hero-actions">
              <button type="button" class="radio-cta" @click="toggleRadio">
                <i class="fas radio-cta-icon" :class="playerStore.isPlaying ? 'fa-pause' : 'fa-play'"></i>
                <span>{{ playerStore.isPlaying ? 'Pause' : 'Listen Now' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section v-if="current" class="radio-now">
      <h3 class="radio-section-title">Currently Playing</h3>
      <div class="radio-track-card">
        <div class="radio-track-main">
          <img
            class="radio-track-cover"
            :src="current.cover_art || current.artwork || defaultCover"
            alt="cover"
          />
          <div class="radio-track-info">
            <h4 class="radio-track-title">{{ current.title || '—' }}</h4>
            <div class="radio-track-artist">{{ current.artist || '—' }}</div>
            <div class="radio-track-meta">
              <template v-if="current.album"><span>Album: {{ current.album }}</span></template>
              <template v-if="current.year"><span>{{ current.year }}</span></template>
              <template v-if="durationSec"><span>{{ formatTime(durationSec) }}</span></template>
            </div>
          </div>
          <div class="radio-track-actions">
            <button type="button" class="radio-icon-btn" title="Boost" @click="boostArtist(current)">
              <i class="fas fa-bolt"></i>
            </button>
            <button type="button" class="radio-icon-btn queue-btn" title="Add to queue" @click="addToQueue(current)">
              <i class="fas fa-plus"></i>
            </button>
          </div>
        </div>
        <div class="radio-progress-wrap">
          <div class="radio-progress-times">
            <span>{{ formatTime(playerStore.currentTime) }}</span>
            <span>{{ formatTime(durationSec) }}</span>
          </div>
          <div class="radio-progress-bar" @click="seekFromClick">
            <div class="radio-progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
        </div>
      </div>
    </section>

    <section class="radio-justplayed">
      <h3 class="radio-section-title">Previously Played</h3>
      <div class="playing-list">
        <div
          v-for="item in justPlayedSlice"
          :key="item.id"
          class="playing-item"
          :style="playingItemStyle(item)"
          @click="playNow(item)"
        >
          <div class="item-details">
            <h4>{{ item.title }}</h4>
            <p>{{ item.artist }}</p>
          </div>
          <div class="play-indicator"><i class="fas fa-play"></i></div>
        </div>
      </div>
      <p v-if="!justPlayedSlice.length" class="radio-empty-hint">Tracks you play will appear here.</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'
import { usePlayerStore } from '../stores/player'

const DEFAULT_COVER = 'https://ahoy.ooo/images/Ahoy-Indie-Media-DEFAULT-COVER-A-8.jpg'

const playerStore = usePlayerStore()
const allTracks = ref([])
const justPlayed = ref([])

const stationName = 'Indie Rock Station'
const stationTagline = 'Independent and alternative rock music, curated by music lovers.'
const defaultCover = DEFAULT_COVER

const current = computed(() => playerStore.currentTrack)

const currentCover = computed(() => {
  const t = playerStore.currentTrack
  if (t?.cover_art || t?.artwork) return t.cover_art || t.artwork
  const first = allTracks.value[0]
  return first?.cover_art || defaultCover
})

const durationSec = computed(() => playerStore.duration || 0)
const progressPercent = computed(() => playerStore.progress ?? 0)

const justPlayedSlice = computed(() => justPlayed.value.slice(0, 8))

function formatTime(sec) {
  const s = Math.max(0, Math.floor(Number(sec) || 0))
  const m = Math.floor(s / 60)
  const r = s % 60
  return `${String(m).padStart(2, '0')}:${String(r).padStart(2, '0')}`
}

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function buildQueue() {
  const list = allTracks.value.filter((t) => t.audio_url || t.preview_url)
  const deduped = []
  const seen = new Set()
  for (const t of list) {
    if (seen.has(t.id)) continue
    seen.add(t.id)
    deduped.push(t)
  }
  const shuffled = shuffle(deduped)
  playerStore.setQueue(shuffled, 0)
}

function toggleRadio() {
  if (playerStore.isPlaying) {
    playerStore.pause()
    return
  }
  if (playerStore.currentTrack) {
    playerStore.play()
    return
  }
  if (allTracks.value.length) buildQueue()
}

function playNow(item) {
  const prev = playerStore.currentTrack
  if (prev && prev.id !== item.id) {
    justPlayed.value = [prev, ...justPlayed.value].slice(0, 20)
  }
  playerStore.play(item)
}

function seekFromClick(e) {
  const bar = e.currentTarget
  const rect = bar.getBoundingClientRect()
  const x = Math.min(rect.width, Math.max(0, e.clientX - rect.left))
  const pct = rect.width ? (x / rect.width) * 100 : 0
  playerStore.seek(pct)
}

function addToQueue(item) {
  playerStore.addToQueue(item)
  window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Added to queue' } }))
}

function boostArtist() {
  window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Boost coming soon' } }))
}

function playingItemStyle(item) {
  const url = item.cover_art || item.artwork || defaultCover
  return {
    backgroundImage: `linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.8)), url(${url})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
  }
}

// When current track changes, push previous to justPlayed
watch(
  () => playerStore.currentTrack,
  (next, prev) => {
    if (prev && next && prev.id !== next.id) {
      justPlayed.value = [prev, ...justPlayed.value].slice(0, 20)
    }
  }
)

onMounted(async () => {
  const data = await apiFetchCached('/api/music').catch(() => ({ tracks: [] }))
  const raw = data.tracks || []
  const withAudio = raw.filter((t) => t.audio_url || t.preview_url)
  const seen = new Set()
  allTracks.value = withAudio.filter((t) => {
    if (seen.has(t.id)) return false
    seen.add(t.id)
    return true
  })
})
</script>

<style scoped>
.radio-page--v2 {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.25rem 1.25rem 3rem;
  background: transparent;
}
.radio-page--v2 button {
  width: auto !important;
  min-height: unset;
}

.radio-page-header {
  margin-bottom: 18px;
}
.radio-page-header.podcasts-hero .podcasts-hero-inner h1 {
  margin: 0 0 6px 0;
  font-size: 28px;
  font-weight: 700;
}
.radio-page-header.podcasts-hero .podcasts-hero-inner p {
  margin: 0;
  color: rgba(255, 255, 255, 0.68);
}

.radio-hero {
  border-radius: 24px;
  overflow: hidden;
  position: relative;
  margin-bottom: 8px;
  background: linear-gradient(180deg, rgba(18, 18, 18, 1) 0%, rgba(10, 10, 10, 1) 100%);
  border: 1px solid rgba(255, 255, 255, 0.04);
  box-shadow: 0 22px 44px rgba(0, 0, 0, 0.6), inset 6px 6px 14px rgba(255, 255, 255, 0.03), inset -8px -8px 18px rgba(0, 0, 0, 0.8);
}
.radio-hero-inner {
  padding: 28px 28px 26px;
  position: relative;
  z-index: 1;
}
.radio-hero-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 28px;
  align-items: center;
}
.radio-hero-art {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.02);
  box-shadow: inset 4px 4px 10px rgba(255, 255, 255, 0.04), inset -6px -6px 12px rgba(0, 0, 0, 0.8);
}
.radio-hero-art img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.radio-live {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(210, 210, 210, 0.7);
  margin-bottom: 8px;
  font-size: 0.78rem;
  font-family: "SF Mono", "Menlo", "Monaco", "Consolas", monospace;
}
.radio-live-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: rgba(210, 210, 210, 0.7);
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
  transition: opacity 0.2s, box-shadow 0.2s;
}
.radio-live-dot--on {
  background: rgba(80, 200, 120, 0.9);
  box-shadow: 0 0 12px rgba(80, 200, 120, 0.5);
  animation: radio-live-pulse 1.2s ease-in-out infinite;
}
@keyframes radio-live-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.85; transform: scale(1.08); }
}
.radio-hero-title {
  margin: 0;
  font-size: clamp(2.1rem, 4.2vw, 3.6rem);
  line-height: 1.05;
  letter-spacing: 0.02em;
  color: rgba(230, 230, 230, 0.96);
  font-weight: 800;
  text-transform: uppercase;
}
.radio-hero-subtitle {
  margin: 12px 0 0;
  max-width: 58ch;
  color: rgba(180, 180, 180, 0.7);
  font-size: 1rem;
  line-height: 1.5;
}
.radio-eq {
  display: inline-flex;
  align-items: flex-end;
  gap: 6px;
  height: 34px;
  margin: 6px 0 12px;
}
.radio-eq span {
  width: 6px;
  border-radius: 3px;
  background: linear-gradient(180deg, rgba(230, 230, 230, 0.9) 0%, rgba(160, 160, 160, 0.75) 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2);
  opacity: 0.85;
}
.radio-eq span:nth-child(1) { height: 10px; }
.radio-eq span:nth-child(2) { height: 18px; }
.radio-eq span:nth-child(3) { height: 26px; }
.radio-eq span:nth-child(4) { height: 16px; }
.radio-eq span:nth-child(5) { height: 22px; }
.radio-eq span:nth-child(6) { height: 14px; }
.radio-eq span:nth-child(7) { height: 24px; }
.radio-eq span:nth-child(8) { height: 12px; }
.radio-hero-actions {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-top: 24px;
}
/* Big primary CTA – Listen Now / Pause (Flask radio vibe) */
.radio-cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  min-height: 56px;
  padding: 16px 28px;
  border-radius: 12px;
  font-size: 1.05rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: linear-gradient(180deg, rgba(75, 75, 75, 0.98) 0%, rgba(48, 48, 48, 0.98) 100%);
  color: rgba(240, 240, 240, 0.98);
  box-shadow: 6px 6px 20px rgba(0, 0, 0, 0.7), -4px -4px 12px rgba(255, 255, 255, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  cursor: pointer;
  font-family: "SF Mono", "Menlo", "Monaco", "Consolas", monospace;
  transition: transform 0.15s, box-shadow 0.2s, background 0.2s;
}
.radio-cta:hover {
  background: linear-gradient(180deg, rgba(85, 85, 85, 0.98) 0%, rgba(55, 55, 55, 0.98) 100%);
  box-shadow: 8px 8px 24px rgba(0, 0, 0, 0.6), -4px -4px 12px rgba(255, 255, 255, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.12);
}
.radio-cta:active {
  transform: translateY(2px);
  box-shadow: inset 4px 4px 12px rgba(0, 0, 0, 0.8), inset -2px -2px 6px rgba(255, 255, 255, 0.05);
}
.radio-cta-icon {
  font-size: 1.2rem;
}

.radio-section-title {
  margin: 26px 0 12px;
  font-size: 1.35rem;
  letter-spacing: 0.12em;
  color: rgba(200, 200, 200, 0.85);
  font-weight: 700;
  text-transform: uppercase;
  font-family: "SF Mono", "Menlo", "Monaco", "Consolas", monospace;
}
.radio-track-card {
  background: linear-gradient(180deg, rgba(22, 22, 22, 0.98) 0%, rgba(14, 14, 14, 0.98) 100%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 16px 16px 28px rgba(0, 0, 0, 0.65), -6px -6px 14px rgba(255, 255, 255, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}
.radio-track-main {
  display: grid;
  grid-template-columns: 86px 1fr auto;
  gap: 16px;
  align-items: center;
  padding: 16px 18px 10px;
}
.radio-track-cover {
  width: 74px;
  height: 74px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.45);
  box-shadow: inset 4px 4px 8px rgba(0, 0, 0, 0.6), inset -2px -2px 6px rgba(255, 255, 255, 0.04);
}
.radio-track-title {
  margin: 0;
  font-weight: 800;
  color: rgba(225, 225, 225, 0.95);
  letter-spacing: 0.02em;
  font-size: 1.35rem;
  line-height: 1.2;
  text-transform: uppercase;
}
.radio-track-artist {
  margin: 6px 0 0;
  color: rgba(180, 180, 180, 0.7);
  font-weight: 600;
  font-size: 0.98rem;
}
.radio-track-meta {
  margin: 8px 0 0;
  color: rgba(150, 150, 150, 0.6);
  font-size: 0.86rem;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  font-family: "SF Mono", "Menlo", "Monaco", "Consolas", monospace;
}
.radio-track-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}
.radio-icon-btn {
  width: 48px !important;
  height: 48px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(52, 52, 52, 0.95) 0%, rgba(34, 34, 34, 0.95) 100%);
  color: rgba(215, 215, 215, 0.92);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 6px 6px 12px rgba(0, 0, 0, 0.75), -3px -3px 8px rgba(255, 255, 255, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.08);
}
.radio-icon-btn:hover {
  background: linear-gradient(180deg, rgba(60, 60, 60, 0.95) 0%, rgba(34, 34, 34, 0.95) 100%);
}
.radio-track-actions .radio-icon-btn {
  width: 44px !important;
  height: 44px;
  background: linear-gradient(180deg, rgba(50, 50, 50, 0.95) 0%, rgba(34, 34, 34, 0.95) 100%);
}
.radio-progress-wrap {
  padding: 10px 18px 16px;
}
.radio-progress-times {
  display: flex;
  justify-content: space-between;
  color: rgba(170, 170, 170, 0.65);
  font-size: 0.86rem;
  margin-bottom: 10px;
  font-family: "SF Mono", "Menlo", "Monaco", "Consolas", monospace;
}
.radio-progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: inset 3px 3px 6px rgba(0, 0, 0, 0.7), inset -2px -2px 4px rgba(255, 255, 255, 0.04);
}
.radio-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, rgba(220, 220, 220, 0.9) 0%, rgba(160, 160, 160, 0.9) 60%, rgba(120, 120, 120, 0.85) 100%);
  border-radius: 6px;
  transition: width 0.12s linear;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.18);
}

.playing-list {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}
.playing-item {
  position: relative;
  border-radius: 12px;
  min-height: 130px;
  overflow: hidden;
  color: #fff;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  box-shadow: 12px 12px 20px rgba(0, 0, 0, 0.6), -6px -6px 12px rgba(255, 255, 255, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}
.playing-item .item-details {
  position: absolute;
  left: 14px;
  right: 14px;
  bottom: 12px;
}
.playing-item h4 {
  margin: 0;
  font-weight: 700;
  font-size: 0.98rem;
  line-height: 1.2;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: rgba(220, 220, 220, 0.95);
}
.playing-item p {
  margin: 6px 0 0;
  color: rgba(180, 180, 180, 0.75);
  font-weight: 600;
  font-size: 0.88rem;
}
.play-indicator {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: linear-gradient(180deg, rgba(58, 58, 58, 0.95) 0%, rgba(36, 36, 36, 0.95) 100%);
  box-shadow: 6px 6px 10px rgba(0, 0, 0, 0.7), -3px -3px 8px rgba(255, 255, 255, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.08);
}
.radio-empty-hint {
  color: rgba(160, 160, 160, 0.7);
  font-size: 0.9rem;
  margin: 12px 0 0;
}

@media (max-width: 980px) {
  .radio-hero-grid { grid-template-columns: 220px 1fr; }
}
@media (max-width: 820px) {
  .radio-page--v2 { padding: 1rem 1rem 2.5rem; }
  .radio-hero-inner { padding: 20px 18px 22px; }
  .radio-hero-grid { grid-template-columns: 1fr; }
  .radio-hero-art { max-width: 320px; margin: 0 auto; }
  .radio-hero-actions { flex-wrap: wrap; }
  .radio-cta {
    width: 100% !important;
    min-height: 52px;
    justify-content: center;
    padding: 14px 20px;
  }
  .playing-list { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .radio-track-main { grid-template-columns: 76px 1fr; }
  .radio-track-actions { grid-column: 1 / -1; justify-content: flex-end; }
}
</style>
