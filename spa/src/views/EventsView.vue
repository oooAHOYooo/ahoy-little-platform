<template>
  <div class="events-page">
    <div class="unified-header events-subheader">
      <div class="header-content">
        <h1>Events</h1>
      </div>
    </div>

    <div class="podcasts-section" v-if="events.length">
      <h2 class="section-title">Upcoming Events</h2>
      <div class="episode-list">
        <div class="episode-row" v-for="event in events" :key="event.id">
          <div class="episode-art">
            <img :src="event.image || '/static/img/default-cover.jpg'" :alt="event.title" loading="lazy" />
          </div>
          <div class="episode-meta">
            <div class="episode-title">{{ event.title }}</div>
            <div class="episode-show">{{ event.date }} &middot; {{ event.venue }}</div>
            <div class="episode-desc" v-if="event.description">{{ event.description }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading skeletons -->
    <div class="podcasts-section" v-else>
      <div class="episode-list">
        <div class="episode-row" v-for="i in 4" :key="i">
          <div class="episode-art skeleton" style="width:80px;height:80px"></div>
          <div class="episode-meta">
            <div class="skeleton" style="height:14px;width:60%;margin-bottom:6px"></div>
            <div class="skeleton" style="height:12px;width:40%"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'

const events = ref([])

onMounted(async () => {
  const data = await apiFetchCached('/api/events').catch(() => ({ events: [] }))
  events.value = data.events || []
})
</script>
