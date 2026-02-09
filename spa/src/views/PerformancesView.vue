<template>
  <div class="performances-page">
    <section class="podcasts-hero performances-hero">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-theater-masks" aria-hidden="true"></i> Live Performances</h1>
        <p>Discover amazing live performances, concerts, and exclusive events.</p>
      </div>
    </section>

    <div class="performances-content">
      <div v-if="loading" class="performances-loading">Loading…</div>
      <div v-else-if="performances.length" class="performances-grid">
        <div
          v-for="p in performances"
          :key="p.id || p.slug"
          class="performance-card"
          @click="playPerformance(p)"
        >
          <div class="perf-art">
            <img :src="p.thumbnail || p.cover_art || p.image || '/static/img/default-cover.jpg'" :alt="p.title" loading="lazy" />
            <div class="perf-play"><i class="fas fa-play"></i></div>
          </div>
          <div class="perf-info">
            <h3>{{ p.title || p.name }}</h3>
            <p>{{ p.description || p.host || '' }}</p>
          </div>
        </div>
      </div>
      <div v-else class="performances-empty">
        <p>No performances available yet. Check back soon.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '../composables/useApi'
import { usePlayerStore } from '../stores/player'

const playerStore = usePlayerStore()
const performances = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const data = await apiFetch('/api/performances')
    performances.value = data.performances || data.shows || data || []
    if (Array.isArray(performances.value) === false) performances.value = []
  } catch {
    performances.value = []
  } finally {
    loading.value = false
  }
})

function playPerformance(p) {
  const track = p.audio_url ? p : (p.episodes && p.episodes[0]) || null
  if (track) playerStore.play(track)
}
</script>

<style scoped>
.performances-page { padding-bottom: 3rem; }
.performances-hero.podcasts-hero .podcasts-hero-inner h1 { margin: 0 0 6px 0; font-size: 28px; font-weight: 700; }
.performances-hero.podcasts-hero .podcasts-hero-inner p { margin: 0; color: rgba(255,255,255,0.68); }
.performances-content { max-width: 1000px; margin: 0 auto; padding: 1.5rem; }
.performances-loading, .performances-empty { text-align: center; color: rgba(255,255,255,0.6); padding: 2rem; }
.performances-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1.25rem; }
.performance-card { cursor: pointer; border-radius: 12px; overflow: hidden; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); transition: transform 0.2s, border-color 0.2s; }
.performance-card:hover { transform: translateY(-2px); border-color: rgba(255,255,255,0.15); }
.perf-art { position: relative; aspect-ratio: 1; overflow: hidden; }
.perf-art img { width: 100%; height: 100%; object-fit: cover; }
.perf-play { position: absolute; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; color: #fff; font-size: 1.5rem; opacity: 0; transition: opacity 0.2s; }
.performance-card:hover .perf-play { opacity: 1; }
.perf-info { padding: 12px; }
.perf-info h3 { margin: 0 0 4px; font-size: 0.95rem; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.perf-info p { margin: 0; font-size: 0.8rem; color: rgba(255,255,255,0.5); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
</style>
