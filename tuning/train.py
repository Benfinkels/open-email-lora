import yaml
import os
import subprocess
from pathlib import Path

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def run_training(config):
    """
    Wraps the Unsloth CLI for a streamlined experience.
    """
    print(f"--- [INITIALIZING TRAINING: {config['model']}] ---")
    
    # We build the command based on the YAML config
    cmd = [
        "unsloth", "train",
        "--model", config["model"],
        "--local-dataset", config["dataset_path"],
        "--output-dir", config["output_dir"],
        "--num-epochs", str(config["epochs"]),
        "--learning-rate", str(config["learning_rate"]),
        "--batch-size", str(config["batch_size"]),
        "--bf16", "true" if config.get("bf16") else "false"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("SUCCESS: Training completed.")
    except subprocess.CalledProcessError as e:
        print(f"FAILURE: Training failed with error {e}")

if __name__ == "__main__":
    # In a real project, we'd add CLI args here
    sample_config = {
        "model": "unsloth/gemma-4-E4B-it-unsloth-bnb-4bit",
        "dataset_path": "data/dataset.jsonl",
        "output_dir": "outputs/lora_adapter",
        "epochs": 3,
        "learning_rate": 2e-4,
        "batch_size": 2,
        "bf16": True
    }
    
    if not os.path.exists("config.yaml"):
        with open("config.yaml", "w") as f:
            yaml.dump(sample_config, f)
            
    run_training(sample_config)
