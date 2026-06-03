#!/usr/bin/env bash
# One-time setup + deploy for svg-to-slides on Cloud Run.
# Run from the repo root: bash cloud/deploy.sh
#
# Prerequisites: gcloud CLI installed and authenticated (gcloud auth login).
# All steps are idempotent — safe to re-run.

set -euo pipefail

# ── Config — edit these ────────────────────────────────────────────────────────
PROJECT_ID="svgslides-prod"          # e.g. "svg-to-slides-prod"  — leave blank to create new
REGION="us-central1"
SERVICE_NAME="svg-to-slides"
SA_NAME="svg-to-slides-sa"
SA_KEY_FILE="/tmp/svg-to-slides-sa-key.json"
SECRET_NAME="svg-to-slides-sa-json"
# ──────────────────────────────────────────────────────────────────────────────

if [[ -z "$PROJECT_ID" ]]; then
  echo "ERROR: Set PROJECT_ID at the top of this script."
  exit 1
fi

echo "=== 1. Select / create GCP project ==="
if gcloud projects describe "$PROJECT_ID" &>/dev/null; then
  echo "  Project $PROJECT_ID already exists."
else
  gcloud projects create "$PROJECT_ID" --name="SVG to Slides"
fi
gcloud config set project "$PROJECT_ID"

echo ""
echo "=== 2. Link billing (manual step) ==="
echo "  Open: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
echo "  Link a billing account, then press Return to continue."
read -r _

echo ""
echo "=== 3. Enable APIs ==="
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  drive.googleapis.com \
  secretmanager.googleapis.com \
  --project "$PROJECT_ID"

echo ""
echo "=== 4. Service account ==="
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
if gcloud iam service-accounts describe "$SA_EMAIL" &>/dev/null; then
  echo "  SA $SA_EMAIL already exists."
else
  gcloud iam service-accounts create "$SA_NAME" \
    --display-name="SVG to Slides converter"
fi

echo ""
echo "=== 5. Create & store SA key in Secret Manager ==="
gcloud iam service-accounts keys create "$SA_KEY_FILE" \
  --iam-account="$SA_EMAIL"

if gcloud secrets describe "$SECRET_NAME" --project "$PROJECT_ID" &>/dev/null; then
  gcloud secrets versions add "$SECRET_NAME" --data-file="$SA_KEY_FILE"
  echo "  New key version added to existing secret."
else
  gcloud secrets create "$SECRET_NAME" \
    --data-file="$SA_KEY_FILE" \
    --replication-policy="automatic"
fi
rm -f "$SA_KEY_FILE"
echo "  Key stored; local copy deleted."

echo ""
echo "=== 6. Grant SA access to read its own secret ==="
gcloud secrets add-iam-policy-binding "$SECRET_NAME" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/secretmanager.secretAccessor"

echo ""
echo "=== 7. Create shared Drive output folder (manual step) ==="
cat <<'MSG'
  In a browser, sign into the Google account that will own output files.
  Create a folder called "SVG to Slides Outputs" in My Drive.
  Share it with the service account email below as Editor:

MSG
echo "    $SA_EMAIL"
echo ""
echo "  Then open the folder in Drive and copy the folder ID from the URL:"
echo "    https://drive.google.com/drive/folders/<FOLDER_ID>"
echo ""
read -rp "  Paste FOLDER_ID here: " FOLDER_ID

echo ""
echo "=== 8. Build and deploy to Cloud Run ==="
# Build from repo root so the Dockerfile COPY paths resolve correctly
gcloud builds submit . \
  --tag "gcr.io/$PROJECT_ID/$SERVICE_NAME" \
  --project "$PROJECT_ID"

gcloud run deploy "$SERVICE_NAME" \
  --image "gcr.io/$PROJECT_ID/$SERVICE_NAME" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --set-secrets "GOOGLE_SA_JSON=${SECRET_NAME}:latest" \
  --set-env-vars "DRIVE_FOLDER_ID=$FOLDER_ID" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --project "$PROJECT_ID"

echo ""
echo "=== Done ==="
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region "$REGION" --project "$PROJECT_ID" \
  --format "value(status.url)")
echo "  Service URL: $SERVICE_URL"
