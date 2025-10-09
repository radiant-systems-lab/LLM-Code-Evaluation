#!/usr/bin/env python3
"""
Scalable Libraries.io Data Collector
High-performance collector with robust error handling for large-scale data collection
"""

import requests
import json
import time
import ast
from pathlib import Path
from collections import Counter
from typing import Dict, List, Optional
import concurrent.futures
from threading import Lock
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScalableLibrariesCollector:
    """High-performance Libraries.io collector with concurrent processing"""

    def __init__(self, api_key: str, max_workers: int = 4):
        self.api_key = api_key
        self.base_url = "https://libraries.io/api"
        self.max_workers = max_workers
        self.collected_data = {}
        self.data_lock = Lock()

        # Rate limiting: 60 requests per minute
        self.request_interval = 60.0 / 60  # 1 second between requests
        self.last_request_time = 0
        self.time_lock = Lock()

        logger.info(f"🚀 Scalable Libraries.io Collector initialized")
        logger.info(f"📊 Max workers: {max_workers}")
        logger.info(f"⏱️ Rate limit: 60 requests/minute")

    def _wait_for_rate_limit(self):
        """Thread-safe rate limiting"""
        with self.time_lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time

            if time_since_last < self.request_interval:
                sleep_time = self.request_interval - time_since_last + 0.1
                time.sleep(sleep_time)

            self.last_request_time = time.time()

    def get_package_data(self, import_name: str, pypi_name: str, usage_freq: int, total_scripts: int) -> Optional[Dict]:
        """Get comprehensive package data with retries"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                self._wait_for_rate_limit()

                # Create session for this request
                session = requests.Session()
                session.params['api_key'] = self.api_key
                session.headers.update({'User-Agent': 'DepLLM-Research/1.0'})

                # Get package info
                url = f"{self.base_url}/pypi/{pypi_name}"
                logger.info(f"📡 Fetching {pypi_name} (attempt {attempt + 1})")

                response = session.get(url, timeout=20)

                if response.status_code == 200:
                    package_info = response.json()

                    # Get dependencies with shorter timeout
                    deps_url = f"{self.base_url}/pypi/{pypi_name}/latest/dependencies"
                    try:
                        deps_response = session.get(deps_url, timeout=15)
                        dependencies = deps_response.json() if deps_response.status_code == 200 else []
                    except:
                        dependencies = []

                    # Structure data
                    return {
                        "import_name": import_name,
                        "pypi_name": pypi_name,
                        "usage_frequency": usage_freq,
                        "usage_percentage": round((usage_freq / total_scripts) * 100, 1),
                        "package_info": {
                            "name": package_info.get('name', pypi_name),
                            "description": package_info.get('description', ''),
                            "homepage": package_info.get('homepage', ''),
                            "repository_url": package_info.get('repository_url', ''),
                            "rank": package_info.get('rank', 0),
                            "dependents_count": package_info.get('dependents_count', 0),
                            "latest_version": package_info.get('latest_stable_release_number', ''),
                            "created_at": package_info.get('created_at', ''),
                            "stars": package_info.get('stars', 0),
                            "language": package_info.get('language', 'Python'),
                            "licenses": package_info.get('normalized_licenses', [])
                        },
                        "dependencies": dependencies
                    }

                elif response.status_code == 404:
                    logger.warning(f"❌ Package not found: {pypi_name}")
                    return None
                else:
                    logger.warning(f"⚠️ HTTP {response.status_code} for {pypi_name}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    return None

            except requests.exceptions.Timeout:
                logger.warning(f"⏰ Timeout for {pypi_name} (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
            except Exception as e:
                logger.error(f"❌ Error with {pypi_name}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None

        return None

    def extract_all_imports(self) -> Dict[str, List[str]]:
        """Fast import extraction using AST"""
        script_imports = {}
        code_path = Path("../code_scripts")

        logger.info(f"🔍 Scanning {code_path} for imports...")

        for script_file in code_path.glob("script_*.py"):
            imports = []
            try:
                with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module.split('.')[0])

                script_imports[script_file.name] = list(set(imports))

            except Exception as e:
                logger.warning(f"⚠️ Error parsing {script_file.name}: {e}")

        return script_imports

    def map_imports_to_pypi(self, imports: List[str]) -> Dict[str, str]:
        """Enhanced import to PyPI mapping"""
        import_mapping = {
            'cv2': 'opencv-python', 'PIL': 'Pillow', 'sklearn': 'scikit-learn',
            'yaml': 'PyYAML', 'bs4': 'beautifulsoup4', 'psycopg2': 'psycopg2-binary',
            'dateutil': 'python-dateutil', 'serial': 'pyserial', 'crypto': 'pycrypto',
            'jwt': 'PyJWT', 'MySQLdb': 'mysqlclient', 'Image': 'Pillow',
            'ImageDraw': 'Pillow', 'Crypto': 'pycrypto'
        }

        # Expanded stdlib to filter out
        stdlib = {
            'os', 'sys', 'json', 'time', 'datetime', 'math', 'random', 're',
            'collections', 'itertools', 'functools', 'pathlib', 'urllib', 'http',
            'socket', 'threading', 'multiprocessing', 'subprocess', 'pickle',
            'csv', 'xml', 'html', 'email', 'base64', 'hashlib', 'hmac',
            'logging', 'unittest', 'argparse', 'configparser', 'tempfile',
            'shutil', 'glob', 'fnmatch', 'textwrap', 'struct', 'codecs',
            'calendar', 'enum', 'copy', 'types', 'weakref', 'gc', 'inspect',
            'sqlite3', 'contextlib', 'secrets', 'queue', 'concurrent',
            'asyncio', 'typing', 'dataclasses', 'abc', 'warnings', 'operator',
            'string', 'io', 'locale', 'pprint', 'reprlib', 'linecache',
            'unicodedata', 'site', 'importlib', 'ssl'
        }

        result = {}
        for imp in set(imports):
            if imp not in stdlib and imp.strip():
                result[imp] = import_mapping.get(imp, imp)

        return result

    def collect_packages_batch(self, packages_batch: List, total_scripts: int):
        """Collect a batch of packages"""
        for import_name, pypi_name, usage_freq in packages_batch:
            try:
                package_data = self.get_package_data(import_name, pypi_name, usage_freq, total_scripts)

                if package_data:
                    with self.data_lock:
                        self.collected_data[import_name] = package_data

                    rank = package_data['package_info']['rank']
                    dependents = package_data['package_info']['dependents_count']
                    deps_count = len(package_data['dependencies'])

                    logger.info(f"✅ {pypi_name}: Rank #{rank:,} | Deps: {dependents:,} | Dependencies: {deps_count}")
                else:
                    logger.warning(f"❌ Failed to collect {pypi_name}")

            except Exception as e:
                logger.error(f"❌ Batch error for {pypi_name}: {e}")

    def collect_all_packages(self, max_packages: int = None) -> Dict:
        """Main collection method with concurrent processing"""
        logger.info("🚀 Starting comprehensive Libraries.io collection")

        # Extract imports
        script_imports = self.extract_all_imports()
        all_imports = []
        for imports in script_imports.values():
            all_imports.extend(imports)

        import_frequency = Counter(all_imports)
        pypi_mapping = self.map_imports_to_pypi(list(import_frequency.keys()))

        total_scripts = len(script_imports)
        total_packages = len(pypi_mapping)

        logger.info(f"📊 Analysis Summary:")
        logger.info(f"   Scripts: {total_scripts}")
        logger.info(f"   Unique imports: {len(import_frequency)}")
        logger.info(f"   PyPI packages: {total_packages}")

        if max_packages:
            logger.info(f"   Limited to: {max_packages} packages")

        # Sort by frequency
        sorted_packages = sorted(pypi_mapping.items(),
                               key=lambda x: import_frequency[x[0]],
                               reverse=True)

        # Limit if requested
        if max_packages:
            sorted_packages = sorted_packages[:max_packages]

        # Show top packages
        logger.info("🔝 Top packages to collect:")
        for i, (imp, pypi) in enumerate(sorted_packages[:15]):
            freq = import_frequency[imp]
            logger.info(f"   {i+1:2d}. {pypi:20} (usage: {freq:2d}x)")

        # Create batches for processing
        packages_to_collect = [(imp, pypi, import_frequency[imp])
                             for imp, pypi in sorted_packages]

        # Process sequentially due to API rate limits (60/min)
        # Using threading would exceed rate limits
        logger.info(f"\n📦 Collecting {len(packages_to_collect)} packages...")

        start_time = time.time()
        successful = 0
        failed = 0

        for i, (import_name, pypi_name, usage_freq) in enumerate(packages_to_collect):
            logger.info(f"\n[{i+1:3d}/{len(packages_to_collect)}] Processing {pypi_name}")

            package_data = self.get_package_data(import_name, pypi_name, usage_freq, total_scripts)

            if package_data:
                self.collected_data[import_name] = package_data
                successful += 1
            else:
                failed += 1

        elapsed = time.time() - start_time

        logger.info(f"\n✅ Collection completed in {elapsed:.1f}s")
        logger.info(f"   Success: {successful} packages")
        logger.info(f"   Failed: {failed} packages")
        logger.info(f"   Success rate: {(successful/(successful+failed)*100):.1f}%")

        return self.collected_data, script_imports

    def save_comprehensive_dataset(self, collected_data: Dict, script_imports: Dict):
        """Save comprehensive dataset"""
        output_dir = Path("scalable_libraries_data")
        output_dir.mkdir(exist_ok=True)

        logger.info(f"💾 Saving comprehensive dataset to {output_dir}/")

        # Main dataset
        with open(output_dir / "comprehensive_libraries_data.json", 'w') as f:
            json.dump(collected_data, f, indent=2, default=str)

        # Script imports
        with open(output_dir / "script_imports_mapping.json", 'w') as f:
            json.dump(script_imports, f, indent=2)

        # Summary stats
        stats = {
            "collection_info": {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "api_source": "Libraries.io Official API",
                "total_packages": len(collected_data),
                "total_scripts": len(script_imports)
            },
            "package_summary": {
                "total_collected": len(collected_data),
                "avg_dependents": sum(pkg['package_info']['dependents_count']
                                    for pkg in collected_data.values()) / len(collected_data) if collected_data else 0,
                "total_dependencies": sum(len(pkg['dependencies'])
                                        for pkg in collected_data.values()),
                "top_by_usage": [
                    {
                        "import_name": pkg['import_name'],
                        "pypi_name": pkg['pypi_name'],
                        "usage_frequency": pkg['usage_frequency'],
                        "rank": pkg['package_info']['rank']
                    }
                    for pkg in sorted(collected_data.values(),
                                    key=lambda x: x['usage_frequency'],
                                    reverse=True)[:20]
                ]
            }
        }

        with open(output_dir / "collection_summary.json", 'w') as f:
            json.dump(stats, f, indent=2, default=str)

        logger.info(f"✅ Dataset saved:")
        logger.info(f"   📄 comprehensive_libraries_data.json - {len(collected_data)} packages")
        logger.info(f"   📄 script_imports_mapping.json - {len(script_imports)} scripts")
        logger.info(f"   📄 collection_summary.json - Statistics")

        return output_dir, stats

def main():
    """Main scalable collection process"""
    print("🚀 Scalable Libraries.io Data Collection")
    print("High-performance collection for comprehensive dependency analysis")
    print("=" * 80)

    # Initialize collector
    API_KEY = "b6a94607560db5e63b31153f41d37c68"
    collector = ScalableLibrariesCollector(API_KEY, max_workers=1)  # Sequential for rate limits

    # Collect comprehensive data (no limit = get ALL packages)
    print("Starting comprehensive collection...")
    collected_data, script_imports = collector.collect_all_packages()

    # Save dataset
    output_dir, stats = collector.save_comprehensive_dataset(collected_data, script_imports)

    print(f"\n🎉 Comprehensive Collection Complete!")
    print(f"\n📊 Final Results:")
    print(f"   • Total packages: {stats['collection_info']['total_packages']}")
    print(f"   • Scripts analyzed: {stats['collection_info']['total_scripts']}")
    print(f"   • Average dependents: {stats['package_summary']['avg_dependents']:,.0f}")
    print(f"   • Total dependencies: {stats['package_summary']['total_dependencies']}")
    print(f"\n📂 Complete dataset saved in: {output_dir}/")
    print(f"🎯 Ready for advanced dependency analysis!")

if __name__ == "__main__":
    main()