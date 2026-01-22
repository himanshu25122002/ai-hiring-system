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
        row.get("interview_score"),
        row.get("rank"),
        row.get("rank_score"),
        row.get("recommendation"),
        row.get("shortlisted"),
        row.get("resume_file"),
        row.get("confidence"),
        row.get("email_stage", "RESUME_SHORTLISTED"),
        row.get("personal_form_submitted", False)

    ])

def update_candidate_by_id(candidate_id: str, updates: dict):
    sheet = get_sheet()
    records = sheet.get_all_records()

    for idx, row in enumerate(records, start=2):  # row 1 = header
        if str(row.get("candidate_id")) == str(candidate_id):
            for col_name, value in updates.items():
                col_index = list(row.keys()).index(col_name) + 1
                sheet.update_cell(idx, col_index, value)
            return True

    raise ValueError("Candidate not found in Google Sheet")



