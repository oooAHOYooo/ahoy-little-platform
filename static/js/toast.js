export function showToast(msg, ms = 2200) {
  const el = document.getElementById("app-toast");
  if (!el) return;
  el.textContent = msg;
  el.classList.remove("hidden");
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.add("hidden"), ms);
}

document.addEventListener("ahoy:toast", (e) => showToast(e.detail || "Done"));
