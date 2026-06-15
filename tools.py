# tools.py
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from notion_client import Client

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly"
]

# ─── Google Auth ───────────────────────────────────────────

def get_google_creds():
    creds = None
    token_path = os.getenv("GOOGLE_TOKEN_PATH", "auth/token.json")
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "auth/credentials.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, "w") as f:
                f.write(creds.to_json())
    return creds

# ─── Tool 1: Calendar ──────────────────────────────────────

def get_calendar_events() -> str:
    creds = get_google_creds()
    service = build("calendar", "v3", credentials=creds)

    now = datetime.now(timezone.utc).isoformat()
    today_end = datetime.now(timezone.utc).replace(
        hour=23, minute=59, second=59
    ).isoformat()

    result = service.events().list(
        calendarId="primary",
        timeMin=now,
        timeMax=today_end,
        maxResults=10,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = []
    for e in result.get("items", []):
        start = e.get("start", {})
        events.append({
            "title": e.get("summary", "No title"),
            "start": start.get("dateTime", start.get("date", "?")),
            "duration": e.get("end", {}).get("dateTime", "?"),
            "location": e.get("location", ""),
        })

    return json.dumps(events if events else [{"message": "No events today"}])

# ─── Tool 2: Gmail ─────────────────────────────────────────

def get_emails() -> str:
    creds = get_google_creds()
    service = build("gmail", "v1", credentials=creds)

    result = service.users().messages().list(
        userId="me",
        labelIds=["INBOX", "UNREAD"],
        maxResults=5
    ).execute()

    messages = []
    for msg in result.get("messages", []):
        detail = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["From", "Subject"]
        ).execute()

        headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
        snippet = detail.get("snippet", "")

        messages.append({
            "from": headers.get("From", "?"),
            "subject": headers.get("Subject", "No subject"),
            "snippet": snippet[:150]
        })

    return json.dumps(messages if messages else [{"message": "No unread emails"}])

# ─── Tool 3: Notion Tasks ──────────────────────────────────

def get_tasks() -> str:
    import httpx
    
    db_id = os.getenv("NOTION_DATABASE_ID")
    token = os.getenv("NOTION_TOKEN")

    response = httpx.post(
        f"https://api.notion.com/v1/databases/{db_id}/query",
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        },
        json={}
    )

    data = response.json()
    tasks = []

    for page in data.get("results", []):
        props = page["properties"]

        name = props.get("Name", {}).get("title", [{}])
        name = name[0].get("plain_text", "?") if name else "?"

        status = props.get("Status", {}).get("status", {})
        status = status.get("name", "?") if status else "?"

        priority = props.get("Priority", {}).get("select", {})
        priority = priority.get("name", "?") if priority else "?"

        due = props.get("Due Date", {}).get("date", {})
        due = due.get("start", "No date") if due else "No date"

        tasks.append({
            "task": name,
            "status": status,
            "priority": priority,
            "due": due
        })

    return json.dumps(tasks if tasks else [{"message": "No pending tasks"}])

# ─── Registry ──────────────────────────────────────────────

TOOLS = {
    "get_calendar_events": get_calendar_events,
    "get_emails": get_emails,
    "get_tasks": get_tasks,
}

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_calendar_events",
            "description": "Returns today's calendar events with title, start time and end time.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_emails",
            "description": "Returns unread emails from inbox with sender, subject and snippet.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": "Returns pending tasks from Notion with priority, status and due date.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
]


if __name__ == "__main__":
    print("📅 CALENDAR:")
    print(get_calendar_events())
    print("\n📧 EMAILS:")
    print(get_emails())
    print("\n✅ TASKS:")
    print(get_tasks())