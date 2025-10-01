// Collections API client with paywall support
const fx = (typeof window !== "undefined" && window.fetchWithPaywall) || fetch;

const CollectionsAPI = {
  async create(payload) {
    const r = await fx(`/api/collections/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return r.json();
  },
  
  async list() {
    const r = await fx(`/api/collections/`);
    return r.json();
  },
  
  async addItem(collectionId, item) {
    const r = await fx(`/api/collections/${collectionId}/items`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(item),
    });
    return r.json();
  }
};

// Make it available globally
window.CollectionsAPI = CollectionsAPI;
