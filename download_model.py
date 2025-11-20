#!/usr/bin/env python3
"""
Download Qwen3-Embedding model for Meeting Value Estimator
"""

import sys
from pathlib import Path

try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("❌ huggingface_hub not found. Please run 'pip install -r requirements.txt' first.")
    sys.exit(1)

MODEL_ID = "Qwen/Qwen3-Embedding-0.6B"
MODEL_DIR = Path("models/qwen3-embedding")

def download_model():
    if MODEL_DIR.exists() and (MODEL_DIR / "config.json").exists():
        print(f"✅ Model already exists at {MODEL_DIR}")
        return

    print(f"⬇️ Downloading {MODEL_ID} to {MODEL_DIR}...")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    try:
        snapshot_download(repo_id=MODEL_ID, local_dir=MODEL_DIR)
        print("✅ Model downloaded successfully!")
    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_model()
