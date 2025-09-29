(() => {
  const STORAGE_KEY = "ahoy.bookmarks.v1";
  const API = "/api/bookmarks";
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
    state.items[k] = { ...it, key: k, added_at: it.added_at || new Date().toISOString() };
    saveLocal();
  }
  function removeLocalKey(k) {
    delete state.items[k];
    saveLocal();
  }

  async function fetchServer() {
    if (!state.loggedIn) return;
    const r = await fetch(API);
    if (!r.ok) return;
    const data = await r.json();
    const serverItems = toObj(data.items || [], (x) => x.key);

    // Merge local → server if needed
    const localOnly = Object.values(state.items).filter(it => !serverItems[it.key]);
    if (localOnly.length) {
      await fetch(`${API}/merge`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: localOnly })
      }).catch(() => {});
    }

    state.items = { ...loadLocal(), ...serverItems };
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
      const r = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: exists ? "remove" : "add", item: { ...it, key } })
      });
      if (r.ok) {
        const data = await r.json();
        if (Array.isArray(data.items)) {
          state.items = toObj(data.items, (x) => x.key);
          saveLocal();
        }
      }
    } catch {}
  }

  // Expose global API
  window.AhoyBookmarks = {
    all: () => Object.values(state.items),
    isBookmarked: (type, id) => !!state.items[keyOf(type, id)],
    toggle,
  };

  state.items = loadLocal();

  // ✅ Integrate with Alpine.js
  document.addEventListener("alpine:init", () => {
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
      }
    }));
  });

  // Initial fetch (logged-in sync)
  document.addEventListener("DOMContentLoaded", () => {
    fetchServer().catch(() => {});
  });
})();