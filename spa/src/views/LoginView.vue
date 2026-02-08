<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <i class="fas fa-anchor" style="font-size:36px;color:var(--accent-primary,#6ddcff)"></i>
        <h1>Ahoy</h1>
      </div>

      <!-- Toggle login / signup -->
      <div class="auth-tabs">
        <button :class="{ active: mode === 'login' }" @click="mode = 'login'">Log In</button>
        <button :class="{ active: mode === 'signup' }" @click="mode = 'signup'">Sign Up</button>
      </div>

      <form @submit.prevent="onSubmit" class="auth-form">
        <div class="auth-field" v-if="mode === 'signup'">
          <label for="username">Username</label>
          <input id="username" v-model="username" type="text" placeholder="your name" autocomplete="username" />
        </div>
        <div class="auth-field">
          <label for="email">Email</label>
          <input id="email" v-model="email" type="email" placeholder="you@example.com" autocomplete="email" required />
        </div>
        <div class="auth-field">
          <label for="password">Password</label>
          <input id="password" v-model="password" type="password" placeholder="••••••••" autocomplete="current-password" required />
        </div>

        <div class="auth-error" v-if="auth.error.value">{{ auth.error.value }}</div>

        <button type="submit" class="auth-submit" :disabled="auth.loading.value">
          <i v-if="auth.loading.value" class="fas fa-spinner fa-spin"></i>
          <span v-else>{{ mode === 'login' ? 'Log In' : 'Create Account' }}</span>
        </button>
      </form>

      <button class="auth-skip" @click="router.push('/')">
        Continue as Guest
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const auth = useAuth()

const mode = ref('login')
const email = ref('')
const password = ref('')
const username = ref('')

async function onSubmit() {
  let result
  if (mode.value === 'login') {
    result = await auth.login(email.value, password.value)
  } else {
    result = await auth.signup(email.value, password.value, username.value)
  }
  if (result.success) {
    window.dispatchEvent(new CustomEvent('ahoy:toast', {
      detail: { message: mode.value === 'login' ? 'Welcome back!' : 'Account created!', type: 'success' }
    }))
    router.push('/')
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
.auth-card {
  width: 100%;
  max-width: 380px;
  background: rgba(20, 20, 28, 0.85);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 32px 24px;
}
.auth-logo {
  text-align: center;
  margin-bottom: 24px;
}
.auth-logo h1 {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  margin: 8px 0 0;
}
.auth-tabs {
  display: flex;
  background: rgba(255,255,255,0.06);
  border-radius: 10px;
  padding: 3px;
  margin-bottom: 20px;
}
.auth-tabs button {
  flex: 1;
  background: none;
  border: none;
  color: rgba(255,255,255,0.5);
  font-size: 14px;
  font-weight: 600;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.auth-tabs button.active {
  background: rgba(255,255,255,0.1);
  color: #fff;
}
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.auth-field label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255,255,255,0.5);
  margin-bottom: 6px;
}
.auth-field input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.06);
  color: #fff;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}
.auth-field input:focus {
  border-color: var(--accent-primary, #6ddcff);
}
.auth-field input::placeholder { color: rgba(255,255,255,0.25); }
.auth-error {
  color: #f87171;
  font-size: 13px;
  text-align: center;
}
.auth-submit {
  width: 100%;
  padding: 14px;
  border-radius: 12px;
  border: none;
  background: var(--accent-primary, #6ddcff);
  color: #111;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s;
}
.auth-submit:disabled { opacity: 0.5; }
.auth-submit:active { opacity: 0.8; }
.auth-skip {
  display: block;
  width: 100%;
  background: none;
  border: none;
  color: rgba(255,255,255,0.4);
  font-size: 14px;
  margin-top: 16px;
  cursor: pointer;
  text-align: center;
}
.auth-skip:active { color: rgba(255,255,255,0.6); }
</style>
