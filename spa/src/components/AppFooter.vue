<template>
  <footer class="app-footer">
    <div class="footer-content">
      <!-- Column 1: Brand / Logo -->
      <div class="footer-column footer-brand-column">
        <div class="footer-logo">
          <img :src="logoUrl" alt="Ahoy Indie Media" loading="lazy" decoding="async" />
        </div>
        <p class="footer-tagline">Your gateway to independent music discovery and organization</p>
      </div>

      <!-- Column 2: App Navigation -->
      <div class="footer-column">
        <h4 class="footer-column-title">App Navigation</h4>
        <ul>
          <li><router-link to="/">Explore</router-link></li>
          <li><router-link to="/music">Music</router-link></li>
          <li><router-link to="/podcasts">Podcasts</router-link></li>
          <li><router-link to="/live-tv">Live TV</router-link></li>
          <li><router-link to="/videos">Videos</router-link></li>
          <li><router-link to="/artists">Artists</router-link></li>
          <li><router-link to="/radio">Radio</router-link></li>
          <li><router-link to="/events">Events</router-link></li>
          <li><router-link to="/merch">Merch</router-link></li>
          <li><router-link to="/my-saves">Saved</router-link></li>
        </ul>
      </div>

      <!-- Column 3: Legal -->
      <div class="footer-column">
        <h4 class="footer-column-title">Legal</h4>
        <ul>
          <li><a href="/privacy" rel="nofollow">Privacy Policy</a></li>
          <li><a href="/terms" rel="nofollow">Terms of Service</a></li>
          <li><a href="/security">Security</a></li>
          <li><router-link to="/feedback">Feedback</router-link></li>
          <li><a href="/beta-testers">Beta Testers</a></li>
          <li><a href="/sitemap">Sitemap</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <p class="footer-copyright">&copy; 2026 Ahoy Indie Media. All rights reserved.</p>
      <p class="footer-refresh mobile-only" style="margin-top: 8px; font-size: 0.85rem; opacity: 0.85;">
        Having trouble? <a href="/refresh">Get the latest version</a>
      </p>
      <a
        v-if="showAdminLink"
        href="/admin"
        class="footer-admin-link"
        title="Admin Dashboard"
        aria-label="Admin"
      >⚙</a>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { useAuth } from '../composables/useAuth'

const auth = useAuth()

// Same as NavBar: runtime path so build doesn't resolve Flask static
const logoUrl = '/static/img/ahoy_logo.png'

const showAdminLink = computed(() => {
  const user = auth.user.value
  return user?.email === 'alex@ahoy.ooo'
})
</script>
