#!/usr/bin/env python3
"""
Download GPT-OSS models directly from HuggingFace
"""
import os
from huggingface_hub import snapshot_download
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_model(model_name, local_dir):
    """Download model files from HuggingFace"""
    try:
        logger.info(f"Downloading {model_name} to {local_dir}...")
        os.makedirs(local_dir, exist_ok=True)
        
        # Download all model files
        snapshot_download(
            repo_id=model_name,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        logger.info(f"Successfully downloaded {model_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to download {model_name}: {e}")
        return False

if __name__ == "__main__":
    models_to_download = [
        ("openai/gpt-oss-20b", "models/openai_gpt-oss-20b"),
        ("openai/gpt-oss-120b", "models/openai_gpt-oss-120b")
    ]
    
    for model_name, local_dir in models_to_download:
        success = download_model(model_name, local_dir)
        if success:
            logger.info(f"✓ {model_name} downloaded to {local_dir}")
        else:
            logger.error(f"✗ Failed to download {model_name}")