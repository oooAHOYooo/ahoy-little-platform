<template>
  <div class="whats-new-page">
    <section class="podcasts-hero whats-new-hero">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-sparkles" aria-hidden="true"></i> What's New</h1>
        <p>Updates and improvements to Ahoy Indie Media.</p>
      </div>
    </section>
    <div class="whats-new-container">
      <p>Check the blog and release notes on the main site for the latest updates.</p>
      <router-link to="/" class="policy-back">Back to Ahoy</router-link>
    </div>
  </div>
</template>

<style scoped>
.whats-new-page { padding-bottom: 3rem; }
.whats-new-hero.podcasts-hero .podcasts-hero-inner h1 { margin: 0 0 6px 0; font-size: 28px; font-weight: 700; }
.whats-new-hero.podcasts-hero .podcasts-hero-inner p { margin: 0; color: rgba(255,255,255,0.68); }
.whats-new-container { max-width: 560px; margin: 0 auto; padding: 1.5rem; color: rgba(255,255,255,0.85); }
.policy-back { display: inline-block; margin-top: 1rem; color: var(--accent-primary); }
</style>
