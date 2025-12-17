(() => {
  const STORAGE_KEY = "ahoy.bookmarks.v1";
  const API = "/api/bookmarks";
  const ACCESS_KEY = "access_token";
  const state = {
    items: {},
    loggedIn: !!(window.LOGGED_IN),
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

  function getAccessToken() {
    try { return localStorage.getItem(ACCESS_KEY) || null; } catch { return null; }
  }
  function authHeaders() {
    const t = getAccessToken();
    const h = { "Content-Type": "application/json" };
    if (t) h["Authorization"] = `Bearer ${t}`;
    return h;
  }

  async function fetchServer() {
    const token = getAccessToken();
    if (!token) return; // guest mode
    const r = await fetch(`${API}?page=1&per_page=100`, { headers: authHeaders() });
    if (!r.ok) return;
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
      const token = getAccessToken();
      if (!token) return; // guest mode handled via local above
      if (exists) {
        // Need bookmark id; find it by listing current
        const rList = await fetch(`${API}?page=1&per_page=100`, { headers: authHeaders() });
        const data = await rList.json();
        const found = (data.items || []).find((x) => x.media_id == it.id && x.media_type === (it.type === 'track' ? 'music' : it.type));
        if (found) {
          await fetch(`${API}/${found.id}`, { method: "DELETE", headers: authHeaders() });
        }
      } else {
        const media_type = it.type === 'track' ? 'music' : it.type;
        await fetch(API, { method: "POST", headers: authHeaders(), body: JSON.stringify({ media_id: String(it.id), media_type }) });
      }
    } catch (e) {
      if (String(e?.message || '').includes('401')) {
        if (confirm('Please log in to sync bookmarks. Go to login now?')) window.location.href = '/auth';
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
    // Aging
    getBookmarkAge,
    getBookmarkAgeCategory,
    getBookmarkFadeOpacity,
    markAccessed
  };

  state.items = loadLocal();

  // ✅ Integrate with Alpine.js
  document.addEventListener("alpine:init", () => {
    // Global bookmark handler for use in bookmark buttons throughout the site
    Alpine.data("globalBookmarkHandler", () => ({
      showCountFade: false,
      showExploreNotification: false,
      bookmarkCount: 0,

      init() {
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
      }
    }));

    Alpine.data("bookmarkHandler", () => ({
      bookmarks: state.items,
      animatingItems: new Set(),

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
  });

  // Initial fetch (logged-in sync)
  document.addEventListener("DOMContentLoaded", () => {
    fetchServer().catch(() => {});
  });
})();