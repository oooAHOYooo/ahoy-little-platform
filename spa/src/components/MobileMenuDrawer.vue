<template>
  <!-- Same structure as Flask _nav_main.html: offcanvas overlay + left panel -->
  <Teleport to="body">
    <div
      v-show="open"
      class="offcanvas-overlay mobile-only"
      aria-hidden="false"
      @click="close"
    />
    <aside
      v-show="open"
      class="offcanvas-panel offcanvas-left mobile-only"
      :class="{ open }"
      role="dialog"
      aria-label="Menu"
    >
        <div class="offcanvas-header">
          <h2>Explore</h2>
          <button type="button" class="offcanvas-close" aria-label="Close navigation" @click="close">✕</button>
        </div>
        <nav class="offcanvas-nav">
          <router-link to="/" @click="close"><i class="fas fa-compass"></i><span>Explore</span></router-link>
          <router-link to="/music" @click="close"><i class="fas fa-music"></i><span>Music</span></router-link>
          <router-link to="/videos" @click="close"><i class="fas fa-video"></i><span>Videos</span></router-link>
          <router-link to="/artists" @click="close"><i class="fas fa-users"></i><span>Artists</span></router-link>
          <router-link to="/merch" @click="close"><i class="fas fa-shopping-bag"></i><span>Merch</span></router-link>
          <router-link to="/radio" @click="close"><i class="fas fa-broadcast-tower"></i><span>Radio</span></router-link>
          <router-link to="/live-tv" @click="close"><i class="fas fa-tv"></i><span>Live TV</span></router-link>
          <router-link to="/my-saves" @click="close"><i class="fas fa-bookmark"></i><span>Saved</span></router-link>
          <router-link to="/recently-played" @click="close"><i class="fas fa-history"></i><span>Recently Played</span></router-link>
          <router-link to="/settings" @click="close"><i class="fas fa-cog"></i><span>Settings</span></router-link>
          <router-link to="/account" @click="close"><i class="fas fa-user-circle"></i><span>Account</span></router-link>
        </nav>
      </aside>
  </Teleport>
</template>

<script setup>
import { watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
})
const emit = defineEmits(['close'])
function close() {
  emit('close')
}

// Lock body scroll when drawer is open (match Flask mobile behavior)
watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) document.body.style.overflow = 'hidden'
    else document.body.style.overflow = ''
  },
  { immediate: true }
)
</script>

<style scoped>
.offcanvas-nav a {
  text-decoration: none;
  color: inherit;
}
</style>
