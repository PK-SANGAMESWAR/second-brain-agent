from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os, json

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly"
]

def get_google_creds():
    creds = None
    if os.path.exists("auth/token.json"):
        creds = Credentials.from_authorized_user_file("auth/token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("auth/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("auth/token.json", "w") as f:
            f.write(creds.to_json())
    return creds

creds = get_google_creds()

# Test Calendar
cal = build("calendar", "v3", credentials=creds)
events = cal.events().list(calendarId="primary", maxResults=3).execute()
print("📅 Calendar:", [e["summary"] for e in events.get("items", [])])

# Test Gmail
gmail = build("gmail", "v1", credentials=creds)
msgs = gmail.users().messages().list(userId="me", maxResults=3).execute()
print("📧 Gmail messages found:", msgs.get("resultSizeEstimate"))