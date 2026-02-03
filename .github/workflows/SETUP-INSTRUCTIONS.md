# Android Auto-Deploy Setup Instructions

## Prerequisites

1. **Google Play Console Access**
   - You need a Google Play Developer account ($25 one-time fee)
   - Your app must be created in Play Console

2. **Google Cloud Project**
   - Link your Play Console to Google Cloud
   - Enable Google Play Android Developer API

## Step-by-Step Setup

### 1. Create Service Account for Play Store API

```bash
# Go to Google Cloud Console
# https://console.cloud.google.com/

# 1. Select your project (or create one)
# 2. Go to "IAM & Admin" → "Service Accounts"
# 3. Click "Create Service Account"
#    Name: "github-actions-play-deploy"
#    Role: "Service Account User"
# 4. Click "Create and Continue"
# 5. Click "Done"
# 6. Click on the service account
# 7. Go to "Keys" tab
# 8. Click "Add Key" → "Create new key" → "JSON"
# 9. Save the JSON file (you'll need it for GitHub Secrets)
```

### 2. Grant Service Account Access to Play Console

```bash
# Go to Google Play Console
# https://play.google.com/console

# 1. Select your app
# 2. Go to "Setup" → "API access"
# 3. Click "Link" to link your Google Cloud project
# 4. Find your service account in the list
# 5. Click "Grant access"
# 6. Select permissions:
#    - "Releases" → "Release to testing tracks"
#    - "App information" → "View app information"
# 7. Click "Invite user" → "Send invitation"
```

### 3. Encode Your Keystore to Base64

```bash
# From your project root:
cd android/keystore
base64 -i ahoy-release.jks | pbcopy
# Your keystore is now copied to clipboard as base64
```

### 4. Add Secrets to GitHub

```bash
# Go to your GitHub repo
# https://github.com/YOUR_USERNAME/ahoy-little-platform

# 1. Go to "Settings" → "Secrets and variables" → "Actions"
# 2. Click "New repository secret"
# 3. Add each secret:
```

**Required Secrets:**

| Secret Name | Value | Where to Get It |
|-------------|-------|-----------------|
| `ANDROID_KEYSTORE_BASE64` | Base64 encoded keystore | Output from step 3 above |
| `KEYSTORE_PASSWORD` | `26trustdaL0RD` | From `android/keystore/sign.properties` |
| `KEY_ALIAS` | `ahoy` | From `android/keystore/sign.properties` |
| `KEY_PASSWORD` | `26trustdaL0RD` | Same as keystore password |
| `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` | Full JSON content | The JSON file from step 1 |

**For GOOGLE_PLAY_SERVICE_ACCOUNT_JSON:**
```bash
# Copy the entire contents of the JSON file:
cat ~/Downloads/your-service-account-key.json | pbcopy
# Paste into GitHub secret (it's a big JSON blob)
```

### 5. Test the Workflow

**Option A: Manual Trigger**
```bash
# Go to GitHub → "Actions" tab
# Click "Deploy Android to Play Store"
# Click "Run workflow" → "Run workflow"
```

**Option B: Git Push**
```bash
# Make a change to a file in static/ or templates/
git add .
git commit -m "Test auto-deploy"
git push origin main
# Check GitHub Actions tab to watch progress
```

### 6. Verify Deployment

```bash
# After workflow succeeds:
# 1. Go to Play Console
# 2. Navigate to "Testing" → "Internal testing"
# 3. You should see a new release!
# 4. Add testers and share the link
```

## Troubleshooting

### Error: "The Android App Bundle was not signed"
- Check that `ANDROID_KEYSTORE_BASE64` secret is correct
- Verify keystore password is correct

### Error: "Service account does not have access"
- Go to Play Console → API Access
- Grant permissions to service account (step 2 above)
- Wait 5-10 minutes for permissions to propagate

### Error: "packageName not found"
- Verify your app is created in Play Console
- Check that package name matches: `com.ahoy.app`
- You may need to upload the first version manually

### Workflow doesn't trigger
- Check that you pushed to `main` branch
- Check that files in `static/` or `templates/` changed
- Try manual trigger from Actions tab

## Advanced: Version Bumping

To automatically bump version numbers, add this to your workflow:

```yaml
- name: Bump version code
  run: |
    # Auto-increment versionCode
    cd android
    VERSION_CODE=$(grep versionCode app/build.gradle | awk '{print $2}')
    NEW_VERSION=$((VERSION_CODE + 1))
    sed -i '' "s/versionCode $VERSION_CODE/versionCode $NEW_VERSION/" app/build.gradle
    git config user.name "GitHub Actions"
    git config user.email "actions@github.com"
    git add app/build.gradle
    git commit -m "Bump Android version to $NEW_VERSION"
    git push
```

## Cost & Limits

- **Google Play Console**: $25 one-time fee
- **GitHub Actions**: 2,000 free minutes/month for private repos
- **Play Store Internal Testing**: 100 testers max
- **Build time**: ~5-10 minutes per deploy

## Alternative: Deploy on Tag/Release Only

If you want to deploy only on releases (not every push), change the trigger:

```yaml
on:
  release:
    types: [published]
  workflow_dispatch:
```

Then create releases:
```bash
git tag v1.0.0
git push origin v1.0.0
# Or create release via GitHub UI
```
