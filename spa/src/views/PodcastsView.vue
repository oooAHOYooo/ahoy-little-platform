<template>
  <div class="podcasts-page">
    <div class="unified-header podcasts-subheader">
      <div class="header-content">
        <h1>Podcasts</h1>
        <span class="header-count">{{ podcasts.length }} shows</span>
      </div>
    </div>

    <!-- Show cards -->
    <div class="podcasts-section podcasts-featured-section" v-if="podcasts.length">
      <div class="podcast-shows podcast-shows-preview">
        <router-link
          v-for="show in podcasts"
          :key="show.slug"
          :to="`/podcasts/${show.slug}`"
          class="podcast-show-preview-card"
          style="text-decoration:none;color:inherit"
        >
          <img :src="show.artwork" :alt="show.title" class="podcast-show-art" loading="lazy" />
          <div class="podcast-show-name">{{ show.title }}</div>
          <div class="podcast-show-count">{{ show.episodes?.length || 0 }} episodes</div>
        </router-link>
      </div>
    </div>

    <!-- Loading skeletons -->
    <div class="podcasts-section" v-else>
      <div class="podcast-shows podcast-shows-preview">
        <div class="podcast-show-preview-card" v-for="i in 4" :key="i">
          <div class="podcast-show-art skeleton" style="aspect-ratio:1;width:100%"></div>
          <div class="skeleton" style="height:14px;width:80%;margin-top:8px"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'

const podcasts = ref([])

onMounted(async () => {
  const data = await apiFetchCached('/api/podcasts').catch(() => ({ shows: [] }))
  podcasts.value = data.shows || []
})
</script>
