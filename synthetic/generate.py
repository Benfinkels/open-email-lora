import json
import os
import requests
import random

# CONFIG
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi4:mini"
OUTPUT_FILE = "synthetic_emails.jsonl"

PROMPT_TEMPLATE = """
Generate a realistic email for a fine-tuning dataset.
The email should be from a {role} and discuss {topic}.
Include realistic headers (From, Subject, Date).
The content should be {tone}.

Format the output as a JSON object with:
"instruction": "Classify this email or summarize it",
"input": "Full email text",
"output": "{classification}"
"""

def generate_email(role, topic, tone, classification):
    prompt = PROMPT_TEMPLATE.format(role=role, topic=topic, tone=tone, classification=classification)
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        return response.json().get('response', '')
    except Exception as e:
        return f"Error: {e}"

def main():
    roles = ["Boss", "Coworker", "Spam Bot", "Recruiter", "Friend"]
    topics = ["Project deadline", "Lunch plans", "Win a free iPhone", "Job opportunity", "Family reunion"]
    tones = ["Professional", "Casual", "Aggressive", "Urgent"]
    
    print(f"--- [STARTING SYNTHETIC DATA GENERATION: {MODEL}] ---")
    
    with open(OUTPUT_FILE, "a") as f:
        for _ in range(5): # Generate a small sample
            role = random.choice(roles)
            topic = random.choice(topics)
            tone = random.choice(tones)
            classification = "ACTION" if role in ["Boss", "Recruiter"] else "IGNORE"
            
            email_data = generate_email(role, topic, tone, classification)
            f.write(email_data + "\n")
            print(f"Generated: {role} -> {topic}")

if __name__ == "__main__":
    main()
