import gspread
from google.oauth2.service_account import Credentials
import os
import json


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


def get_sheet():
    service_account_info = json.loads(
        os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    )

    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    sheet = client.open("AI Hiring – Candidates Database").worksheet("Candidates")
    return sheet


def append_candidate(row: dict):
    sheet = get_sheet()

    sheet.append_row([
        row["job_id"],
        row["role"],
        row["candidate_id"],
        row["name"],
        row["email"],
        row["skills"],
        row["experience_years"],
        row["score"],
        row["shortlisted"],
        row["resume_file"],
        row["confidence"]
    ])
def append_interview_qna(row: dict):
    worksheet = client.open(SHEET_NAME).worksheet("interview_qna")
    worksheet.append_row([
        row["candidate_id"],
        row["question_no"],
        row["question"],
        row["answer"]
    ])


