<template>
  <div class="events-page">
    <!-- Subpage hero (same as Flask) -->
    <section class="podcasts-hero">
      <div class="podcasts-hero-inner">
        <h1>
          <i class="fas fa-calendar" aria-hidden="true"></i>
          Events
        </h1>
        <p>Upcoming live Ahoy shows, plus past events and recordings.</p>
      </div>
    </section>

    <!-- Upcoming -->
    <section class="podcasts-section">
      <div class="podcasts-section-header">
        <h2>Upcoming</h2>
      </div>

      <!-- Featured event hero (first upcoming) -->
      <div v-if="featured" class="podcast-show-hero" style="margin-top: 10px;">
        <img
          class="podcast-show-hero-art"
          :src="featured.image || '/static/img/default-cover.jpg'"
          :alt="featured.title"
        />
        <div class="podcast-show-hero-meta">
          <div class="podcast-show-hero-kicker">Featured event</div>
          <h1 class="podcast-show-hero-title">{{ featured.title }}</h1>
          <p class="podcast-show-hero-desc">{{ featured.description }}</p>
          <div class="episode-subtitle" style="margin-bottom: 10px;">
            <span>{{ formatDate(featured.date) }}</span>
            <span class="episode-dot">•</span>
            <span>{{ featured.time || '' }}</span>
            <span class="episode-dot" v-if="featured.venue">•</span>
            <span v-if="featured.venue">{{ featured.venue }}</span>
          </div>
          <div class="podcast-show-hero-actions">
            <a
              class="podcast-cta"
              :href="featured.rsvp_external_url || '/events'"
              @click.stop
            >
              {{ featured.rsvp_external_url ? 'RSVP' : 'View' }}
            </a>
            <button type="button" class="podcast-cta secondary" @click="copyLink(featured.rsvp_external_url || (origin + '/events'))">
              Copy link
            </button>
          </div>
        </div>
      </div>

      <div class="episode-list" style="margin-top: 12px;">
        <article
          v-for="evt in upcoming"
          :key="evt.id || evt.title"
          class="episode-row"
        >
          <img
            class="episode-art"
            :src="evt.image || '/static/img/default-cover.jpg'"
            :alt="evt.title"
            loading="lazy"
          />
          <div class="episode-meta">
            <div class="episode-title">{{ evt.title || 'Live Show' }}</div>
            <div class="episode-subtitle">
              <span>{{ formatDate(evt.date) }}</span>
              <span class="episode-dot">•</span>
              <span>{{ evt.time || '' }}</span>
              <span class="episode-dot" v-if="evt.venue">•</span>
              <span v-if="evt.venue">{{ evt.venue }}</span>
            </div>
            <div class="episode-desc" v-if="evt.description">{{ evt.description }}</div>
          </div>
          <div class="episode-actions">
            <a
              class="episode-open"
              :href="evt.rsvp_external_url || '/events'"
              @click.stop
            >
              {{ evt.rsvp_external_url ? 'RSVP' : 'Open' }}
            </a>
          </div>
        </article>
      </div>

      <div v-if="!loading && upcoming.length === 0" class="empty-state" style="margin-top:14px;">
        <i class="fas fa-calendar-times"></i>
        <h4>No upcoming events</h4>
        <p>Check back soon.</p>
      </div>
    </section>

    <!-- Past events -->
    <section class="podcasts-section">
      <div class="podcasts-section-header">
        <h2>Past events</h2>
      </div>

      <div class="episode-list">
        <article
          v-for="evt in past"
          :key="evt.id || evt.title"
          class="episode-row"
        >
          <img
            class="episode-art"
            :src="evt.image || '/static/img/default-cover.jpg'"
            :alt="evt.title"
            loading="lazy"
          />
          <div class="episode-meta">
            <div class="episode-title">{{ evt.title || 'Event' }}</div>
            <div class="episode-subtitle">
              <span>{{ formatDate(evt.date) }}</span>
              <span class="episode-dot">•</span>
              <span>{{ evt.venue || '' }}</span>
              <span class="episode-dot" v-if="evt.videoStatus">•</span>
              <span v-if="evt.videoStatus">{{ evt.videoStatus }}</span>
            </div>
            <div class="episode-desc" v-if="evt.description">{{ evt.description }}</div>
          </div>
          <div class="episode-actions">
            <a
              v-if="evt.videoUrl"
              class="episode-open"
              :href="evt.videoUrl"
              target="_blank"
              rel="noopener"
              @click.stop
            >
              Watch
            </a>
            <router-link
              v-if="evt.id || evt.title"
              :to="`/events/${encodeURIComponent(evt.id || evt.title)}`"
              class="episode-open"
              @click.stop
            >
              View
            </router-link>
            <span
              v-if="!evt.videoUrl && evt.videoStatus"
              class="episode-open"
              style="opacity:0.7; cursor:default;"
            >
              {{ evt.videoStatus }}
            </span>
          </div>
        </article>
      </div>
    </section>

    <!-- Loading -->
    <section v-if="loading" class="podcasts-section">
      <div class="episode-list">
        <div class="episode-row" v-for="i in 4" :key="i">
          <div class="episode-art skeleton" style="width:80px;height:80px;border-radius:8px"></div>
          <div class="episode-meta">
            <div class="skeleton" style="height:14px;width:60%;margin-bottom:6px"></div>
            <div class="skeleton" style="height:12px;width:40%"></div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetchCached } from '../composables/useApi'

const loading = ref(true)
const rawEvents = ref([])
const rawVideos = ref([])

const origin = typeof window !== 'undefined' ? window.location.origin : ''

function isRemoteUrl(u) {
  return typeof u === 'string' && /^https?:\/\//i.test(u)
}

function pickFirstRemote(arr) {
  if (!Array.isArray(arr)) return null
  for (const u of arr) {
    if (isRemoteUrl(u)) return u
  }
  return null
}

const normalizedEvents = computed(() => {
  const events = Array.isArray(rawEvents.value?.events) ? rawEvents.value.events : []
  const videos = Array.isArray(rawVideos.value?.videos) ? rawVideos.value.videos : []
  const videoByEventId = new Map()
  for (const v of videos) {
    if (!v?.event_id) continue
    videoByEventId.set(String(v.event_id), v)
  }
  return events.map((e) => {
    const vid = videoByEventId.get(String(e.id || ''))
    const remotePhoto = pickFirstRemote(e?.photos)
    const remoteImage = isRemoteUrl(e?.image) ? e.image : null
    const remoteThumb = isRemoteUrl(vid?.thumbnail) ? vid.thumbnail : null
    return {
      ...e,
      image: remotePhoto || remoteImage || remoteThumb || null,
      photos: Array.isArray(e?.photos) ? e.photos.filter(isRemoteUrl) : [],
      videoUrl: vid?.url || null,
      videoStatus:
        vid?.status === 'available'
          ? 'Recording available'
          : vid?.status === 'coming_soon'
            ? 'Recording coming soon'
            : '',
    }
  })
})

const upcoming = computed(() => {
  const list = normalizedEvents.value.filter((e) => String(e.status || '').toLowerCase() === 'upcoming')
  const unknown = normalizedEvents.value.filter(
    (e) => !['upcoming', 'past'].includes(String(e.status || '').toLowerCase())
  )
  const now = new Date()
  for (const e of unknown) {
    const d = e.date ? new Date(e.date) : null
    if (!d || isNaN(d.getTime())) list.push(e)
    else if (d >= now) list.push(e)
  }
  list.sort((a, b) => String(a.date || '').localeCompare(String(b.date || '')))
  return list.slice(0, 12)
})

const past = computed(() => {
  const list = normalizedEvents.value.filter((e) => String(e.status || '').toLowerCase() === 'past')
  const unknown = normalizedEvents.value.filter(
    (e) => !['upcoming', 'past'].includes(String(e.status || '').toLowerCase())
  )
  const now = new Date()
  for (const e of unknown) {
    const d = e.date ? new Date(e.date) : null
    if (d && !isNaN(d.getTime()) && d < now) list.push(e)
  }
  list.sort((a, b) => String(b.date || '').localeCompare(String(a.date || '')))
  return list
})

const featured = computed(() => upcoming.value[0] || null)

function formatDate(ds) {
  if (!ds) return ''
  const d = new Date(ds)
  if (isNaN(d.getTime())) return String(ds)
  return d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })
}

async function copyLink(url) {
  try {
    await navigator.clipboard.writeText(url)
    window.dispatchEvent(new CustomEvent('ahoy:toast', { detail: { message: 'Link copied.' } }))
  } catch (_) {}
}

onMounted(async () => {
  loading.value = true
  try {
    const data = await apiFetchCached('/api/events')
    rawEvents.value = { events: data.events || [] }
    rawVideos.value = { videos: data.videos || [] }
  } catch {
    rawEvents.value = { events: [] }
    rawVideos.value = { videos: [] }
  }
  loading.value = false
})
</script>
