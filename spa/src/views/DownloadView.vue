<template>
  <div class="download-app-page">
    <!-- Liquid glass hero -->
    <section class="download-hero download-hero-glass">
      <div class="download-hero-glow"></div>
      <div class="download-hero-inner">
        <div class="download-hero-icon">
          <i class="fas fa-download" aria-hidden="true"></i>
        </div>
        <h1>Get Ahoy</h1>
        <p>Use Ahoy Indie Media on your favorite device.</p>
      </div>
    </section>

    <!-- Platform cards in glass container -->
    <div class="download-content-glass">
      <div class="download-platform-grid">
        <div class="download-platform-card glass-card">
          <div class="download-platform-icon web">
            <i class="fas fa-globe"></i>
          </div>
          <h3>Web</h3>
          <p>Use Ahoy in any modern browser. No install required.</p>
          <a
            href="/"
            class="download-platform-cta neu-btn neu-btn-primary"
            @click.prevent="$router.push('/')"
          >
            Open in browser
          </a>
        </div>

        <div class="download-platform-card glass-card">
          <div class="download-platform-icon android">
            <i class="fab fa-android"></i>
          </div>
          <h3>Android</h3>
          <p>Native app for phones and tablets. Internal testing on Google Play.</p>
          <a
            href="https://play.google.com/store/apps"
            target="_blank"
            rel="noopener noreferrer"
            class="download-platform-cta neu-btn neu-btn-primary"
          >
            Google Play
          </a>
        </div>

        <div class="download-platform-card glass-card">
          <div class="download-platform-icon ios">
            <i class="fab fa-apple"></i>
          </div>
          <h3>iOS</h3>
          <p>Native app for iPhone and iPad. TestFlight beta coming soon.</p>
          <a
            href="https://testflight.apple.com"
            target="_blank"
            rel="noopener noreferrer"
            class="download-platform-cta neu-btn neu-btn-secondary"
          >
            TestFlight
          </a>
        </div>

        <div class="download-platform-card glass-card">
          <div class="download-platform-icon desktop">
            <i class="fas fa-desktop"></i>
          </div>
          <h3>Desktop</h3>
          <p>Windows, macOS, and Linux standalone apps. Coming soon.</p>
          <span class="download-badge coming-soon">Coming soon</span>
        </div>
      </div>

      <p class="download-footer-note">
        Mobile and desktop apps load the same experience from the cloud. Your account and progress sync everywhere.
      </p>
    </div>
  </div>
</template>

<script setup>
// No state needed; static download page
</script>

<style scoped>
.download-app-page {
  min-height: 100vh;
  background: var(--background-dark, #0c0c0e);
  color: var(--text-primary, #e5e7eb);
  padding: var(--gutter, 20px);
  padding-bottom: 4rem;
}

/* ===== Liquid glass hero ===== */
.download-hero-glass {
  position: relative;
  background: linear-gradient(135deg, rgba(15, 15, 25, 0.95) 0%, rgba(20, 20, 35, 0.9) 50%, rgba(25, 25, 45, 0.85) 100%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  margin-bottom: var(--section-gap, 22px);
  overflow: hidden;
  backdrop-filter: saturate(140%) blur(20px);
  -webkit-backdrop-filter: saturate(140%) blur(20px);
  box-shadow:
    0 20px 50px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    inset 0 -1px 0 rgba(0, 0, 0, 0.3);
}

.download-hero-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 30% 30%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 70% 70%, rgba(139, 92, 246, 0.06) 0%, transparent 50%);
  pointer-events: none;
}

.download-hero-inner {
  position: relative;
  z-index: 2;
  padding: var(--spacing-xl, 2rem);
  text-align: center;
}

.download-hero-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.2) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  color: rgba(139, 92, 246, 0.95);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
}

.download-hero-inner h1 {
  margin: 0 0 0.25rem;
  font-size: 1.75rem;
  font-weight: 700;
  color: #fff;
}

.download-hero-inner p {
  margin: 0;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.6);
}

/* ===== Glass content container ===== */
.download-content-glass {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  padding: var(--spacing-xl, 1.5rem);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.download-platform-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.download-platform-card {
  background: rgba(19, 19, 22, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 18px;
  padding: 1.5rem;
  text-align: center;
  transition: box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease;
  position: relative;
  box-shadow: inset 4px 4px 10px rgba(0, 0, 0, 0.3), inset -2px -2px 6px rgba(255, 255, 255, 0.02);
}

.download-platform-card:hover {
  background: rgba(22, 22, 26, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: inset 3px 3px 8px rgba(0, 0, 0, 0.4), inset -2px -2px 6px rgba(255, 255, 255, 0.03), 0 0 20px rgba(99, 102, 241, 0.06);
}

.download-platform-icon {
  width: 52px;
  height: 52px;
  margin: 0 auto 1rem;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.download-platform-icon.web {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(99, 102, 241, 0.2));
  color: rgba(96, 165, 250, 0.95);
}

.download-platform-icon.android {
  background: linear-gradient(135deg, rgba(52, 168, 83, 0.25), rgba(139, 92, 246, 0.15));
  color: rgba(134, 239, 172, 0.95);
}

.download-platform-icon.ios {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.06));
  color: rgba(255, 255, 255, 0.9);
}

.download-platform-icon.desktop {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.15));
  color: rgba(167, 139, 250, 0.95);
}

.download-platform-card h3 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.download-platform-card p {
  margin: 0 0 1rem;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.5;
}

.download-platform-cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s ease, background 0.2s ease;
}

.download-platform-cta.neu-btn-primary {
  background: linear-gradient(135deg, #1e1b2e, #1a1730);
  color: rgba(139, 92, 246, 0.95);
  box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.5), -3px -3px 8px rgba(255, 255, 255, 0.02), 0 0 12px rgba(99, 102, 241, 0.08);
}

.download-platform-cta.neu-btn-primary:hover {
  color: rgba(139, 92, 246, 1);
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.4), 0 0 20px rgba(99, 102, 241, 0.12);
}

.download-platform-cta.neu-btn-secondary {
  background: #18181b;
  color: rgba(255, 255, 255, 0.6);
  box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.5), -3px -3px 8px rgba(255, 255, 255, 0.02);
}

.download-platform-cta.neu-btn-secondary:hover {
  color: rgba(255, 255, 255, 0.85);
}

.download-badge {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
}

.download-badge.coming-soon {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.download-footer-note {
  margin: 0;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.4);
  line-height: 1.5;
  text-align: center;
}

@media (max-width: 768px) {
  .download-app-page {
    padding: 16px 12px 100px;
  }
  .download-hero-inner {
    padding: 1.5rem 1rem;
  }
  .download-platform-grid {
    grid-template-columns: 1fr;
  }
}
</style>
