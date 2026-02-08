<template>
  <div class="playlists-page">
    <div class="unified-header">
      <div class="header-content">
        <h1>Playlists</h1>
        <span class="header-count">{{ playlists.length }} playlists</span>
      </div>
    </div>

    <div v-if="!auth.isLoggedIn.value" class="playlists-guest">
      <p>Sign in to create and manage playlists.</p>
      <router-link to="/login" class="account-btn primary">Sign in</router-link>
    </div>

    <template v-else>
      <div class="playlists-actions">
        <input
          v-model="newName"
          type="text"
          placeholder="New playlist name"
          class="playlist-input"
          @keyup.enter="createPlaylist"
        />
        <button type="button" class="playlist-btn primary" :disabled="!newName.trim() || playlistsApi.loading.value" @click="createPlaylist">
          <i v-if="playlistsApi.loading.value" class="fas fa-spinner fa-spin"></i>
          <i v-else class="fas fa-plus"></i>
          Create
        </button>
      </div>

      <div v-if="playlistsApi.error.value" class="playlists-error">{{ playlistsApi.error.value }}</div>

      <div class="playlists-list">
        <router-link
          v-for="p in playlists"
          :key="p.id"
          :to="`/playlists/${p.id}`"
          class="playlist-card"
        >
          <i class="fas fa-list-ul playlist-icon"></i>
          <div class="playlist-info">
            <span class="playlist-name">{{ p.name }}</span>
          </div>
          <i class="fas fa-chevron-right"></i>
        </router-link>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'
import { usePlaylists } from '../composables/usePlaylists'

const auth = useAuth()
const playlistsApi = usePlaylists()
const playlists = ref([])
const newName = ref('')

async function load() {
  playlists.value = await playlistsApi.list()
}

async function createPlaylist() {
  const name = newName.value.trim()
  if (!name) return
  try {
    const created = await playlistsApi.create(name)
    playlists.value = [...playlists.value, { id: created.id, name: created.name }]
    newName.value = ''
    window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Playlist created', type: 'success' } }))
  } catch {
    // error in composable
  }
}

onMounted(load)
</script>

<style scoped>
.playlists-page {
  padding: 16px 20px 100px;
}
.playlists-guest {
  text-align: center;
  padding: 40px 20px;
}
.playlists-guest p {
  color: var(--text-secondary);
  margin-bottom: 16px;
}
.account-btn.primary {
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
.playlists-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
.playlist-input {
  flex: 1;
  padding: 10px 14px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 15px;
}
.playlist-btn {
  padding: 10px 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.playlist-btn.primary {
  background: var(--accent-primary, #6ddcff);
  color: #111;
}
.playlists-error {
  color: #ff6b6b;
  font-size: 14px;
  margin-bottom: 12px;
}
.playlists-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.playlist-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: rgba(20, 20, 28, 0.85);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  text-decoration: none;
  color: inherit;
  transition: background 0.2s;
}
.playlist-card:hover {
  background: rgba(255,255,255,0.06);
}
.playlist-icon {
  font-size: 20px;
  color: var(--text-secondary);
}
.playlist-info {
  flex: 1;
  min-width: 0;
}
.playlist-name {
  font-weight: 600;
  color: var(--text-primary);
}
</style>
