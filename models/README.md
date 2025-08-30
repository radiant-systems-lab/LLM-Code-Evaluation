# Models Directory

This directory will store downloaded language models after you run the download scripts.

## How to Download Models

### Method 1: Using the Download Script (Recommended)
```bash
# Downloads both gpt-oss-20b and gpt-oss-120b
python import_hf_to_ollama.py
```

### Method 2: Manual Download
```bash
# For individual models
python -c "
from huggingface_hub import snapshot_download
snapshot_download('openai/gpt-oss-20b', local_dir='models/gpt-oss-20b')
snapshot_download('openai/gpt-oss-120b', local_dir='models/gpt-oss-120b')
"
```

## After Download, Directory Structure Will Be:
```
models/
├── gpt-oss-20b/          # 20B parameter model files (~13GB)
├── gpt-oss-120b/         # 120B parameter model files (~240GB)
└── README.md             # This file
```

## Model Sizes:
- **gpt-oss-20b**: ~13GB (20 billion parameters)
- **gpt-oss-120b**: ~240GB (120 billion parameters)

## Important Notes:
- Models are downloaded once and cached locally
- Large storage space required (especially for 120B model)
- Download time depends on internet connection
- Models are not included in git repository to save space