<template>
  <div class="success-page">
    <div class="success-card">
      <div class="success-emoji">🎉</div>
      <h1 class="success-title">Thank you!</h1>
      <p v-if="status && status !== 'paid'" class="success-text">Your payment is processing. If you don't see it finalize in a moment, refresh this page.</p>
      <p v-else class="success-text">Your purchase was completed successfully.</p>
      <p v-if="pid" class="success-ref">Reference: #{{ pid }}</p>
      <div class="success-actions">
        <router-link to="/" class="success-btn secondary">Back to Ahoy</router-link>
        <template v-if="artistId">
          <a :href="`/checkout?type=boost&artist_id=${artistId}&amount=${amount || 1}`" class="success-btn primary">Add {{ (amount || 1).toFixed(2) }} more</a>
          <a :href="`/checkout?type=boost&artist_id=${artistId}&amount=5`" class="success-btn primary">Add $5</a>
          <a :href="`/checkout?type=boost&artist_id=${artistId}&amount=10`" class="success-btn primary">Add $10</a>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const pid = computed(() => route.query.pid || '')
const status = computed(() => route.query.status || '')
const artistId = computed(() => route.query.artist_id || '')
const amount = computed(() => route.query.amount || '')
</script>

<style scoped>
.success-page {
  max-width: 36rem;
  margin: 0 auto;
  padding: 4rem 1rem;
}
.success-card {
  background: rgba(10,10,10,0.7);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 1rem;
  padding: 2rem;
  text-align: center;
  color: #fff;
}
.success-emoji { font-size: 2.5rem; margin-bottom: 0.5rem; }
.success-title { font-size: 1.5rem; font-weight: 700; margin: 0 0 0.5rem; }
.success-text { margin: 0 0 0.5rem; }
.success-ref { font-size: 0.875rem; color: rgba(255,255,255,0.7); margin: 0 0 1rem; }
.success-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 1rem;
}
.success-btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  text-decoration: none;
  transition: background 0.2s;
}
.success-btn.secondary {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
}
.success-btn.secondary:hover { background: rgba(255,255,255,0.15); }
.success-btn.primary { background: #2563eb; color: #fff; }
.success-btn.primary:hover { background: #3b82f6; }
</style>
