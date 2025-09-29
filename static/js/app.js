// Ahoy Indie Media - Main JavaScript (Global Version)

// unified API helper
async function api(url, method="GET", payload=null) {
  const opts = { 
    method, 
    headers: { "Content-Type": "application/json" }, 
    credentials: "include",
    redirect: "follow" // Follow redirects automatically
  };
  if (payload) opts.body = JSON.stringify(payload);
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error(`API ${method} ${url} -> ${res.status}`);
  try { return await res.json(); } catch { return {}; }
}

// Bookmark-only delegation
document.addEventListener("click", async (e) => {
  const bmBtn = e.target.closest("[data-bookmark]") || e.target.closest("[data-like]"); // compat
  if (!bmBtn) return;
  e.preventDefault();
  const id = bmBtn.dataset.id;
  const kind = bmBtn.dataset.kind || "track";
  if (!id) return;
  try {
    bmBtn.classList.add("is-loading");
    const { status } = await api("/api/bookmarks", "POST", { id, kind });
    bmBtn.classList.toggle("bookmarked", status === "bookmarked");
    window.__ahoyToast && window.__ahoyToast("Bookmarked!");
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

// Boot watchdog: clears the loading screen even if a request fails
(function boot() {
  function clearLoader() {
    const loader = document.getElementById("app-loader") || document.getElementById("loading-indicator");
    if (loader) loader.style.display = "none";
  }
  window.addEventListener("DOMContentLoaded", async () => {
    // try to hydrate bookmarks; even on failure, clear loader so UI is usable
    try { await window.hydrateBookmarksState(); } catch (e) { console.warn(e); }
    // If your app does additional bootstrapping, call it here in try/catch too.
    clearLoader();
  });

  // Safety net: if DOMContentLoaded didn't fire, force-clear loader after 5s
  setTimeout(clearLoader, 5000);
})();
