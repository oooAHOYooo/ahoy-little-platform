/**
 * Recently played list: stored in localStorage so it works for guests and logged-in users.
 * Tracks all media types: track, podcast, episode, show, video, live_tv.
 */

const RECENT_STORAGE_KEY = 'ahoy.recentlyPlayed.v1'
const MAX_RECENT_ITEMS = 50

/**
 * Build a normalized play record from any media item (music, podcast, show, live_tv, etc.)
 */
function toPlayRecord(item) {
  if (!item || (item.id == null && item.slug == null)) return null
  const id = item.id ?? item.slug
  const type = item.type || 'track'
  return {
    id,
    type,
    title: item.title || item.name || 'Untitled',
    artist: item.artist ?? item.host ?? '',
    artwork: item.artwork || item.cover_art || item.thumbnail,
    audio_url: item.audio_url || item.url,
    url: item.url || item.audio_url,
    key: `${type}:${id}`,
    played_at: new Date().toISOString(),
  }
}

/**
 * Append a play to the recently-played list (localStorage) and dispatch event.
 * Safe to call from anywhere (store, views). Works for guest accounts.
 */
export function trackRecentPlay(item) {
  const playRecord = toPlayRecord(item)
  if (!playRecord) return
  try {
    const raw = localStorage.getItem(RECENT_STORAGE_KEY)
    let recent = raw ? JSON.parse(raw) : []
    recent = recent.filter((r) => r.key !== playRecord.key)
    recent.unshift(playRecord)
    recent = recent.slice(0, MAX_RECENT_ITEMS)
    localStorage.setItem(RECENT_STORAGE_KEY, JSON.stringify(recent))
    window.dispatchEvent(new CustomEvent('recentlyPlayed:updated', { detail: { recent } }))
  } catch (e) {
    console.warn('trackRecentPlay failed', e)
  }
}

/**
 * Composable: optionally get the list and load function for components that display it.
 */
export function useRecentlyPlayed() {
  return {
    trackRecentPlay,
    storageKey: RECENT_STORAGE_KEY,
    maxItems: MAX_RECENT_ITEMS,
  }
}
