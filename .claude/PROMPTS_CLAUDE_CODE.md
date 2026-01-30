# High-impact prompts for Claude Code

**Use these in a fresh session.** Each prompt assumes the assistant will **read CLAUDE.md first** for repo context (paths, patterns, mobile/scroll notes, cache busting) so you don’t burn tokens on setup.

Copy-paste one prompt below, or combine with your own instructions.

---

## 1. Split base.html (reduce size and complexity)

```
Read CLAUDE.md first for repo context. Then: templates/base.html is ~4.5k lines with layout, nav, modals, and a lot of inline Alpine.js. Propose a refactor that splits it into smaller Jinja partials and/or extracts inline JS into static/js files, without changing behavior. Prefer incremental steps (e.g. one logical block at a time) and note what to test after each step.
```

---

## 2. Add real tests and wire CI

```
Read CLAUDE.md first for repo context. Then: We have tests/test_smoke.py and tests/test_payments.py but CI doesn’t run them. Add or fix tests so pytest actually runs in CI (see .github/workflows/ci.yml). Prioritize: (1) smoke tests for key routes, (2) one integration-style test for a payment or auth flow if feasible. Update the workflow to run pytest and report results.
```

---

## 3. Stripe webhooks audit and hardening

```
Read CLAUDE.md first for repo context. Then: Audit routes/stripe_webhooks.py and related payment code (blueprints/payments.py, routes/boost_stripe.py) for Stripe best practices: idempotency, signature verification, handling of relevant event types, and any missing error paths. Suggest concrete code changes and add short comments where needed.
```

---

## 4. CSS structure and main.css

```
Read CLAUDE.md first for repo context. Then: static/css/main.css is very large (~25k lines). Propose a non-breaking way to split or reorganize it (e.g. by feature or section, or moving overrides into combined.css). List the main sections/blocks and suggest a file layout; implement the first split or one representative file if feasible.
```

---

## 5. Alembic migration hygiene

```
Read CLAUDE.md first for repo context. Then: Review alembic/versions/ and models.py. Suggest how to keep migrations maintainable (e.g. naming, downgrade correctness, or one-time data migrations). If there are redundant or risky patterns, list them and propose a single example fix.
```

---

## 6. Security and auth pass

```
Read CLAUDE.md first for repo context. Then: Do a focused pass on auth and security: utils/auth.py, utils/csrf.py, utils/security_headers.py, and any route that handles login or payments. List potential issues (e.g. session fixation, CSRF gaps, missing checks) and suggest minimal fixes with code snippets.
```

---

## 7. Docs sync from code

```
Read CLAUDE.md first for repo context. Then: docs/ has 40+ markdown files (deployment, Stripe, wallet, runbooks). Identify docs that likely reference code (routes, env vars, scripts) and list which files to update if we change X (e.g. a new env var, or a renamed route). Optionally update one doc to match current code as an example.
```

---

## 8. Native / packaging (Android or iOS)

```
Read CLAUDE.md first for repo context. Then: [Choose one] Review android/ build config (Gradle, signing, AAB) OR ios/ and packaging/ for iOS. List steps to produce a store-ready build from the repo and any obvious gaps or outdated settings. Prefer pointing to existing docs in packaging/ or docs/ and then suggesting edits.
```

---

**Tip:** Start with “Read CLAUDE.md first, then…” so the model loads that file before doing the task. You can still use the main Cursor agent for frontend tweaks, player fixes, and small UI changes.
