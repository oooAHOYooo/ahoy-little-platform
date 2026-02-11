<template>
  <div class="tv-container">
    <!-- Subpage hero (same as Flask) -->
    <section class="podcasts-hero">
      <div class="podcasts-hero-inner">
        <h1>
          <i class="fas fa-tv" aria-hidden="true"></i>
          Live TV
        </h1>
        <p>Channel surf and watch live programming.</p>
      </div>
    </section>

    <div class="video-spotlight">
      <div class="spotlight-grid">
        <div class="spotlight-left">
          <!-- Hero video player with glass gradient -->
          <div class="panelstream-player hero-player">
            <video
              ref="videoEl"
              controls
              autoplay
              muted
              playsinline
              webkit-playsinline
              @play="isPlaying = true"
              @pause="isPlaying = false"
              @ended="onVideoEnded"
              @error="resyncVideo"
              @stalled="resyncVideo"
            ></video>
            <div class="video-header">
              <span class="now-playing-label">Now Playing</span>
              <span class="channel-name-label" aria-live="polite">{{ channelLabel }}</span>
            </div>
            <div class="hero-glass"></div>
          </div>

          <!-- Remote controls below video -->
          <div class="channel-remote remote-below" aria-label="Channel Controls">
            <button type="button" class="remote-btn" title="Play/Pause" @click="togglePlay">
              <i :class="isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
            </button>
            <button type="button" class="remote-btn" title="Mute" @click="toggleMute">
              <i :class="isMuted ? 'fas fa-volume-mute' : 'fas fa-volume-up'"></i>
            </button>
            <button type="button" class="remote-btn" title="Fullscreen" @click="toggleFullscreen">
              <i class="fas fa-expand"></i>
            </button>
            <button type="button" class="remote-btn" title="Go to Guide" @click="scrollToGuide">
              <i class="fas fa-list"></i>
            </button>
            <button type="button" class="remote-btn" title="Channel Up" @click="channelUp">
              <i class="fas fa-chevron-up"></i>
            </button>
            <button type="button" class="remote-btn" title="Channel Down" @click="channelDown">
              <i class="fas fa-chevron-down"></i>
            </button>
          </div>

          <!-- Playing now bar with progress -->
          <div class="playing-now glass">
            <img :src="nowThumb" alt="" />
            <div class="now-col">
              <div class="np-title">{{ nowTitle }}</div>
              <div class="np-sub">{{ nowMeta }}</div>
            </div>
            <div class="next-col">
              <div class="np-label">Up Next</div>
              <div class="np-next">{{ upNextTitle }}</div>
            </div>
            <div class="ltv-progress-wrap"><div class="ltv-progress" :style="{ width: progressPct + '%' }"></div></div>
          </div>
        </div>

        <!-- Right dashboard (hidden on mobile) -->
        <aside class="right-dashboard glass hidden-mobile" aria-label="Channel Dashboard">
          <img :src="nowThumb" alt="" class="rd-thumb" />
          <div class="rd-now">
            <div class="rd-label">Playing Now</div>
            <div class="rd-title">{{ nowTitle }}</div>
            <div class="rd-meta"><span>{{ nowMeta }}</span></div>
          </div>
          <div class="rd-next">
            <div class="rd-label">Up Next</div>
            <div class="rd-title">{{ upNextTitle }}</div>
          </div>
        </aside>
      </div>
    </div>

    <!-- Channel selector -->
    <div id="channel-selector">
      <template v-if="loading">
        <div v-for="i in 4" :key="'skeleton-' + i" class="channel-button" style="pointer-events:none">
          <div class="skeleton" style="height:20px;width:70%;margin-bottom:8px"></div>
          <div class="skeleton" style="height:14px;width:50%"></div>
        </div>
      </template>
      <template v-else-if="channels.length === 0">
        <div class="channel-selector-empty">
          <p class="channel-selector-empty-text">{{ loadError ? 'Couldn\'t load channels' : 'No channels available' }}</p>
          <p v-if="loadError" class="channel-selector-empty-hint">Check your connection and try again.</p>
          <button type="button" class="channel-selector-retry" @click="loadChannels">
            <i class="fas fa-sync-alt"></i> Retry
          </button>
        </div>
      </template>
      <button
        v-else
        v-for="(ch, idx) in channels"
        :key="ch.id"
        type="button"
        class="channel-button"
        :class="{ active: selectedRow === idx }"
        @click="selectChannel(idx)"
        @mouseenter="startHoverPreview($event, idx)"
        @mouseleave="hideHoverPreview"
      >
        <div class="channel-button-name">{{ rowLabels[idx] || ch.name }}</div>
        <div class="channel-button-next">{{ channelNowTitle(idx) }}</div>
      </button>
    </div>

    <!-- Hover preview tooltip -->
    <div
      v-if="hoverPreview.visible"
      class="live-tv-channel-preview visible"
      :style="{ left: hoverPreview.x + 'px', top: hoverPreview.y + 'px' }"
      aria-hidden="true"
    >
      <img :src="hoverPreview.thumb" alt="" />
      <div class="live-tv-channel-preview-title">{{ hoverPreview.title }}</div>
      <div class="live-tv-channel-preview-meta">{{ hoverPreview.meta }}</div>
    </div>

    <!-- TV Guide section -->
    <div ref="guideRef" class="live-tv-container" aria-label="TV Guide">
      <aside class="live-tv-sidebar" :class="{ open: mobileDrawerOpen }" aria-label="Channels">
        <ul class="channel-list" role="listbox" aria-label="Live TV Channels">
          <li
            v-for="(ch, idx) in channels"
            :key="ch.id"
            class="channel-item"
            role="option"
            :aria-selected="String(selectedRow === idx)"
            tabindex="0"
            @click="selectChannel(idx)"
            @keydown.enter="selectChannel(idx)"
          >
            <span class="channel-pill" :style="{ background: pillColors[idx % 4] }"></span>
            <span class="channel-name">{{ ch.name }}</span>
          </li>
        </ul>
      </aside>

      <section class="live-tv-main">
        <!-- Mobile channels toggle -->
        <div class="mobile-only" style="padding:8px 10px;">
          <button class="channels-btn" type="button" @click="mobileDrawerOpen = true">
            <i class="fas fa-list"></i> Channels
          </button>
        </div>

        <div class="guide">
          <div class="guide-header">
            <div>Guide</div>
            <div class="kbd-hint" aria-hidden="true">
              <span>Navigate</span>
              <span class="kbd">&uarr;</span><span class="kbd">&darr;</span>
              <span class="kbd">&larr;</span><span class="kbd">&rarr;</span>
              <span>Tune to channel</span>
              <span class="kbd">Enter</span>
            </div>
          </div>
          <div class="guide-timebar">
            <div v-for="t in timeMarkers" :key="t" class="time-marker" :style="{ minWidth: (30 * pxPerMinute) + 'px' }">{{ t }}</div>
          </div>
          <div class="guide-scroller">
            <div class="guide-rows" role="grid" aria-label="Channel Guide">
              <div class="now-line" :style="{ left: '150px' }"></div>
              <div v-for="(ch, rowIdx) in channels" :key="ch.id" class="guide-row" role="row">
                <div class="guide-channel-label">
                  <span class="guide-channel-icon" :style="{ background: pillColors[rowIdx % 4] }"></span>
                  <span>{{ ch.name }}</span>
                </div>
                <div class="guide-track">
                  <div
                    v-for="(prog, colIdx) in guidePrograms[rowIdx] || []"
                    :key="rowIdx + '-' + colIdx"
                    class="program"
                    :class="{ selected: guideFocus.row === rowIdx && guideFocus.col === colIdx }"
                    :style="{ width: prog.widthPx + 'px' }"
                    :data-row="rowIdx"
                    :data-col="colIdx"
                    tabindex="0"
                    role="gridcell"
                    :aria-label="prog.title + ' • ' + prog.durMin + ' min'"
                    @click="setGuideFocus(rowIdx, colIdx); selectChannel(rowIdx)"
                    @keydown.enter="setGuideFocus(rowIdx, colIdx); selectChannel(rowIdx)"
                  >
                    <img class="program-thumb" :src="prog.thumbnail" :alt="prog.title" loading="lazy" />
                    <div class="program-title">{{ prog.title }}</div>
                    <div class="program-meta">{{ prog.timeLabel }} &bull; {{ prog.category }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Mobile overlay for channel drawer -->
      <div v-if="mobileDrawerOpen" class="ltv-overlay" @click="mobileDrawerOpen = false"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { apiFetch, apiFetchCached } from '../composables/useApi'
import { trackRecentPlay } from '../composables/useRecentlyPlayed'

const DEFAULT_COVER = '/static/img/default-cover.jpg'

// --- Refs ---
const videoEl = ref(null)
const guideRef = ref(null)
const channels = ref([])
const selectedRow = ref(0)
const loading = ref(true)
const loadError = ref(false)
const isPlaying = ref(false)
const isMuted = ref(true)
const nowTitle = ref('Live')
const nowMeta = ref('—')
const nowThumb = ref(DEFAULT_COVER)
const upNextTitle = ref('—')
const progressPct = ref(0)
const mobileDrawerOpen = ref(false)

// Generated thumbnails from video frames (videoUrl -> data URL) when item has no thumbnail
const generatedThumbs = ref({})

// Guide focus (for keyboard nav and highlight; Enter = tune to channel)
const guideFocus = ref({ row: 0, col: 0 })

// Hover preview
const hoverPreview = ref({ visible: false, x: 0, y: 0, thumb: '', title: '', meta: '' })
let hoverTimer = null

// Schedule engine
const schedule = ref([])
let lastSrc = ''
let engineTimer = null

// Constants
const pillColors = ['#7c66ff', '#ff6b6b', '#22c55e', '#f59e0b']
const pxPerMinute = 6
const horizonMinutes = 180

const ROW_DEFS = [
  { key: 'misc', titles: ['misc', 'clips', 'clip'], label: 'Channel 01 — Misc' },
  { key: 'films', titles: ['films', 'film', 'movies', 'movie', 'short films', 'short film'], label: 'Channel 02 — Short Films' },
  { key: 'music-videos', titles: ['music videos', 'music_video', 'music'], label: 'Channel 03 — Music Videos' },
  { key: 'live-shows', titles: ['live shows', 'broadcast', 'shows', 'live'], label: 'Channel 04 — Live Shows' },
]

// Computed
const rowLabels = computed(() => {
  return channels.value.map((ch, idx) => {
    const def = ROW_DEFS[idx]
    return def?.label || `Channel ${String(idx + 1).padStart(2, '0')} — ${ch.name}`
  })
})

const channelLabel = computed(() => {
  const idx = selectedRow.value
  const ch = channels.value[idx]
  const num = String(idx + 1).padStart(2, '0')
  return `Channel ${num} — ${ch?.name || 'Live TV'}`
})

const timeMarkers = computed(() => {
  const markers = []
  const now = new Date()
  for (let m = 0; m <= horizonMinutes; m += 30) {
    const t = new Date(now.getTime() + m * 60000)
    markers.push(t.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }))
  }
  return markers
})

// Guide programs grid (thumbnail uses getThumbnail so generatedThumbs reactivity applies)
const guidePrograms = computed(() => {
  void generatedThumbs.value // dependency for reactivity
  const result = {}
  const now = new Date()
  channels.value.forEach((ch, rowIdx) => {
    const progs = []
    let cursor = new Date(now)
    let col = 0
    const items = ch.items || []
    if (!items.length) { result[rowIdx] = progs; return }
    while (diffMinutes(now, cursor) < horizonMinutes) {
      const item = items[col % items.length]
      const src = item?.video_url || item?.mp4_link || item?.trailer_url || ''
      const durMin = Math.max(5, Math.round((item?.duration_seconds || 300) / 60))
      const end = new Date(cursor.getTime() + durMin * 60000)
      progs.push({
        title: item?.title || 'Untitled',
        thumbnail: getThumbnail(item, src),
        category: item?.category || ch.name || 'Show',
        durMin,
        widthPx: durMin * pxPerMinute,
        timeLabel: `${fmtTime(cursor)} – ${fmtTime(end)}`,
        startUTC: cursor.getTime(),
        endUTC: end.getTime(),
        src,
        item,
      })
      cursor = end
      col++
    }
    result[rowIdx] = progs
  })
  return result
})

// --- Helpers ---
function diffMinutes(a, b) {
  return Math.round((b.getTime() - a.getTime()) / 60000)
}

function fmtTime(d) {
  return d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
}

function cleanTitle(title) {
  if (!title) return 'Untitled'
  return title.replace(/\[[^\]]*\]/g, '').replace(/\([^)]*\)/g, '').trim() || 'Untitled'
}

function getVideoUrl(item) {
  return item?.video_url || item?.mp4_link || item?.trailer_url || ''
}

// Resolve thumbnail: use item's thumbnail, or generated frame from video, or default
function getThumbnail(item, videoUrl) {
  if (item?.thumbnail) return item.thumbnail
  const url = videoUrl || getVideoUrl(item)
  if (url && generatedThumbs.value[url]) return generatedThumbs.value[url]
  return DEFAULT_COVER
}

// Capture a single frame from a video URL (for thumbnail generation)
const _thumbQueue = []
let _thumbInFlight = 0
const MAX_CONCURRENT_THUMBS = 2

function captureVideoFrame(videoUrl) {
  return new Promise((resolve, reject) => {
    if (!videoUrl || typeof videoUrl !== 'string') {
      reject(new Error('Invalid video URL'))
      return
    }
    const video = document.createElement('video')
    video.muted = true
    video.playsInline = true
    video.crossOrigin = 'anonymous'
    video.preload = 'metadata'
    const timeout = setTimeout(() => {
      video.src = ''
      video.load()
      reject(new Error('Timeout'))
    }, 15000)
    video.onerror = () => {
      clearTimeout(timeout)
      reject(new Error('Video load failed'))
    }
    video.onloadeddata = () => {
      const t = Math.min(1, Math.max(0, video.duration ? video.duration * 0.05 : 1))
      video.currentTime = t
    }
    video.onseeked = () => {
      clearTimeout(timeout)
      try {
        const canvas = document.createElement('canvas')
        const w = 320
        const h = Math.round((video.videoHeight / video.videoWidth) * w) || 180
        canvas.width = w
        canvas.height = h
        const ctx = canvas.getContext('2d')
        if (!ctx) {
          resolve(null)
          return
        }
        ctx.drawImage(video, 0, 0, w, h)
        const dataUrl = canvas.toDataURL('image/jpeg', 0.85)
        video.src = ''
        video.load()
        resolve(dataUrl)
      } catch (e) {
        reject(e)
      }
    }
    video.src = videoUrl
    video.load().catch(() => reject(new Error('Load failed')))
  })
}

function processThumbQueue() {
  if (_thumbInFlight >= MAX_CONCURRENT_THUMBS || _thumbQueue.length === 0) return
  const videoUrl = _thumbQueue.shift()
  if (generatedThumbs.value[videoUrl]) {
    processThumbQueue()
    return
  }
  _thumbInFlight++
  captureVideoFrame(videoUrl)
    .then((dataUrl) => {
      if (dataUrl) {
        generatedThumbs.value = { ...generatedThumbs.value, [videoUrl]: dataUrl }
      }
    })
    .catch(() => {})
    .finally(() => {
      _thumbInFlight--
      processThumbQueue()
    })
}

function ensureVideoThumb(videoUrl) {
  if (!videoUrl || generatedThumbs.value[videoUrl]) return
  if (_thumbQueue.includes(videoUrl)) return
  _thumbQueue.push(videoUrl)
  processThumbQueue()
}

// --- Schedule engine ---
function buildSchedule() {
  const sched = []
  const now = new Date()
  channels.value.forEach((ch, rowIdx) => {
    const items = ch.items || []
    if (!items.length) return
    let cursor = new Date(now)
    let col = 0
    while (diffMinutes(now, cursor) < horizonMinutes) {
      const item = items[col % items.length]
      const durMin = Math.max(5, Math.round((item?.duration_seconds || 300) / 60))
      const end = new Date(cursor.getTime() + durMin * 60000)
      sched.push({
        startUTC: cursor.getTime(),
        endUTC: end.getTime(),
        row: rowIdx,
        col,
        title: item?.title || 'Program',
        category: item?.category || ch.name || 'Show',
        src: getVideoUrl(item),
        thumb: item?.thumbnail || '',
        durationSec: durMin * 60,
      })
      cursor = end
      col++
    }
  })
  sched.sort((a, b) => a.startUTC - b.startUTC)
  schedule.value = sched
}

function getCurrentSlot(rowFilter) {
  const now = Date.now()
  for (const s of schedule.value) {
    if (rowFilter != null && s.row !== rowFilter) continue
    if (now >= s.startUTC && now < s.endUTC) return s
  }
  return null
}

function getNextSlot(rowFilter) {
  const now = Date.now()
  let candidate = null
  for (const s of schedule.value) {
    if (rowFilter != null && s.row !== rowFilter) continue
    if (s.startUTC > now) {
      if (!candidate || s.startUTC < candidate.startUTC) candidate = s
    }
  }
  return candidate
}

function getSeekTime(slot) {
  const elapsed = Math.max(0, Date.now() - slot.startUTC)
  return Math.max(0, Math.min(Math.floor(elapsed / 1000), slot.durationSec - 1))
}

function playCurrentSlot() {
  const video = videoEl.value
  if (!video || !schedule.value.length) return
  const slot = getCurrentSlot(selectedRow.value)
  if (!slot || !slot.src) return
  const needSrc = slot.src !== lastSrc
  const seekSec = getSeekTime(slot)
  if (needSrc) {
    lastSrc = slot.src
    try { video.pause() } catch (_) {}
    video.src = slot.src
    try { video.load() } catch (_) {}
    video.currentTime = seekSec
    video.muted = true
    isMuted.value = true
    video.play().catch(() => {})
    const ch = channels.value[selectedRow.value]
    trackRecentPlay({
      id: `live_tv-${ch?.id ?? selectedRow.value}-${slot.startUTC}`,
      type: 'live_tv',
      title: slot.title || 'Live TV',
      host: ch?.name || channelLabel.value,
      thumbnail: slot.thumb,
      url: slot.src,
    })
  } else {
    if (Math.abs((video.currentTime || 0) - seekSec) > 3) {
      try { video.currentTime = seekSec } catch (_) {}
    }
  }
}

function updateNowNext() {
  const slot = getCurrentSlot(selectedRow.value)
  const next = getNextSlot(selectedRow.value)
  if (slot) {
    nowTitle.value = cleanTitle(slot.title)
    nowMeta.value = slot.category || ''
    nowThumb.value = slot.thumb || generatedThumbs.value[slot.src] || DEFAULT_COVER
  }
  upNextTitle.value = next ? cleanTitle(next.title) : '—'
}

function updateProgress() {
  const slot = getCurrentSlot(selectedRow.value)
  if (!slot) { progressPct.value = 0; return }
  const now = Date.now()
  progressPct.value = Math.max(0, Math.min(100, ((now - slot.startUTC) / (slot.endUTC - slot.startUTC)) * 100))
}

function tick() {
  playCurrentSlot()
  updateNowNext()
  updateProgress()
}

function resyncVideo() {
  const slot = getCurrentSlot(selectedRow.value)
  if (!slot) return
  const video = videoEl.value
  if (!video) return
  const seek = getSeekTime(slot)
  try {
    if (Math.abs((video.currentTime || 0) - seek) > 2) {
      video.currentTime = seek
    }
  } catch (_) {}
}

function onVideoEnded() {
  isPlaying.value = false
  const next = getNextSlot(selectedRow.value)
  if (!next) return
  const startNext = () => {
    lastSrc = ''
    tick()
  }
  const now = Date.now()
  if (now < next.startUTC) {
    setTimeout(startNext, Math.max(0, next.startUTC - now + 50))
  } else {
    startNext()
  }
}

// --- Controls ---
function togglePlay() {
  if (!videoEl.value) return
  if (isPlaying.value) videoEl.value.pause()
  else videoEl.value.play().catch(() => {})
}

function toggleMute() {
  if (!videoEl.value) return
  isMuted.value = !isMuted.value
  videoEl.value.muted = isMuted.value
}

function toggleFullscreen() {
  const target = videoEl.value || document.documentElement
  if (!document.fullscreenElement) {
    target?.requestFullscreen?.()?.catch(() => {})
  } else {
    document.exitFullscreen?.()
  }
}

function channelUp() {
  const total = channels.value.length
  if (!total) return
  const next = (selectedRow.value + 1) % total
  selectChannel(next)
}

function channelDown() {
  const total = channels.value.length
  if (!total) return
  const next = (selectedRow.value - 1 + total) % total
  selectChannel(next)
}

function selectChannel(idx) {
  selectedRow.value = idx
  lastSrc = ''
  tick()
}

function scrollToGuide() {
  guideRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

// --- Channel selector helpers ---
function channelNowTitle(idx) {
  const slot = getCurrentSlot(idx)
  if (slot) return cleanTitle(slot.title)
  const ch = channels.value[idx]
  if (ch?.items?.length) return cleanTitle(ch.items[0].title)
  return '—'
}

// --- Hover preview ---
function startHoverPreview(event, idx) {
  hideHoverPreview()
  hoverTimer = setTimeout(() => {
    const ch = channels.value[idx]
    if (!ch) return
    const slot = getCurrentSlot(idx)
    const videoUrl = slot?.src || getVideoUrl(ch.items?.[0])
    const thumb = slot
      ? (slot.thumb || generatedThumbs.value[slot.src] || DEFAULT_COVER)
      : getThumbnail(ch.items?.[0], videoUrl)
    const title = slot ? cleanTitle(slot.title) : cleanTitle(ch.items?.[0]?.title)
    const meta = slot?.category || ch.items?.[0]?.category || ch.name || ''
    const rect = event.target.closest('.channel-button').getBoundingClientRect()
    const previewWidth = 280
    let left = rect.left + (rect.width / 2) - (previewWidth / 2)
    let top = rect.top - 12
    if (left < 12) left = 12
    if (left + previewWidth > window.innerWidth - 12) left = window.innerWidth - previewWidth - 12
    if (top < 12) top = rect.bottom + 12
    hoverPreview.value = { visible: true, x: left, y: top, thumb, title, meta }
  }, 1000)
}

function hideHoverPreview() {
  if (hoverTimer) { clearTimeout(hoverTimer); hoverTimer = null }
  hoverPreview.value = { ...hoverPreview.value, visible: false }
}

// --- Guide ---
function setGuideFocus(row, col) {
  guideFocus.value = { row, col }
}

// Keyboard navigation for guide
function onGlobalKeydown(e) {
  // Only handle if guide is in viewport-ish
  if (!guideRef.value) return
  const rect = guideRef.value.getBoundingClientRect()
  if (rect.bottom < 0 || rect.top > window.innerHeight) return

  const rows = channels.value.length
  if (!rows) return
  const { row, col } = guideFocus.value

  if (e.key === 'ArrowUp') {
    e.preventDefault()
    setGuideFocus(Math.max(0, row - 1), col)
  } else if (e.key === 'ArrowDown') {
    e.preventDefault()
    setGuideFocus(Math.min(rows - 1, row + 1), col)
  } else if (e.key === 'ArrowRight') {
    e.preventDefault()
    const maxCol = (guidePrograms.value[row]?.length || 1) - 1
    setGuideFocus(row, Math.min(maxCol, col + 1))
  } else if (e.key === 'ArrowLeft') {
    e.preventDefault()
    setGuideFocus(row, Math.max(0, col - 1))
  } else if (e.key === 'Enter') {
    e.preventDefault()
    selectChannel(guideFocus.value.row)
  }
}

// Parse live-tv API response (same shape as Flask: { channels: [ { id, name, items }, ... ] })
function parseLiveTvChannels(data) {
  const raw = data?.channels ?? data?.data?.channels ?? []
  if (!Array.isArray(raw)) return []
  return raw.map((c) => ({
    ...c,
    id: c?.id ?? 'misc',
    name: c?.name ?? 'Channel',
    items: Array.isArray(c?.items) ? c.items : [],
  }))
}

// --- Load channels (network first with cache-bust, then cache fallback; used on mount and retry) ---
async function loadChannels() {
  loading.value = true
  loadError.value = false
  if (engineTimer) {
    clearInterval(engineTimer)
    engineTimer = null
  }
  let data = null
  try {
    data = await apiFetch('/api/live-tv/channels?_=' + Date.now())
  } catch {
    try {
      data = await apiFetchCached('/api/live-tv/channels')
    } catch {
      loadError.value = true
      channels.value = []
      loading.value = false
      return
    }
  }
  channels.value = parseLiveTvChannels(data || {})
  if (channels.value.length) {
    buildSchedule()
    tick()
    engineTimer = setInterval(tick, 1000)
    // Queue thumbnail generation for items that have video but no thumbnail
    nextTick(() => {
      channels.value.forEach((ch) => {
        (ch.items || []).forEach((item) => {
          const url = getVideoUrl(item)
          if (url && !item?.thumbnail) ensureVideoThumb(url)
        })
      })
    })
  }
  loading.value = false
}

// --- Lifecycle ---
onMounted(async () => {
  document.addEventListener('keydown', onGlobalKeydown)
  await loadChannels()
})

onUnmounted(() => {
  if (engineTimer) clearInterval(engineTimer)
  if (hoverTimer) clearTimeout(hoverTimer)
  document.removeEventListener('keydown', onGlobalKeydown)
})
</script>

<style scoped>
/* ===== Live TV Layout ===== */
.tv-container {
  background: #000;
  min-height: 100vh;
  color: #e5e7eb;
}

/* ===== Hero Player ===== */
.video-spotlight {
  padding: 0 12px;
}
.spotlight-grid {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 16px;
  max-width: 1200px;
  margin: 0 auto;
}
.spotlight-left {
  min-width: 0;
}
.panelstream-player.hero-player {
  position: relative;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  min-height: 48vh;
}
.hero-player video {
  width: 100%;
  height: 100%;
  display: block;
}
.video-header {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  gap: 10px;
  align-items: center;
  z-index: 2;
}
.now-playing-label {
  background: rgba(59, 130, 246, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.channel-name-label {
  font-size: 13px;
  font-weight: 600;
  opacity: 0.9;
}
.hero-glass {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: linear-gradient(transparent, rgba(0,0,0,0.6));
  pointer-events: none;
}

/* ===== Remote Controls ===== */
.channel-remote.remote-below {
  display: flex;
  gap: 8px;
  padding: 12px 0;
  justify-content: center;
}
.remote-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.9);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 16px;
}
.remote-btn:hover {
  background: rgba(255,255,255,0.1);
  border-color: rgba(255,255,255,0.2);
}
.remote-btn:active {
  transform: scale(0.95);
  background: rgba(255,255,255,0.15);
}

/* ===== Playing Now Bar ===== */
.playing-now {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}
.playing-now img {
  width: 50px;
  height: 34px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
}
.now-col { flex: 1; min-width: 0; }
.np-title { font-weight: 700; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.np-sub { font-size: 11px; opacity: 0.7; }
.next-col { flex-shrink: 0; text-align: right; }
.np-label { font-size: 10px; text-transform: uppercase; opacity: 0.5; letter-spacing: 0.5px; }
.np-next { font-size: 13px; opacity: 0.85; }

.ltv-progress-wrap {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(255,255,255,0.08);
}
.ltv-progress {
  height: 100%;
  background: #3b82f6;
  transition: width 1s linear;
}

/* ===== Right Dashboard ===== */
.right-dashboard {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 16px;
  display: grid;
  gap: 12px;
  position: sticky;
  top: 12px;
  align-self: start;
}
.rd-thumb {
  width: 100%;
  aspect-ratio: 16/9;
  border-radius: 8px;
  object-fit: cover;
  background: #1b1b1b;
}
.rd-label {
  font-size: 10px;
  text-transform: uppercase;
  opacity: 0.5;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}
.rd-title {
  font-size: 15px;
  font-weight: 700;
}
.rd-meta {
  font-size: 12px;
  opacity: 0.7;
}

/* ===== Channel Selector ===== */
#channel-selector {
  padding: 32px 16px;
  background: #000;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
.channel-button {
  background: #111;
  border: 2px solid #222;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  color: #fff;
  font-family: inherit;
  font-size: inherit;
}
.channel-button:hover {
  background: #1a1a1a;
  border-color: #444;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
.channel-button.active {
  background: #1a1a1a;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59,130,246,0.2);
}
.channel-button-name {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 8px;
}
.channel-button-next {
  font-size: 13px;
  color: #999;
  margin-top: 8px;
}

/* ===== Channel selector empty / retry (mobile-friendly) ===== */
.channel-selector-empty {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 24px 16px;
  text-align: center;
  min-height: 120px;
}
.channel-selector-empty-text {
  font-size: 16px;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0;
}
.channel-selector-empty-hint {
  font-size: 13px;
  color: #9ca3af;
  margin: 0;
}
.channel-selector-retry {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 10px;
  background: #3b82f6;
  border: none;
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  font-family: inherit;
  margin-top: 4px;
}
.channel-selector-retry:hover {
  background: #2563eb;
}
.channel-selector-retry:active {
  transform: scale(0.98);
}

/* ===== Hover Preview ===== */
.live-tv-channel-preview {
  position: fixed;
  z-index: 9999;
  width: 280px;
  max-width: 90vw;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0,0,0,0.5);
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s ease;
}
.live-tv-channel-preview.visible {
  opacity: 1;
}
.live-tv-channel-preview img {
  width: 100%;
  aspect-ratio: 16/9;
  object-fit: cover;
  display: block;
}
.live-tv-channel-preview-title {
  padding: 10px 12px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  line-height: 1.3;
}
.live-tv-channel-preview-meta {
  padding: 0 12px 10px;
  font-size: 12px;
  color: #999;
}

/* ===== TV Guide ===== */
.live-tv-container {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 16px;
  padding: 12px;
  max-width: 1200px;
  margin: 0 auto;
}
.live-tv-sidebar {
  background: #0f0f0f;
  border-radius: 8px;
  padding: 8px;
}
.channel-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.channel-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
}
.channel-item[aria-selected="true"] {
  background: #222;
  outline: 2px solid #444;
}
.channel-pill {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}
.channel-name {
  font-weight: 600;
  letter-spacing: 0.25px;
}

.live-tv-main {
  min-width: 0;
}

.guide {
  background: #0f0f0f;
  border-radius: 8px;
  padding: 8px;
  overflow: hidden;
  min-height: 48vh;
}
.guide-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-bottom: 1px solid #222;
  font-weight: 600;
}
.kbd-hint {
  font-size: 12px;
  opacity: 0.75;
  margin-left: auto;
  display: flex;
  gap: 8px;
  align-items: center;
}
.kbd {
  border: 1px solid #333;
  background: #151515;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}
.guide-timebar {
  position: sticky;
  top: 0;
  background: #0f0f0f;
  z-index: 2;
  padding: 6px 10px;
  display: flex;
  gap: 24px;
  border-bottom: 1px solid #1d1d1d;
  flex-wrap: nowrap;
  overflow-x: auto;
}
.time-marker {
  color: #bbb;
  font-size: 12px;
  text-align: left;
  flex: 0 0 auto;
}
.guide-scroller {
  overflow-x: auto;
  overflow-y: auto;
}
.guide-rows {
  position: relative;
}
.guide-row {
  display: flex;
  gap: 8px;
  align-items: stretch;
  padding: 10px;
  border-bottom: 1px solid #141414;
}
.guide-channel-label {
  width: 140px;
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 13px;
}
.guide-channel-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: inline-block;
  flex-shrink: 0;
}
.guide-track {
  position: relative;
  display: flex;
  gap: 8px;
  min-width: 1200px;
}
.program {
  background: #141414;
  border: 1px solid #1f1f1f;
  border-radius: 8px;
  padding: 8px;
  display: grid;
  gap: 6px;
  color: #e5e7eb;
  cursor: pointer;
  flex-shrink: 0;
}
.program:focus {
  outline: 2px solid #4f46e5;
}
.program.selected {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.35) inset;
}
.program-thumb {
  width: 100%;
  aspect-ratio: 16/9;
  border-radius: 6px;
  object-fit: cover;
  background: #222;
}
.program-title {
  font-weight: 600;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.program-meta {
  font-size: 11px;
  opacity: 0.85;
}
.now-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #3b82f6;
  opacity: 0.85;
}

/* ===== Mobile ===== */
.mobile-only { display: none; }
.channels-btn {
  background: #1d1d1f;
  border: 1px solid #2a2a2a;
  color: #e5e7eb;
  padding: 8px 14px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
}

.ltv-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 99;
}

.hidden-mobile {}

@media (max-width: 900px) {
  .spotlight-grid {
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 0 8px;
  }
  .right-dashboard {
    position: relative;
    top: 0;
    max-height: none;
    margin-top: 12px;
  }
  .live-tv-container {
    grid-template-columns: 1fr;
  }
  .live-tv-main {
    grid-template-columns: 1fr;
  }
  #channel-selector {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .hidden-mobile {
    display: none !important;
  }
  .mobile-only {
    display: block;
  }
  .tv-container {
    padding-bottom: 80px;
  }
  .hero-player {
    border-radius: 12px;
    overflow: hidden;
  }
  .hero-player video {
    width: 100%;
    height: auto;
    min-height: 200px;
    max-height: 50vh;
  }
  .channel-remote.remote-below {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    padding: 12px;
    max-width: 100%;
  }
  .remote-btn {
    width: auto;
    min-height: 48px;
    border-radius: 10px;
  }
  .remote-btn i {
    font-size: 16px;
  }
  .playing-now {
    flex-direction: column;
    gap: 8px;
    padding: 12px;
  }
  .playing-now img {
    width: 60px;
    height: 40px;
  }
  .np-title, .np-next { font-size: 14px; }
  .np-sub, .np-label { font-size: 11px; }
  #channel-selector {
    padding: 16px 8px;
    gap: 12px;
  }
  .channel-button {
    padding: 16px;
    border-radius: 10px;
  }
  .channel-button-name { font-size: 16px; }
  .channel-button-next { font-size: 12px; }
  .channel-selector-empty {
    min-width: 100%;
    padding: 20px 12px;
  }
  .channel-selector-retry {
    min-height: 48px;
    padding: 14px 24px;
  }
  .guide {
    min-height: auto;
    border-radius: 10px;
  }
  .guide-header { padding: 8px; }
  .guide-timebar { padding: 6px 8px; gap: 16px; }
  .time-marker { font-size: 10px; min-width: 50px; }
  .guide-row { padding: 8px; }
  .guide-channel-label { width: 100px; font-size: 12px; }
  .program { padding: 6px; min-width: 100px; }
  .program-title { font-size: 11px; }
  .program-meta { font-size: 10px; }

  /* Mobile sidebar drawer */
  .live-tv-sidebar {
    position: fixed;
    top: 0;
    left: -100%;
    width: 86vw;
    max-width: 360px;
    height: 100vh;
    z-index: 100;
    transition: left 0.3s ease;
    overflow-y: auto;
  }
  .live-tv-sidebar.open {
    left: 0;
  }
  .channel-item {
    padding: 12px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .remote-btn { font-size: 12px; }
}
</style>
