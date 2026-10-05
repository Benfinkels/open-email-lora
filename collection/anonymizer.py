import re
import json
from pathlib import Path


class EmailScrubber:
    """
    Scrubs Personally Identifiable Information (PII) from email text,
    including email addresses, phone numbers, URLs, IP addresses,
    Social Security Numbers (SSNs), and credit card numbers.
    """
    def __init__(self):
        self.email_regex = re.compile(
            r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        )
        self.phone_regex = re.compile(
            r'(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b'
        )
        self.url_regex = re.compile(
            r'https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_+.~#?&/=]*'
        )
        self.ip_regex = re.compile(
            r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        )
        self.ssn_regex = re.compile(
            r'\b\d{3}-\d{2}-\d{4}\b'
        )
        self.cc_regex = re.compile(
            r'\b(?:\d{4}[ -]?){3}\d{4}\b'
        )

    def scrub(self, text: str) -> str:
        if not text:
            return ""

        # Replace URLs first so embedded emails or IPs in params are handled cleanly
        text = self.url_regex.sub("[URL]", text)
        # Replace Emails
        text = self.email_regex.sub("[EMAIL]", text)
        # Replace SSNs before phone numbers
        text = self.ssn_regex.sub("[SSN]", text)
        # Replace Credit Cards
        text = self.cc_regex.sub("[CREDIT_CARD]", text)
        # Replace Phone numbers
        text = self.phone_regex.sub("[PHONE]", text)
        # Replace IP addresses
        text = self.ip_regex.sub("[IP_ADDRESS]", text)

        return text


def scrub_jsonl(input_path: str, output_path: str) -> int:
    """
    Reads an Unsloth-formatted JSONL file, scrubs all 'input' fields,
    and writes the scrubbed entries to output_path.
    Returns the count of scrubbed entries.
    """
    scrubber = EmailScrubber()
    count = 0
    in_file = Path(input_path)
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"--- [SCRUBBING PII: {in_file} -> {out_file}] ---")

    with open(in_file, "r", encoding="utf-8", errors="replace") as f_in, \
         open(out_file, "w", encoding="utf-8") as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if "input" in data:
                data["input"] = scrubber.scrub(data["input"])
            f_out.write(json.dumps(data) + "\n")
            count += 1

    print(f"Scrubbed {count} entries successfully.")
    return count


if __name__ == "__main__":
    test_input = "Hello Ben, call me at (555) 019-9482 or email test@example.com at 192.168.1.1 or visit https://antigravity.google.com"
    scrubber = EmailScrubber()
    print(f"Original: {test_input}")
    print(f"Scrubbed: {scrubber.scrub(test_input)}")
