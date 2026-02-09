<template>
  <div class="wallet-page">
    <section class="podcasts-hero wallet-hero">
      <div class="podcasts-hero-inner">
        <h1><i class="fas fa-wallet"></i> Wallet</h1>
        <p>Balance and transaction history</p>
      </div>
    </section>

    <div class="wallet-content">
      <div class="wallet-actions">
        <router-link to="/account" class="wallet-back">
          <i class="fas fa-arrow-left"></i> Back to Account
        </router-link>
      </div>

      <div v-if="!auth.isLoggedIn.value" class="wallet-guest">
        <p>Sign in to view your wallet.</p>
        <router-link to="/login" class="wallet-btn primary">Sign in</router-link>
      </div>

      <template v-else>
        <div class="wallet-balance-card">
          <span class="wallet-balance-label">Current Balance</span>
          <span class="wallet-balance-amount">{{ formatCurrency(balance) }}</span>
        </div>

        <div class="wallet-card">
          <div class="wallet-card-header">
            <h2>Transaction History</h2>
            <button type="button" class="wallet-refresh" :disabled="loading" @click="load" title="Refresh">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
            </button>
          </div>
          <div class="wallet-card-body">
            <div v-if="loading" class="wallet-state">
              <i class="fas fa-spinner fa-spin"></i>
              <p>Loading transactions...</p>
            </div>
            <div v-else-if="error" class="wallet-state wallet-error">
              <i class="fas fa-exclamation-triangle"></i>
              <p>{{ error }}</p>
              <button type="button" class="wallet-btn primary" @click="load">Try Again</button>
            </div>
            <div v-else-if="transactions.length === 0" class="wallet-state">
              <i class="fas fa-wallet"></i>
              <p>No transactions yet</p>
              <router-link to="/account" class="wallet-btn primary">Add Funds</router-link>
            </div>
            <div v-else class="wallet-table-wrap">
              <table class="wallet-table">
                <thead>
                  <tr>
                    <th>Date & Time</th>
                    <th>Type</th>
                    <th>Description</th>
                    <th class="num">Amount</th>
                    <th class="num">Balance After</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="tx in transactions" :key="tx.id">
                    <td>
                      <div>{{ formatDate(tx.created_at) }}</div>
                      <div class="wallet-time">{{ formatTime(tx.created_at) }}</div>
                    </td>
                    <td>
                      <span class="wallet-type" :class="tx.type">{{ txTypeLabel(tx.type) }}</span>
                    </td>
                    <td>{{ tx.description || '—' }}</td>
                    <td class="num" :class="tx.type === 'fund' ? 'positive' : tx.type === 'spend' ? 'negative' : 'neutral'">
                      {{ tx.type === 'fund' ? '+' : '-' }}{{ formatCurrency(Math.abs(tx.amount)) }}
                    </td>
                    <td class="num">{{ formatCurrency(tx.balance_after) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-if="transactions.length >= limit && !loading" class="wallet-load-more">
              <button type="button" class="wallet-btn secondary" :disabled="loadingMore" @click="loadMore">
                <i v-if="loadingMore" class="fas fa-spinner fa-spin"></i>
                {{ loadingMore ? 'Loading...' : 'Load More' }}
              </button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'
import { apiFetch } from '../composables/useApi'

const auth = useAuth()
const balance = ref(0)
const transactions = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const error = ref(null)
const limit = 50
const offset = ref(0)

async function load() {
  if (!auth.isLoggedIn.value) return
  loading.value = true
  error.value = null
  try {
    const [balRes, txRes] = await Promise.all([
      apiFetch('/payments/wallet'),
      apiFetch(`/payments/wallet/transactions?limit=${limit}`),
    ])
    balance.value = balRes.balance ?? 0
    transactions.value = txRes.transactions ?? []
    offset.value = transactions.value.length
  } catch (e) {
    error.value = 'Failed to load transactions. Please try again.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (loadingMore.value || transactions.value.length < offset.value) return
  loadingMore.value = true
  try {
    const data = await apiFetch(`/payments/wallet/transactions?limit=${limit}&offset=${offset.value}`)
    const list = data.transactions || []
    if (list.length) {
      transactions.value = [...transactions.value, ...list]
      offset.value = transactions.value.length
    }
  } catch (e) {
    console.error(e)
  } finally {
    loadingMore.value = false
  }
}

onMounted(() => { if (auth.isLoggedIn.value) load() })

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount ?? 0)
}
function formatDate(dateString) {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}
function formatTime(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
}
function txTypeLabel(type) {
  if (!type) return '—'
  return type.charAt(0).toUpperCase() + type.slice(1)
}
</script>

<style scoped>
.wallet-page { min-height: 100vh; background: var(--page-bg, #0a0a0a); }
.wallet-hero.podcasts-hero .podcasts-hero-inner h1 { margin: 0 0 6px 0; }
.wallet-content { max-width: 900px; margin: 0 auto; padding: 1.5rem 1rem; }
.wallet-actions { margin-bottom: 1rem; }
.wallet-back {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--accent-primary, #6ddcff);
  text-decoration: none;
  font-size: 0.95rem;
}
.wallet-back:hover { text-decoration: underline; }
.wallet-balance-card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.wallet-balance-label { color: rgba(255,255,255,0.7); font-weight: 500; }
.wallet-balance-amount { font-size: 1.75rem; font-weight: 700; color: #fff; }
.wallet-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  overflow: hidden;
}
.wallet-card-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.wallet-card-header h2 { margin: 0; font-size: 1.1rem; color: #fff; }
.wallet-refresh {
  background: none;
  border: none;
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  padding: 0.5rem;
}
.wallet-refresh:hover { color: #fff; }
.wallet-card-body { padding: 1.5rem; }
.wallet-state {
  text-align: center;
  padding: 2rem;
  color: rgba(255,255,255,0.6);
}
.wallet-state i { font-size: 2rem; display: block; margin-bottom: 0.5rem; opacity: 0.7; }
.wallet-state p { margin: 0 0 1rem; }
.wallet-error i { color: #f59e0b; }
.wallet-table-wrap { overflow-x: auto; }
.wallet-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.wallet-table th, .wallet-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.06); }
.wallet-table th { color: rgba(255,255,255,0.6); font-weight: 600; }
.wallet-table td { color: rgba(255,255,255,0.9); }
.wallet-table th.num, .wallet-table td.num { text-align: right; }
.wallet-time { font-size: 0.75rem; color: rgba(255,255,255,0.5); }
.wallet-type {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
}
.wallet-type.fund { background: rgba(34,197,94,0.2); color: #86efac; }
.wallet-type.spend { background: rgba(239,68,68,0.2); color: #fca5a5; }
.wallet-type.refund { background: rgba(59,130,246,0.2); color: #93c5fd; }
.wallet-table td.positive { color: #86efac; }
.wallet-table td.negative { color: #fca5a5; }
.wallet-table td.neutral { color: #93c5fd; }
.wallet-load-more { text-align: center; margin-top: 1rem; }
.wallet-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  border: none;
  cursor: pointer;
  font-size: 0.95rem;
}
.wallet-btn.primary { background: var(--accent-primary, #6ddcff); color: #111; }
.wallet-btn.secondary { background: rgba(255,255,255,0.1); color: #fff; border: 1px solid rgba(255,255,255,0.2); }
.wallet-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.wallet-guest { text-align: center; padding: 3rem 1rem; color: rgba(255,255,255,0.7); }
.wallet-guest p { margin-bottom: 1rem; }
@media (max-width: 768px) {
  .wallet-table th:nth-child(3), .wallet-table td:nth-child(3) { display: none; }
}
</style>
