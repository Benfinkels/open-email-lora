import os
from typing import List, Dict, Any

try:
    from .base import EmailProvider
except ImportError:
    from base import EmailProvider


class GmailProvider(EmailProvider):
    """
    Ingests emails from Gmail via OAuth2 or service account credentials.
    """
    def __init__(self, credentials_path: str = "secrets/token.json"):
        self.credentials_path = credentials_path
        self.service = None

    def connect(self):
        """Initializes Google API client if dependencies and token are present."""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Gmail credentials not found at {self.credentials_path}. "
                "See documentation for setting up Google API OAuth2 credentials."
            )
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = Credentials.from_authorized_user_file(self.credentials_path)
            self.service = build("gmail", "v1", credentials=creds)
            print("Successfully authenticated with Gmail API.")
        except ImportError:
            raise ImportError(
                "google-api-python-client and google-auth-oauthlib are required for GmailProvider. "
                "Install with: pip install google-api-python-client google-auth-oauthlib"
            )

    def fetch_emails(self, query: str = "is:unread", limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail using the query."""
        if not self.service:
            self.connect()

        results = []
        try:
            response = self.service.users().messages().list(userId="me", q=query, maxResults=limit).execute()
            messages = response.get("messages", [])

            for msg_meta in messages:
                msg = self.service.users().messages().get(userId="me", id=msg_meta["id"], format="full").execute()
                headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
                snippet = msg.get("snippet", "")

                results.append({
                    "id": msg_meta["id"],
                    "sender": headers.get("from", "Unknown"),
                    "subject": headers.get("subject", "No Subject"),
                    "body": snippet
                })
        except Exception as e:
            print(f"Error fetching Gmail messages: {e}")
            raise

        return results
