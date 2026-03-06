<template>
  <div class="podcasts-page">
    <!-- Sub-menu filter (design parity with Music Library) -->
    <section class="podcasts-section">
      <SubMenuFilter
        v-model="activeShowSlug"
        :filters="showFilters"
        all-value="all"
        filter-all-label="All Shows"
        :show-search="true"
        search-placeholder="Search shows or episodes…"
        :search-query="searchQuery"
        @update:searchQuery="searchQuery = $event"
        action-label="Random Episode"
        action-icon="fas fa-random"
        @action="goRandomEpisode"
      />
    </section>

    <!-- Featured section: Shows + show cards (Desktop Only) -->
    <section class="podcasts-section podcasts-featured-section desktop-only">
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

      <div class="episode-list desktop-only">
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

      <!-- Mobile: list view (parity with Music Library) -->
      <div class="podcast-mobile-list mobile-only">
        <div
          v-for="ep in filteredEpisodes"
          :key="'mobile-' + ep.key"
          class="podcast-mobile-row"
          :class="{ playing: playerStore.currentTrack && (playerStore.currentTrack.id === ep.id || playerStore.currentTrack.key === ep.key) }"
          @click="playEpisode(ep)"
        >
          <div class="podcast-mobile-art">
            <img
              class="podcast-mobile-art-img"
              :src="ep.artwork || '/static/img/default-cover.jpg'"
              :alt="ep.title"
              loading="lazy"
              @error="($event.target).src = '/static/img/default-cover.jpg'"
            />
            <button
              type="button"
              class="podcast-mobile-art-play"
              :aria-label="playerStore.currentTrack && (playerStore.currentTrack.id === ep.id || playerStore.currentTrack.key === ep.key) && playerStore.isPlaying ? 'Pause' : 'Play'"
              @click.stop="playEpisode(ep)"
            >
              <i :class="playerStore.currentTrack && (playerStore.currentTrack.id === ep.id || playerStore.currentTrack.key === ep.key) && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'" aria-hidden="true"></i>
            </button>
          </div>

          <div class="podcast-mobile-meta">
            <span class="podcast-mobile-title">{{ ep.title }}</span>
            <span class="podcast-mobile-artist">{{ ep.showTitle }}</span>
          </div>

          <div class="podcast-mobile-right">
            <div class="podcast-mobile-duration">{{ ep.duration }}</div>
            <div class="podcast-mobile-actions">
              <button
                type="button"
                class="episode-btn podcast-mobile-btn podcast-mobile-play-btn"
                :title="playerStore.currentTrack && (playerStore.currentTrack.id === ep.id || playerStore.currentTrack.key === ep.key) && playerStore.isPlaying ? 'Pause' : 'Play'"
                @click.stop="playEpisode(ep)"
              >
                <i :class="playerStore.currentTrack && (playerStore.currentTrack.id === ep.id || playerStore.currentTrack.key === ep.key) && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'" aria-hidden="true"></i>
              </button>
              <button
                type="button"
                class="episode-btn queue-btn podcast-mobile-btn"
                title="Add to queue"
                @click.stop="addToQueue(ep)"
              >
                <i class="fas fa-plus" aria-hidden="true"></i>
              </button>
              <button
                type="button"
                class="episode-btn bm-btn podcast-mobile-btn"
                title="Save"
                @click.stop="toggleBookmark(ep)"
              >
                <i class="fas fa-bookmark" aria-hidden="true"></i>
              </button>
            </div>
          </div>
        </div>
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
import SubMenuFilter from '../components/SubMenuFilter.vue'

const router = useRouter()
const playerStore = usePlayerStore()
const bookmarks = useBookmarks()

const shows = ref([])
const loading = ref(true)
const searchQuery = ref('')
const activeShowSlug = ref('all')

const featuredShows = computed(() => {
  let list = shows.value || []
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(s => 
      s.title.toLowerCase().includes(q) || 
      (s.description && s.description.toLowerCase().includes(q))
    )
  }
  return list.slice(0, 4)
})

const showFilters = computed(() => {
  return (shows.value || []).map(s => ({
    value: s.slug,
    label: s.title,
    image: s.artwork || null
  }))
})

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
  let list = episodes.value
  if (activeShowSlug.value !== 'all') {
    list = list.filter(ep => ep.showSlug === activeShowSlug.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(ep => 
      ep.title.toLowerCase().includes(q) || 
      ep.description.toLowerCase().includes(q) ||
      ep.showTitle.toLowerCase().includes(q)
    )
  }
  return list
})

function goRandomEpisode() {
  if (episodes.value.length === 0) return
  const pick = episodes.value[Math.floor(Math.random() * episodes.value.length)]
  playEpisode(pick)
}

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

<style scoped>
.podcasts-page {
  padding: 0;
}

.podcasts-section {
  padding: 0 16px;
  margin-bottom: 32px;
}

.podcasts-section-header {
  margin-bottom: 20px;
}

.podcasts-section-subtitle {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
  margin-top: 4px;
}

/* Featured Shows Grid */
.podcast-shows {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.podcast-show-preview-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  cursor: pointer;
  transition: all 0.2s;
}

.podcast-show-preview-card:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-2px);
}

.podcast-show-preview-card.active {
  border-color: var(--accent-color, #00d4ff);
  background: rgba(0, 212, 255, 0.05);
}

.podcast-show-card-art {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 8px;
  object-fit: cover;
  margin-bottom: 12px;
}

.podcast-show-card-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.podcast-show-card-meta {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
}

/* Episode List (Desktop) */
.episode-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.episode-row {
  display: grid;
  grid-template-columns: 80px 1fr auto;
  gap: 20px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
}

.episode-row:hover {
  background: rgba(255, 255, 255, 0.06);
}

.episode-row.playing {
  border-color: var(--accent-color, #00d4ff);
  background: rgba(0, 212, 255, 0.05);
}

.episode-art {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
}

.episode-title {
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 6px;
}

.episode-subtitle {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.episode-desc {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.episode-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.episode-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.episode-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.episode-open {
  color: rgba(255, 255, 255, 0.5);
  font-size: 1.2rem;
  margin-left: 10px;
}

.episode-open:hover {
  color: #fff;
}

/* Mobile Styles Parity with Music Library */
.podcast-mobile-list {
  display: none;
}

@media (max-width: 768px) {
  .podcasts-page {
    padding: 0 !important;
  }

  /* Force content area to be flush */
  :deep(.content-area) {
    padding-left: 0 !important;
    padding-right: 0 !important;
    margin: 0 !important;
  }

  .podcasts-section {
    padding: 0 !important;
    margin-bottom: 0;
  }

  .podcasts-featured-section {
    display: none; /* Hide featured shows grid on mobile to match music flow */
  }

  .podcast-mobile-list {
    display: flex;
    flex-direction: column;
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
  }

  .podcast-mobile-row {
    display: grid;
    grid-template-columns: 48px minmax(0, 1fr) auto;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    width: 100%;
  }

  .podcast-mobile-row.playing {
    background: rgba(0, 212, 255, 0.1) !important;
  }

  .podcast-mobile-art {
    position: relative;
    width: 44px;
    height: 44px;
    border-radius: 4px;
    overflow: hidden;
  }

  .podcast-mobile-art-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .podcast-mobile-art-play {
    position: absolute;
    inset: 0;
    border: none;
    background: rgba(0, 0, 0, 0.4);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
  }

  .podcast-mobile-meta {
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0 !important;
  }

  .podcast-mobile-title {
    display: block;
    font-size: 15px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.95);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.1;
  }

  .podcast-mobile-artist {
    display: block;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.5);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.1;
    margin-top: 1px;
  }

  .podcast-mobile-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .podcast-mobile-duration {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.45);
    font-variant-numeric: tabular-nums;
  }

  .podcast-mobile-actions {
    display: flex;
    gap: 4px;
  }

  .podcast-mobile-btn {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    font-size: 12px;
    padding: 0;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .podcast-mobile-play-btn {
    background: linear-gradient(180deg, rgba(0, 212, 255, 0.15), rgba(0, 212, 255, 0.08));
    border-color: rgba(0, 212, 255, 0.15);
  }
}
</style>
