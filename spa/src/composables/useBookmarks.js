/**
 * Bookmark composable — localStorage + optional server sync when logged in.
 * Syncs to Flask POST /api/bookmarks (add) and DELETE /api/bookmarks/:id (remove).
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuth } from './useAuth'
import { apiFetch } from './useApi'

const STORAGE_KEY = 'ahoy.bookmarks.v2'

function readAll() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

function writeAll(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  window.dispatchEvent(new CustomEvent('bookmarks:changed'))
}

/** Map SPA item type to API media_type (music, show, artist, clip) */
function toMediaType(item) {
  const t = (item.type || item._type || 'track').toLowerCase()
  if (t === 'artist') return 'artist'
  if (t === 'show' || t === 'video') return 'show'
  if (t === 'podcast' || t === 'episode') return 'clip'
  return 'music'
}

export function useBookmarks() {
  const auth = useAuth()
  const bookmarks = ref(readAll())

  function refresh() {
    bookmarks.value = readAll()
  }

  function isBookmarked(item) {
    const key = item.id || item.slug
    return !!bookmarks.value[key]
  }

  async function toggle(item) {
    const key = item.id || item.slug
    const all = readAll()
    const existing = all[key]

    if (existing) {
      if (auth.isLoggedIn.value && existing.serverBookmarkId != null) {
        try {
          await apiFetch(`/api/bookmarks/${existing.serverBookmarkId}`, { method: 'DELETE' })
        } catch {
          // still remove locally
        }
      }
      delete all[key]
    } else {
      const payload = {
        id: item.id,
        slug: item.slug,
        title: item.title,
        artist: item.artist || item.host || '',
        cover_art: item.cover_art || item.thumbnail || item.artwork || item.image || '',
        type: item.type || item._type || 'track',
        audio_url: item.audio_url || item.url || '',
      }
      if (auth.isLoggedIn.value) {
        try {
          const res = await apiFetch('/api/bookmarks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              media_id: String(item.id ?? item.slug ?? ''),
              media_type: toMediaType(item),
            }),
          })
          if (res.id) payload.serverBookmarkId = res.id
        } catch {
          // save locally only
        }
      }
      all[key] = payload
    }
    writeAll(all)
    bookmarks.value = all
  }

  function remove(item) {
    const key = item.id || item.slug
    const all = readAll()
    const existing = all[key]
    if (auth.isLoggedIn.value && existing?.serverBookmarkId != null) {
      apiFetch(`/api/bookmarks/${existing.serverBookmarkId}`, { method: 'DELETE' }).catch(() => {})
    }
    delete all[key]
    writeAll(all)
    bookmarks.value = all
  }

  onMounted(() => {
    window.addEventListener('bookmarks:changed', refresh)
  })
  onUnmounted(() => {
    window.removeEventListener('bookmarks:changed', refresh)
  })

  return { bookmarks, isBookmarked, toggle, remove }
}
