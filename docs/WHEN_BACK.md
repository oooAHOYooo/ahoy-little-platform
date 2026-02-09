# When you're back — quick handoff

Use this when you return to the project so you know where things stand and what to do next.

---

## Current state

- **Branch:** `spa-v2` (all recent work is here; not merged to `main` yet).
- **Archive tag:** `archive/spa-v2-pre-merge` — points to the last commit before any merge. If a merge goes wrong, you can restore with:  
  `git checkout -b spa-v2-restore archive/spa-v2-pre-merge`
- **Stripe:** Wallet, boost, and merch in the SPA work by redirecting to Flask `/checkout` and `/payments/*`. No Render config change needed; see `docs/deployment/RENDER_SPA_AND_STRIPE.md`.

---

## What to do when back

### 1. Get latest and confirm branch

```bash
git fetch origin
git checkout spa-v2
git pull origin spa-v2
```

### 2. Run the app locally (optional)

```bash
# Backend
python app.py

# SPA dev (separate terminal)
cd spa && npm run dev
```

### 3. Before merging spa-v2 → main

- [ ] Run tests: `pytest tests/` (or at least `pytest tests/test_smoke.py -v`).
- [ ] Build SPA: `cd spa && npm run build` (no errors).
- [ ] Optional: deploy `spa-v2` to a staging URL and click through main flows + Stripe (wallet, boost, merch).

### 4. Merge to main

- Merge `spa-v2` into `main` (PR or local merge, then push).
- Render will auto-deploy from `main` (build runs `./scripts/build_with_spa.sh`, so the SPA is built and served; `/checkout` and `/payments/*` stay as Flask).

### 5. After merge

- [ ] Smoke-check production: open app URL, log in, try music/podcasts, wallet, boost, merch checkout.
- [ ] Mobile: if you use the native app, it loads from the same production URL; no extra deploy step.

---

## Useful paths

| What | Where |
|------|--------|
| App entry | `app.py` (`create_app()`) |
| SPA routes | `spa/src/router.js` |
| SPA views | `spa/src/views/` |
| Stripe/checkout | Flask routes in `app.py` (e.g. `/checkout`, `/success`), `blueprints/payments.py` |
| Render config | `render.yaml` |
| SPA + Stripe on Render | `docs/deployment/RENDER_SPA_AND_STRIPE.md` |
| Pre-merge checklist | This file, "Before merging" section above |

---

## If something breaks after merge

- Restore from archive: `git checkout -b spa-v2-restore archive/spa-v2-pre-merge`, then fix or revert the merge on `main` as needed.
- Roll back on Render: redeploy the previous `main` commit from the Render dashboard.

---

*Last updated: when you ran "git push everything and write me a md of what to do when back".*
