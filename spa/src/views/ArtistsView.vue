<template>
  <div class="artists-page">
    <div class="unified-header artists-subheader">
      <div class="header-content">
        <h1>Artists</h1>
        <span class="header-count">{{ artists.length }} artists</span>
      </div>
    </div>

    <div class="artists-container">
      <div class="artists-grid-section">
        <div class="artists-grid" v-if="artists.length">
          <div class="artist-card" v-for="artist in artists" :key="artist.id">
            <div class="artist-cover">
              <img :src="artist.image" :alt="artist.name" loading="lazy" />
            </div>
            <div class="artist-type-badge" v-if="artist.type">{{ artist.type }}</div>
            <div class="artist-info">
              <div class="artist-name">{{ artist.name }}</div>
            </div>
          </div>
        </div>

        <!-- Loading skeletons -->
        <div class="artists-grid" v-else>
          <div class="artist-card" v-for="i in 6" :key="i">
            <div class="artist-cover skeleton"></div>
            <div class="artist-info"><div class="skeleton" style="height:14px;width:80%"></div></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'

const artists = ref([])

onMounted(async () => {
  const data = await apiFetchCached('/api/artists').catch(() => ({ artists: [] }))
  artists.value = data.artists || []
})
</script>
