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

    <!-- More videos (same style as main Videos page grid) -->
    <section class="shows-grid-section more-videos-section" v-if="relatedShows.length">
      <div class="section-header">
        <h2><i class="fas fa-th"></i> More Videos</h2>
      </div>
      <div class="shows-grid shows-grid-16x9">
        <router-link
          v-for="s in relatedShows"
          :key="s.id"
          :to="`/videos/${s.id}`"
          class="show-card more-videos-card"
        >
          <div class="show-thumbnail">
            <img :src="s.thumbnail || '/static/img/default-cover.jpg'" :alt="s.title" loading="lazy" class="image-placeholder" />
            <div class="show-overlay">
              <span class="play-btn"><i class="fas fa-play"></i></span>
            </div>
          </div>
          <div class="show-info">
            <h4>{{ s.title }}</h4>
            <p class="show-host">{{ s.host }}</p>
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

<style scoped>
/* More videos: same style as main Videos page (red/accent, no share buttons) */
.more-videos-section {
  margin-top: 24px;
}
.more-videos-section .section-header h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.more-videos-section .section-header h2 i {
  color: var(--primary-color, #ec4899);
}
.more-videos-section .shows-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}
.more-videos-card {
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  border-radius: var(--border-radius-lg, 12px);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  transition: border-color 0.2s, transform 0.2s;
}
.more-videos-card:hover {
  border-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}
.more-videos-card .show-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
}
.more-videos-card .show-info .show-host {
  margin: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}
.more-videos-card .play-btn {
  background: var(--primary-color, #ec4899);
  color: white;
  border: none;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 12px rgba(236, 72, 153, 0.4);
}
@media (max-width: 768px) {
  .more-videos-section .shows-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
  }
}
</style>
