<template>
  <div class="home-page">
    <!-- Global subpage hero (one line on mobile: Home · Explore) -->
    <section class="podcasts-hero">
      <div
        class="podcasts-hero-inner"
        :style="{
          backgroundImage: `url(${selectedGif})`,
          backgroundPosition: `${parallaxX}% ${parallaxY}%`
        }"
        @mouseenter="enableParallax = true"
        @mouseleave="resetParallax"
        @mousemove="handleParallaxMove"
      >
        <h1><i class="fas fa-home" aria-hidden="true"></i> Home</h1>
        <p>Explore</p>
        
        <!-- Search Bar -->
        <div class="hero-search-wrapper" :class="{ 'has-results': showResults && searchResults.length > 0, 'expanded': searchExpanded }">
          <input
            type="text"
            class="hero-search-input"
            placeholder="Search artists, tracks, or shows..."
            v-model="searchQuery"
            @input="handleSearchInput"
            @keydown.enter="handleSearch"
          />

          <!-- Search Results -->
          <div v-if="showResults && searchResults.length > 0" class="search-results-container">
            <div class="search-results-header">
              <span class="results-count">{{ searchResults.length }} {{ searchResults.length === 1 ? 'result' : 'results' }}</span>
              <div class="search-actions">
                <button
                  type="button"
                  class="search-action-btn"
                  :class="{ active: searchExpanded }"
                  @click="searchExpanded = !searchExpanded"
                  :title="searchExpanded ? 'Collapse' : 'Expand'"
                >
                  <i :class="searchExpanded ? 'fas fa-compress-alt' : 'fas fa-expand-alt'"></i>
                </button>
                <button
                  type="button"
                  class="search-action-btn"
                  @click="ejectSearch"
                  title="Open in Search Page"
                >
                  <i class="fas fa-external-link-alt"></i>
                </button>
                <button
                  type="button"
                  class="search-action-btn"
                  @click="saveSearch"
                  title="Save Search"
                >
                  <i class="fas fa-bookmark"></i>
                </button>
                <button
                  type="button"
                  class="search-action-btn close-btn"
                  @click="clearSearch"
                  title="Clear"
                >
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>

            <div class="search-results-list">
              <a
                v-for="result in displayedResults"
                :key="result.id"
                :href="getResultUrl(result)"
                class="search-result-item"
                @click.prevent="navigateToResult(result)"
              >
                <div class="result-image">
                  <img
                    :src="result.image || result.cover_art || result.artwork || result.thumbnail || '/static/img/default-cover.jpg'"
                    :alt="result.title || result.name"
                    loading="lazy"
                  />
                  <div class="result-type-badge">{{ result.type }}</div>
                </div>
                <div class="result-info">
                  <div class="result-title">{{ result.title || result.name }}</div>
                  <div class="result-subtitle">{{ result.artist || result.host || result.description || '' }}</div>
                </div>
                <div class="result-arrow">
                  <i class="fas fa-chevron-right"></i>
                </div>
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Live Dashboard (TV + Radio) — same structure as Flask home.html -->
    <section class="live-dashboard">
      <div class="dashboard-grid">
        <!-- Left: Live TV main card -->
        <div
          class="dashboard-main"
          role="button"
          tabindex="0"
          @click="tvCurrent && tvCurrent.id !== 'placeholder' && tvCurrent.id !== 'error' ? playShow(tvCurrent) : null"
          @keydown.enter.prevent="tvCurrent && tvCurrent.id !== 'placeholder' && tvCurrent.id !== 'error' ? playShow(tvCurrent) : null"
        >
          <div class="dash-preview">
            <img
              :src="tvCurrent?.thumbnail || '/static/img/default-cover.jpg'"
              alt="Live TV"
              class="dash-bg"
            />
            <div class="dash-overlay">
              <div class="dash-badges">
                <span class="live-badge">LIVE TV</span>
                <span class="channel-badge">{{ tvCurrentChannel?.name || 'Channel 01 — Misc' }}</span>
              </div>
              <div v-if="tvChannels.length > 1" class="channel-nav">
                <button type="button" class="channel-nav-btn" aria-label="Previous channel" @click.stop="switchTVChannel('prev')">
                  <i class="fas fa-chevron-left"></i>
                </button>
                <button type="button" class="channel-nav-btn" aria-label="Next channel" @click.stop="switchTVChannel('next')">
                  <i class="fas fa-chevron-right"></i>
                </button>
              </div>
              <div class="dash-content">
                <h2>{{ tvCurrent?.title || 'Loading...' }}</h2>
                <p>{{ tvCurrent?.artist || tvCurrent?.host || '' }}</p>
                <div class="dash-actions">
                  <button
                    v-if="tvCurrent && tvCurrent.id !== 'placeholder' && tvCurrent.id !== 'error'"
                    type="button"
                    class="dash-play-btn"
                    @click.stop="playShow(tvCurrent)"
                  >
                    <i class="fas fa-play"></i> Watch Now
                  </button>
                  <router-link to="/live-tv" class="dash-guide-btn" @click.native.stop>
                    <i class="fas fa-tv"></i> View All Channels
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Live Radio sidebar -->
        <div class="dashboard-sidebar">
          <div class="sidebar-header">
            <h3>Live Radio</h3>
          </div>
          <div class="dash-item radio-item" :class="{ active: radioIsPlaying }">
            <div class="dash-thumb">
              <img
                :src="(radioCurrent || radioUpNext[0])?.cover_art || 'https://ahoy.ooo/images/Ahoy-Indie-Media-DEFAULT-COVER-A-8.jpg'"
                alt="Radio"
              />
              <div class="dash-icon"><i class="fas fa-broadcast-tower"></i></div>
            </div>
            <div class="dash-info">
              <div class="dash-label">On Air Now</div>
              <h4>{{ (radioCurrent || radioUpNext[0])?.title || 'Loading...' }}</h4>
              <p>{{ (radioCurrent || radioUpNext[0])?.artist || '' }}</p>
            </div>
            <button type="button" class="dash-action-btn" aria-label="Play/Pause radio" @click.stop="toggleRadio">
              <i :class="radioIsPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
            </button>
          </div>
          <div class="radio-next-list">
            <div class="list-label">Up Next</div>
            <div v-for="track in radioUpNext.slice(0, 3)" :key="track.id" class="mini-track">
              <span class="track-title">{{ track.title }}</span>
              <span class="track-artist">{{ track.artist }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- TV Channel Strip (same as Flask) -->
      <div v-if="tvChannels.length > 1" class="tv-channel-strip">
        <div class="tv-channel-strip-header">
          <div class="tv-channel-strip-title">Live TV Channels</div>
          <div class="tv-channel-strip-subtitle">Tap a channel to switch</div>
        </div>
        <div class="tv-channel-strip-list">
          <button
            v-for="(ch, idx) in tvChannels"
            :key="ch.id"
            type="button"
            class="tv-channel-strip-item"
            :class="{ active: tvCurrentChannel && tvCurrentChannel.id === ch.id }"
            @click.stop="selectTVChannel(idx)"
          >
            <div class="tv-channel-strip-meta">
              <span class="tv-channel-strip-name">{{ getTVChannelName(ch, idx) }}</span>
              <span class="tv-channel-strip-live">LIVE</span>
            </div>
            <div class="tv-channel-strip-now">{{ (tvNowByChannel[ch.id] || {}).title || 'No content available' }}</div>
            <div v-if="tvNextByChannel[ch.id]" class="tv-channel-strip-next">
              Up next: {{ (tvNextByChannel[ch.id] || {}).title || '' }}
            </div>
          </button>
        </div>
      </div>
    </section>

    <!-- Explore Widgets (Podcasts, Videos, Radio, Music, Artists) -->
    <!-- Priority: Habits (Recent/Saves) First -->
    <ExploreWidgets />

    <!-- What's New at Ahoy (same as Flask) -->
    <section class="whats-new-section">
      <div class="whats-new-container">
        <div class="whats-new-header">
          <h2>What's New at Ahoy</h2>
          <a v-if="!whatsNewLoading && whatsNew.length > 0" href="/whats-new" class="view-all-link">
            View All <i class="fas fa-arrow-right"></i>
          </a>
        </div>
        <div v-show="whatsNewLoading" class="whats-new-loading">
          <span>Loading updates...</span>
        </div>
        <div v-show="!whatsNewLoading && whatsNew.length > 0" class="whats-new-updates">
          <a
            v-for="(update, i) in whatsNew"
            :key="update.id || update.title || i"
            :href="getUpdateUrl(update)"
            class="whats-new-item clickable"
            :class="'type-' + (update.type || 'update')"
          >
            <div class="whats-new-content">
              <h3>{{ update.title }}</h3>
              <p>{{ update.description }}</p>
              <span class="whats-new-date">{{ formatWhatsNewDate(update.date, update.type) }}</span>
            </div>
            <div class="whats-new-arrow">
              <i class="fas fa-chevron-right"></i>
            </div>
          </a>
        </div>
        <div v-show="!whatsNewLoading && whatsNew.length === 0" class="whats-new-empty">
          <p>No updates available at this time.</p>
          <a href="/whats-new" class="view-archive-link">View Archive</a>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetchCached } from '../composables/useApi'
import { usePlayerStore } from '../stores/player'
import ExploreWidgets from '../components/ExploreWidgets.vue'

const router = useRouter()
const playerStore = usePlayerStore()

// Search GIF background
const searchGifs = [
  'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExeGlreWRqaHZxc295NHNvZWs4MWJoeTIwdXk1NnNuN2syOTE4Z3JleSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/14hS1ZEmSfKdTW/giphy.gif',
  'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdnI2M2VxZmhkeTM1bHVoZmV0NmdmYzVjeWt3eHc1eGZtOWk4N3c0YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/AS9LIFttYzkc0/giphy.gif',
  'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjB3cjhjNXEwMXhrcTFvYnF4Zm5xamduNm8ycjB4ZnJneDhyb2IzNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/wSYE7n6pk9dqRXzitR/giphy.gif',
  'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMWVkeG1sY3hvYTlwMjl0bWZrbTI3bXlqOGQ2cmYyZXVmZ2RuZWIwcCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xWC0BCZtkDxE869erD/giphy.gif',
  'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjJ4Mml1ajMzNGh1ODVrN3J3cnVtbjZkeXZnN29wNmQ2aHhncTJ0OCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l1J9BYe5eZccC4Nck/giphy.gif',
  'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWZnNnhxbjgzM3B1NXdzOWJwZjJnM3hveTJwNnE1bjZrb3ZicXU3bSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oGRFs7yHPDlB8JYsg/giphy.gif'
]
const selectedGif = ref('')

// Parallax effect
const enableParallax = ref(false)
const parallaxX = ref(50)
const parallaxY = ref(50)

function handleParallaxMove(event) {
  if (!enableParallax.value) return

  const rect = event.currentTarget.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top

  // Calculate percentage position (with subtle movement range)
  const xPercent = (x / rect.width) * 100
  const yPercent = (y / rect.height) * 100

  // Smoothly interpolate (40-60% range for subtle effect)
  parallaxX.value = 40 + (xPercent / 100) * 20
  parallaxY.value = 40 + (yPercent / 100) * 20
}

function resetParallax() {
  enableParallax.value = false
  parallaxX.value = 50
  parallaxY.value = 50
}

// Search
const searchQuery = ref('')
const searchResults = ref([])
const searchExpanded = ref(false)
const showResults = ref(false)
const searchDebounceTimer = ref(null)
let allSearchableData = {
  tracks: [],
  albums: [],
  shows: [],
  podcasts: [],
  artists: []
}

const displayedResults = computed(() => {
  return searchExpanded.value ? searchResults.value : searchResults.value.slice(0, 6)
})

async function loadSearchableData() {
  try {
    const [musicData, showsData, podcastsData, artistsData] = await Promise.all([
      apiFetchCached('/api/music').catch(() => ({ tracks: [], albums: [] })),
      apiFetchCached('/api/shows').catch(() => ({ shows: [] })),
      apiFetchCached('/api/podcasts').catch(() => ({ shows: [] })),
      apiFetchCached('/api/artists').catch(() => ({ artists: [] }))
    ])

    allSearchableData.tracks = (musicData.tracks || []).map(t => ({ ...t, type: 'track' }))

    // Extract albums from tracks
    const albumMap = new Map()
    for (const track of musicData.tracks || []) {
      if (track.album && track.album !== 'Single' && !albumMap.has(track.album)) {
        albumMap.set(track.album, {
          id: track.album,
          title: track.album,
          name: track.album,
          artist: track.artist,
          cover_art: track.cover_art || track.artwork,
          type: 'album'
        })
      }
    }
    allSearchableData.albums = Array.from(albumMap.values())

    allSearchableData.shows = (showsData.shows || []).map(s => ({ ...s, type: 'video' }))
    allSearchableData.podcasts = (podcastsData.shows || []).map(p => ({ ...p, type: 'podcast' }))
    allSearchableData.artists = (artistsData.artists || []).map(a => ({ ...a, type: 'artist' }))
  } catch (e) {
    console.error('Error loading searchable data', e)
  }
}

function performSearch(query) {
  if (!query || query.trim().length < 2) {
    searchResults.value = []
    showResults.value = false
    return
  }

  showResults.value = true
  const q = query.toLowerCase().trim()
  const results = []

  // Search tracks
  for (const track of allSearchableData.tracks) {
    if (
      track.title?.toLowerCase().includes(q) ||
      track.artist?.toLowerCase().includes(q) ||
      track.album?.toLowerCase().includes(q)
    ) {
      results.push(track)
    }
  }

  // Search albums
  for (const album of allSearchableData.albums) {
    if (
      album.title?.toLowerCase().includes(q) ||
      album.artist?.toLowerCase().includes(q)
    ) {
      results.push(album)
    }
  }

  // Search shows/videos
  for (const show of allSearchableData.shows) {
    if (
      show.title?.toLowerCase().includes(q) ||
      show.artist?.toLowerCase().includes(q) ||
      show.host?.toLowerCase().includes(q)
    ) {
      results.push(show)
    }
  }

  // Search podcasts
  for (const podcast of allSearchableData.podcasts) {
    if (
      podcast.title?.toLowerCase().includes(q) ||
      podcast.host?.toLowerCase().includes(q) ||
      podcast.description?.toLowerCase().includes(q)
    ) {
      results.push(podcast)
    }
  }

  // Search artists
  for (const artist of allSearchableData.artists) {
    if (artist.name?.toLowerCase().includes(q)) {
      results.push(artist)
    }
  }

  searchResults.value = results.slice(0, 50) // Limit to 50 results
}

function handleSearchInput() {
  if (searchDebounceTimer.value) {
    clearTimeout(searchDebounceTimer.value)
  }

  searchDebounceTimer.value = setTimeout(() => {
    performSearch(searchQuery.value)
  }, 300)
}

function handleSearch() {
  if (!searchQuery.value.trim()) return
  router.push({ path: '/search', query: { q: searchQuery.value } })
}

function clearSearch() {
  searchQuery.value = ''
  searchResults.value = []
  searchExpanded.value = false
  showResults.value = false
}

function ejectSearch() {
  if (!searchQuery.value.trim()) return
  router.push({ path: '/search', query: { q: searchQuery.value } })
  clearSearch()
}

function saveSearch() {
  if (!searchQuery.value.trim()) return

  try {
    const savedSearches = JSON.parse(localStorage.getItem('ahoy.savedSearches') || '[]')
    const newSearch = {
      query: searchQuery.value,
      timestamp: new Date().toISOString(),
      resultsCount: searchResults.value.length
    }

    // Don't save duplicates
    const exists = savedSearches.find(s => s.query === searchQuery.value)
    if (!exists) {
      savedSearches.unshift(newSearch)
      localStorage.setItem('ahoy.savedSearches', JSON.stringify(savedSearches.slice(0, 20)))

      // Show feedback (you could add a toast notification here)
      alert(`Search saved: "${searchQuery.value}"`)
    }
  } catch (e) {
    console.error('Failed to save search', e)
  }
}

function getResultUrl(result) {
  switch (result.type) {
    case 'track':
      return `/music/${result.id}`
    case 'album':
      return `/music?q=${encodeURIComponent(result.title)}`
    case 'video':
      return `/videos?play=${result.id}`
    case 'podcast':
      return `/podcasts/${result.slug || result.id}`
    case 'artist':
      return `/artists/${result.slug || result.id}`
    default:
      return '#'
  }
}

function navigateToResult(result) {
  router.push(getResultUrl(result))
  clearSearch()
}

// Live TV
const tvChannels = ref([])
const tvChannelIndex = ref(0)
const tvCurrent = ref(null)
const tvCurrentChannel = ref(null)
const tvNowByChannel = ref({})
const tvNextByChannel = ref({})
let tvScheduleInterval = null

const TV_CHANNEL_NAMES = {
  misc: 'Channel 01 — Misc',
  films: 'Channel 02 — Short Films',
  'music-videos': 'Channel 03 — Music Videos',
  'live-shows': 'Channel 04 — Live Shows',
}

function getTVChannelName(ch, idx) {
  return TV_CHANNEL_NAMES[ch.id] || `Channel ${String(idx + 1).padStart(2, '0')} — ${ch.name || 'Unknown'}`
}

function computeTVSchedule() {
  const hour = new Date().getHours()
  const nowBy = {}
  const nextBy = {}
  for (let i = 0; i < tvChannels.value.length; i++) {
    const ch = tvChannels.value[i]
    if (ch?.items?.length) {
      const itemIndex = hour % ch.items.length
      nowBy[ch.id] = ch.items[itemIndex]
      nextBy[ch.id] = ch.items.length > itemIndex + 1 ? ch.items[itemIndex + 1] : ch.items[0]
    }
  }
  tvNowByChannel.value = nowBy
  tvNextByChannel.value = nextBy
  if (tvCurrentChannel.value?.id) {
    const id = tvCurrentChannel.value.id
    if (nowBy[id]) tvCurrent.value = nowBy[id]
  }
}

function selectTVChannel(index) {
  if (!tvChannels.value.length) return
  tvChannelIndex.value = (index + tvChannels.value.length) % tvChannels.value.length
  const ch = tvChannels.value[tvChannelIndex.value]
  tvCurrentChannel.value = { ...ch, name: getTVChannelName(ch, tvChannelIndex.value) }
  if (tvNowByChannel.value[ch.id]) {
    tvCurrent.value = tvNowByChannel.value[ch.id]
  } else if (ch.items?.length) {
    tvCurrent.value = ch.items[0]
  } else {
    tvCurrent.value = { id: 'placeholder', title: 'No content available', thumbnail: '/static/img/default-cover.jpg', host: ch.name }
  }
}

function switchTVChannel(direction) {
  if (!tvChannels.value.length) return
  selectTVChannel(tvChannelIndex.value + (direction === 'next' ? 1 : -1))
}

function playShow(show) {
  if (!show?.id || show.id === 'placeholder' || show.id === 'error') return
  router.push({ path: '/videos', query: { play: show.id } })
}

// Live Radio (sync with player store)
const radioTracks = ref([])
const radioQueue = ref([])
const radioUpNext = ref([])
const radioCurrent = ref(null)

const radioIsPlaying = computed(() => {
  if (!radioCurrent.value || !playerStore.currentTrack) return false
  const a = String(radioCurrent.value.id ?? '')
  const b = String(playerStore.currentTrack.id ?? '')
  return a === b && playerStore.isPlaying
})

function buildRadioQueue() {
  const list = [...radioTracks.value]
  list.sort(() => 0.5 - Math.random())
  radioQueue.value = list.map(t => ({ ...t, type: 'track' }))
  radioUpNext.value = radioQueue.value.slice(0, 20)
}

function toggleRadio() {
  if (radioIsPlaying.value) {
    playerStore.pause()
    return
  }
  if (radioCurrent.value) {
    playerStore.resume()
    return
  }
  const next = radioQueue.value[0] || radioUpNext.value[0]
  if (next) {
    radioCurrent.value = next
    playerStore.setQueue(radioTracks.value, radioTracks.value.findIndex(t => t.id === next.id))
  }
}

// What's New
const whatsNew = ref([])
const whatsNewLoading = ref(true)

function formatWhatsNewDate(dateString) {
  if (!dateString) return ''
  try {
    const d = new Date(dateString)
    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short' })
  } catch {
    return dateString
  }
}

function getUpdateUrl(update) {
  if (update.year && update.month && update.section) {
    const base = `/whats-new/${update.year}/${update.month}/${update.section}`
    return update.slug ? `${base}#update-${update.slug}` : base
  }
  if (update.link) return update.link
  return '/whats-new'
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

onMounted(async () => {
  // Randomly select search background GIF
  selectedGif.value = searchGifs[Math.floor(Math.random() * searchGifs.length)]

  // Load searchable data for instant search
  loadSearchableData()

  // Live TV channels — network first with cache-bust to avoid stale empty response, then cache fallback
  try {
    let data = null
    try {
      const response = await fetch('/api/live-tv/channels?_=' + Date.now())
      data = await response.json()
    } catch {
      data = await apiFetchCached('/api/live-tv/channels').catch(() => null)
    }
    const channels = data ? parseLiveTvChannels(data) : []
    tvChannels.value = channels
    if (channels.length) {
      const ch = channels.find((c) => c.id === 'misc') || channels[0]
      tvChannelIndex.value = channels.findIndex((c) => c.id === ch.id)
      computeTVSchedule()
      selectTVChannel(tvChannelIndex.value)
    } else {
      tvCurrent.value = { id: 'placeholder', title: 'Loading Live TV...', thumbnail: '/static/img/default-cover.jpg', host: 'Ahoy TV' }
      tvCurrentChannel.value = { id: 'misc', name: 'Channel 01 — Misc' }
    }
    tvScheduleInterval = setInterval(computeTVSchedule, 60 * 1000)
  } catch {
    tvCurrent.value = { id: 'error', title: 'Live TV', thumbnail: '/static/img/default-cover.jpg', host: 'Ahoy TV' }
    tvCurrentChannel.value = { id: 'misc', name: 'Channel 01 — Misc' }
  }

  // Radio: load music and build queue
  try {
    const musicData = await apiFetchCached('/api/music').catch(() => ({ tracks: [] }))
    const tracks = (musicData.tracks || []).filter(t => t.audio_url || t.preview_url)
    const seen = new Set()
    radioTracks.value = tracks.filter(t => {
      if (seen.has(t.id)) return false
      seen.add(t.id)
      return true
    })
    buildRadioQueue()
  } catch {}

  // Sync radio current from player
  if (playerStore.currentTrack && radioTracks.value.length) {
    const isRadioTrack = radioTracks.value.some(
      t => String(t.id) === String(playerStore.currentTrack?.id)
    )
    if (isRadioTrack) radioCurrent.value = playerStore.currentTrack
  }

  // What's New
  whatsNewLoading.value = true
  try {
    const data = await apiFetchCached('/api/whats-new').catch(() => ({ updates: [] }))
    const raw = data.updates
    if (Array.isArray(raw)) {
      whatsNew.value = raw.slice(0, 4)
    } else if (raw && typeof raw === 'object') {
      const flat = []
      for (const year of Object.keys(raw).sort().reverse()) {
        for (const month of Object.keys(raw[year] || {}).sort().reverse()) {
          for (const section of Object.keys(raw[year][month] || {})) {
            const items = (raw[year][month][section].items || []).map(it => ({
              ...it,
              year,
              month,
              section,
            }))
            flat.push(...items)
          }
        }
      }
      whatsNew.value = flat.slice(0, 4)
    } else {
      whatsNew.value = []
    }
  } catch {
    whatsNew.value = []
  } finally {
    whatsNewLoading.value = false
  }
})

onUnmounted(() => {
  if (tvScheduleInterval) clearInterval(tvScheduleInterval)
})

// Keep radio current in sync with player
watch(
  () => playerStore.currentTrack,
  (track) => {
    if (!track) return
    const isRadio = radioTracks.value.some(t => String(t.id) === String(track.id))
    if (isRadio) radioCurrent.value = track
  },
  { deep: true }
)
</script>

<!-- Styles from Flask home.html inline block so SPA home matches main branch -->
<style>
.home-page .live-dashboard { margin-bottom: 2rem; }
.home-page .dashboard-grid {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 1.5rem;
  height: 420px;
  min-height: 420px;
}
/*.podcasts-hero-inner needs flex column for search bar*/
.home-page .podcasts-hero-inner {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    gap: 0.75rem;
    padding: 3rem 2.5rem;
    min-height: 420px;
    text-align: left;
    border-radius: 28px;
    background-size: 110%;
    background-position: center;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: background-position 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Dark overlay to ensure text readability */
.home-page .podcasts-hero-inner::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(0, 0, 0, 0.6) 0%, rgba(0, 0, 0, 0.2) 100%);
    z-index: 0;
}

.home-page .podcasts-hero-inner > * {
    position: relative;
    z-index: 1;
}

.home-page .podcasts-hero-inner h1 {
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}

.home-page .podcasts-hero-inner p {
    font-size: 1.1rem;
    color: rgba(255, 255, 255, 0.8);
    margin: 0 0 0.5rem 0;
    font-weight: 500;
}

.hero-search-wrapper {
  position: relative;
  width: 100%;
  max-width: 600px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.hero-search-wrapper.has-results {
  max-width: 900px;
}

.hero-search-wrapper.expanded {
  max-width: 100%;
}

.hero-search-input {
  width: 100%;
  padding: 0.9rem 1.5rem;
  border-radius: 99px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  color: #fff;
  font-size: 1rem;
  font-weight: 500;
  outline: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  text-align: center;
}

.hero-search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
}

.hero-search-input:focus {
  background: rgba(0, 0, 0, 0.5);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
  transform: scale(1.01);
}

.hero-search-wrapper.has-results .hero-search-input {
  border-radius: 20px 20px 0 0;
  border-bottom: none;
}

/* Search Results Container - Glass Neumorphism */
.search-results-container {
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-top: none;
  border-radius: 0 0 24px 24px;
  box-shadow:
    0 20px 60px -10px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    inset 0 -1px 40px rgba(0, 0, 0, 0.2);
  animation: slideDown 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.search-results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0) 100%);
}

.results-count {
  font-size: 0.85rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.search-actions {
  display: flex;
  gap: 0.5rem;
}

.search-action-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.85rem;
}

.search-action-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
  transform: scale(1.1);
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
}

.search-action-btn.active {
  background: rgba(99, 102, 241, 0.3);
  border-color: rgba(99, 102, 241, 0.5);
  color: #fff;
}

.search-action-btn.close-btn:hover {
  background: rgba(255, 0, 0, 0.2);
  border-color: rgba(255, 0, 0, 0.4);
  color: #ff6b6b;
}

.search-results-list {
  max-height: 480px;
  overflow-y: auto;
  padding: 0.75rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.75rem;
}

.hero-search-wrapper.expanded .search-results-list {
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  max-height: 600px;
}

.search-results-list::-webkit-scrollbar {
  width: 8px;
}

.search-results-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.search-results-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.search-results-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.85rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.search-result-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateX(4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.result-image {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.result-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.result-type-badge {
  position: absolute;
  bottom: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.result-info {
  flex: 1;
  min-width: 0;
}

.result-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-subtitle {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-arrow {
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.85rem;
  transition: all 0.2s;
  flex-shrink: 0;
}

.search-result-item:hover .result-arrow {
  color: rgba(255, 255, 255, 0.8);
  transform: translateX(4px);
}

@media (max-width: 768px) {
  .home-page .podcasts-hero-inner {
    min-height: 360px;
    padding: 2rem 1.5rem;
  }

  .hero-search-wrapper {
    max-width: 100%;
  }

  .search-results-list {
    grid-template-columns: 1fr;
    max-height: 360px;
  }

  .hero-search-wrapper.expanded .search-results-list {
    grid-template-columns: 1fr;
    max-height: 480px;
  }

  .search-action-btn {
    width: 32px;
    height: 32px;
    font-size: 0.75rem;
  }
}

.home-page .dashboard-main {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: #000;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), border-color 0.3s;
}
.home-page .dashboard-main:hover { border-color: rgba(255, 255, 255, 0.2); transform: scale(1.005); }
.home-page .dash-preview { height: 100%; width: 100%; position: relative; }
.home-page .dash-bg {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.25, 0.8, 0.25, 1); opacity: 0.85;
}
.home-page .dashboard-main:hover .dash-bg { transform: scale(1.03); opacity: 0.6; }
.home-page .dash-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.6) 40%, rgba(0,0,0,0.1) 100%);
  padding: 2.5rem; display: flex; flex-direction: column; justify-content: flex-end;
}
.home-page .dash-badges { position: absolute; top: 1.5rem; left: 1.5rem; display: flex; gap: 0.75rem; z-index: 2; }
.home-page .channel-nav { position: absolute; top: 1.5rem; right: 1.5rem; display: flex; gap: 0.5rem; z-index: 2; }
.home-page .channel-nav-btn {
  width: 36px; height: 36px; border-radius: 50%;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.2); color: white;
  display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 0.875rem;
}
.home-page .channel-nav-btn:hover { background: rgba(0,0,0,0.8); border-color: rgba(255,255,255,0.4); transform: scale(1.1); }
.home-page .live-badge {
  background: #ff0000; color: white; padding: 0.35rem 0.85rem; border-radius: 8px;
  font-weight: 800; font-size: 0.75rem; letter-spacing: 0.08em;
  box-shadow: 0 4px 12px rgba(255,0,0,0.4); text-transform: uppercase;
}
.home-page .channel-badge {
  background: rgba(20,20,20,0.75); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  color: rgba(255,255,255,0.9); padding: 0.35rem 0.85rem; border-radius: 8px;
  font-weight: 600; font-size: 0.75rem; border: 1px solid rgba(255,255,255,0.1);
}
.home-page .dash-content { position: relative; z-index: 2; }
.home-page .dash-content h2 {
  font-size: 2.5rem; font-weight: 800; margin: 0 0 0.5rem 0; line-height: 1.1; letter-spacing: -0.02em;
  text-shadow: 0 2px 10px rgba(0,0,0,0.8);
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.home-page .dash-content p { font-size: 1.1rem; color: rgba(255,255,255,0.8); margin: 0 0 1.75rem 0; font-weight: 500; }
.home-page .dash-actions { display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }
.home-page .dash-play-btn {
  background: rgba(20,20,20,0.6); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  color: #fff; border: 1px solid rgba(255,255,255,0.1); padding: 0.85rem 1.75rem; border-radius: 99px;
  font-weight: 700; font-size: 0.95rem; display: inline-flex; align-items: center; gap: 0.6rem;
  cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 20px rgba(255,255,255,0.2); text-decoration: none;
}
.home-page .dash-play-btn:hover { background: #f0f0f0; color: #111; transform: translateY(-2px); }
.home-page .dash-guide-btn {
  background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.2);
  padding: 0.85rem 1.75rem; border-radius: 99px; font-weight: 700; font-size: 0.95rem;
  display: inline-flex; align-items: center; gap: 0.6rem; text-decoration: none;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}
.home-page .dash-guide-btn:hover { background: rgba(255,255,255,0.2); border-color: rgba(255,255,255,0.3); transform: translateY(-2px); }
.home-page .dashboard-sidebar {
  display: flex; flex-direction: column; gap: 1rem;
  background: rgba(20,20,20,0.6); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-radius: 24px; border: 1px solid rgba(255,255,255,0.08); padding: 1.5rem; height: 100%;
}
.home-page .sidebar-header { border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 1rem; margin-bottom: 0.5rem; }
.home-page .sidebar-header h3 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.15em; color: rgba(255,255,255,0.5); margin: 0; font-weight: 700; }
.home-page .dash-item {
  display: flex; align-items: center; gap: 1.25rem; padding: 1rem; border-radius: 16px;
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); transition: all 0.2s ease;
}
.home-page .dash-item:hover { background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.1); transform: translateX(4px); }
.home-page .dash-item.active { background: rgba(99,102,241,0.15); border-color: rgba(99,102,241,0.3); }
.home-page .dash-thumb { width: 72px; height: 72px; border-radius: 12px; overflow: hidden; position: relative; flex-shrink: 0; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
.home-page .dash-thumb img { width: 100%; height: 100%; object-fit: cover; }
.home-page .dash-icon { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.4); opacity: 0; transition: opacity 0.2s; }
.home-page .dash-item:hover .dash-icon, .home-page .dash-item.active .dash-icon { opacity: 1; }
.home-page .dash-icon i { font-size: 1.2rem; color: white; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5)); }
.home-page .dash-info { flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: center; }
.home-page .dash-label { font-size: 0.65rem; color: var(--accent-color, #6366f1); text-transform: uppercase; font-weight: 800; letter-spacing: 0.05em; margin-bottom: 0.35rem; }
.home-page .dash-info h4 { margin: 0 0 0.25rem 0; font-size: 1.1rem; font-weight: 700; line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #fff; }
.home-page .dash-info p { margin: 0; font-size: 0.9rem; color: rgba(255,255,255,0.6); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.home-page .dash-action-btn {
  width: 42px; height: 42px; border-radius: 50%; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.1);
  color: white; display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0;
}
.home-page .dash-action-btn:hover { background: rgba(30,30,30,0.8); border-color: rgba(255,255,255,0.2); transform: scale(1.1); }
.home-page .radio-next-list { margin-top: auto; padding-top: 1rem; }
.home-page .list-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.4); margin-bottom: 0.75rem; font-weight: 600; }
.home-page .mini-track { display: flex; gap: 0.5rem; padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.85rem; }
.home-page .mini-track:last-child { border-bottom: none; }
.home-page .track-title { color: rgba(255,255,255,0.9); font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1; }
.home-page .track-artist { color: rgba(255,255,255,0.5); max-width: 40%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: right; }
.home-page .tv-channel-strip {
  margin-top: 1rem; background: rgba(20,20,20,0.55); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
  border-radius: 20px; border: 1px solid rgba(255,255,255,0.08); padding: 1rem;
}
.home-page .tv-channel-strip-header { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; margin-bottom: 0.75rem; padding-bottom: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.06); }
.home-page .tv-channel-strip-title { font-size: 0.85rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; color: rgba(255,255,255,0.7); }
.home-page .tv-channel-strip-subtitle { font-size: 0.85rem; color: rgba(255,255,255,0.45); white-space: nowrap; }
.home-page .tv-channel-strip-list { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.75rem; }
.home-page .tv-channel-strip-item {
  appearance: none; border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.03); color: #fff;
  border-radius: 16px; padding: 0.9rem; text-align: left; cursor: pointer; transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease; min-width: 0;
}
.home-page .tv-channel-strip-item:hover { transform: translateY(-2px); background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.14); }
.home-page .tv-channel-strip-item.active { background: rgba(99,102,241,0.14); border-color: rgba(99,102,241,0.35); }
.home-page .tv-channel-strip-meta { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; margin-bottom: 0.5rem; min-width: 0; }
.home-page .tv-channel-strip-name { font-size: 0.8rem; font-weight: 700; color: rgba(255,255,255,0.75); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
.home-page .tv-channel-strip-live { flex-shrink: 0; font-size: 0.7rem; font-weight: 900; letter-spacing: 0.08em; padding: 0.18rem 0.45rem; border-radius: 999px; background: rgba(255,0,0,0.18); border: 1px solid rgba(255,0,0,0.35); color: rgba(255,255,255,0.9); text-transform: uppercase; }
.home-page .tv-channel-strip-now { font-size: 0.95rem; font-weight: 800; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 0.4rem; }
.home-page .tv-channel-strip-next { font-size: 0.8rem; color: rgba(255,255,255,0.55); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
@media (max-width: 900px) {
  .home-page .dashboard-grid { grid-template-columns: 1fr; height: auto; min-height: 0; gap: 1rem; }
  .home-page .dashboard-main { aspect-ratio: 4/3; min-height: 360px; }
  .home-page .dashboard-sidebar { padding: 1rem; height: auto; }
  .home-page .dash-content h2 { font-size: 1.75rem; }
  .home-page .dash-overlay { padding: 1.5rem; }
  .home-page .tv-channel-strip-list { display: flex; overflow-x: auto; -webkit-overflow-scrolling: touch; gap: 0.75rem; padding-bottom: 0.25rem; scroll-snap-type: x mandatory; }
  .home-page .tv-channel-strip-item { flex: 0 0 82%; max-width: 360px; scroll-snap-align: start; }
}
/* What's New at Ahoy (from Flask home.html) */
.home-page .whats-new-section { margin: 2rem 0; padding: 0; }
.home-page .whats-new-container {
  background: rgba(20,20,20,0.6); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-radius: 24px; border: 1px solid rgba(255,255,255,0.08); padding: 2rem;
  max-width: 1800px; margin: 0;
}
.home-page .whats-new-header {
  margin-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 1rem;
  display: flex; justify-content: space-between; align-items: center;
}
.home-page .whats-new-header h2 { font-size: 1.5rem; font-weight: 700; margin: 0; color: #fff; }
.home-page .view-all-link {
  color: rgba(255,255,255,0.7); text-decoration: none; font-size: 0.9rem;
  display: flex; align-items: center; gap: 0.5rem; transition: color 0.2s, gap 0.2s;
}
.home-page .view-all-link:hover { color: #fff; gap: 0.75rem; }
.home-page .whats-new-loading, .home-page .whats-new-empty { text-align: center; padding: 2rem; color: rgba(255,255,255,0.5); }
.home-page .view-archive-link { display: inline-block; margin-top: 1rem; color: rgba(99,102,241,1); text-decoration: none; font-weight: 500; }
.home-page .whats-new-updates { display: flex; flex-direction: column; gap: 1rem; }
.home-page .whats-new-item {
  display: flex; gap: 1rem; padding: 1.25rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05);
  border-radius: 16px; transition: all 0.2s ease; text-decoration: none; color: inherit;
}
.home-page .whats-new-item:hover { background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.1); transform: translateX(4px); }
.home-page .whats-new-content { flex: 1; min-width: 0; }
.home-page .whats-new-content h3 { font-size: 1.1rem; font-weight: 700; margin: 0 0 0.5rem 0; color: #fff; }
.home-page .whats-new-content p { font-size: 0.9rem; color: rgba(255,255,255,0.7); margin: 0 0 0.5rem 0; line-height: 1.5; }
.home-page .whats-new-date { font-size: 0.75rem; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.05em; }
.home-page .whats-new-arrow { display: flex; align-items: center; color: rgba(255,255,255,0.4); transition: all 0.2s; flex-shrink: 0; }
.home-page .whats-new-item:hover .whats-new-arrow { color: rgba(255,255,255,0.8); transform: translateX(4px); }
</style>
