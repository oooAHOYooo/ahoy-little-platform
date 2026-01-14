(() => {
  const STORAGE_KEY = "ahoy.bookmarks.v1";
  const API = "/api/bookmarks";
  const state = {
    items: {},
    loggedIn: false, // Will be determined by checking session
    serverLoaded: false
  };

  const keyOf = (type, id) => `${type}:${id}`;
  const toObj = (arr, keyFn) => arr.reduce((m, x) => (m[keyFn(x)] = x, m), {});

  function loadLocal() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return {};
      const parsed = JSON.parse(raw);
      return parsed.items || {};
    } catch {
      return {};
    }
  }
  function saveLocal() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ items: state.items }));
  }

  function setLocalItem(it) {
    const k = it.key || keyOf(it.type, it.id);
    const now = new Date().toISOString();
    state.items[k] = { 
      ...it, 
      key: k, 
      added_at: it.added_at || now,
      last_accessed: it.last_accessed || now,
      access_count: it.access_count || 0,
      tags: it.tags || []
    };
    saveLocal();
  }
  function removeLocalKey(k) {
    delete state.items[k];
    saveLocal();
  }

  // Session-based auth (no JWT tokens needed)
  function authHeaders() {
    return { 
      "Content-Type": "application/json"
      // No Authorization header - Flask sessions handle auth via cookies
    };
  }

  async function fetchServer() {
    // Check if user is logged in by trying to fetch their bookmarks
    // Guest mode: just use local storage
    const r = await fetch(`${API}?page=1&per_page=100`, { 
      headers: authHeaders(),
      credentials: 'include' // Include session cookies
    });
    if (!r.ok) {
      // Not logged in or error - continue with guest mode
      return;
    }
    const data = await r.json();
    const serverItems = toObj((data.items || []).map((x) => ({
      id: x.media_id,
      type: x.media_type,
      key: `${x.media_type}:${x.media_id}`,
      added_at: x.created_at,
    })), (x) => x.key);

    state.items = { ...serverItems };
    saveLocal();
    state.serverLoaded = true;
  }

  async function toggle(it) {
    const key = it.key || keyOf(it.type, it.id);
    const exists = !!state.items[key];
    exists ? removeLocalKey(key) : setLocalItem({ ...it, key });
    
    // Trigger a custom event to notify all Alpine.js components
    document.dispatchEvent(new CustomEvent('bookmarks:changed', { 
      detail: { items: state.items, action: exists ? 'remove' : 'add', item: it } 
    }));

    try {
      // Try to sync with server (session-based auth via cookies)
      if (exists) {
        // Need bookmark id; find it by listing current
        const rList = await fetch(`${API}?page=1&per_page=100`, { 
          headers: authHeaders(),
          credentials: 'include' // Include session cookies
        });
        if (!rList.ok) return; // Not logged in - guest mode
        const data = await rList.json();
        const found = (data.items || []).find((x) => x.media_id == it.id && x.media_type === (it.type === 'track' ? 'music' : it.type));
        if (found) {
          await fetch(`${API}/${found.id}`, { 
            method: "DELETE", 
            headers: authHeaders(),
            credentials: 'include'
          });
        }
      } else {
        const media_type = it.type === 'track' ? 'music' : it.type;
        await fetch(API, { 
          method: "POST", 
          headers: authHeaders(), 
          credentials: 'include',
          body: JSON.stringify({ media_id: String(it.id), media_type }) 
        });
      }
    } catch (e) {
      if (String(e?.message || '').includes('401') || String(e?.message || '').includes('Unauthorized')) {
        // Session expired or not logged in - continue with guest mode
        console.log('Not logged in, using guest mode for bookmarks');
      }
    }
  }

  // Nests system
  const NESTS_KEY = "ahoy.nests.v1";
  
  function loadNests() {
    try {
      const raw = localStorage.getItem(NESTS_KEY);
      if (!raw) return {};
      return JSON.parse(raw);
    } catch {
      return {};
    }
  }
  
  function saveNests(nests) {
    localStorage.setItem(NESTS_KEY, JSON.stringify(nests));
  }
  
  function createNest(name, description = "", color = "#00d4ff") {
    const nestId = `nest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const nests = loadNests();
    nests[nestId] = {
      id: nestId,
      name,
      description,
      color,
      created_at: new Date().toISOString(),
      item_count: 0
    };
    saveNests(nests);
    return nestId;
  }
  
  function updateNest(nestId, updates) {
    const nests = loadNests();
    if (nests[nestId]) {
      nests[nestId] = { ...nests[nestId], ...updates };
      saveNests(nests);
    }
  }
  
  function deleteNest(nestId) {
    const nests = loadNests();
    delete nests[nestId];
    saveNests(nests);
    
    // Remove nest_id from all bookmarks
    Object.values(state.items).forEach(item => {
      if (item.nest_id === nestId) {
        item.nest_id = null;
      }
    });
    saveLocal();
  }
  
  function addToNest(itemKey, nestId) {
    if (state.items[itemKey]) {
      state.items[itemKey].nest_id = nestId;
      saveLocal();
      
      // Update nest count
      const nests = loadNests();
      if (nests[nestId]) {
        nests[nestId].item_count = Object.values(state.items).filter(item => item.nest_id === nestId).length;
        saveNests(nests);
      }
    }
  }
  
  function removeFromNest(itemKey) {
    if (state.items[itemKey]) {
      const oldNestId = state.items[itemKey].nest_id;
      state.items[itemKey].nest_id = null;
      saveLocal();
      
      // Update nest count
      if (oldNestId) {
        const nests = loadNests();
        if (nests[oldNestId]) {
          nests[oldNestId].item_count = Object.values(state.items).filter(item => item.nest_id === oldNestId).length;
          saveNests(nests);
        }
      }
    }
  }
  
  // Aging system
  function getBookmarkAge(item) {
    const added = new Date(item.added_at);
    const now = new Date();
    const diffTime = Math.abs(now - added);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  }
  
  function getBookmarkAgeCategory(item) {
    const age = getBookmarkAge(item);
    if (age <= 1) return 'new';
    if (age <= 7) return 'recent';
    if (age <= 30) return 'older';
    return 'ancient';
  }
  
  function getBookmarkFadeOpacity(item) {
    const age = getBookmarkAge(item);
    const accessCount = item.access_count || 0;
    
    // Base opacity on age
    let opacity = 1;
    if (age > 30) opacity = 0.6;
    else if (age > 7) opacity = 0.8;
    else if (age > 1) opacity = 0.9;
    
    // Boost opacity based on access count
    const accessBoost = Math.min(accessCount * 0.1, 0.3);
    opacity = Math.min(opacity + accessBoost, 1);
    
    return opacity;
  }
  
  function markAccessed(itemKey) {
    if (state.items[itemKey]) {
      state.items[itemKey].last_accessed = new Date().toISOString();
      state.items[itemKey].access_count = (state.items[itemKey].access_count || 0) + 1;
      saveLocal();
    }
  }

  // Expose global API
  window.AhoyBookmarks = {
    all: () => Object.values(state.items),
    isBookmarked: (type, id) => !!state.items[keyOf(type, id)],
    count: () => Object.keys(state.items).length,
    toggle,
    // Nests
    getNests: () => Object.values(loadNests()),
    createNest,
    updateNest,
    deleteNest,
    addToNest,
    removeFromNest,
    // Aging
    getBookmarkAge,
    getBookmarkAgeCategory,
    getBookmarkFadeOpacity,
    markAccessed
  };

  state.items = loadLocal();

  // ✅ Integrate with Alpine.js (support both "before Alpine loads" and "after")
  function registerAlpineData() {
    // Guard: Alpine might not be present (or may load later)
    if (typeof Alpine === "undefined") return;
    // Global bookmark handler for use in bookmark buttons throughout the site
    Alpine.data("globalBookmarkHandler", () => ({
      nests: {},
      showNestMenu: false,
      showCountFade: false,
      showExploreNotification: false,
      bookmarkCount: 0,

      init() {
        this.loadNests();
        
        // Listen for nest changes
        document.addEventListener('bookmarks:changed', () => {
          this.loadNests();
        });
      },

      loadNests() {
        this.nests = {};
        if (window.AhoyBookmarks) {
          const nests = window.AhoyBookmarks.getNests();
          nests.forEach(nest => {
            this.nests[nest.id] = nest;
          });
        }
      },

      toggleBookmark(type, id, title, artwork) {
        if (window.AhoyBookmarks) {
          const item = {
            type,
            id,
            title,
            artwork,
            key: keyOf(type, id)
          };
          
          // Check if item is currently bookmarked
          const wasBookmarked = window.AhoyBookmarks.isBookmarked(type, id);
          window.AhoyBookmarks.toggle(item);
          
          // Dispatch bookmark change event for navbar updates
          document.dispatchEvent(new CustomEvent('bookmarks:changed', {
            detail: { 
              action: wasBookmarked ? 'removed' : 'added',
              item: item,
              totalCount: window.AhoyBookmarks.count()
            }
          }));
          
          // Show notification for new bookmarks
          if (!wasBookmarked) {
            // Get current bookmark count
            this.bookmarkCount = window.AhoyBookmarks.count();
            
            // Show count fade animation
            this.showCountFade = true;
            
            // Show explore notification after count fade
            setTimeout(() => {
              this.showExploreNotification = true;
            }, 2500); // Show after count fade starts to disappear
            
            // Trigger bookmark notification for navbar glow
            document.dispatchEvent(new CustomEvent('bookmark:notified', {
              detail: { count: this.bookmarkCount }
            }));
            
            window.__ahoyToast && window.__ahoyToast("Bookmarked!");
            // Trigger notification system
            window.__ahoyNotifyNewBookmark && window.__ahoyNotifyNewBookmark();
          }
        }
      },

      isBookmarked(type, id) {
        if (window.AhoyBookmarks) {
          return window.AhoyBookmarks.isBookmarked(type, id);
        }
        return false;
      },

      addToNest(type, id, nestId) {
        if (window.AhoyBookmarks) {
          const itemKey = keyOf(type, id);
          window.AhoyBookmarks.addToNest(itemKey, nestId);
        }
      },

      removeFromNest(type, id) {
        if (window.AhoyBookmarks) {
          const itemKey = keyOf(type, id);
          window.AhoyBookmarks.removeFromNest(itemKey);
        }
      },

      getCurrentNest(type, id) {
        if (window.AhoyBookmarks) {
          const itemKey = keyOf(type, id);
          const item = state.items[itemKey];
          return item?.nest_id || null;
        }
        return null;
      }
    }));

    Alpine.data("bookmarkHandler", () => ({
      bookmarks: state.items,
      animatingItems: new Set(),
      nests: {},
      showNestManager: false,
      newNestName: '',
      newNestDescription: '',
      newNestColor: '#00d4ff',

      init() {
        // Listen for bookmark changes
        document.addEventListener('bookmarks:changed', (e) => {
          this.bookmarks = { ...e.detail.items };
          
          // Add fun animation for the changed item
          if (e.detail.item) {
            const itemKey = e.detail.item.key || keyOf(e.detail.item.type, e.detail.item.id);
            this.animatingItems.add(itemKey);
            setTimeout(() => {
              this.animatingItems.delete(itemKey);
            }, 600);
          }
        });
        
        // Load nests
        this.loadNests();
      },

      loadNests() {
        this.nests = {};
        const nests = window.AhoyBookmarks.getNests();
        nests.forEach(nest => {
          this.nests[nest.id] = nest;
        });
      },

      toggleBookmark(it) {
        window.AhoyBookmarks.toggle(it);
      },

      isBookmarked(type, id) {
        return window.AhoyBookmarks.isBookmarked(type, id);
      },

      list() {
        return window.AhoyBookmarks.all();
      },

      isAnimating(item) {
        const key = item.key || keyOf(item.type, item.id);
        return this.animatingItems.has(key);
      },

      // Nests functionality
      createNest() {
        if (!this.newNestName.trim()) return;
        
        const nestId = window.AhoyBookmarks.createNest(
          this.newNestName.trim(),
          this.newNestDescription.trim(),
          this.newNestColor
        );
        
        this.loadNests();
        this.newNestName = '';
        this.newNestDescription = '';
        this.newNestColor = '#00d4ff';
        this.showNestManager = false;
      },

      deleteNest(nestId) {
        if (confirm('Are you sure you want to delete this nest? All bookmarks will be moved to "Unorganized".')) {
          window.AhoyBookmarks.deleteNest(nestId);
          this.loadNests();
        }
      },

      addToNest(itemKey, nestId) {
        window.AhoyBookmarks.addToNest(itemKey, nestId);
        this.loadNests();
      },

      removeFromNest(itemKey) {
        window.AhoyBookmarks.removeFromNest(itemKey);
        this.loadNests();
      },

      getNestName(nestId) {
        return this.nests[nestId]?.name || 'Unorganized';
      },

      getNestColor(nestId) {
        return this.nests[nestId]?.color || '#666';
      },

      // Aging functionality
      getBookmarkAge(item) {
        return window.AhoyBookmarks.getBookmarkAge(item);
      },

      getBookmarkAgeCategory(item) {
        return window.AhoyBookmarks.getBookmarkAgeCategory(item);
      },

      getBookmarkFadeOpacity(item) {
        return window.AhoyBookmarks.getBookmarkFadeOpacity(item);
      },

      markAccessed(itemKey) {
        window.AhoyBookmarks.markAccessed(itemKey);
      },

      getAgeLabel(item) {
        const age = this.getBookmarkAge(item);
        if (age <= 1) return 'New';
        if (age <= 7) return 'Recent';
        if (age <= 30) return 'Older';
        return 'Ancient';
      },

      getAgeIcon(item) {
        const category = this.getBookmarkAgeCategory(item);
        switch (category) {
          case 'new': return 'fas fa-sparkles';
          case 'recent': return 'fas fa-clock';
          case 'older': return 'fas fa-calendar';
          case 'ancient': return 'fas fa-hourglass-half';
          default: return 'fas fa-bookmark';
        }
      }
    }));
  }

  document.addEventListener("alpine:init", registerAlpineData);
  // If Alpine is already present (script order), register immediately
  try { registerAlpineData(); } catch (_) {}

  // Initial fetch (logged-in sync)
  document.addEventListener("DOMContentLoaded", () => {
    // Avoid hitting the server for guests (big win on mobile)
    if (!window.LOGGED_IN) return;
    fetchServer().catch(() => {});
  });
})();