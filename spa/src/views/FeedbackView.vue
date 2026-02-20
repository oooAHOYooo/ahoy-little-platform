<template>
  <div class="feedback-page">
    <div class="feedback-container">
      <section class="podcasts-hero feedback-header">
        <div class="podcasts-hero-inner">
          <h1>
            <i class="fas fa-comment" aria-hidden="true"></i>
            Feedback
          </h1>
          <p>Help us improve Ahoy for the upcoming Poetry Event!</p>
        </div>
      </section>

      <div class="feedback-content">
        <!-- Feedback Form -->
        <div v-if="!submitted" class="neu-card">
          <h2><i class="fas fa-edit"></i> Share your thoughts</h2>
          <form @submit.prevent="submitFeedback">
            <div class="form-group">
              <label for="feedback-type">What's this about?</label>
              <select id="feedback-type" v-model="form.type" class="neu-select">
                <option value="general">General Feedback</option>
                <option value="bug">Report a Bug</option>
                <option value="feature">Feature Request</option>
                <option value="artist">Artist Suggestion</option>
              </select>
            </div>

            <div class="form-group">
              <label for="feedback-message">Message</label>
              <textarea 
                id="feedback-message" 
                v-model="form.message" 
                placeholder="Tell us what's on your mind... (max 2000 chars)" 
                maxlength="2000"
                class="neu-textarea"
                required
              ></textarea>
            </div>

            <div class="feedback-footer">
              <p class="reward-hint">
                <i class="fas fa-sparkles"></i>
                Submit feedback to get a sticker claim code!
              </p>
              <button 
                type="submit" 
                class="neu-btn neu-btn-primary submit-btn" 
                :disabled="isSubmitting"
              >
                <i class="fas" :class="isSubmitting ? 'fa-spinner fa-spin' : 'fa-paper-plane'"></i>
                {{ isSubmitting ? 'Sending...' : 'Submit Feedback' }}
              </button>
            </div>
          </form>
        </div>

        <!-- Success Message -->
        <div v-else class="neu-card feedback-success">
          <div class="success-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <h2>Thank you!</h2>
          <p>Your feedback helps us make Ahoy better.</p>
          
          <div class="claim-code-card">
            <p class="claim-label">Sticker Claim Code</p>
            <div class="claim-code">{{ claimCode }}</div>
            <p class="claim-instructions">
              Show this code at the merch table during the Poetry Event to claim your sticker!
            </p>
          </div>

          <button class="neu-btn neu-btn-secondary" @click="resetForm">
            <i class="fas fa-plus"></i>
            Send more feedback
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { apiFetch } from '../composables/useApi'

const submitted = ref(false)
const isSubmitting = ref(false)
const claimCode = ref('')

const form = reactive({
  type: 'general',
  message: ''
})

async function submitFeedback() {
  if (!form.message.trim()) return
  
  isSubmitting.value = true
  try {
    const data = await apiFetch('/api/feedback/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    
    if (data.success) {
      claimCode.value = data.claim_code
      submitted.value = true
      window.dispatchEvent(new CustomEvent('ahoy:toast', { 
        detail: { message: 'Feedback submitted! Thank you.', type: 'success' } 
      }))
    } else {
      throw new Error(data.error || 'Submission failed')
    }
  } catch (err) {
    console.error('Feedback error:', err)
    window.dispatchEvent(new CustomEvent('ahoy:toast', { 
      detail: { message: 'Failed to submit feedback. Please try again.', type: 'error' } 
    }))
  } finally {
    isSubmitting.value = false
  }
}

function resetForm() {
  submitted.value = false
  form.message = ''
  form.type = 'general'
  claimCode.value = ''
}
</script>

<style scoped>
.feedback-page {
  min-height: 100vh;
  background: #0e0e10;
  padding: 24px 16px 80px;
}
.feedback-container {
  max-width: 640px;
  margin: 0 auto;
}
.feedback-header.podcasts-hero .podcasts-hero-inner h1 {
  margin: 0 0 6px 0;
  font-size: 28px;
  font-weight: 700;
}
.feedback-header.podcasts-hero .podcasts-hero-inner p {
  margin: 0;
  color: rgba(255, 255, 255, 0.68);
}

.feedback-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.neu-card {
  background: #18181b;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  box-shadow: 8px 8px 20px rgba(0, 0, 0, 0.6), -4px -4px 12px rgba(255, 255, 255, 0.02);
}
.neu-card h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-group {
  margin-bottom: 20px;
}
.form-group label {
  display: block;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 8px;
}

.neu-select, .neu-textarea {
  width: 100%;
  background: #0e0e10;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  color: white;
  padding: 12px 16px;
  font-size: 15px;
  box-shadow: inset 2px 2px 5px rgba(0,0,0,0.5);
  outline: none;
  transition: border-color 0.2s;
}

.neu-select:focus, .neu-textarea:focus {
  border-color: rgba(139, 92, 246, 0.5);
}

.neu-textarea {
  min-height: 150px;
  resize: vertical;
}

.feedback-footer {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
  margin-top: 24px;
}

.reward-hint {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
  background: rgba(139, 92, 246, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.submit-btn {
  width: 100%;
  justify-content: center;
  padding: 16px;
}

.feedback-success {
  text-align: center;
}
.success-icon {
  font-size: 48px;
  color: #10b981;
  margin-bottom: 16px;
}

.claim-code-card {
  background: rgba(139, 92, 246, 0.05);
  border: 2px dashed rgba(139, 92, 246, 0.3);
  border-radius: 16px;
  padding: 32px;
  margin: 24px 0;
}
.claim-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 12px;
}
.claim-code {
  font-family: 'Courier New', Courier, monospace;
  font-size: 32px;
  font-weight: 800;
  color: #8b5cf6;
  letter-spacing: 2px;
}
.claim-instructions {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 16px;
  line-height: 1.5;
}

.neu-btn {
  padding: 12px 24px;
  border-radius: 12px;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}
.neu-btn-primary {
  background: linear-gradient(135deg, #1e1b2e, #1a1730);
  color: rgba(139, 92, 246, 0.9);
  box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.5), -3px -3px 8px rgba(255, 255, 255, 0.02);
}
.neu-btn-primary:active {
  box-shadow: inset 2px 2px 5px rgba(0,0,0,0.5);
}
.neu-btn-secondary {
  background: #18181b;
  color: rgba(255, 255, 255, 0.5);
  box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.5), -3px -3px 8px rgba(255, 255, 255, 0.02);
}
</style>
