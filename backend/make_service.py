import os
import requests

# These will come from environment variables
MAKE_SHORTLIST_WEBHOOK = os.getenv("MAKE_SHORTLIST_WEBHOOK")
MAKE_INTERVIEW_WEBHOOK = os.getenv("MAKE_INTERVIEW_WEBHOOK")
MAKE_FINAL_WEBHOOK = os.getenv("MAKE_FINAL_WEBHOOK")

def trigger_make_webhook(url: str, payload: dict):
    if not url:
        print("Make webhook URL not configured")
        return

    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("Make webhook error:", e)
