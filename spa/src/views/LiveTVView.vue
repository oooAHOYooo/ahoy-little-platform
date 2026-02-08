<template>
  <div class="home-page">
    <div class="unified-header">
      <div class="header-content">
        <h1>Live TV</h1>
      </div>
    </div>

    <div class="live-dashboard">
      <div class="dashboard-grid">
        <div class="dashboard-main" v-if="channels.length">
          <div class="dash-preview">
            <img :src="channels[currentChannel]?.thumbnail || '/static/img/default-cover.jpg'" alt="Live TV" />
            <div class="dash-overlay"></div>
            <div class="dash-badges">
              <span class="dash-badge live">LIVE TV</span>
            </div>
          </div>
          <div class="dash-content">
            <h2>{{ channels[currentChannel]?.name || 'Ahoy TV' }}</h2>
            <p>{{ channels[currentChannel]?.description || '' }}</p>
          </div>
        </div>

        <div class="dashboard-main" v-else>
          <div class="dash-preview skeleton" style="aspect-ratio:16/9"></div>
          <div class="dash-content">
            <div class="skeleton" style="height:20px;width:60%;margin-bottom:8px"></div>
            <div class="skeleton" style="height:14px;width:80%"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'

const channels = ref([])
const currentChannel = ref(0)

onMounted(async () => {
  const data = await apiFetchCached('/api/live-tv').catch(() => ({ channels: [] }))
  channels.value = data.channels || []
})
</script>
