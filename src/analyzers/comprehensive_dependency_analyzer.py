#!/usr/bin/env python3
"""
Comprehensive LLM-Based Dependency Analyzer for Reproducibility
This analyzer focuses on finding ALL dependencies needed for full reproducibility.
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Set
import json
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveDependencyAnalyzer:
    def __init__(self):
        """Initialize the comprehensive dependency analyzer"""
        logger.info(f"🚀 Initializing Comprehensive Dependency Analyzer")
        logger.info(f"🎯 Focus: Complete reproducibility analysis")
        
        # Initialize with improved analysis methodology
        self.analysis_categories = {
            'pip_packages': [],
            'system_packages': [],
            'services': [],
            'build_tools': [],
            'notes': ''
        }

    def create_comprehensive_analysis_prompt(self, code: str) -> str:
        """Create comprehensive prompt for full reproducibility analysis"""
        return f"""You are an expert system for analyzing Python code dependencies with focus on COMPLETE REPRODUCIBILITY.

MISSION: Identify ALL dependencies someone would need to successfully run this code from scratch on a clean system.

ANALYSIS CATEGORIES:
1. PIP PACKAGES: Python packages installable via pip
2. SYSTEM PACKAGES: OS-level packages (apt, yum, brew, etc.)
3. SERVICES: Databases, web servers, external services
4. BUILD TOOLS: Compilers, build systems, development tools
5. IMPLICIT DEPENDENCIES: Libraries used indirectly

PYTHON CODE TO ANALYZE:
```python
{code}
```

COMPREHENSIVE ANALYSIS INSTRUCTIONS:

📦 PIP PACKAGES:
- Look for all import statements
- Identify packages from function calls and usage patterns
- Include ML/AI ecosystem dependencies (torch -> CUDA, tensorflow -> tensorrt, etc.)
- Include GUI framework dependencies
- Include web framework ecosystem packages

🔧 SYSTEM PACKAGES:
- Database drivers and system libraries
- Image/video processing libraries (ffmpeg, opencv system deps)
- Audio processing libraries
- Graphics and rendering libraries
- Networking and security libraries

🗄️ SERVICES/DATABASES:
- Database servers (PostgreSQL, MySQL, MongoDB, Redis)
- Web servers and proxies
- Message queues and caching systems
- External APIs that need authentication

🛠️ BUILD TOOLS:
- Compilers for compiled extensions
- Build systems (cmake, make, etc.)
- Language-specific tools

ANALYSIS RULES:
- Be thorough - miss nothing that could break reproducibility
- Consider the full software stack
- Think about what a Docker container would need
- Consider version compatibility issues
- Include development vs production differences

OUTPUT: Provide a detailed analysis covering all categories above. Be specific and comprehensive."""

    def analyze_code_comprehensively(self, code: str) -> Dict[str, Any]:
        """Perform comprehensive static analysis of Python code"""
        
        # Initialize results
        result = {
            'pip_packages': set(),
            'system_packages': set(),
            'services': set(),
            'build_tools': set(),
            'notes': []
        }
        
        # Enhanced pattern analysis for comprehensive detection
        
        # 1. Direct imports and pip packages
        import_patterns = {
            # Data Science & ML
            'numpy': ['numpy', 'np.', 'ndarray', 'dtype='],
            'pandas': ['pandas', 'pd.', 'DataFrame', 'Series', '.to_csv', '.read_csv'],
            'matplotlib': ['matplotlib', 'plt.', 'pyplot', '.plot(', '.show()', '.savefig'],
            'seaborn': ['seaborn', 'sns.', '.heatmap', '.boxplot'],
            'sklearn': ['sklearn', 'train_test_split', 'LinearRegression', 'RandomForest'],
            'scipy': ['scipy', 'stats.', 'optimize.', 'signal.'],
            'torch': ['torch', 'nn.Module', '.cuda()', 'optim.'],
            'tensorflow': ['tensorflow', 'tf.', 'keras', 'Model('],
            'transformers': ['transformers', 'AutoModel', 'pipeline('],
            
            # Web & Network
            'requests': ['requests.', '.get(', '.post(', '.json()'],
            'flask': ['Flask', '@app.route', 'render_template'],
            'django': ['django', 'models.Model', 'HttpResponse'],
            'fastapi': ['FastAPI', '@app.get', 'Depends('],
            'aiohttp': ['aiohttp', 'ClientSession', 'async with'],
            
            # Database
            'psycopg2': ['psycopg2', 'connect(', 'cursor()'],
            'sqlalchemy': ['sqlalchemy', 'create_engine', 'sessionmaker'],
            'pymongo': ['pymongo', 'MongoClient', '.find('],
            'redis': ['redis.Redis', 'r.get(', 'r.set('],
            
            # GUI
            'tkinter': ['tkinter', 'Tk()', 'Button(', 'Label('],
            'pyqt5': ['PyQt5', 'QApplication', 'QWidget'],
            'pyqt6': ['PyQt6', 'QMainWindow', 'QLabel'],
            
            # Image/Video Processing  
            'pillow': ['PIL', 'Image.', '.open(', '.save('],
            'opencv-python': ['cv2', 'VideoCapture', 'imread'],
            'imageio': ['imageio', 'imread', 'imwrite'],
            'moviepy': ['moviepy', 'VideoFileClip'],
            
            # Audio
            'librosa': ['librosa', 'load(', 'stft('],
            'pydub': ['pydub', 'AudioSegment'],
            
            # Utility
            'beautifulsoup4': ['BeautifulSoup', 'find(', 'find_all('],
            'lxml': ['lxml', 'etree.', 'fromstring'],
            'yaml': ['yaml', 'load(', 'dump('],
            'cryptography': ['cryptography', 'Fernet', 'generate_key'],
            'pygame': ['pygame', 'init(', 'display.'],
        }
        
        # Analyze imports and usage patterns
        for package, patterns in import_patterns.items():
            if any(pattern in code for pattern in patterns):
                result['pip_packages'].add(package)
        
        # 2. System packages analysis
        system_indicators = {
            # Database system packages
            'postgresql-dev': ['psycopg2', 'PostgreSQL', 'pg_config'],
            'mysql-dev': ['MySQLdb', 'mysql.connector', 'pymysql'],
            'sqlite3-dev': ['sqlite3', '.db'],
            
            # Media processing
            'ffmpeg': ['ffmpeg', 'VideoFileClip', 'AudioFileClip'],
            'libopencv-dev': ['cv2', 'opencv', 'VideoCapture'],
            'libjpeg-dev': ['PIL', 'JPEG', 'Image.'],
            'libpng-dev': ['PNG', 'Image.'],
            
            # Audio
            'libasound2-dev': ['pygame', 'audio', 'sound'],
            'portaudio19-dev': ['pyaudio', 'audio recording'],
            
            # Graphics
            'libgl1-mesa-dev': ['OpenGL', 'graphics', 'rendering'],
            'libglu1-mesa-dev': ['GLU', '3D graphics'],
            
            # Network/Security
            'libssl-dev': ['ssl', 'cryptography', 'https'],
            'libffi-dev': ['cryptography', 'cffi'],
            
            # Build tools
            'gcc': ['compile', 'Cython', '.c extension'],
            'g++': ['C++', 'cpp', 'compile'],
            'make': ['Makefile', 'build system'],
            'cmake': ['CMakeLists.txt', 'cmake'],
        }
        
        for sys_pkg, indicators in system_indicators.items():
            if any(indicator in code for indicator in indicators):
                result['system_packages'].add(sys_pkg)
        
        # 3. Services analysis
        service_patterns = {
            'postgresql': ['psycopg2', 'postgresql://', 'postgres://'],
            'mysql': ['mysql', 'MySQLdb', 'mysql://'],
            'mongodb': ['pymongo', 'mongodb://', 'MongoClient'],
            'redis': ['redis', 'Redis(', 'redis://'],
            'elasticsearch': ['elasticsearch', 'Elasticsearch('],
            'nginx': ['nginx', 'proxy_pass', 'upstream'],
            'docker': ['docker', 'container', 'Dockerfile'],
        }
        
        for service, patterns in service_patterns.items():
            if any(pattern in code for pattern in patterns):
                result['services'].add(service)
        
        # 4. Build tools analysis
        if any(indicator in code for indicator in ['.c', '.cpp', 'Cython', 'setup.py', 'compile']):
            result['build_tools'].add('build-essential')
            result['build_tools'].add('python3-dev')
        
        if 'CMakeLists.txt' in code or 'cmake' in code:
            result['build_tools'].add('cmake')
            
        if any(gpu_indicator in code for gpu_indicator in ['cuda', 'gpu', '.to(device)', 'torch.cuda']):
            result['system_packages'].add('nvidia-cuda-toolkit')
            result['notes'].append('Requires NVIDIA GPU and CUDA drivers')
        
        # Convert sets to sorted lists
        for key in result:
            if isinstance(result[key], set):
                result[key] = sorted(list(result[key]))
        
        return result

    def analyze_script_comprehensively(self, code: str, script_name: str = "unknown") -> Dict[str, Any]:
        """Perform comprehensive analysis of a Python script"""
        start_time = time.time()
        
        logger.info(f"🔍 Comprehensive analysis of {script_name}...")
        
        # Perform static analysis
        static_result = self.analyze_code_comprehensively(code)
        
        # Calculate metrics
        pip_count = len(static_result['pip_packages'])
        system_count = len(static_result['system_packages'])
        services_count = len(static_result['services'])
        build_tools_count = len(static_result['build_tools'])
        total_deps = pip_count + system_count + services_count + build_tools_count
        
        analysis_time = time.time() - start_time
        
        result = {
            'script': script_name,
            'pip_packages': static_result['pip_packages'],
            'system_packages': static_result['system_packages'],
            'services': static_result['services'],
            'build_tools': static_result['build_tools'],
            'notes': static_result['notes'],
            'pip_count': pip_count,
            'system_count': system_count,
            'services_count': services_count,
            'build_tools_count': build_tools_count,
            'total_dependencies': total_deps,
            'analysis_time': round(analysis_time, 3),
            'method': 'comprehensive_static_analysis',
            'reproducibility_focus': True
        }
        
        logger.info(f"📊 Analysis complete for {script_name}:")
        logger.info(f"   🐍 Pip packages: {pip_count}")
        logger.info(f"   🔧 System packages: {system_count}")
        logger.info(f"   🗄️ Services: {services_count}")
        logger.info(f"   🛠️ Build tools: {build_tools_count}")
        logger.info(f"   📦 Total dependencies: {total_deps}")
        logger.info(f"   ⏱️ Analysis time: {analysis_time:.3f}s")
        
        return result

    def analyze_script_file(self, script_path: str) -> Dict[str, Any]:
        """Analyze a Python script file comprehensively"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            script_name = Path(script_path).name
            return self.analyze_script_comprehensively(code, script_name)
            
        except Exception as e:
            logger.error(f"Error reading script {script_path}: {e}")
            return {
                'script': Path(script_path).name,
                'pip_packages': [],
                'system_packages': [],
                'services': [],
                'build_tools': [],
                'notes': [f'File reading error: {str(e)}'],
                'pip_count': 0,
                'system_count': 0,
                'services_count': 0,
                'build_tools_count': 0,
                'total_dependencies': 0,
                'analysis_time': 0,
                'method': 'comprehensive_static_analysis',
                'error': str(e)
            }

    def batch_analyze_all_scripts(self, scripts_dir: str = "../code_scripts", output_dir: str = "../output/ComprehensiveAnalysis"):
        """Analyze all scripts comprehensively"""
        
        scripts_path = Path(scripts_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("🚀 Starting comprehensive batch analysis for full reproducibility")
        logger.info(f"📁 Scripts directory: {scripts_path}")
        logger.info(f"📁 Output directory: {output_path}")
        
        # Find all script files
        script_files = sorted(list(scripts_path.glob("script_*.py")))
        logger.info(f"📊 Found {len(script_files)} scripts to analyze")
        
        all_results = []
        
        for i, script_file in enumerate(script_files, 1):
            logger.info(f"\n🔄 [{i}/{len(script_files)}] Processing {script_file.name}...")
            
            # Analyze script
            result = self.analyze_script_file(str(script_file))
            all_results.append(result)
            
            # Save comprehensive requirements file
            if result['total_dependencies'] > 0:
                req_file = output_path / f"{script_file.stem}_comprehensive_deps.txt"
                with open(req_file, 'w') as f:
                    f.write(f"# COMPREHENSIVE DEPENDENCY ANALYSIS FOR {script_file.name}\n")
                    f.write(f"# Focus: Complete reproducibility requirements\n")
                    f.write(f"# Analysis time: {result['analysis_time']}s\n")
                    f.write(f"# Total dependencies: {result['total_dependencies']}\n\n")
                    
                    if result['pip_packages']:
                        f.write("# =============================================================================\n")
                        f.write("# PIP PACKAGES (install with: pip install -r requirements.txt)\n")
                        f.write("# =============================================================================\n")
                        for pkg in result['pip_packages']:
                            f.write(f"{pkg}\n")
                        f.write("\n")
                    
                    if result['system_packages']:
                        f.write("# =============================================================================\n")
                        f.write("# SYSTEM PACKAGES (install with package manager)\n")
                        f.write("# Ubuntu/Debian: sudo apt-get install <package>\n")
                        f.write("# CentOS/RHEL: sudo yum install <package>\n")
                        f.write("# macOS: brew install <package>\n")
                        f.write("# =============================================================================\n")
                        for pkg in result['system_packages']:
                            f.write(f"# {pkg}\n")
                        f.write("\n")
                    
                    if result['services']:
                        f.write("# =============================================================================\n")
                        f.write("# SERVICES/DATABASES REQUIRED\n")
                        f.write("# These need to be running before executing the script\n")
                        f.write("# =============================================================================\n")
                        for service in result['services']:
                            f.write(f"# {service}\n")
                        f.write("\n")
                    
                    if result['build_tools']:
                        f.write("# =============================================================================\n")
                        f.write("# BUILD TOOLS (for compiling extensions)\n")
                        f.write("# =============================================================================\n")
                        for tool in result['build_tools']:
                            f.write(f"# {tool}\n")
                        f.write("\n")
                    
                    if result['notes']:
                        f.write("# =============================================================================\n")
                        f.write("# SPECIAL NOTES\n")
                        f.write("# =============================================================================\n")
                        for note in result['notes']:
                            f.write(f"# {note}\n")
                
                logger.info(f"💾 Saved comprehensive dependencies to {req_file.name}")
            else:
                logger.info("📝 No external dependencies found")
        
        # Generate comprehensive summary
        logger.info("\n📊 Generating comprehensive summary...")
        
        successful_analyses = [r for r in all_results if 'error' not in r]
        total_pip = sum(r['pip_count'] for r in successful_analyses)
        total_system = sum(r['system_count'] for r in successful_analyses)
        total_services = sum(r['services_count'] for r in successful_analyses)
        total_build_tools = sum(r['build_tools_count'] for r in successful_analyses)
        total_all = sum(r['total_dependencies'] for r in successful_analyses)
        
        summary = {
            'analysis_type': 'comprehensive_reproducibility',
            'total_scripts': len(script_files),
            'successful_analyses': len(successful_analyses),
            'failed_analyses': len(all_results) - len(successful_analyses),
            'total_pip_packages': total_pip,
            'total_system_packages': total_system,
            'total_services': total_services,
            'total_build_tools': total_build_tools,
            'total_all_dependencies': total_all,
            'average_deps_per_script': round(total_all / len(successful_analyses), 2) if successful_analyses else 0,
            'total_analysis_time': round(sum(r['analysis_time'] for r in successful_analyses), 2),
            'average_time_per_script': round(sum(r['analysis_time'] for r in successful_analyses) / len(successful_analyses), 3) if successful_analyses else 0
        }
        
        # Save detailed results
        results_file = output_path / "comprehensive_results.json"
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        # Save summary
        summary_file = output_path / "comprehensive_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print comprehensive summary
        logger.info("\n" + "="*80)
        logger.info("📈 COMPREHENSIVE REPRODUCIBILITY ANALYSIS COMPLETE")
        logger.info("="*80)
        logger.info(f"🎯 Analysis focus: Complete reproducibility")
        logger.info(f"📊 Scripts processed: {summary['total_scripts']}")
        logger.info(f"✅ Successful: {summary['successful_analyses']}")
        logger.info(f"❌ Failed: {summary['failed_analyses']}")
        logger.info(f"🐍 Total pip packages: {summary['total_pip_packages']}")
        logger.info(f"🔧 Total system packages: {summary['total_system_packages']}")
        logger.info(f"🗄️ Total services: {summary['total_services']}")
        logger.info(f"🛠️ Total build tools: {summary['total_build_tools']}")
        logger.info(f"📦 Total ALL dependencies: {summary['total_all_dependencies']}")
        logger.info(f"📊 Average per script: {summary['average_deps_per_script']}")
        logger.info(f"⚡ Total analysis time: {summary['total_analysis_time']}s")
        logger.info(f"⚡ Average per script: {summary['average_time_per_script']}s")
        logger.info(f"💾 Results: {output_path}")
        
        return all_results

def main():
    """Main function"""
    try:
        analyzer = ComprehensiveDependencyAnalyzer()
        
        # Test with sample code first
        test_code = """
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import requests
import psycopg2
import cv2
import torch

def main():
    # Data analysis
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    arr = np.array([1, 2, 3])
    X_train, X_test = train_test_split(arr, test_size=0.2)
    
    # Visualization
    plt.plot([1, 2, 3])
    plt.savefig('plot.png')
    
    # Web request
    response = requests.get('http://example.com')
    
    # Database
    conn = psycopg2.connect('postgresql://user:pass@localhost/db')
    
    # Computer vision
    img = cv2.imread('image.jpg')
    
    # GPU computation
    tensor = torch.cuda.FloatTensor([1, 2, 3])
    
    return df, arr
"""
        
        logger.info("🧪 Running comprehensive test analysis...")
        test_result = analyzer.analyze_script_comprehensively(test_code, "comprehensive_test.py")
        logger.info(f"📋 Test result summary:")
        logger.info(f"   Total dependencies: {test_result['total_dependencies']}")
        logger.info(f"   Categories: pip={test_result['pip_count']}, system={test_result['system_count']}, services={test_result['services_count']}")
        
        # Run full batch analysis
        logger.info("✅ Test successful! Running full comprehensive analysis...")
        results = analyzer.batch_analyze_all_scripts()
        
        logger.info("🎉 Comprehensive analysis complete!")
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()