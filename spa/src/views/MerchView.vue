<template>
  <div>
    <div class="page-header">
      <h1>Merch</h1>
    </div>

    <div class="content-grid" v-if="items.length">
      <div class="card" v-for="item in items" :key="item.id">
        <img :src="item.image_url" :alt="item.name" class="card-image" loading="lazy" />
        <div class="card-body">
          <div class="card-title">{{ item.name }}</div>
          <div class="card-subtitle">${{ item.price_usd.toFixed(2) }}</div>
        </div>
      </div>
    </div>

    <div class="content-grid" v-else>
      <div class="card" v-for="i in 4" :key="i">
        <div class="card-image skeleton"></div>
        <div class="card-body"><div class="skeleton" style="height:14px;width:80%"></div></div>
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
