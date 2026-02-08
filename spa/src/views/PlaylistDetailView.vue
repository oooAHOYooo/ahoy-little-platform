<template>
  <div class="playlist-detail-page">
    <div class="unified-header">
      <div class="header-content">
        <h1>{{ playlist?.name || 'Playlist' }}</h1>
        <span class="header-count">{{ items.length }} items</span>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="!playlist" class="error">Playlist not found.</div>

    <div v-else class="playlist-items">
      <div
        v-for="item in items"
        :key="item.id"
        class="playlist-item-row"
      >
        <span class="item-media">{{ item.media_type }}: {{ item.media_id }}</span>
        <button
          type="button"
          class="item-remove"
          aria-label="Remove"
          @click="removeItem(item.id)"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
      <p v-if="!items.length" class="empty">No tracks yet. Add from Music or Podcasts.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePlaylists } from '../composables/usePlaylists'

const route = useRoute()
const playlistsApi = usePlaylists()
const playlist = ref(null)
const items = ref([])
const loading = ref(true)

async function load() {
  const id = route.params.id
  if (!id) return
  loading.value = true
  try {
    playlist.value = await playlistsApi.get(Number(id))
    items.value = await playlistsApi.listItems(Number(id))
  } finally {
    loading.value = false
  }
}

async function removeItem(itemId) {
  try {
    await playlistsApi.removeItem(Number(route.params.id), itemId)
    items.value = items.value.filter((i) => i.id !== itemId)
    window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Removed', type: 'success' } }))
  } catch {
    //
  }
}

onMounted(load)
watch(() => route.params.id, load)
</script>

<style scoped>
.playlist-detail-page {
  padding: 16px 20px 100px;
}
.loading, .error, .empty {
  color: var(--text-secondary);
  padding: 24px;
}
.playlist-items {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.playlist-item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(255,255,255,0.06);
  border-radius: 12px;
}
.item-media {
  font-size: 14px;
  color: var(--text-primary);
}
.item-remove {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px;
}
.item-remove:hover {
  color: #ff6b6b;
}
</style>
