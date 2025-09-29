// Playlist Manager - Global Version

async function api(url, method="GET", payload=null) {
  const opts = { method, headers: { "Content-Type": "application/json" }, credentials: "include" };
  if (payload) opts.body = JSON.stringify(payload);
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error(`API ${method} ${url} -> ${res.status}`);
  try { return await res.json(); } catch { return {}; }
}

window.Playlists = {
  load: () => api("/api/playlists"),
  create: (name, description="") => api("/api/playlists", "POST", { name, description }),
  rename: (id, name, description="") => api(`/api/playlists/${id}`, "PUT", { name, description }),
  remove: (id) => api(`/api/playlists/${id}`, "DELETE"),
  addItem: (id, itemId, kind="track") => api(`/api/playlists/${id}/items`, "POST", { id: itemId, kind }),
  removeItem: (id, itemId, kind="track") => api(`/api/playlists/${id}/items`, "DELETE", { id: itemId, kind }),
};

// Optional inline handler for a "new playlist" form if present
document.addEventListener("submit", async (e) => {
  const form = e.target.closest("#new-playlist-form");
  if (!form) return;
  e.preventDefault();
  const name = form.querySelector("[name=playlist_name]")?.value?.trim();
  const description = form.querySelector("[name=playlist_description]")?.value || "";
  if (!name) return;
  try {
    await window.Playlists.create(name, description);
    form.reset();
    // TODO: refresh playlist UI
    window.__ahoyToast && window.__ahoyToast("Playlist created");
  } catch (err) {
    console.error(err);
    window.__ahoyToast && window.__ahoyToast("Could not create playlist");
  }
});