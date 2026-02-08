<template>
  <nav class="spa-mobile-nav" role="navigation" aria-label="Primary">
    <router-link to="/music" class="mobile-tab" :class="{ active: route.path === '/music' }">
      <i class="fas fa-music" aria-hidden="true"></i>
      <span>Music</span>
    </router-link>
    <router-link to="/shows" class="mobile-tab" :class="{ active: route.path === '/shows' }">
      <i class="fas fa-video" aria-hidden="true"></i>
      <span>Videos</span>
    </router-link>
    <router-link to="/live-tv" class="mobile-tab" :class="{ active: route.path === '/live-tv' }">
      <i class="fas fa-tv" aria-hidden="true"></i>
      <span>Live TV</span>
    </router-link>
    <router-link to="/artists" class="mobile-tab" :class="{ active: route.path === '/artists' }">
      <i class="fas fa-users" aria-hidden="true"></i>
      <span>Artists</span>
    </router-link>
    <router-link to="/podcasts" class="mobile-tab" :class="{ active: route.path.startsWith('/podcasts') }">
      <i class="fas fa-podcast" aria-hidden="true"></i>
      <span>Podcasts</span>
    </router-link>
    <router-link to="/merch" class="mobile-tab" :class="{ active: route.path === '/merch' }">
      <i class="fas fa-shopping-bag" aria-hidden="true"></i>
      <span>Merch</span>
    </router-link>
    <router-link to="/radio" class="mobile-tab" :class="{ active: route.path === '/radio' }">
      <i class="fas fa-broadcast-tower" aria-hidden="true"></i>
      <span>Radio</span>
    </router-link>
    <router-link to="/my-saves" class="mobile-tab" :class="{ active: route.path === '/my-saves' }">
      <i class="fas fa-bookmark" aria-hidden="true"></i>
      <span>Saved</span>
    </router-link>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
</script>
