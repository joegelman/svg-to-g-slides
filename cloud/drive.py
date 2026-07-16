"""Google Drive upload + sharing for the cloud converter service."""
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
MIME_PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


def _service():
    # On Cloud Run the attached service account provides credentials automatically.
    creds, _ = google.auth.default(scopes=SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


_SHARE_MESSAGE = (
    "Thanks for using svgslid.es! Your converted file has been shared to your Google "
    "account below. This link stays active for 7 days, after which the file is "
    "deleted from our end. To keep it permanently, open the file and choose "
    "File → Save to Drive, then File → Make a copy — the copy is fully yours "
    "to keep, with no expiry."
)


def upload_and_share(pptx_path: Path, email: str | None = None) -> str:
    """Upload pptx_path to Drive, share it, and return the webViewLink.

    We upload through a Google Cloud service account, which has no Drive storage
    quota of its own and can only write into a Shared Drive. Files in a Shared Drive
    can't have per-file ownership transferred (the Shared Drive collectively owns
    everything), so there's no way to hand real ownership to a recipient without
    switching the backend to a real OAuth-authenticated user account. Until then,
    every output file is a share with a fixed retention window (see RETENTION_DAYS
    in main.py / delete_old_files below) — the "Make a copy" step in the UI is the
    user's way to keep a file permanently in the meantime.
    """
    svc = _service()
    folder_id = os.environ.get("DRIVE_FOLDER_ID")

    meta = {"name": pptx_path.name}
    if folder_id:
        meta["parents"] = [folder_id]

    media = MediaFileUpload(str(pptx_path), mimetype=MIME_PPTX, resumable=False)
    file = (
        svc.files()
        .create(body=meta, media_body=media, fields="id",
                supportsAllDrives=True)
        .execute()
    )
    file_id = file["id"]

    # Anyone with the link can view
    svc.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
        sendNotificationEmail=False,
        supportsAllDrives=True,
    ).execute()

    # Also notify/share to a specific account if provided
    if email and email.strip():
        svc.permissions().create(
            fileId=file_id,
            body={"type": "user", "role": "writer", "emailAddress": email.strip()},
            sendNotificationEmail=True,
            emailMessage=_SHARE_MESSAGE,
            supportsAllDrives=True,
        ).execute()

    return f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"


def delete_old_files(folder_id: str, max_age_days: int) -> list[str]:
    """Permanently delete files in folder_id older than max_age_days. Returns deleted file IDs."""
    svc = _service()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=max_age_days)).isoformat()

    deleted = []
    page_token = None
    while True:
        resp = (
            svc.files()
            .list(
                q=f"'{folder_id}' in parents and createdTime < '{cutoff}' and trashed = false",
                fields="nextPageToken, files(id)",
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )
        for f in resp.get("files", []):
            try:
                svc.files().delete(fileId=f["id"], supportsAllDrives=True).execute()
                deleted.append(f["id"])
            except Exception:
                # Ownership may have already transferred to the recipient, in which
                # case we no longer have permission to delete it — that's fine, it's
                # theirs now and outside our retention window entirely.
                continue

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return deleted
