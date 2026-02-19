<template>
  <div class="artist-page-container">
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
       <div class="glass-panel text-center">
          <i class="fas fa-spinner fa-spin"></i> Loading Artist...
       </div>
    </div>

    <template v-else-if="artist">
      <!-- 1. Artist Hero Card (White/Black theme) -->
      <section class="glass-panel artist-hero-panel">
        <div class="panel-header">
           <div class="header-icon icon-white"><i class="fas fa-user-astronaut"></i></div>
           <div class="header-text">
             <h1>{{ artist.name }}</h1>
             <p>{{ artist.genre || 'Artist' }}</p>
           </div>
        </div>
        
        <div class="hero-body">
            <div class="hero-avatar-wrapper">
               <img :src="artist.image || '/static/img/default-avatar.png'" :alt="artist.name" class="hero-avatar" />
            </div>
            <div class="hero-info">
               <div class="hero-bio" v-if="artist.bio">{{ artist.bio }}</div>
               <div class="hero-actions">
                  <button class="action-btn btn-white" @click="onFollow">
                    <i :class="bookmarks.isBookmarked(artist) ? 'fas fa-check' : 'fas fa-plus'"></i>
                    {{ bookmarks.isBookmarked(artist) ? 'Following' : 'Follow' }}
                  </button>
                  <button class="action-btn btn-glass" @click="onShareArtist">
                    <i class="fas fa-share-alt"></i> Share
                  </button>
               </div>
            </div>
        </div>
      </section>

      <!-- 2. Music Section (Green theme) -->
      <section class="glass-panel music-panel" v-if="artistTracks.length">
        <div class="panel-header">
           <div class="header-icon icon-green"><i class="fas fa-music"></i></div>
           <div class="header-text">
             <h2>Music</h2>
             <p>{{ artistTracks.length }} Tracks</p>
           </div>
        </div>
        
        <div class="track-list">
           <div 
             v-for="(t, idx) in artistTracks" 
             :key="t.id"
             class="track-row"
             :class="{ playing: playerStore.currentTrack?.id === t.id }"
             @click="playTrack(idx)"
           >
              <div class="track-art">
                 <img :src="t.cover_art || '/static/img/default-cover.jpg'" loading="lazy" />
                 <div class="track-overlay"><i :class="playerStore.currentTrack?.id === t.id && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i></div>
              </div>
              <div class="track-info">
                 <div class="track-title">{{ t.title }}</div>
                 <div class="track-meta">{{ formatDuration(t.duration_seconds) }}</div>
              </div>
              <button class="track-action" @click.stop="bookmarks.toggle({ ...t, _type: 'track' })">
                <i :class="bookmarks.isBookmarked(t) ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
              </button>
           </div>
        </div>
      </section>

      <!-- 3. Videos Section (Magenta theme) -->
      <section class="glass-panel video-panel" v-if="artistShows.length">
        <div class="panel-header">
           <div class="header-icon icon-magenta"><i class="fas fa-video"></i></div>
           <div class="header-text">
             <h2>Videos</h2>
             <p>{{ artistShows.length }} Videos</p>
           </div>
        </div>
        
        <div class="video-grid">
           <router-link
             v-for="show in artistShows"
             :key="show.id"
             :to="`/videos?play=${show.id}`"
             class="video-card"
           >
              <div class="video-thumb">
                 <img :src="show.thumbnail || '/static/img/default-cover.jpg'" loading="lazy" />
                 <div class="play-overlay"><i class="fas fa-play"></i></div>
              </div>
              <div class="video-title">{{ show.title }}</div>
           </router-link>
        </div>
      </section>

      <!-- Empty State -->
      <section class="glass-panel empty-panel" v-if="!artistTracks.length && !artistShows.length">
         <i class="fas fa-ghost"></i>
         <p>No content found for this artist yet.</p>
      </section>

    </template>
    
    <!-- Not Found -->
    <div v-else class="loading-state">
       <div class="glass-panel text-center">
          <i class="fas fa-exclamation-triangle"></i> Artist not found
       </div>
    </div>

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
const { shareArtist } = useShare()
const haptics = useHaptics()
const loading = ref(true)

const artist = ref(null)
const allTracks = ref([])
const allShows = ref([])

const artistTracks = computed(() => {
  if (!artist.value) return []
  return allTracks.value.filter(t =>
    t.artist === artist.value.name ||
    t.artist_id === artist.value.id
  )
})

const artistShows = computed(() => {
  if (!artist.value) return []
  return allShows.value.filter(s =>
    s.host === artist.value.name ||
    s.host_id === artist.value.id
  )
})

function formatDuration(seconds) {
  if (!seconds) return ''
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function onFollow() {
  haptics.onBookmark()
  bookmarks.toggle({ ...artist.value, _type: 'artist' })
}

function onShareArtist() {
  haptics.light()
  shareArtist(artist.value)
}

function playTrack(idx) {
  playerStore.setQueue(artistTracks.value, idx)
}

onMounted(async () => {
  const slug = route.params.slug
  try {
    const [artistsData, musicData, showsData] = await Promise.all([
        apiFetchCached('/api/artists').catch(() => ({ artists: [] })),
        apiFetchCached('/api/music').catch(() => ({ tracks: [] })),
        apiFetchCached('/api/shows').catch(() => ({ shows: [] })),
    ])
    const artists = artistsData.artists || []
    allTracks.value = musicData.tracks || []
    allShows.value = showsData.shows || []

    // Match by slug or id
    artist.value = artists.find(a =>
        a.slug === slug || String(a.id) === String(slug)
    ) || null
  } catch (e) {
      console.error(e)
  } finally {
      loading.value = false
  }
})
</script>

<style scoped>
/* Container Layout */
.artist-page-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  min-height: 80vh;
}

/* Glass Panel Base (Nintendo/Liquid Vibe) */
.glass-panel {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 32px;
  padding: 2rem;
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  box-shadow: 
    0 15px 35px -5px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    inset 0 0 20px rgba(255, 255, 255, 0.02);
  position: relative;
  overflow: hidden;
}

.glass-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 100%;
    background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0) 40%);
    pointer-events: none;
    z-index: 0;
}

/* Header Styles */
.panel-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 2rem;
  position: relative;
  z-index: 1;
}

.header-icon {
  width: 56px; height: 56px;
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.75rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  color: #000;
}

.icon-white { background: #FFFFFF; color: #000; box-shadow: 0 0 20px rgba(255, 255, 255, 0.3); }
.icon-green { background: #00FF00; color: #000; box-shadow: 0 0 20px rgba(0, 255, 0, 0.3); }
.icon-magenta { background: #FF00FF; color: #000; box-shadow: 0 0 20px rgba(255, 0, 255, 0.3); }

.header-text h1, .header-text h2 {
  font-size: 2rem;
  font-weight: 900;
  margin: 0;
  line-height: 0.9;
  text-transform: uppercase;
  letter-spacing: -0.03em;
  color: rgba(255,255,255,0.95);
}

.header-text p {
  margin: 0.35rem 0 0 0;
  font-size: 0.9rem;
  color: rgba(255,255,255,0.6);
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

/* Hero Section */
.hero-body {
    display: flex;
    gap: 2rem;
    align-items: flex-start;
    position: relative;
    z-index: 1;
}

.hero-avatar-wrapper {
    flex-shrink: 0;
}

.hero-avatar {
    width: 180px;
    height: 180px;
    border-radius: 50%; /* Circle avatar */
    object-fit: cover;
    border: 4px solid rgba(255,255,255,0.1);
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.hero-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding-top: 0.5rem;
}

.hero-bio {
    font-size: 1.1rem;
    line-height: 1.6;
    color: rgba(255,255,255,0.85);
    margin-bottom: 2rem;
    max-width: 600px;
}

.hero-actions {
    display: flex;
    gap: 1rem;
}

.action-btn {
    appearance: none;
    border: none;
    padding: 0.8rem 1.75rem;
    border-radius: 99px; /* Pill shape */
    font-weight: 800;
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    transition: transform 0.2s, filter 0.2s;
}

.action-btn:hover {
    transform: scale(1.05);
    filter: brightness(1.1);
}

.btn-white {
    background: #FFFFFF;
    color: #000;
    box-shadow: 0 4px 15px rgba(255,255,255,0.3);
}

.btn-glass {
    background: rgba(255,255,255,0.1);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.2);
}

/* Track List */
.track-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    position: relative;
    z-index: 1;
}

.track-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem;
    border-radius: 16px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    transition: all 0.2s ease;
    cursor: pointer;
}

.track-row:hover {
    background: rgba(255,255,255,0.08);
    transform: translateX(4px);
    border-color: rgba(255,255,255,0.15);
}

.track-row.playing {
    background: rgba(0, 255, 0, 0.15);
    border-color: rgba(0, 255, 0, 0.3);
}

.track-art {
    width: 48px; height: 48px;
    border-radius: 10px;
    overflow: hidden;
    position: relative;
    flex-shrink: 0;
}

.track-art img { width: 100%; height: 100%; object-fit: cover; }

.track-overlay {
    position: absolute; inset: 0;
    background: rgba(0,0,0,0.4);
    display: flex; align-items: center; justify-content: center;
    opacity: 0; transition: opacity 0.2s;
    color: #fff;
}
.track-row:hover .track-overlay, .track-row.playing .track-overlay { opacity: 1; }

.track-info { flex: 1; min-width: 0; }

.track-title {
    font-weight: 700;
    font-size: 1rem;
    color: #fff;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.track-meta {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.5);
    margin-top: 0.2rem;
}

.track-action {
    width: 36px; height: 36px;
    border-radius: 50%;
    background: transparent;
    border: 1px solid transparent;
    color: rgba(255,255,255,0.5);
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
}

.track-action:hover {
    color: #fff;
    background: rgba(255,255,255,0.1);
}

/* Video Grid */
.video-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1.5rem;
    position: relative;
    z-index: 1;
}

.video-card {
    text-decoration: none;
    color: #fff;
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.video-card:hover {
    transform: translateY(-6px) rotate(-1deg);
}

.video-thumb {
    aspect-ratio: 16/9;
    background: #000;
    border-radius: 16px;
    overflow: hidden;
    position: relative;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    margin-bottom: 0.75rem;
}

.video-thumb img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s; }
.video-card:hover .video-thumb img { transform: scale(1.05); }

.play-overlay {
    position: absolute; inset: 0;
    background: rgba(0,0,0,0.3);
    display: flex; align-items: center; justify-content: center;
    opacity: 0; transition: opacity 0.2s;
}
.play-overlay i { font-size: 2.5rem; color: #fff; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5)); }
.video-card:hover .play-overlay { opacity: 1; }

.video-title {
    font-weight: 700;
    font-size: 0.95rem;
    line-height: 1.3;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
    color: rgba(255,255,255,0.9);
}

/* Empty State */
.empty-panel {
    text-align: center;
    color: rgba(255,255,255,0.4);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    min-height: 300px;
}
.empty-panel i { font-size: 4rem; margin-bottom: 1rem; opacity: 0.5; }

/* Responsive */
@media (max-width: 768px) {
    .artist-page-container { padding: 1rem; gap: 1.5rem; }
    .glass-panel { padding: 1.5rem; border-radius: 24px; }
    
    .hero-body { flex-direction: column; align-items: center; text-align: center; gap: 1.5rem; }
    .hero-avatar { width: 140px; height: 140px; }
    .hero-actions { justify-content: center; }
    
    .panel-header { flex-direction: row; gap: 1rem; margin-bottom: 1.5rem; }
    .header-icon { width: 48px; height: 48px; font-size: 1.5rem; }
    .header-text h1, .header-text h2 { font-size: 1.75rem; }
    
    .video-grid { grid-template-columns: repeat(2, 1fr); gap: 1rem; }
}
</style>
