import imaplib
import email
from email.header import decode_header
import json
from typing import List, Dict, Any

try:
    from .base import EmailProvider
except ImportError:
    from base import EmailProvider


class IMAPProvider(EmailProvider):
    """
    Ingests emails from any IMAP-compliant provider (Outlook, iCloud, Yahoo, etc.).
    This provides a robust way to collect training data from personal mailboxes.
    """
    def __init__(self, host: str, user: str, password: str, port: int = 993):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.mail = None

    def connect(self):
        """Establish a secure connection to the IMAP server."""
        try:
            self.mail = imaplib.IMAP4_SSL(self.host, self.port)
            self.mail.login(self.user, self.password)
            print(f"Connected to {self.host} as {self.user}")
        except Exception as e:
            print(f"IMAP Connection Error: {e}")
            raise

    def fetch_emails(self, query: str = "ALL", limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch emails from the inbox based on a search query.
        Returns a list of standardized dictionaries for processing.
        """
        if not self.mail:
            self.connect()

        # Default to INBOX
        self.mail.select("INBOX")

        status, messages = self.mail.search(None, query)
        if status != 'OK' or not messages or not messages[0]:
            print(f"No messages found for query '{query}'")
            return []

        email_ids = messages[0].split()
        print(f"Found {len(email_ids)} emails. Fetching up to {limit}...")

        email_ids = email_ids[-limit:]

        results = []
        for e_id in reversed(email_ids):
            try:
                status, msg_data = self.mail.fetch(e_id, "(RFC822)")
                if status != 'OK' or not msg_data:
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = self._decode_header(msg.get("Subject", "No Subject"))
                        sender = self._decode_header(msg.get("From", "Unknown Sender"))
                        body = self._get_email_body(msg)

                        results.append({
                            "sender": sender,
                            "subject": subject,
                            "body": body,
                            "id": e_id.decode(errors="ignore")
                        })
            except Exception as e:
                print(f"Error processing email ID {e_id}: {e}")
                continue

        return results

    @staticmethod
    def _decode_header(header_val) -> str:
        """Helper to decode email headers with appropriate encoding."""
        if not header_val:
            return ""
        try:
            decoded_parts = decode_header(header_val)
            text_parts = []
            for decoded, encoding in decoded_parts:
                if isinstance(decoded, bytes):
                    text_parts.append(decoded.decode(encoding if encoding else "utf-8", errors="replace"))
                else:
                    text_parts.append(str(decoded))
            return "".join(text_parts)
        except Exception:
            return str(header_val)

    @staticmethod
    def _get_email_body(msg) -> str:
        """Recursively extract the plain text body from the email."""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(errors="replace")
                    break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(errors="replace")
        return body.strip()

    def disconnect(self):
        """Gracefully close the IMAP session."""
        if self.mail:
            try:
                self.mail.close()
            except Exception:
                pass
            try:
                self.mail.logout()
            except Exception:
                pass
            self.mail = None
