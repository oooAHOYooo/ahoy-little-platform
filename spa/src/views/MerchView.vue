<template>
  <div class="merch-shell">
    <div class="merch-hero">
      <h1>Merch</h1>
    </div>

    <div class="merch-grid" v-if="items.length">
      <div class="merch-card" v-for="item in items" :key="item.id">
        <div class="merch-media">
          <img :src="item.image_url" :alt="item.name" loading="lazy" />
        </div>
        <div class="merch-body">
          <div class="merch-top">
            <div class="merch-name">{{ item.name }}</div>
            <div class="merch-price">${{ item.price_usd?.toFixed(2) }}</div>
          </div>
          <div class="merch-chips" v-if="item.tags?.length">
            <span class="merch-chip" v-for="tag in item.tags" :key="tag">{{ tag }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading skeletons -->
    <div class="merch-grid" v-else>
      <div class="merch-card" v-for="i in 4" :key="i">
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
import { ref, onMounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'

const items = ref([])

onMounted(async () => {
  const data = await apiFetchCached('/api/merch').catch(() => ({ items: [] }))
  items.value = data.items || []
})
</script>
