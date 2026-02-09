<template>
  <div class="policy-page">
    <section class="podcasts-hero policy-hero">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-shield-alt" aria-hidden="true"></i> Privacy Policy</h1>
        <p>Last updated: February 2026</p>
      </div>
    </section>
    <div class="policy-container">
      <div class="policy-content">
        <p>We collect account information, content preferences, and usage data. We use this to provide and improve our services, process payments, and personalize your experience. We do not sell your personal information. For the full policy, see the main site or contact <a href="mailto:privacy@ahoyindie.com">privacy@ahoyindie.com</a>.</p>
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
.policy-content a { color: var(--accent-primary, #6ddcff); }
.policy-back { display: inline-block; margin-top: 1.5rem; color: var(--accent-primary); }
</style>
