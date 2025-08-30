#!/usr/bin/env python3
"""
Download models from Huggingface and prepare them for Ollama
"""
import os
import subprocess
import logging
from pathlib import Path
from huggingface_hub import snapshot_download

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_hf_model(model_name: str, local_dir: Path):
    """Download model from Huggingface"""
    try:
        logger.info(f"Downloading {model_name} from Huggingface...")
        local_dir.mkdir(parents=True, exist_ok=True)
        
        snapshot_download(
            repo_id=model_name,
            local_dir=str(local_dir),
            local_dir_use_symlinks=False,
            resume_download=True,
            ignore_patterns=["*.md", "*.txt", ".gitattributes"]
        )
        logger.info(f"Successfully downloaded {model_name} to {local_dir}")
        return True
    except Exception as e:
        logger.error(f"Failed to download {model_name}: {e}")
        return False

def create_ollama_modelfile(model_path: Path, model_name: str):
    """Create Modelfile for Ollama import"""
    modelfile_path = model_path / "Modelfile"
    
    # Check for GGUF files first (Ollama prefers these)
    gguf_files = list(model_path.glob("*.gguf"))
    if gguf_files:
        model_file = gguf_files[0]
        logger.info(f"Found GGUF file: {model_file}")
    else:
        # Look for safetensors or bin files
        safetensor_files = list(model_path.glob("*.safetensors"))
        bin_files = list(model_path.glob("*.bin"))
        
        if safetensor_files:
            logger.info("Found safetensors files - will need conversion to GGUF")
            # For now, we'll create a basic Modelfile
            model_file = model_path
        elif bin_files:
            logger.info("Found bin files - will need conversion to GGUF")
            model_file = model_path
        else:
            logger.error("No model files found")
            return None
    
    # Create basic Modelfile
    modelfile_content = f"""FROM {model_file}

# Model parameters
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096

# System prompt
SYSTEM You are a helpful AI assistant.
"""
    
    with open(modelfile_path, 'w') as f:
        f.write(modelfile_content)
    
    logger.info(f"Created Modelfile at {modelfile_path}")
    return modelfile_path

def import_to_ollama(modelfile_path: Path, ollama_name: str):
    """Import model to Ollama"""
    try:
        logger.info(f"Creating Ollama model '{ollama_name}'...")
        result = subprocess.run(
            ["ollama", "create", ollama_name, "-f", str(modelfile_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully created Ollama model '{ollama_name}'")
            return True
        else:
            logger.error(f"Failed to create Ollama model: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error importing to Ollama: {e}")
        return False

def main():
    # Models to download and import
    models = [
        {
            "hf_name": "openai/gpt-oss-20b",
            "local_dir": Path("models/gpt-oss-20b"),
            "ollama_name": "gpt-oss-20b"
        },
        {
            "hf_name": "openai/gpt-oss-120b", 
            "local_dir": Path("models/gpt-oss-120b"),
            "ollama_name": "gpt-oss-120b"
        }
    ]
    
    for model_info in models:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {model_info['hf_name']}")
        logger.info(f"{'='*60}")
        
        # Check if already downloaded
        if model_info["local_dir"].exists() and any(model_info["local_dir"].iterdir()):
            logger.info(f"Model already downloaded at {model_info['local_dir']}")
        else:
            # Download from Huggingface
            success = download_hf_model(model_info["hf_name"], model_info["local_dir"])
            if not success:
                logger.error(f"Skipping {model_info['hf_name']} due to download failure")
                continue
        
        # Note: Direct import of non-GGUF models to Ollama requires conversion
        # For now, we'll note this limitation
        logger.warning(f"Note: {model_info['hf_name']} uses custom architecture.")
        logger.warning("Direct import to Ollama requires GGUF format.")
        logger.warning("Consider using llama.cpp to convert the model first.")
        
        # List downloaded files
        logger.info(f"\nDownloaded files in {model_info['local_dir']}:")
        for file in model_info["local_dir"].glob("*"):
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                logger.info(f"  - {file.name}: {size_mb:.2f} MB")

if __name__ == "__main__":
    main()