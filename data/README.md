# Raw Evaluation Data

Nine CSV files, one per agent-language combination, containing the evaluation results for all 300 projects.

## Files

| File | Agent | Language | Rows |
|------|-------|----------|------|
| `claude_python_reproducibility_analysis.csv` | Claude | Python | 40 |
| `claude_javascript_reproducibility_analysis.csv` | Claude | JavaScript | 35 |
| `claude_java_reproducibility_analysis.csv` | Claude | Java | 25 |
| `codex_python_reproducibility_analysis.csv` | Codex | Python | 40 |
| `codex_javascript_reproducibility_analysis.csv` | Codex | JavaScript | 35 |
| `codex_java_reproducibility_analysis.csv` | Codex | Java | 25 |
| `gemini_python_reproducibility_analysis.csv` | Gemini | Python | 40 |
| `gemini_javascript_reproducibility_analysis.csv` | Gemini | JavaScript | 35 |
| `gemini_java_reproducibility_analysis.csv` | Gemini | Java | 25 |

**Total: 300 project evaluations**

## CSV Schema (20 columns)

| Column | Type | Description |
|--------|------|-------------|
| `prompt_id` | string | Prompt identifier (1-100 or p_1-p_100) |
| `prompt_text` | string | Brief task description |
| `llm_name` | string | Agent name (claude / codex / gemini) |
| `language` | string | Programming language (python / javascript / java) |
| `project_path` | string | Path on evaluation server |
| `script_file` | string | Main source file name |
| `requirements_file` | string | Dependency file name |
| `claimed_deps` | string | Comma-separated list of declared dependencies |
| `claimed_count` | int | Number of declared dependencies |
| `working_deps` | string | Dependencies after manual fixes |
| `working_count` | int | Number of working dependencies |
| `runtime_deps` | string | Packages found at runtime |
| `runtime_count` | int | Total transitive packages installed (from Docker) |
| `execution_success` | bool/string | true / partial / false |
| `error_type` | string | Error classification (CodeBug, ConfigError, etc.) |
| `error_message` | string | Detailed error description |
| `completeness_gap` | int | Number of missing dependencies |
| `precision_gap` | int | Number of unnecessary dependencies |
| `runtime_gap` | int | runtime_count - claimed_count |
| `notes` | string | Evaluation notes and observations |

## Transitive Dependency Counting

The `runtime_count` values were obtained by running each project in a **fresh Docker container** with zero cached dependencies:

- **Python**: `pip install -r requirements.txt && pip list --format=freeze | wc -l` in `python:3.10-slim`
- **JavaScript**: `npm install && npm list --all --parseable | wc -l` in `node:18-slim`
- **Java**: `mvn dependency:tree | grep artifact-lines | wc -l` in `maven:3.9-eclipse-temurin-17`
