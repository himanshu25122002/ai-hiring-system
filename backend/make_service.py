import os
import requests

# Webhook URLs (configured in Render / environment variables)
MAKE_SHORTLIST_WEBHOOK = os.getenv("MAKE_SHORTLIST_WEBHOOK")
MAKE_INTERVIEW_WEBHOOK = os.getenv("MAKE_INTERVIEW_WEBHOOK")
MAKE_FINAL_WEBHOOK = os.getenv("MAKE_FINAL_WEBHOOK")


def trigger_make_webhook(url: str, payload: dict):
    """
    Generic helper to trigger a Make.com webhook
    """
    if not url:
        print("⚠️ Make webhook URL not configured")
        return

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        print("✅ Make webhook triggered successfully")
    except Exception as e:
        print("❌ Make webhook error:", e)
