#!/usr/bin/env python3
"""
NRP LLM-Based Dependency Analyzer using API
This analyzer uses NRP's hosted LLM API to analyze Python code and extract ALL dependencies.
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

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class NRPLLMDependencyAnalyzer:
    def __init__(self, api_key: str = "sk-6pI0VL9Izp8AUc-gos_Xgw", model: str = "llama3"):
        """Initialize the NRP LLM-based dependency analyzer"""
        self.api_key = api_key
        self.model = model
        self.base_url = "https://llm.nrp-nautilus.io/"
        
        # Initialize OpenAI client for NRP
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        logger.info(f"🚀 Initializing NRP LLM Dependency Analyzer")
        logger.info(f"🔗 API Endpoint: {self.base_url}")
        logger.info(f"🤖 Model: {self.model}")
        
        # Test API connection
        self.test_connection()

    def test_connection(self):
        """Test API connection"""
        try:
            logger.info("🔍 Testing API connection...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello! Can you help analyze Python code?"}],
                max_tokens=50
            )
            logger.info("✅ API connection successful!")
        except Exception as e:
            logger.error(f"❌ API connection failed: {e}")
            raise

    def create_comprehensive_dependency_prompt(self, code: str) -> str:
        """Create a comprehensive prompt for dependency analysis focusing on reproducibility"""
        prompt = f"""You are a Python dependency analysis expert. Analyze the following Python code and identify ALL dependencies required for reproducibility.

TASK: Identify ALL external dependencies needed to run this code successfully.

REQUIREMENTS:
1. List ALL third-party packages (installable via pip, conda, apt-get, etc.)
2. Include system libraries and tools (not just Python packages)
3. Include version-specific requirements if evident in the code
4. Include development tools (if the code uses them)
5. Include runtime dependencies (databases, services, etc.)
6. DO NOT include Python built-in modules (os, sys, json, time, etc.)
7. Focus on REPRODUCIBILITY - what would someone need to install to run this code?

PYTHON CODE:
```python
{code}
```

ANALYSIS INSTRUCTIONS:
- Look for import statements
- Look for subprocess calls that use external tools
- Look for file format handlers (PDF, images, etc.)
- Look for database connections
- Look for web frameworks and their dependencies
- Look for machine learning libraries and their ecosystem
- Look for GUI frameworks
- Look for system-level tools and libraries

OUTPUT FORMAT:
Return ONLY a JSON object with this exact structure:
{{
    "pip_packages": ["package1", "package2"],
    "system_packages": ["system-tool1", "system-tool2"],
    "services": ["database-service", "web-service"],
    "notes": "Any important setup notes"
}}

IMPORTANT: Return ONLY the JSON object, no additional text or explanation."""

        return prompt

    def create_validation_prompt(self, code: str, analysis_result: Dict) -> str:
        """Create validation prompt to double-check the analysis"""
        prompt = f"""VALIDATION TASK: Review this dependency analysis for completeness and accuracy.

ORIGINAL CODE:
```python
{code}
```

CURRENT ANALYSIS:
{json.dumps(analysis_result, indent=2)}

VALIDATION QUESTIONS:
1. Are there any missing dependencies?
2. Are all listed dependencies actually needed?
3. Are there implicit dependencies (e.g., CUDA for GPU code)?
4. Are there version constraints that should be noted?

OUTPUT: Return the corrected JSON analysis or "CORRECT" if the analysis is accurate.
Return ONLY the JSON object or "CORRECT", no additional text."""

        return prompt

    def extract_dependencies_from_response(self, response_text: str) -> Dict[str, List[str]]:
        """Extract dependencies from LLM JSON response"""
        try:
            # Clean the response
            response_text = response_text.strip()
            
            # Try to find JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > 0:
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
                
                # Ensure all required keys exist
                dependencies = {
                    'pip_packages': result.get('pip_packages', []),
                    'system_packages': result.get('system_packages', []),
                    'services': result.get('services', []),
                    'notes': result.get('notes', '')
                }
                
                # Clean and validate packages
                for key in ['pip_packages', 'system_packages', 'services']:
                    if isinstance(dependencies[key], list):
                        # Clean package names
                        cleaned = []
                        for pkg in dependencies[key]:
                            if isinstance(pkg, str) and pkg.strip():
                                clean_pkg = pkg.strip().lower()
                                # Remove version specifiers for consistency
                                clean_pkg = re.split(r'[>=<~!]', clean_pkg)[0].strip()
                                if clean_pkg and re.match(r'^[a-zA-Z][a-zA-Z0-9_.-]*$', clean_pkg):
                                    cleaned.append(clean_pkg)
                        dependencies[key] = list(set(cleaned))  # Remove duplicates
                
                return dependencies
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
        except Exception as e:
            logger.warning(f"Error extracting dependencies: {e}")
        
        # Fallback: return empty structure
        return {
            'pip_packages': [],
            'system_packages': [],
            'services': [],
            'notes': 'Failed to parse response'
        }

    def analyze_script_with_nrp_llm(self, code: str, script_name: str = "unknown") -> Dict[str, Any]:
        """Analyze a Python script using NRP LLM API"""
        start_time = time.time()
        
        logger.info(f"🔍 Analyzing {script_name} with NRP LLM...")
        
        try:
            # Primary comprehensive analysis
            primary_prompt = self.create_comprehensive_dependency_prompt(code)
            logger.info("📝 Running comprehensive dependency analysis...")
            
            primary_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": primary_prompt}],
                max_tokens=800,
                temperature=0.1  # Lower temperature for more consistent results
            )
            
            primary_text = primary_response.choices[0].message.content
            primary_deps = self.extract_dependencies_from_response(primary_text)
            
            logger.info(f"🔍 Primary analysis found:")
            logger.info(f"   Pip packages: {len(primary_deps['pip_packages'])} - {primary_deps['pip_packages']}")
            logger.info(f"   System packages: {len(primary_deps['system_packages'])} - {primary_deps['system_packages']}")
            logger.info(f"   Services: {len(primary_deps['services'])} - {primary_deps['services']}")
            
            # Validation analysis
            logger.info("🔄 Running validation analysis...")
            validation_prompt = self.create_validation_prompt(code, primary_deps)
            
            validation_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": validation_prompt}],
                max_tokens=600,
                temperature=0.1
            )
            
            validation_text = validation_response.choices[0].message.content
            
            if "CORRECT" not in validation_text.upper():
                validated_deps = self.extract_dependencies_from_response(validation_text)
                if validated_deps and any(validated_deps.values()):
                    logger.info("🔄 Validation analysis provided updates")
                    final_deps = validated_deps
                else:
                    final_deps = primary_deps
            else:
                logger.info("✅ Validation confirmed primary analysis")
                final_deps = primary_deps
            
            # Calculate total dependency count
            total_deps = len(final_deps['pip_packages']) + len(final_deps['system_packages']) + len(final_deps['services'])
            
            analysis_time = time.time() - start_time
            
            result = {
                'script': script_name,
                'pip_packages': final_deps['pip_packages'],
                'system_packages': final_deps['system_packages'],
                'services': final_deps['services'],
                'notes': final_deps['notes'],
                'total_dependencies': total_deps,
                'pip_count': len(final_deps['pip_packages']),
                'system_count': len(final_deps['system_packages']),
                'services_count': len(final_deps['services']),
                'analysis_time': round(analysis_time, 2),
                'method': 'nrp_llm_comprehensive',
                'model_used': self.model,
                'primary_response': primary_text,
                'validation_response': validation_text
            }
            
            logger.info(f"✅ Analysis complete for {script_name}: {total_deps} total dependencies in {analysis_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing {script_name}: {e}")
            return {
                'script': script_name,
                'pip_packages': [],
                'system_packages': [],
                'services': [],
                'notes': f'Analysis failed: {str(e)}',
                'total_dependencies': 0,
                'pip_count': 0,
                'system_count': 0,
                'services_count': 0,
                'analysis_time': 0,
                'method': 'nrp_llm_comprehensive',
                'model_used': self.model,
                'error': str(e)
            }

    def analyze_script_file(self, script_path: str) -> Dict[str, Any]:
        """Analyze a Python script file"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            script_name = Path(script_path).name
            return self.analyze_script_with_nrp_llm(code, script_name)
            
        except Exception as e:
            logger.error(f"Error reading script {script_path}: {e}")
            return {
                'script': Path(script_path).name,
                'pip_packages': [],
                'system_packages': [],
                'services': [],
                'notes': f'File reading error: {str(e)}',
                'total_dependencies': 0,
                'pip_count': 0,
                'system_count': 0,
                'services_count': 0,
                'analysis_time': 0,
                'method': 'nrp_llm_comprehensive',
                'model_used': self.model,
                'error': f"File reading error: {str(e)}"
            }

    def batch_analyze_all_scripts(self, scripts_dir: str = "code_scripts", output_dir: str = "output/NRPLLMAnalysis"):
        """Analyze all scripts using NRP LLM API"""
        
        scripts_path = Path(scripts_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("🚀 Starting comprehensive batch analysis using NRP LLM API")
        logger.info(f"📁 Scripts directory: {scripts_path}")
        logger.info(f"📁 Output directory: {output_path}")
        logger.info(f"🤖 Model: {self.model}")
        logger.info(f"🔗 Endpoint: {self.base_url}")
        
        # Find all script files
        script_files = sorted(list(scripts_path.glob("script_*.py")))
        logger.info(f"📊 Found {len(script_files)} scripts to analyze")
        
        all_results = []
        
        for i, script_file in enumerate(script_files, 1):
            logger.info(f"\n🔄 [{i}/{len(script_files)}] Processing {script_file.name}...")
            
            # Analyze script
            result = self.analyze_script_file(str(script_file))
            all_results.append(result)
            
            # Save individual comprehensive requirements file
            if result['total_dependencies'] > 0:
                req_file = output_path / f"{script_file.stem}_comprehensive_requirements.txt"
                with open(req_file, 'w') as f:
                    f.write(f"# Comprehensive Dependency Analysis for {script_file.name}\n")
                    f.write(f"# Generated by NRP LLM Analyzer ({self.model})\n")
                    f.write(f"# Analysis time: {result['analysis_time']}s\n")
                    f.write(f"# Total dependencies: {result['total_dependencies']}\n\n")
                    
                    if result['pip_packages']:
                        f.write("# PIP PACKAGES\n")
                        for dep in sorted(result['pip_packages']):
                            f.write(f"{dep}\n")
                        f.write("\n")
                    
                    if result['system_packages']:
                        f.write("# SYSTEM PACKAGES (install via package manager)\n")
                        for dep in sorted(result['system_packages']):
                            f.write(f"# {dep}\n")
                        f.write("\n")
                    
                    if result['services']:
                        f.write("# SERVICES/DATABASES REQUIRED\n")
                        for service in sorted(result['services']):
                            f.write(f"# {service}\n")
                        f.write("\n")
                    
                    if result['notes']:
                        f.write(f"# NOTES: {result['notes']}\n")
                
                logger.info(f"💾 Saved comprehensive requirements to {req_file.name}")
            else:
                logger.info("📝 No dependencies found")
            
            # Small delay to be respectful to API
            time.sleep(1)
        
        # Generate summary report
        logger.info("\n📊 Generating comprehensive summary report...")
        
        successful_analyses = [r for r in all_results if 'error' not in r]
        total_pip_deps = sum(r['pip_count'] for r in successful_analyses)
        total_system_deps = sum(r['system_count'] for r in successful_analyses)
        total_services = sum(r['services_count'] for r in successful_analyses)
        total_all_deps = sum(r['total_dependencies'] for r in successful_analyses)
        avg_deps = total_all_deps / len(successful_analyses) if successful_analyses else 0
        total_time = sum(r['analysis_time'] for r in successful_analyses)
        
        summary = {
            'total_scripts': len(script_files),
            'successful_analyses': len(successful_analyses),
            'failed_analyses': len(all_results) - len(successful_analyses),
            'total_pip_packages': total_pip_deps,
            'total_system_packages': total_system_deps,
            'total_services': total_services,
            'total_all_dependencies': total_all_deps,
            'average_dependencies_per_script': round(avg_deps, 2),
            'total_analysis_time_seconds': round(total_time, 2),
            'average_time_per_script': round(total_time / len(successful_analyses), 2) if successful_analyses else 0,
            'model_used': self.model,
            'endpoint': self.base_url
        }
        
        # Save detailed results
        detailed_results_file = output_path / "comprehensive_analysis_results.json"
        with open(detailed_results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        # Save summary
        summary_file = output_path / "comprehensive_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        logger.info("\n" + "="*80)
        logger.info("📈 NRP LLM COMPREHENSIVE ANALYSIS COMPLETE")
        logger.info("="*80)
        logger.info(f"🤖 Model used: {summary['model_used']}")
        logger.info(f"🔗 Endpoint: {summary['endpoint']}")
        logger.info(f"📊 Total scripts processed: {summary['total_scripts']}")
        logger.info(f"✅ Successful analyses: {summary['successful_analyses']}")
        logger.info(f"❌ Failed analyses: {summary['failed_analyses']}")
        logger.info(f"📦 Total pip packages: {summary['total_pip_packages']}")
        logger.info(f"🔧 Total system packages: {summary['total_system_packages']}")
        logger.info(f"🗄️ Total services: {summary['total_services']}")
        logger.info(f"📊 Total all dependencies: {summary['total_all_dependencies']}")
        logger.info(f"📊 Average dependencies per script: {summary['average_dependencies_per_script']}")
        logger.info(f"⏱️ Total analysis time: {summary['total_analysis_time_seconds']}s")
        logger.info(f"⏱️ Average time per script: {summary['average_time_per_script']}s")
        logger.info(f"💾 Results saved to: {output_path}")
        
        return all_results

def test_analyzer():
    """Test the analyzer with sample code"""
    analyzer = NRPLLMDependencyAnalyzer()
    
    test_code = """
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import requests
import sqlite3
import subprocess

def main():
    # Data analysis
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    arr = np.array([1, 2, 3])
    X_train, X_test = train_test_split(arr, test_size=0.2)
    
    # Visualization
    plt.plot([1, 2, 3])
    
    # Web request
    response = requests.get('http://example.com')
    
    # Database
    conn = sqlite3.connect('test.db')
    
    # System call
    subprocess.run(['git', 'status'])
    
    return df, arr
"""
    
    result = analyzer.analyze_script_with_nrp_llm(test_code, "test_comprehensive.py")
    logger.info(f"Test Result: {json.dumps(result, indent=2)}")
    return result

def main():
    """Main function"""
    try:
        # Test analyzer first
        logger.info("🧪 Running comprehensive test analysis...")
        test_result = test_analyzer()
        
        if test_result and 'error' not in test_result:
            logger.info("✅ Test successful! Running full comprehensive batch analysis...")
            # Initialize analyzer for batch processing
            analyzer = NRPLLMDependencyAnalyzer()
            
            # Run batch analysis
            results = analyzer.batch_analyze_all_scripts()
            
            logger.info("🎉 Comprehensive analysis complete!")
        else:
            logger.error("❌ Test failed, skipping batch analysis")
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()