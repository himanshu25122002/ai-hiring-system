from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaIoBaseDownload
import io
import os

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = "service_account.json"

creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

drive_service = build("drive", "v3", credentials=creds)


def extract_folder_id(folder_url: str) -> str:
    """
    Extract folder ID from Google Drive link
    """
    if "folders" in folder_url:
        return folder_url.split("folders/")[1].split("?")[0]
    raise ValueError("Invalid Google Drive folder link")


def list_files_in_folder(folder_id: str):
    query = f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder'"
    results = drive_service.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()
    return results.get("files", [])


def download_file(file_id: str, filename: str, download_dir: str):
    request = drive_service.files().get_media(fileId=file_id)
    file_path = os.path.join(download_dir, filename)

    with io.FileIO(file_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    return file_path
