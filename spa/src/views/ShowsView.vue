<template>
  <div class="shows-page">
    <div class="unified-header shows-subheader">
      <div class="header-content">
        <h1>Videos</h1>
        <span class="header-count">{{ shows.length }} shows</span>
      </div>
    </div>

    <div class="shows-container">
      <div class="shows-grid-section">
        <div class="shows-grid" v-if="shows.length">
          <router-link
            v-for="show in shows"
            :key="show.id"
            :to="`/shows/${show.id}`"
            class="show-card"
            style="text-decoration:none;color:inherit"
          >
            <div class="show-thumbnail">
              <img :src="show.thumbnail" :alt="show.title" loading="lazy" />
              <div class="show-overlay">
                <button class="play-btn"><i class="fas fa-play"></i></button>
              </div>
            </div>
            <div class="show-info">
              <div class="show-title">{{ show.title }}</div>
              <div class="show-host">{{ show.host }}</div>
            </div>
          </router-link>
        </div>

        <!-- Loading skeletons -->
        <div class="shows-grid" v-else>
          <div class="show-card" v-for="i in 6" :key="i">
            <div class="show-thumbnail skeleton"></div>
            <div class="show-info"><div class="skeleton" style="height:14px;width:80%"></div></div>
          </div>
        </div>
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
