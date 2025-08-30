# Example Scripts

This directory contains sample Python scripts to test the dependency managers with.

## Available Scripts

### script1.py - Data Analysis
- **Purpose**: Demonstrates data analysis with pandas and visualization
- **Libraries used**: pandas, numpy, matplotlib
- **Output**: analysis_results.png
- **Use case**: Testing data science dependency detection

### script2.py - Web Scraping & Text Processing  
- **Purpose**: Web requests and basic text analysis
- **Libraries used**: requests, beautifulsoup4, nltk, collections, json
- **Output**: text_analysis_results.json
- **Use case**: Testing web scraping dependency detection

### script3.py - Machine Learning
- **Purpose**: Basic machine learning model training
- **Libraries used**: scikit-learn, joblib, numpy, json
- **Output**: trained_model.pkl, model_results.json
- **Use case**: Testing ML dependency detection

## How to Use with Dependency Managers

### Test with Traditional Manager:
```bash
# Single script
python dependency_manager_main.py examples/script1.py

# Multiple scripts
python dependency_manager_main.py examples/script1.py examples/script2.py examples/script3.py --combined

# Install and execute
python dependency_manager_main.py examples/script1.py --install --execute
```

### Test with Ollama Manager:
```bash
# Single script
python ollama_dependency_manager.py examples/script1.py --model "gpt-oss-20b"

# Multiple scripts with execution
python ollama_dependency_manager.py examples/script1.py examples/script2.py examples/script3.py --install --execute

# Generate combined requirements
python ollama_dependency_manager.py examples/*.py --combined
```

## Expected Outputs

Each script will generate:
1. **Requirements file**: Based on detected dependencies
2. **Script output**: Results from script execution (if --execute flag used)
3. **Generated files**: Each script creates output files for verification

## Notes

- These scripts use common libraries to test dependency detection
- Some libraries may not be pre-installed - this is intentional for testing
- Generated requirements.txt files will show detected dependencies
- Use these to compare traditional vs Ollama dependency manager performance