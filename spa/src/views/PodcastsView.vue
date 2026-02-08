<template>
  <div>
    <div class="page-header">
      <h1>Podcasts</h1>
      <p>{{ podcasts.length }} shows</p>
    </div>

    <div class="content-grid" v-if="podcasts.length">
      <div class="card" v-for="show in podcasts" :key="show.slug">
        <img :src="show.artwork" :alt="show.title" class="card-image" loading="lazy" />
        <div class="card-body">
          <div class="card-title">{{ show.title }}</div>
          <div class="card-subtitle">{{ show.episodes?.length || 0 }} episodes</div>
        </div>
      </div>
    </div>

    <div class="content-grid" v-else>
      <div class="card" v-for="i in 4" :key="i">
        <div class="card-image skeleton"></div>
        <div class="card-body"><div class="skeleton" style="height:14px;width:80%"></div></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'

const podcasts = ref([])

onMounted(async () => {
  // The podcasts page is server-rendered on the Flask site;
  // we'll need a /api/podcasts endpoint. For now, try the shows endpoint.
  const data = await apiFetchCached('/api/podcasts').catch(() => ({ shows: [] }))
  podcasts.value = data.shows || []
})
</script>
