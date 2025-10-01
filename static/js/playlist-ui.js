// Tiny client for the Playlists API
const fx = (typeof window !== "undefined" && window.fetchWithPaywall) || fetch;

const PlaylistsAPI = {
  async createFromCollection(collectionId, { owner, name, is_public = false }) {
    const r = await fx(`/api/playlists/from-collection/${collectionId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ owner, name, is_public }),
    });
    if (!r.ok) throw new Error((await r.json()).error || "Failed to create playlist");
    return r.json();
  },
  async list(user) {
    const r = await fx(`/api/playlists/?user=${encodeURIComponent(user)}`);
    return r.json();
  },
};

// Bottom-sheet helper
function openSheet(el) { el?.classList.remove("hidden"); requestAnimationFrame(() => el?.classList.add("opacity-100")); }
function closeSheet(el) { el?.classList.remove("opacity-100"); setTimeout(()=>el?.classList.add("hidden"), 150); }

// Suggest cute playlist names from collection name
function suggestName(collectionName) {
  const vibes = ["Mix", "Vibes", "Flow", "Session", "Queue", "Run", "Trip", "Loop"];
  const pick = vibes[Math.floor(Math.random() * vibes.length)];
  return `${collectionName} ${pick}`;
}

// Wire up "Make Playlist" buttons anywhere on the page
document.addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-make-playlist]");
  if (!btn) return;
  const sheet = document.getElementById("playlist-sheet");
  const form  = sheet?.querySelector("form");
  const nameInput = sheet?.querySelector("[name='playlist_name']");
  const ownerInput = sheet?.querySelector("[name='owner']");
  const colNameLabel = sheet?.querySelector("[data-col-name]");

  const collectionId = btn.getAttribute("data-collection-id");
  const collectionName = btn.getAttribute("data-collection-name") || "My Collection";
  const owner = btn.getAttribute("data-owner");

  ownerInput.value = owner || "";
  nameInput.value = suggestName(collectionName);
  colNameLabel.textContent = collectionName;

  form.dataset.collectionId = collectionId;
  openSheet(sheet);
});

// Handle sheet submit
document.addEventListener("submit", async (e) => {
  const form = e.target.closest("#playlist-sheet form");
  if (!form) return;

  e.preventDefault();
  const sheet = document.getElementById("playlist-sheet");
  const submitBtn = form.querySelector("button[type='submit']");
  const owner = form.querySelector("[name='owner']").value.trim();
  const name  = form.querySelector("[name='playlist_name']").value.trim();
  const isPublic = form.querySelector("[name='is_public']").checked;
  const collectionId = form.dataset.collectionId;

  submitBtn.disabled = true;
  submitBtn.textContent = "Creating…";

  try {
    const pl = await PlaylistsAPI.createFromCollection(collectionId, { owner, name, is_public: isPublic });

    // Fire a custom event your player/queue can listen to
    document.dispatchEvent(new CustomEvent("playlist:created", { detail: pl }));

    // Confetti-lite ✨
    const toast = document.getElementById("playlist-toast");
    toast.textContent = `Playlist "${pl.name}" is ready!`;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 2000);

    closeSheet(sheet);
  } catch (err) {
    alert(err.message || "Something went wrong");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Create Playlist";
  }
});

// Optional: a global handler where your player can react
document.addEventListener("playlist:created", (e) => {
  // Example: auto-open the new playlist in your player sidebar / queue
  // console.log("New playlist created", e.detail);
});
