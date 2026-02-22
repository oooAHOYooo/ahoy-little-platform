<template>
  <section class="explore-widgets-container" v-if="!loading">

    <!-- 1. Recently Played (Habit Loop: Jump back in) -->
    <div class="explore-widget recent-widget">
      <div class="widget-header">
        <div class="header-icon"><i class="fas fa-history"></i></div>
        <div class="header-text">
          <h3>Recently Played</h3>
          <p>Jump back in</p>
        </div>
      </div>
      <div class="widget-grid">
        <div v-if="recentlyPlayed.length === 0" class="empty-placeholder">
          No history yet
        </div>
        <router-link
          v-else
          v-for="item in recentlyPlayed"
          :key="item.key || item.id"
          :to="`/${item.type === 'show' ? 'shows' : 'music'}/${item.id}`"
          class="widget-card"
          v-tilt="{ target: '.card-image img', scale: 1.1, speed: 600, max: 10 }"
          @mouseenter="playHoverSound"
          @click="playClickSound"
        >
          <div class="card-image">
            <img :src="item.artwork || item.cover_art || '/static/img/default-cover.jpg'" :alt="item.title" loading="lazy" />
            <div class="play-icon"><i class="fas fa-play"></i></div>
          </div>
          <div class="card-title">{{ item.title }}</div>
        </router-link>
      </div>
      <div class="widget-cta cta-indigo" style="cursor: default">
        Your History
      </div>
    </div>

    <!-- 2. My Saves (Habit Loop: Personal Library) -->
    <div class="explore-widget saves-widget">
      <div class="widget-header">
        <div class="header-icon"><i class="fas fa-bookmark"></i></div>
        <div class="header-text">
          <h3>My Saves</h3>
          <p>Your Favorites</p>
        </div>
      </div>
      <div class="widget-grid">
        <div v-if="mySaves.length === 0" class="empty-placeholder">
          Nothing### Video Widget Unification
- Verified that Videos now appear square (1:1), matching the Podcasts and Music sections.
- Verified that the grid items align perfectly across different widgets.

### Backend API Test
        </div>
        <router-link
          v-else
          v-for="item in mySaves"
          :key="item.id || item.slug"
          :to="item.type === 'artist' ? `/artists/${item.slug}` : `/${item.type === 'show' ? 'shows' : 'music'}/${item.id}`"
          class="widget-card"
          v-tilt="{ target: '.card-image img', scale: 1.1, speed: 600, max: 10 }"
          @mouseenter="playHoverSound"
          @click="playClickSound"
        >
          <div class="card-image">
            <img :src="item.cover_art || '/static/img/default-cover.jpg'" :alt="item.title" loading="lazy" />
          </div>
          <div class="card-title">{{ item.title || item.name }}</div>
        </router-link>
      </div>
      <router-link to="/profile" class="widget-cta cta-gold" @click="playClickSound">
        View All Saves
      </router-link>
    </div>
    
    <!-- 3. Videos (High Engagement) -->
    <div class="explore-widget video-widget">
      <div class="widget-header">
        <div class="header-icon"><i class="fas fa-video"></i></div>
        <div class="header-text">
          <h3>Videos</h3>
          <p>Watch latest content</p>
        </div>
      </div>
      <div class="widget-grid">
        <router-link
          v-for="video in randomVideos"
          :key="video.id"
          :to="`/videos?play=${video.id}`"
          class="widget-card video-card"
          v-tilt="{ target: '.card-image img', scale: 1.1, speed: 600, max: 10 }"
          @mouseenter="playHoverSound"
          @click="playClickSound"
        >
          <div class="card-image">
            <img :src="video.thumbnail || '/static/img/default-cover.jpg'" :alt="video.title" loading="lazy" />
            <div class="play-icon"><i class="fas fa-play"></i></div>
          </div>
          <div class="card-title">{{ video.title }}</div>
        </router-link>
      </div>
      <router-link to="/videos" class="widget-cta cta-red" @click="playClickSound">
        Watch Now
      </router-link>
    </div>

    <!-- 4. Podcasts -->
    <div class="explore-widget podcast-widget">
      <div class="widget-header">
        <div class="header-icon"><i class="fas fa-podcast"></i></div>
        <div class="header-text">
          <h3>Podcasts</h3>
          <p>Fresh episodes & shows</p>
        </div>
      </div>
      <div class="widget-grid">
        <router-link
          v-for="show in randomPodcasts"
          :key="show.slug"
          :to="`/podcasts/${show.slug}`"
          class="widget-card"
          v-tilt="{ target: '.card-image img', scale: 1.1, speed: 600, max: 10 }"
          @mouseenter="playHoverSound"
          @click="playClickSound"
        >
          <div class="card-image">
            <img :src="show.artwork || '/static/img/default-cover.jpg'" :alt="show.title" loading="lazy" />
          </div>
          <div class="card-title">{{ show.title }}</div>
        </router-link>
      </div>
      <router-link to="/podcasts" class="widget-cta cta-purple" @click="playClickSound">
        Explore Podcasts
      </router-link>
    </div>

    <!-- 5. Music -->
    <div class="explore-widget music-widget">
      <div class="widget-header">
        <div class="header-icon"><i class="fas fa-music"></i></div>
        <div class="header-text">
          <h3>Music</h3>
          <p>Albums & Singles</p>
        </div>
      </div>
      <div class="widget-grid">
        <router-link
          v-for="item in randomMusic"
          :key="item.id || item.title"
          :to="item.type === 'album' ? { path: '/music', query: { q: item.title } } : `/music/${item.id}`"
          class="widget-card"
          v-tilt="{ target: '.card-image img', scale: 1.1, speed: 600, max: 10 }"
          @mouseenter="playHoverSound"
          @click="playClickSound"
        >
          <div class="card-image">
            <img :src="item.cover_art || '/static/img/default-cover.jpg'" :alt="item.title" loading="lazy" />
          </div>
          <div class="card-title">{{ item.title }}</div>
        </router-link>
      </div>
      <router-link to="/music" class="widget-cta cta-blue" @click="playClickSound">
        Music Library
      </router-link>
    </div>

    <!-- 6. Artists -->
    <div class="explore-widget artist-widget">
      <div class="widget-header">
        <div class="header-icon"><i class="fas fa-users"></i></div>
        <div class="header-text">
          <h3>Artists</h3>
          <p>Meet the creators</p>
        </div>
      </div>
      <div class="widget-grid">
        <router-link
          v-for="artist in randomArtists"
          :key="artist.slug"
          :to="`/artists/${artist.slug}`"
          class="widget-card"
          v-tilt="{ target: '.card-image img', scale: 1.1, speed: 600, max: 10 }"
          @mouseenter="playHoverSound"
          @click="playClickSound"
        >
          <div class="card-image circle">
            <img :src="artist.image || '/static/img/default-avatar.png'" :alt="artist.name" loading="lazy" />
          </div>
          <div class="card-title">{{ artist.name }}</div>
        </router-link>
      </div>
      <router-link to="/artists" class="widget-cta cta-green" @click="playClickSound">
        Discover Artists
      </router-link>
    </div>

  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'
import { useBookmarks } from '../composables/useBookmarks'
import { useUISounds } from '../composables/useUISounds'
import vTilt from '../directives/vTilt'

const loading = ref(true)
const randomPodcasts = ref([])
const randomVideos = ref([])
const randomMusic = ref([]) // Albums or Tracks
const randomArtists = ref([])
const mySaves = ref([])
const recentlyPlayed = ref([])

const bookmarks = useBookmarks()
const { playHoverSound, playClickSound } = useUISounds()

// Determine if we can use tilt (desktop only mostly)
const canTilt = typeof window !== 'undefined' && window.matchMedia('(hover: hover)').matches

function getRandomItems(arr, count) {
  if (!arr || arr.length === 0) return []
  const shuffled = [...arr].sort(() => 0.5 - Math.random())
  return shuffled.slice(0, count)
}

function loadRecentlyPlayed() {
  try {
    const raw = localStorage.getItem('ahoy.recentlyPlayed.v1')
    if (raw) {
      recentlyPlayed.value = JSON.parse(raw).slice(0, 6)
    }
  } catch (e) {
    console.error('Failed to load recently played', e)
  }
}

function updateMySaves() {
    const all = Object.values(bookmarks.bookmarks.value || {})
    mySaves.value = all.reverse().slice(0, 6)
}

onMounted(async () => {
  try {
    // Fetch all data in parallel
    const [podData, videoData, musicData, artistData] = await Promise.all([
      apiFetchCached('/api/podcasts').catch(() => ({ shows: [] })),
      apiFetchCached('/api/shows').catch(() => ({ shows: [] })),
      apiFetchCached('/api/music').catch(() => ({ tracks: [], albums: [] })),
      apiFetchCached('/api/artists').catch(() => ({ artists: [] }))
    ])

    // Process Podcasts
    randomPodcasts.value = getRandomItems(podData.shows || [], 6)

    // Process Videos
    randomVideos.value = getRandomItems(videoData.shows || [], 6)

    // Process Music
    const allTracks = musicData.tracks || []
    const albumMap = new Map()
    const singles = []
    
    for (const t of allTracks) {
      if (t.album && t.album !== 'Single' && !albumMap.has(t.album)) {
        albumMap.set(t.album, {
          id: t.album,
          title: t.album,
          cover_art: t.cover_art || t.artwork,
          artist: t.artist,
          type: 'album'
        })
      } else {
        singles.push({
          id: t.id,
          title: t.title,
          cover_art: t.cover_art || t.artwork,
          artist: t.artist,
          type: 'track'
        })
      }
    }
    
    let musicItems = Array.from(albumMap.values())
    
    if (musicItems.length < 3) {
      const needed = 3 - musicItems.length
      const randomSingles = getRandomItems(singles, needed)
      musicItems = [...musicItems, ...randomSingles]
    }
    
    if (musicItems.length < 3) {
       const remaining = 3 - musicItems.length
       const existingIds = new Set(musicItems.map(i => i.id || i.title))
       const moreTracks = allTracks.filter(t => !existingIds.has(t.id) && !existingIds.has(t.title))
       
       const randomMore = getRandomItems(moreTracks, remaining).map(t => ({
          id: t.id,
          title: t.title,
          cover_art: t.cover_art || t.artwork,
          artist: t.artist,
          type: 'track'
       }))
       musicItems = [...musicItems, ...randomMore]
    }
    
    randomMusic.value = musicItems.slice(0, 6)

    // Process Artists
    const artists = (artistData.artists || []).map(a => ({
       ...a,
       slug: a.slug || a.id || (a.name || '').toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
    }))
    randomArtists.value = getRandomItems(artists, 6)

    // Load Local Data
    loadRecentlyPlayed()
    updateMySaves()
    
    // Listen for updates
    window.addEventListener('recentlyPlayed:updated', (e) => {
        if (e.detail && e.detail.recent) {
            recentlyPlayed.value = e.detail.recent.slice(0, 12)
        }
    })
    
    window.addEventListener('bookmarks:changed', updateMySaves)

  } catch (e) {
    console.error('Error loading explore widgets', e)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
    window.removeEventListener('recentlyPlayed:updated', loadRecentlyPlayed)
    window.removeEventListener('bookmarks:changed', updateMySaves)
})
</script>

<style scoped>
.explore-widgets-container {
  display: flex;
  flex-direction: column;
  gap: 3rem;
  padding: 2rem 0;
  max-width: 1800px;
  margin: 0;
}

/* Base Widget Style */
.explore-widget {
  background: rgba(0, 0, 0, 0.4); /* Darker base */
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 32px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  box-shadow: 
    0 20px 50px -10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.15),
    inset 0 0 40px rgba(0, 0, 0, 0.2);
  transition: all 0.5s cubic-bezier(0.19, 1, 0.22, 1);
  position: relative;
  overflow: hidden;
  /* Parallax container setup */
  transform-style: preserve-3d;
  perspective: 1000px;
}

.explore-widget::before {
    /* Subtle noise/texture overlay could go here, but keeping clean glass */
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 100%;
    background: linear-gradient(180deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0) 100%);
    pointer-events: none;
    z-index: 0;
}

.explore-widget:hover {
    background: rgba(0, 0, 0, 0.5);
    border-color: rgba(255, 255, 255, 0.25);
    transform: scale(1.02) translateY(-5px); /* Smooth zoom parallax */
    box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.6);
}

/* Header */
.widget-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 0.5rem;
  position: relative;
  z-index: 1;
}

.header-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  color: #000;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  background: #fff; /* Default, overridden by themes */
}

.header-text h3 {
  font-size: 1.75rem;
  font-weight: 900;
  margin: 0;
  line-height: 0.9;
  text-transform: uppercase;
  letter-spacing: -0.03em;
  color: rgba(255,255,255,0.95);
}

.header-text p {
  margin: 0.35rem 0 0 0;
  font-size: 0.85rem;
  color: rgba(255,255,255,0.6);
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

/* Grid */
.widget-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 1.5rem;
  position: relative;
  z-index: 1;
}

/* Card */
.widget-card {
  display: block;
  text-decoration: none;
  color: inherit;
  transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  cursor: pointer;
  group: card;
}

/* 
   REMOVED: .widget-card:hover transform 
   Reason: We want the frame to be static while the content moves in 3D 
*/
/*.widget-card:hover {
  transform: translateY(-8px) scale(1.05) rotate(1deg);
}*/

.card-image {
  aspect-ratio: 1 / 1;
  width: 100%;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 0.85rem;
  box-shadow: 0 10px 25px rgba(0,0,0,0.4);
  background: #000;
  position: relative;
  border: 0;
  /* 3D Context for inner image tilt */
  transform-style: preserve-3d;
  perspective: 1000px; 
}

/* removed video-card 16:9 override for unification */

.card-image.circle {
    border-radius: 50%;
    aspect-ratio: 1;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s ease;
  /* Ensure image can be tilted */
  transform-origin: center center;
  will-change: transform;
}

/* 
   REMOVED: .widget-card:hover .card-image img transform
   Reason: Handled by v-tilt directive now 
*/
/*
.widget-card:hover .card-image img {
    transform: scale(1.1);
}
*/

.card-title {
  font-weight: 700;
  font-size: 0.95rem;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 0.25rem;
  color: rgba(255,255,255,0.9);
  opacity: 0.8;
  transition: opacity 0.2s;
}

.widget-card:hover .card-title {
    opacity: 1;
}

/* Play Icon Overlay */
.play-icon {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0,0,0,0.2);
    opacity: 0;
    transition: opacity 0.2s;
}

.play-icon i {
    font-size: 3rem;
    color: #fff;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5));
}

.widget-card:hover .play-icon {
    opacity: 1;
}

/* Empty State for Saves/Recent */
.empty-placeholder {
    grid-column: span 3;
    text-align: center;
    padding: 2rem;
    color: rgba(255,255,255,0.4);
    font-style: italic;
    background: rgba(255,255,255,0.03);
    border-radius: 16px;
}

/* CTA Buttons */
.widget-cta {
  display: block;
  text-align: center;
  padding: 1.1rem 0;
  border-radius: 18px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.05); /* Glass base */
  border: 1px solid rgba(255, 255, 255, 0.2); /* Base border */
  color: #fff;
  transition: all 0.3s ease;
  font-size: 1rem;
  position: relative;
  z-index: 1;
  margin-top: 0.5rem;
  backdrop-filter: blur(10px);
}

.widget-cta:hover {
  background: rgba(255, 255, 255, 0.1); 
  border-color: rgba(255, 255, 255, 0.4);
  /* do not scale as requested */
  transform: none;
  box-shadow: 
    0 0 30px rgba(0, 0, 0, 0.8),
    0 10px 40px rgba(0, 0, 0, 0.6);
  text-shadow: 0 0 10px rgba(255,255,255,0.3);
}

/* Theme Colors - Affects Icons and Button Borders/Glows */

/* CYAN (Podcasts) */
.podcast-widget .header-icon { background: #00ffff; box-shadow: 0 0 25px rgba(0, 255, 255, 0.4); }
.cta-purple { border-color: rgba(0, 255, 255, 0.3); color: #00ffff; }
.cta-purple:hover { border-color: #00ffff; box-shadow: 0 0 40px rgba(0, 0, 0, 0.9); color: #fff; }

/* ELECTRIC BLUE (Videos) */
.video-widget .header-icon { background: #00a2ff; box-shadow: 0 0 25px rgba(0, 162, 255, 0.4); }
.cta-red { border-color: rgba(0, 162, 255, 0.3); color: #00a2ff; }
.cta-red:hover { border-color: #00a2ff; box-shadow: 0 0 40px rgba(0, 0, 0, 0.9); color: #fff; }

/* DEEP BLUE (Music) */
.music-widget .header-icon { background: #0066ff; box-shadow: 0 0 25px rgba(0, 102, 255, 0.4); }
.cta-blue { border-color: rgba(0, 102, 255, 0.3); color: #0066ff; }
.cta-blue:hover { border-color: #0066ff; box-shadow: 0 0 40px rgba(0, 0, 0, 0.9); color: #fff; }

/* SILVER (Artists) */
.artist-widget .header-icon { background: #e5e7eb; color: #111; box-shadow: 0 0 25px rgba(255, 255, 255, 0.2); }
.cta-green { border-color: rgba(255, 255, 255, 0.2); color: #e5e7eb; }
.cta-green:hover { border-color: #fff; box-shadow: 0 0 40px rgba(0, 0, 0, 0.9); color: #000; background: #fff; }

/* INDIGO (My Saves / Recent) */
.saves-widget .header-icon { background: #5b21b6; box-shadow: 0 0 25px rgba(91, 33, 182, 0.4); }
.cta-gold { border-color: rgba(91, 33, 182, 0.3); color: #a78bfa; }
.cta-gold:hover { border-color: #a78bfa; box-shadow: 0 0 40px rgba(0, 0, 0, 0.9); color: #fff; }

.recent-widget .header-icon { background: #4c1d95; box-shadow: 0 0 25px rgba(76, 29, 149, 0.4); }
.cta-indigo { border-color: rgba(76, 29, 149, 0.3); color: #c4b5fd; }
.cta-indigo:hover { border-color: #c4b5fd; box-shadow: 0 0 40px rgba(0, 0, 0, 0.9); color: #fff; }


@media (max-width: 768px) {
  .widget-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
  }
  .widget-grid .widget-card:nth-child(n+4) {
    display: none;
  }
  .explore-widget {
    padding: 1.5rem;
    border-radius: 24px;
    gap: 1rem;
  }
  .card-title {
      font-size: 0.8rem;
  }
  .header-text h3 { font-size: 1.4rem; }
  .header-icon { width: 42px; height: 42px; font-size: 1.25rem; border-radius: 12px; }
  .widget-cta { padding: 0.9rem 0; font-size: 0.9rem; }
}
</style>
