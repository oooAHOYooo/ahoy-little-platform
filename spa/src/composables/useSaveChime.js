/**
 * 8-bit style chimes — synthesized with Web Audio API (no audio files).
 * Save chime: localStorage 'ahoy.sound.saveChime' = 'false' to disable.
 * Tap chime (on button/link click): localStorage 'ahoy.sound.tapChime' = 'false' to disable.
 */
const PREF_SAVE = 'ahoy.sound.saveChime'
const PREF_TAP = 'ahoy.sound.tapChime'

let audioContext = null
let reverbIRBuffer = null

function getContext() {
  if (!audioContext && typeof window !== 'undefined') {
    const Ctor = window.AudioContext || window.webkitAudioContext
    if (Ctor) audioContext = new Ctor()
  }
  return audioContext
}

/**
 * Generate a "giant space" reverb impulse response (long decay, diffuse tail).
 * Cached per context so we only build it once.
 */
function getBigSpaceReverbIR(ctx) {
  if (reverbIRBuffer) return reverbIRBuffer
  const sampleRate = ctx.sampleRate
  const decayTime = 2.8 // seconds — long tail for huge space
  const length = Math.min(sampleRate * decayTime, sampleRate * 4)
  const buffer = ctx.createBuffer(2, length, sampleRate)
  const left = buffer.getChannelData(0)
  const right = buffer.getChannelData(1)
  // Exponential decay from 1 to ~0; slight L/R variation for width
  const decay = Math.pow(0.001, 1 / (sampleRate * decayTime * 0.4))
  left[0] = 0.5
  right[0] = 0.5
  for (let i = 1; i < length; i++) {
    const t = i / sampleRate
    const decayCurve = Math.pow(decay, i)
    // Slight early reflections and diffusion
    const early = Math.exp(-t * 8) * 0.15 * (Math.sin(i * 0.7) * 0.5 + 0.5)
    left[i] = (decayCurve + early * (i % 2 === 0 ? 1 : 0.7)) * (0.98 + Math.sin(i * 0.3) * 0.02)
    right[i] = (decayCurve + early * (i % 2 === 1 ? 1 : 0.7)) * (0.98 + Math.sin(i * 0.31) * 0.02)
  }
  reverbIRBuffer = buffer
  return reverbIRBuffer
}

/**
 * Play a short two-tone "coin" style chime (8-bit / NES-like).
 * Square wave, ~200ms total. Safe to call repeatedly; each call schedules a new sound.
 */
export function playSaveChime() {
  if (typeof window === 'undefined') return
  try {
    if (localStorage.getItem(PREF_SAVE) === 'false') return
  } catch {
    // ignore localStorage errors
  }

  const ctx = getContext()
  if (!ctx) return

  const resume = ctx.state === 'suspended' ? ctx.resume() : Promise.resolve()
  resume.then(() => {
    const t0 = ctx.currentTime
    const gain1 = ctx.createGain()
    const gain2 = ctx.createGain()
    gain1.gain.setValueAtTime(0, t0)
    gain1.gain.linearRampToValueAtTime(0.12, t0 + 0.02)
    gain1.gain.exponentialRampToValueAtTime(0.001, t0 + 0.08)

    const osc1 = ctx.createOscillator()
    osc1.type = 'square'
    osc1.frequency.setValueAtTime(523.25, t0) // C5
    osc1.connect(gain1)
    gain1.connect(ctx.destination)
    osc1.start(t0)
    osc1.stop(t0 + 0.08)

    gain2.gain.setValueAtTime(0, t0 + 0.06)
    gain2.gain.linearRampToValueAtTime(0.1, t0 + 0.08)
    gain2.gain.exponentialRampToValueAtTime(0.001, t0 + 0.22)

    const osc2 = ctx.createOscillator()
    osc2.type = 'square'
    osc2.frequency.setValueAtTime(659.25, t0 + 0.06) // E5
    osc2.connect(gain2)
    gain2.connect(ctx.destination)
    osc2.start(t0 + 0.06)
    osc2.stop(t0 + 0.22)
  }).catch(() => {})
}

/**
 * Whether the chime is enabled (user hasn't set preference to false).
 */
export function isSaveChimeEnabled() {
  try {
    return localStorage.getItem(PREF_SAVE) !== 'false'
  } catch {
    return true
  }
}

/**
 * Enable or disable the save chime. Use from a settings toggle.
 */
export function setSaveChimeEnabled(enabled) {
  try {
    if (enabled) localStorage.removeItem(PREF_SAVE)
    else localStorage.setItem(PREF_SAVE, 'false')
  } catch {}
}

// ── Tap chime (tiny blip on button/link click) ────────────────────────

/**
 * Play a deep, reverbed “button press” with a blaster-like punch — low thunk + sharp attack, blooms into a giant space.
 */
export function playTapChime() {
  if (typeof window === 'undefined') return
  try {
    if (localStorage.getItem(PREF_TAP) === 'false') return
  } catch {}

  const ctx = getContext()
  if (!ctx) return

  const resume = ctx.state === 'suspended' ? ctx.resume() : Promise.resolve()
  resume.then(() => {
    const t0 = ctx.currentTime
    const sourceGain = ctx.createGain()
    sourceGain.gain.setValueAtTime(0, t0)
    sourceGain.gain.linearRampToValueAtTime(0.6, t0 + 0.012)
    sourceGain.gain.exponentialRampToValueAtTime(0.001, t0 + 0.08)

    // Deep body: 55 Hz down to 32 Hz
    const osc = ctx.createOscillator()
    osc.type = 'square'
    osc.frequency.setValueAtTime(55, t0)
    osc.frequency.exponentialRampToValueAtTime(32, t0 + 0.06)
    osc.connect(sourceGain)

    // Blaster-style transient: short high punch at the hit
    const blasterGain = ctx.createGain()
    blasterGain.gain.setValueAtTime(0, t0)
    blasterGain.gain.linearRampToValueAtTime(0.4, t0 + 0.003)
    blasterGain.gain.exponentialRampToValueAtTime(0.001, t0 + 0.022)
    const blaster = ctx.createOscillator()
    blaster.type = 'square'
    blaster.frequency.setValueAtTime(280, t0)
    blaster.frequency.exponentialRampToValueAtTime(90, t0 + 0.02)
    blaster.connect(blasterGain)
    blasterGain.connect(sourceGain)
    blaster.start(t0)
    blaster.stop(t0 + 0.022)

    const convolver = ctx.createConvolver()
    convolver.normalize = true
    convolver.buffer = getBigSpaceReverbIR(ctx)
    sourceGain.connect(convolver)

    const reverbGain = ctx.createGain()
    reverbGain.gain.setValueAtTime(0.72, t0)
    convolver.connect(reverbGain)
    reverbGain.connect(ctx.destination)

    osc.start(t0)
    osc.stop(t0 + 0.08)
  }).catch(() => {})
}

export function isTapChimeEnabled() {
  try {
    return localStorage.getItem(PREF_TAP) !== 'false'
  } catch {
    return true
  }
}

export function setTapChimeEnabled(enabled) {
  try {
    if (enabled) localStorage.removeItem(PREF_TAP)
    else localStorage.setItem(PREF_TAP, 'false')
  } catch {}
}
