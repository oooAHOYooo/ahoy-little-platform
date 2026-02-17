<template>
  <div id="compact-footer" class="compact-footer">
    <div class="compact-footer-content">
      <div class="compact-footer-time-weather">
        <span class="compact-time">{{ currentTime }}</span>
      </div>
      <div class="compact-footer-ticker">
        <div class="ticker-wrapper" ref="tickerWrapperRef">
          <div
            class="ticker-content"
            ref="tickerContentRef"
            :style="{ transform: `translateX(${tickerOffset}px)` }"
          >
            <span
              v-for="(item, index) in announcements"
              :key="index"
              class="ticker-item"
            >{{ item }}</span>
            <!-- Duplicate for seamless loop -->
            <span
              v-for="(item, index) in announcements"
              :key="'dup-' + index"
              class="ticker-item"
            >{{ item }}</span>
          </div>
        </div>
      </div>
      <div class="compact-footer-quicklinks">
        <router-link to="/music" class="quicklink">Music</router-link>
        <span class="quicklink-sep">•</span>
        <router-link to="/videos" class="quicklink">Videos</router-link>
        <span class="quicklink-sep">•</span>
        <router-link to="/artists" class="quicklink">Artists</router-link>
        <span class="quicklink-sep">•</span>
        <router-link to="/my-saves" class="quicklink">Saved</router-link>
      </div>
      <p class="compact-footer-refresh mobile-only" style="margin-top: 6px; font-size: 0.75rem; opacity: 0.8;">
        Having trouble? <a href="/refresh" style="color: rgba(255,255,255,0.9); text-decoration: underline;">Get the latest version</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const announcements = [
  'Welcome to Ahoy Indie Media',
  'Discover new indie music and videos',
  'Create playlists and save your favorites',
  'Follow your favorite artists',
  'Explore videos and events',
]

const currentTime = ref('')
const tickerOffset = ref(0)
const tickerSpeed = 0.5
const tickerWrapperRef = ref(null)
const tickerContentRef = ref(null)

let timeInterval = null
let tickerAnimationId = null

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  })
}

function startTimeUpdate() {
  updateTime()
  if (timeInterval) return
  timeInterval = setInterval(() => {
    if (document.visibilityState === 'visible') {
      updateTime()
    }
  }, 1000)
}

function stopTimeUpdate() {
  if (timeInterval) {
    clearInterval(timeInterval)
    timeInterval = null
  }
}

function startTicker() {
  const tickerContent = tickerContentRef.value
  const tickerWrapper = tickerWrapperRef.value
  if (!tickerContent || !tickerWrapper) return

  const animate = () => {
    tickerOffset.value -= tickerSpeed
    const contentWidth = tickerContent.scrollWidth / 2
    if (Math.abs(tickerOffset.value) >= contentWidth) {
      tickerOffset.value = 0
    }
    tickerAnimationId = requestAnimationFrame(animate)
  }
  tickerAnimationId = requestAnimationFrame(animate)
}

function stopTicker() {
  if (tickerAnimationId) {
    cancelAnimationFrame(tickerAnimationId)
    tickerAnimationId = null
  }
}

function onVisibilityChange() {
  if (document.visibilityState === 'visible') {
    updateTime()
    startTimeUpdate()
  } else {
    stopTimeUpdate()
  }
}

onMounted(() => {
  updateTime()
  if (document.visibilityState === 'visible') {
    startTimeUpdate()
  }
  document.addEventListener('visibilitychange', onVisibilityChange)
  setTimeout(startTicker, 300)
})

onUnmounted(() => {
  stopTimeUpdate()
  stopTicker()
  document.removeEventListener('visibilitychange', onVisibilityChange)
})
</script>
