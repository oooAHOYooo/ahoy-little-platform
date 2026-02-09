<template>
  <div class="tip-artist-page">
    <section class="podcasts-hero tip-hero">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-heart"></i> Boost Artists</h1>
        <p>Support the indie artists you love</p>
      </div>
    </section>

    <div class="tip-content">
      <div class="tip-grid">
        <!-- Left: Form -->
        <div class="tip-card tip-form-card">
          <h2><i class="fas fa-user-music"></i> Select Artist</h2>
          <div class="tip-field">
            <label>Choose an Artist</label>
            <select v-model="selectedArtist" @change="onArtistChange" class="tip-select">
              <option value="">-- Select an artist --</option>
              <option v-for="a in artists" :key="a.id || a.name" :value="a.name">{{ a.name }}</option>
            </select>
          </div>
          <div v-if="selectedArtistInfo" class="tip-artist-preview">
            <img v-if="selectedArtistInfo?.image" :src="selectedArtistInfo.image" alt="" class="tip-artist-img" @error="($event.target).style.display='none'" />
            <div v-else class="tip-artist-placeholder"><i class="fas fa-user-music"></i></div>
            <div>
              <h3>{{ selectedArtist }}</h3>
              <p class="tip-artist-desc">{{ selectedArtistInfo.description || 'Indie artist' }}</p>
            </div>
          </div>
          <div class="tip-field">
            <label>Amount (USD)</label>
            <div class="tip-amount-btns">
              <button v-for="amt in [5, 10, 25, 50]" :key="amt" type="button" class="tip-amount-btn" :class="{ active: tipAmount === amt }" @click="tipAmount = amt">${{ amt }}</button>
            </div>
            <input v-model.number="tipAmount" type="number" min="1" step="1" class="tip-input" placeholder="Or enter custom amount" />
          </div>
          <div class="tip-field">
            <label>Optional Message</label>
            <textarea v-model="tipNote" class="tip-textarea" placeholder="Leave a message for the artist..." rows="3"></textarea>
          </div>
          <button type="button" class="tip-submit" :disabled="!selectedArtist || !tipAmount || tipAmount < 1 || loading" @click="submitTip">
            <i v-if="loading" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-heart"></i>
            Boost ${{ (tipAmount || 0).toFixed(0) }}
          </button>
        </div>

        <!-- Right: Recent tips -->
        <div class="tip-card tip-history-card">
          <h2><i class="fas fa-history"></i> Your Boosts</h2>
          <div v-if="recentTips.length === 0" class="tip-empty">
            <i class="fas fa-inbox"></i>
            <p>No boosts yet. Start supporting artists!</p>
          </div>
          <div v-else class="tip-list">
            <div v-for="tip in recentTips" :key="tip.id" class="tip-item">
              <div class="tip-item-main">
                <h4>{{ tip.artist_name }}</h4>
                <p class="tip-item-date">{{ formatDate(tip.created_at) }}</p>
                <p v-if="tip.note" class="tip-item-note">"{{ tip.note }}"</p>
              </div>
              <div class="tip-item-amount">${{ (tip.amount / 100).toFixed(2) }}</div>
            </div>
          </div>
          <div v-if="recentTips.length > 0" class="tip-total">
            <span>Total Boosts:</span>
            <span>${{ (totalTipsCents / 100).toFixed(2) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { apiFetch } from '../composables/useApi'

const router = useRouter()
const auth = useAuth()

const artists = ref([])
const selectedArtist = ref('')
const selectedArtistInfo = computed(() => selectedArtist.value ? artists.value.find(a => a.name === selectedArtist.value) || null : null)
const tipAmount = ref(10)
const tipNote = ref('')
const loading = ref(false)
const recentTips = ref([])
const totalTipsCents = computed(() => recentTips.value.reduce((s, t) => s + (t.amount || 0), 0))

onMounted(async () => {
  if (!auth.isLoggedIn.value) {
    router.push('/login')
    return
  }
  await loadArtists()
  await loadRecentTips()
})

function onArtistChange() {
  // selectedArtistInfo is computed
}

async function loadArtists() {
  try {
    const data = await apiFetch('/api/artists')
    const list = data.artists || []
    try {
      const music = await apiFetch('/api/music')
      const names = new Set(list.map(a => a.name))
      ;(music.tracks || []).forEach(t => { if (t.artist && !names.has(t.artist)) { list.push({ name: t.artist, id: `artist_${t.artist}`, description: 'Indie artist' }); names.add(t.artist) } })
    } catch {}
    list.sort((a, b) => (a.name || '').localeCompare(b.name || ''))
    artists.value = list
  } catch (e) {
    console.error(e)
  }
}

async function loadRecentTips() {
  try {
    const data = await apiFetch('/api/tips')
    recentTips.value = data.tips || []
  } catch (e) {
    console.error(e)
  }
}

async function submitTip() {
  if (!selectedArtist.value || !tipAmount.value || tipAmount.value < 1) return
  loading.value = true
  try {
    await apiFetch('/api/tips', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        artist_name: selectedArtist.value,
        amount: Math.round(Number(tipAmount.value) * 100),
        note: (tipNote.value || '').slice(0, 500),
      }),
    })
    selectedArtist.value = ''
    tipAmount.value = 10
    tipNote.value = ''
    await loadRecentTips()
    window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Boost sent!', type: 'success' } }))
  } catch (e) {
    const msg = e.message || 'Failed to send boost'
    window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: msg, type: 'error' } }))
  } finally {
    loading.value = false
  }
}

function formatDate(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.tip-artist-page { min-height: 100vh; background: var(--page-bg, #0a0a0a); }
.tip-hero.podcasts-hero .podcasts-hero-inner h1 { margin: 0 0 6px 0; }
.tip-hero .fa-heart { color: #e17055; }
.tip-content { max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; }
.tip-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
@media (max-width: 768px) { .tip-grid { grid-template-columns: 1fr; } }
.tip-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 1.5rem;
}
.tip-card h2 { font-size: 1.25rem; margin: 0 0 1rem; color: #fff; }
.tip-card h2 i { margin-right: 8px; opacity: 0.8; }
.tip-field { margin-bottom: 1rem; }
.tip-field label { display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.7); font-weight: 500; }
.tip-select, .tip-input, .tip-textarea {
  width: 100%;
  padding: 0.75rem;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  color: #fff;
  font-size: 1rem;
  box-sizing: border-box;
}
.tip-textarea { resize: vertical; min-height: 80px; }
.tip-amount-btns { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.5rem; }
.tip-amount-btn {
  padding: 0.5rem 1rem;
  background: rgba(255,255,255,0.1);
  border: 2px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}
.tip-amount-btn.active { border-color: var(--accent-primary, #6ddcff); background: rgba(109,220,255,0.2); }
.tip-artist-preview {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255,255,255,0.03);
  border-radius: 8px;
  margin-bottom: 1rem;
}
.tip-artist-img { width: 60px; height: 60px; border-radius: 8px; object-fit: cover; }
.tip-artist-placeholder { width: 60px; height: 60px; border-radius: 8px; background: rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,0.4); font-size: 1.5rem; }
.tip-artist-preview h3 { margin: 0; color: #fff; font-size: 1rem; }
.tip-artist-desc { margin: 0.25rem 0 0; color: #999; font-size: 0.875rem; }
.tip-submit {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #e17055, #ff0066);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: 0.5rem;
}
.tip-submit:disabled { opacity: 0.5; cursor: not-allowed; }
.tip-submit:not(:disabled):hover { opacity: 0.95; transform: scale(1.01); }
.tip-list { max-height: 400px; overflow-y: auto; }
.tip-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem;
  background: rgba(255,255,255,0.03);
  border-radius: 8px;
  margin-bottom: 0.75rem;
}
.tip-item-main h4 { margin: 0; color: #fff; font-size: 1rem; }
.tip-item-date { margin: 0.25rem 0 0; color: #999; font-size: 0.875rem; }
.tip-item-note { margin: 0.5rem 0 0; color: #ccc; font-size: 0.85rem; font-style: italic; }
.tip-item-amount { font-size: 1.25rem; font-weight: 600; color: var(--accent-primary, #6ddcff); }
.tip-empty { text-align: center; padding: 2rem; color: #999; }
.tip-empty i { font-size: 2.5rem; opacity: 0.5; display: block; margin-bottom: 0.5rem; }
.tip-total {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255,255,255,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: rgba(255,255,255,0.8);
}
.tip-total span:last-child { font-size: 1.25rem; color: var(--accent-primary, #6ddcff); }
</style>
