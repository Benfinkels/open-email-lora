from abc import ABC, abstractmethod
import json

class EmailProvider(ABC):
    """
    Abstract base class for all email ingestion methods.
    """
    @abstractmethod
    def fetch_emails(self, query: str, limit: int):
        """Fetch emails and return a list of standardized dicts."""
        pass

    def save_to_jsonl(self, emails, output_path):
        """Helper to save fetched emails to the standard training format."""
        with open(output_path, "a") as f:
            for email in emails:
                # Format for Unsloth/Gemma
                entry = {
                    "instruction": "Classify this email based on its content.",
                    "input": f"From: {email['sender']}\nSubject: {email['subject']}\nBody: {email['body']}",
                    "output": "UNKNOWN" # To be filled during labeling
                }
                f.write(json.dumps(entry) + "\n")
