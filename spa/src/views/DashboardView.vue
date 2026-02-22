<template>
  <div class="dashboard-page">
    <div class="dashboard-sidebars">
      <aside class="dashboard-sidebar dashboard-left desktop-only">
        <div class="sidebar-content">
          <div class="sidebar-panel sidebar-item">
            <div class="section-title">Search</div>
            <router-link to="/" class="sidebar-search-link">
              <i class="fas fa-search"></i>
              <span>Search music, artists, podcasts...</span>
            </router-link>
          </div>
          <div class="sidebar-panel sidebar-item">
            <div class="section-title">Saved</div>
            <div class="sidebar-bookmarks">
              <template v-if="bookmarkList.length">
                <router-link
                  v-for="(item, key) in bookmarkList"
                  :key="key"
                  :to="bookmarkToRoute(item)"
                  class="sidebar-list-item"
                >
                  <i class="fas fa-bookmark"></i>
                  <span>{{ item.title }}</span>
                </router-link>
              </template>
              <p v-else class="sidebar-empty">No saved items</p>
            </div>
            <router-link to="/my-saves" class="sidebar-see-all">See all</router-link>
          </div>
          <div class="sidebar-panel sidebar-item tip-jar-compact">
            <div class="section-title">Boost</div>
            <p class="tip-jar-copy">Support an artist — 100% goes to them.</p>
            <select v-model="boostArtistId" class="tip-jar-select" aria-label="Select artist">
              <option value="">Select artist…</option>
              <option v-for="a in artists" :key="a.id" :value="a.id || a.name">{{ a.name }}</option>
            </select>
            <div class="tip-jar-amount-row">
              <span class="tip-jar-currency">$</span>
              <input v-model.number="boostAmount" type="number" min="0.5" step="0.5" placeholder="1" class="tip-jar-amount" />
            </div>
            <a
              :href="boostCheckoutUrl"
              class="tip-jar-submit"
              target="_blank"
              rel="noopener"
            >
              <i class="fas fa-bolt"></i> Boost
            </a>
          </div>
          <div class="sidebar-panel sidebar-item">
            <div class="section-title">App</div>
            <div class="sidebar-list">
              <router-link to="/settings" class="sidebar-list-item">
                <i class="fas fa-cog"></i>
                <span>Settings</span>
              </router-link>
              <router-link to="/feedback" class="sidebar-list-item">
                <i class="fas fa-comment"></i>
                <span>Feedback</span>
              </router-link>
            </div>
          </div>
        </div>
      </aside>

      <div class="dashboard-main">
        <div class="content-area content-pad-bottom">
          <div class="unified-header">
            <div class="header-content">
              <h1>Dashboard</h1>
            </div>
          </div>
          <p class="dashboard-welcome">Use the sidebars to search, open saved items, boost artists, and see what’s up next.</p>
          <router-link to="/" class="dashboard-link">Explore home</router-link>
        </div>
      </div>

      <aside class="dashboard-sidebar dashboard-right desktop-only">
        <div class="sidebar-header">
          <h3>Up Next</h3>
        </div>
        <div class="sidebar-content">
          <div v-if="playerStore.queue.length" class="queue-list">
            <div
              v-for="(item, index) in playerStore.queue"
              :key="index"
              class="queue-item"
              @click="playFromQueue(index)"
            >
              <img
                :src="item.cover_art || item.thumbnail || item.artwork || '/static/img/default-cover.jpg'"
                :alt="item.title"
                class="queue-item-art"
              />
              <div class="queue-item-info">
                <div class="queue-item-title">{{ item.title }}</div>
                <div class="queue-item-artist">{{ item.artist || item.host || '' }}</div>
              </div>
            </div>
          </div>
          <div v-else class="sidebar-empty">Queue is empty</div>
          <router-link to="/music" class="sidebar-see-all">Add tracks</router-link>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useBookmarks } from '../composables/useBookmarks'
import { usePlayerStore } from '../stores/player'
import { apiFetchCached } from '../composables/useApi'

const API_BASE = import.meta.env.VITE_API_BASE || 'https://app.ahoy.ooo'

const bookmarks = useBookmarks()
const playerStore = usePlayerStore()

const bookmarkList = computed(() => {
  const b = bookmarks.bookmarks.value
  return Object.entries(b).map(([k, v]) => ({ key: k, ...v }))
})

function bookmarkToRoute(item) {
  const t = (item.type || item._type || 'track').toLowerCase()
  const id = item.id || item.slug
  if (t === 'artist') return `/artists/${item.slug || id}`
  if (t === 'show') return `/videos/${id}`
  if (t === 'podcast' || t === 'clip') return `/podcasts/${item.slug || id}`
  return `/music/${id}`
}

const artists = ref([])
const boostArtistId = ref('')
const boostAmount = ref(1)

const boostCheckoutUrl = computed(() => {
  if (!boostArtistId.value || !boostAmount.value || boostAmount.value < 0.5) return '#'
  return `${API_BASE}/checkout?type=boost&artist_id=${encodeURIComponent(boostArtistId.value)}&amount=${encodeURIComponent(boostAmount.value)}`
})

function playFromQueue(index) {
  const list = playerStore.queue
  if (list[index]) playerStore.play(list[index])
}

onMounted(async () => {
  try {
    const data = await apiFetchCached('/api/artists')
    artists.value = data.artists || []
  } catch {
    artists.value = []
  }
})
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
}
.dashboard-sidebars {
  display: flex;
  gap: 0;
  max-width: 1400px;
  margin: 0 auto;
}
.dashboard-sidebar {
  flex: 0 0 220px;
  padding: 16px;
  border-right: 1px solid rgba(255,255,255,0.06);
  background: rgba(12, 12, 14, 0.5);
}
.dashboard-sidebar.dashboard-right {
  border-right: none;
  border-left: 1px solid rgba(255,255,255,0.06);
}
.sidebar-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.section-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}
.sidebar-search-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(255,255,255,0.06);
  border-radius: 10px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
}
.sidebar-search-link:hover {
  background: rgba(255,255,255,0.1);
  color: var(--text-primary);
}
.sidebar-bookmarks {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 200px;
  overflow-y: auto;
}
.sidebar-list-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  color: var(--text-primary);
  text-decoration: none;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sidebar-list-item:hover {
  color: var(--accent-primary);
}
.sidebar-empty {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}
.sidebar-see-all {
  font-size: 12px;
  color: var(--accent-primary);
  text-decoration: none;
  margin-top: 4px;
}
.tip-jar-compact {
  margin-top: 8px;
}
.tip-jar-copy {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0 0 10px;
}
.tip-jar-select,
.tip-jar-amount {
  width: 100%;
  padding: 8px 10px;
  margin-bottom: 8px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
}
.tip-jar-amount-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}
.tip-jar-currency {
  padding: 8px 10px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px 0 0 8px;
  color: var(--text-secondary);
}
.tip-jar-amount {
  margin-bottom: 0;
  border-radius: 0 8px 8px 0;
  flex: 1;
}
.tip-jar-submit {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: var(--accent-primary, #6ddcff);
  color: #111;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  border: none;
  cursor: pointer;
}
.tip-jar-submit:hover {
  filter: brightness(1.1);
}
.dashboard-main {
  flex: 1;
  min-width: 0;
  padding: 16px 24px;
}
.dashboard-welcome {
  color: var(--text-secondary);
  margin: 0 0 16px;
}
.dashboard-link {
  color: var(--accent-primary);
  text-decoration: none;
}
.sidebar-header h3 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 12px;
  color: var(--text-primary);
}
.queue-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 320px;
  overflow-y: auto;
}
.queue-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
}
.queue-item:hover {
  background: rgba(255,255,255,0.06);
}
.queue-item-art {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  object-fit: cover;
}
.queue-item-info {
  flex: 1;
  min-width: 0;
}
.queue-item-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.queue-item-artist {
  font-size: 11px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 768px) {
  .dashboard-sidebars {
    flex-direction: column;
  }
  .dashboard-sidebar.dashboard-left,
  .dashboard-sidebar.dashboard-right {
    display: none;
  }
}
</style>
