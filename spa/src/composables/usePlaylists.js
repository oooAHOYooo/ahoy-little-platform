/**
 * Playlists — list, create, get, rename, delete, list items, add item, remove item.
 * All require login (session cookie).
 */
import { ref } from 'vue'
import { apiFetch } from './useApi'

export function usePlaylists() {
  const loading = ref(false)
  const error = ref(null)

  async function list() {
    loading.value = true
    error.value = null
    try {
      const data = await apiFetch('/api/playlists')
      return data.items || []
    } catch (e) {
      error.value = e.message
      return []
    } finally {
      loading.value = false
    }
  }

  async function create(name) {
    loading.value = true
    error.value = null
    try {
      const data = await apiFetch('/api/playlists', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: String(name).trim() }),
      })
      return data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function get(playlistId) {
    try {
      return await apiFetch(`/api/playlists/${playlistId}`)
    } catch (e) {
      error.value = e.message
      return null
    }
  }

  async function rename(playlistId, name) {
    try {
      return await apiFetch(`/api/playlists/${playlistId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: String(name).trim() }),
      })
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  async function remove(playlistId) {
    try {
      await apiFetch(`/api/playlists/${playlistId}`, { method: 'DELETE' })
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  async function listItems(playlistId) {
    try {
      const data = await apiFetch(`/api/playlists/${playlistId}/items`)
      return data.items || []
    } catch (e) {
      error.value = e.message
      return []
    }
  }

  async function addItem(playlistId, mediaId, mediaType, position) {
    const body = { media_id: String(mediaId), media_type: mediaType }
    if (position != null) body.position = position
    try {
      return await apiFetch(`/api/playlists/${playlistId}/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  async function removeItem(playlistId, itemId) {
    try {
      await apiFetch(`/api/playlists/${playlistId}/items/${itemId}`, { method: 'DELETE' })
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  return {
    loading,
    error,
    list,
    create,
    get,
    rename,
    remove,
    listItems,
    addItem,
    removeItem,
  }
}
