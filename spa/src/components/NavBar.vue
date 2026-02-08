<template>
  <nav class="nav-bar">
    <router-link to="/" class="nav-item" :class="{ active: route.path === '/' }">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>
      <span>Home</span>
    </router-link>
    <router-link to="/music" class="nav-item" :class="{ active: route.path === '/music' }">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="5.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="15.5" r="2.5"/><path d="M8 17V5l12-2v12"/></svg>
      <span>Music</span>
    </router-link>
    <router-link to="/shows" class="nav-item" :class="{ active: route.path === '/shows' }">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
      <span>Shows</span>
    </router-link>
    <router-link to="/podcasts" class="nav-item" :class="{ active: route.path === '/podcasts' }">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2M12 19v4M8 23h8"/></svg>
      <span>Podcasts</span>
    </router-link>
    <router-link to="/artists" class="nav-item" :class="{ active: route.path === '/artists' }">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      <span>Artists</span>
    </router-link>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
</script>
