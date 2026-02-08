/**
 * Add to playlist — singleton modal state. Call open(track) from anywhere to show the modal.
 */
import { ref, readonly } from 'vue'
import { usePlaylists } from './usePlaylists'
import { useAuth } from './useAuth'

const showModal = ref(false)
const trackToAdd = ref(null)

export function useAddToPlaylist() {
  const auth = useAuth()
  const playlistsApi = usePlaylists()

  function open(track) {
    if (!track) return
    trackToAdd.value = track
    showModal.value = true
  }

  function close() {
    showModal.value = false
    trackToAdd.value = null
  }

  return {
    showModal: readonly(showModal),
    trackToAdd: readonly(trackToAdd),
    open,
    close,
    playlistsApi,
    auth,
  }
}
