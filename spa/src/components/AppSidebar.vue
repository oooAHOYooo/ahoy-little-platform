<template>
  <aside class="app-sidebar" aria-label="Primary">
    <router-link class="app-sidebar-logo" to="/" aria-label="Ahoy Home">
      <img :src="logoUrl" alt="Ahoy Indie Media" @error="logoError = true" />
      <span v-if="logoError" class="app-sidebar-logo-text">Ahoy</span>
    </router-link>

    <nav class="app-sidebar-nav" aria-label="Primary navigation">
      <router-link to="/" class="app-sidebar-item" :class="{ active: route.path === '/' }" data-icon="compass">
        <i class="fas fa-compass" aria-hidden="true"></i>
        <span>Explore</span>
      </router-link>
      <router-link to="/music" class="app-sidebar-item" :class="{ active: route.path === '/music' }" data-icon="music">
        <i class="fas fa-music" aria-hidden="true"></i>
        <span>Music</span>
      </router-link>
      <router-link to="/podcasts" class="app-sidebar-item" :class="{ active: route.path.startsWith('/podcasts') }" data-icon="podcast">
        <i class="fas fa-podcast" aria-hidden="true"></i>
        <span>Podcasts</span>
      </router-link>
      <router-link to="/live-tv" class="app-sidebar-item" :class="{ active: route.path === '/live-tv' }" data-icon="tv">
        <i class="fas fa-tv" aria-hidden="true"></i>
        <span>Live TV</span>
      </router-link>
      <router-link to="/shows" class="app-sidebar-item" :class="{ active: route.path === '/shows' }" data-icon="video">
        <i class="fas fa-video" aria-hidden="true"></i>
        <span>Videos</span>
      </router-link>
      <router-link to="/artists" class="app-sidebar-item" :class="{ active: route.path === '/artists' }" data-icon="users">
        <i class="fas fa-users" aria-hidden="true"></i>
        <span>Artists</span>
      </router-link>
      <router-link to="/radio" class="app-sidebar-item" :class="{ active: route.path === '/radio' }" data-icon="broadcast-tower">
        <i class="fas fa-broadcast-tower" aria-hidden="true"></i>
        <span>Radio</span>
      </router-link>
      <router-link to="/events" class="app-sidebar-item" :class="{ active: route.path.startsWith('/events') }" data-icon="calendar-alt">
        <i class="fas fa-calendar-alt" aria-hidden="true"></i>
        <span>Events</span>
      </router-link>
      <router-link to="/merch" class="app-sidebar-item" :class="{ active: route.path === '/merch' }" data-icon="shopping-bag">
        <i class="fas fa-shopping-bag" aria-hidden="true"></i>
        <span>Merch</span>
      </router-link>
      <router-link to="/my-saves" class="app-sidebar-item" :class="{ active: route.path === '/my-saves' }" data-icon="bookmark">
        <i class="fas fa-bookmark" aria-hidden="true"></i>
        <span>Saved</span>
      </router-link>
    </nav>

    <div class="app-sidebar-divider"></div>
    <div class="app-sidebar-spacer"></div>

    <nav class="app-sidebar-nav app-sidebar-nav--secondary" aria-label="Account">
      <router-link to="/login" class="app-sidebar-item" :class="{ active: route.path === '/login' }" data-icon="user">
        <i class="fas fa-user" aria-hidden="true"></i>
        <span>{{ auth.isLoggedIn.value ? auth.username.value : 'Profile' }}</span>
      </router-link>
      <router-link to="/login" class="app-sidebar-item" data-icon="cog">
        <i class="fas fa-cog" aria-hidden="true"></i>
        <span>Settings</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const route = useRoute()
const auth = useAuth()

const API_BASE = import.meta.env.VITE_API_BASE || 'https://app.ahoy.ooo'
const logoUrl = `${API_BASE}/static/img/ahoy_logo.png`
const logoError = ref(false)
</script>

<style scoped>
.app-sidebar-logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
}
</style>
