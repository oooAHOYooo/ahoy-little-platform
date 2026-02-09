<template>
  <div class="contact-page">
    <section class="podcasts-hero contact-hero">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-envelope" aria-hidden="true"></i> Contact</h1>
        <p>Have a question or want to reach out? We'd love to hear from you.</p>
      </div>
    </section>
    <div class="contact-container">
      <p>Email us at <a href="mailto:support@ahoyindie.com">support@ahoyindie.com</a> or use the feedback form for product feedback.</p>
      <router-link to="/feedback" class="contact-link">Go to Feedback</router-link>
      <router-link to="/" class="policy-back">Back to Ahoy</router-link>
    </div>
  </div>
</template>

<style scoped>
.contact-page { padding-bottom: 3rem; }
.contact-hero.podcasts-hero .podcasts-hero-inner h1 { margin: 0 0 6px 0; font-size: 28px; font-weight: 700; }
.contact-hero.podcasts-hero .podcasts-hero-inner p { margin: 0; color: rgba(255,255,255,0.68); }
.contact-container { max-width: 560px; margin: 0 auto; padding: 1.5rem; color: rgba(255,255,255,0.85); line-height: 1.6; }
.contact-container a { color: var(--accent-primary, #6ddcff); }
.contact-link { display: inline-block; margin-top: 1rem; margin-right: 1rem; }
.policy-back { display: inline-block; margin-top: 1rem; color: var(--accent-primary); }
</style>
