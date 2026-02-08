<template>
  <div class="events-page event-detail-page" v-if="event">
    <!-- Breadcrumb -->
    <nav class="ds-crumbs event-detail-crumbs" aria-label="Breadcrumb" style="padding:12px 16px 0">
      <span class="ds-crumbs__item">
        <router-link to="/events" class="ds-crumbs__link" style="color:var(--accent-primary,#6ddcff);text-decoration:none">Events</router-link>
        <span class="ds-crumbs__sep" style="margin:0 6px;color:rgba(255,255,255,0.4)">›</span>
      </span>
      <span class="ds-crumbs__item">
        <span class="ds-crumbs__current" style="color:rgba(255,255,255,0.7)">{{ event.title }}</span>
      </span>
    </nav>

    <!-- Hero -->
    <section class="podcast-show-hero" style="margin-top:12px">
      <img
        class="podcast-show-hero-art"
        :src="event.image || '/static/img/default-cover.jpg'"
        :alt="event.title"
      />
      <div class="podcast-show-hero-meta">
        <div class="podcast-show-hero-kicker">Event</div>
        <h1 class="podcast-show-hero-title">{{ event.title }}</h1>
        <p class="podcast-show-hero-desc" v-if="event.description">{{ event.description }}</p>
        <div class="episode-subtitle" style="margin-bottom:10px">
          <span v-if="event.date">{{ event.date }}</span>
          <span class="episode-dot" v-if="event.date && event.time"> · </span>
          <span v-if="event.time">{{ event.time }}</span>
          <span class="episode-dot" v-if="(event.date || event.time) && event.venue"> · </span>
          <span v-if="event.venue">{{ event.venue }}</span>
        </div>
        <div class="episode-desc" v-if="event.venue_address" style="color:rgba(255,255,255,0.5);font-size:13px">
          {{ event.venue_address }}
        </div>
        <div class="podcast-show-hero-actions" style="margin-top:12px">
          <button class="podcast-cta secondary" @click="bookmarks.toggle({ ...event, _type: 'event' })">
            <i :class="bookmarks.isBookmarked(event) ? 'fas fa-bookmark' : 'far fa-bookmark'"></i>
            {{ bookmarks.isBookmarked(event) ? 'Saved' : 'Save' }}
          </button>
          <a
            v-if="event.rsvp_url || event.link"
            :href="event.rsvp_url || event.link"
            target="_blank"
            class="podcast-cta"
            style="text-decoration:none"
          >
            <i class="fas fa-external-link-alt"></i>
            RSVP
          </a>
        </div>
      </div>
    </section>

    <!-- Photos -->
    <section class="podcasts-section" v-if="event.photos && event.photos.length" style="margin-top:16px">
      <div class="podcasts-section-header">
        <h2>Photos</h2>
      </div>
      <div class="shows-grid" style="grid-template-columns:repeat(auto-fill,minmax(200px,1fr))">
        <div v-for="(photo, idx) in event.photos" :key="idx" style="border-radius:12px;overflow:hidden">
          <img :src="photo" :alt="`${event.title} photo`" loading="lazy" style="width:100%;display:block" />
        </div>
      </div>
    </section>
  </div>

  <!-- Loading -->
  <div class="events-page" v-else>
    <section class="podcast-show-hero" style="margin-top:24px">
      <div class="podcast-show-hero-art skeleton" style="aspect-ratio:16/9;width:100%"></div>
      <div class="podcast-show-hero-meta">
        <div class="skeleton" style="height:14px;width:30%;margin-bottom:8px"></div>
        <div class="skeleton" style="height:24px;width:60%;margin-bottom:8px"></div>
        <div class="skeleton" style="height:14px;width:80%"></div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiFetchCached } from '../composables/useApi'
import { useBookmarks } from '../composables/useBookmarks'

const route = useRoute()
const bookmarks = useBookmarks()

const event = ref(null)

onMounted(async () => {
  const id = route.params.id
  const data = await apiFetchCached('/api/events').catch(() => ({ events: [] }))
  const events = data.events || []
  event.value = events.find(e => String(e.id) === String(id)) || null
})
</script>
