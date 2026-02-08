import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePlayerStore = defineStore('player', () => {
  // State
  const currentTrack = ref(null)
  const isPlaying = ref(false)
  const queue = ref([])
  const currentTime = ref(0)
  const duration = ref(0)
  const loading = ref(false)
  const shuffle = ref(false)
  const repeat = ref(false) // false = off, true = repeat all (queue)

  // Audio element (singleton)
  let audio = null
  function getAudio() {
    if (!audio) {
      audio = new Audio()
      audio.preload = 'auto'

      audio.addEventListener('timeupdate', () => {
        currentTime.value = audio.currentTime
        // Update Media Session position state
        updatePositionState()
      })
      audio.addEventListener('loadedmetadata', () => {
        duration.value = audio.duration
        loading.value = false
      })
      audio.addEventListener('ended', () => {
        next()
      })
      audio.addEventListener('pause', () => {
        isPlaying.value = false
      })
      audio.addEventListener('play', () => {
        isPlaying.value = true
        loading.value = false
      })
      audio.addEventListener('waiting', () => {
        loading.value = true
      })
      audio.addEventListener('canplay', () => {
        loading.value = false
      })
      audio.addEventListener('error', (e) => {
        console.warn('Audio error:', e)
        loading.value = false
        isPlaying.value = false
      })

      // Set up Media Session action handlers (lock screen / steering wheel controls)
      if ('mediaSession' in navigator) {
        navigator.mediaSession.setActionHandler('play', () => play())
        navigator.mediaSession.setActionHandler('pause', () => pause())
        navigator.mediaSession.setActionHandler('previoustrack', () => previous())
        navigator.mediaSession.setActionHandler('nexttrack', () => next())
        navigator.mediaSession.setActionHandler('seekto', (details) => {
          if (details.seekTime != null) {
            audio.currentTime = details.seekTime
          }
        })
      }
    }
    return audio
  }

  // Media Session metadata (lock screen, notification, steering wheel)
  function updateMediaSession(track) {
    if (!('mediaSession' in navigator) || !track) return
    navigator.mediaSession.metadata = new MediaMetadata({
      title: track.title || 'Unknown',
      artist: track.artist || '',
      album: track.album || 'Ahoy Indie Media',
      artwork: [
        { src: track.cover_art || track.thumbnail || track.artwork || '/static/img/default-cover.jpg', sizes: '512x512', type: 'image/jpeg' },
      ],
    })
  }

  function updatePositionState() {
    if (!('mediaSession' in navigator) || !audio) return
    try {
      if (audio.duration && isFinite(audio.duration)) {
        navigator.mediaSession.setPositionState({
          duration: audio.duration,
          playbackRate: audio.playbackRate,
          position: audio.currentTime,
        })
      }
    } catch { /* ignore */ }
  }

  // Computed
  const progress = computed(() => {
    if (!duration.value) return 0
    return (currentTime.value / duration.value) * 100
  })

  const hasQueue = computed(() => queue.value.length > 0)

  // Actions
  function play(track) {
    const a = getAudio()
    if (track) {
      currentTrack.value = track
      const src = track.audio_url || track.url || ''
      if (src) {
        loading.value = true
        a.src = src
        a.load()
        a.play().catch((err) => {
          // Autoplay blocked — user will need to tap play
          console.warn('Playback blocked:', err.message)
          loading.value = false
        })
        updateMediaSession(track)
        saveLastPlayed(track)
      }
    } else if (a.src) {
      a.play().catch(() => {})
    }
  }

  function pause() {
    isPlaying.value = false
    getAudio().pause()
  }

  function togglePlay() {
    if (isPlaying.value) {
      pause()
    } else {
      play()
    }
  }

  function seek(percent) {
    const a = getAudio()
    if (a.duration && isFinite(a.duration)) {
      a.currentTime = (percent / 100) * a.duration
    }
  }

  function setQueue(tracks, startIndex = 0) {
    queue.value = tracks
    if (tracks.length > startIndex) {
      play(tracks[startIndex])
    }
  }

  function next() {
    if (!currentTrack.value) return
    if (!queue.value.length) return
    const idx = queue.value.findIndex(t => (t.id === currentTrack.value.id) || (t.id === currentTrack.value.slug))
    if (idx < 0) {
      play(queue.value[0])
      return
    }
    if (shuffle.value) {
      const others = queue.value.filter((_, i) => i !== idx)
      const randomIdx = Math.floor(Math.random() * (others.length || 1))
      play(others[randomIdx] || queue.value[(idx + 1) % queue.value.length])
    } else {
      const nextIdx = (idx + 1) % queue.value.length
      if (repeat.value && nextIdx === 0) play(queue.value[0])
      else play(queue.value[nextIdx])
    }
  }

  function previous() {
    if (!queue.value.length || !currentTrack.value) return
    const a = getAudio()
    if (a.currentTime > 3) {
      a.currentTime = 0
      return
    }
    const idx = queue.value.findIndex(t => (t.id === currentTrack.value.id) || (t.id === currentTrack.value.slug))
    const prevIdx = idx > 0 ? idx - 1 : queue.value.length - 1
    play(queue.value[prevIdx])
  }

  function clearQueue() {
    queue.value = []
  }

  function removeFromQueue(index) {
    queue.value = queue.value.filter((_, i) => i !== index)
  }

  // Persist last played track to localStorage for session resume
  function saveLastPlayed(track) {
    try {
      localStorage.setItem('ahoy.lastPlayed', JSON.stringify({
        track,
        timestamp: Date.now(),
      }))
    } catch { /* storage full */ }
  }

  // Restore last played track (call once on app startup)
  function restoreLastPlayed() {
    try {
      const raw = localStorage.getItem('ahoy.lastPlayed')
      if (raw) {
        const { track } = JSON.parse(raw)
        if (track) {
          currentTrack.value = track
          // Don't auto-play — just show in mini player
          const a = getAudio()
          const src = track.audio_url || track.url || ''
          if (src) {
            a.src = src
            a.load()
          }
          updateMediaSession(track)
        }
      }
    } catch { /* ignore */ }
  }

  // Get the raw audio element (for speed control, etc.)
  function getAudioElement() {
    return getAudio()
  }

  return {
    currentTrack,
    isPlaying,
    loading,
    queue,
    currentTime,
    duration,
    progress,
    hasQueue,
    shuffle,
    repeat,
    play,
    pause,
    togglePlay,
    seek,
    setQueue,
    next,
    previous,
    clearQueue,
    removeFromQueue,
    restoreLastPlayed,
    getAudioElement,
  }
})
