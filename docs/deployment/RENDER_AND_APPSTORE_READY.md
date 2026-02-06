# Render + App Store Readiness (Dynamic Content DB)

## What’s already in place

- **Render:** `render.yaml` uses `startCommand: ./scripts/migrate_and_start.sh`, which:
  1. Runs `alembic upgrade head` (migrations, including `content_events` and `content_merch`)
  2. Runs `import_content_from_json.py` (music, shows, artists, podcasts from `dev/legacy_json/`)
  3. Runs `import_events_merch.py` (events from `static/data/events.json`; merch from `data/merch.json` if present)
  4. Runs `import_podcast_collection.py` (podcasts from `static/data/podcastCollection.json`)
  5. Starts Gunicorn

- **Dynamic content:** Events, merch, podcasts, and settings are DB-backed with JSON fallback. After each deploy, migrations run and the import scripts re-seed from the repo JSON (idempotent upserts).

- **Mobile app:** Capacitor loads the **deployed** site (e.g. `https://ahoy-indie-media.onrender.com` or `app.ahoy.ooo`). No extra config needed for “dynamic content”; the app uses the same APIs as the web app.

---

## Checklist: Render

| Step | Action |
|------|--------|
| 1 | Push to `main` (Render auto-deploys if `autoDeploy: true` in `render.yaml`). |
| 2 | Ensure **Start Command** is `./scripts/migrate_and_start.sh` (Render Dashboard → Service → Settings). |
| 3 | Ensure **Environment** has `DATABASE_URL` (from Render Postgres), `SECRET_KEY`, and any Stripe/email keys. |
| 4 | After deploy, open `/events`, `/merch`, `/podcasts` and confirm content loads (from DB or JSON fallback). |
| 5 | Optional: Run imports manually in Render Shell: `python scripts/import_events_merch.py` and `python scripts/import_podcast_collection.py` (e.g. if you added JSON after deploy). |

**Note:** `data/merch.json` is gitignored. On Render, merch import is skipped unless you add that file or seed merch another way. Events and podcasts are imported from `static/data/` which is in the repo.

---

## Checklist: App Store readiness

| Area | What to do |
|------|------------|
| **Backend** | Render deploy and migrations (above). App and store builds use the live API. |
| **Android (Play Store)** | Signed AAB is produced by your build (e.g. `android/app/build/outputs/bundle/release/app-release.aab`). Upload to Play Console → Internal testing (or production). Ensure store listing, privacy policy URL, and content rating are set. |
| **iOS (TestFlight/App Store)** | Complete Apple Developer enrollment ($99/yr), register bundle ID `com.ahoy.app`. Build via `./packaging/build-ios.sh` and upload in Xcode Organizer (or script). Add app in App Store Connect and submit for TestFlight. |
| **Capacitor URL** | `capacitor.config.ts` / `server.url` should point at your live URL (e.g. `https://ahoy-indie-media.onrender.com` or `https://app.ahoy.ooo`). |
| **Store assets** | Icons, screenshots, descriptions, privacy policy (e.g. `https://app.ahoy.ooo/privacy`), and support URL. |

---

## If content is missing after deploy

- **Events / podcasts empty:** Imports read from `static/data/events.json` and `static/data/podcastCollection.json`. If those exist in the repo, the next deploy will run the import scripts and seed the DB. You can also run the import scripts once in Render Shell.
- **Merch empty:** Add `data/merch.json` to the repo (or remove `data/*.json` from `.gitignore` and commit a minimal `merch.json`), then redeploy so `import_events_merch.py` can run, or seed merch via an admin/script later.
