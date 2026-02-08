<template>
  <div class="settings-page">
    <div class="unified-header">
      <div class="header-content">
        <h1>Settings</h1>
      </div>
    </div>

    <div class="settings-card">
      <template v-if="auth.isLoggedIn.value">
        <div class="settings-profile">
          <span class="settings-label">Logged in as</span>
          <span class="settings-value">{{ auth.user.value?.email }}</span>
        </div>
        <router-link to="/account" class="settings-link">
          <i class="fas fa-user-circle"></i>
          Account & wallet
        </router-link>
        <router-link to="/my-saves" class="settings-link">
          <i class="fas fa-bookmark"></i>
          Saved
        </router-link>
        <button type="button" class="settings-btn logout" @click="onLogout">
          <i class="fas fa-sign-out-alt"></i>
          Sign out
        </button>
      </template>
      <div v-else class="settings-guest">
        <p>Sign in to manage your preferences.</p>
        <router-link to="/login" class="account-btn primary">Sign in</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const auth = useAuth()

async function onLogout() {
  await auth.logout()
  window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Signed out', type: 'success' } }))
  router.push('/')
}
</script>

<style scoped>
.settings-page {
  padding: 16px 20px 100px;
}
.settings-card {
  max-width: 420px;
  margin: 0 auto;
  background: rgba(20, 20, 28, 0.85);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 24px;
}
.settings-profile {
  margin-bottom: 20px;
}
.settings-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}
.settings-value {
  font-size: 15px;
  color: var(--text-primary);
}
.settings-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 0;
  color: var(--text-primary);
  text-decoration: none;
  font-size: 15px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.settings-link:hover { color: var(--accent-primary); }
.settings-btn.logout {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  margin-top: 20px;
  padding: 12px;
  background: rgba(255,255,255,0.08);
  border: none;
  border-radius: 12px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
}
.settings-btn.logout:hover {
  background: rgba(255,255,255,0.12);
}
.settings-guest {
  text-align: center;
  padding: 20px 0;
}
.settings-guest p {
  color: var(--text-secondary);
  margin-bottom: 16px;
}
.account-btn.primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  background: var(--accent-primary, #6ddcff);
  color: #111;
  text-decoration: none;
  border: none;
  cursor: pointer;
}
</style>
