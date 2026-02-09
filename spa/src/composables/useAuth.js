/**
 * Auth composable — session-based auth with Flask /api/auth/*.
 *
 * Uses cookies (credentials: 'include' in useApi). No token storage.
 * Restores session on load via GET /api/auth/me.
 */
import { ref, computed } from 'vue'
import { apiFetch } from './useApi'

const USER_KEY = 'ahoy.auth.user'

// Shared state (singleton)
const user = ref(null)
const loading = ref(false)
const error = ref(null)
let mePromise = null

// Optional: hydrate from localStorage for instant UI, then validate with /me
function hydrateFromStorage() {
  try {
    const saved = localStorage.getItem(USER_KEY)
    if (saved) user.value = JSON.parse(saved)
  } catch { /* ignore */ }
}

async function fetchMe() {
  if (mePromise) return mePromise
  mePromise = apiFetch('/api/auth/me').then((data) => {
    if (data?.user) {
      user.value = data.user
      try { localStorage.setItem(USER_KEY, JSON.stringify(data.user)) } catch { /* ignore */ }
    } else {
      user.value = null
    }
    return data
  }).catch(() => {
    user.value = null
    try { localStorage.removeItem(USER_KEY) } catch { /* ignore */ }
    return null
  }).finally(() => { mePromise = null })
  return mePromise
}

// Run once on first composable use (e.g. when app mounts)
function restoreSession() {
  hydrateFromStorage()
  fetchMe()
}

export function useAuth() {
  const isLoggedIn = computed(() => !!user.value)
  const username = computed(() => user.value?.username || user.value?.email || '')

  async function login(email, password) {
    loading.value = true
    error.value = null
    try {
      const data = await apiFetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier: email, password }),
      })
      if (data.success && data.user) {
        user.value = data.user
        try { localStorage.setItem(USER_KEY, JSON.stringify(data.user)) } catch { /* ignore */ }
        return { success: true }
      }
      const msg = data.error === 'invalid_credentials' ? 'Invalid email or password.' : (data.message || data.error || 'Login failed')
      error.value = msg
      return { success: false, error: msg }
    } catch (e) {
      error.value = e.message || 'Network error'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function signup(email, password, username) {
    loading.value = true
    error.value = null
    try {
      const data = await apiFetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, username: username || undefined }),
      })
      if (data.success && data.user) {
        user.value = data.user
        try { localStorage.setItem(USER_KEY, JSON.stringify(data.user)) } catch { /* ignore */ }
        return { success: true }
      }
      const msg = data.error === 'invalid_username' && data.suggestions?.length
        ? `Username invalid. Try: ${data.suggestions.slice(0, 2).join(', ')}`
        : (data.error === 'account_already_exists' ? 'An account with this email already exists.' : (data.message || data.error || 'Signup failed'))
      error.value = msg
      return { success: false, error: msg }
    } catch (e) {
      error.value = e.message || 'Network error'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    error.value = null
    try {
      await apiFetch('/api/auth/logout', { method: 'POST' })
    } catch { /* ignore */ }
    user.value = null
    try { localStorage.removeItem(USER_KEY) } catch { /* ignore */ }
    loading.value = false
  }

  // For callers that expect auth headers (e.g. future API that uses Bearer). Session uses cookies.
  function authHeaders() {
    return {}
  }

  return {
    user,
    loading,
    error,
    isLoggedIn,
    username,
    login,
    signup,
    logout,
    authHeaders,
    restoreSession,
  }
}

// Call once on app load (e.g. from App.vue onMounted) to restore session from cookie
export { restoreSession }
