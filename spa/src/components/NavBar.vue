<template>
  <!-- Same structure as Flask base.html: mobile-dock (unified two-row bar) -->
  <div class="mobile-only">
    <div class="mobile-footer-logo mobile-only">
      <img :src="logoUrl" alt="Ahoy" class="mobile-footer-logo-img" />
    </div>
    <div class="mobile-dock mobile-only" role="navigation" aria-label="Mobile Navigation">
      <nav class="mobile-dock-row mobile-dock-row-secondary" aria-label="Secondary Navigation">
        <router-link to="/artists" class="mobile-tab" :class="{ active: route.path === '/artists' }">
          <i class="fas fa-users"></i>
          <span>Artists</span>
        </router-link>
        <router-link to="/merch" class="mobile-tab" :class="{ active: route.path === '/merch' }">
          <i class="fas fa-shopping-bag"></i>
          <span>Merch</span>
        </router-link>
        <router-link to="/events" class="mobile-tab" :class="{ active: route.path.startsWith('/events') }">
          <i class="fas fa-calendar-alt"></i>
          <span>Events</span>
        </router-link>
        <router-link to="/account" class="mobile-tab" :class="{ active: route.path === '/account' || route.path === '/settings' }">
          <i class="fas fa-user-circle"></i>
          <span>Profile</span>
        </router-link>
        <router-link to="/my-saves" class="mobile-tab" :class="{ active: route.path === '/my-saves' }">
          <i class="fas fa-bookmark"></i>
          <span>Saved</span>
        </router-link>
      </nav>
      <nav class="mobile-dock-row mobile-dock-row-primary" aria-label="Media Navigation">
        <router-link to="/" class="mobile-tab" :class="{ active: route.path === '/' }">
          <i class="fas fa-home"></i>
          <span>Home</span>
        </router-link>
        <router-link to="/music" class="mobile-tab" :class="{ active: route.path === '/music' }">
          <i class="fas fa-music"></i>
          <span>Music</span>
        </router-link>
        <router-link to="/podcasts" class="mobile-tab" :class="{ active: route.path.startsWith('/podcasts') }">
          <i class="fas fa-podcast"></i>
          <span>Podcasts</span>
        </router-link>
        <router-link to="/live-tv" class="mobile-tab" :class="{ active: route.path === '/live-tv' }">
          <i class="fas fa-tv"></i>
          <span>Live TV</span>
        </router-link>
        <router-link to="/shows" class="mobile-tab" :class="{ active: route.path === '/shows' }">
          <i class="fas fa-video"></i>
          <span>Videos</span>
        </router-link>
        <router-link to="/radio" class="mobile-tab" :class="{ active: route.path === '/radio' }">
          <i class="fas fa-broadcast-tower"></i>
          <span>Radio</span>
        </router-link>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
// Runtime path so build doesn't resolve Flask static (logo served when SPA is under same origin)
const logoUrl = '/static/img/ahoy_logo.png'
</script>
