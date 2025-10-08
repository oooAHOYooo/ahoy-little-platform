// Playlist Manager - JWT-aware client with guest fallback

function getAccessToken() {
  try { return localStorage.getItem("access_token") || null; } catch { return null; }
}

function authHeaders() {
  const token = getAccessToken();
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

async function api(url, method = "GET", payload = null) {
  const opts = { method, headers: authHeaders() };
  if (payload != null) opts.body = JSON.stringify(payload);
  const res = await fetch(url, opts);
  if (res.status === 401) {
    // Prompt login on unauthorized
    if (confirm("Your session has expired. Log in now?")) window.location.href = "/auth";
    throw new Error("Unauthorized");
  }
  if (!res.ok) throw new Error(`API ${method} ${url} -> ${res.status}`);
  try { return await res.json(); } catch { return {}; }
}

function mapKindToMediaType(kind) {
  // Legacy callers may use 'track' → map to 'music'
  if (kind === "track") return "music";
  return kind;
}

async function postHistory(media_id, media_type, action = "interact") {
  try {
    await fetch("/api/history", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ media_id, media_type, action })
    });
  } catch {}
}

window.Playlists = {
  load: (page = 1, per_page = 50) => api(`/api/playlists?page=${page}&per_page=${per_page}`),
  create: (name) => api("/api/playlists", "POST", { name }),
  rename: (id, name) => api(`/api/playlists/${id}`, "PATCH", { name }),
  remove: (id) => api(`/api/playlists/${id}`, "DELETE"),
  listItems: (id, page = 1, per_page = 100) => api(`/api/playlists/${id}/items?page=${page}&per_page=${per_page}`),
  addItem: async (id, itemId, kind = "track", position = null) => {
    const media_type = mapKindToMediaType(kind);
    const payload = { media_id: String(itemId), media_type };
    if (position != null) payload.position = position;
    const created = await api(`/api/playlists/${id}/items`, "POST", payload);
    // Fire-and-forget history
    postHistory(String(itemId), media_type, "playlist_add");
    return created;
  },
  removeItem: async (id, itemId /* server item id */) => {
    const out = await api(`/api/playlists/${id}/items/${itemId}`, "DELETE");
    return out;
  },
};

// Optional inline handler for a "new playlist" form if present
document.addEventListener("submit", async (e) => {
  const form = e.target.closest("#new-playlist-form");
  if (!form) return;
  e.preventDefault();
  const name = form.querySelector("[name=playlist_name]")?.value?.trim();
  if (!name) return;
  try {
    await window.Playlists.create(name);
    form.reset();
    // TODO: refresh playlist UI
    window.__ahoyToast && window.__ahoyToast("Playlist created");
  } catch (err) {
    console.error(err);
    window.__ahoyToast && window.__ahoyToast("Could not create playlist");
  }
});

// Offer to import guest data on first login (bookmarks + playlists from local)
document.addEventListener("DOMContentLoaded", async () => {
  try {
    const token = getAccessToken();
    const IMPORT_FLAG = "ahoy.import.done";
    if (!token || localStorage.getItem(IMPORT_FLAG) === "1") return;

    // Detect local bookmarks from bookmarks module
    const bmRaw = localStorage.getItem("ahoy.bookmarks.v1");
    const bm = bmRaw ? JSON.parse(bmRaw) : { items: {} };
    const guestBookmarks = Object.values(bm.items || {});

    if (guestBookmarks.length > 0) {
      const yes = confirm("Import guest bookmarks to your account?");
      if (yes) {
        for (const it of guestBookmarks) {
          const media_type = mapKindToMediaType(it.type || it.media_type || "music");
          try {
            await api("/api/bookmarks", "POST", { media_id: String(it.id || it.media_id), media_type });
          } catch {}
        }
        // Clear guest bookmarks
        localStorage.removeItem("ahoy.bookmarks.v1");
      }
    }

    localStorage.setItem(IMPORT_FLAG, "1");
  } catch {}
});