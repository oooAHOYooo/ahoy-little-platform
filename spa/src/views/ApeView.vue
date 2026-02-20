<template>
  <div class="ape-page">
    <section class="podcasts-hero ape-hero">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-robot" aria-hidden="true"></i> Ape</h1>
        <p>Advanced Platform Engine - Documentation & Details</p>
      </div>
    </section>
    <div class="ape-content">
      <p>Coming Soon. This page will describe the Ape platform details based on the documentation.</p>
      <router-link to="/downloads" class="back-link"><i class="fas fa-arrow-left"></i> Back to Downloads</router-link>
    </div>
  </div>
</template>

<style scoped>
.ape-page { padding-bottom: 3rem; }
.ape-hero.podcasts-hero .podcasts-hero-inner h1 { margin: 0 0 6px 0; font-size: 28px; font-weight: 700; }
.ape-hero.podcasts-hero .podcasts-hero-inner p { margin: 0; color: rgba(255,255,255,0.68); }
.ape-content { max-width: 800px; margin: 2rem auto; padding: 1.5rem; color: rgba(255,255,255,0.85); line-height: 1.6; }
.back-link { display: inline-flex; align-items: center; gap: 0.5rem; color: var(--accent-primary); text-decoration: none; margin-top: 1rem; }
.back-link:hover { text-decoration: underline; }
</style>
