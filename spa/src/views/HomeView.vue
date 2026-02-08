<template>
  <div>
    <div class="page-header">
      <h1>Ahoy Indie Media</h1>
      <p>Discover independent music, shows & podcasts</p>
    </div>

    <!-- Featured Music -->
    <div class="section-header">
      <h2>Music</h2>
      <router-link to="/music" class="see-all">See All</router-link>
    </div>
    <div class="scroll-row" v-if="tracks.length">
      <div class="card" v-for="track in tracks.slice(0, 10)" :key="track.id" @click="playTrack(track)">
        <img :src="track.cover_art" :alt="track.title" class="card-image" loading="lazy" />
        <div class="card-body">
          <div class="card-title">{{ track.title }}</div>
          <div class="card-subtitle">{{ track.artist }}</div>
        </div>
      </div>
    </div>
    <div class="scroll-row" v-else>
      <div class="card" v-for="i in 5" :key="i">
        <div class="card-image skeleton"></div>
        <div class="card-body"><div class="skeleton" style="height:14px;width:80%"></div></div>
      </div>
    </div>

    <!-- Shows -->
    <div class="section-header">
      <h2>Shows</h2>
      <router-link to="/shows" class="see-all">See All</router-link>
    </div>
    <div class="scroll-row" v-if="shows.length">
      <div class="card" v-for="show in shows.slice(0, 10)" :key="show.id">
        <img :src="show.thumbnail" :alt="show.title" class="card-image" loading="lazy" />
        <div class="card-body">
          <div class="card-title">{{ show.title }}</div>
          <div class="card-subtitle">{{ show.host }}</div>
        </div>
      </div>
    </div>
    <div class="scroll-row" v-else>
      <div class="card" v-for="i in 5" :key="i">
        <div class="card-image skeleton"></div>
        <div class="card-body"><div class="skeleton" style="height:14px;width:80%"></div></div>
      </div>
    </div>

    <!-- Artists -->
    <div class="section-header">
      <h2>Artists</h2>
      <router-link to="/artists" class="see-all">See All</router-link>
    </div>
    <div class="scroll-row" v-if="artists.length">
      <div class="card" v-for="artist in artists.slice(0, 10)" :key="artist.id">
        <img :src="artist.image" :alt="artist.name" class="card-image" loading="lazy" />
        <div class="card-body">
          <div class="card-title">{{ artist.name }}</div>
          <div class="card-subtitle">{{ artist.type }}</div>
        </div>
      </div>
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

function playTrack(track) {
  playerStore.setQueue(tracks.value, tracks.value.indexOf(track))
}

onMounted(async () => {
  // Fetch all in parallel
  const [musicData, showsData, artistsData] = await Promise.all([
    apiFetchCached('/api/music').catch(() => ({ tracks: [] })),
    apiFetchCached('/api/shows').catch(() => ({ shows: [] })),
    apiFetchCached('/api/artists').catch(() => ({ artists: [] })),
  ])
  tracks.value = musicData.tracks || []
  shows.value = showsData.shows || []
  artists.value = artistsData.artists || []
})
</script>
