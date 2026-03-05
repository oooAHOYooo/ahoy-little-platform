<template>
  <div class="ahoy-hub-container">
    <div class="ahoy-hub-widget" :class="{ 'has-active-search': activeSearchPillar }">
      <!-- Gamified Save Counter -->
      <div class="hub-save-counter" :class="{ 'pulse': savePulse }">
        <i class="fas fa-bookmark"></i>
        <span>{{ savedCount }}</span>
      </div>

      <!-- Main Widget Body -->
      <div class="hub-inner">
        <div class="hub-brand">
          <div class="brand-header">
            <span>AHOY UNIVERSAL HUB</span>
          </div>
          <span class="brand-desc">Get content and make quick decisions to save or boost.</span>
        </div>

        <div class="hub-pillars">
          <!-- Pillar Buttons & Search Inputs -->
          <div 
            v-for="pillar in pillars" 
            :key="pillar.id" 
            class="hub-pillar-group"
            :class="{ 'active': activeSearchPillar === pillar.id }"
          >
            <button 
              type="button" 
              class="pillar-btn"
              @click="togglePillarSearch(pillar.id)"
              :title="pillar.label"
            >
              <i :class="pillar.icon"></i>
              <span class="pillar-label">{{ pillar.label }}</span>
            </button>
            
            <div class="pillar-search-wrapper" v-if="activeSearchPillar === pillar.id">
               <input 
                 ref="searchInput"
                 type="text" 
                 class="pillar-search-input" 
                 :placeholder="pillar.placeholder"
                 v-model="searchQuery"
                 @input="handleSearch"
               />
               <i class="fas fa-search search-icon"></i>
            </div>
          </div>
        </div>
        
        <button class="close-hub-btn" v-if="activeSearchPillar" @click="closeSearch" title="Close Search">
           <i class="fas fa-times"></i>
        </button>
      </div>
    </div>

    <!-- Expandable Search Feed ("Warp Pipe" Effect) -->
    <transition name="warp-pipe">
      <div v-if="activeSearchPillar && (searchQuery || isSearching)" class="hub-search-feed">
        <div class="feed-header">
           Results for "{{ activeSearchPillar }}"
        </div>
        <div v-if="isSearching" class="feed-loading">
           <div class="spinner"></div> Loading {{ activeSearchPillar }}...
        </div>
        <div v-else-if="searchResults.length === 0 && searchQuery" class="feed-empty">
           No results found in {{ activeSearchPillar }}.
        </div>
        <div v-else class="feed-results-list">
          <div class="feed-result-item" v-for="result in searchResults.slice(0, 4)" :key="result.id">
            <img :src="result.image" :alt="result.title" class="result-thumb" />
            <div class="result-info">
              <a :href="result.link" class="result-title">{{ result.title }}</a>
              <a :href="result.artistLink" class="result-artist">{{ result.artist }}</a>
            </div>
            <div class="result-actions">
              <button class="quick-action-btn boost-btn" title="Boost" @click="handleBoost(result)">
                <i class="fas fa-bolt"></i>
              </button>
              <button class="quick-action-btn save-btn" :class="{ 'saved': result.saved }" title="Bookmark" @click="handleSave(result)">
                <i class="fas fa-bookmark"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const savedCount = ref(0)
const savePulse = ref(false)
const activeSearchPillar = ref(null)
const searchQuery = ref('')
const searchInput = ref(null)
const searchResults = ref([])
const isSearching = ref(false)
let searchTimeout = null

const pillars = [
  { id: 'music', label: 'Music', icon: 'fas fa-music', placeholder: 'Search artists, tracks...' },
  { id: 'podcasts', label: 'Podcasts', icon: 'fas fa-microphone-alt', placeholder: 'Search shows, episodes...' },
  { id: 'videos', label: 'Videos', icon: 'fas fa-video', placeholder: 'Search clips, films...' },
  { id: 'live', label: 'Live TV', icon: 'fas fa-tv', placeholder: 'Search channels...' }
]

function togglePillarSearch(pillarId) {
  if (activeSearchPillar.value === pillarId) {
    // If clicking the active one, close it
    closeSearch()
  } else {
    // Open new pillar
    activeSearchPillar.value = pillarId
    searchQuery.value = ''
    searchResults.value = []
    
    // Focus input smoothly
    nextTick(() => {
      if (searchInput.value && searchInput.value[0]) {
         searchInput.value[0].focus()
      }
    })
  }
}

function closeSearch() {
  activeSearchPillar.value = null
  searchQuery.value = ''
  searchResults.value = []
}

function handleSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  if (!searchQuery.value.trim()) {
     searchResults.value = []
     return
  }
  
  isSearching.value = true
  // Mock search delay and results based on pillar
  searchTimeout = setTimeout(() => {
    generateMockResults(searchQuery.value, activeSearchPillar.value)
    isSearching.value = false
  }, 400)
}

function generateMockResults(query, type) {
  // Generate beautiful mock data for the feed
  const arr = []
  for(let i=1; i<=4; i++) {
    arr.push({
      id: `${type}-${i}`,
      title: `${query} ${type === 'music' ? 'Track' : type === 'videos' ? 'Video' : 'Item'} ${i}`,
      artist: `Artist ${i}`,
      image: `https://picsum.photos/seed/${type}${i}/100/100`, // Placeholder beautiful images
      link: '#',
      artistLink: '#',
      saved: false
    })
  }
  searchResults.value = arr
}

function handleSave(result) {
  result.saved = !result.saved
  if (result.saved) {
    // Gamification pulse
    savedCount.value++
    savePulse.value = true
    setTimeout(() => {
       savePulse.value = false
    }, 400) // matches css animation duration
  } else {
    savedCount.value = Math.max(0, savedCount.value - 1)
  }
}

function handleBoost(result) {
  // Just visual feedback for now
  console.log(`Boosted ${result.title}!`)
}

</script>

<style scoped>
/* Liquid Glass & Container Styling */
.ahoy-hub-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  width: 100%;
  margin: 0; /* Remove margin to sit flush if needed */
  padding: 0;
  font-family: inherit;
  z-index: 50;
  /* Instead of a fixed large minimum height leaving weird empty space, let it hug the widget but allow filling */
  min-height: auto; 
  justify-content: flex-end; /* Push content to bottom */
}

.ahoy-hub-widget {
  width: 100%;
  max-width: 100vw;
  box-sizing: border-box;
  background: rgba(15, 15, 25, 0.5);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-left: none;
  border-right: none;
  border-bottom: none;
  border-radius: 60px 60px 0 0; /* Only top rounding for a 'floor' look */
  padding: 40px 60px; /* Substantial padding for height */
  position: relative;
  box-shadow: 0 -10px 50px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.1);
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: visible;
  min-height: 200px;
  display: flex;
  align-items: center;
}

/* Glowing aesthetic wrapper */
.ahoy-hub-widget::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 61px 61px 0 0;
  padding: 2px;
  background: linear-gradient(135deg, rgba(88, 101, 242, 0.4), rgba(235, 69, 158, 0.4), rgba(0, 255, 255, 0.3));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  opacity: 0.8;
  transition: opacity 0.4s ease;
}

.ahoy-hub-widget:hover::before, .ahoy-hub-widget.has-active-search::before {
  opacity: 1;
  background: linear-gradient(135deg, rgba(88, 101, 242, 0.8), rgba(235, 69, 158, 0.8), rgba(0, 255, 255, 0.6));
}

.hub-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 1400px; /* Content safety limit but widget is full width */
  margin: 0 auto;
}

.hub-brand {
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: center;
  max-width: 400px;
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 900;
  font-size: 1.1rem;
  letter-spacing: 2px;
  color: #fff;
  text-transform: uppercase;
  text-shadow: 0 4px 10px rgba(0,0,0,0.5);
  white-space: normal;
}

.brand-header i {
  color: #00ffff;
}

.brand-desc {
  font-size: 0.85rem;
  color: rgba(255,255,255,0.7);
  line-height: 1.4;
  letter-spacing: 0.5px;
}

.hub-pillars {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  justify-content: center;
  flex-wrap: wrap; /* allow wrapping to prevent horizontal scroll */
}

.hub-pillar-group {
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
}

.pillar-btn {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 30px;
  padding: 14px 24px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.pillar-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.3);
}

.hub-pillar-group.active .pillar-btn {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 0 25px rgba(255, 255, 255, 0.1);
}

.pillar-search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 350px;
  animation: slide-in 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slide-in {
  from { width: 0; opacity: 0; }
  to { width: 350px; opacity: 1; }
}

.pillar-search-input {
  width: 100%;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 30px;
  padding: 14px 18px 14px 44px;
  color: #fff;
  font-size: 1.05rem;
  outline: none;
  transition: all 0.3s ease;
}

.pillar-search-input:focus {
  border-color: rgba(255, 255, 255, 0.6);
  box-shadow: 0 0 20px rgba(255,255,255,0.15);
  background: rgba(0, 0, 0, 0.6);
}

.pillar-search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.search-icon {
  position: absolute;
  left: 18px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 1.1rem;
}

.close-hub-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 10px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-hub-btn:hover {
  color: #fff;
  background: rgba(255,255,255,0.1);
}

/* Gamified Save Counter */
.hub-save-counter {
  position: absolute;
  top: -24px;
  right: 60px;
  background: linear-gradient(45deg, #ff416c, #ff4b2b);
  border-radius: 25px;
  padding: 8px 18px;
  color: #fff;
  font-weight: 800;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 8px 24px rgba(255, 65, 108, 0.5);
  z-index: 10;
  border: 1px solid rgba(255,255,255,0.4);
  transform-origin: center;
}

.hub-save-counter i {
  font-size: 1.1rem;
}

.hub-save-counter.pulse {
  animation: save-pulse 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes save-pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.4) translateY(-6px); }
  100% { transform: scale(1); }
}

/* Expandable Search Feed ("Warp Pipe") */
.hub-search-feed {
  width: 100%;
  background: rgba(15, 15, 20, 0.8);
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-top: none;
  border-bottom: none;
  padding: 30px 60px;
  box-shadow: 0 40px 80px rgba(0,0,0,0.8);
  position: relative;
  z-index: 1;
}

/* Vue Transitions */
.warp-pipe-enter-active, .warp-pipe-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: top;
}
.warp-pipe-enter-from, .warp-pipe-leave-to {
  opacity: 0;
  transform: translateY(-20px) scaleY(0.9);
}

.feed-header {
  max-width: 1400px;
  margin: 0 auto 24px auto;
  font-size: 1.1rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: rgba(255,255,255,0.4);
  padding-bottom: 18px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.feed-loading {
  text-align: center;
  color: rgba(255,255,255,0.7);
  padding: 60px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  font-size: 1.2rem;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255,255,255,0.2);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s infinite linear;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.feed-empty {
  text-align: center;
  color: rgba(255,255,255,0.5);
  padding: 60px 0;
  font-style: italic;
  font-size: 1.1rem;
}

.feed-results-list {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* Two columns for full width feed */
  gap: 24px;
}

.feed-result-item {
  display: flex;
  align-items: center;
  gap: 20px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 20px;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.feed-result-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255,255,255,0.3);
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 12px 30px rgba(0,0,0,0.4);
}

.result-thumb {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  object-fit: cover;
  box-shadow: 0 8px 20px rgba(0,0,0,0.5);
}

.result-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.result-title {
  color: #fff;
  font-weight: 700;
  font-size: 1.25rem;
  text-decoration: none;
  transition: color 0.2s;
}
.result-title:hover {
  color: #00ffff;
  text-decoration: none;
}

.result-artist {
  color: rgba(255,255,255,0.6);
  font-size: 1.1rem;
  text-decoration: none;
  transition: color 0.2s;
}
.result-artist:hover {
  color: #fff;
}

.result-actions {
  display: flex;
  gap: 12px;
}

.quick-action-btn {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.7);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 1.2rem;
}

.quick-action-btn:hover {
  background: rgba(255,255,255,0.2);
  color: #fff;
  transform: scale(1.15);
  box-shadow: 0 0 15px rgba(255,255,255,0.2);
}

.quick-action-btn.boost-btn:hover {
  color: #ffd700;
  border-color: #ffd700;
  box-shadow: 0 0 20px rgba(255,215,0,0.4);
}

.quick-action-btn.save-btn.saved {
  color: #ff416c;
  background: rgba(255, 65, 108, 0.2);
  border-color: rgba(255, 65, 108, 0.5);
  box-shadow: 0 0 20px rgba(255, 65, 108, 0.3);
}
.quick-action-btn.save-btn.saved i {
  animation: pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes pop {
  0% { transform: scale(1); }
  50% { transform: scale(1.5); }
  100% { transform: scale(1); }
}

/* Responsive adjustments */
@media (max-width: 1100px) {
  .feed-results-list {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .ahoy-hub-widget {
    border-radius: 40px 40px 0 0;
    padding: 30px 20px;
  }
  .hub-inner {
    flex-direction: column;
    gap: 30px;
    width: 100%;
    box-sizing: border-box;
  }
  .hub-brand {
    align-items: center;
    text-align: center;
    width: 100%;
  }
  .brand-header span {
    display: block; /* Keep text on mobile for premium feel if space allows */
  }
  .hub-pillars {
    flex-wrap: wrap;
    gap: 15px;
  }
  .pillar-label {
    display: none; 
  }
  .pillar-search-wrapper {
    width: 100%;
  }
  @keyframes slide-in {
    from { width: 0; opacity: 0; }
    to { width: 100%; opacity: 1; }
  }
  .feed-results-list {
    padding: 0;
  }
  .ahoy-hub-container {
    min-height: auto;
  }
}
</style>
