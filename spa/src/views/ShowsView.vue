<template>
  <div>
    <div class="page-header">
      <h1>Shows</h1>
      <p>{{ shows.length }} shows</p>
    </div>

    <div class="content-grid" v-if="shows.length">
      <div class="card" v-for="show in shows" :key="show.id">
        <img :src="show.thumbnail" :alt="show.title" class="card-image" loading="lazy" />
        <div class="card-body">
          <div class="card-title">{{ show.title }}</div>
          <div class="card-subtitle">{{ show.host }}</div>
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

const shows = ref([])

onMounted(async () => {
  const data = await apiFetchCached('/api/shows').catch(() => ({ shows: [] }))
  shows.value = data.shows || []
})
</script>
