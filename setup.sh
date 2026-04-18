#!/bin/bash

# Open Email LoRA Setup Script
# Creates directories and virtual environments for the modular pipeline.

set -e

echo "--- [INITIALIZING PROJECT STRUCTURE] ---"
mkdir -p data outputs

echo "--- [SETTING UP VIRTUAL ENVIRONMENTS] ---"

# 1. Collection & Synthetic Venv
if [ ! -d "venv-collection" ]; then
    echo "Installing Collection & Synthetic environment..."
    python3 -m venv venv-collection
    source venv-collection/bin/activate
    pip install --upgrade pip
    pip install -r collection/requirements.txt
    pip install -r synthetic/requirements.txt
    deactivate
fi

# 2. Tuning Venv (Unsloth/Torch)
if [ ! -d "venv-tuning" ]; then
    echo "Installing Tuning environment (this may take a while)..."
    python3 -m venv venv-tuning
    source venv-tuning/bin/activate
    pip install --upgrade pip
    pip install -r tuning/requirements.txt
    deactivate
fi

# 3. Runtime Venv (FastAPI)
if [ ! -d "venv-runtime" ]; then
    echo "Installing Runtime environment..."
    python3 -m venv venv-runtime
    source venv-runtime/bin/activate
    pip install --upgrade pip
    pip install -r runtime/requirements.txt
    deactivate
fi

echo "--- [SETUP COMPLETE] ---"
echo "To start collecting data: source venv-collection/bin/activate"
echo "To start training: source venv-tuning/bin/activate"
echo "To run the API: source venv-runtime/bin/activate"
