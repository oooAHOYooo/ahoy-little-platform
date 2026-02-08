<template>
  <div
    class="pull-refresh-wrapper"
    ref="wrapper"
    @touchstart.passive="onTouchStart"
    @touchmove.passive="onTouchMove"
    @touchend.passive="onTouchEnd"
  >
    <!-- Pull indicator -->
    <div class="pull-indicator" :class="{ active: pulling, refreshing }" :style="{ transform: `translateY(${indicatorY}px)`, opacity: indicatorOpacity }">
      <i :class="refreshing ? 'fas fa-spinner fa-spin' : 'fas fa-arrow-down'" :style="{ transform: readyToRefresh ? 'rotate(180deg)' : '' }"></i>
      <span>{{ refreshing ? 'Refreshing...' : readyToRefresh ? 'Release to refresh' : 'Pull to refresh' }}</span>
    </div>

    <!-- Content -->
    <div class="pull-content" :style="{ transform: `translateY(${contentY}px)` }">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['refresh'])

const wrapper = ref(null)
const pulling = ref(false)
const refreshing = ref(false)
const startY = ref(0)
const pullDistance = ref(0)

const THRESHOLD = 70
const MAX_PULL = 120

const contentY = computed(() => refreshing.value ? THRESHOLD * 0.6 : Math.min(pullDistance.value * 0.5, MAX_PULL * 0.5))
const indicatorY = computed(() => refreshing.value ? 0 : Math.min(pullDistance.value * 0.4, MAX_PULL * 0.4) - 40)
const indicatorOpacity = computed(() => refreshing.value ? 1 : Math.min(pullDistance.value / THRESHOLD, 1))
const readyToRefresh = computed(() => pullDistance.value >= THRESHOLD)

function isAtTop() {
  // Check if page is scrolled to top
  return window.scrollY <= 0
}

function onTouchStart(e) {
  if (!isAtTop() || refreshing.value) return
  startY.value = e.touches[0].clientY
  pulling.value = true
}

function onTouchMove(e) {
  if (!pulling.value || refreshing.value) return
  const delta = e.touches[0].clientY - startY.value
  if (delta > 0) {
    pullDistance.value = delta
  } else {
    pulling.value = false
    pullDistance.value = 0
  }
}

function onTouchEnd() {
  if (!pulling.value) return
  if (readyToRefresh.value) {
    refreshing.value = true
    pullDistance.value = 0
    emit('refresh', done)
  } else {
    pullDistance.value = 0
  }
  pulling.value = false
}

function done() {
  refreshing.value = false
  pullDistance.value = 0
}
</script>

<style scoped>
.pull-refresh-wrapper {
  position: relative;
  overflow: visible;
}
.pull-indicator {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  z-index: 10;
  transition: opacity 0.2s;
}
.pull-indicator i {
  transition: transform 0.2s;
}
.pull-indicator.refreshing {
  color: var(--accent-primary, #6ddcff);
}
.pull-content {
  transition: transform 0.25s ease;
}
</style>
