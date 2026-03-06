<template>
  <div class="studio-col-page">
    <!-- Back -->
    <router-link to="/studio" class="studio-back">
      <i class="fas fa-arrow-left"></i> Studio
    </router-link>

    <!-- Loading -->
    <div v-if="loading" class="studio-col-loading">
      <div class="skeleton studio-hero-skel"></div>
      <div style="padding: 20px 0;">
        <div class="skeleton" style="height:26px;width:55%;margin-bottom:12px;border-radius:6px"></div>
        <div class="skeleton" style="height:14px;width:35%;border-radius:4px"></div>
      </div>
      <div class="studio-photo-grid">
        <div v-for="i in 8" :key="i" class="skeleton studio-photo-skel"></div>
      </div>
    </div>

    <!-- Collection detail -->
    <template v-else-if="collection">
      <!-- Hero -->
      <div class="studio-hero">
        <div class="studio-hero-img-wrap">
          <img
            :src="collection.cover || photos[0] || '/static/img/default-cover.jpg'"
            :alt="collection.title"
          />
          <div class="studio-hero-gradient" />
          <div class="studio-hero-meta">
            <div v-if="collection.tag" class="studio-hero-tag">{{ collection.tag }}</div>
            <h1 class="studio-hero-title">{{ collection.title }}</h1>
            <div v-if="collection.date" class="studio-hero-date">{{ formatDate(collection.date) }}</div>
          </div>
        </div>
        <p v-if="collection.description" class="studio-col-desc">{{ collection.description }}</p>
      </div>

      <!-- Photo count bar -->
      <div v-if="photos.length" class="studio-count-bar">
        <i class="fas fa-images"></i>
        {{ photos.length }} photo{{ photos.length !== 1 ? 's' : '' }}
      </div>

      <!-- Photo grid -->
      <div v-if="photos.length" class="studio-photo-grid">
        <button
          v-for="(url, idx) in photos"
          :key="idx"
          class="studio-photo-thumb"
          @click="openLightbox(idx)"
          :aria-label="`View photo ${idx + 1}`"
        >
          <img :src="url" :alt="`${collection.title} — photo ${idx + 1}`" loading="lazy" />
          <div class="studio-thumb-hover">
            <i class="fas fa-expand-alt"></i>
          </div>
        </button>
      </div>

      <div v-else class="studio-no-photos">
        <i class="fas fa-camera"></i>
        <p>Photos coming soon.</p>
      </div>
    </template>

    <!-- Not found -->
    <div v-else class="studio-not-found">
      <i class="fas fa-camera-slash" style="font-size:2.5rem;opacity:0.3;display:block;margin-bottom:12px"></i>
      <h3>Collection not found</h3>
      <router-link to="/studio" class="studio-back" style="margin-top:12px;display:inline-block">← Back to Studio</router-link>
    </div>

    <!-- Lightbox -->
    <Teleport to="body">
      <Transition name="lb-fade">
        <div v-if="lightboxOpen" class="studio-lightbox" @click.self="closeLightbox">
          <!-- Close -->
          <button class="studio-lb-close" @click="closeLightbox" aria-label="Close lightbox">
            <i class="fas fa-times"></i>
          </button>

          <!-- Prev -->
          <button
            v-if="photos.length > 1"
            class="studio-lb-arrow studio-lb-prev"
            @click="prevPhoto"
            aria-label="Previous photo"
          >
            <i class="fas fa-chevron-left"></i>
          </button>

          <!-- Image -->
          <div class="studio-lb-img-wrap" @click.stop>
            <Transition name="lb-img" mode="out-in">
              <img
                :key="lightboxIndex"
                :src="photos[lightboxIndex]"
                :alt="`Photo ${lightboxIndex + 1} of ${photos.length}`"
                class="studio-lb-img"
              />
            </Transition>
          </div>

          <!-- Next -->
          <button
            v-if="photos.length > 1"
            class="studio-lb-arrow studio-lb-next"
            @click="nextPhoto"
            aria-label="Next photo"
          >
            <i class="fas fa-chevron-right"></i>
          </button>

          <!-- Counter -->
          <div class="studio-lb-counter">{{ lightboxIndex + 1 }} / {{ photos.length }}</div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiFetchCached } from '../composables/useApi'

const route = useRoute()
const loading = ref(true)
const collection = ref(null)
const lightboxOpen = ref(false)
const lightboxIndex = ref(0)

const photos = computed(() => {
  if (!collection.value?.photos) return []
  return Array.isArray(collection.value.photos)
    ? collection.value.photos.filter(Boolean)
    : []
})

function formatDate(ds) {
  if (!ds) return ''
  const d = new Date(ds)
  if (isNaN(d.getTime())) return String(ds)
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
}

function openLightbox(idx) {
  lightboxIndex.value = idx
  lightboxOpen.value = true
  document.body.style.overflow = 'hidden'
}

function closeLightbox() {
  lightboxOpen.value = false
  document.body.style.overflow = ''
}

function prevPhoto() {
  lightboxIndex.value = (lightboxIndex.value - 1 + photos.value.length) % photos.value.length
}

function nextPhoto() {
  lightboxIndex.value = (lightboxIndex.value + 1) % photos.value.length
}

function onKeyDown(e) {
  if (!lightboxOpen.value) return
  if (e.key === 'Escape') closeLightbox()
  if (e.key === 'ArrowLeft') prevPhoto()
  if (e.key === 'ArrowRight') nextPhoto()
}

onMounted(async () => {
  loading.value = true
  window.addEventListener('keydown', onKeyDown)
  try {
    const data = await apiFetchCached(`/api/studio/${route.params.id}`)
    collection.value = data
  } catch {
    collection.value = null
  }
  loading.value = false
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.studio-col-page {
  min-height: 60vh;
}

/* Back link */
.studio-back {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.45);
  text-decoration: none;
  margin-bottom: 20px;
  letter-spacing: 0.02em;
  transition: color 0.15s;
}
.studio-back:hover {
  color: rgba(255, 255, 255, 0.85);
}

/* Hero */
.studio-hero {
  margin-bottom: 24px;
}
.studio-hero-img-wrap {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 7;
  overflow: hidden;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.05);
  margin-bottom: 16px;
}
.studio-hero-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.studio-hero-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    transparent 35%,
    rgba(0, 0, 0, 0.75) 100%
  );
}
.studio-hero-meta {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px 22px;
}
.studio-hero-tag {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.55);
  margin-bottom: 6px;
}
.studio-hero-title {
  font-size: clamp(1.5rem, 4vw, 2.6rem);
  font-weight: 900;
  letter-spacing: -0.02em;
  color: #fff;
  margin: 0 0 6px;
  line-height: 1.1;
  text-shadow: 0 2px 12px rgba(0,0,0,0.5);
}
.studio-hero-date {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}
.studio-col-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.55);
  line-height: 1.6;
  margin: 0;
}

/* Count bar */
.studio-count-bar {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.35);
  letter-spacing: 0.05em;
  margin-bottom: 14px;
  padding-top: 4px;
}

/* Photo grid */
.studio-photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px;
}

.studio-photo-thumb {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  padding: 0;
  cursor: pointer;
  transition: transform 0.2s ease;
}
.studio-photo-thumb:hover {
  transform: scale(1.02);
}
.studio-photo-thumb:hover .studio-thumb-hover {
  opacity: 1;
}
.studio-photo-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.35s ease;
}
.studio-photo-thumb:hover img {
  transform: scale(1.06);
}
.studio-thumb-hover {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.2rem;
}

/* Skeleton photo grid */
.studio-photo-skel {
  aspect-ratio: 1;
  border-radius: 8px;
}
.studio-hero-skel {
  width: 100%;
  aspect-ratio: 16 / 7;
  border-radius: 14px;
}

/* No photos / not found */
.studio-no-photos,
.studio-not-found {
  text-align: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.25);
}
.studio-not-found h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.4);
  margin: 0 0 8px;
}

/* Lightbox */
.studio-lightbox {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.96);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  touch-action: pan-y;
}

.studio-lb-close {
  position: fixed;
  top: 18px;
  right: 20px;
  z-index: 10001;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.15s, color 0.15s;
}
.studio-lb-close:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.studio-lb-arrow {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10001;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.7);
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.1rem;
  transition: background 0.15s, color 0.15s;
}
.studio-lb-arrow:hover {
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
}
.studio-lb-prev { left: 16px; }
.studio-lb-next { right: 16px; }

.studio-lb-img-wrap {
  max-width: min(90vw, 900px);
  max-height: 85vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.studio-lb-img {
  max-width: 100%;
  max-height: 85vh;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.8);
}

.studio-lb-counter {
  position: fixed;
  bottom: 22px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 0.1em;
  background: rgba(0, 0, 0, 0.5);
  padding: 5px 14px;
  border-radius: 20px;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

/* Loading state */
.studio-col-loading { width: 100%; }

/* Transitions */
.lb-fade-enter-active,
.lb-fade-leave-active {
  transition: opacity 0.2s ease;
}
.lb-fade-enter-from,
.lb-fade-leave-to {
  opacity: 0;
}
.lb-img-enter-active,
.lb-img-leave-active {
  transition: opacity 0.15s ease;
}
.lb-img-enter-from,
.lb-img-leave-to {
  opacity: 0;
}

@media (max-width: 600px) {
  .studio-photo-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
  }
  .studio-hero-img-wrap {
    aspect-ratio: 4 / 3;
    border-radius: 10px;
  }
  .studio-lb-arrow {
    width: 38px;
    height: 38px;
    font-size: 0.9rem;
  }
  .studio-lb-prev { left: 8px; }
  .studio-lb-next { right: 8px; }
}
</style>
