import os
import json
import argparse
import subprocess

def get_emails(query="is:unread", limit=100, dry_run=True):
    """
    Extracts emails using the 'gog' CLI.
    In a public repo, we'd replace this with a native IMAP/Gmail API client.
    """
    print(f"--- [COLLECTING EMAILS: query='{query}', limit={limit}] ---")
    if dry_run:
        print("NOTE: Running in DRY-RUN mode. No state changes will be made to your inbox.")
    
    # Heuristic: we'll simulate the extraction for the public project logic
    # In a real environment, we'd call: gog gmail messages list ...
    
    # Standard output format: JSONL
    # Each line: {"instruction": "...", "input": "sender/subject/body", "output": "classification"}
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email Collector for LoRA Fine-tuning")
    parser.add_argument("--query", default="is:unread", help="Gmail search query")
    parser.add_argument("--limit", type=int, default=100, help="Max emails to download")
    parser.add_argument("--read-only", action="store_true", default=True, help="Do not modify email state")
    
    args = parser.parse_args()
    get_emails(args.query, args.limit, args.read_only)
