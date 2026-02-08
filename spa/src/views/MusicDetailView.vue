<template>
  <div class="music-container" v-if="track">
    <!-- Hero -->
    <section class="podcast-show-hero">
      <img
        class="podcast-show-hero-art"
        :src="track.cover_art || '/static/img/default-cover.jpg'"
        :alt="track.title"
      />
      <div class="podcast-show-hero-meta">
        <div class="podcast-show-hero-kicker">Track</div>
        <h1 class="podcast-show-hero-title">{{ track.title }}</h1>
        <p class="podcast-show-hero-desc" v-if="track.artist">{{ track.artist }}</p>
        <p class="episode-subtitle" v-if="track.duration_seconds">
          {{ formatDuration(track.duration_seconds) }}
        </p>
        <div class="podcast-show-hero-actions">
          <button class="podcast-cta" @click="playThis">
            <i :class="isCurrentAndPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
            {{ isCurrentAndPlaying ? 'Pause' : 'Play' }}
          </button>
          <button class="podcast-cta secondary" @click="onBookmark">
            <i :class="bookmarks.isBookmarked(track) ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
            {{ bookmarks.isBookmarked(track) ? 'Saved' : 'Save' }}
          </button>
          <button class="podcast-cta secondary" @click="onShareTrack">
            <i class="fas fa-share-alt"></i>
            Share
          </button>
        </div>
      </div>
    </section>

    <!-- More from this artist -->
    <section class="podcasts-section" v-if="relatedTracks.length">
      <div class="podcasts-section-header">
        <h2>More from {{ track.artist }}</h2>
      </div>
      <div class="episode-list">
        <article
          v-for="(t, idx) in relatedTracks"
          :key="t.id"
          class="episode-row"
          :class="{ playing: playerStore.currentTrack?.id === t.id }"
          @click="playRelated(idx)"
        >
          <img class="episode-art" :src="t.cover_art || '/static/img/default-cover.jpg'" :alt="t.title" loading="lazy" />
          <div class="episode-meta">
            <div class="episode-title">{{ t.title }}</div>
            <div class="episode-show">{{ t.artist }}</div>
          </div>
          <div class="episode-actions">
            <button class="episode-btn" @click.stop="playRelated(idx)">
              <i :class="playerStore.currentTrack?.id === t.id && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
            </button>
          </div>
        </article>
      </div>
    </section>
  </div>

  <!-- Loading -->
  <div class="music-container" v-else>
    <section class="podcast-show-hero">
      <div class="podcast-show-hero-art skeleton" style="aspect-ratio:1;width:100%"></div>
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
import { usePlayerStore } from '../stores/player'
import { useShare, useHaptics } from '../composables/useNative'

const route = useRoute()
const playerStore = usePlayerStore()
const bookmarks = useBookmarks()
const { shareTrack } = useShare()
const haptics = useHaptics()

const track = ref(null)
const allTracks = ref([])

const relatedTracks = computed(() => {
  if (!track.value) return []
  return allTracks.value.filter(t => t.artist === track.value.artist && t.id !== track.value.id)
})

const isCurrentAndPlaying = computed(() =>
  playerStore.currentTrack?.id === track.value?.id && playerStore.isPlaying
)

function formatDuration(seconds) {
  if (!seconds) return ''
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function playThis() {
  if (isCurrentAndPlaying.value) {
    playerStore.pause()
  } else {
    playerStore.play(track.value)
    playerStore.setQueue(allTracks.value, allTracks.value.findIndex(t => t.id === track.value.id))
  }
}

function onBookmark() {
  haptics.onBookmark()
  bookmarks.toggle({ ...track.value, _type: 'track' })
}

function onShareTrack() {
  haptics.light()
  shareTrack(track.value)
}

function playRelated(idx) {
  playerStore.setQueue(relatedTracks.value, idx)
}

onMounted(async () => {
  const data = await apiFetchCached('/api/music').catch(() => ({ tracks: [] }))
  allTracks.value = data.tracks || []
  const id = route.params.id
  track.value = allTracks.value.find(t => String(t.id) === String(id)) || null
})
</script>
