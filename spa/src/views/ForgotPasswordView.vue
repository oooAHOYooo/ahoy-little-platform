<template>
  <div class="pw-wrap">
    <div class="pw-card">
      <h1 class="pw-title">Forgot your password? No stress 😄</h1>
      <p class="pw-sub">Drop your email and we'll send you a magic reset link (expires in 1 hour).</p>

      <form class="pw-form" @submit.prevent="submit">
        <label class="pw-label">
          Email
          <input v-model.trim="email" class="pw-input" type="email" autocomplete="email" placeholder="you@example.com" required />
        </label>
        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="!loading">Send reset link ✉️</span>
          <span v-else>Sending…</span>
        </button>
      </form>

      <div v-if="message" class="pw-msg">{{ message }}</div>
      <div class="pw-note">Tip: We'll always show success here (even if the email isn't registered) to keep accounts private.</div>
      <div class="pw-note"><router-link to="/login">Back to sign in</router-link></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { apiFetch } from '../composables/useApi'

const email = ref('')
const loading = ref(false)
const message = ref('')

async function submit() {
  loading.value = true
  message.value = ''
  try {
    const data = await apiFetch('/api/auth/password-reset/request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value }),
    }).catch(() => ({}))
    message.value = data?.message || "If that email exists, we sent a reset link."
  } catch {
    message.value = "If that email exists, we sent a reset link."
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.pw-wrap { max-width: 520px; margin: 0 auto; padding: 22px 16px 44px; }
.pw-card { border-radius: 16px; border: 1px solid rgba(255,255,255,0.10); background: rgba(255,255,255,0.03); padding: 16px; }
.pw-title { font-size: 20px; margin: 0; color: #fff; }
.pw-sub { margin: 8px 0 0; color: rgba(255,255,255,0.72); }
.pw-form { margin-top: 14px; display: flex; flex-direction: column; gap: 10px; }
.pw-label { font-weight: 800; display: flex; flex-direction: column; gap: 6px; color: rgba(255,255,255,0.9); }
.pw-input { width: 100%; padding: 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.14); background: rgba(0,0,0,0.35); color: #fff; }
.pw-note { margin-top: 10px; font-size: 12px; color: rgba(255,255,255,0.65); }
.pw-note a { color: var(--accent-primary, #6ddcff); }
.pw-msg { margin-top: 10px; padding: 10px 12px; border-radius: 12px; border: 1px solid rgba(59,130,246,0.30); background: rgba(59,130,246,0.10); color: rgba(255,255,255,0.92); }
.btn { padding: 12px 20px; border-radius: 12px; font-weight: 600; border: none; cursor: pointer; }
.btn-primary { background: var(--accent-primary, #6ddcff); color: #111; }
.btn:disabled { opacity: 0.7; cursor: not-allowed; }
</style>
