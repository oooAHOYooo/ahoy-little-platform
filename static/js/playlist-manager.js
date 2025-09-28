// Ahoy Indie Media - Playlist Manager JavaScript

async function api(url, method="GET", payload=null) {
    const opts = { method, headers: { "Content-Type": "application/json" }, credentials: "include" };
    if (payload) opts.body = JSON.stringify(payload);
    const res = await fetch(url, opts);
    if (!res.ok) throw new Error(`API ${method} ${url} -> ${res.status}`);
    try { return await res.json(); } catch { return {}; }
}

export async function loadPlaylists() {
    return api("/api/playlists");
}

export async function createPlaylist(name, description="") {
    return api("/api/playlists", "POST", { name, description });
}

export async function renamePlaylist(id, name, description="") {
    return api(`/api/playlists/${id}`, "PUT", { name, description });
}

export async function deletePlaylist(id) {
    return api(`/api/playlists/${id}`, "DELETE");
}

export async function addToPlaylist(id, itemId, kind="track") {
    return api(`/api/playlists/${id}/items`, "POST", { id: itemId, kind });
}

export async function removeFromPlaylist(id, itemId, kind="track") {
    return api(`/api/playlists/${id}/items`, "DELETE", { id: itemId, kind });
}

// Example UI glue (optional)
document.addEventListener("submit", async (e) => {
    const form = e.target.closest("#new-playlist-form");
    if (!form) return;
    e.preventDefault();
    const name = form.querySelector("[name=playlist_name]").value.trim();
    const description = form.querySelector("[name=playlist_description]")?.value || "";
    if (!name) return;
    try {
        await createPlaylist(name, description);
        form.reset();
        // refresh list UI...
        if (window.ahoyApp && window.ahoyApp.showNotification) {
            window.ahoyApp.showNotification("Playlist created successfully!", "success");
        }
    } catch (err) {
        console.error(err);
        if (window.ahoyApp && window.ahoyApp.showNotification) {
            window.ahoyApp.showNotification("Failed to create playlist", "error");
        }
    }
});

// Make functions available globally
window.PlaylistManager = {
    loadPlaylists,
    createPlaylist,
    renamePlaylist,
    deletePlaylist,
    addToPlaylist,
    removeFromPlaylist
};
