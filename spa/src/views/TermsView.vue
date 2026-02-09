<template>
  <div class="policy-page">
    <section class="podcasts-hero policy-hero">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-file-contract" aria-hidden="true"></i> Terms of Service</h1>
        <p>Last updated: December 2024</p>
      </div>
    </section>
    <div class="policy-container">
      <div class="policy-content">
        <p>By using Ahoy Indie Media you agree to our terms. The service is for discovering and enjoying independent music and shows. You must be at least 13 to create an account. For the full terms, see the main site or contact support.</p>
        <router-link to="/" class="policy-back">Back to Ahoy</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.policy-page { padding-bottom: 3rem; }
.policy-hero.podcasts-hero .podcasts-hero-inner h1 { margin: 0 0 6px 0; font-size: 28px; font-weight: 700; }
.policy-hero.podcasts-hero .podcasts-hero-inner p { margin: 0; color: rgba(255,255,255,0.68); }
.policy-container { max-width: 720px; margin: 0 auto; padding: 1.5rem; }
.policy-content { color: rgba(255,255,255,0.85); line-height: 1.6; }
.policy-back { display: inline-block; margin-top: 1.5rem; color: var(--accent-primary); }
</style>
