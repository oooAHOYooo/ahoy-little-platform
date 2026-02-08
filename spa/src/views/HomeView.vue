<template>
  <div class="home-page">
    <!-- What's New Section -->
    <div class="whats-new-section" v-if="whatsNew.length">
      <div class="whats-new-container">
        <div class="whats-new-header">
          <h2>What's New at Ahoy</h2>
        </div>
        <div class="whats-new-updates">
          <div class="whats-new-item" v-for="item in whatsNew.slice(0, 5)" :key="item.title">
            <div class="whats-new-content">
              <div class="whats-new-title">{{ item.title }}</div>
              <div class="whats-new-desc">{{ item.description }}</div>
              <div class="whats-new-date" v-if="item.date">{{ item.date }}</div>
            </div>
            <div class="whats-new-arrow"><i class="fas fa-chevron-right"></i></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Featured Music -->
    <div class="section-header">
      <h2>Music</h2>
      <router-link to="/music" class="see-all">See All</router-link>
    </div>
    <div class="scroll-row" v-if="tracks.length">
      <div class="track-card" v-for="(track, idx) in tracks.slice(0, 10)" :key="track.id">
        <div class="track-cover" @click="playTrack(idx)">
          <img :src="track.cover_art" :alt="track.title" loading="lazy" />
          <div class="track-overlay">
            <button class="play-btn">
              <i :class="playerStore.currentTrack?.id === track.id && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
            </button>
          </div>
        </div>
        <router-link :to="`/music/${track.id}`" class="track-info" style="text-decoration:none;color:inherit">
          <div class="track-title">{{ track.title }}</div>
          <div class="track-artist">{{ track.artist }}</div>
        </router-link>
      </div>
    </div>
    <div class="scroll-row" v-else>
      <div class="track-card" v-for="i in 5" :key="i">
        <div class="track-cover skeleton"></div>
        <div class="track-info"><div class="skeleton" style="height:14px;width:80%"></div></div>
      </div>
    </div>

    <!-- Shows -->
    <div class="section-header">
      <h2>Videos</h2>
      <router-link to="/shows" class="see-all">See All</router-link>
    </div>
    <div class="scroll-row" v-if="shows.length">
      <router-link v-for="show in shows.slice(0, 10)" :key="show.id" :to="`/shows/${show.id}`" class="show-card" style="text-decoration:none;color:inherit">
        <div class="show-thumbnail">
          <img :src="show.thumbnail" :alt="show.title" loading="lazy" />
        </div>
        <div class="show-info">
          <div class="show-title">{{ show.title }}</div>
          <div class="show-host">{{ show.host }}</div>
        </div>
      </router-link>
    </div>
    <div class="scroll-row" v-else>
      <div class="show-card" v-for="i in 5" :key="i">
        <div class="show-thumbnail skeleton"></div>
        <div class="show-info"><div class="skeleton" style="height:14px;width:80%"></div></div>
      </div>
    </div>

    <!-- Artists -->
    <div class="section-header">
      <h2>Artists</h2>
      <router-link to="/artists" class="see-all">See All</router-link>
    </div>
    <div class="scroll-row" v-if="artists.length">
      <router-link v-for="artist in artists.slice(0, 10)" :key="artist.id" :to="`/artists/${artist.slug || artist.id}`" class="artist-card" style="text-decoration:none;color:inherit">
        <div class="artist-cover">
          <img :src="artist.image" :alt="artist.name" loading="lazy" />
        </div>
        <div class="artist-info">
          <div class="artist-name">{{ artist.name }}</div>
          <div class="artist-type">{{ artist.type }}</div>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'
import { usePlayerStore } from '../stores/player'

const playerStore = usePlayerStore()
const tracks = ref([])
const shows = ref([])
const artists = ref([])
const whatsNew = ref([])

function playTrack(idx) {
  const track = tracks.value[idx]
  if (playerStore.currentTrack?.id === track.id && playerStore.isPlaying) {
    playerStore.pause()
  } else {
    playerStore.setQueue(tracks.value, idx)
  }
}

onMounted(async () => {
  const [musicData, showsData, artistsData, whatsNewData] = await Promise.all([
    apiFetchCached('/api/music').catch(() => ({ tracks: [] })),
    apiFetchCached('/api/shows').catch(() => ({ shows: [] })),
    apiFetchCached('/api/artists').catch(() => ({ artists: [] })),
    apiFetchCached('/api/whats-new').catch(() => ({ updates: {} })),
  ])
  tracks.value = musicData.tracks || []
  shows.value = showsData.shows || []
  artists.value = artistsData.artists || []

  // Flatten whats-new nested structure into a simple list
  const updates = whatsNewData.updates || {}
  const flat = []
  for (const year of Object.keys(updates).sort().reverse()) {
    for (const month of Object.keys(updates[year]).sort().reverse()) {
      for (const section of Object.keys(updates[year][month])) {
        const items = updates[year][month][section].items || []
        flat.push(...items)
      }
    }
  }
  whatsNew.value = flat
})
</script>
