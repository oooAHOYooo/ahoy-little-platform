<template>
  <div>
    <div class="page-header">
      <h1>Events</h1>
    </div>

    <div class="content-grid" v-if="events.length">
      <div class="card" v-for="event in events" :key="event.id">
        <img :src="event.image || '/static/img/default-cover.jpg'" :alt="event.title" class="card-image" loading="lazy" />
        <div class="card-body">
          <div class="card-title">{{ event.title }}</div>
          <div class="card-subtitle">{{ event.date }} &middot; {{ event.venue }}</div>
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

const events = ref([])

onMounted(async () => {
  const data = await apiFetchCached('/api/events').catch(() => ({ events: [] }))
  events.value = data.events || []
})
</script>
