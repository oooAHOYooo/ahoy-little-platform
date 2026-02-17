<template>
  <div class="shows-page videos-page">
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
              <button type="button" class="btn btn-primary placeholder-watch-random" @click="playRandomShow">
                <i class="fas fa-play"></i> Watch Random
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Videos grid (16:9 thumbnails) -->
      <section class="shows-grid-section">
        <div class="shows-grid shows-grid-16x9">
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
              <div class="show-overlay video-card-overlay">
                <button type="button" class="show-overlay-open action-btn open-btn" title="Open" @click.stop="viewSoloShow(show)">
                  Open
                </button>
                <button
                  type="button"
                  class="show-overlay-save action-btn bm-btn"
                  :aria-pressed="isShowBookmarked(show)"
                  :class="{ bookmarked: isShowBookmarked(show) }"
                  title="Bookmark"
                  @click.stop="toggleShowBookmark(show)"
                >
                  <i :class="isShowBookmarked(show) ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
                  <span class="sr-only">{{ isShowBookmarked(show) ? 'Remove bookmark' : 'Add bookmark' }}</span>
                </button>
                <button type="button" class="play-btn" @click.stop="playShow(show)">
                  <i class="fas fa-play"></i>
                </button>
              </div>
            </div>
            <div class="show-info">
              <h4>{{ show.title }}</h4>
              <p class="show-host">{{ show.host }}</p>
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
          <p>Try a different search or check back later.</p>
          <button type="button" class="btn btn-primary" @click="clearFilters">Clear search</button>
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
  filteredShows.value = list
}

function clearSearch() {
  searchQuery.value = ''
  filterShows()
}

function clearFilters() {
  searchQuery.value = ''
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
  const base = (route.path.startsWith('/videos') ? '/videos' : '/shows')
  router.replace({ path: base, query: { ...route.query, play: show.id } })
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
  router.push({ name: 'video-detail', params: { id: show.id } })
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

.placeholder-watch-random {
  margin-top: 14px;
}

/* Video card overlay: Open top-left, Save top-right, Play center */
.video-card-overlay {
  display: flex;
  align-items: center;
  justify-content: center;
}
.video-card-overlay .show-overlay-open {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 2;
  padding: 4px 8px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: rgba(0, 0, 0, 0.5);
  color: rgba(255, 255, 255, 0.95);
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}
.video-card-overlay .show-overlay-open:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
}
.video-card-overlay .show-overlay-save {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 2;
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.5);
  color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}
.video-card-overlay .show-overlay-save:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.35);
}
.video-card-overlay .show-overlay-save.bookmarked {
  color: var(--accent-color, #00d4ff);
  border-color: rgba(0, 212, 255, 0.5);
}
.video-card-overlay .play-btn {
  position: relative;
  z-index: 1;
}

/* 16:9 video grid – enforce ratio on all videos page cards */
.videos-page .shows-grid .show-thumbnail,
.shows-grid-16x9 .show-thumbnail {
  aspect-ratio: 16 / 9;
  overflow: hidden;
}
.videos-page .shows-grid .show-thumbnail img,
.shows-grid-16x9 .show-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
</style>
