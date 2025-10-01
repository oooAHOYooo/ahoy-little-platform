// "You bookmarked!" overlay + first-visit counts.
// Fire these events from your bookmark toggle code:
// document.dispatchEvent(new CustomEvent("bookmark:added", { detail: { type: "track" }}));

function showOverlay(msg) {
  const el = document.getElementById("celebrate");
  if (!el) return;
  el.querySelector("[data-celebrate-text]").textContent = msg;
  el.classList.remove("hidden","opacity-0");
  el.classList.add("opacity-100");
  clearTimeout(el._t);
  el._t = setTimeout(() => {
    el.classList.remove("opacity-100");
    el.classList.add("opacity-0");
    setTimeout(()=>el.classList.add("hidden"), 250);
  }, 1400);
}

function countCards() {
  return document.querySelectorAll("[data-card]").length;
}

document.addEventListener("bookmark:added", (e) => {
  const total = countCards();
  showOverlay(`You bookmarked! ${total} saved so far ✨`);
  document.dispatchEvent(new CustomEvent("ahoy:toast", { detail: "Saved to Bookmarks" }));
});

// Optional: first-visit gentle nudge if everything is unorganized
window.addEventListener("load", () => {
  const badges = [...document.querySelectorAll("[data-collection-badge]")];
  if (badges.length && badges.every(b => /unorganized/i.test(b.textContent.trim()))) {
    document.dispatchEvent(new CustomEvent("ahoy:toast", { detail: "Tip: Click 📁 on a card to organize into a Collection." }));
  }
});
