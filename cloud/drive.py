"""Google Drive upload + sharing for the cloud converter service."""
import json
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
MIME_PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


def _service():
    raw = os.environ.get("GOOGLE_SA_JSON")
    if not raw:
        raise RuntimeError("GOOGLE_SA_JSON env var not set")
    info = json.loads(raw)
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def upload_and_share(pptx_path: Path, email: str | None = None) -> str:
    """Upload pptx_path to Drive, set sharing, return the webViewLink."""
    svc = _service()
    folder_id = os.environ.get("DRIVE_FOLDER_ID")

    meta = {"name": pptx_path.name}
    if folder_id:
        meta["parents"] = [folder_id]

    media = MediaFileUpload(str(pptx_path), mimetype=MIME_PPTX, resumable=False)
    file = (
        svc.files()
        .create(body=meta, media_body=media, fields="id,webViewLink")
        .execute()
    )
    file_id = file["id"]

    # Anyone with the link can view
    svc.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
        sendNotificationEmail=False,
    ).execute()

    # Also notify/share to a specific account if provided
    if email and email.strip():
        svc.permissions().create(
            fileId=file_id,
            body={"type": "user", "role": "writer", "emailAddress": email.strip()},
            sendNotificationEmail=True,
        ).execute()

    return file["webViewLink"]
