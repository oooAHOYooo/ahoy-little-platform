<template>
  <div class="pw-wrap">
    <div class="pw-card">
      <h1 class="pw-title">New password time 🔐</h1>
      <p class="pw-sub">Make it strong-ish. Your future self will high-five you.</p>

      <form class="pw-form" @submit.prevent="submit">
        <label class="pw-label">
          New password
          <input v-model="password" class="pw-input" :type="show ? 'text' : 'password'" autocomplete="new-password" minlength="8" required />
        </label>
        <label class="pw-label">
          Confirm
          <input v-model="confirm" class="pw-input" :type="show ? 'text' : 'password'" autocomplete="new-password" minlength="8" required />
        </label>
        <label class="pw-show">
          <input v-model="show" type="checkbox" /> show password
        </label>
        <button type="submit" class="btn btn-primary" :disabled="loading || !canSubmit">
          <span v-if="!loading">Reset password 🎉</span>
          <span v-else>Resetting…</span>
        </button>
      </form>

      <div v-if="message" class="pw-msg" :class="{ 'pw-err': isError }">{{ message }}</div>
      <div class="pw-note"><router-link to="/login">Back to sign in</router-link></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const token = ref('')
const password = ref('')
const confirm = ref('')
const show = ref(false)
const loading = ref(false)
const message = ref('')
const isError = ref(false)

const canSubmit = computed(() =>
  password.value && password.value.length >= 8 && password.value === confirm.value && !!token.value
)

onMounted(() => {
  token.value = route.query.token || ''
  if (!token.value) {
    message.value = 'Missing reset token. Please request a new link.'
    isError.value = true
  }
})

async function submit() {
  if (password.value !== confirm.value) {
    message.value = 'Passwords do not match.'
    isError.value = true
    return
  }
  loading.value = true
  message.value = ''
  isError.value = false
  try {
    const base = import.meta.env.VITE_API_BASE || ''
    const r = await fetch(base + '/api/auth/password-reset/confirm', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: token.value, password: password.value }),
    })
    const data = await r.json().catch(() => ({}))
    if (!r.ok) {
      isError.value = true
      message.value = data.error === 'token_expired' ? 'That link expired. Request a new one?' : 'Reset failed. Try requesting a new link.'
      return
    }
    message.value = 'Password reset! Redirecting to sign in...'
    setTimeout(() => { window.location.href = '/login' }, 2000)
  } catch {
    isError.value = true
    message.value = 'Reset failed. Try requesting a new link.'
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
.pw-show { display: flex; align-items: center; gap: 8px; font-weight: 800; color: rgba(255,255,255,0.9); }
.pw-note { margin-top: 10px; }
.pw-note a { color: var(--accent-primary, #6ddcff); }
.pw-msg { margin-top: 10px; padding: 10px 12px; border-radius: 12px; border: 1px solid rgba(16,185,129,0.30); background: rgba(16,185,129,0.10); color: rgba(255,255,255,0.92); }
.pw-msg.pw-err { border-color: rgba(239,68,68,0.35); background: rgba(239,68,68,0.10); }
.btn { padding: 12px 20px; border-radius: 12px; font-weight: 600; border: none; cursor: pointer; }
.btn-primary { background: var(--accent-primary, #6ddcff); color: #111; }
.btn:disabled { opacity: 0.7; cursor: not-allowed; }
</style>
