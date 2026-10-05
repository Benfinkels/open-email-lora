import json
from collection.anonymizer import EmailScrubber, scrub_jsonl


def test_scrubber_emails():
    scrubber = EmailScrubber()
    text = "Contact alice.smith@work-place.org or bob+extra@gmail.com."
    result = scrubber.scrub(text)
    assert "alice.smith@work-place.org" not in result
    assert "bob+extra@gmail.com" not in result
    assert "[EMAIL]" in result


def test_scrubber_phone_numbers():
    scrubber = EmailScrubber()
    cases = [
        "Call me at (555) 123-4567 today.",
        "My desk is 555-987-6543.",
        "Cell: 555.234.5678",
        "Direct: +1-555-876-5432"
    ]
    for case in cases:
        result = scrubber.scrub(case)
        assert "[PHONE]" in result


def test_scrubber_urls_and_ips():
    scrubber = EmailScrubber()
    text = "Visit https://app.internal.domain/dashboard?user=123 or check server 192.168.1.50."
    result = scrubber.scrub(text)
    assert "[URL]" in result
    assert "[IP_ADDRESS]" in result
    assert "https://" not in result
    assert "192.168.1.50" not in result


def test_scrubber_ssn_and_credit_card():
    scrubber = EmailScrubber()
    text = "SSN: 000-12-3456 and Card: 4111 2222 3333 4444"
    result = scrubber.scrub(text)
    assert "[SSN]" in result
    assert "[CREDIT_CARD]" in result
    assert "000-12-3456" not in result


def test_scrub_jsonl(tmp_path):
    in_file = tmp_path / "raw.jsonl"
    out_file = tmp_path / "clean.jsonl"

    data = [
        {"instruction": "Classify", "input": "Call 555-111-2222 or email test@corp.io", "output": "ACTION"},
        {"instruction": "Classify", "input": "No sensitive data here.", "output": "INFO"}
    ]
    with open(in_file, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

    count = scrub_jsonl(str(in_file), str(out_file))
    assert count == 2

    with open(out_file, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]
    assert "[PHONE]" in lines[0]["input"]
    assert "[EMAIL]" in lines[0]["input"]
    assert lines[1]["input"] == "No sensitive data here."
