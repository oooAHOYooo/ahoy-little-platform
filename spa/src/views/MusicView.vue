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

      <!-- Music header: same UI pattern as Podcasts (section header + filter chips + toolbar) -->
      <section class="podcasts-section podcasts-featured-section">
        <div class="podcasts-section-header podcasts-featured-header">
          <div>
            <h2>Tracks</h2>
            <p class="podcasts-section-subtitle">Filter by artist or search. Sort and switch between list and grid.</p>
          </div>
          <div class="podcast-filter-chips">
            <button
              type="button"
              class="podcast-filter-chip"
              :class="{ active: !selectedArtist }"
              @click="selectedArtist = ''"
            >
              All
            </button>
            <button
              v-for="artist in artists.slice(0, 14)"
              :key="artist"
              type="button"
              class="podcast-filter-chip"
              :class="{ active: selectedArtist === artist }"
              @click="selectedArtist = artist"
            >
              {{ artist }}
            </button>
          </div>
        </div>
        <!-- Mobile: dropdown artist picker -->
        <div class="podcast-shows-dropdown-mobile">
          <select v-model="selectedArtist" class="podcast-show-select" aria-label="Filter by artist">
            <option value="">All Artists</option>
            <option v-for="artist in artists" :key="artist" :value="artist">{{ artist }}</option>
          </select>
        </div>
        <!-- Toolbar: search, sort, view, play random -->
        <div class="music-header-toolbar">
          <div class="search-bar music-toolbar-search">
            <i class="fas fa-search" aria-hidden="true"></i>
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="Search music..."
              aria-label="Search music"
            />
            <button v-show="searchQuery" type="button" class="search-clear" aria-label="Clear search" @click="searchQuery = ''">
              <i class="fas fa-times" aria-hidden="true"></i>
            </button>
          </div>
          <select v-model="sortBy" class="music-toolbar-sort" aria-label="Sort music">
            <option value="title">Title</option>
            <option value="artist">Artist</option>
            <option value="plays">Plays</option>
            <option value="added_date">Date Added</option>
          </select>
          <div class="view-options">
            <button
              type="button"
              class="view-btn"
              :class="{ active: viewMode === 'grid' }"
              aria-label="Grid view"
              @click="viewMode = 'grid'"
            >
              <i class="fas fa-th" aria-hidden="true"></i>
            </button>
            <button
              type="button"
              class="view-btn"
              :class="{ active: viewMode === 'list' }"
              aria-label="List view"
              @click="viewMode = 'list'"
            >
              <i class="fas fa-list" aria-hidden="true"></i>
            </button>
          </div>
          <button
            type="button"
            class="episode-btn music-toolbar-play"
            title="Play Random"
            @click="playRandomTrack"
          >
            <i class="fas fa-random" aria-hidden="true"></i>
            <span class="sr-only">Play Random</span>
          </button>
        </div>
      </section>

      <!-- List view (default) -->
      <div v-show="viewMode === 'list' && !loading && filteredTracks.length > 0" class="music-list">
        <div class="music-table-wrap">
          <table class="music-table">
            <thead>
              <tr>
                <th class="col-cover"></th>
                <th class="col-play"></th>
                <th class="col-title">Title</th>
                <th class="col-artist">Artist</th>
                <th class="col-duration">Time</th>
                <th class="col-plays">Plays</th>
                <th class="col-action">Actions</th>
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
                <td class="col-cover">
                  <img
                    class="music-table-thumb"
                    :src="getTrackCover(track)"
                    :alt="track.title"
                    loading="lazy"
                    @error="($event.target).src = '/static/img/default-cover.jpg'"
                  />
                </td>
                <td class="col-play">
                  <button
                    type="button"
                    class="play-btn"
                    :aria-label="playerStore.currentTrack?.id === track.id && playerStore.isPlaying ? 'Pause' : 'Play'"
                    @click.stop="playTrackAtFilteredIndex(idx)"
                  >
                    <i :class="playerStore.currentTrack?.id === track.id && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
                  </button>
                </td>
                <td class="col-title">
                  <router-link :to="`/music/${track.id}`" class="title-text" @click.stop>{{ track.title }}</router-link>
                </td>
                <td class="col-artist">{{ track.artist }}</td>
                <td class="col-duration">{{ formatDuration(track.duration_seconds) }}</td>
                <td class="col-plays">{{ track.play_count || 0 }}</td>
                <td class="col-action">
                  <button
                    type="button"
                    class="action-btn queue-btn"
                    :class="{ 'in-queue': playerStore.isInQueue({ id: track.id }) }"
                    title="Add to queue"
                    :aria-label="playerStore.isInQueue({ id: track.id }) ? 'In queue' : 'Add to queue'"
                    @click.stop="addToQueue(track)"
                  >
                    <i :class="playerStore.isInQueue({ id: track.id }) ? 'fas fa-check' : 'fas fa-plus'"></i>
                    <span class="sr-only">Add to queue</span>
                  </button>
                  <button
                    type="button"
                    class="action-btn boost-btn"
                    :title="'Boost ' + (track.artist || 'artist')"
                    aria-label="Boost artist"
                    @click.stop="openBoost(track)"
                  >
                    <i class="fas fa-heart"></i>
                    <span class="sr-only">Boost</span>
                  </button>
                  <button
                    type="button"
                    class="action-btn bm-btn"
                    :class="{ bookmarked: bookmarks.isBookmarked({ id: track.id }) }"
                    :aria-pressed="bookmarks.isBookmarked({ id: track.id })"
                    title="Save"
                    @click.stop="toggleBookmark(track)"
                  >
                    <i :class="bookmarks.isBookmarked({ id: track.id }) ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
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
                class="track-overlay-btn boost-btn"
                title="Boost artist"
                @click.stop="openBoost(track)"
              >
                <i class="fas fa-heart"></i>
              </button>
              <button
                type="button"
                class="track-overlay-btn bm-btn"
                :title="bookmarks.isBookmarked({ id: track.id }) ? 'Unsave' : 'Save'"
                @click.stop="toggleBookmark(track)"
              >
                <i :class="bookmarks.isBookmarked({ id: track.id }) ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
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
import { apiFetch } from '../composables/useApi'
import { usePlayerStore } from '../stores/player'
import { useAddToPlaylist } from '../composables/useAddToPlaylist'
import { useBookmarks } from '../composables/useBookmarks'
import PullRefresh from '../components/PullRefresh.vue'

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

function openBoost(track) {
  if (!track || !track.artist) return
  const detail = {
    recipientType: 'artist',
    recipientId: track.artist_slug || track.artist,
    recipientName: track.artist,
  }
  if (typeof document !== 'undefined' && document.dispatchEvent) {
    document.dispatchEvent(new CustomEvent('ahoy:boost:open', { detail }))
  } else {
    const params = new URLSearchParams({ type: 'boost', artist_id: detail.recipientId || detail.recipientName, amount: '1' })
    window.location.href = `/checkout?${params.toString()}`
  }
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
</style>
