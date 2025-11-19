// AHOY TOAST SYSTEM - ephemeral, dark glass, slide-up
export function showToast(message, durationMs = 3000) {
  const toast = document.createElement("div");
  toast.className = "ahoy-toast";
  toast.textContent = message || "Done";
  document.body.appendChild(toast);
  // slide-in
  requestAnimationFrame(() => toast.classList.add("visible"));
  // auto-dismiss
  setTimeout(() => {
    toast.classList.remove("visible");
    setTimeout(() => toast.remove(), 320);
  }, Math.max(1200, durationMs));
}

// Global listener for fire-and-forget usage
document.addEventListener("ahoy:toast", (e) => showToast(e.detail || "Done"));
