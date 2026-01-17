import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import re

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def get_drive_service():
    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    if not service_account_json:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON not set")

    service_account_info = json.loads(service_account_json)

    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )

    return build("drive", "v3", credentials=creds)

drive_service = get_drive_service()

def extract_folder_id(folder_link: str) -> str:
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", folder_link)
    if not match:
        raise ValueError("Invalid Google Drive folder link")
    return match.group(1)

def list_files_in_folder(folder_id: str):
    results = drive_service.files().list(
        q=f"'{folder_id}' in parents and mimeType!='application/vnd.google-apps.folder'",
        fields="files(id, name)"
    ).execute()
    return results.get("files", [])

def download_file(file_id: str, file_name: str, download_path: str):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(download_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()
