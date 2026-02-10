<template>
  <Teleport to="body">
    <Transition name="slide-up">
      <div v-if="visible" class="guest-save-prompt" role="dialog" aria-label="Create account to sync saves">
        <div class="guest-save-prompt-inner">
          <p class="guest-save-text">
            <i class="fas fa-bookmark"></i>
            Saved to this device. Create an account to sync everywhere.
          </p>
          <div class="guest-save-actions">
            <button type="button" class="guest-save-dismiss" @click="dismiss">Not now</button>
            <router-link to="/login?signup=1" class="guest-save-cta" @click="dismiss">Create account</router-link>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const visible = ref(false)

function show() {
  visible.value = true
}

function dismiss() {
  visible.value = false
}

function onGuestSaved() {
  show()
}

onMounted(() => {
  window.addEventListener('ahoy:guest-saved', onGuestSaved)
})
onUnmounted(() => {
  window.removeEventListener('ahoy:guest-saved', onGuestSaved)
})
</script>

<style scoped>
.guest-save-prompt {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  padding: 12px 16px;
  padding-bottom: max(12px, env(safe-area-inset-bottom));
  background: rgba(20, 20, 28, 0.98);
  border-top: 1px solid rgba(255,255,255,0.12);
  box-shadow: 0 -4px 24px rgba(0,0,0,0.3);
}
.guest-save-prompt-inner {
  max-width: 480px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.guest-save-text {
  margin: 0;
  font-size: 14px;
  color: var(--text-primary, #fff);
  display: flex;
  align-items: center;
  gap: 8px;
}
.guest-save-text i {
  color: var(--accent-primary, #6ddcff);
}
.guest-save-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.guest-save-dismiss {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  padding: 8px 12px;
}
.guest-save-dismiss:hover {
  color: var(--text-primary);
}
.guest-save-cta {
  display: inline-flex;
  align-items: center;
  padding: 10px 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  background: var(--accent-primary, #6ddcff);
  color: #111;
  text-decoration: none;
}
.guest-save-cta:hover {
  filter: brightness(1.1);
}
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.25s ease, opacity 0.2s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
