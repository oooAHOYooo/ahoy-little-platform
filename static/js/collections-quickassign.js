// tiny helper: prefer paywall-aware fetch if present
const fx = (typeof window !== "undefined" && window.fetchWithPaywall) || fetch;

// Minimal API (matches the collections API you added earlier)
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

// Local preference: last used collection id per user
const Last = {
  get(owner) { try { return JSON.parse(localStorage.getItem(`ahoy:lastCol:${owner}`)); } catch { return null; } },
  set(owner, col) { localStorage.setItem(`ahoy:lastCol:${owner}`, JSON.stringify({ id: col.id, name: col.name })); }
};

// Show/hide quick-move buttons based on last collection
function updateQuickMoveButtons() {
  document.querySelectorAll('[data-quick-assign][data-quick-last]').forEach(btn => {
    const owner = btn.getAttribute("data-owner");
    const last = Last.get(owner);
    btn.style.display = last ? 'grid' : 'none';
    if (last) {
      btn.title = `Quick move to "${last.name}"`;
    }
  });
}

// Build & show the popover near a button
async function openQuickAssign(btn) {
  const owner = btn.getAttribute("data-owner");
  const itemId = btn.getAttribute("data-id");
  const itemType = btn.getAttribute("data-type"); // 'track' | 'show' | 'episode'
  if (!owner || !itemId || !itemType) return;

  const cols = await CollectionsAPI.list(owner);
  const last = Last.get(owner);
  const pop = document.createElement("div");
  pop.className = "qa-pop fixed z-[60] w-[280px] rounded-xl shadow-xl border border-white/10 bg-[#111] text-white p-2";
  pop.innerHTML = `
    <div class="px-2 py-1 text-xs text-white/70">Move to Collection</div>
    <div class="max-h-52 overflow-auto mt-1 space-y-1" data-col-list></div>
    <div class="mt-2 p-2 rounded-lg bg-white/5">
      <input class="w-full bg-transparent outline-none text-sm" placeholder="New collection name…" data-new-name>
      <button class="mt-2 w-full text-sm rounded-lg bg-white text-black py-1.5" data-create>+ Create & Assign</button>
    </div>
  `;

  // add rows
  const list = pop.querySelector("[data-col-list]");
  const row = (c, highlight=false) => {
    const el = document.createElement("button");
    el.className = `w-full text-left px-2 py-1.5 rounded-lg hover:bg-white/10 ${highlight ? "ring-1 ring-white/40" : ""}`;
    el.textContent = c.name;
    el.dataset.colId = c.id;
    return el;
  };
  if (last && cols.find(c => c.id === last.id)) list.appendChild(row(last, true));
  cols.filter(c => !last || c.id !== last.id).forEach(c => list.appendChild(row(c)));

  // position near button
  document.body.appendChild(pop);
  const rect = btn.getBoundingClientRect();
  const top = window.scrollY + rect.top - pop.offsetHeight - 8;
  const left = Math.max(12, Math.min(window.scrollX + rect.left, window.scrollX + window.innerWidth - 300));
  pop.style.top = `${Math.max(12, top)}px`;
  pop.style.left = `${left}px`;

  // handlers
  const close = () => { pop.remove(); document.removeEventListener("click", onDoc); };
  const assign = async (col) => {
    await CollectionsAPI.addItem(col.id, { id: itemId, type: itemType });
    Last.set(owner, col);
    // update badge on card
    const card = btn.closest("[data-card]");
    if (card) {
      const badge = card.querySelector("[data-collection-badge]");
      if (badge) {
        badge.textContent = col.name;
        badge.classList.remove("bg-white/10");
        badge.classList.add("bg-blue-600");
      }
    }
    document.dispatchEvent(new CustomEvent("ahoy:toast", { detail: `Added to "${col.name}"` }));
    updateQuickMoveButtons(); // Update quick-move buttons
    close();
  };

  list.addEventListener("click", async (e) => {
    const b = e.target.closest("button[data-col-id]");
    if (!b) return;
    const col = cols.find(c => c.id === b.dataset.colId) || (last && last.id === b.dataset.colId ? last : null);
    if (col) assign(col);
  });

  pop.querySelector("[data-create]").addEventListener("click", async () => {
    const name = pop.querySelector("[data-new-name]").value.trim();
    if (!name) return;
    const created = await CollectionsAPI.create({ name, owner });
    assign(created);
  });

  const onDoc = (e) => { if (!pop.contains(e.target) && e.target !== btn) close(); };
  setTimeout(() => document.addEventListener("click", onDoc), 0);
}

// Delegate clicks from any "organize" hover button
document.addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-quick-assign]");
  if (!btn) return;
  e.preventDefault();
  
  const owner = btn.getAttribute("data-owner");
  const last = Last.get(owner);
  
  if (btn.hasAttribute("data-quick-last") && last) {
    // direct assign to last without popover
    await CollectionsAPI.addItem(last.id, { id: btn.getAttribute("data-id"), type: btn.getAttribute("data-type") });
    document.dispatchEvent(new CustomEvent("ahoy:toast", { detail: `Added to "${last.name}"` }));
    const badge = btn.closest("[data-card]")?.querySelector("[data-collection-badge]");
    if (badge) { 
      badge.textContent = last.name; 
      badge.classList.remove("bg-white/10"); 
      badge.classList.add("bg-blue-600"); 
    }
    updateQuickMoveButtons(); // Update quick-move buttons
    return;
  }
  
  openQuickAssign(btn);
});

// Initialize quick-move buttons on page load
document.addEventListener('DOMContentLoaded', updateQuickMoveButtons);
