#!/usr/bin/env bash
# One-time setup + deploy for svg-to-slides on Cloud Run.
# Run from the repo root: bash cloud/deploy.sh
#
# Uses Workload Identity (no SA key file, no Secret Manager).
# Prerequisites: gcloud CLI installed and authenticated (gcloud auth login).
# All steps are idempotent — safe to re-run.

set -euo pipefail

# ── Config — edit these ────────────────────────────────────────────────────────
PROJECT_ID="svgslides-prod"
REGION="us-central1"
SERVICE_NAME="svg-to-slides"
SA_NAME="svg-to-slides-sa"
CLEANUP_JOB_NAME="svg-to-slides-cleanup"
CLEANUP_SCHEDULE="0 3 * * *"   # daily at 03:00 UTC
RETENTION_DAYS="7"             # max age of output files before /cleanup deletes them
FOLDER_ID="0AKb8tLQLj7MGUk9PVA"  # Drive output folder — press Return at the step 5 prompt to keep this
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
  cloudscheduler.googleapis.com \
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
echo "=== 5. Drive output folder ==="
echo "  Using FOLDER_ID from the config block above: $FOLDER_ID"
cat <<MSG
  (To use a different folder: in a browser, sign into the Google account that
  will own output files, create a folder in My Drive, share it with the
  service account below as Editor, then paste its ID here. Note the service
  account has no Drive storage quota of its own — it can only write into a
  Shared Drive, not a plain folder shared to it.

    $SA_EMAIL
  )
MSG
read -rp "  Paste a different FOLDER_ID, or press Return to keep the default: " INPUT_FOLDER_ID
FOLDER_ID="${INPUT_FOLDER_ID:-$FOLDER_ID}"

echo ""
echo "=== 6. Build and deploy to Cloud Run ==="
# Fresh secret each deploy — Cloud Run and the Scheduler job below are updated
# together, so rotating it on every run is safe.
CLEANUP_TOKEN=$(openssl rand -hex 32)

# Build from repo root using cloudbuild.yaml (Dockerfile is in cloud/).
# Note: cloudbuild.yaml hardcodes the image path rather than using a substitution,
# so it must match PROJECT_ID/SERVICE_NAME above if either is ever changed.
gcloud builds submit . \
  --config "cloudbuild.yaml" \
  --project "$PROJECT_ID"

gcloud run deploy "$SERVICE_NAME" \
  --image "us-central1-docker.pkg.dev/$PROJECT_ID/svg-to-slides/$SERVICE_NAME" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --service-account "$SA_EMAIL" \
  --set-env-vars "DRIVE_FOLDER_ID=$FOLDER_ID,CLEANUP_TOKEN=$CLEANUP_TOKEN,RETENTION_DAYS=$RETENTION_DAYS" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --project "$PROJECT_ID"

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region "$REGION" --project "$PROJECT_ID" \
  --format "value(status.url)")

echo ""
echo "=== 7. Schedule automatic cleanup ==="
if gcloud scheduler jobs describe "$CLEANUP_JOB_NAME" --location "$REGION" --project "$PROJECT_ID" &>/dev/null; then
  gcloud scheduler jobs update http "$CLEANUP_JOB_NAME" \
    --location "$REGION" \
    --schedule "$CLEANUP_SCHEDULE" \
    --uri "$SERVICE_URL/cleanup" \
    --http-method POST \
    --update-headers "X-Cleanup-Token=$CLEANUP_TOKEN" \
    --project "$PROJECT_ID"
else
  gcloud scheduler jobs create http "$CLEANUP_JOB_NAME" \
    --location "$REGION" \
    --schedule "$CLEANUP_SCHEDULE" \
    --uri "$SERVICE_URL/cleanup" \
    --http-method POST \
    --headers "X-Cleanup-Token=$CLEANUP_TOKEN" \
    --project "$PROJECT_ID"
fi

echo ""
echo "=== Done ==="
echo "  Service URL: $SERVICE_URL"
echo "  Cleanup job: $CLEANUP_JOB_NAME ($CLEANUP_SCHEDULE, retention ${RETENTION_DAYS}d)"
