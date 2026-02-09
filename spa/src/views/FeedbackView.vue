<template>
  <div class="feedback-page">
    <section class="podcasts-hero feedback-hero">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-comment-dots" aria-hidden="true"></i> Feedback</h1>
        <p>Help us improve by sharing what you think.</p>
      </div>
    </section>

    <div class="feedback-container">
      <form class="feedback-form" @submit.prevent="submit">
        <div class="form-section">
          <h3>What type of feedback?</h3>
          <div class="feedback-types">
            <label v-for="t in types" :key="t.value" class="feedback-type-label">
              <input v-model="formData.type" type="radio" :value="t.value" />
              <span>{{ t.label }}</span>
            </label>
          </div>
        </div>
        <div class="form-section">
          <h3>Rating (1–5)</h3>
          <div class="star-rating">
            <button v-for="i in 5" :key="i" type="button" class="star-btn" :class="{ on: formData.rating >= i }" @click="formData.rating = i">
              <i class="fas fa-star"></i>
            </button>
          </div>
        </div>
        <div class="form-section">
          <label for="fb-message">Your feedback *</label>
          <textarea id="fb-message" v-model="formData.message" class="feedback-textarea" rows="4" placeholder="Tell us more…" required></textarea>
        </div>
        <button type="submit" class="feedback-submit" :disabled="sending">
          {{ sending ? 'Sending…' : 'Send Feedback' }}
        </button>
        <p v-if="sent" class="feedback-success">Thank you! We got your feedback.</p>
        <p v-if="error" class="feedback-error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { apiFetch } from '../composables/useApi'

const types = [
  { value: 'general', label: 'General' },
  { value: 'ui', label: 'UI/Design' },
  { value: 'performance', label: 'Performance' },
  { value: 'bug', label: 'Bug Report' },
  { value: 'feature', label: 'Feature Request' },
]

const formData = reactive({ type: 'general', rating: 5, message: '' })
const sending = ref(false)
const sent = ref(false)
const error = ref('')

async function submit() {
  if (!formData.message.trim()) return
  sending.value = true
  error.value = ''
  sent.value = false
  try {
    await apiFetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: formData.type,
        rating: formData.rating,
        message: formData.message.trim(),
      }),
    })
    sent.value = true
    formData.message = ''
    window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Thank you for your feedback!', type: 'success' } }))
  } catch (e) {
    error.value = e?.message || 'Could not send. Try again.'
  } finally {
    sending.value = false
  }
}
</script>

<style scoped>
.feedback-page { padding-bottom: 3rem; }
.feedback-hero.podcasts-hero .podcasts-hero-inner h1 { margin: 0 0 6px 0; font-size: 28px; font-weight: 700; }
.feedback-hero.podcasts-hero .podcasts-hero-inner p { margin: 0; color: rgba(255,255,255,0.68); }
.feedback-container { max-width: 560px; margin: 0 auto; padding: 1.5rem; }
.feedback-form { display: flex; flex-direction: column; gap: 1.25rem; }
.form-section h3 { margin: 0 0 0.5rem; font-size: 0.95rem; color: rgba(255,255,255,0.9); }
.feedback-types { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.feedback-type-label { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; color: rgba(255,255,255,0.8); font-size: 0.9rem; }
.star-rating { display: flex; gap: 4px; }
.star-btn { background: none; border: none; color: rgba(255,255,255,0.3); cursor: pointer; font-size: 1.25rem; padding: 4px; }
.star-btn.on { color: #fbbf24; }
.feedback-textarea { width: 100%; padding: 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.15); background: rgba(0,0,0,0.3); color: #fff; font-size: 1rem; resize: vertical; }
.feedback-submit { padding: 12px 24px; border-radius: 12px; background: var(--accent-primary, #6ddcff); color: #111; font-weight: 600; border: none; cursor: pointer; }
.feedback-submit:disabled { opacity: 0.7; cursor: not-allowed; }
.feedback-success { color: #4ade80; margin: 0; }
.feedback-error { color: #f87171; margin: 0; }
</style>
