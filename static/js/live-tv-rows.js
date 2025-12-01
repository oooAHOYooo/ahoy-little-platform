(function () {
  const qs = (sel, el = document) => el.querySelector(sel);
  const qsa = (sel, el = document) => Array.from(el.querySelectorAll(sel));
  const byId = (id) => document.getElementById(id);

  const state = {
    channels: [],
    rowOrder: [
      { key: 'misc', titles: ['misc', 'clips', 'clip'] },
      { key: 'short_films', titles: ['short films', 'short film', 'films', 'film', 'movies', 'movie'] },
      { key: 'music_videos', titles: ['music videos', 'music_video', 'music'] },
      { key: 'films', titles: ['films', 'movies', 'film', 'movie'] }, // kept for fallback; not used as a rail key
      { key: 'live_shows', titles: ['live shows', 'broadcast', 'shows', 'live'] },
    ],
    focus: { row: 0, col: 0 },
    videoEl: null,
    nowThumb: null,
    nowTitle: null,
    nextTitle: null,
  };

  function init() {
    state.videoEl = byId('livePlayer') || byId('tvPlayer');
    state.nowThumb = byId('playingNowThumb');
    state.nowTitle = byId('playingNowTitle');
    state.nextTitle = byId('upNextTitle');

    buildTimeStrip();
    fetch('/api/live-tv/channels')
      .then(r => r.json())
      .then(data => {
        state.channels = (data && data.channels) || [];
        state.channels.forEach(c => { if (!Array.isArray(c.items)) c.items = []; });
        renderRows();
        addRailArrows();
        autoFocusFirst();
        // enable simple keyboard navigation
        wireGlobalKeys();
        wireChannelButtons();
      })
      .catch(err => console.error('live-tv-rows load failed', err));
  }

  function buildTimeStrip() {
    const strip = byId('timeStrip');
    if (!strip) return;
    strip.innerHTML = '';
    const now = new Date();
    // next 3 hours at 30-min intervals
    for (let m = 0; m <= 180; m += 30) {
      const t = new Date(now.getTime() + m * 60000);
      const tick = document.createElement('div');
      tick.className = 'tick';
      tick.textContent = t.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
      strip.appendChild(tick);
    }
  }

  function findChannelForKey(key, titles) {
    const matches = (s) => typeof s === 'string' ? s.toLowerCase() : '';
    return state.channels.find(ch => {
      const id = matches(ch.id);
      const name = matches(ch.name);
      return titles.some(t => id.includes(t) || name.includes(t));
    });
  }

  function makeCard(item, rowIdx, colIdx) {
    const el = document.createElement('button');
    el.className = 'tv-card compact panelstream-item';
    el.type = 'button';
    el.setAttribute('role', 'listitem');
    el.setAttribute('tabindex', '0');
    el.dataset.row = String(rowIdx);
    el.dataset.col = String(colIdx);
    el.dataset.src = item.video_url || item.mp4_link || item.trailer_url || '';
    el.dataset.thumb = item.thumbnail || '/static/img/default-cover.jpg';
    el.dataset.title = item.title || 'Untitled';

    const meta = document.createElement('div');
    meta.className = 'meta';
    const title = document.createElement('div');
    title.className = 'title';
    title.textContent = item.title || 'Untitled';
    const time = document.createElement('div');
    time.className = 'time';
    const mins = Math.round(Math.max(60, item.duration_seconds || 0) / 60);
    time.textContent = `${mins} min`;
    meta.appendChild(title);
    meta.appendChild(time);

    el.appendChild(meta);

    // Width reflects duration while keeping universal height (CSS).
    // Clamp to reasonable bounds for usability.
    const widthPx = Math.max(220, Math.min(520, Math.round(160 + mins * 6)));
    el.style.width = widthPx + 'px';

    // Preview on hover/focus
    const preview = () => updatePreview(el);
    el.addEventListener('mouseenter', preview);
    el.addEventListener('focus', preview);
    el.addEventListener('touchstart', preview, { passive: true });
    // No on-demand click-to-play in linear TV mode

    return el;
  }

  function renderRows() {
    state.rowOrder.forEach((rowDef, rowIdx) => {
      const container = byId(`row-${rowDef.key.replace('_', '-')}`);
      if (!container) return;
      container.innerHTML = '';
      const ch = findChannelForKey(rowDef.key, rowDef.titles) || state.channels[rowIdx] || null;
      if (!ch) return;
      ch.items.forEach((item, colIdx) => {
        const card = makeCard(item, rowIdx, colIdx);
        container.appendChild(card);
      });
      // highlight active rail on pointer hover
      container.addEventListener('mouseenter', () => setActiveRail(rowIdx));
      container.addEventListener('mouseleave', () => {
        container.classList.remove('rail-active');
      });
    });
  }

  function wireChannelButtons() {
    const btns = qsa('.channel-btn');
    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-target');
        if (target) {
          const el = document.querySelector(target);
          if (el && typeof el.scrollIntoView === 'function') {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }
        btns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  }

  function addRailArrows() {
    const rows = qsa('.guide-row');
    rows.forEach((row) => {
      const scroller = qs('.channel-cards', row);
      if (!scroller || row.querySelector('.nav-arrow')) return;
      const makeBtn = (side) => {
        const b = document.createElement('button');
        b.className = `nav-arrow nav-arrow-${side}`;
        b.type = 'button';
        b.setAttribute('aria-label', side === 'left' ? 'Scroll left' : 'Scroll right');
        b.textContent = side === 'left' ? '‹' : '›';
        b.addEventListener('click', () => {
          const delta = (side === 'left' ? -1 : 1) * Math.round(scroller.clientWidth * 0.8);
          scroller.scrollBy({ left: delta, behavior: 'smooth' });
        });
        return b;
      };
      row.appendChild(makeBtn('left'));
      row.appendChild(makeBtn('right'));
    });
  }

  function updatePreview(cardEl) {
    const thumb = cardEl?.dataset?.thumb;
    const title = cardEl?.dataset?.title || 'Untitled';
    if (state.videoEl) {
      state.videoEl.poster = thumb || '';
      // do not autoplay audio; keep muted and don't call play()
    }
    if (state.nowThumb) state.nowThumb.src = thumb || '';
    if (state.nowTitle) state.nowTitle.textContent = title;
    // Up next: next sibling in same row
    const row = Number(cardEl.dataset.row || 0);
    const col = Number(cardEl.dataset.col || 0);
    const next = qsa(`.tv-card[data-row="${row}"]`)[col + 1];
    if (state.nextTitle) state.nextTitle.textContent = next?.dataset?.title || '—';
    state.focus = { row, col };
  }

  function playCard(cardEl) {
    const src = cardEl?.dataset?.src;
    if (!src || !state.videoEl) return;
    try { state.videoEl.pause(); } catch (_) {}
    state.videoEl.src = src;
    try { state.videoEl.load(); } catch (_) {}
    state.videoEl.muted = false;
    const p = state.videoEl.play();
    if (p && typeof p.catch === 'function') p.catch(() => {});
    updatePreview(cardEl);
  }

  function autoFocusFirst() {
    const first = qs('.tv-card');
    if (first) {
      try { first.focus(); } catch (_) {}
      updatePreview(first);
    }
  }

  function wireGlobalKeys() {
    document.addEventListener('keydown', (e) => {
      const rows = state.rowOrder.length;
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        state.focus.row = Math.max(0, state.focus.row - 1);
        focusCurrent();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        state.focus.row = Math.min(rows - 1, state.focus.row + 1);
        focusCurrent();
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        state.focus.col = Math.max(0, state.focus.col - 1);
        focusCurrent();
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        state.focus.col = state.focus.col + 1;
        focusCurrent();
      } else if (e.key === 'Enter') {
        // In linear TV mode, do not trigger on-demand playback.
        e.preventDefault();
      }
    });
  }

  function getCurrentCard() {
    const rowContainer = byId(`row-${state.rowOrder[state.focus.row].key.replace('_', '-')}`);
    if (!rowContainer) return null;
    const cards = qsa('.tv-card', rowContainer);
    const col = Math.max(0, Math.min(cards.length - 1, state.focus.col));
    state.focus.col = col;
    return cards[col] || null;
  }

  function focusCurrent() {
    const el = getCurrentCard();
    if (el) {
      try { el.focus(); } catch (_) {}
      el.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
      updatePreview(el);
      // Highlight active rail
      const rowIdx = Number(el.dataset.row || 0);
      setActiveRail(rowIdx);
    }
  }

  function setActiveRail(rowIdx) {
    state.rowOrder.forEach((rowDef, idx) => {
      const container = byId(`row-${rowDef.key.replace('_', '-')}`);
      if (!container) return;
      if (idx === rowIdx) {
        container.classList.add('rail-active');
      } else {
        container.classList.remove('rail-active');
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // After initial render, mount rail arrows and keyboard navigation
  document.addEventListener('DOMContentLoaded', () => {
    addRailArrows();
    wireGlobalKeys();
  });
})();


