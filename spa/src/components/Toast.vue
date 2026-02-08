<template>
  <Teleport to="body">
    <TransitionGroup name="toast" tag="div" class="toast-container">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast-item"
        :class="toast.type"
      >
        <i :class="iconFor(toast.type)" class="toast-icon"></i>
        <span class="toast-message">{{ toast.message }}</span>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const toasts = ref([])
let nextId = 0

function iconFor(type) {
  switch (type) {
    case 'success': return 'fas fa-check-circle'
    case 'error': return 'fas fa-exclamation-circle'
    case 'bookmark': return 'fas fa-bookmark'
    case 'share': return 'fas fa-share-alt'
    case 'play': return 'fas fa-play'
    default: return 'fas fa-info-circle'
  }
}

function show(message, type = 'info', durationMs = 2500) {
  const id = ++nextId
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, durationMs)
}

// Expose globally so any component can trigger a toast
defineExpose({ show })

// Also make it available via a custom event for non-component code
if (typeof window !== 'undefined') {
  window.addEventListener('ahoy:toast', (e) => {
    const { message, type, duration } = e.detail || {}
    show(message || '', type, duration)
  })
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: env(safe-area-inset-top, 12px);
  left: 16px;
  right: 16px;
  z-index: 100000;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
  padding-top: 12px;
}
.toast-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  background: rgba(20, 20, 28, 0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  pointer-events: auto;
}
.toast-icon { font-size: 16px; flex-shrink: 0; }
.toast-item.success .toast-icon { color: #4ade80; }
.toast-item.error .toast-icon { color: #f87171; }
.toast-item.bookmark .toast-icon { color: #6ddcff; }
.toast-item.share .toast-icon { color: #a78bfa; }
.toast-item.play .toast-icon { color: #6ddcff; }
.toast-message { flex: 1; }

/* Transition */
.toast-enter-active { transition: all 0.3s ease; }
.toast-leave-active { transition: all 0.25s ease; }
.toast-enter-from { opacity: 0; transform: translateY(-20px) scale(0.95); }
.toast-leave-to { opacity: 0; transform: translateY(-10px) scale(0.98); }
</style>
