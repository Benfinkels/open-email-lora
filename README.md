# Open Email LoRA: Telling openclaw which emails you will actually respond to

This project provides a comprehensive, modular framework for building personal email classification models using LoRA (Low-Rank Adaptation). It is designed to take you from raw inbox ingestion to a production-ready inference API using **Gemma 4** and **Unsloth**.

## Architecture Overview

The project is divided into four distinct modules, each responsible for a specific stage of the pipeline:

### 1. Collection (`collection/`)
Handles the ingestion and sanitization of email data.
- **IMAP Support:** `imap_provider.py` allows robust collection from any standard mail provider (Outlook, iCloud, etc.).
- **Anonymization:** `anonymizer.py` automatically scrubs PII (Emails, Phone Numbers, URLs) from your data before it ever touches a model.
- **Interface:** Built on a flexible `EmailProvider` base class for easy expansion.

### 2. Synthetic Data (`synthetic/`)
Bootstraps your training dataset with high-quality generated emails.
- Uses `phi4:mini` via Ollama to generate realistic email scenarios.
- Perfect for balanced classification when you have sparse data for specific categories.

### 3. Tuning (`tuning/`)
The core training engine.
- **Unsloth Integration:** Leverages Unsloth for 2x faster training and 70% less memory usage.
- **Gemma 4 Optimized:** Pre-configured for the latest Gemma models.
- **Configuration-Driven:** Control your experiments via `config.yaml`.

### 4. Runtime (`runtime/`)
A high-performance inference API.
- **FastAPI Oracle:** A REST API that takes raw email content and returns real-time classifications.
- **Dockerized:** Ready for deployment as a microservice.

## Modular Docker Architecture

The project is fully containerized using a modular `docker-compose.yml` structure:
- **Collector:** Ephemeral service for data extraction.
- **Synthetic:** Generator service for data augmentation.
- **Tuner:** GPU-accelerated service for model training (requires NVIDIA Container Toolkit).
- **Oracle:** Persistent API service for model serving.

## Quick Start

1. **Setup Environment:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Collect Data:**
   Configure your IMAP credentials and run:
   ```bash
   python collection/collector.py --query "ALL" --limit 500
   ```

3. **Train Model:**
   ```bash
   python tuning/train.py
   ```

4. **Deploy API:**
   ```bash
   docker-compose up oracle
   ```

## Requirements

- Python 3.10+
- NVIDIA GPU (16GB+ VRAM recommended for training)
- Docker & Docker Compose
- Ollama (for synthetic generation and local serving)

## License
MIT
