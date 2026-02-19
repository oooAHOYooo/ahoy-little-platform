/**
 * UI Sounds — synthesized 8-bit style interface sound effects.
 * Uses Web Audio API to generate sounds without external files.
 */

let audioContext = null

function getContext() {
    if (!audioContext && typeof window !== 'undefined') {
        const Ctor = window.AudioContext || window.webkitAudioContext
        if (Ctor) audioContext = new Ctor()
    }
    return audioContext
}

/**
 * Play a short, high-pitched "blip" for hover interactions.
 * Very subtle, like a Nintendo switch menu movement.
 */
export function playHoverSound() {
    if (typeof window === 'undefined') return
    const ctx = getContext()
    if (!ctx) return

    // Resume context if suspended (browser autoplay policy)
    if (ctx.state === 'suspended') ctx.resume().catch(() => { })

    const t0 = ctx.currentTime
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()

    // Short sine/triangle blip
    osc.type = 'triangle'
    osc.frequency.setValueAtTime(800, t0)
    osc.frequency.exponentialRampToValueAtTime(1200, t0 + 0.05)

    // Quick envelope
    gain.gain.setValueAtTime(0, t0)
    gain.gain.linearRampToValueAtTime(0.05, t0 + 0.01) // Very quiet
    gain.gain.exponentialRampToValueAtTime(0.001, t0 + 0.05)

    osc.connect(gain)
    gain.connect(ctx.destination)
    osc.start(t0)
    osc.stop(t0 + 0.05)
}

/**
 * Play a "click" or "select" sound.
 * Slightly lower pitch, more definite.
 */
export function playClickSound() {
    if (typeof window === 'undefined') return
    const ctx = getContext()
    if (!ctx) return

    if (ctx.state === 'suspended') ctx.resume().catch(() => { })

    const t0 = ctx.currentTime
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()

    osc.type = 'square'
    osc.frequency.setValueAtTime(400, t0)
    osc.frequency.exponentialRampToValueAtTime(600, t0 + 0.1)

    gain.gain.setValueAtTime(0, t0)
    gain.gain.linearRampToValueAtTime(0.08, t0 + 0.01)
    gain.gain.exponentialRampToValueAtTime(0.001, t0 + 0.1)

    osc.connect(gain)
    gain.connect(ctx.destination)
    osc.start(t0)
    osc.stop(t0 + 0.1)
}

export function useUISounds() {
    return {
        playHoverSound,
        playClickSound
    }
}
