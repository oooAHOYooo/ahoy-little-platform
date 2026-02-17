<template>
  <div class="now-playing-wrapper" :class="{ 'has-player': !!playerStore.currentTrack, 'collapsed': collapse.isPlayerCollapsed.value, 'ejecting': ejecting }">
    <div
      class="now-playing-glass now-playing-sticky"
      :class="{ 'now-playing-is-playing': playerStore.currentTrack && playerStore.isPlaying }"
    >
      <!-- Eject (when track loaded) — left of collapse button -->
      <button
        v-if="playerStore.currentTrack"
        type="button"
        class="eject-btn-top"
        title="Eject"
        aria-label="Eject track"
        @click="onEject"
      >
        <i class="fas fa-eject"></i>
      </button>
      <!-- Minimize built into the bar (mobile only) -->
      <button
        type="button"
        class="minimize-btn mobile-only"
        :title="collapse.isPlayerCollapsed.value ? 'Expand player' : 'Minimize player'"
        aria-label="Minimize player"
        @click="collapse.togglePlayer"
      >
        <i :class="collapse.isPlayerCollapsed.value ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
      </button>
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
              <div
                class="now-playing-title now-playing-title-link"
                :title="displayTitle"
                @click="goToNowPlaying"
              >{{ displayTitle }}</div>
              <div class="now-playing-secondary">
                <span
                  class="now-playing-artist now-playing-artist-link"
                  :title="displayArtist"
                  @click="goToNowPlaying"
                >{{ displayArtist }}</span>
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
              class="now-playing-btn now-playing-action-btn now-playing-volume-mobile-btn"
              :title="playerStore.isMuted ? 'Unmute' : 'Volume'"
              @click="playerStore.toggleMute()"
            >
              <i :class="volumeIconClass"></i>
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
import { useMobileCollapse } from '../composables/useMobileCollapse'
const router = useRouter()
const playerStore = usePlayerStore()
const bookmarks = useBookmarks()
const haptics = useHaptics()
const collapse = useMobileCollapse()

const showQueue = ref(false)
const ejecting = ref(false)

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

function onEject() {
  if (!playerStore.currentTrack || ejecting.value) return
  haptics.onPlay?.()
  ejecting.value = true
  setTimeout(() => {
    playerStore.eject()
    ejecting.value = false
  }, 280)
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

/* Minimize button built into the now-playing bar */
.now-playing-glass {
  position: relative;
}

/* Eject: top-right, left of minimize */
.eject-btn-top {
  position: absolute;
  top: 6px;
  right: 58px;
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.5);
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 5;
  -webkit-tap-highlight-color: transparent;
  transition: background 0.2s ease, color 0.2s ease;
}

.eject-btn-top:hover,
.eject-btn-top:active {
  background: rgba(255, 255, 255, 0.14);
  color: rgba(255, 255, 255, 0.85);
}

.minimize-btn {
  position: absolute;
  top: 6px;
  right: 10px;
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.4);
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 5;
  -webkit-tap-highlight-color: transparent;
  transition: background 0.2s ease, color 0.2s ease;
}

.minimize-btn:hover,
.minimize-btn:active {
  background: rgba(255, 255, 255, 0.14);
  color: rgba(255, 255, 255, 0.6);
}

/* Title / artist: click to open Now Playing */
.now-playing-title-link,
.now-playing-artist-link {
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.now-playing-title-link:hover,
.now-playing-artist-link:hover {
  opacity: 0.9;
}

/* Eject: Nintendo cartridge pop — track “pops out” then clears */
.now-playing-wrapper.ejecting .now-playing-left {
  animation: cartridge-eject 0.28s ease-out forwards;
}

@keyframes cartridge-eject {
  0% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
  40% {
    transform: translateY(2px) scale(1.02);
    opacity: 1;
  }
  100% {
    transform: translateY(14px) scale(0.92);
    opacity: 0.5;
  }
}

/* Collapsed state: handled in app.css on mobile (strip on top of dock). Desktop never collapsed. */
.now-playing-wrapper {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@media (min-width: 769px) {
  .minimize-btn.mobile-only {
    display: none;
  }
}

@media (max-width: 768px) {
  .now-playing-wrapper.collapsed .eject-btn-top {
    display: none;
  }
}
</style>
