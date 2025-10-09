#!/usr/bin/env python3
"""
True LLM-Based Dependency Analyzer using Llama Models
This analyzer uses Llama models from Hugging Face to analyze Python code and extract dependencies.
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Set
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import re
import json
from huggingface_hub import login

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class LlamaDependencyAnalyzer:
    def __init__(self, model_name: str = "meta-llama/Llama-3.2-3B-Instruct"):
        """Initialize the Llama-based dependency analyzer"""
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"🦙 Initializing Llama Dependency Analyzer")
        logger.info(f"📦 Model: {self.model_name}")
        logger.info(f"🖥️ Device: {self.device}")
        
        self.load_model()
        
        # Standard library modules to filter out
        self.stdlib_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'random', 'math', 're',
            'collections', 'itertools', 'functools', 'pathlib', 'typing',
            'logging', 'argparse', 'subprocess', 'threading', 'multiprocessing',
            'urllib', 'http', 'socket', 'email', 'html', 'xml', 'csv', 'sqlite3',
            'pickle', 'gzip', 'zipfile', 'tarfile', 'shutil', 'tempfile', 'glob',
            'warnings', 'copy', 'decimal', 'fractions', 'statistics', 'enum',
            'io', 'contextlib', 'abc', 'numbers', 'operator', 'keyword', 'builtins'
        }

    def load_model(self):
        """Load Llama model from Hugging Face"""
        try:
            logger.info("🔄 Loading Llama model and tokenizer...")
            
            # Load tokenizer
            logger.info("📝 Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with optimizations for inference
            logger.info("🧠 Loading model (this may take a while)...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True,
                device_map="auto" if self.device == "cuda" else None
            )
            
            # Create pipeline for easier inference
            logger.info("🔧 Creating inference pipeline...")
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map="auto" if self.device == "cuda" else None,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                do_sample=True,
                temperature=0.3,
                top_p=0.9,
                max_new_tokens=200,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            logger.info("✅ Llama model loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            # Fallback to smaller model if the main one fails
            logger.info("🔄 Trying fallback model: microsoft/DialoGPT-medium")
            try:
                self.model_name = "microsoft/DialoGPT-medium"
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    low_cpu_mem_usage=True
                )
                
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if self.device == "cuda" else -1,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                logger.info("✅ Fallback model loaded successfully!")
            except Exception as e2:
                logger.error(f"❌ Fallback model also failed: {e2}")
                raise

    def create_dependency_prompt(self, code: str) -> str:
        """Create a structured prompt for dependency analysis"""
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a Python expert who analyzes code to identify external library dependencies that need to be installed via pip.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Analyze this Python code and identify ALL external library dependencies that need to be installed via pip.

IMPORTANT RULES:
1. Look for explicit imports (import statements)
2. Look for implicit usage patterns (function calls, method calls, object usage)
3. identify third-party packages as well (built-in Python modules like os, sys, json, etc.)
4. Return all the package names
5. Do not include explanations or commentary just dependencies

Python Code:
```python
{code}
```

List the pip installable packages (one per line):
<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        return prompt

    def create_validation_prompt(self, code: str, dependencies: List[str]) -> str:
        """Create a validation prompt to double-check dependencies"""
        deps_str = "\n".join(dependencies) if dependencies else "None found"
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a Python expert who validates dependency analysis results.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Validate this dependency analysis. Are these dependencies correct for the given Python code?

Python Code:
```python
{code}
```

Identified Dependencies:
{deps_str}

Are these dependencies correct? If yes, respond with "CORRECT". If not, provide the corrected list (one package per line):
<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        return prompt

    def extract_dependencies_from_response(self, response_text: str) -> List[str]:
        """Extract dependency names from LLM response"""
        dependencies = []
        
        # Clean the response text
        response_text = response_text.strip()
        
        # Split response into lines and clean up
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip common response patterns and headers
            if any(skip in line.lower() for skip in [
                '<|', 'task:', 'instructions:', 'python code:', 'dependencies:', 
                'external dependencies:', '```', 'answer:', 'question:',
                'identified dependencies:', 'correct', 'none found', 'list the',
                'pip installable', 'system', 'user', 'assistant', 'begin_of_text',
                'start_header_id', 'end_header_id', 'eot_id'
            ]):
                continue
            
            # Extract package name (remove comments, version specs, etc.)
            # Handle patterns like "numpy  # for arrays" or "pandas==1.3.0"
            clean_line = re.split(r'[#>=<~!]', line)[0].strip()
            
            # Remove common prefixes and bullets
            clean_line = re.sub(r'^\d+\.\s*', '', clean_line)  # Remove numbered lists
            clean_line = re.sub(r'^[-*•]\s*', '', clean_line)  # Remove bullet points
            clean_line = re.sub(r'^(pip install\s+)', '', clean_line)  # Remove "pip install"
            
            # Validate package name format
            if re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', clean_line):
                if clean_line.lower() not in self.stdlib_modules:
                    dependencies.append(clean_line.lower())
        
        return list(set(dependencies))  # Remove duplicates

    def analyze_script_with_llm(self, code: str, script_name: str = "unknown") -> Dict[str, Any]:
        """Analyze a Python script using LLM inference"""
        start_time = time.time()
        
        logger.info(f"🔍 Analyzing {script_name} with Llama...")
        
        try:
            # Primary analysis
            primary_prompt = self.create_dependency_prompt(code)
            logger.info("📝 Running primary dependency analysis...")
            
            primary_response = self.pipeline(
                primary_prompt,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.3,
                return_full_text=False,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            primary_text = primary_response[0]['generated_text']
            primary_deps = self.extract_dependencies_from_response(primary_text)
            
            logger.info(f"🔍 Primary analysis found: {primary_deps}")
            
            # Validation analysis (if we found dependencies)
            validation_text = None
            if primary_deps:
                logger.info("🔄 Running validation analysis...")
                validation_prompt = self.create_validation_prompt(code, primary_deps)
                
                validation_response = self.pipeline(
                    validation_prompt,
                    max_new_tokens=100,
                    do_sample=True,
                    temperature=0.2,
                    return_full_text=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
                validation_text = validation_response[0]['generated_text']
                
                if "CORRECT" not in validation_text.upper():
                    validated_deps = self.extract_dependencies_from_response(validation_text)
                    if validated_deps:
                        logger.info(f"🔄 Validation analysis updated to: {validated_deps}")
                        final_deps = validated_deps
                    else:
                        final_deps = primary_deps
                else:
                    logger.info("✅ Validation confirmed primary analysis")
                    final_deps = primary_deps
            else:
                final_deps = primary_deps
            
            analysis_time = time.time() - start_time
            
            result = {
                'script': script_name,
                'dependencies': final_deps,
                'dependency_count': len(final_deps),
                'analysis_time': round(analysis_time, 2),
                'method': 'llama_llm_analysis',
                'model_used': self.model_name,
                'primary_response': primary_text,
                'validation_response': validation_text
            }
            
            logger.info(f"✅ Analysis complete for {script_name}: {len(final_deps)} dependencies found in {analysis_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing {script_name}: {e}")
            return {
                'script': script_name,
                'dependencies': [],
                'dependency_count': 0,
                'analysis_time': 0,
                'method': 'llama_llm_analysis',
                'model_used': self.model_name,
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
                'method': 'llama_llm_analysis',
                'model_used': self.model_name,
                'error': f"File reading error: {str(e)}"
            }

    def batch_analyze_all_scripts(self, scripts_dir: str = "code_scripts", output_dir: str = "output/LlamaLLMAnalysis"):
        """Analyze all scripts in the directory using Llama LLM"""
        
        scripts_path = Path(scripts_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("🚀 Starting batch analysis of all scripts using Llama LLM Analysis")
        logger.info(f"📁 Scripts directory: {scripts_path}")
        logger.info(f"📁 Output directory: {output_path}")
        logger.info(f"🦙 Model: {self.model_name}")
        
        # Find all script files
        script_files = sorted(list(scripts_path.glob("script_*.py")))
        logger.info(f"📊 Found {len(script_files)} scripts to analyze")
        
        all_results = []
        
        for i, script_file in enumerate(script_files, 1):
            logger.info(f"\n🔄 [{i}/{len(script_files)}] Processing {script_file.name}...")
            
            # Analyze script
            result = self.analyze_script_file(str(script_file))
            all_results.append(result)
            
            # Save individual requirements file
            if result['dependencies']:
                req_file = output_path / f"{script_file.stem}_requirements.txt"
                with open(req_file, 'w') as f:
                    f.write(f"# LLM Dependency Analysis for {script_file.name}\n")
                    f.write(f"# Generated by Llama LLM Analyzer ({self.model_name})\n")
                    f.write(f"# Analysis time: {result['analysis_time']}s\n")
                    f.write(f"# Dependencies found: {result['dependency_count']}\n\n")
                    
                    for dep in sorted(result['dependencies']):
                        f.write(f"{dep}\n")
                
                logger.info(f"💾 Saved requirements to {req_file.name}")
            else:
                logger.info("📝 No dependencies found")
            
            # Small delay to prevent overloading
            time.sleep(2)
        
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
            'average_time_per_script': round(total_time / len(successful_analyses), 2) if successful_analyses else 0,
            'model_used': self.model_name
        }
        
        # Save detailed results
        detailed_results_file = output_path / "detailed_analysis_results.json"
        with open(detailed_results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        # Save summary
        summary_file = output_path / "analysis_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        logger.info("\n" + "="*80)
        logger.info("📈 LLAMA LLM ANALYSIS COMPLETE - SUMMARY REPORT")
        logger.info("="*80)
        logger.info(f"🦙 Model used: {summary['model_used']}")
        logger.info(f"📊 Total scripts processed: {summary['total_scripts']}")
        logger.info(f"✅ Successful analyses: {summary['successful_analyses']}")
        logger.info(f"❌ Failed analyses: {summary['failed_analyses']}")
        logger.info(f"📦 Total dependencies found: {summary['total_dependencies_found']}")
        logger.info(f"📊 Average dependencies per script: {summary['average_dependencies_per_script']}")
        logger.info(f"⏱️ Total analysis time: {summary['total_analysis_time_seconds']}s")
        logger.info(f"⏱️ Average time per script: {summary['average_time_per_script']}s")
        logger.info(f"💾 Results saved to: {output_path}")
        
        return all_results

def test_single_script():
    """Test the analyzer on a single script"""
    analyzer = LlamaDependencyAnalyzer()
    
    # Test with a sample script
    test_code = """
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import requests
import json

def analyze_data():
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    arr = np.array([1, 2, 3])
    X_train, X_test = train_test_split(arr, test_size=0.2)
    plt.plot([1, 2, 3])
    response = requests.get('http://example.com')
    return df, arr
"""
    
    result = analyzer.analyze_script_with_llm(test_code, "test_script.py")
    print("Test Result:", result)
    return result

def main():
    """Main function to run the Llama LLM Dependency Analyzer"""
    try:
        # Test with a single script first
        logger.info("🧪 Running test analysis...")
        test_result = test_single_script()
        
        if test_result and 'error' not in test_result:
            logger.info("✅ Test successful! Running full batch analysis...")
            # Initialize analyzer for batch processing
            analyzer = LlamaDependencyAnalyzer()
            
            # Run batch analysis
            results = analyzer.batch_analyze_all_scripts()
            
            logger.info("🎉 Analysis complete!")
        else:
            logger.error("❌ Test failed, skipping batch analysis")
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()