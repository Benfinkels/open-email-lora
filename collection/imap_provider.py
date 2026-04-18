import imaplib
import email
from email.header import decode_header
import json
from .base import EmailProvider

class IMAPProvider(EmailProvider):
    """
    Ingests emails from any IMAP-compliant provider (Outlook, iCloud, Yahoo, etc.).
    This provides a robust way to collect training data from personal mailboxes.
    """
    def __init__(self, host, user, password, port=993):
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

    def fetch_emails(self, query: str = "ALL", limit: int = 100):
        """
        Fetch emails from the inbox based on a search query.
        Returns a list of standardized dictionaries for processing.
        """
        if not self.mail:
            self.connect()
        
        # Default to INBOX
        self.mail.select("INBOX")
        
        # Search for emails matching the query
        # Standard IMAP queries: 'ALL', 'UNSEEN', 'FROM "name@domain.com"'
        status, messages = self.mail.search(None, query)
        if status != 'OK':
            print(f"Search failed for query '{query}'")
            return []

        email_ids = messages[0].split()
        print(f"Found {len(email_ids)} emails. Fetching last {limit}...")
        
        # Get the latest 'limit' emails
        email_ids = email_ids[-limit:]
        
        results = []
        for e_id in reversed(email_ids): # Process newest first
            try:
                status, msg_data = self.mail.fetch(e_id, "(RFC822)")
                if status != 'OK':
                    continue
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Extract and decode headers
                        subject = self._decode_header(msg.get("Subject", "No Subject"))
                        sender = self._decode_header(msg.get("From", "Unknown Sender"))
                        
                        # Extract email body
                        body = self._get_email_body(msg)
                        
                        results.append({
                            "sender": sender,
                            "subject": subject,
                            "body": body,
                            "id": e_id.decode()
                        })
            except Exception as e:
                print(f"Error processing email ID {e_id.decode()}: {e}")
                continue
                
        return results

    def _decode_header(self, header_val):
        """Helper to decode email headers with appropriate encoding."""
        if not header_val:
            return ""
        decoded, encoding = decode_header(header_val)[0]
        if isinstance(decoded, bytes):
            return decoded.decode(encoding if encoding else "utf-8", errors="replace")
        return decoded

    def _get_email_body(self, msg):
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
                self.mail.logout()
            except:
                pass
