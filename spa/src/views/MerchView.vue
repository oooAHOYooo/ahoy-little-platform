<template>
  <div class="merch-shell">
    <!-- Subpage hero (same as Flask subpage_hero) -->
    <section class="podcasts-hero">
      <div class="podcasts-hero-inner">
        <h1>
          <i class="fas fa-shopping-bag" aria-hidden="true"></i>
          Merch
        </h1>
        <p>Support Ahoy with limited drops and essentials.</p>
      </div>
    </section>

    <!-- Desktop hero (Flask: merch-hero desktop-only) -->
    <div class="merch-hero desktop-only">
      <h1>Merch</h1>
      <p>Support Ahoy with limited drops and essentials. Fast checkout, easy quantities.</p>
    </div>

    <!-- Controls: search + sort (Flask: merch-controls) -->
    <div class="merch-controls">
      <div class="merch-search" role="search">
        <i class="fas fa-search" aria-hidden="true"></i>
        <input
          v-model="q"
          type="search"
          placeholder="Search merch…"
          aria-label="Search merch"
        />
      </div>
      <div class="merch-pill">
        <span style="opacity:.7;font-size:12px;letter-spacing:.08em;text-transform:uppercase;">Sort</span>
        <select v-model="sort" aria-label="Sort merch">
          <option value="featured">Featured</option>
          <option value="low">Price: Low</option>
          <option value="high">Price: High</option>
          <option value="az">Name: A–Z</option>
        </select>
      </div>
    </div>

    <!-- Grid (Flask: merch-grid, merch-card) -->
    <div v-if="filteredItems.length" class="merch-grid">
      <div
        v-for="i in filteredItems"
        :key="i.id"
        class="merch-card"
        :class="{ 'sale-pending': isPurchased(i) }"
      >
        <div
          class="merch-media"
          @mouseenter="hoverBack[i.id] = !!i.image_url_back"
          @mouseleave="hoverBack[i.id] = false"
        >
          <img
            :src="(hoverBack[i.id] && i.image_url_back) ? i.image_url_back : (i.image_url || '/static/img/default-cover.jpg')"
            :alt="i.name || i.id"
            loading="lazy"
            decoding="async"
            :title="hoverBack[i.id] ? 'Back view' : 'Front view'"
            @error="onMerchImageError($event, i)"
          />
          <div v-if="i.image_url_back" class="image-toggle-hint">
            <i class="fas fa-sync-alt"></i>
            <span>Hover to see back</span>
          </div>
          <div v-if="isPurchased(i)" class="sale-pending-badge">
            <i class="fas fa-clock" aria-hidden="true"></i>
            <span>Sale Pending</span>
          </div>
        </div>
        <div class="merch-body">
          <div class="merch-top">
            <h3 class="merch-title">{{ i.name || i.id }}</h3>
            <div class="merch-price">
              <div class="usd">{{ i.price_usd != null ? '$' + (+i.price_usd).toFixed(2) : '—' }}</div>
              <div class="sub">USD</div>
            </div>
          </div>
          <div class="merch-chips">
            <span v-for="c in chipsFor(i)" :key="c" class="merch-chip">{{ c }}</span>
          </div>
          <div class="merch-actions">
            <input
              class="qty"
              type="number"
              min="1"
              max="1"
              value="1"
              :id="'qty_' + (i.id || '')"
              disabled
              aria-label="Quantity"
              title="One-of-a-kind item"
            />
            <a
              class="merch-cta"
              :class="{ disabled: isPurchased(i) }"
              href="#"
              @click.prevent="isPurchased(i) ? null : checkout(i)"
            >
              <span>{{ isPurchased(i) ? 'Sold' : 'Checkout' }}</span>
              <i :class="isPurchased(i) ? 'fas fa-lock' : 'fas fa-arrow-right'" aria-hidden="true"></i>
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state (Flask: merch-empty) -->
    <div v-else-if="!loading" class="merch-empty">
      No merch items found yet. Add images to <code>static/merch/images/</code> and run
      <code>python manifest.py merch</code> to generate <code>data/merch.json</code>.
    </div>

    <!-- Loading skeletons -->
    <div v-else class="merch-grid">
      <div v-for="j in 6" :key="j" class="merch-card">
        <div class="merch-media skeleton" style="aspect-ratio:4/3"></div>
        <div class="merch-body">
          <div class="skeleton" style="height:14px;width:60%;margin-bottom:6px"></div>
          <div class="skeleton" style="height:12px;width:30%"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'

const items = ref([])
const purchasedItemIds = ref(new Set())
const loading = ref(true)
const q = ref('')
const sort = ref('featured')
const hoverBack = ref({})

function norm(s) {
  return String(s || '').toLowerCase()
}

function isMerch(i) {
  const k = norm(i && (i.kind || i.type || i.category))
  return !['theme', 'themes', 'subscription', 'subscriptions', 'membership', 'memberships'].includes(k)
}

const filteredItems = computed(() => {
  let out = Array.isArray(items.value) ? [...items.value] : []
  out = out.filter((i) => isMerch(i))
  const query = norm(q.value)
  if (query) out = out.filter((i) => norm(i.name || i.id).includes(query))
  if (sort.value === 'low') out.sort((a, b) => (+a.price_usd || 0) - (+b.price_usd || 0))
  else if (sort.value === 'high') out.sort((a, b) => (+b.price_usd || 0) - (+a.price_usd || 0))
  else if (sort.value === 'az') out.sort((a, b) => String(a.name || a.id || '').localeCompare(String(b.name || b.id || '')))
  return out
})

function isPurchased(i) {
  if (!i || !i.id) return false
  return purchasedItemIds.value.has(String(i.id))
}

function chipsFor(i) {
  const name = norm(i.name || i.id)
  const price = +i.price_usd || 0
  const chips = []
  if (name.includes('limited') || name.includes('drop')) chips.push('Limited Drop')
  if (name.includes('bundle')) chips.push('Bundle')
  if (price >= 50) chips.push('Collector')
  else chips.push('Supporter')
  return chips.slice(0, 2)
}

function checkout(i) {
  if (isPurchased(i)) return
  const id = encodeURIComponent(i.id || '')
  const title = encodeURIComponent(i.name || i.id || 'Merch')
  const amount = encodeURIComponent(i.price_usd ?? '')
  const qtyEl = document.getElementById('qty_' + (i.id || ''))
  const qty = encodeURIComponent((qtyEl && qtyEl.value) ? qtyEl.value : '1')
  window.location.assign(`/checkout?type=merch&item_id=${id}&qty=${qty}&amount=${amount}&title=${title}`)
}

const defaultCover = '/static/img/default-cover.jpg'
function onMerchImageError(event, item) {
  const el = event?.target
  if (!el || el.dataset.merchFallback) return
  el.dataset.merchFallback = '1'
  const back = hoverBack.value[item?.id] && item?.image_url_back
  if (back && el.src === item?.image_url_back) {
    el.src = item?.image_url || defaultCover
  } else {
    el.src = defaultCover
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const data = await apiFetchCached('/api/merch')
    items.value = data.items || []
    purchasedItemIds.value = new Set((data.purchased_item_ids || []).map(String))
  } catch {
    items.value = []
    purchasedItemIds.value = new Set()
  }
  loading.value = false
})
</script>
