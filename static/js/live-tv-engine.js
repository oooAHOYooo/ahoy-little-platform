(function () {
  // Live TV Engine: keeps hero player synced to UTC schedule parsed from DOM EPG
  // Provides:
  // - CHANNEL_SCHEDULE built from .program meta times for the next ~3h
  // - getCurrentSlot, getNextSlot, getSeekTimeForSlot
  // - Syncs #livePlayer with UTC (auto-seek), updates Now/Next, progress, EPG highlight
  // - Recovers on errors by re-seeking
  const byId = (id) => document.getElementById(id);
  const qsa = (sel, el = document) => Array.from(el.querySelectorAll(sel));
  const qs = (sel, el = document) => el.querySelector(sel);
  const log = (...args) => console.info('[LTV]', ...args);

  const engine = {
    channels: [],
    schedule: [],
    lastSrc: '',
    video: null,
    selectedRow: 0,
    els: {
      nowThumb: null,
      nowTitle: null,
      nextTitle: null,
      progressWrap: null,
      progress: null,
    },
    timer: null,
    ready: false,
  };

  function init() {
    engine.video = byId('livePlayer') || byId('tvPlayer');
    engine.els.nowThumb = byId('playingNowThumb');
    engine.els.nowTitle = byId('playingNowTitle');
    engine.els.nextTitle = byId('upNextTitle');
    engine.els.progressWrap = byId('ltv-progress-wrap');
    engine.els.progress = byId('ltv-progress');

    if (engine.video) {
      wireVideoRecovery(engine.video);
    }

    // Load channels to resolve video URLs for EPG items
    fetch('/api/live-tv/channels')
      .then(r => r.json())
      .then(data => {
        engine.channels = (data && data.channels) || [];
        engine.channels.forEach(c => { if (!Array.isArray(c.items)) c.items = []; });
        // Build canonical schedule from DOM EPG
        buildScheduleFromDOM();
        engine.ready = engine.schedule.length > 0;
        if (!engine.ready) {
          // EPG may not be rendered yet; retry shortly
          setTimeout(() => {
            buildScheduleFromDOM();
            engine.ready = engine.schedule.length > 0;
            if (engine.ready) startEngine();
          }, 600);
        } else {
          startEngine();
        }
      })
      .catch(err => log('channel load failed', err));
  }

  function wireVideoRecovery(video) {
    const resync = () => {
      const slot = getCurrentSlot(engine.schedule);
      if (!slot) return;
      const seek = getSeekTimeForSlot(slot);
      try {
        if (Math.abs((video.currentTime || 0) - seek) > 2) {
          video.currentTime = seek;
        }
      } catch (_) {}
    };
    video.addEventListener('error', resync);
    video.addEventListener('stalled', resync);
    video.addEventListener('waiting', resync);
    video.addEventListener('timeupdate', () => {
      // keep drift minimal
      const slot = getCurrentSlot(engine.schedule);
      if (!slot) return;
      const seek = getSeekTimeForSlot(slot);
      if (Math.abs((video.currentTime || 0) - seek) > 3) {
        resync();
      }
    });
    // Auto-advance to the next scheduled slot when a video ends
    video.addEventListener('ended', () => {
      const now = Date.now();
      const curr = getCurrentSlot(engine.schedule);
      const next = getNextSlot(engine.schedule);
      // Prefer the true next scheduled slot; if it's in the future, wait until its start to preserve "Always On"
      const startNext = () => {
        const playSlot = getCurrentSlot(engine.schedule) || next;
        if (!playSlot || !playSlot.src) return;
        engine.lastSrc = ''; // force reload in playCurrentSlot
        const seekSec = getSeekTimeForSlot(playSlot);
        try { video.pause(); } catch (_) {}
        video.src = playSlot.src;
        try { video.load(); } catch (_) {}
        try { video.currentTime = seekSec; } catch (_) {}
        video.muted = false;
        const p = video.play();
        if (p && typeof p.catch === 'function') p.catch(() => {});
      };
      if (next) {
        if (now < next.startUTC) {
          // Wait until the scheduled next slot start time
          setTimeout(startNext, Math.max(0, next.startUTC - now + 50));
        } else {
          startNext();
        }
      } else if (curr) {
        // If no next found (end of horizon), try to re-sync with current slot timeline
        startNext();
      }
    });
  }

  function parseTimeLabelToUTC(label) {
    // label e.g. "11:15 AM – 11:25 AM • Clips"
    if (!label) return null;
    const m = label.match(/(\d{1,2}:\d{2}\s?(AM|PM))\s*[–-]\s*(\d{1,2}:\d{2}\s?(AM|PM))/i);
    if (!m) return null;
    const startStr = m[1];
    const endStr = m[3];
    const now = new Date();
    const mk = (ts) => {
      // Build date with today's Y-M-D and provided time in local, then get UTC epoch
      const d = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const parts = ts.trim().toUpperCase();
      const mm = parts.match(/(\d{1,2}):(\d{2})\s?(AM|PM)/);
      if (!mm) return null;
      let hh = parseInt(mm[1], 10);
      const min = parseInt(mm[2], 10);
      const ap = mm[3];
      if (ap === 'PM' && hh !== 12) hh += 12;
      if (ap === 'AM' && hh === 12) hh = 0;
      d.setHours(hh, min, 0, 0);
      return d;
    };
    let start = mk(startStr);
    let end = mk(endStr);
    if (!start || !end) return null;
    // If end wraps to next day
    if (end < start) {
      end = new Date(end.getTime() + 24 * 3600 * 1000);
    }
    return { startUTC: start.getTime(), endUTC: end.getTime() };
  }

  function buildScheduleFromDOM() {
    const programs = qsa('.guide .program');
    const schedule = [];
    programs.forEach((el) => {
      const row = Number(el.getAttribute('data-row') || '0');
      const col = Number(el.getAttribute('data-col') || '0');
      const meta = qs('.program-meta', el);
      const titleEl = qs('.program-title', el);
      const title = titleEl ? titleEl.textContent.trim() : (el.getAttribute('aria-label') || 'Program');
      const times = parseTimeLabelToUTC(meta ? meta.textContent.trim() : '');
      if (!times) return;
      const ch = engine.channels[row];
      const item = ch && ch.items ? ch.items[col % Math.max(1, ch.items.length)] : null;
      const src = item?.video_url || item?.mp4_link || item?.trailer_url || '';
      const thumb = item?.thumbnail || '';
      const category = item?.category || ch?.name || 'Show';
      schedule.push({
        startUTC: times.startUTC,
        endUTC: times.endUTC,
        row,
        col,
        title,
        category,
        src,
        thumb,
        el, // link to EPG element
        durationSec: Math.max(1, Math.round((times.endUTC - times.startUTC) / 1000)),
      });
    });
    schedule.sort((a, b) => a.startUTC - b.startUTC);
    engine.schedule = schedule;
    log('schedule built', schedule.length, 'items');
    window.CHANNEL_SCHEDULE = schedule; // expose for debugging
  }

  function getCurrentSlot(schedule, rowFilter) {
    const now = Date.now();
    for (let i = 0; i < schedule.length; i++) {
      const s = schedule[i];
      if (rowFilter != null && s.row !== rowFilter) continue;
      if (now >= s.startUTC && now < s.endUTC) return s;
    }
    return null;
  }

  function getNextSlot(schedule, rowFilter) {
    const now = Date.now();
    let candidate = null;
    for (let i = 0; i < schedule.length; i++) {
      const s = schedule[i];
      if (rowFilter != null && s.row !== rowFilter) continue;
      if (s.startUTC > now) {
        if (!candidate || s.startUTC < candidate.startUTC) candidate = s;
      }
    }
    return candidate;
  }

  function getSeekTimeForSlot(slot) {
    const now = Date.now();
    const elapsedMs = Math.max(0, now - slot.startUTC);
    const t = Math.floor(elapsedMs / 1000);
    return Math.max(0, Math.min(t, slot.durationSec - 1));
  }

  function playCurrentSlot() {
    if (!engine.video || engine.schedule.length === 0) return;
    const slot = getCurrentSlot(engine.schedule, engine.selectedRow);
    if (!slot || !slot.src) return;
    const needSrc = slot.src !== engine.lastSrc;
    const seekSec = getSeekTimeForSlot(slot);
    if (needSrc) {
      engine.lastSrc = slot.src;
      try { engine.video.pause(); } catch (_) {}
      engine.video.src = slot.src;
      try { engine.video.load(); } catch (_) {}
      engine.video.currentTime = seekSec;
      engine.video.muted = false;
      const p = engine.video.play();
      if (p && typeof p.catch === 'function') p.catch(() => {});
      log('play slot', slot.title, 'seek', seekSec, 'sec');
    } else {
      // keep in sync
      if (Math.abs((engine.video.currentTime || 0) - seekSec) > 2) {
        try { engine.video.currentTime = seekSec; } catch (_) {}
      }
    }
  }

  function updateNowNext() {
    const slot = getCurrentSlot(engine.schedule, engine.selectedRow);
    const next = getNextSlot(engine.schedule, engine.selectedRow);
    if (slot) {
      if (engine.els.nowTitle) engine.els.nowTitle.textContent = slot.title || 'Now Playing';
      if (engine.els.nowThumb && slot.thumb) engine.els.nowThumb.src = slot.thumb;
      const npMeta = document.getElementById('playingNowMeta');
      if (npMeta) npMeta.textContent = slot.category || '';
      // Right dashboard
      const rdThumb = document.getElementById('rd-thumb');
      const rdNow = document.getElementById('rd-now-title');
      const rdCat = document.getElementById('rd-category');
      if (rdThumb && slot.thumb) rdThumb.src = slot.thumb;
      if (rdNow) rdNow.textContent = slot.title || '—';
      if (rdCat) rdCat.textContent = slot.category || '—';
    }
    if (next) {
      if (engine.els.nextTitle) engine.els.nextTitle.textContent = next.title || '—';
      // Right dashboard next
      const rdNext = document.getElementById('rd-next-title');
      if (rdNext) rdNext.textContent = next.title || '—';
    }
  }

  function updateProgressBar() {
    const slot = getCurrentSlot(engine.schedule, engine.selectedRow);
    if (!slot || !engine.els.progress) return;
    const now = Date.now();
    const pct = Math.max(0, Math.min(100, ((now - slot.startUTC) / (slot.endUTC - slot.startUTC)) * 100));
    engine.els.progress.style.width = pct + '%';
  }

  function highlightCurrentEPG() {
    const slot = getCurrentSlot(engine.schedule, engine.selectedRow);
    qsa('.program.epg-current').forEach(n => n.classList.remove('epg-current'));
    if (slot && slot.el) {
      slot.el.classList.add('epg-current');
      // ensure visible only if element is in layout (not hidden)
      const isVisible = !!(slot.el.offsetParent);
      if (isVisible) {
        try { slot.el.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' }); } catch (_) {}
      }
    }
  }

  function tick() {
    if (!engine.ready) return;
    playCurrentSlot();
    updateNowNext();
    updateProgressBar();
    highlightCurrentEPG();
  }

  function startEngine() {
    if (engine.timer) clearInterval(engine.timer);
    engine.timer = setInterval(tick, 1000);
    tick();
    log('engine started');
    wireRemoteControls();
    updateChannelLabel();
  }

  function wireRemoteControls() {
    const btnUp = document.getElementById('btnChUp');
    const btnDown = document.getElementById('btnChDown');
    const totalRows = engine.channels.length;
    const setRow = (row) => {
      engine.selectedRow = Math.max(0, Math.min(totalRows - 1, row));
      engine.lastSrc = ''; // force reload on next tick
      tick();
      log('channel changed to row', engine.selectedRow);
      updateChannelLabel();
    };
    if (btnUp) btnUp.addEventListener('click', () => setRow(engine.selectedRow + 1 >= totalRows ? 0 : engine.selectedRow + 1));
    if (btnDown) btnDown.addEventListener('click', () => setRow(engine.selectedRow - 1 < 0 ? totalRows - 1 : engine.selectedRow - 1));
  }

  function updateChannelLabel() {
    const label = document.getElementById('channelNameLabel');
    if (!label) return;
    const idx = engine.selectedRow;
    const total = Math.max(1, engine.channels.length);
    const ch = engine.channels[idx];
    const num = (idx + 1).toString().padStart(2, '0');
    label.textContent = `Channel ${num} — ${ch?.name || 'Live TV'}`;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();


