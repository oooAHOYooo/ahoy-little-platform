<template>
  <div class="artist-detail-page" v-if="artist">
    <!-- Hero Banner -->
    <section class="artist-hero-banner">
      <div class="hero-bg-overlay"></div>
      <div class="hero-bg-image" :style="{ backgroundImage: `url(${artist.image || '/static/img/default-avatar.png'})` }"></div>
      <div class="hero-content-wrapper">
        <div class="hero-content">
          <div class="hero-avatar">
            <img :src="artist.image || '/static/img/default-avatar.png'" :alt="artist.name" class="avatar-image" />
          </div>
          <div class="hero-info">
            <h1 class="hero-name">{{ artist.name }}</h1>
            <p class="hero-genre">{{ artist.genre || artist.type || 'Artist' }}</p>
            <p class="hero-bio" v-if="artist.bio">{{ artist.bio }}</p>
            <div class="hero-actions">
              <button class="follow-button" @click="onFollow">
                <i :class="bookmarks.isBookmarked(artist) ? 'fas fa-check' : 'fas fa-plus'"></i>
                <span>{{ bookmarks.isBookmarked(artist) ? 'Following' : 'Follow Artist' }}</span>
              </button>
              <button class="follow-button" @click="onShareArtist" style="background:rgba(255,255,255,0.08)">
                <i class="fas fa-share-alt"></i>
                <span>Share</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Music Section -->
    <section class="podcasts-section" v-if="artistTracks.length">
      <div class="podcasts-section-header">
        <h2>Music</h2>
        <span class="queue-count-badge">{{ artistTracks.length }}</span>
      </div>
      <div class="episode-list">
        <article
          v-for="(t, idx) in artistTracks"
          :key="t.id"
          class="episode-row"
          :class="{ playing: playerStore.currentTrack?.id === t.id }"
          @click="playTrack(idx)"
        >
          <img class="episode-art" :src="t.cover_art || '/static/img/default-cover.jpg'" :alt="t.title" loading="lazy" />
          <div class="episode-meta">
            <div class="episode-title">{{ t.title }}</div>
            <div class="episode-show" v-if="t.duration_seconds">{{ formatDuration(t.duration_seconds) }}</div>
          </div>
          <div class="episode-actions">
            <button class="episode-btn" @click.stop="playTrack(idx)">
              <i :class="playerStore.currentTrack?.id === t.id && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
            </button>
            <button class="episode-btn" @click.stop="bookmarks.toggle({ ...t, _type: 'track' })">
              <i :class="bookmarks.isBookmarked(t) ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
            </button>
          </div>
        </article>
      </div>
    </section>

    <!-- Shows / Videos Section -->
    <section class="podcasts-section" v-if="artistShows.length">
      <div class="podcasts-section-header">
        <h2>Videos</h2>
        <span class="queue-count-badge">{{ artistShows.length }}</span>
      </div>
      <div class="shows-grid">
        <router-link
          v-for="show in artistShows"
          :key="show.id"
          :to="`/shows/${show.id}`"
          class="show-card"
        >
          <div class="show-thumbnail">
            <img :src="show.thumbnail || '/static/img/default-cover.jpg'" :alt="show.title" loading="lazy" />
            <div class="show-overlay">
              <button class="play-btn"><i class="fas fa-play"></i></button>
            </div>
          </div>
          <div class="show-info">
            <div class="show-title">{{ show.title }}</div>
          </div>
        </router-link>
      </div>
    </section>

    <!-- Empty state if no content -->
    <section class="podcasts-section" v-if="!artistTracks.length && !artistShows.length && !loading">
      <div class="empty-state" style="text-align:center;padding:40px 20px;color:rgba(255,255,255,0.5)">
        <i class="fas fa-music" style="font-size:48px;margin-bottom:16px;display:block"></i>
        <p>No content available yet for {{ artist.name }}</p>
      </div>
    </section>
  </div>

  <!-- Loading -->
  <div class="artist-detail-page" v-else>
    <section class="artist-hero-banner">
      <div class="hero-content-wrapper">
        <div class="hero-content">
          <div class="hero-avatar"><div class="skeleton" style="width:120px;height:120px;border-radius:50%"></div></div>
          <div class="hero-info">
            <div class="skeleton" style="height:28px;width:60%;margin-bottom:8px"></div>
            <div class="skeleton" style="height:16px;width:40%"></div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiFetchCached } from '../composables/useApi'
import { useBookmarks } from '../composables/useBookmarks'
import { usePlayerStore } from '../stores/player'
import { useShare, useHaptics } from '../composables/useNative'

const route = useRoute()
const playerStore = usePlayerStore()
const bookmarks = useBookmarks()
const { shareArtist } = useShare()
const haptics = useHaptics()
const loading = ref(true)

const artist = ref(null)
const allTracks = ref([])
const allShows = ref([])

const artistTracks = computed(() => {
  if (!artist.value) return []
  return allTracks.value.filter(t =>
    t.artist === artist.value.name ||
    t.artist_id === artist.value.id
  )
})

const artistShows = computed(() => {
  if (!artist.value) return []
  return allShows.value.filter(s =>
    s.host === artist.value.name ||
    s.host_id === artist.value.id
  )
})

function formatDuration(seconds) {
  if (!seconds) return ''
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function onFollow() {
  haptics.onBookmark()
  bookmarks.toggle({ ...artist.value, _type: 'artist' })
}

function onShareArtist() {
  haptics.light()
  shareArtist(artist.value)
}

function playTrack(idx) {
  playerStore.setQueue(artistTracks.value, idx)
}

onMounted(async () => {
  const slug = route.params.slug
  const [artistsData, musicData, showsData] = await Promise.all([
    apiFetchCached('/api/artists').catch(() => ({ artists: [] })),
    apiFetchCached('/api/music').catch(() => ({ tracks: [] })),
    apiFetchCached('/api/shows').catch(() => ({ shows: [] })),
  ])
  const artists = artistsData.artists || []
  allTracks.value = musicData.tracks || []
  allShows.value = showsData.shows || []

  // Match by slug or id
  artist.value = artists.find(a =>
    a.slug === slug || String(a.id) === String(slug)
  ) || null

  loading.value = false
})
</script>
