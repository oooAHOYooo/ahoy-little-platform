<template>
  <div class="artists-page">
    <!-- Mobile: subpage hero (same as Flask macros/subpage_header) -->
    <section class="podcasts-hero mobile-only">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-users" aria-hidden="true"></i> Artists</h1>
        <p>Discover indie musicians, show hosts, athletes, filmmakers, and more.</p>
      </div>
    </section>

    <!-- Desktop: full unified subheader with search, filters, actions -->
    <section class="unified-header artists-subheader desktop-only">
      <div class="header-content">
        <div class="header-title">
          <div class="title-text">
            <h1>Artists</h1>
            <p>Discover indie musicians, show hosts, athletes, filmmakers, and more.</p>
          </div>
        </div>
        <div class="header-search">
          <div class="search-bar">
            <i class="fas fa-search" aria-hidden="true"></i>
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="Search artists, genres, or descriptions..."
              @input="applyFilters"
            />
            <button v-if="searchQuery" type="button" class="search-clear" aria-label="Clear search" @click="searchQuery = ''; applyFilters()">
              <i class="fas fa-times" aria-hidden="true"></i>
            </button>
          </div>
        </div>
        <div class="header-filters">
          <div class="filter-tabs">
            <button type="button" class="filter-tab" :class="{ active: selectedType === 'all' }" @click="setType('all')">
              <span>All Artists</span>
            </button>
            <button type="button" class="filter-tab" :class="{ active: selectedType === 'musician' }" @click="setType('musician')">
              <span>Musicians</span>
            </button>
            <button type="button" class="filter-tab" :class="{ active: selectedType === 'host' }" @click="setType('host')">
              <span>Hosts</span>
            </button>
            <button type="button" class="filter-tab" :class="{ active: selectedType === 'filmmaker' }" @click="setType('filmmaker')">
              <span>Filmmakers</span>
            </button>
            <button type="button" class="filter-tab" :class="{ active: selectedType === 'producer' }" @click="setType('producer')">
              <span>Producers</span>
            </button>
          </div>
          <div class="filter-tabs-mobile mobile-only">
            <button type="button" class="filter-tab-mobile" :class="{ active: selectedType === 'all' }" @click="setType('all')"><span>All</span></button>
            <button type="button" class="filter-tab-mobile" :class="{ active: selectedType === 'musician' }" @click="setType('musician')"><span>Musicians</span></button>
            <button type="button" class="filter-tab-mobile" :class="{ active: selectedType === 'host' }" @click="setType('host')"><span>Hosts</span></button>
            <button type="button" class="filter-tab-mobile" :class="{ active: selectedType === 'filmmaker' }" @click="setType('filmmaker')"><span>Filmmakers</span></button>
            <button type="button" class="filter-tab-mobile" :class="{ active: selectedType === 'producer' }" @click="setType('producer')"><span>Producers</span></button>
          </div>
        </div>
        <div class="header-actions">
          <div class="view-options">
            <button type="button" class="view-btn" :class="{ active: viewMode === 'grid' }" @click="viewMode = 'grid'">
              <i class="fas fa-th"></i>
            </button>
            <button type="button" class="view-btn" :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'">
              <i class="fas fa-list"></i>
            </button>
          </div>
          <button type="button" class="btn btn-primary btn-large" @click="goRandomArtist">
            <i class="fas fa-user"></i> Discover Random Artist
          </button>
        </div>
      </div>
    </section>

    <!-- Mobile: search + filter strip then episode list -->
    <section class="podcasts-section mobile-only">
      <div class="podcasts-section-header">
        <h2>All Artists</h2>
        <button type="button" class="episode-btn" title="Discover Random Artist" @click="goRandomArtist">
          <i class="fas fa-random" aria-hidden="true"></i>
          <span class="sr-only">Discover Random Artist</span>
        </button>
      </div>
      <div class="artists-mobile-controls">
        <div class="search-bar">
          <i class="fas fa-search" aria-hidden="true"></i>
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="Search artists..."
            @input="applyFilters"
          />
          <button v-if="searchQuery" type="button" class="search-clear" aria-label="Clear search" @click="searchQuery = ''; applyFilters()">
            <i class="fas fa-times" aria-hidden="true"></i>
          </button>
        </div>
        <div class="filter-tabs-mobile">
          <button type="button" class="filter-tab-mobile" :class="{ active: selectedType === 'all' }" @click="setType('all')"><span>All</span></button>
          <button type="button" class="filter-tab-mobile" :class="{ active: selectedType === 'musician' }" @click="setType('musician')"><span>Musicians</span></button>
          <button type="button" class="filter-tab-mobile" :class="{ active: selectedType === 'host' }" @click="setType('host')"><span>Hosts</span></button>
          <button type="button" class="filter-tab-mobile" :class="{ active: selectedType === 'filmmaker' }" @click="setType('filmmaker')"><span>Filmmakers</span></button>
          <button type="button" class="filter-tab-mobile" :class="{ active: selectedType === 'producer' }" @click="setType('producer')"><span>Producers</span></button>
        </div>
      </div>
      <div class="episode-list">
        <article
          v-for="artist in filteredArtists"
          :key="artist.id || artist.slug || artist.name"
          class="episode-row"
          @click="viewArtist(artist)"
        >
          <img
            class="episode-art"
            :src="artist.image || '/static/img/default-avatar.png'"
            :alt="artist.name"
            loading="lazy"
            decoding="async"
          />
          <div class="episode-meta">
            <div class="episode-title">{{ artist.name }}</div>
          </div>
          <div class="episode-actions">
            <button type="button" class="episode-btn" title="Open" @click.stop="viewArtist(artist)">
              <i class="fas fa-chevron-right" aria-hidden="true"></i>
              <span class="sr-only">Open</span>
            </button>
          </div>
        </article>
      </div>
    </section>

    <!-- Desktop: grid/list section -->
    <div class="artists-container desktop-only">
      <section class="artists-grid-section">
        <div class="section-header">
          <h2><i class="fas fa-th"></i> All Artists</h2>
          <div class="view-controls">
            <button type="button" class="view-btn" :class="{ active: viewMode === 'grid' }" @click="viewMode = 'grid'">
              <i class="fas fa-th"></i>
            </button>
            <button type="button" class="view-btn" :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'">
              <i class="fas fa-list"></i>
            </button>
          </div>
        </div>

        <!-- Grid view -->
        <div v-show="viewMode === 'grid'" class="artists-grid">
          <template v-if="filteredArtists.length">
            <router-link
              v-for="artist in filteredArtists"
              :key="artist.id || artist.slug"
              :to="`/artists/${artist.slug || artist.id}`"
              class="artist-card"
              style="text-decoration:none;color:inherit"
            >
              <div class="artist-cover">
                <img
                  :src="artist.image || '/static/img/default-avatar.png'"
                  :alt="artist.name"
                  class="artist-image image-placeholder"
                  loading="lazy"
                />
                <div v-if="artist.type" class="artist-type-badge ahoy-subheader">{{ (artist.type || '').toUpperCase() }}</div>
              </div>
              <div class="artist-info">
                <h4>{{ artist.name }}</h4>
              </div>
            </router-link>
          </template>
          <template v-else>
            <div v-for="i in 6" :key="i" class="artist-card">
              <div class="artist-cover skeleton"></div>
              <div class="artist-info"><div class="skeleton" style="height:14px;width:80%"></div></div>
            </div>
          </template>
        </div>

        <!-- List view -->
        <div v-show="viewMode === 'list'" class="artists-list">
          <div class="list-header">
            <span class="col-avatar">Avatar</span>
            <span class="col-name">Name</span>
            <span class="col-type">Type</span>
            <span class="col-genre">Genre</span>
          </div>
          <div class="list-items">
            <div
              v-for="artist in filteredArtists"
              :key="artist.id || artist.slug"
              class="list-item"
              @click="viewArtist(artist)"
            >
              <div class="col-avatar">
                <img
                  :src="artist.image || '/static/img/default-avatar.png'"
                  :alt="artist.name"
                  class="artist-thumbnail image-placeholder"
                  loading="lazy"
                />
                <div v-if="artist.type" class="artist-type-badge ahoy-subheader">{{ (artist.type || '').toUpperCase() }}</div>
              </div>
              <div class="col-name"><h4>{{ artist.name }}</h4></div>
              <span class="col-type">{{ artist.type || '—' }}</span>
              <span class="col-genre">{{ (artist.genres || []).join(', ') || 'Various' }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Loading -->
    <section v-if="loading" class="loading-section">
      <div class="spinner"></div>
      <p>Loading artists...</p>
    </section>

    <!-- Empty state -->
    <section v-if="!loading && filteredArtists.length === 0" class="empty-section">
      <div class="empty-content">
        <i class="fas fa-users"></i>
        <h3>No artists found</h3>
        <p>Try adjusting your search or filters</p>
        <button type="button" class="btn btn-primary" @click="clearFilters">Clear Filters</button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetchCached } from '../composables/useApi'

const router = useRouter()
const artists = ref([])
const loading = ref(true)
const searchQuery = ref('')
const selectedType = ref('all')
const viewMode = ref('grid')

const filteredArtists = computed(() => {
  let list = [...artists.value]
  const q = (searchQuery.value || '').toLowerCase()
  if (q) {
    list = list.filter(
      (a) =>
        (a.name || '').toLowerCase().includes(q) ||
        (a.description || '').toLowerCase().includes(q) ||
        (Array.isArray(a.genres) && a.genres.some((g) => String(g).toLowerCase().includes(q)))
    )
  }
  if (selectedType.value !== 'all') {
    list = list.filter((a) => (a.type || '').toLowerCase() === selectedType.value)
  }
  return list
})

function applyFilters() {
  /* reactive via computed */
}

function setType(type) {
  selectedType.value = type
}

function clearFilters() {
  searchQuery.value = ''
  selectedType.value = 'all'
}

function viewArtist(artist) {
  const slug = artist.slug || artist.id || (artist.name || '').toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
  router.push(`/artists/${slug}`)
}

function goRandomArtist() {
  if (artists.value.length === 0) return
  const pick = artists.value[Math.floor(Math.random() * artists.value.length)]
  viewArtist(pick)
}

onMounted(async () => {
  loading.value = true
  const data = await apiFetchCached('/api/artists').catch(() => ({ artists: [] }))
  artists.value = data.artists || []
  loading.value = false
})
</script>
