import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('./views/HomeView.vue'),
  },
  {
    path: '/music',
    name: 'music',
    component: () => import('./views/MusicView.vue'),
  },
  {
    path: '/shows',
    name: 'shows',
    component: () => import('./views/ShowsView.vue'),
  },
  {
    path: '/podcasts',
    name: 'podcasts',
    component: () => import('./views/PodcastsView.vue'),
  },
  {
    path: '/artists',
    name: 'artists',
    component: () => import('./views/ArtistsView.vue'),
  },
  {
    path: '/events',
    name: 'events',
    component: () => import('./views/EventsView.vue'),
  },
  {
    path: '/merch',
    name: 'merch',
    component: () => import('./views/MerchView.vue'),
  },
  // Catch-all
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
