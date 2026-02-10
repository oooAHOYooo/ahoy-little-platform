(function () {
  const qs = (sel, el = document) => el.querySelector(sel);
  const qsa = (sel, el = document) => Array.from(el.querySelectorAll(sel));
  const byId = (id) => document.getElementById(id);

  const state = {
    channels: [],
    rowOrder: [
      { key: 'misc', titles: ['misc', 'clips', 'clip'], label: 'Channel 01 — Misc' },
      { key: 'films', titles: ['films', 'film', 'movies', 'movie', 'short films', 'short film'], label: 'Channel 02 — Short Films' },
      { key: 'music-videos', titles: ['music videos', 'music_video', 'music'], label: 'Channel 03 — Music Videos' },
      { key: 'live-shows', titles: ['live shows', 'broadcast', 'shows', 'live'], label: 'Channel 04 — Live Shows' },
    ],
    focus: { row: 0, col: 0 },
    videoEl: null,
    nowThumb: null,
    nowTitle: null,
    nextTitle: null,
    hoverPreviewTimer: null,
    hoverPreviewEl: null,
  };

  function getCurrentSlotForRow(schedule, row) {
    if (!Array.isArray(schedule)) return null;
    const now = Date.now();
    for (const s of schedule) {
      if (!s) continue;
      if (s.row !== row) continue;
      if (now >= (s.startUTC || 0) && now < (s.endUTC || 0)) return s;
    }
    return null;
  }

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
        autoFocusFirst();
        // enable simple keyboard navigation
        wireGlobalKeys();
      })
      .catch(err => console.error('live-tv-rows load failed', err));

    // If the schedule engine loads after us, refresh labels so we show "Now playing".
    document.addEventListener('ltv:schedule:ready', () => {
      try { renderRows(); } catch (_) {}
    });
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

  function cleanTitle(title) {
    if (!title) return 'Untitled';
    // Strip brackets and their contents: [Brackets], (Parentheses), etc.
    return title.replace(/\[[^\]]*\]/g, '').replace(/\([^)]*\)/g, '').trim() || 'Untitled';
  }

  function getChannelLabel(key, channelName) {
    const rowDef = state.rowOrder.find(r => r.key === key);
    return rowDef?.label || `Channel — ${channelName || 'Unknown'}`;
  }

  function ensurePreviewEl() {
    if (state.hoverPreviewEl) return state.hoverPreviewEl;
    const el = document.createElement('div');
    el.className = 'live-tv-channel-preview';
    el.setAttribute('aria-hidden', 'true');
    el.innerHTML = '<img src="" alt=""><div class="live-tv-channel-preview-title"></div><div class="live-tv-channel-preview-meta"></div>';
    document.body.appendChild(el);
    state.hoverPreviewEl = el;
    return el;
  }

  function getPreviewDataForRow(rowIdx) {
    const ch = state.channels[rowIdx];
    if (!ch) return null;
    const schedule = window.CHANNEL_SCHEDULE;
    const slot = getCurrentSlotForRow(schedule, rowIdx);
    const thumb = slot?.thumb || ch.items?.[0]?.thumbnail || '/static/img/default-cover.jpg';
    const title = slot?.title || ch.items?.[0]?.title || '—';
    const meta = slot?.category || ch.items?.[0]?.category || ch.name || '';
    return { thumb, title: cleanTitle(title), meta };
  }

  function showPreview(button, rowIdx) {
    const data = getPreviewDataForRow(rowIdx);
    if (!data) return;
    const el = ensurePreviewEl();
    const img = el.querySelector('img');
    const titleEl = el.querySelector('.live-tv-channel-preview-title');
    const metaEl = el.querySelector('.live-tv-channel-preview-meta');
    if (img) {
      img.dataset.thumbGenerated = ''; // reset flag for new src
      img.onerror = function () { if (window.ahoyThumbGen) ahoyThumbGen(img, data.title, data.meta); };
      img.src = data.thumb;
    }
    if (titleEl) titleEl.textContent = data.title;
    if (metaEl) metaEl.textContent = data.meta;
    const rect = button.getBoundingClientRect();
    const previewWidth = 280;
    const padding = 12;
    let left = rect.left + (rect.width / 2) - (previewWidth / 2);
    let top = rect.top - padding;
    if (left < padding) left = padding;
    if (left + previewWidth > window.innerWidth - padding) left = window.innerWidth - previewWidth - padding;
    if (top < padding) top = rect.bottom + padding;
    el.style.left = left + 'px';
    el.style.top = top + 'px';
    el.classList.add('visible');
    el.setAttribute('aria-hidden', 'false');
  }

  function hidePreview() {
    if (state.hoverPreviewTimer) {
      clearTimeout(state.hoverPreviewTimer);
      state.hoverPreviewTimer = null;
    }
    if (state.hoverPreviewEl) {
      state.hoverPreviewEl.classList.remove('visible');
      state.hoverPreviewEl.setAttribute('aria-hidden', 'true');
    }
  }

  function renderRows() {
    const selectorContainer = byId('channel-selector');
    if (!selectorContainer) return;

    selectorContainer.innerHTML = '';

    state.rowOrder.forEach((rowDef, rowIdx) => {
      const ch = findChannelForKey(rowDef.key, rowDef.titles) || state.channels[rowIdx] || null;
      if (!ch) return;

      const schedule = window.CHANNEL_SCHEDULE;
      const slot = getCurrentSlotForRow(schedule, rowIdx);

      // Create channel button
      const button = document.createElement('button');
      button.className = 'channel-button';
      button.type = 'button';
      button.dataset.channel = rowDef.key;
      button.dataset.channelIndex = String(rowIdx);

      // Channel name
      const name = document.createElement('div');
      name.className = 'channel-button-name';
      name.textContent = getChannelLabel(rowDef.key, ch.name);
      button.appendChild(name);

      // Mobile-first: show what's playing now for this channel (no "Next" label).
      const nowLine = document.createElement('div');
      nowLine.className = 'channel-button-next';
      if (slot && slot.title) {
        nowLine.textContent = cleanTitle(slot.title);
      } else if (ch.items && ch.items.length > 0) {
        // Fallback: show the first item title if schedule isn't ready.
        nowLine.textContent = cleanTitle(ch.items[0].title);
      } else {
        nowLine.textContent = '—';
      }
      button.appendChild(nowLine);

      // Hover preview: show after 1 second
      button.addEventListener('mouseenter', () => {
        hidePreview();
        state.hoverPreviewTimer = setTimeout(() => {
          state.hoverPreviewTimer = null;
          showPreview(button, rowIdx);
        }, 1000);
      });
      button.addEventListener('mouseleave', () => {
        hidePreview();
      });

      // Click handler
      button.addEventListener('click', () => {
        // Remove active class from all buttons
        qsa('.channel-button').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Play what's on NOW for this channel if available (schedule-driven).
        const scheduleNow = getCurrentSlotForRow(window.CHANNEL_SCHEDULE, rowIdx);
        const playSrc =
          scheduleNow?.src ||
          ch.items?.[0]?.video_url ||
          ch.items?.[0]?.mp4_link ||
          ch.items?.[0]?.trailer_url;

        if (playSrc && state.videoEl) {
          try { state.videoEl.pause(); } catch (_) {}
          state.videoEl.src = playSrc;
          try { state.videoEl.load(); } catch (_) {}
          state.videoEl.muted = false;
          const p = state.videoEl.play();
          if (p && typeof p.catch === 'function') p.catch(() => {});

          // Update preview
          const thumb = scheduleNow?.thumb || ch.items?.[0]?.thumbnail || '/static/img/default-cover.jpg';
          const title = scheduleNow?.title || ch.items?.[0]?.title || '—';
          const category = scheduleNow?.category || ch.items?.[0]?.category || ch.name || '';
          if (state.nowThumb) {
            state.nowThumb.dataset.thumbGenerated = '';
            state.nowThumb.onerror = function () { if (window.ahoyThumbGen) ahoyThumbGen(state.nowThumb, cleanTitle(title), category); };
            state.nowThumb.src = thumb;
          }
          if (state.nowTitle) state.nowTitle.textContent = cleanTitle(title);

          // Update "Up next" line if the schedule engine can find it.
          try {
            if (state.nextTitle && Array.isArray(window.CHANNEL_SCHEDULE)) {
              const now = Date.now();
              const next = window.CHANNEL_SCHEDULE
                .filter(s => s && s.row === rowIdx && (s.startUTC || 0) > now)
                .sort((a, b) => (a.startUTC || 0) - (b.startUTC || 0))[0];
              state.nextTitle.textContent = next?.title ? cleanTitle(next.title) : '—';
            }
          } catch (_) {}
        }
      });

      selectorContainer.appendChild(button);
    });
  }

  function autoFocusFirst() {
    const first = qs('.channel-button');
    if (first) {
      try { first.focus(); } catch (_) {}
    }
  }

  function wireGlobalKeys() {
    document.addEventListener('keydown', (e) => {
      const buttons = qsa('.channel-button');
      if (buttons.length === 0) return;
      
      if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
        e.preventDefault();
        state.focus.row = Math.max(0, state.focus.row - 1);
        focusCurrent();
      } else if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
        e.preventDefault();
        state.focus.row = Math.min(buttons.length - 1, state.focus.row + 1);
        focusCurrent();
      } else if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        const button = buttons[state.focus.row];
        if (button) button.click();
      }
    });
  }

  function focusCurrent() {
    const buttons = qsa('.channel-button');
    if (state.focus.row >= buttons.length) return;
    const button = buttons[state.focus.row];
    if (button) {
      try { button.focus(); } catch (_) {}
      button.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // After initial render, mount keyboard navigation
  document.addEventListener('DOMContentLoaded', () => {
    wireGlobalKeys();
  });
})();


