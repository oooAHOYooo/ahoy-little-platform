<template>
  <div class="beta-tester-page">
    <div class="beta-container">
      <header class="beta-header">
        <h1>Beta Program</h1>
        <p class="subtitle">Join the early beta testers</p>
      </header>

      <section class="beta-benefit-card neu-card pulse-border">
        <h2>Beta Program Information</h2>
        <p>We're looking for early adopters to help us test the mobile version of Ahoy. To get on the app store app store - we need some brave souls, to tell us what they like, and didn't like about it all.</p>
      </section>

      <div class="beta-steps-grid">
        <!-- Android Section -->
        <article class="beta-platform-card neu-card">
          <div class="platform-header">
            <h3>Android</h3>
            <span class="platform-tag">Google Play Store</span>
          </div>
          <div class="steps-list">
            <div class="step-item">
              <span class="step-num">1</span>
              <p>Open the <strong>Google Play Store</strong> on your Android device.</p>
            </div>
            <div class="step-item">
              <span class="step-num">2</span>
              <p>Search for <strong>"Ahoy Indie Media"</strong>.</p>
            </div>
            <div class="step-item">
              <span class="step-num">3</span>
              <p>Scroll down to the <strong>"Join the beta"</strong> section.</p>
            </div>
            <div class="step-item">
              <span class="step-num">4</span>
              <p>Tap <strong>"Join"</strong> and wait a few minutes for the update.</p>
            </div>
          </div>
        </article>

        <!-- iOS Section -->
        <article class="beta-platform-card neu-card">
          <div class="platform-header">
            <h3>iOS</h3>
            <span class="platform-tag">Apple TestFlight</span>
          </div>
          <div class="steps-list">
            <div class="step-item">
              <span class="step-num">1</span>
              <p>Download the <strong>TestFlight</strong> app from the iOS App Store.</p>
            </div>
            <div class="step-item">
              <span class="step-num">2</span>
              <p>Sign up below with your Apple ID email.</p>
            </div>
            <div class="step-item">
              <span class="step-num">3</span>
              <p>Wait for an invite email from <strong>TestFlight</strong>.</p>
            </div>
            <div class="step-item">
              <span class="step-num">4</span>
              <p>Open the link in the email to install Ahoy via TestFlight.</p>
            </div>
          </div>
        </article>
      </div>

      <section class="signup-section neu-card">
        <h2>Claim Your Stickers</h2>
        <form @submit.prevent="handleSignup" class="signup-form">
          <div class="form-group">
            <label for="email">Email Address</label>
            <input 
              type="email" 
              id="email" 
              v-model="form.email" 
              placeholder="Enter your email" 
              required
              class="neu-input"
            />
          </div>
          <div class="form-group">
            <label>Your Platform</label>
            <div class="platform-radio-group">
              <label class="radio-label">
                <input type="radio" value="android" v-model="form.platform" />
                <span>Android</span>
              </label>
              <label class="radio-label">
                <input type="radio" value="ios" v-model="form.platform" />
                <span>iOS</span>
              </label>
              <label class="radio-label">
                <input type="radio" value="both" v-model="form.platform" />
                <span>Both</span>
              </label>
            </div>
          </div>
          <button type="submit" class="neu-btn neu-btn-primary submit-btn" :disabled="loading">
            {{ loading ? 'Signing up...' : 'Join Beta Program' }}
          </button>
        </form>
        <p v-if="message" :class="['status-message', messageType]">{{ message }}</p>
      </section>

      <footer class="beta-footer">
        <p>Questions? Reach out to <a href="mailto:support@ahoy.ooo">support@ahoy.ooo</a></p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { apiFetch } from '../composables/useApi'

const form = reactive({
  email: '',
  platform: 'android'
})

const loading = ref(false)
const message = ref('')
const messageType = ref('')

async function handleSignup() {
  loading.value = true
  message.value = ''
  
  try {
    const response = await apiFetch('/api/beta/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    
    if (response.ok) {
      message.value = response.message || 'Successfully signed up!'
      messageType.value = 'success'
      form.email = ''
    } else {
      message.value = response.error || 'Something went wrong. Please try again.'
      messageType.value = 'error'
    }
  } catch (err) {
    message.value = 'Failed to connect to server. Please try again later.'
    messageType.value = 'error'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.beta-tester-page {
  min-height: 100vh;
  background: #0e0e10;
  padding: 40px 20px 80px;
  color: #fff;
}

.beta-container {
  max-width: 800px;
  margin: 0 auto;
}

.beta-header {
  text-align: center;
  margin-bottom: 40px;
}

.beta-header h1 {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.6);
}

.neu-card {
  background: #18181b;
  border-radius: 20px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 10px 10px 30px rgba(0, 0, 0, 0.5), -5px -5px 20px rgba(255, 255, 255, 0.02);
}

.beta-benefit-card {
  text-align: center;
  margin-bottom: 40px;
  background: linear-gradient(145deg, #1e1b2e, #18181b);
}

.beta-benefit-card h2 {
  color: #f59e0b;
  margin-bottom: 12px;
}

.pulse-border {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.3); }
  70% { box-shadow: 0 0 0 15px rgba(245, 158, 11, 0); }
  100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
}

.beta-steps-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 40px;
}

.platform-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.platform-tag {
  font-size: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  padding: 4px 10px;
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.4);
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.step-num {
  width: 24px;
  height: 24px;
  background: #8b5cf6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
  flex-shrink: 0;
}

.signup-section h2 {
  margin-bottom: 24px;
  text-align: center;
}

.signup-form {
  max-width: 400px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
}

.neu-input {
  width: 100%;
  background: #0e0e10;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px 16px;
  border-radius: 12px;
  color: #fff;
  outline: none;
  transition: border-color 0.2s;
}

.neu-input:focus {
  border-color: #8b5cf6;
}

.platform-radio-group {
  display: flex;
  gap: 15px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.9rem;
}

.neu-btn {
  width: 100%;
  padding: 14px;
  border-radius: 12px;
  border: none;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.1s, box-shadow 0.2s;
}

.neu-btn-primary {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: #fff;
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
}

.neu-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
}

.neu-btn-primary:active {
  transform: translateY(0);
}

.status-message {
  margin-top: 16px;
  text-align: center;
  font-size: 0.9rem;
}

.status-message.success { color: #10b981; }
.status-message.error { color: #ef4444; }

.beta-footer {
  margin-top: 40px;
  text-align: center;
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.85rem;
}

.beta-footer a {
  color: #8b5cf6;
  text-decoration: none;
}

@media (max-width: 600px) {
  .beta-steps-grid {
    grid-template-columns: 1fr;
  }
}
</style>
