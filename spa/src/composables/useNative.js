/**
 * Native feature composables — things that were impossible with Flask/Jinja.
 * Uses Web APIs that work in both browsers and Capacitor WebViews.
 * When Capacitor plugins are installed later, these can be swapped to native calls.
 */

// ── Native Share ────────────────────────────────────────────────────
// Flask couldn't do this: the OS share sheet (contacts, messages, AirDrop, etc.)
export function useShare() {
  const canShare = 'share' in navigator

  async function share({ title, text, url }) {
    if (!canShare) {
      // Fallback: copy to clipboard
      try {
        await navigator.clipboard.writeText(url || text || title)
        return { shared: false, copied: true }
      } catch {
        return { shared: false, copied: false }
      }
    }
    try {
      await navigator.share({ title, text, url })
      return { shared: true }
    } catch (err) {
      if (err.name === 'AbortError') return { shared: false, cancelled: true }
      return { shared: false }
    }
  }

  function shareTrack(track) {
    return share({
      title: `${track.title} — ${track.artist || 'Ahoy Indie Media'}`,
      text: `Listen to "${track.title}" on Ahoy Indie Media`,
      url: `https://app.ahoy.ooo/music/${track.id}`,
    })
  }

  function shareArtist(artist) {
    return share({
      title: `${artist.name} on Ahoy Indie Media`,
      text: `Check out ${artist.name} on Ahoy Indie Media`,
      url: `https://app.ahoy.ooo/artists/${artist.slug || artist.id}`,
    })
  }

  function shareShow(show) {
    return share({
      title: `${show.title} — Ahoy Indie Media`,
      text: `Watch "${show.title}" on Ahoy Indie Media`,
      url: `https://app.ahoy.ooo/shows/${show.id}`,
    })
  }

  function sharePodcast(show) {
    return share({
      title: `${show.title} — Ahoy Indie Media`,
      text: `Listen to "${show.title}" podcast on Ahoy Indie Media`,
      url: `https://app.ahoy.ooo/podcasts/${show.slug}`,
    })
  }

  function shareEvent(event) {
    return share({
      title: `${event.title} — Ahoy Indie Media`,
      text: `${event.title}${event.date ? ' · ' + event.date : ''}${event.venue ? ' · ' + event.venue : ''}`,
      url: `https://app.ahoy.ooo/events/${event.id}`,
    })
  }

  return { canShare, share, shareTrack, shareArtist, shareShow, sharePodcast, shareEvent }
}

// ── Haptic Feedback ─────────────────────────────────────────────────
// Flask had zero haptics. Now taps feel physical.
export function useHaptics() {
  const canVibrate = 'vibrate' in navigator

  function light() {
    if (canVibrate) navigator.vibrate(10)
  }

  function medium() {
    if (canVibrate) navigator.vibrate(25)
  }

  function heavy() {
    if (canVibrate) navigator.vibrate([30, 20, 50])
  }

  // Specific interaction haptics
  function onPlay() { light() }
  function onBookmark() { medium() }
  function onNavigate() { light() }
  function onError() { heavy() }

  return { canVibrate, light, medium, heavy, onPlay, onBookmark, onNavigate, onError }
}

// ── Screen Wake Lock ────────────────────────────────────────────────
// Flask: screen would dim and lock during playback. Now it stays on.
let wakeLock = null

export function useWakeLock() {
  const isSupported = 'wakeLock' in navigator

  async function request() {
    if (!isSupported) return false
    try {
      wakeLock = await navigator.wakeLock.request('screen')
      wakeLock.addEventListener('release', () => { wakeLock = null })
      return true
    } catch {
      return false
    }
  }

  async function release() {
    if (wakeLock) {
      await wakeLock.release()
      wakeLock = null
    }
  }

  // Re-acquire on visibility change (screen locks release when tab is hidden)
  function autoReacquire() {
    document.addEventListener('visibilitychange', async () => {
      if (document.visibilityState === 'visible' && !wakeLock) {
        await request()
      }
    })
  }

  return { isSupported, request, release, autoReacquire }
}

// ── Sleep Timer ─────────────────────────────────────────────────────
// Flask couldn't do this. Stop playback after N minutes (bedtime listening).
let sleepTimerId = null
let sleepCallback = null

export function useSleepTimer() {
  function start(minutes, onSleep) {
    clear()
    sleepCallback = onSleep
    sleepTimerId = setTimeout(() => {
      if (sleepCallback) sleepCallback()
      sleepTimerId = null
    }, minutes * 60 * 1000)
  }

  function clear() {
    if (sleepTimerId) {
      clearTimeout(sleepTimerId)
      sleepTimerId = null
    }
    sleepCallback = null
  }

  function isActive() {
    return sleepTimerId !== null
  }

  return { start, clear, isActive }
}

// ── Playback Speed ──────────────────────────────────────────────────
// Flask player had no speed control. Essential for podcasts.
export function usePlaybackSpeed(getAudioElement) {
  const speeds = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]

  function set(speed) {
    const audio = getAudioElement()
    if (audio) audio.playbackRate = speed
  }

  function cycle(currentSpeed) {
    const idx = speeds.indexOf(currentSpeed)
    const nextIdx = (idx + 1) % speeds.length
    const newSpeed = speeds[nextIdx]
    set(newSpeed)
    return newSpeed
  }

  return { speeds, set, cycle }
}
