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
          <div ref="heroPlaceholder" class="panelstream-player hero-player">
            <div v-if="!playerStore.currentTrack || playerStore.mode !== 'video'" class="placeholder-content">
               <i class="fas fa-tv fa-3x" style="opacity:0.2; margin-bottom: 20px;"></i>
               <span>Select a channel to start watching</span>
            </div>
            
            <div class="video-header">
              <span class="now-playing-label">Now Playing</span>
              <span class="channel-name-label" aria-live="polite">{{ channelLabel }}</span>
            </div>
            <div class="hero-glass"></div>
          </div>

          <!-- Remote controls below video -->
          <div 
            class="channel-remote remote-below" 
            :class="{ 'vibes-hidden': !showControls }"
            aria-label="Channel Controls"
          >
            <button type="button" class="remote-btn" title="Play/Pause" @click="playerStore.togglePlay()">
              <i :class="playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
            </button>
            <button type="button" class="remote-btn" title="Mute" @click="playerStore.toggleMute()">
              <i :class="playerStore.isMuted ? 'fas fa-volume-mute' : 'fas fa-volume-up'"></i>
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
            <!-- Manual hide button -->
            <button type="button" class="remote-btn hide-vibes-btn" title="Hide Controls" @click="showControls = false">
              <i class="fas fa-eye-slash"></i>
            </button>
          </div>

          <!-- Playing now bar with progress -->
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
          
          <div class="rd-suggested">
             <div class="rd-suggested-title">Suggested for You</div>
             <div v-for="(ch, idx) in channels.slice(0, 4)" :key="ch.id" class="rd-suggested-item" @click="selectChannel(idx)">
                <span class="rd-suggested-dot" :style="{ background: pillColors[idx % 4] }"></span>
                <span class="rd-suggested-name">{{ ch.name }}</span>
                <span class="rd-suggested-meta">Live</span>
             </div>
          </div>
        </aside>
      </div>
    </div>

    <!-- TV Guide section (Moved flush under controls) -->
    <div ref="guideRef" class="live-tv-container guide-flush" aria-label="TV Guide">
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
            </div>
          </div>
          <div class="guide-timebar">
            <div v-for="t in timeMarkers" :key="t" class="time-marker" :style="{ minWidth: (30 * pxPerMinute) + 'px' }">{{ t }}</div>
          </div>
          <div class="guide-scroller" ref="scrollerRef" @mousedown="onMouseDown" @mousemove="onMouseMove" @mouseup="onMouseUp" @mouseleave="onMouseUp">
            <div class="guide-rows" role="grid" aria-label="Channel Guide">
              <div class="now-line" :style="nowLineStyle"></div>
              <div v-for="(ch, rowIdx) in channels" :key="ch.id" class="guide-row" role="row">
                <div class="guide-channel-label">
                  <div class="guide-channel-icon" :style="{ background: pillColors[rowIdx % 4] }"></div>
                  <div class="guide-channel-name">{{ ch.name }}</div>
                </div>
                <div class="guide-track">
                  <div
                    v-for="(prog, colIdx) in guidePrograms[rowIdx] || []"
                    :key="rowIdx + '-' + colIdx"
                    class="program"
                    :class="{ selected: guideFocus.row === rowIdx && guideFocus.col === colIdx }"
                    @click="openProgramDetails(prog)"
                    @keydown.enter="openProgramDetails(prog)"
                    :data-row="rowIdx"
                    :data-col="colIdx"
                    tabindex="0"
                    role="gridcell"
                    :aria-label="prog.title + ' • ' + prog.durMin + ' min'"
                    :style="{
                       width: prog.widthPx + 'px',
                       background: pillColors[rowIdx % 4],
                       boxShadow: '0 0 10px ' + pillColors[rowIdx % 4] + '66, inset 0 0 5px rgba(255,255,255,0.2)'
                    }"
                  >
                    <!-- No Thumbnail -->
                    <div class="program-title" style="font-size:11px; opacity:0.9">{{ prog.title }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Mobile overlay for channel drawer -->
      <div v-if="mobileDrawerOpen" class="ltv-overlay" @click="mobileDrawerOpen = false"></div>

      <!-- Program Details Modal -->
      <div v-if="selectedProgram" class="program-modal-overlay" @click.self="closeProgramDetails">
        <div class="program-modal">
          <button class="close-btn" @click="closeProgramDetails" aria-label="Close">
            <i class="fas fa-times"></i>
          </button>
          
          <div class="modal-content">
            <div class="modal-header">
              <h2 class="modal-title">{{ cleanTitle(selectedProgram.title) }}</h2>
              <div class="modal-meta">
                <span class="modal-badge">{{ selectedProgram.category }}</span>
                <span>{{ selectedProgram.durMin }} min</span>
              </div>
            </div>
            
            <div class="modal-body">
              <p class="modal-desc">
                {{ selectedProgram.item?.description || "No description available for this program." }}
              </p>
              
              <div class="modal-actions">
                <button class="action-btn primary" @click="addToSaved(selectedProgram)">
                  <i class="fas fa-plus"></i> Add to Saved
                </button>
                <!-- Watch Now button if it's currently playing or capable of VOD (future enhancement) -->
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { apiFetch, apiFetchCached } from '../composables/useApi'
import { trackRecentPlay } from '../composables/useRecentlyPlayed'
import { useRoute } from 'vue-router'
import { usePlayerStore } from '../stores/player'
import MiniPlayer from '../components/MiniPlayer.vue'
import GlobalTvPlayer from '../components/GlobalTvPlayer.vue'
import CompactFooter from '../components/CompactFooter.vue'

const route = useRoute()
const DEFAULT_COVER = '' // Use empty string to trigger fallback logic

// --- Refs ---
const heroPlaceholder = ref(null)
const scrollerRef = ref(null)
const playerStore = usePlayerStore()
const channels = ref([])
const selectedRow = ref(0)
const loading = ref(true)
const loadError = ref(false)
const mobileDrawerOpen = ref(false)
const showControls = ref(true)
let controlsTimer = null

// Guide Drag-Scroll Logic
const isDragging = ref(false)
const startX = ref(0)
const scrollLeft = ref(0)

function onMouseDown(e) {
  isDragging.value = true
  startX.value = e.pageX - scrollerRef.value.offsetLeft
  scrollLeft.value = scrollerRef.value.scrollLeft
  scrollerRef.value.style.cursor = 'grabbing'
}

function onMouseMove(e) {
  if (!isDragging.value) return
  e.preventDefault()
  const x = e.pageX - scrollerRef.value.offsetLeft
  const walk = (x - startX.value) * 1.5
  scrollerRef.value.scrollLeft = scrollLeft.value - walk
}

function onMouseUp() {
  isDragging.value = false
  if (scrollerRef.value) scrollerRef.value.style.cursor = 'grab'
}


function resetControlsTimer() {
  showControls.value = true
  if (controlsTimer) clearTimeout(controlsTimer)
  controlsTimer = setTimeout(() => {
    showControls.value = false
  }, 5000)
}

// Generated thumbnails from video frames (videoUrl -> data URL) when item has no thumbnail
const generatedThumbs = ref({})

// Guide focus (for keyboard nav and highlight; Enter = tune to channel)
const guideFocus = ref({ row: 0, col: 0 })

// Guide Anchoring
const gridStart = ref(getAnchorTime())

function getAnchorTime() {
  // Round down to nearest 30 minutes
  const now = new Date()
  const ms = 1000 * 60 * 30
  return new Date(Math.floor(now.getTime() / ms) * ms)
}

// Calculated "now" line position
const nowLineStyle = computed(() => {
  const now = Date.now()
  const start = gridStart.value.getTime()
  const minutesElapsed = (now - start) / 60000
  const px = minutesElapsed * pxPerMinute
  
  // Pivot is 158px (Label width + gaps)
  // But we need to ensure it doesn't drift if we scroll? 
  // Actually the guide-rows is inside guide-scroller. 
  // The line is inside guide-rows (relative). 
  // So 'left' should be label_width + px.
  
  // constant 140px label + 8px gap + 10px padding = 158px?
  // Let's check styles: guide-channel-label is 140px, gap 8px. padding 10px to row.
  // Actually guide-row has padding 10px. 
  // guide-track is flex. 
  
  // The '.now-line' is absolute in '.guide-rows'.
  // .guide-row has padding: 10px. 
  // .guide-channel-label width 140px. Gap 8px.
  // So track starts at 10px + 140px + 8px = 158px.
  
  return { left: (158 + px) + 'px' }
})
const hoverPreview = ref({ visible: false, x: 0, y: 0, thumb: '', title: '', meta: '' })
let hoverTimer = null

// Program Details
const selectedProgram = ref(null)

function openProgramDetails(prog) {
  selectedProgram.value = prog
}

function closeProgramDetails() {
  selectedProgram.value = null
}

function addToSaved(prog) {
  // Mock functionality
  console.log('Added to saved:', prog.title)
  // Could show a toast here
  closeProgramDetails()
}
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
  const start = gridStart.value
  for (let m = 0; m <= horizonMinutes; m += 30) {
    const t = new Date(start.getTime() + m * 60000)
    markers.push(t.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }))
  }
  return markers
})

// Guide programs grid (thumbnail uses getThumbnail so generatedThumbs reactivity applies)
const guidePrograms = computed(() => {
  void generatedThumbs.value // dependency for reactivity
  const result = {}
  const start = gridStart.value
  const endLimit = new Date(start.getTime() + horizonMinutes * 60000)
  
  channels.value.forEach((ch, rowIdx) => {
    const progs = []
    const items = ch.items || []
    if (!items.length) { result[rowIdx] = progs; return }
    
    // We need to find programs that overlap with [start, endLimit]
    // Since items loop, we need to map the canonical schedule to our window
    
    // Simplification: Just tile placeholders starting from 'start'
    // In a real app with absolute ISO times, we'd filter.
    // Here we assume the channel loops continuously? 
    // actually buildSchedule() creates a schedule relative to 'now' called 'schedule'.
    // That schedule is for playback logic.
    // For visualisation, let's just tile items starting from gridStart.
    
    let cursor = new Date(start) // Pivot from grid start
    let col = 0
    
    // To generate consistent patterns, maybe we should seed 'col' based on time?
    // For now, let's just start t=0 at gridStart.
    
    while (diffMinutes(start, cursor) < horizonMinutes) {
      const item = items[col % items.length]
      const src = item?.video_url || item?.mp4_link || item?.trailer_url || ''
      
      // Duration
      let durMin = Math.max(5, Math.round((item?.duration_seconds || 300) / 60))
      
      const itemEnd = new Date(cursor.getTime() + durMin * 60000)
      
      // If we are tiling, we just add it.
      progs.push({
        title: item?.title || 'Untitled',
        thumbnail: getThumbnail(item, src),
        category: item?.category || ch.name || 'Show',
        durMin,
        widthPx: durMin * pxPerMinute,
        timeLabel: `${fmtTime(cursor)} – ${fmtTime(itemEnd)}`,
        startUTC: cursor.getTime(),
        endUTC: itemEnd.getTime(),
        src,
        item,
      })
      cursor = itemEnd
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
  const slot = getCurrentSlot(selectedRow.value)
  if (!slot || !slot.src) return
  
  const ch = channels.value[selectedRow.value]
  const track = {
    type: 'live_tv',
    id: `live_tv-${ch?.id ?? selectedRow.value}`,
    title: slot.title || 'Live TV',
    host: ch?.name || 'Live TV',
    thumbnail: slot.thumb,
    video_url: slot.src,
    duration_seconds: slot.durationSec,
  }

  if (playerStore.currentTrack?.video_url !== slot.src) {
    playerStore.play(track)
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
  if (!slot || !playerStore.videoElement) return
  const seek = getSeekTime(slot)
  try {
    if (Math.abs((playerStore.videoElement.currentTime || 0) - seek) > 2) {
      playerStore.videoElement.currentTime = seek
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
  return 'Off Air'
}

function getChannelProgress(idx) {
  const slot = getCurrentSlot(idx)
  if (!slot) return 0
  const now = Date.now()
  const pct = Math.max(0, Math.min(100, ((now - slot.startUTC) / (slot.endUTC - slot.startUTC)) * 100))
  return pct
}

function getChannelThumb(idx) {
  const slot = getCurrentSlot(idx)
  const ch = channels.value[idx]
  // Return slot thumb, or generated thumb, or item thumb, or default
  if (slot) return slot.thumb || generatedThumbs.value[slot.src] || null
  if (ch?.items?.length) return getThumbnail(ch.items[0], getVideoUrl(ch.items[0]))
  return null
}

function getChannelBg(idx) {
  const thumb = getChannelThumb(idx)
  if (thumb && thumb !== DEFAULT_COVER) {
     return { backgroundImage: `url(${thumb})` }
  }
  // Fallback gradient based on index color
  const color = pillColors[idx % 4]
  return {
    background: `linear-gradient(135deg, ${color}22 0%, #111 60%)`,
    opacity: 0.8
  }
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
  
  // FALLBACK: If a channel has no items, generate placeholders so it looks like a timeline
  channels.value.forEach((ch, idx) => {
    if (!ch.items || ch.items.length === 0) {
      // Generate 24 hours of placeholder content
      const placeholders = []
      const titles = ['Broadcast', 'Live Segment', 'Commercial Break', 'Station ID']
      for (let i = 0; i < 24; i++) {
         placeholders.push({
           title: titles[i % titles.length] + ' #' + (i+1),
           duration_seconds: 3600, // 1 hour blocks
           category: ch.name
         })
      }
      ch.items = placeholders
    }
  })

  if (channels.value.length) {
    buildSchedule()
    // Update gridStart occasionally? 
    // Logic: if now > gridStart + 30mins, we could shift.
    // But for now let's keep it fixed.
    
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
let resizeObserver = null

function updateBounds() {
  if (heroPlaceholder.value) {
    const rect = heroPlaceholder.value.getBoundingClientRect()
    playerStore.setHeroBounds({
      top: rect.top + window.scrollY,
      left: rect.left + window.scrollX,
      width: rect.width,
      height: rect.height
    })
  }
}

onMounted(async () => {
  document.addEventListener('keydown', onGlobalKeydown)
  window.addEventListener('mousemove', resetControlsTimer)
  window.addEventListener('touchstart', resetControlsTimer)
  resetControlsTimer()
  
  await loadChannels()

  // Sync Global Player position
  updateBounds()
  if (window.ResizeObserver) {
    resizeObserver = new ResizeObserver(updateBounds)
    resizeObserver.observe(heroPlaceholder.value)
  }
  window.addEventListener('resize', updateBounds)
})

onUnmounted(() => {
  if (engineTimer) clearInterval(engineTimer)
  if (hoverTimer) clearTimeout(hoverTimer)
  if (controlsTimer) clearTimeout(controlsTimer)
  window.removeEventListener('mousemove', resetControlsTimer)
  window.removeEventListener('touchstart', resetControlsTimer)
  document.removeEventListener('keydown', onGlobalKeydown)
  window.removeEventListener('resize', updateBounds)
  if (resizeObserver) resizeObserver.disconnect()
  
  // Detach Global Player from Hero position -> goes Mini
  playerStore.setHeroBounds(null)
})
</script>

<style scoped>
/* ===== Live TV Layout ===== */
.tv-container {
  background: #000;
  min-height: 100vh;
  color: #e5e7eb;
  padding-bottom: 0; /* Remove bottom padded space if any */
}

/* ===== Hero Player ===== */
.video-spotlight {
  padding: 0; /* FLUSH */
}
.spotlight-grid {
  display: flex;
  flex-direction: column;
  gap: 0; /* FLUSH */
  max-width: 100%;
  margin: 0 auto;
}
.spotlight-left {
  min-width: 0;
}
.panelstream-player.hero-player {
  position: relative;
  background: #000;
  border-radius: 0; /* Flush edges */
  overflow: hidden;
  /* Revert strict height, just ensure it doesn't go crazy */
  width: 100%;
  aspect-ratio: 2.39/1; /* Spaghetti Western / Cinemascope */
  max-height: 70vh;
  margin: 0 auto;
}
@media (max-width: 768px) {
  .panelstream-player.hero-player {
    min-height: auto; /* Let aspect ratio drive height */
    width: 100%;
  }
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
  padding: 8px 12px; /* Slight padding for touch, but bg connects */
  justify-content: center;
  background: #000; /* Match player bg for flush look */
  border-top: 1px solid rgba(255,255,255,0.1);
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


.vibes-hidden {
  opacity: 0 !important;
  pointer-events: none !important;
  transition: opacity 0.5s ease;
}

.channel-remote {
  transition: opacity 0.5s ease;
}

.guide-flush {
  margin-top: 0 !important;
  padding-top: 0 !important;
}

/* ===== Right Dashboard ===== */
.right-dashboard {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  gap: 0; /* FLUSH */
  padding: 0; /* FLUSH */
  max-width: 100%;
  margin: 0 auto;
  background: #000;
}
.live-tv-sidebar {
  background: #0f0f0f;
  border-radius: 0;
  padding: 8px;
  border-right: 1px solid rgba(255,255,255,0.05);
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
  background: #000;
  backdrop-filter: none;
  border: none;
  border-radius: 0;
  padding: 0;
  overflow: hidden;
  min-height: 48vh;
}
.guide-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(255, 255, 255, 0.03);
  font-weight: 700;
  font-size: 15px;
  letter-spacing: 0.5px;
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
  background: rgba(15, 15, 15, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  z-index: 10;
  padding: 10px 16px;
  display: flex;
  gap: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  flex-wrap: nowrap;
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
  /* Neuromorphic block style */
  border-radius: 6px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
  color: #fff;
}
.program:hover {
  transform: translateY(-1px);
  filter: brightness(1.1);
  cursor: pointer; /* Now interactive */
}
.program-title {
  font-weight: 600;
  font-size: 11px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 0.9;
}
.program:focus {
  outline: 2px solid #4f46e5;
}
.program.selected {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.35) inset;
}
.now-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #3b82f6;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.8);
  z-index: 5;
  pointer-events: none;
}
.now-line::after {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(59, 130, 246, 1);
}

/* ===== Program Pop-up Modal ===== */
.program-modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(5px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.program-modal {
  background: #1a1a1a;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
  position: relative;
  overflow: hidden;
  animation: modalPop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes modalPop {
  from { transform: scale(0.9); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
.close-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(255,255,255,0.1);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  z-index: 2;
}
.close-btn:hover { background: rgba(255,255,255,0.2); }

.modal-content {
  padding: 24px;
}
.modal-header {
  margin-bottom: 16px;
}
.modal-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 8px 0;
  line-height: 1.3;
}
.modal-meta {
  display: flex;
  gap: 10px;
  font-size: 13px;
  color: #9ca3af;
  align-items: center;
}
.modal-badge {
  background: #3b82f6;
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
}
.modal-body {
  color: #d1d5db;
}
.modal-desc {
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 24px;
  opacity: 0.9;
}
.modal-actions {
  display: flex;
  gap: 12px;
}
.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}
.action-btn.primary {
  background: #fff;
  color: #000;
}
.action-btn.primary:hover {
  background: #f3f4f6;
}
.action-btn.primary:active {
  transform: scale(0.97);
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
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .tv-container {
    padding-bottom: 0;
  }
  .podcasts-hero {
    padding: 20px 0;
  }
  .podcasts-hero h1 {
    font-size: 24px;
  }
  
  .spotlight-grid {
    flex-direction: column;
    gap: 0;
    padding: 0;
  }

  .video-header {
    top: 8px;
    left: 8px;
  }
  .now-playing-label {
    padding: 2px 6px;
    font-size: 10px;
  }
  .channel-name-label {
    font-size: 11px;
  }

  .hero-player video {
    border-radius: 8px;
  }

  .remote-btn {
    width: 40px;
    height: 40px;
    font-size: 14px;
  }

  .playing-now {
    padding: 8px;
    gap: 8px;
  }
  .playing-now img {
    width: 40px;
    height: 28px;
  }
  .np-title { font-size: 13px; }
  .np-sub { font-size: 10px; }
  .np-next { font-size: 12px; }

  /* Guide Responsive */
  .live-tv-container {
    display: none !important; /* Re-hide the guide on mobile as per user preference */
  }
}

@media (max-width: 480px) {
  .channel-button-name { font-size: 16px; }
  .channel-button-next { font-size: 12px; }
}

@media (max-width: 768px) {
  .tv-container {
    padding-bottom: 80px; /* Space for bottom dock */
  }
  .spotlight-grid {
    flex-direction: column;
    gap: 0;
  }
  .video-spotlight {
    padding: 0; /* Full width player */
  }
  .panelstream-player.hero-player {
    border-radius: 0; /* Edge to edge */
    background: #0a0a0a; /* Darker harmonized bg */
  }
  .placeholder-content {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #444;
    font-weight: 600;
  }
  .guide-scroller {
    cursor: grab;
    user-select: none;
  }
  .guide-scroller::-webkit-scrollbar {
    height: 6px;
  }
  .guide-scroller::-webkit-scrollbar-track {
    background: transparent;
  }
  .guide-scroller::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.05);
    border-radius: 3px;
  }
  .guide-scroller::-webkit-scrollbar-thumb:hover {
    background: rgba(255,255,255,0.1);
  }
  .tv-container, .live-tv-container, .live-tv-sidebar, .guide {
    background: #050505; /* Blacker harmonize */
  }
  .live-tv-sidebar {
    background: #080808;
    border-right-color: rgba(255,255,255,0.04);
  }
  .rd-suggested-title {
    font-size: 11px;
    text-transform: uppercase;
    color: #555;
    margin-top: 20px;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
  }
  .rd-suggested-item {
    display: flex;
    gap: 10px;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    cursor: pointer;
  }
  .rd-suggested-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }
  .rd-suggested-name {
    font-size: 12px;
    font-weight: 500;
  }
  .rd-suggested-meta {
    font-size: 10px;
    opacity: 0.4;
    margin-left: auto;
  }

  .channel-remote {
    padding: 0 12px;
    justify-content: space-between;
  }
  .remote-btn {
    width: 44px;
    height: 44px; /* Larger touch target */
    font-size: 16px;
  }
  #channel-selector {
    padding: 12px;
    grid-template-columns: 1fr; /* Stack channels */
  }
}
</style>
