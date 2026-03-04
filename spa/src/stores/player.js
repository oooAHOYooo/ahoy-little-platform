import { defineStore } from 'pinia'
import { ref, computed, watch, onUnmounted } from 'vue'
import { apiFetch } from '../composables/useApi'
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
  const repeat = ref(false)
  const volume = ref(JSON.parse(localStorage.getItem('player-volume') || '0.8') * 100) // Initialize from localStorage, convert to 0-100
  const isMuted = ref(false)
  const sessionId = ref(null)

  // Unified Player State
  const mode = ref('audio') // 'audio' or 'video'
  const heroBounds = ref(null) // { top, left, width, height }
  const videoElement = ref(null) // DOM reference to the global video tag
  const isWidescreenPinned = ref(false)

  // Audio element (singleton)
  let audio = null
  function getAudio() {
    if (!audio) {
      audio = new Audio()
      audio.preload = 'auto'

      audio.addEventListener('timeupdate', () => {
        if (mode.value === 'audio') {
          currentTime.value = audio.currentTime
          updatePositionState()
        }
      })
      audio.addEventListener('loadedmetadata', () => {
        if (mode.value === 'audio') {
          duration.value = audio.duration
          loading.value = false
        }
      })
      audio.addEventListener('ended', () => {
        if (mode.value === 'audio') next()
      })
      audio.addEventListener('pause', () => {
        if (mode.value === 'audio') isPlaying.value = false
      })
      audio.addEventListener('play', () => {
        if (mode.value === 'audio') {
          isPlaying.value = true
          loading.value = false
        }
      })
      audio.addEventListener('waiting', () => {
        if (mode.value === 'audio') loading.value = true
      })
      audio.addEventListener('canplay', () => {
        if (mode.value === 'audio') loading.value = false
      })
      audio.addEventListener('error', (e) => {
        if (mode.value === 'audio') {
          console.warn('Audio error:', e)
          loading.value = false
          isPlaying.value = false
        }
      })

      audio.volume = Math.max(0, Math.min(1, volume.value / 100))
      audio.muted = isMuted.value

      if ('mediaSession' in navigator) {
        navigator.mediaSession.setActionHandler('play', () => play())
        navigator.mediaSession.setActionHandler('pause', () => pause())
        navigator.mediaSession.setActionHandler('previoustrack', () => previous())
        navigator.mediaSession.setActionHandler('nexttrack', () => next())
        navigator.mediaSession.setActionHandler('seekto', (details) => {
          if (details.seekTime != null) {
            if (mode.value === 'audio') audio.currentTime = details.seekTime
            else if (videoElement.value) videoElement.value.currentTime = details.seekTime
          }
        })
      }
    }
    return audio
  }

  function setVolume(value) {
    const v = Math.max(0, Math.min(100, Number(value)))
    volume.value = Math.round(v)
    const a = getAudio()
    a.volume = v / 100
    if (videoElement.value) videoElement.value.volume = v / 100
    if (isMuted.value && v > 0) isMuted.value = false
    a.muted = isMuted.value
    if (videoElement.value) videoElement.value.muted = isMuted.value
    localStorage.setItem('player-volume', JSON.stringify(v / 100))
  }

  function toggleMute() {
    isMuted.value = !isMuted.value
    getAudio().muted = isMuted.value
    if (videoElement.value) videoElement.value.muted = isMuted.value
  }

  function seekBackward5() {
    const media = mode.value === 'audio' ? getAudio() : videoElement.value
    if (!media || !media.src) return
    media.currentTime = Math.max(0, (media.currentTime || 0) - 5)
  }

  function seekForward5() {
    const media = mode.value === 'audio' ? getAudio() : videoElement.value
    if (!media || !media.src) return
    const dur = duration.value || media.duration
    const now = media.currentTime || 0
    media.currentTime = Math.min(dur && isFinite(dur) ? dur : now + 5, now + 5)
  }

  function updateMediaSession(track) {
    if (!('mediaSession' in navigator) || !track) return
    navigator.mediaSession.metadata = new MediaMetadata({
      title: track.title || 'Unknown',
      artist: track.artist || track.host || '',
      album: track.album || 'Ahoy Indie Media',
      artwork: [
        { src: track.cover_art || track.thumbnail || track.artwork || '/static/img/default-cover.jpg', sizes: '512x512', type: 'image/jpeg' },
      ],
    })
  }

  function updatePositionState() {
    const media = mode.value === 'audio' ? audio : videoElement.value
    if (!('mediaSession' in navigator) || !media) return
    try {
      if (media.duration && isFinite(media.duration)) {
        navigator.mediaSession.setPositionState({
          duration: media.duration,
          playbackRate: media.playbackRate,
          position: media.currentTime,
        })
      }
    } catch { /* ignore */ }
  }

  const progress = computed(() => {
    if (!duration.value) return 0
    return (currentTime.value / duration.value) * 100
  })

  const hasQueue = computed(() => queue.value.length > 0)

  // Combined Play Action
  function play(track) {
    if (track) {
      const isVideo = !!(track.video_url || track.url?.endsWith('.mp4') || track._type === 'show' || track.type === 'live_tv')

      if (isVideo) {
        // Switch to video mode
        pause() // Pause existing medium
        mode.value = 'video'
        currentTrack.value = track
        // Video element in GlobalTvPlayer will watch currentTrack and load it
      } else {
        // Switch to audio mode
        if (mode.value === 'video' && videoElement.value) {
          videoElement.value.pause()
        }
        mode.value = 'audio'
        currentTrack.value = track
        const a = getAudio()
        const src = track.audio_url || track.url || ''
        if (src) {
          loading.value = true
          a.src = src
          a.load()
          a.play().catch(() => { loading.value = false })
        }
      }
      updateMediaSession(track)
      saveLastPlayed(track)
      trackRecentPlay(track)
    } else {
      // Resume current
      if (mode.value === 'audio') getAudio().play().catch(() => { })
      else if (videoElement.value) {
        videoElement.value.play().catch(() => { })
        isPlaying.value = true
      }
    }
    // Start listening session
    startListeningSession()
  }

  async function startListeningSession() {
    if (!currentTrack.value) return

    // End existing session if any
    if (sessionId.value) {
      await endListeningSession()
    }

    try {
      const resp = await apiFetch('/api/listening/start', {
        method: 'POST',
        body: JSON.stringify({
          media_id: currentTrack.value.id || currentTrack.value.key,
          media_type: currentTrack.value.type || 'track',
          source: 'manual'
        })
      })
      if (resp && resp.session_id) {
        sessionId.value = resp.session_id
      }
    } catch (e) {
      console.error('Failed to start listening session:', e)
    }
  }

  async function endListeningSession() {
    if (!sessionId.value) return

    const sid = sessionId.value
    sessionId.value = null // Clear immediately to avoid re-entry

    try {
      await apiFetch('/api/listening/end', {
        method: 'POST',
        body: JSON.stringify({ session_id: sid })
      })
    } catch (e) {
      console.error('Failed to end listening session:', e)
    }
  }

  function pause() {
    isPlaying.value = false
    getAudio().pause()
    if (videoElement.value) videoElement.value.pause()
    endListeningSession()
  }

  function stop() {
    pause() // Pause and end session
    if (mode.value === 'audio') {
      const a = getAudio()
      a.currentTime = 0
    } else if (videoElement.value) {
      videoElement.value.currentTime = 0
    }
  }

  function togglePlay() {
    if (isPlaying.value) pause()
    else play()
  }

  function resume() { play() }

  function seek(percent) {
    const media = mode.value === 'audio' ? getAudio() : videoElement.value
    if (media && media.duration && isFinite(media.duration)) {
      media.currentTime = (percent / 100) * media.duration
    }
  }

  function setQueue(tracks, startIndex = 0) {
    queue.value = tracks
    if (tracks.length > startIndex) play(tracks[startIndex])
  }

  function next() {
    if (!currentTrack.value || !queue.value.length) return
    const idx = queue.value.findIndex(t => (t.id === currentTrack.value.id) || (t.id === currentTrack.value.slug))
    if (idx < 0) {
      play(queue.value[0])
      return
    }
    const nextIdx = (idx + 1) % queue.value.length
    play(queue.value[nextIdx])
  }

  function previous() {
    const media = mode.value === 'audio' ? getAudio() : videoElement.value
    if (!queue.value.length || !currentTrack.value) return
    if (media && media.currentTime > 3) {
      media.currentTime = 0
      return
    }
    const idx = queue.value.findIndex(t => (t.id === currentTrack.value.id) || (t.id === currentTrack.value.slug))
    const prevIdx = idx > 0 ? idx - 1 : queue.value.length - 1
    play(queue.value[prevIdx])
  }

  function clearQueue() { queue.value = [] }

  function eject() {
    pause()
    if (mode.value === 'audio') {
      const a = getAudio()
      a.src = ''
      a.load()
    } else if (videoElement.value) {
      videoElement.value.src = ''
      videoElement.value.load()
    }
    currentTime.value = 0
    duration.value = 0
    loading.value = false
    currentTrack.value = null
    if ('mediaSession' in navigator) navigator.mediaSession.metadata = null
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

  function saveLastPlayed(track) {
    try {
      localStorage.setItem('ahoy.lastPlayed', JSON.stringify({ track, timestamp: Date.now() }))
    } catch { /* ignore */ }
  }

  function restoreLastPlayed() {
    try {
      const raw = localStorage.getItem('ahoy.lastPlayed')
      if (raw) {
        const { track } = JSON.parse(raw)
        if (track) {
          const isVideo = !!(track.video_url || track.url?.endsWith('.mp4') || track._type === 'show' || track.type === 'live_tv')
          mode.value = isVideo ? 'video' : 'audio'
          currentTrack.value = track
          if (!isVideo) {
            const a = getAudio()
            a.src = track.audio_url || track.url || ''
            a.load()
          }
          updateMediaSession(track)
        }
      }
    } catch { /* ignore */ }
  }

  // --- External Setters ---
  function setVideoElement(el) { videoElement.value = el }
  function setHeroBounds(bounds) { heroBounds.value = bounds }
  function toggleWidescreenPinned() { isWidescreenPinned.value = !isWidescreenPinned.value }

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
    mode,
    heroBounds,
    videoElement,
    play,
    pause,
    resume,
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
    eject,
    restoreLastPlayed,
    setVideoElement,
    setHeroBounds,
    isWidescreenPinned,
    toggleWidescreenPinned
  }
})
