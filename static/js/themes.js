async function getThemes() {
  const r = await fetch("/api/products");
  try { return (await r.json()).themes || []; } catch { return []; }
}

export async function openThemePicker() {
  const themes = await getThemes();
  const pick = window.prompt("Pick a Theme:\n" + themes.map((t,i)=>`${i+1}. ${t.name} — $${t.price_usd}`).join("\n"));
  if (!pick) return;
  // Tonight: just show toast. Later: open Checkout and on success save to users/themes.
  document.dispatchEvent(new CustomEvent("ahoy:toast", { detail: "Theme added! (stub)" }));
}
