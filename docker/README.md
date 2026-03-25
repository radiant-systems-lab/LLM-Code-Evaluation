# Docker Evaluation Environment

Dockerfiles and scripts used to evaluate transitive dependencies in isolated containers.

## Images

| Dockerfile | Base Image | Purpose |
|-----------|-----------|---------|
| `Dockerfile.python` | `python:3.10-slim` | Python project evaluation |
| `Dockerfile.javascript` | `node:18-slim` | JavaScript/Node.js project evaluation |
| `Dockerfile.java` | `maven:3.9-eclipse-temurin-17` | Java/Maven project evaluation |

Each container starts with **zero cached dependencies**, ensuring accurate transitive counts.

## Running the Evaluation

```bash
# From the repository root
chmod +x docker/run_evaluation.sh
./docker/run_evaluation.sh
```

This will:
1. Build three Docker images (one per language)
2. For each of the 300 projects, spin up a **fresh container**
3. Install only the claimed dependencies
4. Count the total transitive packages installed
5. Save results to `docker/results/`

### Per-language methodology

| Language | Install Command | Count Command |
|----------|----------------|---------------|
| Python | `pip install -r requirements.txt` | `pip list --format=freeze \| wc -l` |
| JavaScript | `npm install` | `npm list --all --parseable \| wc -l` |
| Java | `mvn dependency:resolve` | `mvn dependency:tree \| grep artifact-lines` |

## Requirements

- Docker 20.10+
- ~5GB disk space for images
- ~2 hours runtime for all 300 projects

## Why Docker?

Using fresh containers for each project ensures:
- No cached packages from previous installs
- No OS-level library contamination
- Consistent Node.js/Python/Java versions across all evaluations
- Reproducible transitive dependency counts regardless of host environment
