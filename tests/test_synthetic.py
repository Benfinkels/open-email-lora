import json
from synthetic.generate import clean_json_text, run_generation


def test_clean_json_text():
    raw_markdown = 'Here is the generated output:\n```json\n{"instruction": "Classify", "input": "Hello", "output": "ACTION"}\n```\nHope that helps!'
    parsed = clean_json_text(raw_markdown)
    assert parsed is not None
    assert parsed["output"] == "ACTION"

    raw_plain = '{"instruction": "Classify", "input": "Meeting update", "output": "INFO"}'
    parsed_plain = clean_json_text(raw_plain)
    assert parsed_plain is not None
    assert parsed_plain["output"] == "INFO"

    invalid = "Not a json response"
    assert clean_json_text(invalid) is None


def test_run_generation_mock(tmp_path):
    out_file = tmp_path / "synthetic.jsonl"
    count = run_generation(count=4, output_file=str(out_file), mock=True)
    assert count == 4
    assert out_file.exists()

    with open(out_file, "r", encoding="utf-8") as f:
        items = [json.loads(line) for line in f]
    assert len(items) == 4
    for item in items:
        assert "instruction" in item
        assert "input" in item
        assert "output" in item
