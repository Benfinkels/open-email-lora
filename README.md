# Open Email LoRA: Personal Email Classification with LoRA & Gemma

A modular, end-to-end framework for building private, personalized email classification models using Low-Rank Adaptation (LoRA), **Gemma 4**, **Unsloth**, and **Ollama**.

From raw inbox ingestion and automatic PII sanitization to parameter-efficient fine-tuning and a production inference API.

---

## Architecture Overview

The system consists of four modular components:

```
[ Email Ingestion ]                [ Data Augmentation ]
  IMAP / Gmail                       Ollama (phi4-mini)
        │                                    │
        ▼                                    ▼
[ PII Anonymizer ]                  [ Synthetic Pairs ]
 (scrubs email, phone, SSN, etc.)            │
        │                                    │
        └──────────────────┬─────────────────┘
                           │
                           ▼
                 [ Training Dataset ]
                    (data/*.jsonl)
                           │
                           ▼
                  [ LoRA Fine-Tuning ]
                  (Unsloth / Gemma 4)
                           │
                           ▼
                   [ Adapter Weights ]
                           │
                           ▼
                  [ Inference Server ]
                 (FastAPI REST Oracle)
```

### 1. Collection (`collection/`)
- **IMAP Provider (`imap_provider.py`)**: Connects securely to standard mail providers (Outlook, iCloud, Yahoo, Fastmail).
- **Gmail Provider (`gmail_provider.py`)**: OAuth2-authenticated Gmail ingestion.
- **Sample Mode**: Bundled synthetic scenario generator for rapid local development without live credentials.
- **PII Anonymization (`anonymizer.py`)**: Automatically sanitizes emails, phone numbers, URLs, IP addresses, SSNs, and credit cards before data ever reaches a model or disk.

### 2. Synthetic Data (`synthetic/`)
- Generates realistic training examples using Ollama (`phi4-mini`) or deterministic mock generation.
- Balances class distributions (e.g. `ACTION`, `NEWSLETTER`, `SPAM`, `PERSONAL`).

### 3. Tuning (`tuning/`)
- **Unsloth Integration (`train.py`)**: Fast 4-bit / 16-bit LoRA fine-tuning for Gemma 4.
- **Config-Driven**: Experiments and hyperparameters managed via `config.yaml`.
- Includes validation and `--dry-run` modes for non-GPU verification.

### 4. Runtime (`runtime/`)
- **FastAPI Oracle (`api.py`)**: Real-time REST API endpoint (`/classify`) for email categorization.
- Health inspection (`/health`) and metadata (`/info`).
- Non-destructive inference (evaluates content without mutating emails).

---

## Quickstart

### 1. Prerequisites
- Python 3.10+
- (Optional for training) NVIDIA GPU with CUDA for Unsloth
- (Optional for synthetic/local inference) [Ollama](https://ollama.com/)

### 2. Installation
```bash
git clone https://github.com/Benfinkels/open-email-lora.git
cd open-email-lora

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Collect & Anonymize Emails
Generate sample training records offline:
```bash
python collection/collector.py --provider sample --limit 25 --output data/dataset.jsonl
```
Or collect from your personal IMAP mailbox:
```bash
python collection/collector.py --provider imap --host imap.mail.me.com --user you@icloud.com --password app-password --limit 200 --output data/dataset.jsonl
```

### 4. Augment with Synthetic Emails
```bash
# With Ollama running:
python synthetic/generate.py --count 20 --output data/dataset.jsonl

# Offline mock mode:
python synthetic/generate.py --mock --count 20 --output data/dataset.jsonl
```

### 5. Fine-Tune the Model (GPU)
```bash
# Verify configuration:
python tuning/train.py --dry-run

# Run full fine-tuning (requires GPU & Unsloth):
pip install -r tuning/requirements.txt
python tuning/train.py
```

### 6. Run the Inference API
```bash
python runtime/api.py
```
Or with uvicorn:
```bash
uvicorn runtime.api:app --host 0.0.0.0 --port 8050
```

Test classification via cURL:
```bash
curl -X POST http://localhost:8050/classify \
  -H "Content-Type: application/json" \
  -d '{"sender": "boss@corp.com", "subject": "Review requested", "body": "Please review the Q3 budget spreadsheet today."}'
```

---

## Running Tests

Run the unit test suite:
```bash
pytest
```

---

## Docker Deployment

To launch the inference oracle using Docker Compose:
```bash
docker-compose up oracle
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
