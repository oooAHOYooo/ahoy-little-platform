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
        <h3>1. Acceptance of Terms</h3>
        <p>By using Ahoy Indie Media, you agree to these terms. If you do not agree, please do not use the service.</p>
        
        <h3>2. User Accounts</h3>
        <p>You are responsible for maintaining the confidentiality of your account credentials. You must be at least 13 years old to use this service.</p>
        
        <h3>3. Content & Copyright</h3>
        <p>Ahoy is a platform for independent artists. You may not upload or share content that violates the intellectual property rights of others.</p>
        
        <h3>4. Payments & Refunds</h3>
        <p>Wallet funds and boosts are final once processed. Physical merchandise is subject to the return policies listed at checkout.</p>
        
        <h3>5. Termination</h3>
        <p>We reserve the right to suspend or terminate accounts that violate our community standards or terms.</p>
        
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
