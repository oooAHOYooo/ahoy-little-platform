<template>
  <PullRefresh @refresh="onRefresh">
    <div class="music-container">
      <!-- Subpage hero (same as Podcasts / Flask subpage_hero) -->
      <section class="podcasts-hero">
        <div class="podcasts-hero-inner">
          <h1>
            <i class="fas fa-music" aria-hidden="true"></i>
            Music Library
          </h1>
          <p>Explore</p>
        </div>
      </section>

      <!-- Sub-menu filter (all screen sizes) -->
      <section class="music-library-section">
        <SubMenuFilter
          v-model="selectedArtist"
          :filters="artistFilters"
          all-value=""
          filter-all-label="All Artists"
          :show-search="true"
          search-placeholder="Search music…"
          :search-query="searchQuery"
          @update:searchQuery="searchQuery = $event"
          :sort-options="sortOptions"
          sort-label="Sort"
          :sort-by="sortBy"
          @update:sortBy="sortBy = $event"
          :show-view-toggle="true"
          :view-mode="viewMode"
          @update:viewMode="viewMode = $event"
          @action="playRandomTrack"
        >
          <template #action>
            <i class="fas fa-random" aria-hidden="true"></i>
          </template>
        </SubMenuFilter>
      </section>

      <!-- List view (default) -->
      <div v-show="viewMode === 'list' && !loading && filteredTracks.length > 0" class="music-list">
        <div class="music-table-wrap">
          <table class="music-table">
            <thead>
              <tr>
                <th class="col-art">Album</th>
                <th class="col-title-artist">Track</th>
                <th class="col-duration">Duration</th>
                <th class="col-plays col-plays-header">Plays</th>
                <th class="col-action" aria-label="Actions"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(track, idx) in filteredTracks"
                :key="track.id"
                class="music-table-row"
                :class="{ playing: playerStore.currentTrack?.id === track.id }"
                @click="playTrackAtFilteredIndex(idx)"
              >
                <td class="col-art">
                  <div class="music-table-art-wrap">
                    <img
                      class="music-table-art"
                      :src="getTrackCover(track)"
                      :alt="track.title"
                      loading="lazy"
                      @error="($event.target).src = '/static/img/default-cover.jpg'"
                    />
                    <button
                      type="button"
                      class="music-table-art-play"
                      :aria-label="playerStore.currentTrack?.id === track.id && playerStore.isPlaying ? 'Pause' : 'Play'"
                      @click.stop="playTrackAtFilteredIndex(idx)"
                    >
                      <i :class="playerStore.currentTrack?.id === track.id && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'" aria-hidden="true"></i>
                    </button>
                  </div>
                </td>
                <td class="col-title-artist">
                  <div class="music-track-meta">
                    <router-link :to="`/music/${track.id}`" class="title-link" @click.stop>
                      <span class="title-text">{{ track.title }}</span>
                    </router-link>
                    <span class="music-track-artist">{{ track.artist }}</span>
                  </div>
                </td>
                <td class="col-duration">{{ formatDuration(track.duration_seconds) }}</td>
                <td class="col-plays">{{ track.play_count || 0 }}</td>
                <td class="col-action">
                  <button
                    type="button"
                    class="episode-btn queue-btn"
                    title="Add to queue"
                    aria-label="Add to queue"
                    @click.stop="addToQueue(track)"
                  >
                    <i class="fas fa-plus" aria-hidden="true"></i>
                    <span class="sr-only">Add to queue</span>
                  </button>
                  <button
                    type="button"
                    class="episode-btn bm-btn"
                    :class="{ bookmarked: bookmarks.isBookmarked({ id: track.id }) }"
                    :aria-pressed="bookmarks.isBookmarked({ id: track.id })"
                    title="Save"
                    @click.stop="toggleBookmark(track)"
                  >
                    <i :class="bookmarks.isBookmarked({ id: track.id }) ? 'fas fa-bookmark' : 'far fa-bookmark'" aria-hidden="true"></i>
                    <span class="sr-only">Save</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="music-mobile-list">
          <div
            v-for="(track, idx) in filteredTracks"
            :key="'mobile-' + track.id"
            class="music-mobile-row"
            :class="{ playing: playerStore.currentTrack?.id === track.id }"
            @click="playTrackAtFilteredIndex(idx)"
          >
            <div class="music-mobile-art">
              <img
                class="music-mobile-art-img"
                :src="getTrackCover(track)"
                :alt="track.title"
                loading="lazy"
                @error="($event.target).src = '/static/img/default-cover.jpg'"
              />
              <button
                type="button"
                class="music-mobile-art-play"
                :aria-label="playerStore.currentTrack?.id === track.id && playerStore.isPlaying ? 'Pause' : 'Play'"
                @click.stop="playTrackAtFilteredIndex(idx)"
              >
                <i :class="playerStore.currentTrack?.id === track.id && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'" aria-hidden="true"></i>
              </button>
            </div>

            <div class="music-mobile-meta">
              <router-link :to="`/music/${track.id}`" class="music-mobile-title-link" @click.stop>
                <span class="music-mobile-title">{{ track.title }}</span>
              </router-link>
              <span class="music-mobile-artist">{{ track.artist }}</span>
            </div>

            <div class="music-mobile-right">
              <div class="music-mobile-duration">{{ formatDuration(track.duration_seconds) }}</div>
              <div class="music-mobile-actions">
                <button
                  type="button"
                  class="episode-btn music-mobile-btn music-mobile-play-btn"
                  :title="playerStore.currentTrack?.id === track.id && playerStore.isPlaying ? 'Pause' : 'Play'"
                  :aria-label="playerStore.currentTrack?.id === track.id && playerStore.isPlaying ? 'Pause' : 'Play'"
                  @click.stop="playTrackAtFilteredIndex(idx)"
                >
                  <i :class="playerStore.currentTrack?.id === track.id && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'" aria-hidden="true"></i>
                </button>
                <button
                  type="button"
                  class="episode-btn queue-btn music-mobile-btn"
                  title="Add to queue"
                  aria-label="Add to queue"
                  @click.stop="addToQueue(track)"
                >
                  <i class="fas fa-plus" aria-hidden="true"></i>
                </button>
                <button
                  type="button"
                  class="episode-btn bm-btn music-mobile-btn"
                  :class="{ bookmarked: bookmarks.isBookmarked({ id: track.id }) }"
                  :aria-pressed="bookmarks.isBookmarked({ id: track.id })"
                  title="Save"
                  @click.stop="toggleBookmark(track)"
                >
                  <i :class="bookmarks.isBookmarked({ id: track.id }) ? 'fas fa-bookmark' : 'far fa-bookmark'" aria-hidden="true"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Grid view -->
      <div v-show="viewMode === 'grid' && !loading && filteredTracks.length > 0" class="music-grid">
        <div
          v-for="(track, idx) in filteredTracks"
          :key="track.id"
          class="track-card"
          :class="{ playing: playerStore.currentTrack?.id === track.id }"
        >
          <div class="track-cover" @click="playTrackAtFilteredIndex(idx)">
            <img
              :src="getTrackCover(track)"
              :alt="track.title"
              loading="lazy"
              @error="($event.target).src = '/static/img/default-cover.jpg'"
            />
            <div class="track-overlay">
              <button type="button" class="play-btn" @click.stop="playTrackAtFilteredIndex(idx)">
                <i :class="playerStore.currentTrack?.id === track.id && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
              </button>
              <button
                type="button"
                class="track-overlay-btn add-to-playlist-btn"
                title="Add to queue"
                @click.stop="addToQueue(track)"
              >
                <i class="fas fa-plus"></i>
              </button>
              <button
                type="button"
                class="track-overlay-btn bm-btn"
                :title="bookmarks.isBookmarked({ id: track.id }) ? 'Unsave' : 'Save'"
                @click.stop="toggleBookmark(track)"
              >
                <i :class="bookmarks.isBookmarked({ id: track.id }) ? 'fas fa-bookmark' : 'far fa-bookmark'" aria-hidden="true"></i>
              </button>
            </div>
          </div>
          <router-link :to="`/music/${track.id}`" class="track-info" style="text-decoration:none;color:inherit">
            <div class="track-title">{{ track.title }}</div>
            <div class="track-artist">{{ track.artist }}</div>
            <div class="track-duration">{{ formatDuration(track.duration_seconds) }}</div>
          </router-link>
        </div>
      </div>

      <!-- Loading skeletons -->
      <div v-if="loading" class="music-grid">
        <div v-for="i in 8" :key="i" class="track-card">
          <div class="track-cover skeleton"></div>
          <div class="track-info">
            <div class="skeleton" style="height:14px;width:60%;margin-bottom:6px"></div>
            <div class="skeleton" style="height:12px;width:40%;margin-bottom:4px"></div>
            <div class="skeleton" style="height:10px;width:36px"></div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else-if="!loading && filteredTracks.length === 0" class="empty-state">
        <i class="fas fa-music"></i>
        <h3>No music found</h3>
        <p>Try adjusting your filters or search terms</p>
      </div>
    </div>
  </PullRefresh>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '../composables/useApi'
import { usePlayerStore } from '../stores/player'
import { useAddToPlaylist } from '../composables/useAddToPlaylist'
import { useBookmarks } from '../composables/useBookmarks'
import PullRefresh from '../components/PullRefresh.vue'
import SubMenuFilter from '../components/SubMenuFilter.vue'

const router = useRouter()
const playerStore = usePlayerStore()
const addToPlaylist = useAddToPlaylist()
const bookmarks = useBookmarks()

function toggleBookmark(track) {
  bookmarks.toggle({
    type: 'track',
    id: track.id,
    title: track.title,
    cover_art: track.cover_art,
  })
}

function getTrackCover(track) {
  const url = track && (track.cover_art || track.artwork)
  if (typeof url === 'string' && url.trim()) return url
  return '/static/img/default-cover.jpg'
}

function openAddToPlaylist(track) {
  addToPlaylist.open(track)
}

const tracks = ref([])
const loading = ref(true)
const searchQuery = ref('')
const selectedArtist = ref('')
const sortBy = ref('plays')
const viewMode = ref('list') // default table/list like Flask

const artists = computed(() => {
  const set = new Set()
  for (const t of tracks.value) {
    if (t.artist) set.add(t.artist)
  }
  return Array.from(set).sort()
})

// For SubMenuFilter: { value, label, image }
const artistFilters = computed(() => {
  const byName = new Map()
  for (const t of tracks.value) {
    if (!t.artist) continue
    if (!byName.has(t.artist)) {
      byName.set(t.artist, {
        value: t.artist,
        label: t.artist,
        image: t.cover_art || t.artwork || null
      })
    }
  }
  return Array.from(byName.values()).sort((a, b) => (a.label || '').localeCompare(b.label || ''))
})

const sortOptions = [
  { value: 'title', label: 'Title' },
  { value: 'artist', label: 'Artist' },
  { value: 'plays', label: 'Plays' },
  { value: 'added_date', label: 'Date Added' }
]

const filteredTracks = computed(() => {
  let list = [...tracks.value]
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(
      (t) =>
        (t.title || '').toLowerCase().includes(q) ||
        (t.artist || '').toLowerCase().includes(q) ||
        (t.album || '').toLowerCase().includes(q)
    )
  }
  if (selectedArtist.value) {
    list = list.filter((t) => t.artist === selectedArtist.value)
  }
  list.sort((a, b) => {
    switch (sortBy.value) {
      case 'title':
        return (a.title || '').localeCompare(b.title || '')
      case 'artist':
        return (a.artist || '').localeCompare(b.artist || '')
      case 'added_date':
        return new Date(b.added_date || 0) - new Date(a.added_date || 0)
      case 'plays':
        return (b.play_count || 0) - (a.play_count || 0)
      default:
        return 0
    }
  })
  return list
})

function formatDuration(seconds) {
  if (!seconds && seconds !== 0) return '0:00'
  const m = Math.floor(Number(seconds) / 60)
  const s = Math.floor(Number(seconds) % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function playTrackAtFilteredIndex(idx) {
  const list = filteredTracks.value
  const track = list[idx]
  if (!track) return
  if (playerStore.currentTrack?.id === track.id && playerStore.isPlaying) {
    playerStore.pause()
    return
  }
  playerStore.setQueue(list, idx)
}

function addToQueue(track) {
  playerStore.addToQueue({
    type: 'track',
    id: track.id,
    title: track.title,
    artist: track.artist,
    cover_art: track.cover_art,
    duration_seconds: track.duration_seconds,
  })
}

function playRandomTrack() {
  if (filteredTracks.value.length === 0) return
  const idx = Math.floor(Math.random() * filteredTracks.value.length)
  playTrackAtFilteredIndex(idx)
}

async function loadTracks() {
  loading.value = true
  try {
    const data = await apiFetch('/api/music?t=' + Date.now())
    tracks.value = data.tracks || []
  } catch {
    tracks.value = []
  }
  loading.value = false
}

async function onRefresh(done) {
  try {
    const data = await apiFetch('/api/music?t=' + Date.now())
    tracks.value = data.tracks || []
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
.track-duration {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}
.empty-state {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.7);
}
.empty-state i {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  opacity: 0.6;
}
.empty-state h3 {
  margin: 0 0 0.25rem;
  font-size: 1.1rem;
}
.empty-state p {
  margin: 0;
  font-size: 0.9rem;
}

.music-mobile-list {
  display: none;
}

@media (max-width: 768px) {
  .music-container {
    padding-left: 0 !important;
    padding-right: 0 !important;
    margin: 0 !important;
  }

  /* Force content area to be flush for this view */
  :deep(.content-area) {
    padding-left: 0 !important;
    padding-right: 0 !important;
    margin: 0 !important;
  }

  .music-table-wrap {
    display: none;
  }

  .music-mobile-list {
    display: flex;
    flex-direction: column;
    gap: 0;
    padding: 0 !important;
    margin: 0 !important; /* Vital for flush look */
    width: 100% !important;
  }

  .music-mobile-row {
    display: grid;
    grid-template-columns: 48px minmax(0, 1fr) auto;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-radius: 0 !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
    width: 100% !important;
    margin: 0 !important;
    box-shadow: none !important;
  }

  .music-mobile-row.playing {
    background: rgba(99, 102, 241, 0.1) !important;
  }

  .music-mobile-art {
    position: relative;
    width: 44px;
    height: 44px;
    border-radius: 4px;
    overflow: hidden;
    flex-shrink: 0;
  }

  .music-mobile-art-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  .music-mobile-art-play {
    position: absolute;
    inset: 0;
    border: none;
    background: rgba(0, 0, 0, 0.42);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
  }

  .music-mobile-meta {
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0 !important;
  }

  .music-mobile-title-link {
    color: inherit;
    text-decoration: none;
    min-width: 0 !important;
    min-height: 0 !important; /* Override global mobile touch target size */
    display: block;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.1 !important;
  }

  .music-mobile-title {
    display: block;
    font-size: 15px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.95);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.1 !important;
  }

  .music-mobile-artist {
    display: block;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.5);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.1 !important;
    margin-top: 1px !important; /* Tiny optical separation */
  }

  .music-mobile-right {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 8px;
  }

  .music-mobile-duration {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.45);
    font-variant-numeric: tabular-nums;
    margin-right: 4px;
  }

  .music-mobile-actions {
    display: flex;
    gap: 4px;
  }

  .music-mobile-btn {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    font-size: 12px;
    padding: 0;
    background: rgba(255, 255, 255, 0.05);
  }

  .music-mobile-play-btn {
    background: linear-gradient(180deg, rgba(109, 220, 255, 0.15), rgba(109, 220, 255, 0.08));
    border: 1px solid rgba(109, 220, 255, 0.15);
    color: rgba(255, 255, 255, 0.85);
  }
}


</style>
