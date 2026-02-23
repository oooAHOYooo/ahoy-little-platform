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
        <h3>1. Information We Collect</h3>
        <p>We collect information you provide directly to us when you create an account, such as your email address, username, and display name. If you use our wallet features, transaction data is processed via Stripe.</p>
        
        <h3>2. How We Use Your Information</h3>
        <p>We use your data to provide the Ahoy service, personalize your experience, and communicate important updates. Data used for "Now Playing" feeds is anonymized or handled according to your privacy settings.</p>
        
        <h3>3. Data Retention & Deletion</h3>
        <p>We retain your data as long as your account is active. You can delete your account at any time through the Account settings, which will remove your personal profile, saves, and playlists. Financial records are retained only as required by law.</p>
        
        <h3>4. Security</h3>
        <p>We implement industry-standard security measures to protect your data. However, no internet transmission is 100% secure.</p>
        
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
