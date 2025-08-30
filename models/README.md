# Models Directory

This directory stores downloaded language models for the dependency managers.

## Structure
```
models/
├── gpt-oss-20b/          # 20B parameter model files
├── gpt-oss-120b/         # 120B parameter model files
└── [other models]/
```

## Usage
Models are downloaded automatically when you run:
```bash
python import_hf_to_ollama.py
```

## Note
Model files are large (several GB each) and are not included in this repository.
Download them locally using the provided scripts.