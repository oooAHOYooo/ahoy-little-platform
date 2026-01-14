// ==== Auth helpers (session/cookie-based) ==================================
window.AHOY_AUTH = {
  async login(emailOrUsername, password) {
    const r = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      credentials: 'include', // Session cookies
      body: JSON.stringify({ email: emailOrUsername, password }) // Backend accepts email or username
    });
    if (!r.ok) throw new Error((await r.json()).message || 'Login failed');
    return r.json();
  },
  async logout() {
    const r = await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
    if (!r.ok) throw new Error('Logout failed');
    return true;
  },
  async me() {
    const r = await fetch('/api/user/profile', { credentials: 'include' });
    if (!r.ok) return null;
    return r.json();
  }
};
// Ahoy Indie Media - Main JavaScript (Global Version)
// ==== Slug + link helpers ===================================================
window.slugify = function(s){
  return String(s || '').toLowerCase().trim()
    .replace(/[^a-z0-9]+/g,'-')
    .replace(/^-+|-+$/g,'');
};
window.artistHref = function(artist){
  return `/artist/${window.slugify(artist.slug || artist.name)}`;
};

// ==== Artist detail bootstrap ==============================================
document.addEventListener('DOMContentLoaded', async () => {
  const m = location.pathname.match(/\/artist\/([^\/?#]+)/);
  if (!m) return;
  const id = decodeURIComponent(m[1]);
  try {
    const r = await fetch(`/api/artist/${id}`);
    if (!r.ok) { 
      const target = document.querySelector('[data-artist-name]') || document.body;
      target.innerHTML = '<h2>Artist not found</h2>';
      return; 
    }
    const data = await r.json();
    const artist = data.artist || data;
    // attach tracks/shows if provided separately
    if ((data.tracks && Array.isArray(data.tracks)) || (data.shows && Array.isArray(data.shows))) {
      if (!artist.tracks && data.tracks) artist.tracks = data.tracks;
      if (!artist.shows && data.shows) artist.shows = data.shows;
    }
    const nameEl = document.querySelector('[data-artist-name]');
    if (nameEl) nameEl.textContent = artist.name || '';
    // expose for page component
    window.__ARTIST__ = artist;
    document.dispatchEvent(new CustomEvent('artist:loaded', { detail: artist }));
  } catch (e) {
    console.error('Failed to load artist', e);
  }
});
// ============================================================================

// Request deduplication cache - prevents duplicate simultaneous requests
const _requestCache = new Map();
const _pendingRequests = new Map();

// Global fetch wrapper for request deduplication (only for GET requests)
// This prevents multiple components from making the same API call simultaneously
const _originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  const isGet = method === 'GET';
  const cacheKey = isGet && typeof url === 'string' ? url : null;
  
  // Only deduplicate GET requests to API endpoints
  if (!isGet || !cacheKey || !cacheKey.startsWith('/api/')) {
    return _originalFetch(url, options);
  }
  
  // If we have a pending request, return the same promise
  if (_pendingRequests.has(cacheKey)) {
    return _pendingRequests.get(cacheKey).then(res => res.clone());
  }
  
  // Create the request
  const requestPromise = _originalFetch(url, options)
    .finally(() => {
      // Remove from pending requests after a short delay
      setTimeout(() => {
        _pendingRequests.delete(cacheKey);
      }, 50);
    });
  
  // Store pending request
  _pendingRequests.set(cacheKey, requestPromise);
  
  return requestPromise.then(res => res.clone());
};

// Unified API helper with request deduplication
async function api(url, method="GET", payload=null) {
  // Only deduplicate GET requests (safe to cache/share)
  const cacheKey = method === "GET" ? url : null;
  
  // If this is a GET request and we have a pending request, wait for it
  if (cacheKey && _pendingRequests.has(cacheKey)) {
    return _pendingRequests.get(cacheKey);
  }
  
  // If this is a GET request and we have cached data (within 5 seconds), return it
  if (cacheKey && _requestCache.has(cacheKey)) {
    const cached = _requestCache.get(cacheKey);
    const age = Date.now() - cached.timestamp;
    if (age < 5000) { // 5 second cache window
      return Promise.resolve(cached.data);
    }
  }
  
  const opts = { 
    method, 
    headers: { "Content-Type": "application/json" }, 
    credentials: "include",
    redirect: "follow" // Follow redirects automatically
  };
  if (payload) opts.body = JSON.stringify(payload);
  
  // Create the request promise
  const requestPromise = fetch(url, opts)
    .then(res => {
      if (!res.ok) throw new Error(`API ${method} ${url} -> ${res.status}`);
      try { return res.json(); } catch { return {}; }
    })
    .then(data => {
      // Cache successful GET responses
      if (cacheKey) {
        _requestCache.set(cacheKey, { data, timestamp: Date.now() });
        // Clean up old cache entries (older than 30 seconds)
        for (const [key, value] of _requestCache.entries()) {
          if (Date.now() - value.timestamp > 30000) {
            _requestCache.delete(key);
          }
        }
      }
      return data;
    })
    .finally(() => {
      // Remove from pending requests
      if (cacheKey) {
        _pendingRequests.delete(cacheKey);
      }
    });
  
  // Store pending request for GET requests
  if (cacheKey) {
    _pendingRequests.set(cacheKey, requestPromise);
  }
  
  return requestPromise;
}

// Bookmark-only delegation (legacy support for non-Alpine.js buttons)
document.addEventListener("click", async (e) => {
  const bmBtn = e.target.closest("[data-bookmark]") || e.target.closest("[data-like]"); // compat
  if (!bmBtn) return;
  
  // Skip if this is an Alpine.js handled button (has x-data)
  if (bmBtn.closest('[x-data]')) return;
  
  e.preventDefault();
  const id = bmBtn.dataset.id;
  const kind = bmBtn.dataset.kind || "track";
  if (!id) return;
  try {
    bmBtn.classList.add("is-loading");
    const { status } = await api("/api/bookmarks", "POST", { id, kind });
    bmBtn.classList.toggle("bookmarked", status === "bookmarked");
    
    // Show notification for new bookmarks
    if (status === "bookmarked") {
      window.__ahoyToast && window.__ahoyToast("Bookmarked!");
      // Trigger notification system
      window.__ahoyNotifyNewBookmark && window.__ahoyNotifyNewBookmark();
    }
  } catch (err) {
    console.error(err);
    // Handle 302 redirects and 401 errors (not logged in)
    if (err.message.includes("302") || err.message.includes("redirect") || err.message.includes("401")) {
      window.__ahoyToast && window.__ahoyToast("Please sign in to save bookmarks");
    } else {
      window.__ahoyToast && window.__ahoyToast("Failed to bookmark");
    }
  } finally {
    bmBtn.classList.remove("is-loading");
  }
});

// Safe API helper for 401-tolerant calls
async function safeGet(url) {
  try {
    const r = await fetch(url);
    if (r.status === 401) return null;
    if (!r.ok) return null;
    return await r.json();
  } catch { return null; }
}

// Make hydrate function global (no ES module export!)
window.hydrateBookmarksState = async function hydrateBookmarksState() {
  try {
    const r = await fetch('/api/bookmarks', { headers: { 'Content-Type': 'application/json' } });
    if (!r.ok) return; // guests still get 200 with persisted:false in our blueprint
    const data = await r.json();
    // expose for any UI that wants it
    window.__BOOKMARKS__ = Array.isArray(data.items) ? data.items : [];
    // optional: trigger a custom event so components can react
    document.dispatchEvent(new CustomEvent('bookmarks:hydrated', { detail: window.__BOOKMARKS__ }));
    
    // Update existing bookmark button states (for backward compatibility)
    const set = new Set(window.__BOOKMARKS__.map(item => item.key || `${item.type}:${item.id}`));
    document.querySelectorAll("[data-bookmark], [data-like]").forEach(btn => {
      const id = btn.dataset.id;
      const kind = btn.dataset.kind || btn.dataset.type || "track";
      if (!id) return;
      btn.classList.toggle("bookmarked", set.has(`${kind}:${id}`));
    });
  } catch (e) {
    // offline or server down — ignore, the client-side localStorage UI still works
  }
};

// Simple toast (optional)
window.__ahoyToast = function(msg) {
  let el = document.getElementById("ahoy-toast");
  if (!el) {
    el = document.createElement("div");
    el.id = "ahoy-toast";
    el.style.cssText = "position:fixed;bottom:20px;left:50%;transform:translateX(-50%);padding:10px 16px;background:#222;color:#fff;border-radius:8px;z-index:9999;opacity:.95";
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.style.display = "block";
  setTimeout(()=>{ el.style.display="none"; }, 2200);
};

// Boot watchdog: works with new loader system
(function boot() {
  window.addEventListener("DOMContentLoaded", async () => {
    // try to hydrate bookmarks; even on failure, clear loader so UI is usable
    try { await window.hydrateBookmarksState(); } catch (e) { console.warn(e); }
    // Loader is now handled by loader.js with progress tracking
  });
})();

// ========================================
// 🔔 NOTIFICATION SYSTEM
// ========================================

// Global notification state
window.__ahoyNotificationState = {
  newBookmarkCount: 0,
  hasNewBookmarks: false,
  lastBookmarkCount: 0
};

// Function to notify about new bookmarks
window.__ahoyNotifyNewBookmark = function() {
  window.__ahoyNotificationState.newBookmarkCount++;
  window.__ahoyNotificationState.hasNewBookmarks = true;
  
  // Update navbar state if available
  if (window.navbar && typeof window.navbar === 'function') {
    const navbar = window.navbar();
    if (navbar) {
      navbar.newBookmarkCount = window.__ahoyNotificationState.newBookmarkCount;
      navbar.hasNewBookmarks = window.__ahoyNotificationState.hasNewBookmarks;
    }
  }
  
  // Dispatch custom event for other components
  document.dispatchEvent(new CustomEvent('bookmark:notified', { 
    detail: { count: window.__ahoyNotificationState.newBookmarkCount } 
  }));
};

// Function to clear notifications (when user visits bookmarks page)
window.__ahoyClearBookmarkNotifications = function() {
  window.__ahoyNotificationState.newBookmarkCount = 0;
  window.__ahoyNotificationState.hasNewBookmarks = false;
  
  // Update navbar state if available
  if (window.navbar && typeof window.navbar === 'function') {
    const navbar = window.navbar();
    if (navbar) {
      navbar.newBookmarkCount = 0;
      navbar.hasNewBookmarks = false;
    }
  }
  
  // Dispatch custom event
  document.dispatchEvent(new CustomEvent('bookmark:notifications-cleared'));
};

// Initialize notification state on page load
document.addEventListener('DOMContentLoaded', function() {
  // Check if we're on the bookmarks page and clear notifications
  if (window.location.pathname === '/bookmarks') {
    window.__ahoyClearBookmarkNotifications();
  }
});

// ========================================
// 🧭 NAVBAR FUNCTION
// ========================================

// Define the navbar function for Alpine.js
window.navbar = function() {
  return {
    // State
    newBookmarkCount: 0,
    hasNewBookmarks: false,
    totalBookmarkCount: 0,
    isLoggedIn: !!window.LOGGED_IN,
    userProfile: window.userProfile || {},
    searchQuery: '',
    leftMenuOpen: false,
    rightMenuOpen: false,
    bookmarkPoller: null,
    
    // Initialize
    init() {
      this.setupEventListeners();
      // Load bookmark count with a small delay to ensure AhoyBookmarks is available
      setTimeout(() => {
        this.loadBookmarkCount();
      }, 100);
    },
    
    // Load current bookmark count
    loadBookmarkCount() {
      // Try multiple ways to get bookmark count
      if (window.AhoyBookmarks) {
        this.totalBookmarkCount = window.AhoyBookmarks.count();
      } else {
        // Fallback: try to read from localStorage directly
        try {
          const rawData = localStorage.getItem('ahoy.bookmarks.v1');
          if (rawData) {
            const data = JSON.parse(rawData);
            if (data.items) {
              this.totalBookmarkCount = Object.keys(data.items).length;
            }
          }
        } catch (e) {
          console.error('Error reading bookmark count:', e);
        }
      }
    },
    
    // Setup event listeners
    setupEventListeners() {
      // Listen for bookmark changes
      document.addEventListener('bookmarks:changed', () => {
        this.loadBookmarkCount();
      });
      
      // Listen for bookmark notifications
      document.addEventListener('bookmark:notified', (e) => {
        this.newBookmarkCount = e.detail.count;
        this.hasNewBookmarks = true;
      });
      
      // Listen for notification clearing
      document.addEventListener('bookmark:notifications-cleared', () => {
        this.newBookmarkCount = 0;
        this.hasNewBookmarks = false;
      });
      
      // Periodic refresh to ensure count stays updated
      // Optimization: only poll while tab is visible (reduces background CPU)
      const startPoll = () => {
        if (this.bookmarkPoller) return;
        this.bookmarkPoller = setInterval(() => {
          this.loadBookmarkCount();
        }, 2000);
      };
      const stopPoll = () => {
        if (!this.bookmarkPoller) return;
        clearInterval(this.bookmarkPoller);
        this.bookmarkPoller = null;
      };

      // Start polling immediately if visible
      if (document.visibilityState === 'visible') startPoll();

      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
          this.loadBookmarkCount(); // quick resync on return
          startPoll();
        } else {
          stopPoll();
        }
      });
    },
    
    // Search functionality
    performSearch() {
      if (this.searchQuery.trim()) {
        window.location.href = `/search?q=${encodeURIComponent(this.searchQuery.trim())}`;
      }
    },
    
    clearSearch() {
      this.searchQuery = '';
    },
    
    // Fullscreen toggle
    toggleFullscreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
      } else {
        document.exitFullscreen();
      }
    },
    
    // Logout functionality
    logout() {
      // Add logout logic here
      window.location.href = '/logout';
    }
  };
};

// Note: appData() is now defined inline in base.html before Alpine.js loads
// This ensures it's available when Alpine initializes