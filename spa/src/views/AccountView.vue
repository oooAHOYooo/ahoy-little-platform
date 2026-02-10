<template>
  <div class="account-page">
    <div class="unified-header">
      <div class="header-content">
        <h1>Account</h1>
      </div>
    </div>

    <div v-if="auth.isLoggedIn.value" class="account-card">
      <div class="account-profile">
        <div class="account-avatar">
          <i class="fas fa-user-circle"></i>
        </div>
        <div class="account-name">{{ auth.user.value?.display_name || auth.user.value?.username || auth.user.value?.email }}</div>
        <div class="account-email">{{ auth.user.value?.email }}</div>
      </div>

      <section class="account-section">
        <h2 class="account-section-title">Wallet</h2>
        <div class="wallet-balance">
          <span class="wallet-label">Balance</span>
          <span class="wallet-amount">${{ (walletBalance ?? 0).toFixed(2) }}</span>
        </div>
        <p class="wallet-note">Use your wallet for boosts and merch checkout.</p>
        <div class="account-wallet-actions">
          <button type="button" class="account-btn primary" :disabled="walletLoading" @click="addFunds">
            <i v-if="walletLoading" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-wallet"></i>
            Add funds
          </button>
          <router-link to="/wallet" class="account-btn secondary">Transaction history</router-link>
        </div>
      </section>

      <section class="account-section">
        <h2 class="account-section-title">Links</h2>
        <router-link to="/tip-artist" class="account-link">
          <i class="fas fa-heart"></i>
          Boost artists
        </router-link>
        <router-link to="/my-saves" class="account-link">
          <i class="fas fa-bookmark"></i>
          Saved
        </router-link>
        <router-link to="/settings" class="account-link">
          <i class="fas fa-cog"></i>
          Settings
        </router-link>
      </section>

      <button type="button" class="account-btn logout" @click="onLogout">
        <i class="fas fa-sign-out-alt"></i>
        Sign out
      </button>
    </div>

    <div v-else class="account-guest">
      <div class="account-guest-profile">
        <div class="account-avatar">
          <i class="fas fa-user-circle"></i>
        </div>
        <h2 class="account-guest-title">Profile</h2>
        <p class="account-guest-sub">You're browsing as a guest. Save to this device and explore — create an account to sync everywhere.</p>
      </div>

      <section class="account-section">
        <h2 class="account-section-title">Features</h2>
        <router-link to="/my-saves" class="account-link">
          <i class="fas fa-bookmark"></i>
          <span><strong>Saved</strong> — Bookmarks and recently played</span>
        </router-link>
        <router-link to="/playlists" class="account-link">
          <i class="fas fa-list-ul"></i>
          <span><strong>Playlists</strong> — Create and manage (sign in to save)</span>
        </router-link>
        <router-link to="/settings" class="account-link">
          <i class="fas fa-cog"></i>
          <span><strong>Settings</strong> — Audio and preferences</span>
        </router-link>
        <router-link to="/wallet" class="account-link">
          <i class="fas fa-wallet"></i>
          <span><strong>Wallet</strong> — Add funds for boosts and merch (sign in)</span>
        </router-link>
      </section>

      <div class="account-guest-cta">
        <p>Create a free account to sync your saves across devices and unlock wallet, playlists, and more.</p>
        <router-link to="/login?signup=1" class="account-btn primary">Create account</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { apiFetch } from '../composables/useApi'

const router = useRouter()
const auth = useAuth()

const walletBalance = ref(null)
const walletLoading = ref(false)

onMounted(async () => {
  if (auth.isLoggedIn.value) {
    try {
      const data = await apiFetch('/payments/wallet')
      walletBalance.value = data.balance ?? 0
    } catch {
      walletBalance.value = 0
    }
  }
})

async function addFunds() {
  if (!auth.isLoggedIn.value) {
    router.push('/login')
    return
  }
  const amount = 10 // default $10
  walletLoading.value = true
  try {
    const data = await apiFetch('/payments/wallet/fund', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount }),
    })
    if (data.checkout_url) {
      window.location.href = data.checkout_url
      return
    }
    window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: data.error || 'Could not start checkout', type: 'error' } }))
  } catch (e) {
    window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: e.message || 'Failed to add funds', type: 'error' } }))
  } finally {
    walletLoading.value = false
  }
}

async function onLogout() {
  await auth.logout()
  window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Signed out', type: 'success' } }))
  router.push('/')
}
</script>

<style scoped>
.account-page {
  padding: 16px 20px 100px;
}
.account-card {
  max-width: 420px;
  margin: 0 auto;
  background: rgba(20, 20, 28, 0.85);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 24px;
}
.account-profile {
  text-align: center;
  margin-bottom: 24px;
}
.account-avatar {
  font-size: 48px;
  color: rgba(255,255,255,0.6);
}
.account-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #fff);
  margin-top: 8px;
}
.account-email {
  font-size: 13px;
  color: var(--text-secondary, rgba(255,255,255,0.6));
  margin-top: 4px;
}
.account-section {
  margin-bottom: 24px;
}
.account-section-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  margin: 0 0 12px;
}
.wallet-balance {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255,255,255,0.06);
  border-radius: 12px;
  margin-bottom: 8px;
}
.wallet-label { font-size: 14px; color: var(--text-secondary); }
.wallet-amount { font-size: 20px; font-weight: 700; color: #fff; }
.wallet-note {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0 0 12px;
}
.account-wallet-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.account-btn.secondary {
  background: rgba(255,255,255,0.08);
  color: var(--text-primary);
  text-decoration: none;
}
.account-btn.secondary:hover {
  background: rgba(255,255,255,0.12);
}
.account-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: background 0.2s;
}
.account-btn.primary {
  background: var(--accent-primary, #6ddcff);
  color: #111;
}
.account-btn.primary:hover:not(:disabled) {
  filter: brightness(1.1);
}
.account-btn.logout {
  background: rgba(255,255,255,0.08);
  color: var(--text-secondary);
  width: 100%;
  justify-content: center;
}
.account-btn.logout:hover {
  background: rgba(255,255,255,0.12);
}
.account-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 0;
  color: var(--text-primary);
  text-decoration: none;
  font-size: 15px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.account-link:last-of-type { border-bottom: none; }
.account-link:hover { color: var(--accent-primary); }
.account-guest {
  max-width: 420px;
  margin: 0 auto;
  background: rgba(20, 20, 28, 0.85);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 24px;
}
.account-guest-profile {
  text-align: center;
  margin-bottom: 24px;
}
.account-guest-profile .account-avatar {
  font-size: 48px;
  color: rgba(255,255,255,0.5);
}
.account-guest-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary, #fff);
  margin: 12px 0 8px;
}
.account-guest-sub {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.4;
}
.account-guest .account-section {
  margin-bottom: 20px;
}
.account-guest .account-link span {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: normal;
  margin-top: 2px;
}
.account-guest .account-link strong {
  color: var(--text-primary);
  font-weight: 600;
}
.account-guest-cta {
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.08);
}
.account-guest-cta p {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0 0 16px;
  line-height: 1.4;
}
.account-guest-cta .account-btn.primary {
  display: inline-flex;
}
</style>
