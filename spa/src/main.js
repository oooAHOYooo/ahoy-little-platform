import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { usePlayerStore } from './stores/player'
import './assets/app.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.mount('#app')

// Restore last played track so mini player shows immediately
const playerStore = usePlayerStore()
playerStore.restoreLastPlayed()
