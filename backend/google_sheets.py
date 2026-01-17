# backend/google_sheets.py

import gspread
from google.oauth2.service_account import Credentials
import os
import json

# Scope for Google Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

# Sheet & Worksheet names
SPREADSHEET_NAME = "AI Hiring - Candidates Database"
WORKSHEET_NAME = "Candidates"


def get_sheet():
    """
    Authorize and return Google Sheet worksheet
    """
    service_account_info = json.loads(
        os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    )

    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)
    return sheet


def append_candidate(row: dict):
    """
    Append one candidate row to Google Sheet
    """
    sheet = get_sheet()

    sheet.append_row([
        row.get("job_id"),
        row.get("role"),
        row.get("candidate_id"),
        row.get("name"),
        row.get("email"),
        row.get("email_confidence"),
        row.get("skills"),
        row.get("experience_years"),
        row.get("score"),
        row.get("rank"),
        row.get("rank_score"),
        row.get("shortlisted"),
        row.get("interview_score"),
        row.get("final_recommendation"),
        row.get("resume_file"),
        row.get("confidence"),
    ])
