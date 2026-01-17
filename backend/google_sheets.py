import gspread
import json
import os
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

SPREADSHEET_NAME = "AI Hiring - Candidates Database"
WORKSHEET_NAME = "Candidates"


def get_sheet():
    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    if not service_account_json:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON env variable not set")

    service_account_info = json.loads(service_account_json)

    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)
    return sheet


def append_candidate(row: dict):
    sheet = get_sheet()

    sheet.append_row([
        row.get("job_id"),
        row.get("role"),
        row.get("candidate_id"),
        row.get("name"),
        row.get("email"),
        row.get("skills"),
        row.get("experience_years"),
        row.get("score"),
        row.get("shortlisted"),
        row.get("resume_file"),
        row.get("confidence")
    ])
