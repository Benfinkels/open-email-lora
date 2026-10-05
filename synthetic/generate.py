import json
import os
import random
import re
import argparse
from pathlib import Path
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "phi4-mini")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "data/synthetic_emails.jsonl")

PROMPT_TEMPLATE = """You are an email generator for an instruction-tuning dataset.
Generate a realistic email from a {role} discussing {topic}.
Tone: {tone}.

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "instruction": "Classify this email based on its content (e.g., ACTION, NEWSLETTER, SPAM, PERSONAL).",
  "input": "From: <name>\\nSubject: <subject>\\nBody: <body text>",
  "output": "{classification}"
}}"""


def clean_json_text(text: str) -> dict | None:
    """Extract and parse JSON object from LLM response text."""
    if not text:
        return None
    # Strip markdown code blocks if present
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        # Try finding outer braces
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start : end + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def generate_synthetic_email(role: str, topic: str, tone: str, classification: str, url: str, model: str, mock: bool = False) -> dict:
    if mock:
        return {
            "instruction": "Classify this email based on its content (e.g., ACTION, NEWSLETTER, SPAM, PERSONAL).",
            "input": f"From: {role.lower().replace(' ', '.')}@example.com\nSubject: Update regarding {topic}\nBody: Hi there,\nThis is a {tone.lower()} note concerning {topic.lower()}. Please review when possible.\nBest,\n{role}",
            "output": classification
        }

    prompt = PROMPT_TEMPLATE.format(role=role, topic=topic, tone=tone, classification=classification)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        resp = requests.post(url, json=payload, timeout=60)
        if resp.status_code == 200:
            raw_response = resp.json().get("response", "")
            parsed = clean_json_text(raw_response)
            if parsed:
                return parsed
    except Exception as exc:
        print(f"  [Notice] Ollama generation failed: {exc}. Using fallback template.")

    # Fallback template if Ollama fails or format was invalid
    return {
        "instruction": "Classify this email based on its content (e.g., ACTION, NEWSLETTER, SPAM, PERSONAL).",
        "input": f"From: {role.lower().replace(' ', '.')}@domain.net\nSubject: Regarding {topic}\nBody: Hi,\nPlease find the latest details on {topic.lower()}.\nRegards,\n{role}",
        "output": classification
    }


def run_generation(count: int = 5, output_file: str = OUTPUT_FILE, model: str = MODEL, url: str = OLLAMA_URL, mock: bool = False) -> int:
    roles = ["Engineering Manager", "Product Lead", "Security Bot", "Recruiter", "Vendor", "College Friend"]
    topics = ["Sprint planning", "Q4 Roadmap", "Password expiration warning", "Staff AI position", "Invoice payment", "Dinner meetup"]
    tones = ["Urgent", "Professional", "Informative", "Friendly"]

    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"--- [SYNTHETIC DATA GENERATION: count={count}, model={model}, mock={mock}] ---")
    generated_count = 0

    with open(out_path, "a", encoding="utf-8") as f:
        for i in range(count):
            role = random.choice(roles)
            topic = random.choice(topics)
            tone = random.choice(tones)
            classification = "ACTION" if role in ["Engineering Manager", "Security Bot", "Vendor"] else ("PERSONAL" if role == "College Friend" else "INFO")

            entry = generate_synthetic_email(role, topic, tone, classification, url=url, model=model, mock=mock)
            f.write(json.dumps(entry) + "\n")
            generated_count += 1
            print(f"  [{generated_count}/{count}] Generated: {role} -> {topic} ({classification})")

    print(f"Generated {generated_count} synthetic samples to {out_path}.")
    return generated_count


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic emails for LoRA fine-tuning")
    parser.add_argument("--count", type=int, default=5, help="Number of emails to generate")
    parser.add_argument("--output", default=OUTPUT_FILE, help="Output JSONL path")
    parser.add_argument("--model", default=MODEL, help="Ollama model name")
    parser.add_argument("--url", default=OLLAMA_URL, help="Ollama generate URL")
    parser.add_argument("--mock", action="store_true", help="Generate synthetic samples offline without LLM")

    args = parser.parse_args()
    run_generation(count=args.count, output_file=args.output, model=args.model, url=args.url, mock=args.mock)


if __name__ == "__main__":
    main()
