<template>
  <div>
    <div class="page-header">
      <h1>Artists</h1>
      <p>{{ artists.length }} artists</p>
    </div>

    <div class="content-grid" v-if="artists.length">
      <div class="card" v-for="artist in artists" :key="artist.id">
        <img :src="artist.image" :alt="artist.name" class="card-image" loading="lazy" />
        <div class="card-body">
          <div class="card-title">{{ artist.name }}</div>
          <div class="card-subtitle">{{ artist.type }}</div>
        </div>
      </div>
    </div>

    <div class="content-grid" v-else>
      <div class="card" v-for="i in 6" :key="i">
        <div class="card-image skeleton"></div>
        <div class="card-body"><div class="skeleton" style="height:14px;width:80%"></div></div>
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
