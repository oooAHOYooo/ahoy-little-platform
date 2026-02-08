<template>
  <div v-if="addToPlaylist.showModal.value" class="modal-overlay" @click.self="addToPlaylist.close()">
    <div class="modal add-to-playlist-modal" role="dialog" aria-modal="true" aria-label="Add to playlist">
      <div class="modal-header">
        <h3>Add to playlist</h3>
        <button type="button" class="modal-close" aria-label="Close" @click="addToPlaylist.close()">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div v-if="track" class="modal-track">
        {{ track.title }}
        <span class="modal-track-artist">{{ track.artist || track.host }}</span>
      </div>
      <div v-if="!addToPlaylist.auth.isLoggedIn.value" class="modal-guest">
        <p>Sign in to add tracks to playlists.</p>
        <router-link to="/login" class="btn-primary" @click="addToPlaylist.close()">Sign in</router-link>
      </div>
      <div v-else class="modal-list">
        <div v-if="loading" class="modal-loading"><i class="fas fa-spinner fa-spin"></i> Loading playlists…</div>
        <template v-else-if="playlists.length">
          <button
            v-for="p in playlists"
            :key="p.id"
            type="button"
            class="playlist-row"
            @click="addTo(p.id)"
          >
            <i class="fas fa-list-ul"></i>
            <span>{{ p.name }}</span>
          </button>
        </template>
        <p v-else class="modal-empty">No playlists yet. <router-link to="/playlists" @click="addToPlaylist.close()">Create one</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useAddToPlaylist } from '../composables/useAddToPlaylist'

const addToPlaylist = useAddToPlaylist()
const playlists = ref([])
const loading = ref(false)

const track = computed(() => addToPlaylist.trackToAdd.value)

function toMediaType(item) {
  const t = (item?.type || item?._type || 'track').toLowerCase()
  if (t === 'artist') return 'artist'
  if (t === 'show' || t === 'video') return 'show'
  if (t === 'podcast' || t === 'episode') return 'clip'
  return 'music'
}

async function loadPlaylists() {
  if (!addToPlaylist.auth.isLoggedIn.value) return
  loading.value = true
  try {
    playlists.value = await addToPlaylist.playlistsApi.list()
  } finally {
    loading.value = false
  }
}

async function addTo(playlistId) {
  const t = track.value
  if (!t) return
  const mediaId = String(t.id ?? t.slug ?? '')
  const mediaType = toMediaType(t)
  try {
    await addToPlaylist.playlistsApi.addItem(playlistId, mediaId, mediaType)
    window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Added to playlist', type: 'success' } }))
    addToPlaylist.close()
  } catch {
    window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Failed to add', type: 'error' } }))
  }
}

watch(() => addToPlaylist.showModal.value, (open) => {
  if (open) loadPlaylists()
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
}
.add-to-playlist-modal {
  width: 100%;
  max-width: 360px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: rgba(20, 20, 28, 0.98);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}
.modal-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 20px;
  cursor: pointer;
  padding: 4px;
}
.modal-track {
  padding: 12px 20px;
  font-size: 14px;
  color: var(--text-primary);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.modal-track-artist {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}
.modal-guest {
  padding: 24px 20px;
  text-align: center;
}
.modal-guest p {
  margin: 0 0 16px;
  color: var(--text-secondary);
}
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  background: var(--accent-primary, #6ddcff);
  color: #111;
  text-decoration: none;
}
.modal-list {
  padding: 12px 0;
  overflow-y: auto;
  flex: 1;
}
.modal-loading, .modal-empty {
  padding: 20px;
  text-align: center;
  color: var(--text-secondary);
}
.modal-empty a {
  color: var(--accent-primary);
  text-decoration: none;
}
.playlist-row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 20px;
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 15px;
  text-align: left;
  cursor: pointer;
  transition: background 0.2s;
}
.playlist-row:hover {
  background: rgba(255,255,255,0.06);
}
.playlist-row i {
  color: var(--text-secondary);
}
</style>
