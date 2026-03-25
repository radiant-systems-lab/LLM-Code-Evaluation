

### Artifact Available
- All source code, data, and analysis scripts are publicly available in this repository.
- Raw evaluation data: 9 CSV files covering 300 projects across 3 agents and 3 languages.
- Generated code: complete output from all 3 AI coding agents for all 100 prompts.
- Analysis: single Python script (`analysis/regenerate_all.py`) regenerates all 6 figures and 6 tables.

### Artifact Functional
- **Reproduction steps**: `pip install -r requirements.txt && cd analysis && python regenerate_all.py`
- **Expected output**: 6 figures (PNG + PDF) in `analysis/figures/`, 6 tables (CSV) in `analysis/tables/`, key statistics on stdout.
- **Runtime**: < 10 seconds on any modern machine.
- **Dependencies**: Python 3.10+, pandas, numpy, matplotlib (specified in `requirements.txt`).

### Artifact Reusable
- Raw CSV data can be independently analyzed with any tool (R, Excel, etc.).
- The 300 generated projects can be re-evaluated in Docker containers.
- Prompts can be reused to evaluate new AI coding agents.
- The `regenerate_all.py` script is self-contained and documented.

## Evaluation Environment

The original evaluation used:
- **OS**: Ubuntu 22.04 on AWS EC2 (c5.2xlarge)
- **Docker images**: `python:3.10-slim`, `node:18-slim`, `maven:3.9-eclipse-temurin-17`
- **Isolation**: Each project evaluated in a fresh container with no cached dependencies inside each fresh ubunutu instance
