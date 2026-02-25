# Android Release Pipeline Guide

## Overview

This guide explains how the new **controlled release pipeline** works. It's designed to prevent accidental Play Store updates while allowing easy manual releases.

---

## Architecture

### Two-Stage Workflow

**Stage 1: Build (Every Push)**
- Triggers automatically on every push to `main`
- Builds Vue SPA
- Builds signed AAB & APK
- Artifacts stored for 30 days
- **Does NOT upload to Play Store**

**Stage 2: Deploy (Manual/Tag-Based)**
- Only runs when explicitly triggered
- Two methods:
  1. **Manual via GitHub UI** — click "Run workflow"
  2. **Automatic via git tags** — `git tag v1.0.1 && git push --tags`
- Uploads to Play Console (Internal Testing track, draft status)

---

## Setup Steps

### 1. Create Service Account (One-Time)

Run the automated setup script:

```bash
bash scripts/setup-play-console-ci.sh
```

This will:
- Authenticate with Google Cloud
- Create a GCP project
- Create a service account
- Add it to GitHub Secrets automatically

**Then manually in Google Play Console:**
1. Go **Settings** → **API access**
2. Find the service account email (printed in script output)
3. Grant it Play Console permissions

### 2. Add GitHub Secrets

The setup script handles this, but if you need to add manually:

| Secret | Value |
|--------|-------|
| `ANDROID_SIGNING_KEY` | Base64-encoded keystore (ask for help) |
| `ANDROID_KEYSTORE_PASSWORD` | `26trustdaL0RD` |
| `ANDROID_KEY_ALIAS` | `ahoy` |
| `ANDROID_KEY_PASSWORD` | `26trustdaL0RD` |
| `PLAY_CONSOLE_SERVICE_ACCOUNT` | JSON from setup script |

Add via: **GitHub** → **Settings** → **Secrets and variables** → **Actions**

---

## How to Release

### Option 1: Manual Release (Recommended for Weekly Updates)

1. Go to **GitHub** → **Actions** → **Android Build & Release**
2. Click **Run workflow**
3. Select `deploy_to_play: true`
4. Click **Run workflow**
5. Wait for build to complete (~10 min)
6. Check Play Console → Internal Testing track

### Option 2: Git Tag Release (For Version Releases)

```bash
# Create and push a version tag
git tag v1.0.1
git push --tags
```

This automatically:
- Builds the app
- Uploads to Play Console
- Creates a GitHub Release

### Option 3: Scheduled Weekly Release

Edit `.github/workflows/android-release.yml` and add:

```yaml
schedule:
  - cron: '0 9 * * 1'  # Every Monday at 9 AM
```

---

## Monitoring Releases

### Watch the Build Process

1. Go **GitHub** → **Actions**
2. See real-time build logs
3. Artifacts available after build succeeds

### Check Play Console Upload

1. Go **Google Play Console** → **Internal testing**
2. Look for the latest version in "Draft" status
3. Review changes
4. (Optional) Promote to "Staged rollout" or "Production"

---

## Rollback

If you need to revert a release:

1. Go **Play Console** → **Internal testing**
2. Find the previous version
3. Click **...** → **Revert this version**

---

## Troubleshooting

**Build fails?**
- Check GitHub Actions logs for errors
- Verify all GitHub Secrets are set correctly
- Ensure SPA builds locally: `cd spa && npm run build`

**Upload fails?**
- Verify service account has Play Console permissions
- Check that domain is verified (see CLAUDE.md)
- Re-run the setup script to verify credentials

**Want to disable auto-build on push?**
- Edit `.github/workflows/android-release.yml`
- Remove the `push` trigger
- Only manual/tag-based builds will run

---

## Safety Measures

✅ **Fail-Safes:**
- Builds on every push but **never uploads automatically**
- Manual confirmation required for Play Store upload
- Artifacts kept for 30 days (time to review)
- Draft status on upload (never goes live without review)

---

## Next Steps

1. **Fix DNS verification** for `littlemarket.org` in Google Search Console
2. **Run setup script**: `bash scripts/setup-play-console-ci.sh`
3. **Test manual release**: Trigger workflow from GitHub UI
4. **Review in Play Console**: Internal Testing track
5. **Iterate**: Push fixes → Manual release when ready
