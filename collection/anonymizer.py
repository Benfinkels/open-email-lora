import re
import json

class EmailScrubber:
    """
    Scrubs PII (Personally Identifiable Information) from email text.
    """
    def __init__(self):
        self.email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
        self.phone_regex = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
        self.url_regex = re.compile(r'https?://\S+')

    def scrub(self, text):
        if not text:
            return ""
        
        # Replace Emails
        text = self.email_regex.sub("[EMAIL]", text)
        
        # Replace Phones
        text = self.phone_regex.sub("[PHONE]", text)
        
        # Replace URLs
        text = self.url_regex.sub("[URL]", text)
        
        return text

def scrub_jsonl(input_path, output_path):
    scrubber = EmailScrubber()
    print(f"--- [SCRUBBING PII: {input_path} -> {output_path}] ---")
    
    with open(input_path, "r") as f_in, open(output_path, "w") as f_out:
        for line in f_in:
            data = json.loads(line)
            data["input"] = scrubber.scrub(data.get("input", ""))
            f_out.write(json.dumps(data) + "\n")

if __name__ == "__main__":
    # Test with dummy data
    test_input = "Hello Ben, call me at 555-0199 or email me at test@example.com"
    scrubber = EmailScrubber()
    print(f"Original: {test_input}")
    print(f"Scrubbed: {scrubber.scrub(test_input)}")
