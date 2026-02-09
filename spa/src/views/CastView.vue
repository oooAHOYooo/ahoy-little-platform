<template>
  <div class="cast-page">
    <section class="podcasts-hero cast-hero">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-tv" aria-hidden="true"></i> Cast</h1>
        <p>Cast Ahoy to your TV with quick, no-fuss options.</p>
      </div>
    </section>

    <div class="cast-content">
      <div class="cast-card">
        <h3><i class="fas fa-bolt"></i> Quick Start</h3>
        <ol>
          <li>Open this Cast page on your TV or a laptop hooked to your TV.</li>
          <li>Click <strong>Open Receiver (TV)</strong>.</li>
          <li>On your phone/laptop, pick a track/show and click <strong>Send to Receiver</strong>.</li>
        </ol>
        <div class="cast-badges">
          <span class="cast-badge">No account needed</span>
          <span class="cast-badge">Works anywhere</span>
        </div>
        <div class="cast-actions">
          <a href="/cast/receiver" target="_blank" rel="noopener" class="cast-btn primary"><i class="fas fa-tv"></i> Open Receiver (TV)</a>
          <button type="button" class="cast-btn outline" :disabled="!nowPlaying" @click="sendToReceiver">
            <i class="fas fa-paper-plane"></i> Send to Receiver
          </button>
        </div>
        <p v-if="!nowPlaying" class="cast-hint">Boost: press Play on something first, then hit Send.</p>
        <p v-else class="cast-hint"><i class="fas fa-music"></i> Now Playing: <strong>{{ nowPlaying?.title }}</strong></p>
      </div>

      <div class="cast-card">
        <h3><i class="fab fa-apple"></i> AirPlay (Safari / iOS / macOS)</h3>
        <ul>
          <li>No account needed. Open Ahoy in Safari, start playing, then tap the <strong>AirPlay</strong> icon and choose your Apple TV.</li>
        </ul>
      </div>

      <div class="cast-card">
        <h3><i class="fab fa-chrome"></i> Chrome Tab Casting</h3>
        <ul>
          <li>In Chrome, click the <strong>Cast</strong> button and choose your Chromecast or Android TV. Use "Cast tab" for quick casting.</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { usePlayerStore } from '../stores/player'

const playerStore = usePlayerStore()
const nowPlaying = computed(() => playerStore.currentTrack)

function sendToReceiver() {
  if (!nowPlaying.value) return
  window.open('/cast/receiver?send=1', '_blank', 'noopener')
}
</script>

<style scoped>
.cast-page { padding-bottom: 3rem; }
.cast-hero.podcasts-hero .podcasts-hero-inner h1 { margin: 0 0 6px 0; font-size: 28px; font-weight: 700; }
.cast-hero.podcasts-hero .podcasts-hero-inner p { margin: 0; color: rgba(255,255,255,0.68); }
.cast-content { max-width: 640px; margin: 0 auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }
.cast-card {
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 1.25rem;
}
.cast-card h3 { margin: 0 0 0.75rem; font-size: 1.1rem; color: #fff; }
.cast-card ol, .cast-card ul { margin: 0 0 1rem; padding-left: 1.25rem; color: rgba(255,255,255,0.8); line-height: 1.6; }
.cast-badges { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem; }
.cast-badge { background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 8px; font-size: 0.8rem; color: rgba(255,255,255,0.8); }
.cast-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.cast-btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 16px; border-radius: 10px; font-weight: 600; text-decoration: none; border: none; cursor: pointer; font-size: 14px; }
.cast-btn.primary { background: var(--accent-primary, #6ddcff); color: #111; }
.cast-btn.outline { background: transparent; color: #fff; border: 1px solid rgba(255,255,255,0.3); }
.cast-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.cast-hint { margin: 0.75rem 0 0; font-size: 0.9rem; color: rgba(255,255,255,0.6); }
</style>
