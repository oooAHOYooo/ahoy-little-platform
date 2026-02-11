<template>
  <div class="now-playing-wrapper" :class="{ 'has-player': !!playerStore.currentTrack }">
    <div
      class="now-playing-glass now-playing-sticky"
      :class="{ 'now-playing-is-playing': playerStore.currentTrack && playerStore.isPlaying }"
    >
      <div class="now-playing-container">
        <!-- Left: Album art + track info -->
        <div class="now-playing-left">
          <div
            class="now-playing-album-art"
            @click="playerStore.currentTrack ? (goToNowPlaying(), playerStore.togglePlay()) : null"
          >
            <template v-if="playerStore.currentTrack">
              <img
                :src="playerStore.currentTrack.cover_art || playerStore.currentTrack.thumbnail || playerStore.currentTrack.artwork || '/static/img/default-cover.jpg'"
                :alt="playerStore.currentTrack.title"
                class="now-playing-album-img"
                :class="{ spinning: playerStore.isPlaying }"
              />
              <div v-if="!playerStore.isPlaying" class="now-playing-album-overlay">
                <i class="fas fa-play"></i>
              </div>
            </template>
            <template v-else>
              <div class="now-playing-empty-art">
                <i class="fas fa-music"></i>
              </div>
            </template>
          </div>
          <div class="now-playing-info">
            <template v-if="playerStore.currentTrack">
              <div class="now-playing-title" :title="displayTitle">{{ displayTitle }}</div>
              <div class="now-playing-secondary">
                <span class="now-playing-artist" :title="displayArtist">{{ displayArtist }}</span>
                <span class="category-pill">
                  <i class="fas fa-music"></i> {{ trackTypeLabel }}
                </span>
              </div>
            </template>
            <template v-else>
              <div class="now-playing-title now-playing-empty-title">Select a track</div>
              <div class="now-playing-artist now-playing-empty-artist">
                Browse <router-link to="/music" class="now-playing-empty-link">music</router-link>,
                <router-link to="/podcasts" class="now-playing-empty-link">podcasts</router-link>, or
                <router-link to="/radio" class="now-playing-empty-link">radio</router-link>
              </div>
            </template>
          </div>
        </div>

        <!-- Center: Transport (Spotify-style) + ±5s seek -->
        <div class="now-playing-transport">
          <button
            type="button"
            class="now-playing-btn now-playing-seek-btn"
            :class="{ disabled: !playerStore.currentTrack }"
            :disabled="!playerStore.currentTrack"
            title="Back 5 seconds"
            @click="playerStore.seekBackward5()"
          >
            <span class="seek-5-label">−5</span>
          </button>
          <button
            type="button"
            class="now-playing-btn"
            :class="{ disabled: !playerStore.currentTrack }"
            :disabled="!playerStore.currentTrack"
            title="Previous"
            @click="playerStore.previous()"
          >
            <i class="fas fa-step-backward"></i>
          </button>
          <button
            type="button"
            class="now-playing-btn now-playing-play-btn"
            :class="{ disabled: !playerStore.currentTrack, loading: playerStore.loading }"
            :disabled="!playerStore.currentTrack"
            :title="playerStore.loading ? 'Loading...' : (playerStore.isPlaying ? 'Pause' : 'Play')"
            @click="onTogglePlay"
          >
            <i v-if="playerStore.loading" class="fas fa-spinner fa-spin"></i>
            <i v-else :class="playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
          </button>
          <button
            type="button"
            class="now-playing-btn"
            :class="{ disabled: !playerStore.currentTrack }"
            :disabled="!playerStore.currentTrack"
            title="Next"
            @click="playerStore.next()"
          >
            <i class="fas fa-step-forward"></i>
          </button>
          <button
            type="button"
            class="now-playing-btn now-playing-seek-btn"
            :class="{ disabled: !playerStore.currentTrack }"
            :disabled="!playerStore.currentTrack"
            title="Forward 5 seconds"
            @click="playerStore.seekForward5()"
          >
            <span class="seek-5-label">+5</span>
          </button>
        </div>

        <!-- Right: Action buttons + master volume -->
        <div class="now-playing-actions-wrap">
          <div class="now-playing-actions">
            <button
              type="button"
              class="now-playing-btn"
              :class="{ active: playerStore.shuffle, disabled: !playerStore.currentTrack }"
              :disabled="!playerStore.currentTrack"
              title="Shuffle"
              @click="playerStore.shuffle = !playerStore.shuffle"
            >
              <i class="fas fa-random"></i>
            </button>
            <button
              type="button"
              class="now-playing-btn"
              :class="{ active: playerStore.repeat, disabled: !playerStore.currentTrack }"
              :disabled="!playerStore.currentTrack"
              title="Repeat"
              @click="playerStore.repeat = !playerStore.repeat"
            >
              <i class="fas fa-redo"></i>
            </button>
            <button
              type="button"
              class="now-playing-btn now-playing-action-btn"
              :class="{ disabled: !playerStore.currentTrack }"
              :disabled="!playerStore.currentTrack"
              title="Boost artist"
              @click="openBoost"
            >
              <i class="fas fa-bolt"></i>
            </button>
            <button
              type="button"
              class="now-playing-btn now-playing-action-btn"
              :class="{ active: isBookmarked, disabled: !playerStore.currentTrack }"
              :disabled="!playerStore.currentTrack"
              title="Bookmark"
              @click="toggleBookmark"
            >
              <i :class="isBookmarked ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
            </button>
            <button
              type="button"
              class="now-playing-btn now-playing-action-btn"
              :class="{ disabled: !playerStore.currentTrack }"
              :disabled="!playerStore.currentTrack"
              title="Add to playlist"
              @click="openAddToPlaylist"
            >
              <i class="fas fa-plus"></i>
            </button>
            <div class="now-playing-queue-wrap">
            <button
              type="button"
              class="now-playing-btn now-playing-action-btn now-playing-queue-btn"
              :class="{ active: showQueue }"
              title="Queue"
              @click="showQueue = !showQueue"
            >
              <i class="fas fa-list"></i>
              <span v-if="playerStore.queue.length" class="queue-badge">{{ playerStore.queue.length }}</span>
            </button>
            <!-- Queue panel -->
            <div v-if="showQueue" class="queue-panel-backdrop" @click="showQueue = false"></div>
            <div
              v-show="showQueue"
              class="now-playing-queue-panel"
              @click.stop
            >
              <div class="queue-header">
                <div class="queue-header-left">
                  <h4>Up Next</h4>
                  <div class="queue-header-actions">
                    <router-link to="/music" class="queue-add-btn" @click="showQueue = false">Add Tracks</router-link>
                    <router-link to="/podcasts" class="queue-add-btn" @click="showQueue = false">Add Podcasts</router-link>
                  </div>
                </div>
                <button
                  v-if="playerStore.queue.length"
                  type="button"
                  class="queue-clear-btn"
                  title="Clear queue"
                  @click="playerStore.clearQueue()"
                >
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
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
                  <button
                    type="button"
                    class="queue-item-remove"
                    title="Remove"
                    @click.stop="playerStore.removeFromQueue(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
              <div v-else class="queue-empty">
                <i class="fas fa-music"></i>
                <p>Queue is empty</p>
                <span>Add tracks to play next</span>
                <div class="queue-empty-actions">
                  <router-link to="/music" class="queue-add-btn" @click="showQueue = false">Add Tracks</router-link>
                  <router-link to="/podcasts" class="queue-add-btn" @click="showQueue = false">Add Podcasts</router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
          <div class="now-playing-volume-wrap">
            <button
              type="button"
              class="now-playing-btn now-playing-volume-btn"
              :title="playerStore.isMuted ? 'Unmute' : 'Mute'"
              @click="playerStore.toggleMute()"
            >
              <i :class="volumeIconClass"></i>
            </button>
            <input
              type="range"
              class="now-playing-volume"
              min="0"
              max="100"
              :value="playerStore.volume"
              @input="playerStore.setVolume(parseInt($event.target.value, 10))"
              title="Volume"
            />
          </div>
        </div>

        <!-- Mobile-only compact controls (Spotify-like) -->
        <div class="now-playing-mobile-shell">
          <div class="now-playing-mobile-controls">
            <button
              type="button"
              class="now-playing-btn"
              :class="{ active: playerStore.shuffle, disabled: !playerStore.currentTrack }"
              :disabled="!playerStore.currentTrack"
              title="Shuffle"
              @click="playerStore.shuffle = !playerStore.shuffle"
            >
              <i class="fas fa-random"></i>
            </button>
            <button
              type="button"
              class="now-playing-btn"
              :class="{ disabled: !playerStore.currentTrack }"
              :disabled="!playerStore.currentTrack"
              title="Previous"
              @click="playerStore.previous()"
            >
              <i class="fas fa-step-backward"></i>
            </button>
            <button
              type="button"
              class="now-playing-btn now-playing-play-btn"
              :class="{ disabled: !playerStore.currentTrack, loading: playerStore.loading }"
              :disabled="!playerStore.currentTrack"
              :title="playerStore.loading ? 'Loading...' : (playerStore.isPlaying ? 'Pause' : 'Play')"
              @click="onTogglePlay"
            >
              <i v-if="playerStore.loading" class="fas fa-spinner fa-spin"></i>
              <i v-else :class="playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
            </button>
            <button
              type="button"
              class="now-playing-btn"
              :class="{ disabled: !playerStore.currentTrack }"
              :disabled="!playerStore.currentTrack"
              title="Next"
              @click="playerStore.next()"
            >
              <i class="fas fa-step-forward"></i>
            </button>
            <button
              type="button"
              class="now-playing-btn"
              :class="{ active: playerStore.repeat, disabled: !playerStore.currentTrack }"
              :disabled="!playerStore.currentTrack"
              title="Repeat"
              @click="playerStore.repeat = !playerStore.repeat"
            >
              <i class="fas fa-redo"></i>
            </button>
          </div>

          <div class="now-playing-mobile-progress">
            <span class="now-playing-mobile-time">{{ mobileCurrentTimeLabel }}</span>
            <div
              class="now-playing-mobile-progress-track"
              ref="mobileSeekRef"
              @click="onMobileSeek"
            >
              <div class="now-playing-mobile-progress-fill" :style="{ width: playerStore.progress + '%' }"></div>
            </div>
            <span class="now-playing-mobile-time">{{ mobileDurationLabel }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePlayerStore } from '../stores/player'
import { useBookmarks } from '../composables/useBookmarks'
import { useHaptics } from '../composables/useNative'
import { useAddToPlaylist } from '../composables/useAddToPlaylist'

const router = useRouter()
const playerStore = usePlayerStore()
const bookmarks = useBookmarks()
const haptics = useHaptics()

const showQueue = ref(false)
const mobileSeekRef = ref(null)

const displayTitle = computed(() => {
  const t = playerStore.currentTrack
  if (!t) return ''
  return t.title || t.name || 'Unknown track'
})

const displayArtist = computed(() => {
  const t = playerStore.currentTrack
  if (!t) return ''
  return t.artist || t.artist_name || t.host || t.artistName || 'Unknown artist'
})

const trackTypeLabel = computed(() => {
  const t = playerStore.currentTrack
  if (!t) return 'Music'
  if (t.type === 'podcast' || t._type === 'podcast') return 'Podcast'
  if (t.type === 'show' || t._type === 'show') return 'Video'
  return 'Music'
})

const isBookmarked = computed(() =>
  playerStore.currentTrack ? bookmarks.isBookmarked(playerStore.currentTrack) : false
)

const volumeIconClass = computed(() => {
  if (playerStore.isMuted) return 'fas fa-volume-mute'
  if (playerStore.volume > 50) return 'fas fa-volume-up'
  if (playerStore.volume > 0) return 'fas fa-volume-down'
  return 'fas fa-volume-off'
})

const mobileCurrentTimeLabel = computed(() => {
  if (!playerStore.currentTrack) return '-:--'
  return formatMiniTime(playerStore.currentTime)
})

const mobileDurationLabel = computed(() => {
  if (!playerStore.currentTrack) return '-:--'
  return formatMiniTime(playerStore.duration)
})

function formatMiniTime(seconds) {
  const value = Number(seconds)
  if (!isFinite(value) || value < 0) return '-:--'
  const m = Math.floor(value / 60)
  const s = Math.floor(value % 60)
  return `${m}:${String(s).padStart(2, '0')}`
}

function onMobileSeek(event) {
  const el = mobileSeekRef.value
  if (!el || !playerStore.duration) return
  const rect = el.getBoundingClientRect()
  const x = Math.max(0, Math.min(rect.width, event.clientX - rect.left))
  const percent = (x / rect.width) * 100
  playerStore.seek(percent)
}

function onTogglePlay() {
  haptics.onPlay()
  playerStore.togglePlay()
}

function toggleBookmark() {
  if (playerStore.currentTrack) {
    bookmarks.toggle(playerStore.currentTrack)
    haptics.onBookmark?.()
  }
}

const addToPlaylist = useAddToPlaylist()
function openAddToPlaylist() {
  if (playerStore.currentTrack) addToPlaylist.open(playerStore.currentTrack)
}

const API_BASE = import.meta.env.VITE_API_BASE || 'https://app.ahoy.ooo'

function openBoost() {
  if (!playerStore.currentTrack) return
  const track = playerStore.currentTrack
  const artistId = encodeURIComponent(String(track.artist_id || track.artistId || track.artist || '').trim())
  window.location.href = `${API_BASE}/checkout?type=boost&artist_id=${artistId}&amount=1`
}

function goToNowPlaying() {
  router.push('/now-playing')
}

function playFromQueue(index) {
  const list = playerStore.queue
  if (list[index]) playerStore.play(list[index])
  showQueue.value = false
}

// Click-outside to close queue: overlay when panel is open
</script>

<style scoped>
.now-playing-queue-wrap {
  position: relative;
}
.queue-panel-backdrop {
  position: fixed;
  inset: 0;
  z-index: 998;
}
.now-playing-queue-panel {
  z-index: 1000;
}

.now-playing-mobile-shell {
  display: none;
}

@media (max-width: 768px) {
  .now-playing-container {
    display: none;
  }

  .now-playing-mobile-shell {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 10px;
    height: 100%;
    padding: 10px 16px 12px;
  }

  .now-playing-mobile-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
  }

  .now-playing-mobile-progress {
    display: grid;
    grid-template-columns: 44px minmax(0, 1fr) 44px;
    align-items: center;
    gap: 10px;
  }

  .now-playing-mobile-time {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.65);
    text-align: center;
    font-variant-numeric: tabular-nums;
  }

  .now-playing-mobile-progress-track {
    position: relative;
    height: 6px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.24);
    overflow: hidden;
    cursor: pointer;
  }

  .now-playing-mobile-progress-fill {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.85);
    border-radius: 999px;
    width: 0%;
  }
}
</style>
