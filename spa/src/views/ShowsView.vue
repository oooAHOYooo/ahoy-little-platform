<template>
  <div class="shows-page">
    <div class="shows-container">
      <!-- Global subpage hero (mobile: compact two-line like other pages) -->
      <section class="podcasts-hero shows-page-hero">
        <div class="podcasts-hero-inner">
          <h1><i class="fas fa-video" aria-hidden="true"></i> Videos</h1>
          <p>Music videos, skate parts, short films, episodes, and more</p>
        </div>
      </section>

      <!-- Embedded Video Player Section (same as Flask) -->
      <section ref="playerSectionRef" class="embedded-video-section">
        <div class="video-player-wrapper">
          <!-- Video Player -->
          <div v-show="currentVideo" class="embedded-video-player">
            <!-- Native video for direct MP4/URL -->
            <video
              v-if="currentVideo && isDirectVideoUrl(videoSrc(currentVideo))"
              ref="videoEl"
              :src="videoSrc(currentVideo)"
              :poster="currentVideo.thumbnail || ''"
              controls
              class="embedded-video"
              playsinline
              @loadedmetadata="onVideoLoaded"
              @play="isPlaying = true"
              @pause="isPlaying = false"
              @ended="onVideoEnded"
            >
              Your browser does not support the video tag.
            </video>
            <!-- Embed for YouTube/Vimeo: click-to-load (YouTube-style) so embed loads on user gesture (fixes mobile) -->
            <template v-else-if="currentVideo && embedUrlFor(currentVideo)">
              <div
                v-if="!embedLoaded"
                class="video-embed-poster"
                role="button"
                tabindex="0"
                :aria-label="'Play ' + (currentVideo?.title || 'video')"
                @click="loadEmbed"
                @keydown.enter.prevent="loadEmbed"
                @keydown.space.prevent="loadEmbed"
              >
                <img
                  :src="currentVideo.thumbnail || ''"
                  :alt="currentVideo?.title || ''"
                  class="video-embed-poster-img"
                />
                <div class="video-embed-poster-play">
                  <i class="fas fa-play"></i>
                </div>
              </div>
              <div
                v-else
                class="video-embed-wrap"
                style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;background:#000"
              >
                <iframe
                  :src="embedSrc"
                  style="position:absolute;top:0;left:0;width:100%;height:100%;border:0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen
                />
              </div>
            </template>
            <div class="video-info-overlay">
              <div class="video-info-content">
                <h2 class="video-title">{{ currentVideo?.title || 'Untitled' }}</h2>
                <div class="video-meta">
                  <span class="video-host">{{ currentVideo?.host || '' }}</span>
                  <span v-if="currentVideo?.type" class="video-type">
                    {{ String(currentVideo.type || '').replace(/_/g, ' ') }}
                  </span>
                </div>
                <p class="video-description">{{ currentVideo?.description || '' }}</p>
              </div>
              <div class="video-actions-bar">
                <button type="button" class="action-btn view-solo-btn" title="View Solo" @click="viewSolo">
                  <i class="fas fa-external-link-alt"></i>
                  <span class="sr-only">View Solo</span>
                </button>
                <button
                  type="button"
                  class="action-btn bookmark-btn"
                  :class="{ bookmarked: isShowBookmarked(currentVideo) }"
                  :aria-pressed="isShowBookmarked(currentVideo)"
                  :title="isShowBookmarked(currentVideo) ? 'Remove bookmark' : 'Bookmark'"
                  @click="toggleShowBookmark(currentVideo)"
                >
                  <i :class="isShowBookmarked(currentVideo) ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
                  <span class="sr-only">{{ isShowBookmarked(currentVideo) ? 'Remove bookmark' : 'Bookmark' }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Placeholder when no video selected -->
          <div v-show="!currentVideo" class="video-placeholder">
            <div class="placeholder-content">
              <i class="fas fa-play-circle"></i>
              <h3>Select a video to play</h3>
              <p>Click on any video below to start watching</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Unified Header Section (same as Flask) -->
      <section class="unified-header shows-subheader">
        <div class="header-content">
          <div class="header-title">
            <div v-if="featuredShow" class="hero-media">
              <img
                :src="featuredShow.thumbnail || '/static/img/default-cover.jpg'"
                :alt="featuredShow.title"
                class="hero-thumbnail image-placeholder"
              />
              <div class="hero-media-overlay">
                <button type="button" class="hero-play-btn" @click="playShow(featuredShow)">
                  <i class="fas fa-play"></i>
                </button>
              </div>
            </div>
            <div class="title-text">
              <h1>Videos</h1>
              <p>Music videos, skate parts, short films, episodes, and more</p>
            </div>
          </div>

          <div class="header-search desktop-only">
            <div class="search-bar">
              <i class="fas fa-search"></i>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search shows, hosts, or descriptions..."
                class="search-input"
                @input="filterShows"
              />
              <button v-show="searchQuery" type="button" class="search-clear" @click="clearSearch">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
          <div class="header-search mobile-only">
            <div class="search-bar">
              <i class="fas fa-search"></i>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search shows..."
                class="search-input"
                @input="filterShows"
              />
              <button v-show="searchQuery" type="button" class="search-clear" @click="clearSearch">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>

          <div class="header-filters">
            <div class="filter-tabs">
              <button
                type="button"
                class="filter-tab"
                :class="{ active: selectedCategory === 'all' }"
                @click="setCategory('all')"
              >
                All Videos
              </button>
              <button
                type="button"
                class="filter-tab"
                :class="{ active: selectedCategory === 'video_podcast' }"
                @click="setCategory('video_podcast')"
              >
                Video Podcast
              </button>
              <button
                type="button"
                class="filter-tab"
                :class="{ active: selectedCategory === 'episode' }"
                @click="setCategory('episode')"
              >
                Episodes
              </button>
              <button
                type="button"
                class="filter-tab"
                :class="{ active: selectedCategory === 'clip' }"
                @click="setCategory('clip')"
              >
                Clips
              </button>
              <button
                type="button"
                class="filter-tab"
                :class="{ active: selectedCategory === 'music_video' }"
                @click="setCategory('music_video')"
              >
                Music Videos
              </button>
              <button
                type="button"
                class="filter-tab"
                :class="{ active: selectedCategory === 'broadcast' }"
                @click="setCategory('broadcast')"
              >
                Live Broadcasts
              </button>
            </div>
          </div>

          <div class="header-actions">
            <div class="view-options">
              <button
                type="button"
                class="view-btn"
                :class="{ active: viewMode === 'grid' }"
                @click="viewMode = 'grid'"
              >
                <i class="fas fa-th"></i>
              </button>
              <button
                type="button"
                class="view-btn"
                :class="{ active: viewMode === 'list' }"
                @click="viewMode = 'list'"
              >
                <i class="fas fa-list"></i>
              </button>
            </div>
            <button type="button" class="btn btn-primary btn-large" @click="playRandomShow">
              <i class="fas fa-play"></i> Watch Random Show
            </button>
          </div>
        </div>
      </section>

      <!-- Shows Grid / List -->
      <section class="shows-grid-section">
        <div class="section-header">
          <h2><i class="fas fa-th"></i> All Videos</h2>
        </div>

        <!-- Grid View -->
        <div v-show="viewMode === 'grid'" class="shows-grid">
          <div
            v-for="show in filteredShows"
            :key="show.id"
            class="show-card"
            :class="{ 'now-playing': currentVideo && currentVideo.id === show.id }"
            @click="playShow(show)"
          >
            <div class="show-thumbnail">
              <img
                :src="show.thumbnail || '/static/img/default-cover.jpg'"
                :alt="show.title"
                loading="lazy"
                decoding="async"
                class="image-placeholder"
              />
              <div class="show-overlay">
                <button type="button" class="play-btn" @click.stop="playShow(show)">
                  <i class="fas fa-play"></i>
                </button>
                <div class="show-actions">
                  <button
                    type="button"
                    class="action-btn view-solo-mini-btn"
                    title="View Solo"
                    @click.stop="viewSoloShow(show)"
                  >
                    <i class="fas fa-external-link-alt"></i>
                  </button>
                  <button
                    type="button"
                    class="action-btn bm-btn"
                    :aria-pressed="isShowBookmarked(show)"
                    :class="{ bookmarked: isShowBookmarked(show) }"
                    title="Bookmark"
                    @click.stop="toggleShowBookmark(show)"
                  >
                    <i :class="isShowBookmarked(show) ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
                    <span class="sr-only">{{ isShowBookmarked(show) ? 'Remove bookmark' : 'Add bookmark' }}</span>
                  </button>
                </div>
              </div>
            </div>
            <div class="show-info">
              <h4>{{ show.title }}</h4>
              <p class="show-host">{{ show.host }}</p>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-show="viewMode === 'list'" class="shows-list">
          <div class="list-header">
            <span class="col-thumbnail">Thumbnail</span>
            <span class="col-title">Title</span>
            <span class="col-host">Host</span>
            <span class="col-actions">Actions</span>
          </div>
          <div class="list-items">
            <div
              v-for="show in filteredShows"
              :key="show.id"
              class="list-item"
              :class="{ 'now-playing': currentVideo && currentVideo.id === show.id }"
              @click="playShow(show)"
            >
              <div class="col-thumbnail">
                <img
                  :src="show.thumbnail || '/static/img/default-cover.jpg'"
                  :alt="show.title"
                  loading="lazy"
                  decoding="async"
                  class="image-placeholder"
                />
                <div class="play-overlay">
                  <i class="fas fa-play"></i>
                </div>
              </div>
              <div class="col-title">
                <h4>{{ show.title }}</h4>
                <p>{{ (show.description || '').substring(0, 100) }}{{ (show.description || '').length > 100 ? '...' : '' }}</p>
              </div>
              <span class="col-host">{{ show.host }}</span>
              <div class="col-actions">
                <button
                  type="button"
                  class="action-btn view-solo-mini-btn"
                  title="View Solo"
                  @click.stop="viewSoloShow(show)"
                >
                  <i class="fas fa-external-link-alt"></i>
                  <span class="sr-only">View Solo</span>
                </button>
                <button
                  type="button"
                  class="action-btn bm-btn"
                  :aria-pressed="isShowBookmarked(show)"
                  :class="{ bookmarked: isShowBookmarked(show) }"
                  title="Bookmark"
                  @click.stop="toggleShowBookmark(show)"
                >
                  <i :class="isShowBookmarked(show) ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
                  <span class="sr-only">{{ isShowBookmarked(show) ? 'Remove bookmark' : 'Add bookmark' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Loading State -->
      <section v-show="isLoading" class="loading-section">
        <div class="spinner"></div>
        <p>Loading videos...</p>
      </section>

      <!-- Empty State -->
      <section v-show="!isLoading && filteredShows.length === 0" class="empty-section">
        <div class="empty-content">
          <i class="fas fa-play-circle"></i>
          <h3>No videos found</h3>
          <p>Try adjusting your search or filters</p>
          <button type="button" class="btn btn-primary" @click="clearFilters">Clear Filters</button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetchCached } from '../composables/useApi'
import { useBookmarks } from '../composables/useBookmarks'
import { trackRecentPlay } from '../composables/useRecentlyPlayed'

const route = useRoute()
const router = useRouter()
const bookmarks = useBookmarks()

const shows = ref([])
const filteredShows = ref([])
const featuredShow = ref(null)
const searchQuery = ref('')
const selectedCategory = ref('all')
const viewMode = ref('grid')
const isLoading = ref(true)
const currentVideo = ref(null)
const isPlaying = ref(false)
const videoEl = ref(null)
const playerSectionRef = ref(null)
// YouTube-style click-to-load: embed iframe only after user tap (fixes mobile)
const embedLoaded = ref(false)
const embedSrc = ref('')

// Sync URL ?play=id with current video and auto-play on load
function applyPlayFromUrl() {
  const playId = route.query.play
  if (!playId || !shows.value.length) return
  const show = shows.value.find(s => String(s.id) === String(playId))
  if (show) {
    currentVideo.value = show
    nextTickPlay()
  }
}

function nextTickPlay() {
  setTimeout(() => {
    if (videoEl.value) {
      videoEl.value.load()
      videoEl.value.play().catch(() => {})
    }
  }, 100)
}

function videoSrc(show) {
  if (!show) return ''
  return show.video_url || show.mp4_link || show.trailer_url || show.url || ''
}

function isDirectVideoUrl(url) {
  if (!url) return false
  const u = url.toLowerCase()
  return u.endsWith('.mp4') || u.endsWith('.webm') || u.endsWith('.mov') || u.includes('/mp4') || u.startsWith('blob:')
}

function embedUrlFor(show) {
  const url = videoSrc(show)
  const ytMatch = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&]+)/)
  if (ytMatch) return `https://www.youtube.com/embed/${ytMatch[1]}`
  const vimeoMatch = url.match(/vimeo\.com\/(\d+)/)
  if (vimeoMatch) return `https://player.vimeo.com/video/${vimeoMatch[1]}`
  return null
}

function filterShows() {
  let list = [...shows.value]
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(
      s =>
        (s.title || '').toLowerCase().includes(q) ||
        (s.host || '').toLowerCase().includes(q) ||
        (s.description || '').toLowerCase().includes(q)
    )
  }
  if (selectedCategory.value === 'video_podcast') {
    list = list.filter(s => (s.tags || []).includes('video-podcast'))
  } else if (selectedCategory.value !== 'all') {
    list = list.filter(s => (s.type || s.category || '') === selectedCategory.value)
  }
  filteredShows.value = list
}

function setCategory(cat) {
  selectedCategory.value = cat
  filterShows()
}

function clearSearch() {
  searchQuery.value = ''
  filterShows()
}

function clearFilters() {
  searchQuery.value = ''
  selectedCategory.value = 'all'
  filterShows()
}

function playShow(show) {
  currentVideo.value = show
  // Reset embed state when switching video; embeds load on first tap (loadEmbed)
  embedLoaded.value = false
  embedSrc.value = ''
  trackRecentPlay({
    id: show.id,
    type: 'show',
    title: show.title,
    host: show.host,
    thumbnail: show.thumbnail,
    url: show.video_url || show.mp4_link || show.trailer_url || show.url,
  })
  router.replace({ path: '/shows', query: { ...route.query, play: show.id } })
  nextTickPlay()
  // Scroll player into view (especially on mobile) so user sees the video load
  setTimeout(() => {
    playerSectionRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, 100)
}

function loadEmbed() {
  if (!currentVideo.value) return
  const url = embedUrlFor(currentVideo.value)
  if (url) {
    embedSrc.value = url
    embedLoaded.value = true
  }
}

function viewSolo() {
  if (currentVideo.value) viewSoloShow(currentVideo.value)
}

function viewSoloShow(show) {
  router.push({ name: 'show-detail', params: { id: show.id } })
}

function onVideoLoaded() {}
function onVideoEnded() {
  isPlaying.value = false
}

function playRandomShow() {
  if (shows.value.length) {
    const random = shows.value[Math.floor(Math.random() * shows.value.length)]
    playShow(random)
  }
}

function toBookmarkItem(show) {
  return {
    type: 'show',
    _type: 'show',
    id: show.id,
    title: show.title,
    thumbnail: show.thumbnail,
    artwork: show.thumbnail,
  }
}

function isShowBookmarked(show) {
  if (!show) return false
  return bookmarks.isBookmarked(toBookmarkItem(show))
}

function toggleShowBookmark(show) {
  if (!show) return
  bookmarks.toggle(toBookmarkItem(show))
}

onMounted(async () => {
  isLoading.value = true
  try {
    const data = await apiFetchCached('/api/shows').catch(() => ({ shows: [] }))
    const list = data.shows || []
    shows.value = list
    filteredShows.value = [...list]
    if (list.length) {
      featuredShow.value = list[Math.floor(Math.random() * list.length)]
    }
    filterShows()
    applyPlayFromUrl()
  } finally {
    isLoading.value = false
  }
})

watch(
  () => route.query.play,
  () => {
    applyPlayFromUrl()
  }
)
</script>

<style scoped>
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
.video-embed-wrap {
  border-radius: 20px;
  overflow: hidden;
}
/* YouTube-style click-to-load poster */
.video-embed-poster {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  height: 0;
  overflow: hidden;
  background: #000;
  border-radius: 20px;
  cursor: pointer;
}
.video-embed-poster-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.video-embed-poster-play {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 68px;
  height: 68px;
  border-radius: 50%;
  background: rgba(255, 0, 96, 0.9);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  box-shadow: 0 4px 24px rgba(255, 0, 96, 0.5);
  transition: transform 0.2s ease, background 0.2s ease;
}
.video-embed-poster:hover .video-embed-poster-play,
.video-embed-poster:focus .video-embed-poster-play {
  transform: translate(-50%, -50%) scale(1.08);
  background: rgba(255, 0, 96, 1);
}
</style>
