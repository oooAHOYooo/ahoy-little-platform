<template>
  <div class="offline-page">
    <div class="offline-container">
      <img src="/static/img/ahoy_logo.png" alt="Ahoy" class="offline-logo" @error="logoError = true" />
      <span v-if="logoError" class="offline-logo-text">Ahoy</span>
      <h1>You're Offline</h1>
      <p>Connect to the internet to browse new content. Pages you've visited before will load from cache.</p>
      <button type="button" class="offline-btn" @click="retry">Try Again</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const logoError = ref(false)

function retry() {
  window.location.reload()
}
</script>

<style scoped>
.offline-page {
  min-height: 100vh;
  background: #111;
  color: #fff;
  font-family: system-ui, -apple-system, sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
}
.offline-container { max-width: 400px; }
.offline-logo { width: 80px; height: 80px; margin-bottom: 1.5rem; border-radius: 16px; }
.offline-logo-text { display: block; font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem; }
.offline-page h1 { font-size: 1.4rem; margin-bottom: 0.5rem; }
.offline-page p { color: #aaa; line-height: 1.6; font-size: 0.95rem; margin: 0 0 1rem; }
.offline-btn {
  background: #ff6b35;
  color: #fff;
  border: none;
  padding: 12px 28px;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  font-weight: 600;
}
.offline-btn:active { opacity: 0.8; }
</style>
