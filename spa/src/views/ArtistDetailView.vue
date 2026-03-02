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
        <div class="panel-header no-icon">
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
                  <button class="action-btn btn-follow" :class="{ active: bookmarks.isBookmarked(artist) }" @click="onFollow">
                    <i :class="bookmarks.isBookmarked(artist) ? 'fas fa-check-circle' : 'fas fa-plus-circle'"></i>
                    {{ bookmarks.isBookmarked(artist) ? 'Following' : 'Follow' }}
                  </button>
                  <button class="action-btn btn-boost" @click="showBoostModal = true">
                    <i class="fas fa-rocket"></i> Boost
                  </button>
                  <button class="action-btn btn-share" @click="onShareArtist">
                    <i class="fas fa-share-nodes"></i> Share
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
        <div class="panel-header no-icon">
           <div class="header-text">
             <h2>Videos</h2>
             <p>{{ artistShows.length }} Videos</p>
           </div>
        </div>
        
        <div class="video-grid flush-left">
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

      <!-- 4. Similar Artists Section -->
      <section class="glass-panel similar-artists-panel" v-if="similarArtists.length">
        <div class="panel-header no-icon">
           <div class="header-text">
             <h2>Similar Artists</h2>
             <p>Discover more like {{ artist.name }}</p>
           </div>
        </div>
        
        <div class="artists-grid flush-left">
           <router-link
             v-for="a in similarArtists.slice(0, 4)"
             :key="a.id"
             :to="`/artists/${a.slug || a.id}`"
             class="artist-card-mini"
           >
              <div class="artist-thumb">
                 <img :src="a.image || '/static/img/default-avatar.png'" loading="lazy" />
              </div>
              <div class="artist-name">{{ a.name }}</div>
           </router-link>
        </div>
      </section>

      <!-- Empty State -->
      <section class="glass-panel empty-panel" v-if="!artistTracks.length && !artistShows.length">
         <i class="fas fa-ghost"></i>
         <p>No content found for this artist yet.</p>
      </section>

      <!-- Boost Modal (Teleported to body for correct stacking/clicks) -->
      <Teleport to="body">
        <div v-if="showBoostModal" class="modal-overlay" @click.self="showBoostModal = false">
          <div class="glass-panel boost-modal">
            <button class="close-modal" @click="showBoostModal = false">&times;</button>
            <h2>Boost {{ artist.name }}</h2>
            <p>Support this artist directly with a contribution.</p>
            
            <div class="boost-amount-selector">
              <button v-for="amt in [5, 10, 20, 50]" :key="amt" @click="boostAmount = amt" :class="{ active: boostAmount === amt }">
                ${{ amt }}
              </button>
              <div class="custom-amount">
                <span>$</span>
                <input type="number" v-model.number="boostAmount" min="1" step="1" />
              </div>
            </div>

            <div class="fee-breakdown">
              <div class="fee-item">
                <span>Boost Amount:</span>
                <span>${{ (boostAmount || 0).toFixed(2) }}</span>
              </div>
              <div class="fee-item">
                <span>Stripe Fee (2.9% + $0.30):</span>
                <span>${{ stripeFee.toFixed(2) }}</span>
              </div>
              <div class="fee-item">
                <span>Platform Fee (7.5%):</span>
                <span>${{ platformFee.toFixed(2) }}</span>
              </div>
              <div class="fee-item total">
                <span>Total Charged:</span>
                <span>${{ totalCharged.toFixed(2) }}</span>
              </div>
            </div>

            <div id="stripe-card-element" class="stripe-element"></div>
            <div v-if="boostError" class="boost-error">{{ boostError }}</div>

            <button class="action-btn btn-boost-submit" :disabled="boostLoading" @click="handleBoost">
              <i v-if="boostLoading" class="fas fa-spinner fa-spin"></i>
              <span v-else>Confirm ${{ totalCharged.toFixed(2) }} Boost</span>
            </button>
            
            <p class="boost-note">Securely processed by Stripe. Boost amount goes directly to the artist.</p>
          </div>
        </div>
      </Teleport>

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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { apiFetch, apiFetchCached } from '../composables/useApi'
import { useBookmarks } from '../composables/useBookmarks'
import { usePlayerStore } from '../stores/player'
import { useShare, useHaptics } from '../composables/useNative'
import { useStripe } from '../composables/useStripe'

const route = useRoute()
const playerStore = usePlayerStore()
const bookmarks = useBookmarks()
const { shareArtist } = useShare()
const haptics = useHaptics()
const { initStripe, createPaymentIntent, confirmBoost } = useStripe()

const loading = ref(true)
const artist = ref(null)
const allArtists = ref([])
const allTracks = ref([])
const allShows = ref([])

// Boost State
const showBoostModal = ref(false)
const boostAmount = ref(10)
const boostLoading = ref(false)
const boostError = ref(null)
let cardElement = null

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

const similarArtists = computed(() => {
  if (!artist.value || !allArtists.value.length) return []
  return allArtists.value
    .filter(a => a.id !== artist.value.id && a.genre === artist.value.genre)
    .sort(() => 0.5 - Math.random()) // Shuffle
})

const stripeFee = computed(() => {
  const amount = boostAmount.value || 0
  return Math.round(((amount * 0.029) + 0.30) * 100) / 100
})

const platformFee = computed(() => {
  const amount = boostAmount.value || 0
  return Math.round((amount * 0.075) * 100) / 100
})

const totalCharged = computed(() => {
  const amount = boostAmount.value || 0
  return Math.round((amount + stripeFee.value + platformFee.value) * 100) / 100
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

async function handleBoost() {
  if (boostAmount.value < 1) {
    boostError.value = 'Minimum boost is $1'
    return
  }
  boostLoading.value = true
  boostError.value = null
  
  try {
    const stripe = await initStripe()
    const { client_secret } = await createPaymentIntent(artist.value.id, boostAmount.value)
    
    const { error, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
      payment_method: { card: cardElement }
    })
    
    if (error) {
      boostError.value = error.message
    } else if (paymentIntent.status === 'succeeded') {
      await confirmBoost(paymentIntent.id)
      window.dispatchEvent(new CustomEvent('ahoy:toast', { 
        detail: { message: `Successfully boosted ${artist.value.name}!`, type: 'success' } 
      }))
      showBoostModal.value = false
    }
  } catch (e) {
    boostError.value = e.message || 'Payment failed'
  } finally {
    boostLoading.value = false
  }
}

watch(showBoostModal, async (open) => {
  if (open) {
    boostError.value = null
    const stripe = await initStripe()
    if (!stripe) return
    
    // Mount card element
    const elements = stripe.elements()
    cardElement = elements.create('card', {
      style: {
        base: {
          color: '#ffffff',
          fontFamily: 'Inter, sans-serif',
          fontSize: '16px',
          '::placeholder': { color: 'rgba(255,255,255,0.4)' }
        }
      }
    })
    
    // Small delay to ensure DOM is ready
    nextTick(() => {
      const el = document.getElementById('stripe-card-element')
      if (el) cardElement.mount('#stripe-card-element')
    })
  } else if (cardElement) {
    cardElement.destroy()
    cardElement = null
  }
})

onMounted(async () => {
  const slug = route.params.slug
  try {
    const [artistsData, musicData, showsData] = await Promise.all([
        apiFetchCached('/api/artists').catch(() => ({ artists: [] })),
        apiFetchCached('/api/music').catch(() => ({ tracks: [] })),
        apiFetchCached('/api/shows').catch(() => ({ shows: [] })),
    ])
    allArtists.value = artistsData.artists || []
    allTracks.value = musicData.tracks || []
    allShows.value = showsData.shows || []

    artist.value = allArtists.value.find(a =>
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

/* Glass Panel Base (Liquid Vibe) */
.glass-panel {
  background: rgba(15, 15, 25, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 32px;
  padding: 2rem;
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  box-shadow: 
    0 15px 35px -5px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  position: relative;
  overflow: hidden;
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

.panel-header.no-icon {
  margin-bottom: 1.5rem;
}

.header-icon {
  width: 56px; height: 56px;
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.75rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.icon-green { background: #00FF00; color: #000; box-shadow: 0 0 20px rgba(0, 255, 0, 0.3); }

.header-text h1, .header-text h2 {
  font-size: 2.5rem;
  font-weight: 900;
  margin: 0;
  line-height: 1;
  text-transform: uppercase;
  letter-spacing: -0.04em;
  color: #fff;
}

.header-text p {
  margin: 0.25rem 0 0 0;
  font-size: 0.95rem;
  color: rgba(255,255,255,0.5);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* Hero Section */
.hero-body {
    display: flex;
    gap: 2.5rem;
    align-items: center;
    position: relative;
    z-index: 1;
}

.hero-avatar {
    width: 200px;
    height: 200px;
    border-radius: 40px;
    object-fit: cover;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}

.hero-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.hero-bio {
    font-size: 1.15rem;
    line-height: 1.6;
    color: rgba(255,255,255,0.8);
    max-width: 600px;
}

.hero-actions {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-start;
}



/* Track List */
.track-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    border-radius: 12px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    transition: all 0.2s ease;
    cursor: pointer;
}

.track-row:hover {
    background: rgba(255,255,255,0.06);
    border-color: rgba(255,255,255,0.1);
}

.track-row.playing {
    background: rgba(0, 255, 0, 0.1);
    border-color: rgba(0, 255, 0, 0.2);
}

/* Video & Artist Grids */
.video-grid.flush-left, .artists-grid.flush-left {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1.5rem;
}

.video-thumb {
    aspect-ratio: 16/9;
    background: #000;
    border-radius: 12px;
    overflow: hidden;
    position: relative;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    margin-bottom: 0.75rem;
}

.artist-thumb {
    aspect-ratio: 1/1;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 0.75rem;
    border: 1px solid rgba(255,255,255,0.1);
}

.artist-thumb img { width: 100%; height: 100%; object-fit: cover; }

.artist-name {
    font-weight: 800;
    font-size: 1rem;
    text-align: center;
    color: #fff;
}

.artist-card-mini {
    text-decoration: none;
    transition: transform 0.3s;
}
.artist-card-mini:hover { transform: translateY(-5px); }

/* Boost Modal */
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.8);
    backdrop-filter: blur(8px);
    z-index: 999999;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    pointer-events: auto !important;
}

.boost-modal {
    width: 100%;
    max-width: 450px;
    background: rgba(20, 20, 35, 0.95);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px;
    text-align: center;
    padding: 2rem;
    pointer-events: auto !important;
}

.close-modal {
    position: absolute;
    top: 1.5rem; right: 1.5rem;
    background: none; border: none;
    color: #fff; font-size: 2rem;
    cursor: pointer; line-height: 1;
}

.boost-amount-selector {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    margin: 2rem 0;
    flex-wrap: wrap;
}

.boost-amount-selector button {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    color: #fff;
    padding: 0.75rem 1.25rem;
    border-radius: 4px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
}

.boost-amount-selector button.active {
    background: #FF00FF;
    border-color: #FF00FF;
}

.custom-amount {
    display: flex;
    align-items: center;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 4px;
    padding: 0 0.25rem 0 0.75rem;
    cursor: text;
}
.custom-amount:focus-within {
    border-color: #FF00FF;
    background: rgba(255, 0, 255, 0.1);
}

.custom-amount input {
    background: none; border: none;
    color: #fff; padding: 0.75rem 0.5rem;
    width: 60px; font-weight: 700;
    outline: none;
    cursor: text;
}

.stripe-element {
    background: rgba(255,255,255,0.05);
    padding: 1rem;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 1.5rem;
}

.btn-boost-submit {
    width: 100%;
    justify-content: center;
    padding: 1.25rem;
    font-size: 1.1rem;
}

.boost-note {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.4);
    margin-top: 1.5rem;
}

.boost-error {
    color: #FF4D4D;
    background: rgba(255, 77, 77, 0.1);
    padding: 0.75rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    font-size: 0.9rem;
}

.fee-breakdown {
    margin: 1.5rem 0;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    text-align: left;
}

.fee-item {
    display: flex;
    justify-content: space-between;
    font-size: 0.95rem;
    color: rgba(255, 255, 255, 0.6);
}

.fee-item.total {
    margin-top: 0.5rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    color: #fff;
    font-weight: 800;
    font-size: 1.1rem;
}

/* Responsive */
@media (max-width: 768px) {
    .hero-body { flex-direction: column; text-align: center; }
    .hero-avatar { width: 160px; height: 160px; }
    .hero-actions { align-items: center; }
    .header-text h1 { font-size: 2rem; }
    .video-grid.flush-left, .artists-grid.flush-left { grid-template-columns: repeat(2, 1fr); gap: 1rem; }
}
</style>

