<template>
  <div class="about-page">
    <section class="podcasts-hero about-hero">
      <div class="podcasts-hero-inner">
        <div class="hero-logo-container">
          <img src="/static/img/ahoy_logo.png" alt="Ahoy Logo" class="hero-logo" />
        </div>
        <h1>About Ahoy</h1>
        <p>A Independent Media Collective & Platform</p>
      </div>
    </section>

    <div class="about-content">
      <div class="about-grid">
        <div class="about-card neu-card">
          <h3>The Mission</h3>
          <p>Ahoy is built to empower independent artists, podcasters, and filmmakers. We provide a platform that values ownership, privacy, and direct connection with the audience.</p>
        </div>
        <div class="about-card neu-card">
          <h3>No Algorithms</h3>
          <p>We believe in discovery led by humans, not engagement-driven algorithms. Explore what you love, at your own pace, with no noise.</p>
        </div>
        <div class="about-card neu-card">
          <h3>Direct Support</h3>
          <p>100% of boosts go directly to the artists. No hidden fees, no middleman taking a massive cut. Just pure support for the creators you love.</p>
        </div>
      </div>

      <div class="about-links">
        <router-link to="/" class="neu-btn neu-btn-primary">Explore Now</router-link>
        <router-link to="/contact" class="neu-btn neu-btn-secondary">Get in Touch</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.about-page {
  min-height: 100vh;
  padding-bottom: 4rem;
}

.about-hero {
  margin-bottom: 2rem;
}

.about-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.about-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.about-card {
  padding: 2rem;
  text-align: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

.about-card h3 {
  font-size: 1.5rem;
  color: var(--primary-color, #00a2ff);
  margin-bottom: 1rem;
}

.about-card p {
  color: var(--text-secondary);
  line-height: 1.6;
}

.about-links {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 2rem;
}

.hero-logo-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 1rem;
}

.hero-logo {
  height: 80px;
  width: auto;
  filter: drop-shadow(0 0 20px rgba(0, 162, 255, 0.4));
}

@media (max-width: 768px) {
  .about-grid {
    grid-template-columns: 1fr;
  }
}
</style>
