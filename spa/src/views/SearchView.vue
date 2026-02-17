<template>
  <div class="search-page">
    <div class="unified-header search-header">
      <div class="header-content">
        <div class="search-input-wrap">
          <i class="fas fa-search"></i>
          <input
            v-model="query"
            type="search"
            placeholder="Search music, artists, shows, podcasts..."
            class="search-input"
            autofocus
            autocomplete="off"
          />
          <button v-if="query" type="button" class="search-clear" aria-label="Clear" @click="query = ''">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="search-loading">
      <i class="fas fa-spinner fa-spin"></i>
      <span>Loading catalog...</span>
    </div>

    <div v-else class="search-results">
      <template v-if="!query.trim()">
        <p class="search-hint">Type to search across music, artists, videos, and podcasts.</p>
      </template>
      <template v-else>
        <section v-if="results.tracks.length" class="search-section">
          <h2 class="search-section-title">Tracks</h2>
          <div class="search-list">
            <router-link
              v-for="t in results.tracks"
              :key="t.id"
              :to="`/music/${t.id}`"
              class="search-item"
              @click="query = ''"
            >
              <img
                :src="t.cover_art || t.thumbnail || '/static/img/default-cover.jpg'"
                :alt="t.title"
                class="search-item-art"
              />
              <div class="search-item-info">
                <span class="search-item-title">{{ t.title }}</span>
                <span class="search-item-meta">{{ t.artist }}</span>
              </div>
            </router-link>
          </div>
        </section>
        <section v-if="results.artists.length" class="search-section">
          <h2 class="search-section-title">Artists</h2>
          <div class="search-list">
            <router-link
              v-for="a in results.artists"
              :key="a.id"
              :to="`/artists/${a.slug || a.id}`"
              class="search-item"
              @click="query = ''"
            >
              <img
                :src="a.image || a.cover_art || '/static/img/default-cover.jpg'"
                :alt="a.name"
                class="search-item-art"
              />
              <div class="search-item-info">
                <span class="search-item-title">{{ a.name }}</span>
              </div>
            </router-link>
          </div>
        </section>
        <section v-if="results.shows.length" class="search-section">
          <h2 class="search-section-title">Videos</h2>
          <div class="search-list">
            <router-link
              v-for="s in results.shows"
              :key="s.id"
              :to="`/videos/${s.id}`"
              class="search-item"
              @click="query = ''"
            >
              <img
                :src="s.thumbnail || s.cover_art || '/static/img/default-cover.jpg'"
                :alt="s.title"
                class="search-item-art"
              />
              <div class="search-item-info">
                <span class="search-item-title">{{ s.title }}</span>
                <span class="search-item-meta">{{ s.host }}</span>
              </div>
            </router-link>
          </div>
        </section>
        <section v-if="results.podcasts.length" class="search-section">
          <h2 class="search-section-title">Podcasts</h2>
          <div class="search-list">
            <router-link
              v-for="p in results.podcasts"
              :key="p.slug"
              :to="`/podcasts/${p.slug}`"
              class="search-item"
              @click="query = ''"
            >
              <img
                :src="p.artwork || p.image || '/static/img/default-cover.jpg'"
                :alt="p.title"
                class="search-item-art"
              />
              <div class="search-item-info">
                <span class="search-item-title">{{ p.title }}</span>
              </div>
            </router-link>
          </div>
        </section>
        <p v-if="query.trim() && !hasAny" class="search-no-results">No results for "{{ query }}"</p>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { apiFetchCached } from '../composables/useApi'
import { useSearch } from '../composables/useSearch'

const query = ref('')
const catalog = ref({ tracks: [], artists: [], shows: [] })
const loading = ref(true)
const { runSearch } = useSearch()

async function loadCatalog() {
  loading.value = true
  try {
    const [music, artists, shows, podcasts] = await Promise.all([
      apiFetchCached('/api/music').catch(() => ({ tracks: [] })),
      apiFetchCached('/api/artists').catch(() => ({ artists: [] })),
      apiFetchCached('/api/shows').catch(() => ({ shows: [] })),
      apiFetchCached('/api/podcasts').catch(() => ({ shows: [] })),
    ])
    catalog.value = {
      tracks: music.tracks || [],
      artists: artists.artists || [],
      shows: shows.shows || [],
      podcasts: podcasts.shows || [],
    }
  } finally {
    loading.value = false
  }
}

const results = computed(() => {
  const { tracks, artists, shows, podcasts } = catalog.value
  return runSearch(tracks, artists, shows, podcasts, query.value)
})

const hasAny = computed(
  () =>
    results.value.tracks.length +
    results.value.artists.length +
    results.value.shows.length +
    results.value.podcasts.length >
    0
)

watch(
  query,
  () => {},
  { immediate: true }
)

loadCatalog()
</script>

<style scoped>
.search-page {
  padding-bottom: 100px;
}
.search-header {
  padding: 12px 16px;
}
.search-input-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 10px 14px;
}
.search-input-wrap i.fa-search {
  color: var(--text-secondary);
  font-size: 16px;
}
.search-input {
  flex: 1;
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 16px;
  outline: none;
}
.search-input::placeholder {
  color: var(--text-secondary);
}
.search-clear {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
}
.search-loading {
  padding: 40px;
  text-align: center;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}
.search-hint {
  padding: 24px 16px;
  color: var(--text-secondary);
  text-align: center;
}
.search-results {
  padding: 0 16px 24px;
}
.search-section {
  margin-bottom: 24px;
}
.search-section-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  margin: 0 0 12px;
}
.search-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.search-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  text-decoration: none;
  color: inherit;
  transition: background 0.2s;
}
.search-item:hover {
  background: rgba(255,255,255,0.06);
}
.search-item-art {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  object-fit: cover;
}
.search-item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.search-item-title {
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.search-item-meta {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.search-no-results {
  padding: 24px;
  text-align: center;
  color: var(--text-secondary);
}
</style>
