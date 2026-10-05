import os
import sys
import argparse
import json
from pathlib import Path

try:
    from .anonymizer import EmailScrubber, scrub_jsonl
    from .base import EmailProvider
    from .imap_provider import IMAPProvider
    from .gmail_provider import GmailProvider
except ImportError:
    from anonymizer import EmailScrubber, scrub_jsonl
    from base import EmailProvider
    from imap_provider import IMAPProvider
    from gmail_provider import GmailProvider


def generate_sample_emails(limit: int = 10) -> list:
    """Generate realistic emails for testing the collection pipeline without live credentials."""
    samples = [
        {
            "id": "msg-001",
            "sender": "sarah.connor@cyberdyne-tech.com",
            "subject": "Q3 Budget Review - Urgent Action Required",
            "body": "Hi Ben,\nPlease find attached the Q3 budget spreadsheet. We need your sign-off by 5 PM today before submitting to finance.\nLet me know if you have questions at 555-014-9921 or visit https://finance.internal/reports.\nThanks,\nSarah",
            "classification": "ACTION"
        },
        {
            "id": "msg-002",
            "sender": "newsletter@techdigest-daily.io",
            "subject": "Weekly AI Digest: LLM Quantization & LoRA Best Practices",
            "body": "Welcome to this week's issue! Top stories include Gemma 4 optimizations, Unsloth updates, and fine-tuning techniques on consumer hardware. Unsubscribe at https://techdigest-daily.io/unsub?id=8271",
            "classification": "NEWSLETTER"
        },
        {
            "id": "msg-003",
            "sender": "recruiter@talent-scout-global.com",
            "subject": "Exciting Senior Machine Learning Engineer Opportunity",
            "body": "Hi Ben, I came across your GitHub profile and was impressed by your open-source projects. Our client is looking for a Lead AI Engineer ($180k-$240k). Are you open for a quick 10-minute chat this week? Reach me at 415-555-0182.",
            "classification": "ACTION"
        },
        {
            "id": "msg-004",
            "sender": "promo-deals@megasavings.shop",
            "subject": "Flash Sale: Up to 70% off electronics!",
            "body": "Don't miss our 24-hour clearance sale. Claim your exclusive coupon code FLASH70 before midnight at https://megasavings.shop/deal?code=FLASH70.",
            "classification": "SPAM"
        },
        {
            "id": "msg-005",
            "sender": "david.miller@acme-corp.com",
            "subject": "Coffee / Quick catch-up next Tuesday?",
            "body": "Hey Ben! Long time no see. Are you around downtown next Tuesday for a quick coffee? Let me know what time works best for you.",
            "classification": "PERSONAL"
        }
    ]
    # Cycle samples if limit > len(samples)
    results = []
    for i in range(limit):
        item = samples[i % len(samples)].copy()
        item["id"] = f"sample-{i+1:03d}"
        results.append(item)
    return results


def run_collection(
    provider_name: str = "sample",
    query: str = "ALL",
    limit: int = 20,
    output_path: str = "data/raw_emails.jsonl",
    scrub: bool = True,
    imap_host: str = None,
    imap_user: str = None,
    imap_pass: str = None,
    imap_port: int = 993,
    gmail_token: str = "secrets/token.json"
):
    print(f"--- [COLLECTING EMAILS: provider='{provider_name}', query='{query}', limit={limit}] ---")
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    emails = []

    if provider_name == "sample":
        print("Using bundled sample email generator...")
        emails = generate_sample_emails(limit)

    elif provider_name == "imap":
        host = imap_host or os.getenv("IMAP_HOST")
        user = imap_user or os.getenv("IMAP_USER")
        password = imap_pass or os.getenv("IMAP_PASSWORD")
        port = int(imap_port or os.getenv("IMAP_PORT", 993))

        if not (host and user and password):
            print("Error: IMAP host, user, and password are required. Falling back to sample mode.")
            emails = generate_sample_emails(limit)
        else:
            provider = IMAPProvider(host=host, user=user, password=password, port=port)
            try:
                emails = provider.fetch_emails(query=query, limit=limit)
            finally:
                provider.disconnect()

    elif provider_name == "gmail":
        token = gmail_token or os.getenv("GMAIL_TOKEN", "secrets/token.json")
        try:
            provider = GmailProvider(credentials_path=token)
            emails = provider.fetch_emails(query=query, limit=limit)
        except Exception as exc:
            print(f"Gmail collection failed: {exc}. Falling back to sample mode.")
            emails = generate_sample_emails(limit)

    else:
        raise ValueError(f"Unknown provider: {provider_name}")

    print(f"Retrieved {len(emails)} emails.")

    # Save to JSONL
    scrubber = EmailScrubber() if scrub else None
    count = 0
    with open(out_file, "w", encoding="utf-8") as f:
        for em in emails:
            raw_input = f"From: {em.get('sender', '')}\nSubject: {em.get('subject', '')}\nBody: {em.get('body', '')}"
            clean_input = scrubber.scrub(raw_input) if scrubber else raw_input
            entry = {
                "instruction": "Classify this email based on its content (e.g., ACTION, NEWSLETTER, SPAM, PERSONAL).",
                "input": clean_input,
                "output": em.get("classification", "UNKNOWN")
            }
            f.write(json.dumps(entry) + "\n")
            count += 1

    print(f"Saved {count} records to {out_file} (PII scrubbed: {scrub}).")
    return count


def main():
    parser = argparse.ArgumentParser(description="Email Collector for LoRA Fine-tuning")
    parser.add_argument("--provider", choices=["sample", "imap", "gmail"], default="sample", help="Email ingestion source")
    parser.add_argument("--query", default="ALL", help="Search query (e.g., 'ALL', 'is:unread')")
    parser.add_argument("--limit", type=int, default=10, help="Max emails to fetch")
    parser.add_argument("--output", default="data/raw_emails.jsonl", help="Output JSONL path")
    parser.add_argument("--no-scrub", action="store_true", help="Disable automatic PII scrubbing")
    parser.add_argument("--host", help="IMAP server hostname")
    parser.add_argument("--user", help="IMAP username/email")
    parser.add_argument("--password", help="IMAP password")
    parser.add_argument("--port", type=int, default=993, help="IMAP port")

    args = parser.parse_args()

    run_collection(
        provider_name=args.provider,
        query=args.query,
        limit=args.limit,
        output_path=args.output,
        scrub=not args.no_scrub,
        imap_host=args.host,
        imap_user=args.user,
        imap_pass=args.password,
        imap_port=args.port
    )


if __name__ == "__main__":
    main()
