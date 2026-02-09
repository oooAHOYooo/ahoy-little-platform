<template>
  <div class="checkout-redirect">
    <p>Taking you to secure checkout…</p>
    <p v-if="error" class="error">{{ error }}</p>
    <router-link v-else to="/">Back to Ahoy</router-link>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const error = ref('')

onMounted(() => {
  const query = route.fullPath.replace(/^\/checkout/, '') || ''
  try {
    window.location.href = '/checkout' + query
  } catch (e) {
    error.value = 'Could not redirect. Please go to Checkout from the main site.'
  }
})
</script>

<style scoped>
.checkout-redirect {
  max-width: 480px;
  margin: 2rem auto;
  padding: 2rem;
  text-align: center;
  color: rgba(255,255,255,0.9);
}
.checkout-redirect p { margin: 0 0 1rem; }
.checkout-redirect a { color: var(--accent-primary, #6ddcff); }
.checkout-redirect .error { color: #f87171; }
</style>
