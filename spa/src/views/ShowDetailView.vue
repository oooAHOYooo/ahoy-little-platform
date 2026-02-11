<template>
  <div class="shows-page" v-if="show">
    <!-- Hero -->
    <section class="podcast-show-hero">
      <img
        class="podcast-show-hero-art"
        :src="show.thumbnail || '/static/img/default-cover.jpg'"
        :alt="show.title"
      />
      <div class="podcast-show-hero-meta">
        <div class="podcast-show-hero-kicker">Video</div>
        <h1 class="podcast-show-hero-title">{{ show.title }}</h1>
        <p class="podcast-show-hero-desc" v-if="show.host">{{ show.host }}</p>
        <p class="podcast-show-hero-desc" v-if="show.description">{{ show.description }}</p>
        <div class="podcast-show-hero-actions">
          <button class="podcast-cta" @click="playVideo">
            <i class="fas fa-play"></i>
            Watch
          </button>
          <button class="podcast-cta secondary" @click="bookmarks.toggle({ ...show, _type: 'show' })">
            <i :class="bookmarks.isBookmarked(show) ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
            {{ bookmarks.isBookmarked(show) ? 'Saved' : 'Save' }}
          </button>
        </div>
      </div>
    </section>

    <!-- Video embed (if video_url available) -->
    <section class="podcasts-section" v-if="embedUrl" style="margin-top:16px">
      <div class="video-embed-container" style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:12px">
        <iframe
          :src="embedUrl"
          style="position:absolute;top:0;left:0;width:100%;height:100%;border:0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
        ></iframe>
      </div>
    </section>

    <!-- More videos -->
    <section class="podcasts-section" v-if="relatedShows.length" style="margin-top:16px">
      <div class="podcasts-section-header">
        <h2>More Videos</h2>
      </div>
      <div class="shows-grid">
        <router-link
          v-for="s in relatedShows"
          :key="s.id"
          :to="`/shows/${s.id}`"
          class="show-card"
        >
          <div class="show-thumbnail">
            <img :src="s.thumbnail || '/static/img/default-cover.jpg'" :alt="s.title" loading="lazy" />
            <div class="show-overlay">
              <button class="play-btn"><i class="fas fa-play"></i></button>
            </div>
          </div>
          <div class="show-info">
            <div class="show-title">{{ s.title }}</div>
            <div class="show-host">{{ s.host }}</div>
          </div>
        </router-link>
      </div>
    </section>
  </div>

  <!-- Loading -->
  <div class="shows-page" v-else>
    <section class="podcast-show-hero">
      <div class="podcast-show-hero-art skeleton" style="aspect-ratio:16/9;width:100%"></div>
      <div class="podcast-show-hero-meta">
        <div class="skeleton" style="height:14px;width:40%;margin-bottom:8px"></div>
        <div class="skeleton" style="height:24px;width:70%;margin-bottom:8px"></div>
        <div class="skeleton" style="height:14px;width:50%"></div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiFetchCached } from '../composables/useApi'
import { useBookmarks } from '../composables/useBookmarks'
import { trackRecentPlay } from '../composables/useRecentlyPlayed'

const route = useRoute()
const bookmarks = useBookmarks()

const show = ref(null)
const allShows = ref([])

const relatedShows = computed(() => {
  if (!show.value) return []
  return allShows.value
    .filter(s => s.id !== show.value.id)
    .slice(0, 6)
})

const embedUrl = computed(() => {
  if (!show.value) return null
  const url = show.value.video_url || show.value.url || ''
  // Convert YouTube watch URLs to embed
  const ytMatch = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&]+)/)
  if (ytMatch) return `https://www.youtube.com/embed/${ytMatch[1]}`
  // Vimeo
  const vimeoMatch = url.match(/vimeo\.com\/(\d+)/)
  if (vimeoMatch) return `https://player.vimeo.com/video/${vimeoMatch[1]}`
  return null
})

function playVideo() {
  if (show.value) {
    trackRecentPlay({
      id: show.value.id,
      type: 'show',
      title: show.value.title,
      host: show.value.host,
      thumbnail: show.value.thumbnail,
      url: show.value.video_url || show.value.url,
    })
  }
  const url = show.value?.video_url || show.value?.url || ''
  if (url && !embedUrl.value) {
    window.open(url, '_blank')
  }
  // If embed exists, just scroll to it
}

onMounted(async () => {
  const data = await apiFetchCached('/api/shows').catch(() => ({ shows: [] }))
  allShows.value = data.shows || []
  const id = route.params.id
  show.value = allShows.value.find(s => String(s.id) === String(id)) || null
})
</script>
