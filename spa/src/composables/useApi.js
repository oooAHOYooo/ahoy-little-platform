/**
 * API client for the Ahoy backend.
 *
 * In dev mode, Vite proxies /api/* to https://app.ahoy.ooo.
 * In production (Capacitor), the app makes requests directly to the API_BASE.
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'https://app.ahoy.ooo'

/**
 * Fetch JSON from an API endpoint with caching support.
 * @param {string} path - API path like '/api/music'
 * @param {object} options - fetch options
 * @returns {Promise<any>} parsed JSON
 */
export async function apiFetch(path, options = {}) {
  // In dev, use relative path (Vite proxy handles it)
  // In production, use full URL
  const url = import.meta.env.DEV ? path : `${API_BASE}${path}`

  const response = await fetch(url, {
    ...options,
    credentials: 'include', // send/receive session cookies for auth
    headers: {
      'Accept': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
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
