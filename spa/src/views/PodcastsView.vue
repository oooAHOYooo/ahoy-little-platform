<template>
  <div class="podcasts-page">
    <!-- Subpage hero (same as Flask subpage_hero) -->
    <section class="podcasts-hero">
      <div class="podcasts-hero-inner">
        <h1>
          <i class="fas fa-podcast" aria-hidden="true"></i>
          Podcasts
        </h1>
        <p>Fresh episodes and shows from independent creators.</p>
      </div>
    </section>

    <!-- Featured section: Shows + filter chips + show cards -->
    <section class="podcasts-section podcasts-featured-section">
      <div class="podcasts-section-header podcasts-featured-header">
        <div>
          <h2>Shows</h2>
          <p class="podcasts-section-subtitle">Pick a show to filter the latest episodes.</p>
        </div>
        <div class="podcast-filter-chips">
          <button
            type="button"
            class="podcast-filter-chip"
            :class="{ active: activeShowSlug === 'all' }"
            @click="activeShowSlug = 'all'"
          >
            All
          </button>
          <button
            v-for="show in featuredShows"
            :key="show.slug"
            type="button"
            class="podcast-filter-chip"
            :class="{ active: activeShowSlug === show.slug }"
            @click="activeShowSlug = show.slug"
          >
            {{ show.title }}
          </button>
        </div>
      </div>

      <!-- Mobile: dropdown show picker -->
      <div class="podcast-shows-dropdown-mobile">
        <select v-model="activeShowSlug" class="podcast-show-select">
          <option value="all">All Shows</option>
          <option v-for="show in featuredShows" :key="show.slug" :value="show.slug">
            {{ show.title }}
          </option>
        </select>
      </div>

      <!-- Desktop: show cards grid (Flask: podcast-shows podcast-shows-preview podcast-shows-desktop) -->
      <div class="podcast-shows podcast-shows-preview podcast-shows-desktop">
        <div
          v-for="show in featuredShows"
          :key="show.slug"
          class="podcast-show-preview-card"
          :class="{ active: activeShowSlug === show.slug }"
        >
          <button
            type="button"
            class="podcast-show-card podcast-show-card--filter"
            @click="activeShowSlug = show.slug"
          >
            <img
              :src="show.artwork || '/static/img/default-cover.jpg'"
              :alt="show.title"
              class="podcast-show-art"
              loading="lazy"
            />
            <div class="podcast-show-title">{{ show.title }}</div>
            <div class="podcast-show-desc" v-if="show.description">{{ show.description }}</div>
            <div class="podcast-show-updated" v-if="show.last_updated">
              Updated {{ show.last_updated }}
            </div>
          </button>
          <router-link :to="`/podcasts/${show.slug}`" class="podcast-show-open">
            Open show
            <i class="fas fa-arrow-right" aria-hidden="true"></i>
          </router-link>
        </div>
      </div>
    </section>

    <!-- New Episodes section (Flask: episode-list with episode-row) -->
    <section class="podcasts-section">
      <div class="podcasts-section-header">
        <h2>New Episodes</h2>
      </div>

      <div class="episode-list">
        <article
          v-for="ep in filteredEpisodes"
          :key="ep.key"
          class="episode-row"
          :class="{ playing: playerStore.currentTrack && (playerStore.currentTrack.id === ep.id || playerStore.currentTrack.key === ep.key) }"
          @click="openShow(ep.showSlug)"
        >
          <img
            class="episode-art"
            :src="ep.artwork || '/static/img/default-cover.jpg'"
            :alt="ep.title"
            loading="lazy"
          />
          <div class="episode-meta">
            <div class="episode-title">{{ ep.title }}</div>
            <div class="episode-subtitle">
              <span class="episode-show">{{ ep.showTitle }}</span>
              <span class="episode-dot">•</span>
              <span class="episode-time">{{ ep.duration }}</span>
              <span class="episode-dot" v-if="ep.date">•</span>
              <span class="episode-date" v-if="ep.date">{{ ep.date }}</span>
            </div>
            <div class="episode-desc" v-if="ep.description">{{ ep.description }}</div>
          </div>

          <div class="episode-actions">
            <button
              type="button"
              class="episode-btn"
              title="Play"
              @click.stop="playEpisode(ep)"
            >
              <i
                :class="playerStore.currentTrack && (playerStore.currentTrack.id === ep.id || playerStore.currentTrack.key === ep.key) && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"
                aria-hidden="true"
              ></i>
              <span class="sr-only">Play</span>
            </button>
            <button
              type="button"
              class="episode-btn queue-btn"
              :class="{ 'in-queue': playerStore.isInQueue(toTrack(ep)) }"
              title="Add to queue"
              @click.stop="addToQueue(ep)"
            >
              <i
                :class="playerStore.isInQueue(toTrack(ep)) ? 'fas fa-check' : 'fas fa-plus'"
                aria-hidden="true"
              ></i>
              <span class="sr-only">Add to queue</span>
            </button>
            <button
              type="button"
              class="episode-btn bm-btn"
              title="Bookmark"
              @click.stop="toggleBookmark(ep)"
            >
              <i class="fas fa-bookmark" aria-hidden="true"></i>
              <span class="sr-only">Bookmark</span>
            </button>
            <router-link
              :to="`/podcasts/${ep.showSlug}`"
              class="episode-open"
              title="Go to podcast"
              @click.stop
            >
              <i class="fas fa-podcast" aria-hidden="true"></i>
              <span class="sr-only">Go to podcast</span>
            </router-link>
          </div>
        </article>
      </div>
    </section>

    <!-- Loading -->
    <section v-if="loading" class="podcasts-section">
      <div class="podcast-shows podcast-shows-preview">
        <div v-for="i in 4" :key="i" class="podcast-show-preview-card">
          <div class="podcast-show-art skeleton" style="aspect-ratio:1;width:100%"></div>
          <div class="skeleton" style="height:14px;width:80%;margin-top:8px"></div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetchCached } from '../composables/useApi'
import { usePlayerStore } from '../stores/player'
import { useBookmarks } from '../composables/useBookmarks'

const router = useRouter()
const playerStore = usePlayerStore()
const bookmarks = useBookmarks()

const shows = ref([])
const loading = ref(true)
const activeShowSlug = ref('all')

const featuredShows = computed(() => (shows.value || []).slice(0, 4))

const episodes = computed(() => {
  const featured = new Set(featuredShows.value.map(s => s.slug))
  const list = []
  for (const s of shows.value || []) {
    if (!featured.has(s.slug)) continue
    for (const e of s.episodes || []) {
      list.push({
        key: `${s.slug}:${e.id}`,
        showSlug: s.slug,
        showTitle: s.title || s.slug,
        id: e.id,
        title: e.title || 'Untitled',
        description: e.description || '',
        date: e.date || '',
        duration: e.duration || formatDuration(e.duration_seconds),
        duration_seconds: e.duration_seconds || 0,
        artwork: e.artwork || e.cover_art || s.artwork || '/static/img/default-cover.jpg',
        audio_url: e.audio_url || e.url || '',
        type: 'podcast',
        artist: s.title || s.slug,
        cover_art: e.artwork || e.cover_art || s.artwork || '/static/img/default-cover.jpg',
      })
    }
  }
  list.sort((a, b) => String(b.date || '').localeCompare(String(a.date || '')))
  return list
})

const filteredEpisodes = computed(() => {
  if (activeShowSlug.value === 'all') return episodes.value
  return episodes.value.filter(ep => ep.showSlug === activeShowSlug.value)
})

function formatDuration(seconds) {
  if (!seconds) return ''
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function toTrack(ep) {
  return {
    id: ep.id,
    key: ep.key,
    title: ep.title,
    artist: ep.showTitle,
    cover_art: ep.artwork,
    audio_url: ep.audio_url,
    type: 'podcast',
  }
}

function playEpisode(ep) {
  const sorted = [...filteredEpisodes.value].sort((a, b) =>
    (a.title || '').localeCompare(b.title || '', undefined, { sensitivity: 'base' })
  )
  const tracks = sorted.map(e => toTrack(e))
  const idx = sorted.findIndex(e => e.key === ep.key)
  playerStore.setQueue(tracks, idx >= 0 ? idx : 0)
}

function addToQueue(ep) {
  playerStore.addToQueue(toTrack(ep))
}

function toggleBookmark(ep) {
  bookmarks.toggle({
    type: 'podcast-episode',
    id: ep.key,
    title: ep.title,
    artwork: ep.artwork,
    _type: 'podcast-episode',
  })
}

function openShow(slug) {
  router.push(`/podcasts/${slug}`)
}

onMounted(async () => {
  loading.value = true
  const data = await apiFetchCached('/api/podcasts').catch(() => ({ shows: [] }))
  shows.value = data.shows || []
  loading.value = false
})
</script>
