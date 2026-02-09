/**
 * API client for the Ahoy backend.
 *
 * - Dev: Vite proxies /api/* to VITE_API_BASE (default https://app.ahoy.ooo).
 * - Production (web): same origin or VITE_API_BASE. Set VITE_API_BASE="" for same-origin.
 * - Production (Capacitor): VITE_API_BASE or default https://app.ahoy.ooo.
 */

const API_BASE = import.meta.env.VITE_API_BASE ?? 'https://app.ahoy.ooo'

/**
 * Fetch JSON from an API endpoint with caching support.
 * @param {string} path - API path like '/api/music'
 * @param {object} options - fetch options
 * @returns {Promise<any>} parsed JSON
 */
export async function apiFetch(path, options = {}) {
  const base = (API_BASE === '' || API_BASE === undefined) ? '' : API_BASE.replace(/\/$/, '')
  const url = import.meta.env.DEV ? path : `${base}${path}`

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
