#!/usr/bin/env python3
"""
LLaMA3 NRP API Dependency Analyzer
Uses LLaMA3 via NRP API to analyze Python code and extract ALL runtime dependencies
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Set
from openai import OpenAI
import re
import json
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class LLaMA3NRPAnalyzer:
    def __init__(self, api_key: str = "2KrDQlp6jRDIOuxqndLcZ2gaSiucYMQs"):
        """Initialize the LLaMA3 NRP API-based dependency analyzer"""
        self.api_key = api_key
        self.model = "llama3"  # Using LLaMA3 which works

        # Initialize OpenAI client with NRP endpoint
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://ellm.nrp-nautilus.io/v1"
        )

        logger.info(f"🚀 Initializing LLaMA3 NRP Dependency Analyzer")
        logger.info(f"📦 Model: {self.model}")
        logger.info(f"🌐 API Endpoint: https://ellm.nrp-nautilus.io")

        # Standard library modules to filter out
        self.stdlib_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'random', 'math', 're',
            'collections', 'itertools', 'functools', 'pathlib', 'typing',
            'logging', 'argparse', 'subprocess', 'threading', 'multiprocessing',
            'urllib', 'http', 'socket', 'email', 'html', 'xml', 'csv', 'sqlite3',
            'pickle', 'gzip', 'zipfile', 'tarfile', 'shutil', 'tempfile', 'glob',
            'warnings', 'copy', 'decimal', 'fractions', 'statistics', 'enum',
            'io', 'contextlib', 'abc', 'numbers', 'operator', 'keyword', 'builtins',
            'hashlib', 'base64', 'secrets', 'uuid', 'struct', 'importlib', 'inspect',
            'traceback', 'unittest', 'doctest', 'pdb', 'profile', 'timeit'
        }

    def create_dependency_prompt(self, code: str) -> str:
        """Create a comprehensive prompt for complete dependency detection"""
        return f"""You are a Python runtime dependency expert. Analyze this code and identify ALL third-party modules that would be loaded at runtime.

CRITICAL: Identify the COMPLETE dependency tree including transitive dependencies!

For EACH imported third-party package, include:
1. The main package name
2. ALL its required dependencies (transitive dependencies)
3. Sub-modules with dots (e.g., numpy.libs, scipy.libs)
4. Internal modules that get loaded (e.g., PIL for pillow)

Example dependency chains:
- import pandas needs: pandas, numpy, numpy.libs, pytz, python-dateutil, six, tzdata, bottleneck, numexpr, packaging
- import matplotlib needs: matplotlib, numpy, numpy.libs, cycler, kiwisolver, pyparsing, python-dateutil, PIL, pillow, pillow.libs, mpl_toolkits, packaging, fonttools, contourpy
- import sklearn needs: sklearn, scikit-learn, numpy, numpy.libs, scipy, scipy.libs, joblib, threadpoolctl
- import requests needs: requests, urllib3, certifi, charset-normalizer, idna

Python Code:
```python
{code}
```

List ALL third-party runtime dependencies (one per line, no duplicates, no standard library modules):"""

    def extract_dependencies_from_response(self, response_text: str) -> List[str]:
        """Extract dependency names from LLM response"""
        dependencies = []

        # Handle None or empty responses
        if not response_text:
            return []

        # Split response into lines and clean up
        lines = response_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip lines with explanatory text
            if any(skip in line.lower() for skip in [
                '```', 'dependencies:', 'here', 'following', 'runtime', 'would be',
                'loaded', 'imported', 'the code', 'analysis', 'based on', 'install',
                'required', 'optional', 'note:', '###', '##', 'to use', 'you need',
                'you\'ll need', 'statement', 'project', 'python', 'standard library',
                'third-party', 'example', 'for each', 'critical', 'complete'
            ]):
                continue

            # Clean the line
            clean_line = re.split(r'[#>=<~!:\(\)]', line)[0].strip()
            clean_line = re.sub(r'^\d+\.\s*', '', clean_line)
            clean_line = re.sub(r'^[-*•]\s*', '', clean_line)
            clean_line = re.sub(r'^\*\*', '', clean_line)
            clean_line = re.sub(r'\*\*$', '', clean_line)
            clean_line = clean_line.strip("'\"` ")

            # Validate package name format
            if re.match(r'^[a-zA-Z][a-zA-Z0-9_\.-]*$', clean_line):
                # Filter out standard library but keep sub-modules with dots
                base_module = clean_line.split('.')[0].lower()
                if '.' in clean_line or base_module not in self.stdlib_modules:
                    dependencies.append(clean_line.lower())

        return list(set(dependencies))  # Remove duplicates

    def analyze_script_with_llm(self, code: str, script_name: str = "unknown") -> Dict[str, Any]:
        """Analyze a Python script using LLaMA3 via NRP API"""
        start_time = time.time()

        logger.info(f"🔍 Analyzing {script_name} with LLaMA3...")

        try:
            # Create the comprehensive prompt
            prompt = self.create_dependency_prompt(code)

            # Call NRP API with LLaMA3
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Python dependency analyzer. List all third-party runtime dependencies including transitive dependencies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for more consistent results
                max_tokens=2000   # Allow for comprehensive responses
            )

            # Extract response
            response_text = completion.choices[0].message.content if completion.choices[0].message else None
            dependencies = self.extract_dependencies_from_response(response_text) if response_text else []

            analysis_time = time.time() - start_time

            logger.info(f"✅ Found {len(dependencies)} dependencies in {analysis_time:.2f}s")

            return {
                'script': script_name,
                'dependencies': dependencies,
                'dependency_count': len(dependencies),
                'analysis_time': round(analysis_time, 2),
                'method': 'llama3_nrp_analysis',
                'model_used': self.model,
                'raw_response': response_text if response_text else "Empty response"
            }

        except Exception as e:
            logger.error(f"❌ Error analyzing {script_name}: {e}")
            return {
                'script': script_name,
                'dependencies': [],
                'dependency_count': 0,
                'analysis_time': 0,
                'method': 'llama3_nrp_analysis',
                'model_used': self.model,
                'error': str(e)
            }

    def analyze_script_file(self, script_path: str) -> Dict[str, Any]:
        """Analyze a Python script file"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                code = f.read()

            script_name = Path(script_path).name
            return self.analyze_script_with_llm(code, script_name)

        except Exception as e:
            logger.error(f"Error reading script {script_path}: {e}")
            return {
                'script': Path(script_path).name,
                'dependencies': [],
                'dependency_count': 0,
                'analysis_time': 0,
                'error': f"File reading error: {str(e)}"
            }

    def batch_analyze_all_scripts(self, scripts_dir: str = "tests/scripts",
                                 output_dir: str = "results/llama3_nrp_analysis"):
        """Analyze all scripts in the directory using LLaMA3"""

        scripts_path = Path(scripts_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info("🚀 Starting batch analysis with LLaMA3 NRP Analyzer")
        logger.info(f"📁 Scripts directory: {scripts_path}")
        logger.info(f"📁 Output directory: {output_path}")
        logger.info(f"🔧 Model: {self.model}")

        # Find all script files
        script_files = sorted(list(scripts_path.glob("script_*.py")))
        logger.info(f"📊 Found {len(script_files)} scripts to analyze")

        all_results = []

        for i, script_file in enumerate(script_files, 1):
            logger.info(f"\n🔄 [{i}/{len(script_files)}] Processing {script_file.name}...")

            # Analyze script
            result = self.analyze_script_file(str(script_file))
            all_results.append(result)

            # Save individual results
            if result['dependencies']:
                req_file = output_path / f"{script_file.stem}_requirements.txt"
                with open(req_file, 'w') as f:
                    f.write(f"# LLaMA3 NRP Analysis for {script_file.name}\n")
                    f.write(f"# Model: {self.model}\n")
                    f.write(f"# Dependencies found: {result['dependency_count']}\n\n")

                    for dep in sorted(result['dependencies']):
                        f.write(f"{dep}\n")

            # Small delay to avoid rate limiting
            if i % 5 == 0:  # Longer delay every 5 requests
                time.sleep(2)
            else:
                time.sleep(0.5)

        # Generate summary report
        logger.info("\n📊 Generating summary report...")

        successful_analyses = [r for r in all_results if 'error' not in r]
        total_deps_found = sum(len(r['dependencies']) for r in successful_analyses)
        avg_deps = total_deps_found / len(successful_analyses) if successful_analyses else 0
        total_time = sum(r['analysis_time'] for r in successful_analyses)

        summary = {
            'total_scripts': len(script_files),
            'successful_analyses': len(successful_analyses),
            'failed_analyses': len(all_results) - len(successful_analyses),
            'total_dependencies_found': total_deps_found,
            'average_dependencies_per_script': round(avg_deps, 2),
            'total_analysis_time_seconds': round(total_time, 2),
            'model_used': self.model
        }

        # Save results
        with open(output_path / "analysis_results.json", 'w') as f:
            json.dump(all_results, f, indent=2)

        with open(output_path / "summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info("\n" + "="*80)
        logger.info("📈 LLAMA3 NRP ANALYSIS COMPLETE")
        logger.info("="*80)
        logger.info(f"📊 Total scripts: {summary['total_scripts']}")
        logger.info(f"✅ Successful: {summary['successful_analyses']}")
        logger.info(f"📦 Avg dependencies per script: {summary['average_dependencies_per_script']}")
        logger.info(f"⏱️ Total time: {summary['total_analysis_time_seconds']}s")
        logger.info(f"💾 Results saved to: {output_path}")

        return all_results

    def add_results_to_csv(self, csv_path: str = "results/comparison_reports/comprehensive_dependency_analysis.csv"):
        """Add LLaMA3 results as a new column to the existing CSV"""
        logger.info("\n📊 Adding LLaMA3 results to CSV...")

        # Read the analysis results
        results_file = Path("results/llama3_nrp_analysis/analysis_results.json")
        if not results_file.exists():
            logger.error("❌ No analysis results found. Run batch_analyze_all_scripts first.")
            return

        with open(results_file, 'r') as f:
            llama3_results = json.load(f)

        # Read existing CSV
        df = pd.read_csv(csv_path)

        # Create a dictionary mapping script names to dependencies
        llama3_deps_dict = {}
        for result in llama3_results:
            script_name = result['script']
            deps = result.get('dependencies', [])
            llama3_deps_dict[script_name] = sorted(deps)

        # Add new column for LLaMA3 dependencies
        df['llama3_nrp_dependencies'] = df['script_file'].apply(
            lambda x: llama3_deps_dict.get(x, [])
        )

        # Calculate metrics for LLaMA3
        def calculate_llama3_metrics(row):
            sciunit_deps = eval(row['sciunit_dependencies']) if isinstance(row['sciunit_dependencies'], str) else row['sciunit_dependencies']
            llama3_deps = row['llama3_nrp_dependencies']

            sciunit_set = set(sciunit_deps)
            llama3_set = set(llama3_deps)

            tp = len(sciunit_set & llama3_set)
            fp = len(llama3_set - sciunit_set)
            fn = len(sciunit_set - llama3_set)

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

            return pd.Series({
                'llama3_true_positives': tp,
                'llama3_false_positives': fp,
                'llama3_false_negatives': fn,
                'llama3_precision': round(precision, 4),
                'llama3_recall': round(recall, 4),
                'llama3_f1_score': round(f1, 4)
            })

        # Apply metrics calculation
        llama3_metrics = df.apply(calculate_llama3_metrics, axis=1)
        df = pd.concat([df, llama3_metrics], axis=1)

        # Save updated CSV
        df.to_csv(csv_path, index=False)

        logger.info(f"✅ Added LLaMA3 results to CSV")
        logger.info(f"📊 Average LLaMA3 Metrics:")
        logger.info(f"  - Precision: {df['llama3_precision'].mean():.4f}")
        logger.info(f"  - Recall: {df['llama3_recall'].mean():.4f}")
        logger.info(f"  - F1 Score: {df['llama3_f1_score'].mean():.4f}")

def main():
    """Main function to run the LLaMA3 NRP analyzer"""
    analyzer = LLaMA3NRPAnalyzer()

    # Run the analysis
    results = analyzer.batch_analyze_all_scripts()

    # Add results to CSV
    if results:
        analyzer.add_results_to_csv()

    return results

if __name__ == "__main__":
    main()