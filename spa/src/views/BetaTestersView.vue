<template>
  <div class="beta-page">
    <section class="podcasts-hero beta-hero">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-mobile-alt" aria-hidden="true"></i> Beta Testers</h1>
        <p>Join our beta testing program and help shape the future of Ahoy Indie Media.</p>
      </div>
    </section>
    <div class="beta-container">
      <p>Thank you for your interest in beta testing! Your feedback helps us create the best experience for independent music discovery. Installation instructions and signup are available on the full site.</p>
      <router-link to="/" class="policy-back">Back to Ahoy</router-link>
    </div>
  </div>
</template>

<style scoped>
.beta-page { padding-bottom: 3rem; }
.beta-hero.podcasts-hero .podcasts-hero-inner h1 { margin: 0 0 6px 0; font-size: 28px; font-weight: 700; }
.beta-hero.podcasts-hero .podcasts-hero-inner p { margin: 0; color: rgba(255,255,255,0.68); }
.beta-container { max-width: 640px; margin: 0 auto; padding: 1.5rem; color: rgba(255,255,255,0.85); line-height: 1.6; }
.policy-back { display: inline-block; margin-top: 1rem; color: var(--accent-primary); }
</style>
