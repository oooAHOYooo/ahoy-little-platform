/**
 * API client for the Ahoy backend.
 *
 * Resolution order:
 * - VITE_API_BASE (explicit override, can be "" for same-origin)
 * - Dev on Vite port: use local Flask (same host, port VITE_API_PORT or 5002)
 * - Otherwise: same-origin (production/Flask-served SPA)
 */

const ENV_API_BASE = import.meta.env.VITE_API_BASE
const ENV_API_PORT = import.meta.env.VITE_API_PORT

function resolveApiBase() {
  if (ENV_API_BASE !== undefined) return ENV_API_BASE
  if (typeof window === 'undefined') return ''
  const { hostname, port, protocol } = window.location
  if (import.meta.env.DEV && (port === '5173' || port === '4173')) {
    const apiPort = ENV_API_PORT || '5002'
    return `${protocol}//${hostname}:${apiPort}`
  }
  return ''
}

const API_BASE = resolveApiBase()

/**
 * Fetch JSON from an API endpoint with caching support.
 * @param {string} path - API path like '/api/music'
 * @param {object} options - fetch options
 * @returns {Promise<any>} parsed JSON
 */
export async function apiFetch(path, options = {}) {
  const base = (API_BASE === '' || API_BASE === undefined) ? '' : API_BASE.replace(/\/$/, '')
  const url = base ? `${base}${path}` : path

  const response = await fetch(url, {
    ...options,
    credentials: 'include', // send/receive session cookies for auth
    headers: {
      'Accept': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    if (response.status === 401) {
      // Session expired or invalid
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('ahoy:session-expired'))
      }
    }
    throw new Error(`API ${path}: ${response.status}`)
  }

  return response.json()
}

/**
 * Fetch with local cache fallback (IndexedDB).
 * Tries network first, caches on success, returns cached on failure.
 */
export async function apiFetchCached(path, cacheKey) {
  const key = cacheKey || `ahoy:${path}`

  try {
    const data = await apiFetch(path)
    // Cache in localStorage for offline use
    try {
      localStorage.setItem(key, JSON.stringify({ data, ts: Date.now() }))
    } catch (e) { /* storage full, ignore */ }
    return data
  } catch (e) {
    // Network failed — try cache
    const cached = localStorage.getItem(key)
    if (cached) {
      const { data } = JSON.parse(cached)
      return data
    }
    throw e
  }
}
