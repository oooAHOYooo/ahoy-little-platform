<template>
  <div class="relative min-h-screen bg-black text-white overflow-hidden font-sans selection:bg-purple-500 selection:text-white">
    
    <!-- Ambient Background Elements -->
    <div class="fixed inset-0 z-0 pointer-events-none">
        <div class="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-purple-900/40 rounded-full blur-[120px] animate-pulse"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] bg-blue-900/30 rounded-full blur-[120px] animate-pulse" style="animation-delay: 2s"></div>
        <div class="absolute top-[20%] right-[20%] w-[300px] h-[300px] bg-pink-900/20 rounded-full blur-[100px] animate-bounce" style="animation-duration: 10s"></div>
    </div>

    <div class="relative z-10 container mx-auto p-6">
      <header class="mb-12 flex justify-between items-center">
        <div>
          <h1 class="text-4xl font-bold bg-gradient-to-r from-white via-purple-200 to-purple-400 bg-clip-text text-transparent drop-shadow-sm">
            Admin Dashboard
          </h1>
          <p class="text-purple-200/60 text-sm mt-1">Platform Overview & Management</p>
        </div>
        <div v-if="loading" class="text-sm text-purple-300 animate-pulse bg-purple-900/30 px-3 py-1 rounded-full border border-purple-500/30">
          Refreshing data...
        </div>
      </header>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-12">
        <div class="glass-card p-6 group hover:bg-white/5 transition duration-300">
          <h3 class="text-purple-200/60 text-xs font-bold uppercase tracking-wider mb-2">Users</h3>
          <p class="text-3xl font-bold text-white group-hover:scale-105 transition-transform origin-left">{{ stats.users }}</p>
          <div class="h-1 w-full bg-gray-700/50 mt-4 rounded-full overflow-hidden">
            <div class="h-full bg-purple-500 w-[70%]"></div>
          </div>
        </div>
        <div class="glass-card p-6 group hover:bg-white/5 transition duration-300">
          <h3 class="text-purple-200/60 text-xs font-bold uppercase tracking-wider mb-2">Total Tips</h3>
          <p class="text-3xl font-bold text-white group-hover:scale-105 transition-transform origin-left">${{ stats.tip_total?.toFixed(2) }}</p>
          <div class="h-1 w-full bg-gray-700/50 mt-4 rounded-full overflow-hidden">
             <div class="h-full bg-green-500 w-[45%]"></div>
          </div>
        </div>
        <div class="glass-card p-6 group hover:bg-white/5 transition duration-300">
          <h3 class="text-purple-200/60 text-xs font-bold uppercase tracking-wider mb-2">Tips Count</h3>
          <p class="text-3xl font-bold text-white group-hover:scale-105 transition-transform origin-left">{{ stats.tips }}</p>
           <div class="h-1 w-full bg-gray-700/50 mt-4 rounded-full overflow-hidden">
             <div class="h-full bg-blue-500 w-[30%]"></div>
          </div>
        </div>
        <div class="glass-card p-6 group hover:bg-white/5 transition duration-300">
          <h3 class="text-purple-200/60 text-xs font-bold uppercase tracking-wider mb-2">Revenue</h3>
          <p class="text-3xl font-bold text-white group-hover:scale-105 transition-transform origin-left">${{ stats.revenue?.toFixed(2) }}</p>
           <div class="h-1 w-full bg-gray-700/50 mt-4 rounded-full overflow-hidden">
             <div class="h-full bg-yellow-500 w-[60%]"></div>
          </div>
        </div>
         <div class="glass-card p-6 group hover:bg-white/5 transition duration-300">
          <h3 class="text-purple-200/60 text-xs font-bold uppercase tracking-wider mb-2">Purchases</h3>
          <p class="text-3xl font-bold text-white group-hover:scale-105 transition-transform origin-left">{{ stats.purchases }}</p>
           <div class="h-1 w-full bg-gray-700/50 mt-4 rounded-full overflow-hidden">
             <div class="h-full bg-red-500 w-[25%]"></div>
          </div>
        </div>
      </div>

      <!-- Main Content Tabs -->
      <div class="flex space-x-2 mb-8 p-1 bg-white/5 backdrop-blur-md rounded-xl w-fit border border-white/10">
        <button 
          @click="currentTab = 'activity'"
          :class="['px-6 py-2 rounded-lg text-sm font-medium transition-all duration-300', currentTab === 'activity' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50' : 'text-purple-200/60 hover:text-white hover:bg-white/5']"
        >
          Activity Feed
        </button>
        <button 
          @click="currentTab = 'users'"
          :class="['px-6 py-2 rounded-lg text-sm font-medium transition-all duration-300', currentTab === 'users' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50' : 'text-purple-200/60 hover:text-white hover:bg-white/5']"
        >
          Users
        </button>
        <button 
          @click="currentTab = 'actions'"
          :class="['px-6 py-2 rounded-lg text-sm font-medium transition-all duration-300', currentTab === 'actions' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50' : 'text-purple-200/60 hover:text-white hover:bg-white/5']"
        >
          Action Items
          <span v-if="actions.length" class="ml-2 bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded-full">{{ actions.length }}</span>
        </button>
        <button 
          @click="currentTab = 'analytics'"
          :class="['px-6 py-2 rounded-lg text-sm font-medium transition-all duration-300', currentTab === 'analytics' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50' : 'text-purple-200/60 hover:text-white hover:bg-white/5']"
        >
          Analytics
        </button>
      </div>

      <!-- Activity Feed -->
      <div v-if="currentTab === 'activity'" class="space-y-4">
        <div v-for="(event, i) in activity" :key="i" class="glass-card item-card p-4 flex items-center group">
          <div :class="['w-1.5 h-12 rounded-full mr-5 shadow-[0_0_10px_rgba(0,0,0,0.5)]', getActivityColor(event.type)]"></div>
          <div class="flex-1">
            <p class="font-medium text-white group-hover:text-purple-200 transition-colors">{{ event.text }}</p>
            <div class="flex items-center gap-2 mt-1">
                 <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-white/50">{{ event.type.toUpperCase() }}</span>
                 <p class="text-xs text-purple-200/40">{{ formatDate(event.date) }}</p>
            </div>
          </div>
        </div>
        <div v-if="activity.length === 0" class="text-purple-200/40 text-center py-20 italic">No recent activity detected in the ether.</div>
      </div>

      <!-- Users -->
      <div v-if="currentTab === 'users'" class="space-y-6">
        <div class="relative flex gap-4">
             <input 
            v-model="userSearch" 
            @input="searchUsers" 
            placeholder="Search users..." 
            class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-purple-200/20 focus:outline-none focus:border-purple-500/50 focus:bg-white/10 transition-all"
            >
            <a href="/api/admin/users/export" target="_blank" class="bg-gray-800 hover:bg-gray-700 text-white px-6 py-3 rounded-xl border border-white/10 transition flex items-center whitespace-nowrap">
                <span class="mr-2">⬇️</span> CSV
            </a>
            <div class="absolute right-[120px] top-3.5 text-purple-200/20 pointer-events-none">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
            </div>
        </div>
       
        <div class="glass-card overflow-hidden">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-purple-200/40 border-b border-white/5">
                <th class="p-4 font-medium text-xs uppercase tracking-wider">ID</th>
                <th class="p-4 font-medium text-xs uppercase tracking-wider">Email</th>
                <th class="p-4 font-medium text-xs uppercase tracking-wider">Username</th>
                <th class="p-4 font-medium text-xs uppercase tracking-wider">Joined</th>
                <th class="p-4 font-medium text-xs uppercase tracking-wider">Status</th>
                <th class="p-4 font-medium text-xs uppercase tracking-wider">Role</th>
                <th class="p-4 font-medium text-xs uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id" class="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td class="p-4 text-white/30 font-mono text-sm">{{ u.id }}</td>
                <td class="p-4 text-white/90">{{ u.email }}</td>
                <td class="p-4 text-white/70">{{ u.username || '-' }}</td>
                <td class="p-4 text-white/40 text-sm">{{ formatDate(u.created_at) }}</td>
                <td class="p-4">
                     <span v-if="u.disabled" class="text-red-400 font-bold text-xs uppercase tracking-wider bg-red-900/20 px-2 py-1 rounded">Banned</span>
                     <span v-else class="text-green-400 text-xs uppercase tracking-wider bg-green-900/20 px-2 py-1 rounded">Active</span>
                </td>
                <td class="p-4">
                  <span v-if="u.is_admin" class="bg-purple-500/20 border border-purple-500/30 text-purple-200 text-xs px-2 py-1 rounded shadow-[0_0_10px_rgba(168,85,247,0.2)]">Admin</span>
                  <span v-else class="text-white/20 text-xs">User</span>
                </td>
                <td class="p-4">
                    <button 
                      v-if="!u.is_admin"
                      @click="toggleUserSort(u)"
                      :class="['px-3 py-1 rounded text-xs font-bold border transition-all', u.disabled ? 'bg-green-500/20 border-green-500/50 text-green-200 hover:bg-green-500/40' : 'bg-red-500/20 border-red-500/50 text-red-200 hover:bg-red-500/40']"
                    >
                      {{ u.disabled ? 'Unban' : 'Ban' }}
                    </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Action Items -->
      <div v-if="currentTab === 'actions'" class="space-y-4">
        <div v-for="action in actions" :key="action.id" class="glass-card p-6 border-l-4 border-l-purple-500">
          <div class="flex justify-between items-start">
            <div>
              <h3 class="font-bold text-lg text-white">{{ action.title }}</h3>
              <p class="text-purple-200/70 mt-2">{{ action.description }}</p>
              <p class="text-xs text-purple-200/30 mt-4 font-mono">ID: {{ action.id }} • Created: {{ formatDate(action.created_at) }}</p>
            </div>
            <div class="flex space-x-3">
              <button 
                @click="handleAction(action.id, 'approve')" 
                class="bg-green-500/20 hover:bg-green-500/40 border border-green-500/50 text-green-100 px-6 py-2 rounded-lg text-sm transition-all hover:scale-105"
              >
                Approve
              </button>
              <button 
                @click="handleAction(action.id, 'reject')" 
                class="bg-red-500/20 hover:bg-red-500/40 border border-red-500/50 text-red-100 px-6 py-2 rounded-lg text-sm transition-all hover:scale-105"
              >
                Reject
              </button>
            </div>
          </div>
        </div>
         <div v-if="actions.length === 0" class="text-purple-200/40 text-center py-20 italic">No pending actions. The ether is calm.</div>
      </div>
      
      <!-- Analytics / Heatmap -->
      <div v-if="currentTab === 'analytics'" class="space-y-6">
        <div class="glass-card p-8">
           <h3 class="text-xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-purple-200 to-white">Traffic Heatmap</h3>
           <div v-if="heatmap.length === 0" class="text-purple-200/50">No data yet. Browse the app to generate data!</div>
           <div class="space-y-4">
              <div v-for="page in heatmap" :key="page.path" class="relative group">
                <div class="flex mb-2 items-center justify-between z-10 relative">
                  <div>
                    <span class="text-xs font-semibold inline-block py-1 px-3 uppercase rounded bg-black/40 text-purple-200 border border-white/10 backdrop-blur-sm">
                      {{ page.path || '/' }}
                    </span>
                  </div>
                  <div class="text-right">
                    <span class="text-xs font-mono text-purple-200/80">
                      {{ page.count }} views
                    </span>
                  </div>
                </div>
                <div class="overflow-hidden h-3 mb-4 text-xs flex rounded-full bg-white/5 border border-white/5 relative">
                    <!-- Glow effect behind bar -->
                   <div :style="{ width: getHeatmapWidth(page.count) + '%' }" class="absolute inset-0 bg-purple-500/20 blur-md"></div>
                  <div :style="{ width: getHeatmapWidth(page.count) + '%' }" class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r from-purple-600 to-pink-500 relative z-10 transition-all duration-1000 ease-out"></div>
                </div>
              </div>
           </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.glass-card {
    @apply bg-gray-900/40 backdrop-blur-xl border border-white/10 rounded-2xl shadow-xl;
}
</style>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '@/composables/useApi'
import { useAuth } from '@/composables/useAuth'
import { useRouter } from 'vue-router'

const { user, isLoggedIn } = useAuth()
const router = useRouter()

const loading = ref(false)
const stats = ref({})
const activity = ref([])
const users = ref([])
const actions = ref([])
const heatmap = ref([])
const userSearch = ref('')
const currentTab = ref('activity')

const getActivityColor = (type) => {
  const map = {
    signup: 'bg-blue-500',
    tip: 'bg-green-500',
    purchase: 'bg-yellow-500',
    feedback: 'bg-purple-500',
    claim: 'bg-red-500'
  }
  return map[type] || 'bg-gray-500'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}

const fetchData = async () => {
    loading.value = true
    try {
        const [statsData, activityData, usersData, actionsData, heatmapData] = await Promise.all([
            apiFetch('/api/admin/stats'),
            apiFetch('/api/admin/activity'),
            apiFetch('/api/admin/users'),
            apiFetch('/api/admin/actions'),
            apiFetch('/api/admin/heatmap')
        ])
        
        stats.value = statsData
        activity.value = activityData
        users.value = usersData
        actions.value = actionsData
        heatmap.value = heatmapData
        
    } catch (e) {
        console.error("Failed to fetch admin data", e)
    } finally {
        loading.value = false
    }
}

const searchUsers = async () => {
    // Debounce typically, but simplistic here
    try {
        const data = await apiFetch(`/api/admin/users?q=${userSearch.value}`)
        users.value = data
    } catch (e) {
        console.error(e)
    }
}

const handleAction = async (id, action) => {
    if (!confirm(`Are you sure you want to ${action} this request?`)) return
    try {
        await apiFetch(`/api/admin/actions/claim/${id}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ action })
        })
        // Refresh actions
        const actionsData = await apiFetch('/api/admin/actions')
        actions.value = actionsData
    } catch (e) {
        alert("Action failed: " + e.message)
    }
}

const toggleUserSort = async (u) => {
    if (!confirm(`Are you sure you want to ${u.disabled ? 'enable' : 'disable'} this user?`)) return
    try {
        const res = await apiFetch(`/api/admin/users/${u.id}/toggle_status`, { method: 'POST' })
        if (res.ok) {
            u.disabled = res.disabled
        }
    } catch (e) {
        alert("Failed to update status: " + e.message)
    }
}

const getHeatmapWidth = (count) => {
    if (!heatmap.value.length) return 0
    const max = Math.max(...heatmap.value.map(i => i.count))
    return (count / max) * 100
}

onMounted(() => {
    if (!isLoggedIn.value) {
        router.push('/login')
        return
    }
    if (!user.value?.is_admin) {
        router.push('/')
        return
    }
    fetchData()
})
</script>
