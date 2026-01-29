# Token-light request for Claude Code

Copy-paste this when starting a session to give minimal context:

---

**Project:** Ahoy Indie Media — Flask app (music/shows, Stripe, auth). Read `CLAUDE.md` first for full context.

**Paths:** Entry `app.py`; routes `blueprints/`, `routes/`; frontend `static/js`, `static/css`, `templates/`; data `static/data/*.json`.

**Conventions:** DB: `with get_session() as session:`; API: `{"success": true, "data": ...}`; after CSS/JS changes bump `css_version` in `templates/base.html` (~line 144).

**Player (recent):** Global `window.mediaPlayer` (`static/js/player.js`). Toggle play/pause uses `mediaPlayer.isPlaying` and `mediaPlayer.currentTrack` as source of truth. Mini player + music page in `base.html` / `music.html`. Play: bound `element.play.bind(element)`; pause sets `isPlaying = false` then element.pause().

**Run:** `python app.py` (port 5001–5010). Tests: `pytest tests/` (may need DB env).

---

Replace the last paragraph with your actual task.
