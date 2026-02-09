<template>
  <div class="downloads-page">
    <section class="podcasts-hero downloads-hero">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-download" aria-hidden="true"></i> Downloads</h1>
        <p>Get Ahoy Indie Media as a standalone desktop app.</p>
      </div>
    </section>

    <section class="downloads-container">
      <div class="downloads-intro">
        <p>Get Ahoy Indie Media as a standalone desktop application. Desktop apps are coming soon as part of our <router-link to="/whats-new/2026/jan/platform">mobile improvements initiative</router-link>.</p>
      </div>

      <div class="downloads-section">
        <h2>Desktop Applications</h2>
        <div class="download-grid">
          <div class="download-item">
            <div class="platform-name">Windows</div>
            <div class="file-type">Setup Installer</div>
            <span class="coming-soon-badge">Coming Soon</span>
          </div>
          <div class="download-item">
            <div class="platform-name">macOS</div>
            <div class="file-type">DMG Installer</div>
            <span class="coming-soon-badge">Coming Soon</span>
          </div>
          <div class="download-item">
            <div class="platform-name">Linux</div>
            <div class="file-type">AppImage / DEB / RPM</div>
            <span class="coming-soon-badge">Coming Soon</span>
          </div>
        </div>
      </div>

      <div class="mobile-improvements-link">
        <h2>📱 Mobile App Improvements</h2>
        <p>As part of our ongoing mobile improvements initiative, we're working on bringing you native desktop applications.</p>
        <router-link to="/whats-new/2026/jan/platform" class="link-arrow">Learn More About Mobile Improvements <i class="fas fa-arrow-right"></i></router-link>
      </div>

      <div class="whats-new-info">
        <h3>📦 What's Coming?</h3>
        <p>The desktop app will be the <strong>primary distribution method</strong>. Key improvements coming:</p>
        <ul>
          <li><strong>macOS:</strong> DMG installer with drag-and-drop installation</li>
          <li><strong>Windows:</strong> Professional NSIS installer with Start Menu shortcuts</li>
          <li><strong>Standalone:</strong> No Python installation required</li>
          <li><strong>Local Database:</strong> Uses SQLite stored in user directory</li>
          <li><strong>Auto Port Detection:</strong> Automatically finds free ports</li>
        </ul>
      </div>
    </section>
  </div>
</template>

<style scoped>
.downloads-page { padding-bottom: 3rem; }
.downloads-hero.podcasts-hero .podcasts-hero-inner h1 { margin: 0 0 6px 0; font-size: 28px; font-weight: 700; }
.downloads-hero.podcasts-hero .podcasts-hero-inner p { margin: 0; color: rgba(255,255,255,0.68); }

.downloads-container { max-width: 960px; margin: 2rem auto; padding: 1rem; }
.downloads-intro { margin-bottom: 2rem; }
.downloads-intro p { color: rgba(255,255,255,0.7); font-size: 1rem; line-height: 1.6; }
.downloads-intro a { color: rgba(99,102,241,1); text-decoration: none; }

.downloads-section { margin-top: 2rem; }
.downloads-section h2 { color: #fff; font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem; }
.download-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}
.download-item {
  background: rgba(20,20,20,0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  transition: all 0.2s;
}
.download-item:hover {
  background: rgba(30,30,30,0.8);
  border-color: rgba(255,255,255,0.15);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}
.platform-name { font-weight: 600; margin-bottom: 0.5rem; font-size: 1.25rem; color: #fff; }
.file-type { font-size: 0.9rem; color: rgba(255,255,255,0.6); margin-bottom: 1.5rem; }
.coming-soon-badge {
  display: inline-block;
  background: rgba(99,102,241,0.2);
  color: rgba(99,102,241,1);
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  border: 1px solid rgba(99,102,241,0.3);
}

.mobile-improvements-link {
  margin-top: 3rem;
  padding: 2rem;
  background: rgba(20,20,20,0.6);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.1);
}
.mobile-improvements-link h2 { margin-top: 0; color: #fff; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem; }
.mobile-improvements-link p { color: rgba(255,255,255,0.7); margin-bottom: 1.5rem; line-height: 1.6; }
.link-arrow { display: inline-flex; align-items: center; gap: 0.5rem; color: rgba(99,102,241,1); text-decoration: none; font-weight: 500; }
.link-arrow:hover { gap: 0.75rem; }

.whats-new-info {
  margin-top: 2rem;
  padding: 1.5rem;
  background: rgba(20,20,20,0.6);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.1);
  border-left: 4px solid rgba(99,102,241,0.5);
}
.whats-new-info h3 { margin-top: 0; font-size: 1.1rem; color: #fff; margin-bottom: 0.75rem; }
.whats-new-info p { margin-bottom: 0.75rem; font-size: 0.95rem; color: rgba(255,255,255,0.7); }
.whats-new-info ul { margin: 0.5rem 0; padding-left: 1.5rem; font-size: 0.9rem; color: rgba(255,255,255,0.7); line-height: 1.8; }
.whats-new-info strong { color: #fff; }

@media (max-width: 768px) {
  .download-grid { grid-template-columns: 1fr; }
}
</style>
