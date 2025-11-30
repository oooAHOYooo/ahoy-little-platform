document.addEventListener('keydown', e => {
  const items = [...document.querySelectorAll('.panelstream-item')];
  let current = document.activeElement;
  let index = items.indexOf(current);

  if (index === -1) index = 0;

  if (e.key === "ArrowRight") index++;
  if (e.key === "ArrowLeft") index--;

  index = Math.max(0, Math.min(items.length - 1, index));

  if (items[index]) {
    items[index].focus?.();
    items[index].scrollIntoView({ behavior: "smooth", inline: "center" });
  }
});


