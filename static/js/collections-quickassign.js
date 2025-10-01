// v2: Quick-assign popover where each Collection row shows a tiny ➕ on hover
const fx = (typeof window !== "undefined" && window.fetchWithPaywall) || fetch;

const CollectionsAPI = {
  async list(user) {
    const r = await fx(`/api/collections/?user=${encodeURIComponent(user)}`);
    return r.json();
  },
  async create({ name, owner }) {
    const r = await fx(`/api/collections/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, owner }),
    });
    return r.json();
  },
  async addItem(collectionId, { id, type }) {
    const r = await fx(`/api/collections/${collectionId}/items`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, type }),
    });
    return r.json();
  },
};

const Last = {
  get(owner) { try { return JSON.parse(localStorage.getItem(`ahoy:lastCol:${owner}`)); } catch { return null; } },
  set(owner, col) { localStorage.setItem(`ahoy:lastCol:${owner}`, JSON.stringify({ id: col.id, name: col.name })); }
};

async function openQuickAssign(btn) {
  const owner    = btn.getAttribute("data-owner");
  const itemId   = btn.getAttribute("data-id");
  const itemType = btn.getAttribute("data-type"); // 'track' | 'show' | 'episode'
  
  console.log("🔍 Quick assign clicked:", { owner, itemId, itemType, btn });
  
  if (!owner || !itemId || !itemType) {
    console.warn("❌ Missing required data:", { owner, itemId, itemType });
    return;
  }

  console.log("📁 Creating collection popup with z-index 9999");

  let cols = [];
  try {
    cols = await CollectionsAPI.list(owner);
    console.log("📁 Loaded collections:", cols);
  } catch (error) {
    console.error("❌ Error loading collections:", error);
    cols = [];
  }
  const last = Last.get(owner);

  const pop = document.createElement("div");
  pop.className = "qa-pop fixed z-[9999] w-[320px] rounded-xl shadow-2xl border border-white/10 bg-black/90 text-white p-2 backdrop-blur";
  pop.innerHTML = `
    <div class="px-2 pt-1 pb-2 text-xs text-white/70">Move to Collection</div>
    <div class="px-2"><input class="w-full text-sm bg-white/5 rounded-lg px-2 py-1 outline-none" placeholder="Filter collections…" data-filter></div>
    <div class="max-h-56 overflow-auto mt-2 space-y-1" data-col-list></div>
    <div class="mt-3 p-2 rounded-lg bg-white/5">
      <input class="w-full bg-transparent outline-none text-sm" placeholder="New collection name…" data-new-name>
      <button class="mt-2 w-full text-sm rounded-lg bg-white text-black py-1.5" data-create>+ Create & Assign</button>
    </div>
  `;

  // list builder (each row gets a hover ➕)
  const list = pop.querySelector("[data-col-list]");
  function row(c, isLast=false) {
    const el = document.createElement("button");
    el.type = "button";
    el.className = `group w-full flex items-center justify-between gap-2 text-left px-2 py-1.5 rounded-lg hover:bg-white/10 ${isLast ? "ring-1 ring-white/30" : ""}`;
    el.innerHTML = `
      <span class="truncate">${c.name}</span>
      <span class="opacity-0 group-hover:opacity-100 transition text-base leading-none">➕</span>
    `;
    el.dataset.colId = c.id;
    return el;
  }
  if (last && cols.find(c => c.id === last.id)) list.appendChild(row(last, true));
  cols.filter(c => !last || c.id !== last.id).forEach(c => list.appendChild(row(c)));

  document.body.appendChild(pop);
  // position near button
  const rect = btn.getBoundingClientRect();
  const top  = window.scrollY + rect.top - pop.offsetHeight - 8;
  const left = Math.max(12, Math.min(window.scrollX + rect.left, window.scrollX + window.innerWidth - 340));
  pop.style.top  = `${Math.max(12, top)}px`;
  pop.style.left = `${left}px`;

  const close = () => { pop.remove(); document.removeEventListener("click", onDoc); };

  async function assign(col) {
    await CollectionsAPI.addItem(col.id, { id: itemId, type: itemType });
    Last.set(owner, col);
    // update badge on the card immediately
    const card  = btn.closest("[data-card]");
    const badge = card?.querySelector("[data-collection-badge]");
    if (badge) {
      badge.textContent = col.name;
      badge.classList.remove("bg-white/10");
      badge.classList.add("bg-blue-600");
    }
    document.dispatchEvent(new CustomEvent("ahoy:toast", { detail: `Added to "${col.name}"` }));
    close();
  }

  // filter typing
  pop.querySelector("[data-filter]").addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase();
    [...list.children].forEach(li => {
      const name = li.querySelector("span").textContent.toLowerCase();
      li.classList.toggle("hidden", !name.includes(q));
    });
  });

  // click on a row (or its ➕) assigns
  list.addEventListener("click", async (e) => {
    const b = e.target.closest("button[data-col-id]");
    if (!b) return;
    const id = b.dataset.colId;
    const col = cols.find(c => c.id === id) || (last && last.id === id ? last : null);
    if (col) assign(col);
  });

  // create & assign
  pop.querySelector("[data-create]").addEventListener("click", async () => {
    const name = pop.querySelector("[data-new-name]").value.trim();
    if (!name) return;
    const created = await CollectionsAPI.create({ name, owner });
    assign(created);
  });

  const onDoc = (e) => { if (!pop.contains(e.target) && e.target !== btn) close(); };
  setTimeout(() => document.addEventListener("click", onDoc), 0);
}

// Expose globally for Alpine.js
window.openQuickAssign = openQuickAssign;

// Delegate from any button with data-quick-assign
document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-quick-assign]");
  if (btn) {
    console.log("📁 Quick assign button clicked:", btn);
    e.preventDefault();
    e.stopPropagation();
    openQuickAssign(btn);
  }
});

// Optional: quick last-collection add (one click ➕)
document.addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-quick-last]");
  if (!btn) return;
  const owner = btn.getAttribute("data-owner");
  const itemId = btn.getAttribute("data-id");
  const itemType = btn.getAttribute("data-type");
  const last = Last.get(owner);
  if (!last) return openQuickAssign(btn);
  await CollectionsAPI.addItem(last.id, { id: itemId, type: itemType });
  const card = btn.closest("[data-card]");
  const badge = card?.querySelector("[data-collection-badge]");
  if (badge) { badge.textContent = last.name; badge.classList.remove("bg-white/10"); badge.classList.add("bg-blue-600"); }
  document.dispatchEvent(new CustomEvent("ahoy:toast", { detail: `Added to "${last.name}"` }));
});