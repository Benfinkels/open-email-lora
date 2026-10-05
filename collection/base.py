from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import List, Dict, Any


class EmailProvider(ABC):
    """
    Abstract base class for all email ingestion methods.
    """
    @abstractmethod
    def fetch_emails(self, query: str = "ALL", limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch emails and return a list of standardized dicts:
        [{'sender': str, 'subject': str, 'body': str, 'id': str}]
        """
        pass

    def save_to_jsonl(self, emails: List[Dict[str, Any]], output_path: str, instruction: str = "Classify this email based on its content.") -> int:
        """Helper to save fetched emails to the standard instruction-tuning JSONL format."""
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        count = 0
        with open(out_file, "a", encoding="utf-8") as f:
            for email in emails:
                entry = {
                    "instruction": instruction,
                    "input": f"From: {email.get('sender', '')}\nSubject: {email.get('subject', '')}\nBody: {email.get('body', '')}",
                    "output": email.get("classification", "UNKNOWN")
                }
                f.write(json.dumps(entry) + "\n")
                count += 1
        return count
