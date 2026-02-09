<template>
  <div class="settings-page">
    <div class="settings-container">
      <!-- Subpage hero (same as Flask subpage_hero) -->
      <section class="podcasts-hero settings-page-header">
        <div class="podcasts-hero-inner">
          <h1>
            <i class="fas fa-cog" aria-hidden="true"></i>
            Settings
          </h1>
          <p>Customize your Ahoy experience.</p>
        </div>
      </section>

      <!-- Desktop header -->
      <div class="settings-header desktop-only">
        <div class="settings-header-icon">
          <i class="fas fa-cog"></i>
        </div>
        <h1>Settings</h1>
        <p>Customize your Ahoy experience</p>
      </div>

      <div class="settings-content">
        <!-- Account section -->
        <div class="settings-section neu-card">
          <h2><i class="fas fa-user"></i> Account</h2>
          <template v-if="auth.isLoggedIn.value">
            <div class="settings-profile">
              <span class="settings-label">Logged in as</span>
              <span class="settings-value">{{ auth.user.value?.email }}</span>
            </div>
            <div class="settings-links">
              <router-link to="/account" class="settings-link">
                <i class="fas fa-user-circle"></i>
                Account &amp; wallet
              </router-link>
              <router-link to="/my-saves" class="settings-link">
                <i class="fas fa-bookmark"></i>
                Saved
              </router-link>
            </div>
            <button type="button" class="neu-btn neu-btn-secondary logout-btn" @click="onLogout">
              <i class="fas fa-sign-out-alt"></i>
              Sign out
            </button>
          </template>
          <div v-else class="settings-guest">
            <p>Sign in to manage your preferences.</p>
            <router-link to="/login" class="neu-btn neu-btn-primary">Sign in</router-link>
          </div>
        </div>

        <!-- Audio Settings -->
        <div class="settings-section neu-card">
          <h2><i class="fas fa-volume-up"></i> Audio</h2>
          <div class="settings-grid">
            <div class="setting-item">
              <label>Master Volume</label>
              <div class="dial-container">
                <div
                  ref="dialEl"
                  class="neu-dial"
                  :style="{ transform: `rotate(${audioSettings.masterVolume * 1.8 - 90}deg)` }"
                  @mousedown.prevent="startDialDrag($event, 'masterVolume')"
                  @touchstart.prevent="startDialDrag($event, 'masterVolume')"
                >
                  <div class="dial-handle"></div>
                </div>
                <span class="dial-value">{{ Math.round(audioSettings.masterVolume) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Experimental Features -->
        <div class="settings-section neu-card experimental-section">
          <h2><i class="fas fa-flask"></i> Experimental</h2>
          <p class="experimental-disclaimer">These features are still in development and may change or be removed.</p>
          <div class="experimental-grid">
            <a href="/focus" class="experimental-card neu-card-inset">
              <div class="experimental-card-icon">
                <i class="fas fa-headphones"></i>
              </div>
              <div class="experimental-card-info">
                <h3>Focus Mode</h3>
                <p>Ambient audio for deep focus and relaxation</p>
              </div>
              <i class="fas fa-chevron-right experimental-card-arrow"></i>
            </a>
          </div>
        </div>

        <!-- Actions -->
        <div class="settings-actions">
          <button type="button" class="neu-btn neu-btn-secondary" @click="resetSettings">
            <i class="fas fa-undo"></i>
            Reset to Defaults
          </button>
          <button type="button" class="neu-btn neu-btn-primary" @click="saveSettings">
            <i class="fas fa-save"></i>
            Save Settings
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { apiFetch } from '../composables/useApi'
import { usePlayerStore } from '../stores/player'

const router = useRouter()
const auth = useAuth()
const playerStore = usePlayerStore()
const dialEl = ref(null)

const audioSettings = reactive({ masterVolume: 75 })
let isDragging = false
let dragProperty = null
let moveHandler = null
let upHandler = null

const STORAGE_KEY = 'ahoySettings'

function loadSettings() {
  if (auth.isLoggedIn.value) {
    apiFetch('/api/user/profile', { credentials: 'include' })
      .then((data) => {
        if (data?.preferences?.audioSettings) {
          audioSettings.masterVolume = Math.max(0, Math.min(100, data.preferences.audioSettings.masterVolume ?? 75))
        }
        applyFromStorage()
      })
      .catch(() => applyFromStorage())
  } else {
    applyFromStorage()
  }
}

function applyFromStorage() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const settings = JSON.parse(saved)
      if (settings.audioSettings?.masterVolume != null) {
        audioSettings.masterVolume = Math.max(0, Math.min(100, settings.audioSettings.masterVolume))
      }
    }
  } catch {}
  applyAudioSettings()
}

function saveSettings() {
  const settings = { audioSettings: { ...audioSettings } }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
  if (auth.isLoggedIn.value) {
    apiFetch('/api/user/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preferences: { audioSettings: audioSettings } }),
    }).catch(() => {})
  }
  applyAudioSettings()
  window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Settings saved!', type: 'success' } }))
}

function resetSettings() {
  audioSettings.masterVolume = 75
  const settings = { audioSettings: { ...audioSettings } }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
  if (auth.isLoggedIn.value) {
    apiFetch('/api/user/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preferences: { audioSettings: audioSettings } }),
    }).catch(() => {})
  }
  applyAudioSettings()
  window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Settings reset to defaults', type: 'info' } }))
}

function applyAudioSettings() {
  const vol = audioSettings.masterVolume / 100
  document.querySelectorAll('audio').forEach((a) => { a.volume = vol })
  try {
    const el = playerStore.getAudioElement?.()
    if (el) el.volume = vol
  } catch {}
}

function startDialDrag(event, property) {
  isDragging = true
  dragProperty = property
  const dial = event.currentTarget
  moveHandler = (e) => handleDialDrag(e, dial)
  upHandler = () => stopDialDrag()
  document.addEventListener('mousemove', moveHandler)
  document.addEventListener('mouseup', upHandler)
  document.addEventListener('touchmove', moveHandler, { passive: false })
  document.addEventListener('touchend', upHandler)
}

function handleDialDrag(event, dial) {
  if (!isDragging || !dial) return
  const clientX = event.touches ? event.touches[0].clientX : event.clientX
  const clientY = event.touches ? event.touches[0].clientY : event.clientY
  const rect = dial.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2
  const angle = Math.atan2(clientY - centerY, clientX - centerX)
  const degrees = (angle * (180 / Math.PI) + 90 + 360) % 360
  const value = Math.max(0, Math.min(100, degrees / 1.8))
  if (dragProperty === 'masterVolume') audioSettings.masterVolume = value
  applyAudioSettings()
}

function stopDialDrag() {
  isDragging = false
  dragProperty = null
  if (moveHandler) {
    document.removeEventListener('mousemove', moveHandler)
    document.removeEventListener('touchmove', moveHandler)
  }
  if (upHandler) {
    document.removeEventListener('mouseup', upHandler)
    document.removeEventListener('touchend', upHandler)
  }
  moveHandler = null
  upHandler = null
}

async function onLogout() {
  await auth.logout()
  window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Signed out', type: 'success' } }))
  router.push('/')
}

onMounted(() => {
  loadSettings()
})
onUnmounted(() => {
  stopDialDrag()
})
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: #0e0e10;
  padding: 24px 16px 80px;
}
.settings-container {
  max-width: 640px;
  margin: 0 auto;
}
.settings-page-header.podcasts-hero .podcasts-hero-inner h1 {
  margin: 0 0 6px 0;
  font-size: 28px;
  font-weight: 700;
}
.settings-page-header.podcasts-hero .podcasts-hero-inner p {
  margin: 0;
  color: rgba(255, 255, 255, 0.68);
}

.settings-header {
  text-align: center;
  margin-bottom: 40px;
}
.settings-header-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  border-radius: 20px;
  background: #18181b;
  box-shadow: 6px 6px 14px rgba(0, 0, 0, 0.7), -6px -6px 14px rgba(255, 255, 255, 0.03);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: rgba(255, 255, 255, 0.5);
}
.settings-header h1 {
  font-size: 1.8rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 6px;
}
.settings-header p {
  color: rgba(255, 255, 255, 0.35);
  font-size: 0.95rem;
  margin: 0;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.neu-card {
  background: #18181b;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  box-shadow: 8px 8px 20px rgba(0, 0, 0, 0.6), -4px -4px 12px rgba(255, 255, 255, 0.02);
}
.neu-card h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.neu-card h2 i {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.3);
}

.settings-profile { margin-bottom: 12px; }
.settings-label {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 4px;
}
.settings-value {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.9);
}
.settings-links { display: flex; flex-direction: column; gap: 0; }
.settings-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 0;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-size: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.settings-link:hover { color: rgba(139, 92, 246, 0.9); }
.logout-btn {
  margin-top: 20px;
  width: 100%;
  justify-content: center;
}
.settings-guest {
  text-align: center;
  padding: 12px 0;
}
.settings-guest p {
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 16px;
  font-size: 0.95rem;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 20px;
}
.setting-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.setting-item label {
  font-weight: 500;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.dial-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.neu-dial {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  position: relative;
  cursor: pointer;
  background: #18181b;
  border: none;
  box-shadow: 6px 6px 16px rgba(0, 0, 0, 0.7), -4px -4px 10px rgba(255, 255, 255, 0.025), inset 0 0 0 1px rgba(255, 255, 255, 0.04);
  transition: box-shadow 0.2s ease;
}
.neu-dial:hover {
  box-shadow: 6px 6px 16px rgba(0, 0, 0, 0.7), -4px -4px 10px rgba(255, 255, 255, 0.025), inset 0 0 0 1px rgba(255, 255, 255, 0.08), 0 0 20px rgba(99, 102, 241, 0.08);
}
.neu-dial .dial-handle {
  position: absolute;
  top: 8px;
  left: 50%;
  width: 3px;
  height: 24px;
  background: linear-gradient(180deg, rgba(99, 102, 241, 0.9), rgba(139, 92, 246, 0.6));
  border-radius: 2px;
  transform: translateX(-50%);
  box-shadow: 0 0 8px rgba(99, 102, 241, 0.3);
}
.dial-value {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  font-size: 1rem;
  font-variant-numeric: tabular-nums;
}

.experimental-disclaimer {
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.8rem;
  margin-bottom: 16px;
}
.experimental-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.experimental-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 14px;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s ease, background 0.2s ease;
}
.experimental-card:hover {
  background: #161619;
  box-shadow: inset 3px 3px 8px rgba(0, 0, 0, 0.4), inset -2px -2px 6px rgba(255, 255, 255, 0.02), 0 0 16px rgba(99, 102, 241, 0.06);
}
.neu-card-inset {
  background: #131316;
  box-shadow: inset 4px 4px 10px rgba(0, 0, 0, 0.5), inset -2px -2px 6px rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.03);
}
.experimental-card-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #18181b;
  box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.5), -3px -3px 8px rgba(255, 255, 255, 0.02);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  color: rgba(139, 92, 246, 0.7);
  flex-shrink: 0;
}
.experimental-card-info {
  flex: 1;
  min-width: 0;
}
.experimental-card-info h3 {
  margin: 0 0 2px;
  font-size: 0.95rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}
.experimental-card-info p {
  margin: 0;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.35);
}
.experimental-card-arrow {
  color: rgba(255, 255, 255, 0.2);
  font-size: 13px;
  flex-shrink: 0;
}

.settings-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}
.neu-btn {
  padding: 12px 24px;
  border-radius: 12px;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: box-shadow 0.2s ease, background 0.2s ease;
  text-decoration: none;
  color: inherit;
}
.neu-btn-secondary {
  background: #18181b;
  color: rgba(255, 255, 255, 0.5);
  box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.5), -3px -3px 8px rgba(255, 255, 255, 0.02);
}
.neu-btn-secondary:hover {
  color: rgba(255, 255, 255, 0.7);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.4), -2px -2px 4px rgba(255, 255, 255, 0.02);
}
.neu-btn-primary {
  background: linear-gradient(135deg, #1e1b2e, #1a1730);
  color: rgba(139, 92, 246, 0.9);
  box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.5), -3px -3px 8px rgba(255, 255, 255, 0.02), 0 0 12px rgba(99, 102, 241, 0.06);
}
.neu-btn-primary:hover {
  color: rgba(139, 92, 246, 1);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.4), -2px -2px 4px rgba(255, 255, 255, 0.02), 0 0 20px rgba(99, 102, 241, 0.1);
}

@media (max-width: 768px) {
  .settings-page { padding: 16px 12px 100px; }
}
</style>
