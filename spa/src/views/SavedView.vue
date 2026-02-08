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
            <div class="episode-show" v-if="item.type" style="opacity:0.6;font-size:11px">{{ item.type }}</div>
          </div>
          <div class="episode-actions">
            <button
              v-if="item.audio_url || item.url"
              @click="playItem(item)"
              class="episode-btn"
              title="Play"
            >
              <i :class="playerStore.currentTrack?.id === item.id && playerStore.isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
            </button>
            <button @click="bookmarkHelper.remove(item)" class="episode-btn" title="Remove" style="color:var(--accent-primary,#6ddcff)">
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
import { computed } from 'vue'
import { useBookmarks } from '../composables/useBookmarks'
import { usePlayerStore } from '../stores/player'

const bookmarkHelper = useBookmarks()
const playerStore = usePlayerStore()

const savedItems = computed(() => Object.values(bookmarkHelper.bookmarks.value))

function playItem(item) {
  if (playerStore.currentTrack?.id === item.id && playerStore.isPlaying) {
    playerStore.pause()
  } else {
    playerStore.play(item)
  }
}
</script>
