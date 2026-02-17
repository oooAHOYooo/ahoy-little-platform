<template>
  <div class="my-saves-container saved-page" :class="{ 'saved-page--recent': isRecentPage }">
    <!-- Guest banner: prompt to create account to sync -->
    <div v-if="!auth.isLoggedIn.value" class="saves-guest-banner">
      <p>Bookmarks and recently played are stored on this device. <router-link to="/login?signup=1">Create an account</router-link> to sync across devices.</p>
    </div>

    <!-- Hero: full on /my-saves, compact on /recently-played -->
    <div v-if="isRecentPage" class="saves-profile-hero saves-hero--recent">
      <div class="saves-profile-glow"></div>
      <div class="saves-profile-content saves-hero-content--recent">
        <div class="saves-avatar-wrapper">
          <div class="saves-avatar-guest saves-avatar--history">
            <i class="fas fa-history"></i>
          </div>
        </div>
        <div class="saves-profile-info">
          <h1 class="saves-username">Recently Played</h1>
          <div class="saves-stats">
            <div class="saves-stat">
              <span class="saves-stat-number">{{ recentlyPlayed.length }}</span>
              <span class="saves-stat-label">tracks & shows</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="saves-profile-hero">
      <div class="saves-profile-glow"></div>
      <div class="saves-profile-content">
        <div class="saves-avatar-wrapper">
          <div class="saves-avatar-guest">
            <i class="fas fa-bookmark"></i>
          </div>
        </div>
        <div class="saves-profile-info">
          <h1 class="saves-username">{{ heroTitle }}</h1>
          <div class="saves-stats">
            <div class="saves-stat">
              <span class="saves-stat-number">{{ savedItems.length }}</span>
              <span class="saves-stat-label">Bookmarks</span>
            </div>
            <router-link to="/recently-played" class="saves-stat saves-stat-link">
              <span class="saves-stat-number">{{ recentlyPlayed.length }}</span>
              <span class="saves-stat-label">Recently Played</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs: Bookmarks (→ /my-saves) | Recently Played (→ /recently-played) -->
    <div class="saves-tabs-glass">
      <router-link
        :to="{ path: '/my-saves' }"
        class="saves-tab-btn"
        :class="{ active: !isRecentPage }"
      >
        <i class="fas fa-bookmark"></i>
        <span>Bookmarks</span>
        <span class="saves-tab-count">{{ savedItems.length }}</span>
      </router-link>
      <router-link
        :to="{ path: '/recently-played' }"
        class="saves-tab-btn"
        :class="{ active: isRecentPage }"
      >
        <i class="fas fa-history"></i>
        <span>Recently Played</span>
        <span class="saves-tab-count">{{ recentlyPlayed.length }}</span>
      </router-link>
    </div>

    <!-- Bookmarks tab (visible on /my-saves) -->
    <div v-show="!isRecentPage" class="saves-content-glass">
      <div v-if="savedItems.length" class="saves-bookmarks-tab">
        <div class="saves-filter-pills">
          <button
            type="button"
            :class="{ active: savedFilter === 'all' }"
            class="saves-pill"
            @click="savedFilter = 'all'"
          >
            All
          </button>
          <button
            v-for="t in filterTypes"
            :key="t"
            type="button"
            :class="{ active: savedFilter === t }"
            class="saves-pill"
            @click="savedFilter = t"
          >
            {{ t === 'track' ? 'Tracks' : t === 'show' ? 'Shows' : t === 'artist' ? 'Artists' : t }}
          </button>
        </div>
        <div class="saves-grid">
          <div
            v-for="item in filteredSaved"
            :key="itemKey(item)"
            class="saves-card"
            @click="playContent(item)"
          >
            <div class="saves-card-art">
              <img
                :src="item.cover_art || item.thumbnail || item.artwork || '/static/img/default-cover.jpg'"
                :alt="item.title || item.name"
                loading="lazy"
              />
              <div class="saves-card-overlay">
                <button type="button" class="saves-play-btn" @click.stop="playContent(item)">
                  <i class="fas fa-play"></i>
                </button>
              </div>
              <button
                type="button"
                class="saves-remove-btn"
                title="Remove bookmark"
                @click.stop="unsaveContent(item)"
              >
                <i class="fas fa-bookmark"></i>
              </button>
              <span class="saves-type-badge">{{ item.type || 'track' }}</span>
            </div>
            <div class="saves-card-info">
              <h3>{{ item.title || item.name || '—' }}</h3>
              <p>{{ item.artist || item.host || '' }}</p>
              <span v-if="item.added_at" class="saves-date">{{ formatDate(item.added_at) }}</span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="saves-empty-glass">
        <div class="saves-empty-icon">
          <i class="fas fa-bookmark"></i>
        </div>
        <h3>No bookmarks yet</h3>
        <p>Tap the bookmark icon on any track, show, or artist to save it here for easy access.</p>
        <router-link to="/videos" class="saves-cta-btn">Discover Videos</router-link>
      </div>
    </div>

    <!-- Recently Played (visible on /recently-played) -->
    <div v-show="isRecentPage" class="saves-content-glass saves-content--recent">
      <div v-if="recentlyPlayed.length" class="saves-recent-list">
        <div
          v-for="item in recentlyPlayed"
          :key="recentKey(item)"
          class="saves-recent-item"
          @click="playContent(item)"
        >
          <div class="saves-recent-art">
            <img
              :src="item.artwork || item.cover_art || item.thumbnail || '/static/img/default-cover.jpg'"
              :alt="item.title || item.name"
              loading="lazy"
            />
            <div class="saves-recent-play">
              <i class="fas fa-play"></i>
            </div>
          </div>
          <div class="saves-recent-info">
            <h3>{{ item.title || item.name || '—' }}</h3>
            <p>{{ item.artist || item.host || '' }}</p>
            <span class="saves-recent-meta">
              <span class="saves-recent-type">{{ recentTypeLabel(item.type) }}</span>
              <span class="saves-recent-time">{{ formatRelativeTime(item.played_at) }}</span>
            </span>
          </div>
          <div class="saves-recent-actions">
            <button
              type="button"
              class="saves-action-btn"
              :class="{ bookmarked: bookmarkHelper.isBookmarked(item) }"
              :title="bookmarkHelper.isBookmarked(item) ? 'Remove bookmark' : 'Add bookmark'"
              @click.stop="toggleBookmark(item)"
            >
              <i class="fas fa-bookmark"></i>
            </button>
          </div>
        </div>
      </div>
      <div v-else class="saves-empty-glass">
        <div class="saves-empty-icon">
          <i class="fas fa-history"></i>
        </div>
        <h3>No recent plays</h3>
        <p>Content you listen to will appear here so you can easily find it again.</p>
        <router-link to="/music" class="saves-cta-btn">Browse Music</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBookmarks } from '../composables/useBookmarks'
import { usePlayerStore } from '../stores/player'
import { useAuth } from '../composables/useAuth'

const RECENT_STORAGE_KEY = 'ahoy.recentlyPlayed.v1'
const MAX_RECENT_ITEMS = 50

const router = useRouter()
const route = useRoute()
const bookmarkHelper = useBookmarks()
const playerStore = usePlayerStore()
const auth = useAuth()

const savedFilter = ref('all')
const recentlyPlayed = ref([])

const isRecentPage = computed(() => route.path === '/recently-played')

const savedItems = computed(() => Object.values(bookmarkHelper.bookmarks.value))

const heroTitle = computed(() => {
  const n = savedItems.value.length
  if (n >= 3) return 'My Collection'
  return auth.user.value?.display_name || auth.user.value?.email?.split('@')[0] || 'Saved'
})

const filterTypes = computed(() => {
  const types = new Set(savedItems.value.map((i) => i.type || 'track').filter(Boolean))
  return [...types]
})

const filteredSaved = computed(() => {
  if (savedFilter.value === 'all') return savedItems.value
  return savedItems.value.filter((i) => (i.type || 'track') === savedFilter.value)
})

function itemKey(item) {
  return item.id ?? item.slug ?? `${item.type}:${item.title}`
}

function recentKey(item) {
  return item.key ?? `${item.type || 'track'}:${item.id}:${item.played_at || 0}`
}

function formatDate(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

function recentTypeLabel(type) {
  const t = type || 'track'
  if (t === 'live_tv') return 'Live TV'
  if (t === 'show') return 'Video'
  if (t === 'podcast' || t === 'episode') return 'Podcast'
  return 'Music'
}

function formatRelativeTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

function loadRecentlyPlayed() {
  try {
    const raw = localStorage.getItem(RECENT_STORAGE_KEY)
    recentlyPlayed.value = raw ? JSON.parse(raw) : []
  } catch {
    recentlyPlayed.value = []
  }
}

function playContent(item) {
  const type = item.type || 'track'
  if (type === 'show') {
    router.push({ path: '/videos', query: { play: item.id } })
    return
  }
  if (type === 'live_tv') {
    router.push('/live-tv')
    return
  }
  if (playerStore.currentTrack?.id === item.id && playerStore.isPlaying) {
    playerStore.pause()
  } else {
    playerStore.play(item)
  }
}

function unsaveContent(item) {
  bookmarkHelper.remove(item)
  window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Removed from bookmarks', type: 'success' } }))
}

function toggleBookmark(item) {
  bookmarkHelper.toggle(item)
  loadRecentlyPlayed()
}

onMounted(() => {
  loadRecentlyPlayed()
  window.addEventListener('recentlyPlayed:updated', loadRecentlyPlayed)
})
onUnmounted(() => {
  window.removeEventListener('recentlyPlayed:updated', loadRecentlyPlayed)
})
</script>

<style scoped>
.saved-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.25rem 1.25rem 3rem;
}
.saved-page--recent .saves-content--recent {
  min-height: 200px;
}
@media (max-width: 768px) {
  .saved-page {
    padding: 0;
  }
}
.saves-tabs-glass :deep(a.saves-tab-btn) {
  text-decoration: none;
  color: inherit;
}
.saves-hero--recent .saves-hero-content--recent {
  gap: var(--spacing-lg);
}
.saves-avatar--history {
  background: linear-gradient(135deg, rgba(123, 237, 159, 0.3) 0%, rgba(107, 203, 255, 0.25) 100%);
  color: rgba(255, 255, 255, 0.9);
}
@media (max-width: 768px) {
  .saves-hero--recent .saves-profile-content {
    padding: 10px 8px;
  }
}
.saves-guest-banner {
  background: rgba(123, 237, 159, 0.08);
  border: 1px solid rgba(123, 237, 159, 0.2);
  border-radius: 12px;
  padding: 12px 16px;
  margin: 15px;
}
.saves-guest-banner p {
  margin: 0;
  font-size: 14px;
  color: var(--text-primary);
}
.saves-guest-banner a {
  color: var(--saves-accent, #7bed9f);
  font-weight: 600;
  text-decoration: none;
}
.saves-guest-banner a:hover {
  text-decoration: underline;
}
.saves-recent-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-muted, rgba(255, 255, 255, 0.6));
}
.saves-recent-type {
  text-transform: capitalize;
}
.saves-recent-type::after {
  content: '·';
  margin-left: 0.5rem;
  margin-right: 0.25rem;
}
</style>
