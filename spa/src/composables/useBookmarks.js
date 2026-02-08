/**
 * Bookmark composable — persists to localStorage and emits a custom event
 * so the SavedView (and any other listener) can react in real time.
 */
import { ref, onMounted, onUnmounted } from 'vue'

const STORAGE_KEY = 'ahoy.bookmarks.v1'

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

export function useBookmarks() {
  const bookmarks = ref(readAll())

  function refresh() {
    bookmarks.value = readAll()
  }

  function isBookmarked(item) {
    const key = item.id || item.slug
    return !!bookmarks.value[key]
  }

  function toggle(item) {
    const key = item.id || item.slug
    const all = readAll()
    if (all[key]) {
      delete all[key]
    } else {
      all[key] = {
        id: item.id,
        slug: item.slug,
        title: item.title,
        artist: item.artist || item.host || '',
        cover_art: item.cover_art || item.thumbnail || item.artwork || item.image || '',
        type: item.type || item._type || 'track',
        audio_url: item.audio_url || item.url || '',
      }
    }
    writeAll(all)
    bookmarks.value = all
  }

  function remove(item) {
    const key = item.id || item.slug
    const all = readAll()
    delete all[key]
    writeAll(all)
    bookmarks.value = all
  }

  // Listen for changes from other components
  onMounted(() => {
    window.addEventListener('bookmarks:changed', refresh)
  })
  onUnmounted(() => {
    window.removeEventListener('bookmarks:changed', refresh)
  })

  return { bookmarks, isBookmarked, toggle, remove }
}
