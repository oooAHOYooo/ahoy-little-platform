<template>
  <div class="policy-page">
    <div class="policy-container">
      <div class="policy-content">
        <p>We use TLS for data in transit, encryption at rest, and secure password hashing. We implement access controls and regular security updates. For the full security policy, see the main site.</p>
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
