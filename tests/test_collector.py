import json
from pathlib import Path
from collection.collector import generate_sample_emails, run_collection


def test_generate_sample_emails():
    samples = generate_sample_emails(limit=5)
    assert len(samples) == 5
    for s in samples:
        assert "sender" in s
        assert "subject" in s
        assert "body" in s
        assert "classification" in s


def test_run_collection_sample_mode(tmp_path):
    out_file = tmp_path / "emails.jsonl"
    count = run_collection(
        provider_name="sample",
        limit=3,
        output_path=str(out_file),
        scrub=True
    )
    assert count == 3
    assert out_file.exists()

    with open(out_file, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]

    assert len(records) == 3
    for rec in records:
        assert "instruction" in rec
        assert "input" in rec
        assert "output" in rec
        # Verify PII scrubbing on sample emails
        assert "[PHONE]" in rec["input"] or "[URL]" in rec["input"] or "@" not in rec["input"]
