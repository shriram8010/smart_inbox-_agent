from googleapiclient.discovery import build
from auth import gmail_authenticate
import base64
from email.message import EmailMessage


def get_gmail_service():
    creds = gmail_authenticate()
    return build("gmail", "v1", credentials=creds)


def fetch_emails(max_results=10):
    service = get_gmail_service()
    results = service.users().messages().list(
        userId="me",
        maxResults=max_results
    ).execute()

    emails = []

    for msg in results.get("messages", []):
        message = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        headers = message["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "")

        body = ""
        parts = message["payload"].get("parts", [])
        for part in parts:
            if part.get("mimeType") == "text/plain":
                body = base64.urlsafe_b64decode(
                    part["body"]["data"]
                ).decode(errors="ignore")
                break

        emails.append({
            "id": message["id"],
            "threadId": message["threadId"],   # ✅ REQUIRED
            "from": sender,
            "subject": subject,
            "body": body[:3000]
        })

    return emails


def send_reply(original_email, reply_text):
    service = get_gmail_service()

    message = EmailMessage()
    message.set_content(reply_text)

    message["To"] = original_email["from"]
    message["Subject"] = f"Re: {original_email['subject']}"

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    service.users().messages().send(
        userId="me",
        body={
            "raw": raw_message,
            "threadId": original_email["threadId"]  # ✅ FIX
        }
    ).execute()
