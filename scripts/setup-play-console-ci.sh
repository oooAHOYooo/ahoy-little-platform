#!/bin/bash
# Setup Google Play Console service account for CI/CD
# This script automates the creation of a GCP service account with Play Console access

set -e

PROJECT_NAME="ahoy-indie-media-ci"
SERVICE_ACCOUNT_NAME="github-actions-deploy"
KEY_FILE="/tmp/play-console-key.json"
GITHUB_SECRET_NAME="PLAY_CONSOLE_SERVICE_ACCOUNT"

echo "🚀 Setting up Google Play Console CI/CD automation..."
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Install it first:"
    echo "   curl https://sdk.cloud.google.com | bash"
    exit 1
fi

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI not found. Install it first."
    exit 1
fi

echo "✓ gcloud and gh CLIs found"
echo ""

# Step 1: Authenticate with gcloud
echo "📝 Step 1: Authenticating with Google Cloud..."
gcloud auth login

echo ""
echo "📝 Step 2: Creating GCP project '$PROJECT_NAME'..."
PROJECT_ID=$(gcloud projects list --filter="name=$PROJECT_NAME" --format="value(projectId)" 2>/dev/null || true)

if [ -z "$PROJECT_ID" ]; then
    gcloud projects create $PROJECT_NAME --name="$PROJECT_NAME"
    PROJECT_ID=$PROJECT_NAME
    echo "✓ Project created: $PROJECT_ID"
else
    echo "✓ Project already exists: $PROJECT_ID"
fi

# Set as current project
gcloud config set project $PROJECT_ID

echo ""
echo "📝 Step 3: Enabling Google Play Developer API..."
gcloud services enable androidpublisher.googleapis.com --project=$PROJECT_ID

echo ""
echo "📝 Step 4: Creating service account '$SERVICE_ACCOUNT_NAME'..."
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name="GitHub Actions - Ahoy App CI/CD" \
    --project=$PROJECT_ID 2>/dev/null || echo "✓ Service account already exists"

echo "✓ Service account: $SERVICE_ACCOUNT_EMAIL"

echo ""
echo "📝 Step 5: Granting Play Console permissions..."
# Note: This requires manual setup in Play Console, but we can prepare the SA
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/androidpublisher.editor" \
    --quiet

echo "✓ Permissions granted"

echo ""
echo "📝 Step 6: Creating JSON key..."
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SERVICE_ACCOUNT_EMAIL \
    --project=$PROJECT_ID

echo "✓ Key created: $KEY_FILE"

echo ""
echo "📝 Step 7: Adding to GitHub Secrets..."

# Read the key and add to GitHub secrets
if [ -f "$KEY_FILE" ]; then
    KEY_CONTENT=$(cat "$KEY_FILE")

    # Add secret via GitHub CLI
    echo "$KEY_CONTENT" | gh secret set $GITHUB_SECRET_NAME --body -
    echo "✓ GitHub Secret '$GITHUB_SECRET_NAME' created"
else
    echo "❌ Key file not found"
    exit 1
fi

echo ""
echo "✓ All setup complete!"
echo ""
echo "⚠️  IMPORTANT: Finish Play Console setup manually:"
echo "   1. Go to Google Play Console → Settings → API access"
echo "   2. Click 'Create Service Account' link → 'Google Cloud Console'"
echo "   3. Find the service account: $SERVICE_ACCOUNT_EMAIL"
echo "   4. Grant it Play Console permissions"
echo "   5. You should also add it as an admin in Play Console"
echo ""
echo "📋 Service Account Email: $SERVICE_ACCOUNT_EMAIL"
echo "📋 GCP Project: $PROJECT_ID"
echo ""

# Cleanup
rm -f $KEY_FILE
