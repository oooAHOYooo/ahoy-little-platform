<template>
  <div class="podcast-show-page" v-if="show">
    <!-- Hero -->
    <section class="podcast-show-hero">
      <img
        class="podcast-show-hero-art"
        :src="show.artwork || '/static/img/default-cover.jpg'"
        :alt="show.title"
      />
      <div class="podcast-show-hero-meta">
        <div class="podcast-show-hero-kicker">Podcast</div>
        <h1 class="podcast-show-hero-title">{{ show.title }}</h1>
        <p class="podcast-show-hero-desc" v-if="show.description">{{ show.description }}</p>
        <div class="podcast-show-hero-actions">
          <button class="podcast-cta" @click="playLatest">
            <i class="fas fa-play"></i>
            Play Latest
          </button>
          <button class="podcast-cta secondary" @click="bookmarks.toggle({ ...show, _type: 'podcast' })">
            <i :class="bookmarks.isBookmarked(show) ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
            {{ bookmarks.isBookmarked(show) ? 'Saved' : 'Save' }}
          </button>
        </div>
      </div>
    </section>

    <!-- Episodes -->
    <section class="podcasts-section" style="margin-top:16px">
      <div class="podcasts-section-header">
        <h2>Episodes</h2>
        <span class="queue-count-badge">{{ episodes.length }}</span>
      </div>
      <div class="episode-list">
        <article
          v-for="(ep, idx) in episodes"
          :key="ep.id || ep.key || idx"
          class="episode-row"
          :class="{ playing: playerStore.currentTrack?.id === (ep.id || ep.key) }"
          @click="playEpisode(idx)"
        >
          <img class="episode-art" :src="ep.cover_art || ep.artwork || show.artwork || '/static/img/default-cover.jpg'" :alt="ep.title" loading="lazy" />
          <div class="episode-meta">
            <div class="episode-title">{{ ep.title }}</div>
            <div class="episode-subtitle">
              <span class="episode-time" v-if="ep.date">{{ ep.date }}</span>
              <span class="episode-dot" v-if="ep.date && ep.duration_seconds"> · </span>
              <span class="episode-time" v-if="ep.duration_seconds">{{ formatDuration(ep.duration_seconds) }}</span>
            </div>
            <div class="episode-desc" v-if="ep.description">{{ truncate(ep.description, 120) }}</div>
          </div>
          <div class="episode-actions">
            <button class="episode-btn" @click.stop="playEpisode(idx)">
              <i :class="playerStore.currentTrack?.id === (ep.id || ep.key) && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
            </button>
          </div>
        </article>
      </div>
    </section>

    <!-- Empty episodes state -->
    <section class="podcasts-section" v-if="!episodes.length" style="margin-top:16px">
      <div class="empty-state" style="text-align:center;padding:40px 20px;color:rgba(255,255,255,0.5)">
        <i class="fas fa-podcast" style="font-size:48px;margin-bottom:16px;display:block"></i>
        <p>No episodes available yet</p>
      </div>
    </section>
  </div>

  <!-- Loading -->
  <div class="podcast-show-page" v-else>
    <section class="podcast-show-hero">
      <div class="podcast-show-hero-art skeleton" style="aspect-ratio:1;width:100%"></div>
      <div class="podcast-show-hero-meta">
        <div class="skeleton" style="height:14px;width:30%;margin-bottom:8px"></div>
        <div class="skeleton" style="height:24px;width:60%;margin-bottom:8px"></div>
        <div class="skeleton" style="height:14px;width:80%"></div>
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

const route = useRoute()
const playerStore = usePlayerStore()
const bookmarks = useBookmarks()

const show = ref(null)

const episodes = computed(() => {
  if (!show.value) return []
  return (show.value.episodes || []).map(ep => ({
    ...ep,
    // Ensure each episode has a proper ID for the player
    id: ep.id || ep.key || `${show.value.slug}-${ep.title}`,
    artist: show.value.title,
    cover_art: ep.cover_art || ep.artwork || show.value.artwork,
    audio_url: ep.audio_url || ep.url || '',
  }))
})

function formatDuration(seconds) {
  if (!seconds) return ''
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function truncate(str, len) {
  if (!str) return ''
  return str.length > len ? str.slice(0, len) + '...' : str
}

function playLatest() {
  if (episodes.value.length) {
    playerStore.setQueue(episodes.value, 0)
  }
}

function playEpisode(idx) {
  playerStore.setQueue(episodes.value, idx)
}

onMounted(async () => {
  const slug = route.params.slug
  const data = await apiFetchCached('/api/podcasts').catch(() => ({ shows: [] }))
  const shows = data.shows || []
  show.value = shows.find(s => s.slug === slug) || null
})
</script>
