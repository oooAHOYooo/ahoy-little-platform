import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePlayerStore = defineStore('player', () => {
  // State
  const currentTrack = ref(null)
  const isPlaying = ref(false)
  const queue = ref([])
  const currentTime = ref(0)
  const duration = ref(0)

  // Audio element (singleton)
  let audio = null
  function getAudio() {
    if (!audio) {
      audio = new Audio()
      audio.addEventListener('timeupdate', () => {
        currentTime.value = audio.currentTime
      })
      audio.addEventListener('loadedmetadata', () => {
        duration.value = audio.duration
      })
      audio.addEventListener('ended', () => {
        next()
      })
      audio.addEventListener('pause', () => {
        isPlaying.value = false
      })
      audio.addEventListener('play', () => {
        isPlaying.value = true
      })
    }
    return audio
  }

  // Computed
  const progress = computed(() => {
    if (!duration.value) return 0
    return (currentTime.value / duration.value) * 100
  })

  // Actions
  function play(track) {
    const a = getAudio()
    if (track) {
      currentTrack.value = track
      a.src = track.audio_url || track.url || ''
      a.load()
    }
    a.play().catch(() => {})
  }

  function pause() {
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
    if (a.duration) {
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
    if (!queue.value.length || !currentTrack.value) return
    const idx = queue.value.findIndex(t => t.id === currentTrack.value.id)
    const nextIdx = (idx + 1) % queue.value.length
    play(queue.value[nextIdx])
  }

  function previous() {
    if (!queue.value.length || !currentTrack.value) return
    const a = getAudio()
    // If more than 3 seconds in, restart current track
    if (a.currentTime > 3) {
      a.currentTime = 0
      return
    }
    const idx = queue.value.findIndex(t => t.id === currentTrack.value.id)
    const prevIdx = idx > 0 ? idx - 1 : queue.value.length - 1
    play(queue.value[prevIdx])
  }

  return {
    currentTrack,
    isPlaying,
    queue,
    currentTime,
    duration,
    progress,
    play,
    pause,
    togglePlay,
    seek,
    setQueue,
    next,
    previous,
  }
})
