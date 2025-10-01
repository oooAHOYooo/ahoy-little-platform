// Minimal queue stubs so "Make Playlist", "Queue Next", "Queue All" do something tonight.
// Replace these with your real player hookups later.

const Queue = {
  items: [],
  replace(newItems) { this.items = [...newItems]; console.log("[queue] replace", this.items); },
  append(newItems)  { this.items = [...this.items, ...newItems]; console.log("[queue] append", this.items); },
  playNext(newItems){ this.items = [...newItems, ...this.items]; console.log("[queue] playNext", this.items); }
};

// Listen for playlist creation and auto-queue if asked
document.addEventListener("playlist:created", (e) => {
  const pl = e.detail;
  if (!pl || !Array.isArray(pl.items)) return;
  if (pl._queueMode === "replace") Queue.replace(pl.items);
  if (pl._queueMode === "append")  Queue.append(pl.items);
  if (pl._queueMode === "next")    Queue.playNext(pl.items);
});
