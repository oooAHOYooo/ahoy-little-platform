<template>
  <div class="tv-container">
    <!-- Subpage hero (same as Flask) -->
    <section class="podcasts-hero">
      <div class="podcasts-hero-inner">
        <h1>
          <i class="fas fa-tv" aria-hidden="true"></i>
          Live TV
        </h1>
        <p>Channel surf and watch live programming.</p>
      </div>
    </section>

    <div class="video-spotlight">
      <div class="spotlight-grid">
        <div class="spotlight-left">
          <!-- Hero video player -->
          <div class="panelstream-player hero-player">
            <video
              ref="videoEl"
              controls
              playsinline
              webkit-playsinline
              muted
              @play="isPlaying = true"
              @pause="isPlaying = false"
            ></video>
            <div class="video-header">
              <span class="now-playing-label">Now Playing</span>
              <span class="channel-name-label" aria-live="polite">{{ currentChannel?.name || 'Channel —' }}</span>
            </div>
            <div class="hero-glass"></div>
          </div>

          <!-- Channel remote -->
          <div class="channel-remote remote-below" aria-label="Channel Controls">
            <button type="button" class="remote-btn" title="Play/Pause" @click="togglePlay">
              <i :class="isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
            </button>
            <button type="button" class="remote-btn" title="Mute" @click="toggleMute">
              <i :class="isMuted ? 'fas fa-volume-mute' : 'fas fa-volume-up'"></i>
            </button>
            <button type="button" class="remote-btn" title="Fullscreen" @click="toggleFullscreen">
              <i class="fas fa-expand"></i>
            </button>
            <button type="button" class="remote-btn" title="Channel Up" @click="channelUp">
              <i class="fas fa-chevron-up"></i>
            </button>
            <button type="button" class="remote-btn" title="Channel Down" @click="channelDown">
              <i class="fas fa-chevron-down"></i>
            </button>
          </div>

          <!-- Playing now bar -->
          <div class="playing-now glass">
            <img :src="nowThumb" alt="" class="playing-now-thumb" />
            <div class="now-col">
              <div class="np-title">{{ nowTitle }}</div>
              <div class="np-sub">{{ nowMeta }}</div>
            </div>
            <div class="next-col">
              <div class="np-label">Up Next</div>
              <div class="np-next">{{ upNextTitle }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Channel selector (same as Flask) -->
    <div id="channel-selector">
      <template v-if="loading">
        <div v-for="i in 4" :key="'skeleton-' + i" class="channel-button" style="pointer-events:none">
          <div class="skeleton" style="height:20px;width:70%;margin-bottom:8px"></div>
          <div class="skeleton" style="height:14px;width:50%"></div>
        </div>
      </template>
      <button
        v-else
        v-for="(ch, idx) in channels"
        :key="ch.id"
        type="button"
        class="channel-button"
        :class="{ active: currentChannelIndex === idx }"
        @click="selectChannel(idx)"
      >
        <div class="channel-button-name">{{ ch.name }}</div>
        <div class="channel-button-next">{{ firstItemTitle(ch) }}</div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'

const videoEl = ref(null)
const channels = ref([])
const currentChannelIndex = ref(0)
const loading = ref(true)
const isPlaying = ref(false)
const isMuted = ref(true)
const nowTitle = ref('Select a program')
const nowMeta = ref('—')
const nowThumb = ref('/static/img/default-cover.jpg')
const upNextTitle = ref('—')

const currentChannel = computed(() => channels.value[currentChannelIndex.value] || null)

function firstItemTitle(ch) {
  if (!ch?.items?.length) return '—'
  const t = ch.items[0].title
  return (t && String(t).trim()) || '—'
}

function getVideoUrl(item) {
  return item?.video_url || item?.mp4_link || item?.trailer_url || ''
}

function selectChannel(idx) {
  currentChannelIndex.value = idx
  const ch = channels.value[idx]
  if (!ch) return
  const first = ch.items?.[0]
  const src = first ? getVideoUrl(first) : ''
  if (videoEl.value) {
    videoEl.value.pause()
    if (src) {
      videoEl.value.src = src
      videoEl.value.load()
      videoEl.value.muted = false
      isMuted.value = false
      videoEl.value.play().catch(() => {})
      nowTitle.value = first.title || '—'
      nowMeta.value = first.category || (first.description && first.description.slice(0, 60)) || '—'
      nowThumb.value = first.thumbnail || '/static/img/default-cover.jpg'
    } else {
      videoEl.value.removeAttribute('src')
      nowTitle.value = 'Select a program'
      nowMeta.value = '—'
      nowThumb.value = '/static/img/default-cover.jpg'
    }
  }
  const nextItem = ch.items?.[1]
  upNextTitle.value = nextItem?.title ? String(nextItem.title).trim() : '—'
}

function togglePlay() {
  if (!videoEl.value) return
  if (isPlaying.value) videoEl.value.pause()
  else videoEl.value.play().catch(() => {})
}

function toggleMute() {
  if (!videoEl.value) return
  isMuted.value = !isMuted.value
  videoEl.value.muted = isMuted.value
}

function toggleFullscreen() {
  if (!videoEl.value) return
  if (!document.fullscreenElement) {
    videoEl.value.requestFullscreen?.()?.catch(() => {})
  } else {
    document.exitFullscreen?.()
  }
}

function channelUp() {
  const next = (currentChannelIndex.value - 1 + channels.value.length) % channels.value.length
  selectChannel(next)
}

function channelDown() {
  const next = (currentChannelIndex.value + 1) % channels.value.length
  selectChannel(next)
}

onMounted(async () => {
  loading.value = true
  try {
    const data = await apiFetchCached('/api/live-tv/channels')
    channels.value = data.channels || []
    channels.value.forEach((c) => {
      if (!Array.isArray(c.items)) c.items = []
    })
    if (channels.value.length) selectChannel(0)
  } catch {
    channels.value = []
  }
  loading.value = false
})
</script>
