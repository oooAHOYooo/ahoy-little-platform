<template>
  <div class="home-page">
    <div class="unified-header bookmarks-subheader">
      <div class="header-content">
        <h1>Saved</h1>
        <span class="header-count">{{ savedItems.length }} items</span>
      </div>
    </div>

    <div class="podcasts-section" v-if="savedItems.length">
      <div class="episode-list">
        <div class="episode-row" v-for="item in savedItems" :key="item.id || item.slug">
          <div class="episode-art">
            <img :src="item.cover_art || item.thumbnail || item.artwork || '/static/img/default-cover.jpg'" :alt="item.title" loading="lazy" />
          </div>
          <div class="episode-meta">
            <div class="episode-title">{{ item.title }}</div>
            <div class="episode-show" v-if="item.artist">{{ item.artist }}</div>
            <div class="episode-show" v-if="item.type">{{ item.type }}</div>
          </div>
          <div class="episode-actions">
            <button @click="removeBookmark(item)" class="episode-action-btn" title="Remove">
              <i class="fas fa-bookmark"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="podcasts-section" v-else>
      <div class="empty-state" style="text-align:center;padding:40px 20px;color:rgba(255,255,255,0.5)">
        <i class="fas fa-bookmark" style="font-size:48px;margin-bottom:16px;display:block"></i>
        <p>No saved items yet</p>
        <p style="font-size:13px;margin-top:8px">Bookmark music, shows, and podcasts to find them here</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const savedItems = ref([])

function loadBookmarks() {
  try {
    const raw = localStorage.getItem('ahoy.bookmarks.v1')
    if (raw) {
      const data = JSON.parse(raw)
      savedItems.value = Object.values(data)
    }
  } catch (e) {
    savedItems.value = []
  }
}

function removeBookmark(item) {
  try {
    const raw = localStorage.getItem('ahoy.bookmarks.v1')
    if (raw) {
      const data = JSON.parse(raw)
      const key = item.id || item.slug
      delete data[key]
      localStorage.setItem('ahoy.bookmarks.v1', JSON.stringify(data))
      savedItems.value = Object.values(data)
    }
  } catch (e) { /* ignore */ }
}

onMounted(() => {
  loadBookmarks()
  window.addEventListener('bookmarks:changed', loadBookmarks)
})
</script>
