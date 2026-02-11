import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { trackRecentPlay } from '../composables/useRecentlyPlayed'

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
  const volume = ref(100) // 0–100
  const isMuted = ref(false)

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

      // Initial volume from store
      audio.volume = Math.max(0, Math.min(1, volume.value / 100))
      audio.muted = isMuted.value

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
        navigator.mediaSession.setActionHandler('seekbackward', () => seekBackward5())
        navigator.mediaSession.setActionHandler('seekforward', () => seekForward5())
      }
    }
    return audio
  }

  function setVolume(value) {
    const v = Math.max(0, Math.min(100, Number(value)))
    volume.value = Math.round(v)
    const a = getAudio()
    a.volume = v / 100
    if (isMuted.value && v > 0) isMuted.value = false
    a.muted = isMuted.value
  }

  function toggleMute() {
    isMuted.value = !isMuted.value
    getAudio().muted = isMuted.value
  }

  function seekBackward5() {
    const a = getAudio()
    if (!a.src) return
    a.currentTime = Math.max(0, (a.currentTime || 0) - 5)
  }

  function seekForward5() {
    const a = getAudio()
    if (!a.src) return
    const dur = duration.value || a.duration
    const now = a.currentTime || 0
    a.currentTime = Math.min(dur && isFinite(dur) ? dur : now + 5, now + 5)
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
        trackRecentPlay(track)
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

  function addToQueue(track) {
    queue.value = [...queue.value, track]
  }

  function isInQueue(track) {
    if (!track) return false
    const id = track.id ?? track.key
    return queue.value.some(t => (t.id ?? t.key) === id)
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
    volume,
    isMuted,
    play,
    pause,
    togglePlay,
    seek,
    setVolume,
    toggleMute,
    seekBackward5,
    seekForward5,
    setQueue,
    next,
    previous,
    clearQueue,
    removeFromQueue,
    addToQueue,
    isInQueue,
    restoreLastPlayed,
    getAudioElement,
  }
})
