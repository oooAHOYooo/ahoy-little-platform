<template>
  <div class="not-found-page">
    <div class="not-found-inner">
      <div class="not-found-graphic" aria-hidden="true">
        <!-- Tilted boat / "oops" vibe -->
        <svg viewBox="0 0 200 140" class="not-found-svg">
          <defs>
            <linearGradient id="nf-water" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#0ea5e9" stop-opacity="0.4" />
              <stop offset="100%" stop-color="#0369a1" stop-opacity="0.6" />
            </linearGradient>
          </defs>
          <!-- Waves -->
          <path fill="url(#nf-water)" d="M0 90 Q50 70 100 90 T200 90 V140 H0 Z" opacity="0.8" />
          <path fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="2" d="M0 95 Q25 85 50 95 T100 95 T150 95 T200 95" />
          <!-- Little boat, tilted -->
          <g transform="translate(100 55) rotate(-12)">
            <ellipse cx="0" cy="0" rx="28" ry="12" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.4)" stroke-width="2" />
            <line x1="-20" y1="0" x2="-20" y2="-22" stroke="rgba(255,255,255,0.5)" stroke-width="2" />
            <path d="M-24 -22 L-16 -22 L-20 -28 Z" fill="rgba(255,255,255,0.4)" />
            <circle cx="0" cy="0" r="4" fill="rgba(255,255,255,0.2)" />
          </g>
          <!-- Question mark bubble -->
          <g transform="translate(155 35)">
            <ellipse cx="0" cy="0" rx="18" ry="18" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.25)" stroke-width="1.5" />
            <text x="0" y="6" text-anchor="middle" fill="rgba(255,255,255,0.6)" font-size="22" font-weight="bold" font-family="system-ui">?</text>
          </g>
        </svg>
      </div>
      <h1 class="not-found-title">Oops!</h1>
      <p class="not-found-msg">This page sailed away. Maybe it’s in uncharted waters.</p>
      <p class="not-found-code">404</p>
      <router-link to="/" class="not-found-btn">
        <i class="fas fa-anchor"></i> Back to Ahoy
      </router-link>
    </div>
  </div>
</template>

<script setup>
// No props needed – catch-all 404
</script>

<style scoped>
.not-found-page {
  min-height: 100vh;
  background: var(--page-bg, #0a0a0a);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}
.not-found-inner { max-width: 380px; }
.not-found-graphic { margin-bottom: 1.5rem; }
.not-found-svg {
  width: 100%;
  max-width: 220px;
  height: auto;
  margin: 0 auto;
  display: block;
}
.not-found-title {
  font-size: 2.25rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}
.not-found-msg {
  font-size: 1.05rem;
  color: rgba(255,255,255,0.7);
  margin: 0 0 0.5rem;
  line-height: 1.5;
}
.not-found-code {
  font-size: 0.9rem;
  color: rgba(255,255,255,0.4);
  font-variant-numeric: tabular-nums;
  margin: 0 0 1.5rem;
}
.not-found-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--accent-primary, #6ddcff);
  color: #111;
  border-radius: 10px;
  font-weight: 600;
  text-decoration: none;
  transition: transform 0.15s, box-shadow 0.15s;
}
.not-found-btn:hover {
  transform: scale(1.03);
  box-shadow: 0 4px 20px rgba(109, 220, 255, 0.35);
}
</style>
