<template>
  <div class="sitemap-page">
    <section class="podcasts-hero sitemap-hero">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-sitemap" aria-hidden="true"></i> Sitemap</h1>
        <p>Find your way around Ahoy.</p>
      </div>
    </section>
    <div class="sitemap-container">
      <nav class="sitemap-links">
        <router-link to="/">Home</router-link>
        <router-link to="/music">Music</router-link>
        <router-link to="/podcasts">Podcasts</router-link>
        <router-link to="/shows">Shows</router-link>
        <router-link to="/artists">Artists</router-link>
        <router-link to="/events">Events</router-link>
        <router-link to="/radio">Radio</router-link>
        <router-link to="/live-tv">Live TV</router-link>
        <router-link to="/merch">Merch</router-link>
        <router-link to="/my-saves">Saved</router-link>
        <router-link to="/playlists">Playlists</router-link>
        <router-link to="/search">Search</router-link>
        <router-link to="/account">Account</router-link>
        <router-link to="/settings">Settings</router-link>
        <router-link to="/downloads">Downloads</router-link>
        <router-link to="/focus">Focus</router-link>
        <router-link to="/feedback">Feedback</router-link>
        <router-link to="/contact">Contact</router-link>
        <router-link to="/privacy">Privacy</router-link>
        <router-link to="/terms">Terms</router-link>
        <router-link to="/security">Security</router-link>
      </nav>
    </div>
  </div>
</template>

<style scoped>
.sitemap-page { padding-bottom: 3rem; }
.sitemap-hero.podcasts-hero .podcasts-hero-inner h1 { margin: 0 0 6px 0; font-size: 28px; font-weight: 700; }
.sitemap-hero.podcasts-hero .podcasts-hero-inner p { margin: 0; color: rgba(255,255,255,0.68); }
.sitemap-container { max-width: 560px; margin: 0 auto; padding: 1.5rem; }
.sitemap-links { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 0.5rem; }
.sitemap-links a { color: var(--accent-primary, #6ddcff); text-decoration: none; }
.sitemap-links a:hover { text-decoration: underline; }
</style>
