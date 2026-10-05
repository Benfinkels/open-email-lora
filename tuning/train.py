import argparse
import os
import subprocess
import sys
from pathlib import Path
import yaml

DEFAULT_CONFIG = {
    "model": "unsloth/gemma-4-E4B-it-unsloth-bnb-4bit",
    "dataset_path": "data/dataset.jsonl",
    "output_dir": "outputs/lora_adapter",
    "epochs": 3,
    "learning_rate": 2e-4,
    "batch_size": 2,
    "bf16": True,
}


def load_config(path: str = "config.yaml") -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            user_cfg = yaml.safe_load(f) or {}
            cfg = DEFAULT_CONFIG.copy()
            cfg.update(user_cfg)
            return cfg
    return DEFAULT_CONFIG.copy()


def run_training(config: dict, dry_run: bool = False):
    """
    Executes Unsloth LoRA fine-tuning with provided configuration.
    """
    print(f"--- [INITIALIZING LoRA TRAINING: {config['model']}] ---")
    print(f"Dataset:       {config['dataset_path']}")
    print(f"Output:        {config['output_dir']}")
    print(f"Epochs:        {config['epochs']}")
    print(f"Learning Rate: {config['learning_rate']}")
    print(f"Batch Size:    {config['batch_size']}")

    dataset_path = Path(config["dataset_path"])
    if not dataset_path.exists() and not dry_run:
        raise FileNotFoundError(
            f"Dataset not found at '{dataset_path}'. "
            "Run `python collection/collector.py` or `python synthetic/generate.py` to create your training data."
        )

    # Ensure output directory exists
    Path(config["output_dir"]).mkdir(parents=True, exist_ok=True)

    cmd = [
        "unsloth", "train",
        "--model", str(config["model"]),
        "--local-dataset", str(config["dataset_path"]),
        "--output-dir", str(config["output_dir"]),
        "--num-epochs", str(config["epochs"]),
        "--learning-rate", str(config["learning_rate"]),
        "--batch-size", str(config["batch_size"]),
        "--bf16", "true" if config.get("bf16") else "false"
    ]

    print(f"Command: {' '.join(cmd)}")

    if dry_run:
        print("[DRY RUN] Configuration validated successfully. Skipping GPU execution.")
        return 0

    try:
        subprocess.run(cmd, check=True)
        print("SUCCESS: Fine-tuning completed successfully.")
        return 0
    except FileNotFoundError:
        print(
            "ERROR: 'unsloth' CLI not found. Please install tuning dependencies:\n"
            "pip install -r tuning/requirements.txt\n"
            "Note: Unsloth requires an NVIDIA GPU with CUDA support.",
            file=sys.stderr
        )
        return 1
    except subprocess.CalledProcessError as e:
        print(f"FAILURE: Training failed with error code {e.returncode}", file=sys.stderr)
        return e.returncode


def main():
    parser = argparse.ArgumentParser(description="LoRA Fine-tuning Trainer for Open Email Classifier")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--dataset", help="Override dataset path")
    parser.add_argument("--output", help="Override output directory")
    parser.add_argument("--epochs", type=int, help="Override epochs")
    parser.add_argument("--dry-run", action="store_true", help="Validate config without launching GPU training")

    args = parser.parse_args()

    config = load_config(args.config)
    if args.dataset:
        config["dataset_path"] = args.dataset
    if args.output:
        config["output_dir"] = args.output
    if args.epochs:
        config["epochs"] = args.epochs

    # Write default config if not present
    if not os.path.exists(args.config):
        with open(args.config, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False)
        print(f"Created default configuration at {args.config}")

    sys.exit(run_training(config, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
