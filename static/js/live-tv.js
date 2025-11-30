// Live TV Guide: video-only channels, no autoplay, TV-guide schedule with keyboard navigation
(function () {
  const state = {
    channels: [],
    channelIndex: 0, // focused row
    focus: { row: 0, col: 0 }, // focused program cell
    isLoading: true,
    channelListEl: null,
    guideRowsEl: null,
    timebarEl: null,
    nowLineEl: null,
    btnWatchEl: null,
    btnLaterEl: null,
    videoEl: null,
    nowTitleEl: null,
    nowMetaEl: null,
    pxPerMinute: 6,  // width scale for program duration
    horizonMinutes: 180 // show 3 hours ahead
  };

  function qs(id) { return document.getElementById(id); }

  function init() {
    state.channelListEl = qs('channelList');
    state.guideRowsEl = qs('guideRows');
    state.timebarEl = qs('timebar');
    state.nowLineEl = qs('nowLine');
    state.btnWatchEl = qs('btnWatch');
    state.btnLaterEl = qs('btnLater');
    state.videoEl = qs('tvPlayer');
    state.nowTitleEl = qs('nowTitle');
    state.nowMetaEl = qs('nowMeta');

    // Keyboard controls for navigating guide
    document.addEventListener('keydown', onKey);

    // Action buttons
    if (state.btnWatchEl) state.btnWatchEl.addEventListener('click', openFocusedProgram);
    if (state.btnLaterEl) state.btnLaterEl.addEventListener('click', bookmarkFocusedProgram);

    // Bootstrap
    fetch('/api/live-tv/channels')
      .then(r => r.json())
      .then(data => {
        state.channels = (data && data.channels) || [];
        state.channels.forEach(c => { if (!Array.isArray(c.items)) c.items = []; });

        // Focus initial channel if provided
        const root = document.getElementById('liveTvRoot');
        const initialId = root?.dataset?.initialChannel || state.channels[0]?.id;
        const initialIndex = Math.max(0, state.channels.findIndex(c => c.id === initialId));
        state.channelIndex = initialIndex;
        state.focus = { row: initialIndex, col: 0 };
        renderChannels();
        renderTimebar();
        renderGuideRows();
        renderNowLine();
        focusCurrent();
        // Update now line every minute
        setInterval(renderNowLine, 60000);
      })
      .catch(err => {
        console.error('Live TV load failed', err);
      })
      .finally(() => { state.isLoading = false; });
  }

  function onKey(e) {
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      moveFocus(-1, 0);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      moveFocus(1, 0);
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      moveFocus(0, 1);
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      moveFocus(0, -1);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      openFocusedProgram();
    }
  }

  function moveFocus(dRow, dCol) {
    const rows = state.channels.length;
    const newRow = Math.min(Math.max(state.focus.row + dRow, 0), rows - 1);
    state.focus.row = newRow;
    state.channelIndex = newRow;
    const ch = state.channels[newRow];
    const cols = (ch && ch.items ? ch.items.length : 0);
    const newCol = Math.min(Math.max(state.focus.col + dCol, 0), Math.max(cols - 1, 0));
    state.focus.col = newCol;
    renderChannels();
    focusCurrent();
  }

  function openFocusedProgram() {
    const ch = state.channels[state.focus.row];
    if (!ch) return;
    const item = ch.items?.[state.focus.col];
    if (!item) return;
    const source = item.video_url || item.mp4_link || item.trailer_url;
    if (!source || !state.videoEl) return;
    try { state.videoEl.pause(); } catch (_) {}
    state.videoEl.src = source;
    try { state.videoEl.load(); } catch (_) {}
    const p = state.videoEl.play();
    if (p && typeof p.catch === 'function') p.catch(() => {});
    updateOverlay(item);
  }

  async function bookmarkFocusedProgram() {
    const ch = state.channels[state.focus.row];
    if (!ch) return;
    const item = ch.items?.[state.focus.col];
    if (!item || !item.id) return;
    try {
      const res = await fetch('/api/bookmarks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ media_id: item.id, media_type: 'show' })
      });
      if (!res.ok) throw new Error('bookmark failed');
      // optional toast
      window.__ahoyToast && window.__ahoyToast('Saved to Watch Later');
    } catch (_) {
      // Fallback: localStorage queue
      try {
        const key = 'ahoy_watch_later';
        const curr = JSON.parse(localStorage.getItem(key) || '[]');
        if (!curr.find(x => x.id === item.id)) curr.push({ id: item.id, type: 'show', t: Date.now() });
        localStorage.setItem(key, JSON.stringify(curr));
        window.__ahoyToast && window.__ahoyToast('Saved locally');
      } catch (e) {}
    }
  }

  function renderChannels() {
    const ul = state.channelListEl;
    if (!ul) return;
    ul.innerHTML = '';
    state.channels.forEach((ch, idx) => {
      const li = document.createElement('li');
      li.className = 'channel-item';
      li.setAttribute('role', 'option');
      li.setAttribute('aria-selected', String(idx === state.channelIndex));
      li.tabIndex = 0;

      const pill = document.createElement('span');
      pill.className = 'channel-pill';
      pill.style.background = ['#7c66ff','#ff6b6b','#22c55e','#f59e0b'][idx % 4];

      const name = document.createElement('span');
      name.className = 'channel-name';
      name.textContent = ch.name;

      li.appendChild(pill);
      li.appendChild(name);
      li.addEventListener('click', () => {
        state.channelIndex = idx;
        state.focus = { row: idx, col: 0 };
        renderChannels();
        focusCurrent();
      });
      li.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          state.channelIndex = idx;
          state.focus = { row: idx, col: 0 };
          renderChannels();
          focusCurrent();
        }
      });
      ul.appendChild(li);
    });
  }

  function minutes(n) { return Math.max(5, Math.round(n)); }

  function renderTimebar() {
    const el = state.timebarEl;
    if (!el) return;
    el.innerHTML = '';
    const now = new Date();
    const markers = [];
    for (let m = 0; m <= state.horizonMinutes; m += 30) {
      const t = new Date(now.getTime() + m * 60000);
      const label = t.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
      const span = document.createElement('div');
      span.className = 'time-marker';
      span.style.minWidth = `${30 * state.pxPerMinute}px`;
      span.textContent = label;
      markers.push(span);
    }
    markers.forEach(n => el.appendChild(n));
  }

  function renderGuideRows() {
    const container = state.guideRowsEl;
    if (!container) return;
    container.innerHTML = '';
    const now = new Date();

    state.channels.forEach((ch, rowIdx) => {
      const row = document.createElement('div');
      row.className = 'guide-row';
      row.setAttribute('role', 'row');

      const label = document.createElement('div');
      label.className = 'guide-channel-label';
      const icon = document.createElement('span');
      icon.className = 'guide-channel-icon';
      icon.style.background = ['#7c66ff','#ff6b6b','#22c55e','#f59e0b'][rowIdx % 4];
      const name = document.createElement('span');
      name.textContent = ch.name;
      label.appendChild(icon); label.appendChild(name);
      row.appendChild(label);

      const track = document.createElement('div');
      track.className = 'guide-track';

      // Build schedule across horizon by repeating channel items
      let cursor = new Date(now);
      let col = 0;
      while (diffMinutes(now, cursor) < state.horizonMinutes) {
        const item = ch.items[col % (ch.items.length || 1)];
        const durMin = minutes((item?.duration_seconds || 300) / 60);

        const cell = document.createElement('div');
        cell.className = 'program';
        cell.style.width = `${durMin * state.pxPerMinute}px`;
        cell.setAttribute('tabindex', '0');
        cell.setAttribute('role', 'gridcell');
        cell.setAttribute('data-row', String(rowIdx));
        cell.setAttribute('data-col', String(col));
        cell.setAttribute('aria-label', `${item?.title || 'Program'} • ${durMin} min`);
        cell.addEventListener('click', () => {
          state.focus = { row: rowIdx, col };
          openFocusedProgram();
        });
        cell.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            state.focus = { row: rowIdx, col };
            openFocusedProgram();
          }
        });

        const img = document.createElement('img');
        img.className = 'program-thumb';
        img.alt = item?.title || '';
        img.src = item?.thumbnail || '/static/img/default-cover.jpg';

        const title = document.createElement('div');
        title.className = 'program-title';
        title.textContent = item?.title || 'Untitled';

        const meta = document.createElement('div');
        meta.className = 'program-meta';
        const timeLabel = `${fmtTime(cursor)} – ${fmtTime(new Date(cursor.getTime() + durMin * 60000))}`;
        meta.textContent = `${timeLabel} • ${item?.category || 'Show'}`;

        cell.appendChild(img);
        cell.appendChild(title);
        cell.appendChild(meta);
        track.appendChild(cell);

        // advance
        cursor = new Date(cursor.getTime() + durMin * 60000);
        col += 1;
      }
      row.appendChild(track);
      container.appendChild(row);
    });
  }

  function diffMinutes(a, b) {
    return Math.round((b.getTime() - a.getTime()) / 60000);
  }

  function fmtTime(d) {
    return d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  }

  function focusCurrent() {
    // Clear selection classes
    document.querySelectorAll('.program.selected').forEach(n => n.classList.remove('selected'));
    // Try to focus the selected gridcell
    const sel = document.querySelector(`.program[data-row="${state.focus.row}"][data-col="${state.focus.col}"]`);
    if (sel) {
      sel.classList.add('selected');
      sel.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      try { sel.focus(); } catch (_) {}
      const item = resolveFocusedItem();
      updateOverlay(item);
    }
  }

  function resolveFocusedItem() {
    const ch = state.channels[state.focus.row];
    if (!ch) return null;
    return ch.items?.[state.focus.col] || null;
  }

  function updateOverlay(item) {
    if (!item) return;
    const mins = Math.round(Math.max(60, item.duration_seconds || 0) / 60);
    if (state.nowTitleEl) state.nowTitleEl.textContent = item.title || 'Untitled';
    if (state.nowMetaEl) {
      state.nowMetaEl.textContent = `${item.category || 'Show'} • ${mins} min`;
    }
  }

  function renderNowLine() {
    const line = state.nowLineEl;
    const rows = state.guideRowsEl;
    if (!line || !rows) return;
    // The schedule starts at "now", so the now line sits near the left with slight offset
    const offsetMinutes = 0; // could add timezone offset if needed
    const leftPx = Math.max(0, offsetMinutes * state.pxPerMinute) + 140 /* channel label width */ + 10 /* padding */;
    line.style.left = `${leftPx}px`;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();


