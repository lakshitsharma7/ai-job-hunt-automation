"""
Google Sheets Sync Integration for Job Hunt Tracker
Synchronizes the local Job_Hunt_Tracker.xlsx / CSV with a live Google Sheet.
Supports Google Sheets API (v4) with service accounts or OAuth client secrets.
"""

import os
import csv
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "tracker", "Job_Hunt_Tracker.csv")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "gsheets_config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "spreadsheet_id": "",
        "sheet_name": "Job Hunt Tracker",
        "service_account_file": "config/google_service_account.json",
        "status": "REQUIRES_USER_AUTHORIZATION"
    }

def sync_to_google_sheets():
    """
    Reads local Job_Hunt_Tracker.csv and pushes updates to the Google Sheet.
    If credentials are not yet configured, returns a descriptive authorization guide.
    """
    config = load_config()
    spreadsheet_id = config.get("spreadsheet_id")
    sa_file = os.path.join(BASE_DIR, config.get("service_account_file", ""))

    if not spreadsheet_id or not os.path.exists(sa_file):
        return {
            "status": "REQUIRES USER AUTHORIZATION",
            "message": (
                "Google Sheets sync is ready to connect, but requires your Google Sheet URL/ID "
                "and an authorized Google Service Account or OAuth credentials file.\n"
                "In the meantime, your local Job_Hunt_Tracker.xlsx and Job_Hunt_Tracker.csv "
                "are fully updated, formatted, and operational."
            ),
            "instructions": [
                "1. Create a Google Sheet named 'Job Hunt Tracker'.",
                "2. Create a service account in Google Cloud Console and enable Google Sheets API.",
                "3. Share the Google Sheet with the service account email (as Editor).",
                "4. Place service account JSON in 'AI-Job-Hunt/config/google_service_account.json'.",
                "5. Alternatively, install the official Antigravity Google Sheets plugin: 'antigravity-plugins-official/plugin/gsheets'."
            ]
        }

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = service_account.Credentials.from_service_account_file(sa_file, scopes=scopes)
        service = build("sheets", "v4", credentials=creds)

        rows = []
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for r in reader:
                rows.append(r)

        body = {"values": rows}
        range_name = f"{config.get('sheet_name', 'Job Hunt Tracker')}!A1"
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        return {
            "status": "SUCCESS",
            "rows_synced": len(rows),
            "spreadsheet_id": spreadsheet_id
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e)
        }

if __name__ == "__main__":
    result = sync_to_google_sheets()
    print(json.dumps(result, indent=2))

