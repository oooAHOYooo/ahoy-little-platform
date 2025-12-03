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
        autoFocusFirst();
        // enable simple keyboard navigation
        wireGlobalKeys();
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

  function cleanTitle(title) {
    if (!title) return 'Untitled';
    // Strip brackets and their contents: [Brackets], (Parentheses), etc.
    return title.replace(/\[[^\]]*\]/g, '').replace(/\([^)]*\)/g, '').trim() || 'Untitled';
  }

  function getChannelLabel(key, channelName) {
    const rowDef = state.rowOrder.find(r => r.key === key);
    return rowDef?.label || `Channel — ${channelName || 'Unknown'}`;
  }


  function renderRows() {
    const selectorContainer = byId('channel-selector');
    if (!selectorContainer) return;

    selectorContainer.innerHTML = '';

    state.rowOrder.forEach((rowDef, rowIdx) => {
      const ch = findChannelForKey(rowDef.key, rowDef.titles) || state.channels[rowIdx] || null;
      if (!ch) return;

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

      // Next up (optional - show first item title if available)
      if (ch.items && ch.items.length > 0) {
        const firstItem = ch.items[0];
        const next = document.createElement('div');
        next.className = 'channel-button-next';
        next.textContent = `Next: ${cleanTitle(firstItem.title)}`;
        button.appendChild(next);
      }

      // Click handler
      button.addEventListener('click', () => {
        // Remove active class from all buttons
        qsa('.channel-button').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Load first item from this channel
        if (ch.items && ch.items.length > 0) {
          const firstItem = ch.items[0];
          const src = firstItem.video_url || firstItem.mp4_link || firstItem.trailer_url;
          if (src && state.videoEl) {
            try { state.videoEl.pause(); } catch (_) {}
            state.videoEl.src = src;
            try { state.videoEl.load(); } catch (_) {}
            state.videoEl.muted = false;
            const p = state.videoEl.play();
            if (p && typeof p.catch === 'function') p.catch(() => {});
            
            // Update preview
            if (state.nowThumb) state.nowThumb.src = firstItem.thumbnail || '/static/img/default-cover.jpg';
            if (state.nowTitle) state.nowTitle.textContent = cleanTitle(firstItem.title);
            if (state.nextTitle && ch.items.length > 1) {
              state.nextTitle.textContent = cleanTitle(ch.items[1].title);
            }
          }
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


