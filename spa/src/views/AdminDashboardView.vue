<template>
  <div class="relative min-h-screen bg-black text-white overflow-hidden font-sans selection:bg-purple-500 selection:text-white">
    
    <!-- Ambient Background Elements -->
    <div class="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div class="absolute top-[-10%] left-[-10%] w-[60vw] h-[60vw] max-w-[800px] max-h-[800px] bg-purple-600/30 rounded-full blur-[120px] mix-blend-screen animate-pulse duration-10000"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-[50vw] h-[50vw] max-w-[700px] max-h-[700px] bg-blue-500/30 rounded-full blur-[120px] mix-blend-screen animate-pulse" style="animation-delay: 2s; animation-duration: 12s;"></div>
        <div class="absolute top-[30%] right-[30%] w-[30vw] h-[30vw] max-w-[400px] max-h-[400px] bg-pink-500/20 rounded-full blur-[100px] mix-blend-screen animate-bounce" style="animation-duration: 15s"></div>
        <div class="absolute top-[50%] left-[20%] w-[40vw] h-[40vw] max-w-[500px] max-h-[500px] bg-cyan-500/20 rounded-full blur-[100px] mix-blend-screen" style="animation: pulse 8s infinite alternate;"></div>
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
        <div class="glass-card p-6 group">
          <h3 class="text-purple-200/80 text-xs font-bold uppercase tracking-wider mb-2">Users</h3>
          <p class="text-3xl font-bold text-white group-hover:scale-105 transition-transform origin-left drop-shadow-md">{{ stats.users }}</p>
          <div class="h-1 w-full bg-white/10 mt-4 rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-purple-400 to-purple-600 w-[70%] shadow-[0_0_10px_rgba(168,85,247,0.8)]"></div>
          </div>
        </div>
        <div class="glass-card p-6 group">
          <h3 class="text-purple-200/80 text-xs font-bold uppercase tracking-wider mb-2">Total Tips</h3>
          <p class="text-3xl font-bold text-white group-hover:scale-105 transition-transform origin-left drop-shadow-md">${{ stats.tip_total?.toFixed(2) }}</p>
          <div class="h-1 w-full bg-white/10 mt-4 rounded-full overflow-hidden">
             <div class="h-full bg-gradient-to-r from-green-400 to-green-600 w-[45%] shadow-[0_0_10px_rgba(74,222,128,0.8)]"></div>
          </div>
        </div>
        <div class="glass-card p-6 group">
          <h3 class="text-purple-200/80 text-xs font-bold uppercase tracking-wider mb-2">Tips Count</h3>
          <p class="text-3xl font-bold text-white group-hover:scale-105 transition-transform origin-left drop-shadow-md">{{ stats.tips }}</p>
           <div class="h-1 w-full bg-white/10 mt-4 rounded-full overflow-hidden">
             <div class="h-full bg-gradient-to-r from-blue-400 to-blue-600 w-[30%] shadow-[0_0_10px_rgba(96,165,250,0.8)]"></div>
          </div>
        </div>
        <div class="glass-card p-6 group">
          <h3 class="text-purple-200/80 text-xs font-bold uppercase tracking-wider mb-2">Revenue</h3>
          <p class="text-3xl font-bold text-white group-hover:scale-105 transition-transform origin-left drop-shadow-md">${{ stats.revenue?.toFixed(2) }}</p>
           <div class="h-1 w-full bg-white/10 mt-4 rounded-full overflow-hidden">
             <div class="h-full bg-gradient-to-r from-yellow-400 to-yellow-600 w-[60%] shadow-[0_0_10px_rgba(250,204,21,0.8)]"></div>
          </div>
        </div>
         <div class="glass-card p-6 group">
          <h3 class="text-purple-200/80 text-xs font-bold uppercase tracking-wider mb-2">Purchases</h3>
          <p class="text-3xl font-bold text-white group-hover:scale-105 transition-transform origin-left drop-shadow-md">{{ stats.purchases }}</p>
           <div class="h-1 w-full bg-white/10 mt-4 rounded-full overflow-hidden">
             <div class="h-full bg-gradient-to-r from-red-400 to-red-600 w-[25%] shadow-[0_0_10px_rgba(248,113,113,0.8)]"></div>
          </div>
        </div>
      </div>

      <!-- Main Content Tabs -->
      <div class="flex space-x-2 mb-8 p-1 glass-card w-fit !rounded-xl !p-2 border-white/20">
        <button 
          @click="switchTab('activity')"
          :class="['px-6 py-2 rounded-lg text-sm font-medium transition-all duration-300', currentTab === 'activity' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50' : 'text-purple-200/60 hover:text-white hover:bg-white/5']"
        >
          Activity Feed
        </button>
        <button 
          @click="switchTab('users')"
          :class="['px-6 py-2 rounded-lg text-sm font-medium transition-all duration-300', currentTab === 'users' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50' : 'text-purple-200/60 hover:text-white hover:bg-white/5']"
        >
          Users
        </button>
        <button 
          @click="switchTab('actions')"
          :class="['px-6 py-2 rounded-lg text-sm font-medium transition-all duration-300', currentTab === 'actions' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50' : 'text-purple-200/60 hover:text-white hover:bg-white/5']"
        >
          Action Items
          <span v-if="actions.length" class="ml-2 bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded-full">{{ actions.length }}</span>
        </button>
        <button 
          @click="switchTab('content')"
          :class="['px-6 py-2 rounded-lg text-sm font-medium transition-all duration-300', currentTab === 'content' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50' : 'text-purple-200/60 hover:text-white hover:bg-white/5']"
        >
          Content
        </button>
        <button 
          @click="switchTab('analytics')"
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
            class="w-full glass-input rounded-xl px-4 py-3 text-white placeholder-purple-200/40"
            >
            <a href="/api/admin/users/export" target="_blank" class="glass-btn text-white px-6 py-3 rounded-xl flex items-center whitespace-nowrap">
                <span class="mr-2 border-r border-white/20 pr-2">⬇️</span> CSV
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
              <tr v-for="u in users" :key="u.id" class="glass-table-row border-b border-white/5 hover:bg-white/10 transition-colors">
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

      <!-- Content Management -->
      <div v-if="currentTab === 'content'" class="space-y-6">
        <div class="flex flex-wrap gap-2 p-1 bg-white/5 backdrop-blur-md rounded-xl w-fit border border-white/10 mb-6">
          <button 
            v-for="(label, type) in contentTypes" :key="type"
            @click="selectContentType(type)"
            :class="['px-4 py-1.5 rounded-lg text-xs font-medium transition-all duration-300', contentType === type ? 'bg-purple-500/50 text-white' : 'text-purple-200/60 hover:text-white hover:bg-white/5']"
          >
            {{ label }}
          </button>
        </div>

        <div class="flex justify-between items-center mb-6">
          <div class="relative flex-1 max-w-md">
            <input 
              v-model="contentSearch" 
              @input="fetchContent" 
              :placeholder="`Search ${contentTypes[contentType]}...`" 
              class="w-full glass-input rounded-xl px-4 py-2 text-sm text-white placeholder-purple-200/40"
            >
          </div>
          <button 
            @click="openContentEditor()"
            class="glass-primary-btn px-6 py-2 rounded-xl text-sm font-bold active:scale-95"
          >
            + Add {{ contentTypes[contentType].slice(0, -1) }}
          </button>
        </div>

        <div class="glass-card overflow-hidden">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-purple-200/40 border-b border-white/5">
                <th class="p-4 font-medium text-xs uppercase tracking-wider">ID</th>
                <th class="p-4 font-medium text-xs uppercase tracking-wider">Title/Name</th>
                <th class="p-4 font-medium text-xs uppercase tracking-wider">Details</th>
                <th class="p-4 font-medium text-xs uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in contentItems" :key="item.id" class="glass-table-row border-b border-white/5 hover:bg-white/10 transition-colors group">
                <td class="p-4 text-white/30 font-mono text-xs">{{ item.track_id || item.show_id || item.artist_id || item.id }}</td>
                <td class="p-4">
                  <div class="flex items-center gap-3">
                    <img v-if="item.cover_art || item.thumbnail || item.image || item.image_url" :src="item.cover_art || item.thumbnail || item.image || item.image_url" class="w-8 h-8 rounded object-cover border border-white/10 shadow-sm">
                    <div>
                      <div class="text-white/90 font-medium">{{ item.title || item.name }}</div>
                      <div class="text-[10px] text-purple-200/40">{{ item.artist || item.host || item.venue || item.kind }}</div>
                    </div>
                  </div>
                </td>
                <td class="p-4 text-xs text-white/40">
                  <span v-if="item.genre" class="bg-white/5 px-2 py-0.5 rounded mr-2">{{ item.genre }}</span>
                  <span v-if="item.duration_seconds" class="mr-2">{{ Math.floor(item.duration_seconds / 60) }}:{{ (item.duration_seconds % 60).toString().padStart(2, '0') }}</span>
                  <span v-if="item.status" :class="['px-2 py-0.5 rounded text-[10px] uppercase font-bold', item.status === 'upcoming' || item.status === 'active' ? 'text-green-400 bg-green-900/20' : 'text-gray-400 bg-gray-900/20']">{{ item.status }}</span>
                </td>
                <td class="p-4 text-right">
                  <div class="flex justify-end gap-2 opacity-50 group-hover:opacity-100 transition-opacity">
                    <button @click="openContentEditor(item)" class="p-2 hover:bg-purple-500/20 rounded-lg text-purple-300 transition-colors">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
                    </button>
                    <button @click="deleteContentItem(item.id)" class="p-2 hover:bg-red-500/20 rounded-lg text-red-300 transition-colors">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="contentItems.length === 0 && !loading" class="p-20 text-center text-purple-200/40 italic">
            No content found in this dimension.
          </div>
        </div>
      </div>

      <!-- Content Editor Modal -->
      <div v-if="showEditor" class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm">
        <div class="glass-card w-full max-w-2xl max-h-[90vh] overflow-y-auto p-8 shadow-2xl border-purple-500/30">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold">{{ editingId ? 'Edit' : 'Add' }} {{ contentTypes[contentType].slice(0, -1) }}</h2>
            <button @click="showEditor = false" class="text-white/40 hover:text-white transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>

          <form @submit.prevent="saveContent" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div v-for="(value, key) in editorForm" :key="key" class="space-y-1">
                <label v-if="key !== 'id' && key !== 'extra_fields' && key !== 'position' && key !== 'tags' && key !== 'photos' && key !== 'social_links' && key !== 'genres' && key !== 'features'" class="text-[10px] font-bold text-purple-200/60 uppercase tracking-widest pl-1">{{ key.replace(/_/g, ' ') }}</label>
                
                <!-- String/Number fields -->
                <input 
                  v-if="key !== 'id' && key !== 'extra_fields' && key !== 'position' && key !== 'description' && key !== 'social_links' && key !== 'features' && typeof value !== 'boolean' && typeof value !== 'object'"
                  v-model="editorForm[key]"
                  :type="typeof value === 'number' ? 'number' : 'text'"
                  class="w-full glass-input rounded-lg px-4 py-2 text-sm"
                  :placeholder="Array.isArray(value) ? 'Comma separated list...' : ''"
                >

                <!-- Boolean fields -->
                <div v-if="typeof value === 'boolean'" class="flex items-center gap-3 py-2">
                  <input type="checkbox" v-model="editorForm[key]" class="w-4 h-4 rounded bg-white/5 border-white/10 text-purple-600 focus:ring-purple-500/50">
                  <span class="text-sm text-white/70">{{ key.replace(/_/g, ' ') }}</span>
                </div>

                <!-- Textarea (description) -->
                <textarea 
                  v-if="key === 'description'"
                  v-model="editorForm[key]"
                  rows="4"
                  class="w-full md:col-span-2 glass-input rounded-lg px-4 py-2 text-sm"
                ></textarea>
              </div>
            </div>

            <div class="flex justify-end gap-3 mt-8 pt-6 border-t border-white/10">
              <button 
                type="button" @click="showEditor = false"
                class="px-6 py-2 rounded-xl text-sm font-medium text-white/60 hover:text-white hover:bg-white/5 transition-all"
              >
                Cancel
              </button>
              <button 
                type="submit" :disabled="saving"
                class="glass-primary-btn disabled:opacity-50 px-8 py-2 rounded-xl text-sm font-bold active:scale-95"
              >
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
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
    background: rgba(255, 255, 255, 0.05); /* very subtle white */
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.15); /* bright thin edge */
    border-radius: 1.5rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3), inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
}
.glass-card:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.25);
}

.glass-input {
    background: rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: white;
    transition: all 0.3s ease;
}
.glass-input:focus {
    border-color: rgba(168, 85, 247, 0.7); /* vivid purple */
    background: rgba(0, 0, 0, 0.3);
    outline: none;
    box-shadow: 0 0 20px rgba(168, 85, 247, 0.4), inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
}

.glass-btn {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 4px 15px 0 rgba(0, 0, 0, 0.2), inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
    transition: all 0.2s ease;
}
.glass-btn:hover {
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px 0 rgba(0, 0, 0, 0.3), inset 0 1px 0 0 rgba(255, 255, 255, 0.2);
}

.glass-primary-btn {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.8) 0%, rgba(236, 72, 153, 0.8) 100%);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    box-shadow: 0 4px 15px 0 rgba(168, 85, 247, 0.4), inset 0 1px 0 0 rgba(255, 255, 255, 0.2);
    transition: all 0.2s ease;
}
.glass-primary-btn:hover {
    background: linear-gradient(135deg, rgba(168, 85, 247, 1) 0%, rgba(236, 72, 153, 1) 100%);
    border-color: rgba(255, 255, 255, 0.5);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px 0 rgba(168, 85, 247, 0.6), inset 0 1px 0 0 rgba(255, 255, 255, 0.3);
}

.glass-table-row {
    background: rgba(255, 255, 255, 0.02);
    transition: background 0.2s ease;
}
.glass-table-row:hover {
    background: rgba(255, 255, 255, 0.07);
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

// Content Management State
const contentType = ref('tracks')
const contentItems = ref([])
const contentSearch = ref('')
const showEditor = ref(false)
const saving = ref(false)
const editingId = ref(null)
const editorForm = ref({})

const contentTypes = {
  'tracks': 'Tracks',
  'shows': 'Shows',
  'artists': 'Artists',
  'events': 'Events',
  'merch': 'Merch',
  'videos': 'Videos',
  'whats-new': "What's New"
}

// Map content type to default model fields
const getModelFields = (type) => {
  const defaults = {
    tracks: { track_id: '', title: '', artist: '', album: '', genre: '', audio_url: '', cover_art: '', featured: false, position: 0 },
    shows: { show_id: '', title: '', host: '', description: '', thumbnail: '', video_url: '', category: '', position: 0 },
    artists: { artist_id: '', name: '', slug: '', description: '', image: '', artist_type: '', featured: false, position: 0 },
    events: { event_id: '', title: '', date: '', time: '', venue: '', description: '', status: 'upcoming', position: 0 },
    merch: { item_id: '', name: '', price_usd: 20.0, available: true, image_url: '', position: 0 },
    videos: { video_id: '', title: '', description: '', url: '', status: 'coming_soon', position: 0 },
    'whats-new': { year: new Date().getFullYear().toString(), month: 'January', section: 'platform', title: '', description: '', position: 0 }
  }
  return defaults[type] || {}
}

const selectContentType = (type) => {
  contentType.value = type
  fetchContent()
}

const switchTab = (tab) => {
  currentTab.value = tab
  if (tab === 'content') fetchContent()
}

const fetchContent = async () => {
    loading.value = true
    try {
        const data = await apiFetch(`/api/admin/content/${contentType.value}?q=${contentSearch.value}`)
        contentItems.value = data.items
    } catch (e) {
        console.error("Failed to fetch content", e)
    } finally {
        loading.value = false
    }
}

const openContentEditor = (item = null) => {
  if (item) {
    editingId.value = item.id
    editorForm.value = { ...item }
  } else {
    editingId.value = null
    editorForm.value = getModelFields(contentType.value)
  }
  showEditor.value = true
}

const saveContent = async () => {
  saving.value = true
  try {
    const url = editingId.value 
      ? `/api/admin/content/${contentType.value}/${editingId.value}`
      : `/api/admin/content/${contentType.value}`
    
    const method = editingId.value ? 'PUT' : 'POST'
    
    // Process comma-separated arrays
    const payload = { ...editorForm.value }
    for (const key in payload) {
      if (Array.isArray(getModelFields(contentType.value)[key]) && typeof payload[key] === 'string') {
        payload[key] = payload[key].split(',').map(s => s.trim()).filter(Boolean)
      }
    }
    
    await apiFetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    
    showEditor.value = false
    fetchContent()
  } catch (e) {
    alert("Fail: " + e.message)
  } finally {
    saving.value = false
  }
}

const deleteContentItem = async (id) => {
  if (!confirm("Are you sure you want to delete this content? This cannot be undone.")) return
  try {
    await apiFetch(`/api/admin/content/${contentType.value}/${id}`, { method: 'DELETE' })
    fetchContent()
  } catch (e) {
    alert("Delete failed: " + e.message)
  }
}

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
