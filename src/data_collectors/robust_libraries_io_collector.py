#!/usr/bin/env python3
"""
Robust Libraries.io Data Collector
Collects ALL packages with retry logic, caching, and batch processing
"""

import requests
import json
import time
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import ast
import re
from collections import Counter
import pickle

class RobustLibrariesIOCollector:
    """Robust collector with retry logic and caching"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://libraries.io/api"
        self.session = requests.Session()
        self.session.params['api_key'] = api_key

        # More robust settings
        self.session.timeout = 30
        self.session.headers.update({
            'User-Agent': 'DepLLM-Research-Collector/1.0'
        })

        # Rate limiting and retry logic
        self.rate_limit = 55  # Slightly under 60 to be safe
        self.request_interval = 60 / self.rate_limit
        self.last_request_time = 0
        self.max_retries = 3
        self.retry_delay = 2

        # Caching
        self.cache_file = Path("libraries_io_cache.pkl")
        self.package_cache = self.load_cache()

        print(f"🛡️  Robust Libraries.io Collector initialized")
        print(f"📊 Rate limit: {self.rate_limit} requests/minute")
        print(f"💾 Cache: {len(self.package_cache)} packages loaded")

    def load_cache(self) -> Dict:
        """Load cached package data"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        return {}

    def save_cache(self):
        """Save package cache"""
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.package_cache, f)

    def _respect_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_interval:
            sleep_time = self.request_interval - time_since_last
            print(f"   ⏱️  Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_request_with_retry(self, url: str, description: str = "") -> Optional[Dict]:
        """Make HTTP request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                self._respect_rate_limit()

                response = self.session.get(url, timeout=30)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                elif response.status_code == 429:
                    print(f"   ⚠️  Rate limited, waiting longer...")
                    time.sleep(60)  # Wait a full minute
                    continue
                else:
                    print(f"   ⚠️  HTTP {response.status_code} for {description}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    return None

            except requests.exceptions.Timeout:
                print(f"   ⏰ Timeout on attempt {attempt + 1} for {description}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return None
            except Exception as e:
                print(f"   ❌ Error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return None

        return None

    def get_all_script_imports(self) -> Dict[str, List[str]]:
        """Get all imports from all scripts"""
        script_imports = {}
        code_path = Path("../code_scripts")

        print(f"🔍 Extracting imports from all scripts...")

        for script_file in code_path.glob("script_*.py"):
            imports = []
            try:
                with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Use AST parsing
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom) and node.module:
                            imports.append(node.module.split('.')[0])
                except:
                    # Regex fallback
                    for line in content.split('\\n'):
                        line = line.strip()
                        if line.startswith('import '):
                            parts = line.split()
                            if len(parts) >= 2:
                                imports.append(parts[1].split('.')[0])
                        elif line.startswith('from ') and ' import ' in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                imports.append(parts[1].split('.')[0])

                script_imports[script_file.name] = list(set(imports))

            except Exception as e:
                print(f"   ⚠️  Error reading {script_file.name}: {e}")

        print(f"✅ Extracted imports from {len(script_imports)} scripts")
        return script_imports

    def map_all_imports_to_pypi(self, all_imports: List[str]) -> Dict[str, str]:
        """Map ALL imports to PyPI packages"""

        # Comprehensive mapping
        import_to_pypi = {
            # Common mappings
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'Image': 'Pillow',
            'ImageDraw': 'Pillow',
            'ImageFont': 'Pillow',
            'sklearn': 'scikit-learn',
            'yaml': 'PyYAML',
            'dateutil': 'python-dateutil',
            'serial': 'pyserial',
            'crypto': 'pycrypto',
            'Crypto': 'pycrypto',
            'jwt': 'PyJWT',
            'bs4': 'beautifulsoup4',
            'psycopg2': 'psycopg2-binary',
            'MySQLdb': 'mysqlclient',
            'requests_oauthlib': 'requests-oauthlib',
            'google': 'google-api-python-client',
            'openai': 'openai',
            'anthropic': 'anthropic',
            'transformers': 'transformers',
            'torch': 'torch',
            'torchvision': 'torchvision',
            'tensorflow': 'tensorflow',
            'keras': 'keras',
            'skimage': 'scikit-image',

            # Data science stack
            'pandas': 'pandas',
            'numpy': 'numpy',
            'scipy': 'scipy',
            'matplotlib': 'matplotlib',
            'seaborn': 'seaborn',
            'plotly': 'plotly',
            'bokeh': 'bokeh',

            # Web and networking
            'requests': 'requests',
            'urllib3': 'urllib3',
            'flask': 'Flask',
            'django': 'Django',
            'fastapi': 'fastapi',

            # Database
            'sqlalchemy': 'SQLAlchemy',
            'pymongo': 'pymongo',
            'redis': 'redis',

            # Utilities
            'click': 'click',
            'tqdm': 'tqdm',
            'rich': 'rich',
            'colorama': 'colorama',
            'python_dotenv': 'python-dotenv',
            'pydantic': 'pydantic'
        }

        # Standard library modules to skip
        stdlib_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'math', 'random', 're',
            'collections', 'itertools', 'functools', 'operator', 'string', 'io',
            'pathlib', 'urllib', 'http', 'socket', 'threading', 'multiprocessing',
            'subprocess', 'pickle', 'csv', 'xml', 'html', 'email', 'base64',
            'hashlib', 'hmac', 'logging', 'unittest', 'argparse', 'configparser',
            'tempfile', 'shutil', 'glob', 'fnmatch', 'linecache', 'textwrap',
            'unicodedata', 'struct', 'codecs', 'locale', 'calendar', 'pprint',
            'reprlib', 'enum', 'copy', 'types', 'weakref', 'gc', 'inspect',
            'site', 'importlib', 'sqlite3', 'contextlib', 'secrets', 'queue',
            'concurrent', 'asyncio', 'typing', 'dataclasses', 'abc', 'warnings'
        }

        # Filter and map
        pypi_mapping = {}
        for import_name in set(all_imports):
            if import_name not in stdlib_modules and import_name.strip():
                pypi_name = import_to_pypi.get(import_name, import_name)
                pypi_mapping[import_name] = pypi_name

        return pypi_mapping

    def collect_package_data(self, pypi_name: str, import_name: str, usage_count: int) -> Optional[Dict]:
        """Collect comprehensive package data"""

        # Check cache first
        cache_key = f"{pypi_name}_data"
        if cache_key in self.package_cache:
            print(f"   💾 Using cached data for {pypi_name}")
            cached_data = self.package_cache[cache_key].copy()
            cached_data['usage_frequency'] = usage_count
            return cached_data

        print(f"   🌐 Fetching fresh data for {pypi_name}...")

        # Fetch package info
        package_url = f"{self.base_url}/pypi/{pypi_name}"
        package_data = self._make_request_with_retry(package_url, f"package {pypi_name}")

        if not package_data:
            return None

        # Fetch dependencies
        deps_url = f"{self.base_url}/pypi/{pypi_name}/latest/dependencies"
        dependencies = self._make_request_with_retry(deps_url, f"dependencies for {pypi_name}")
        if dependencies is None:
            dependencies = []

        # Fetch versions (first 10)
        versions_url = f"{self.base_url}/pypi/{pypi_name}/versions"
        versions = self._make_request_with_retry(versions_url, f"versions for {pypi_name}")
        if versions is None:
            versions = []

        # Create comprehensive package record
        package_record = {
            'import_name': import_name,
            'pypi_name': pypi_name,
            'usage_frequency': usage_count,
            'package_info': {
                'name': package_data.get('name', pypi_name),
                'platform': package_data.get('platform', 'pypi'),
                'description': package_data.get('description', ''),
                'homepage': package_data.get('homepage', ''),
                'repository_url': package_data.get('repository_url', ''),
                'licenses': package_data.get('normalized_licenses', []),
                'keywords': package_data.get('keywords', []),
                'rank': package_data.get('rank', 0),
                'dependents_count': package_data.get('dependents_count', 0),
                'dependent_repos_count': package_data.get('dependent_repos_count', 0),
                'latest_stable_release': package_data.get('latest_stable_release_number', ''),
                'latest_stable_release_published_at': package_data.get('latest_stable_release_published_at', ''),
                'created_at': package_data.get('created_at', ''),
                'updated_at': package_data.get('updated_at', ''),
                'forks': package_data.get('forks', 0),
                'stars': package_data.get('stars', 0),
                'language': package_data.get('language', ''),
                'status': package_data.get('status', ''),
            },
            'dependencies': dependencies[:50],  # Limit to first 50 deps
            'versions': versions[:20] if isinstance(versions, list) else [],  # Limit to first 20 versions
            'dependency_count': len(dependencies) if isinstance(dependencies, list) else 0,
            'collected_at': time.time()
        }

        # Cache the result
        self.package_cache[cache_key] = package_record.copy()
        self.save_cache()

        return package_record

    def collect_all_packages(self, max_packages: int = 100) -> Dict[str, Dict]:
        """Collect ALL packages robustly"""

        print(f"🚀 Starting comprehensive package collection (max: {max_packages})")
        print("=" * 70)

        # Get all script imports
        script_imports = self.get_all_script_imports()

        # Get import frequency
        all_imports = []
        for imports in script_imports.values():
            all_imports.extend(imports)

        import_frequency = Counter(all_imports)
        print(f"📊 Found {len(import_frequency)} unique imports")

        # Map to PyPI
        pypi_mapping = self.map_all_imports_to_pypi(list(import_frequency.keys()))
        print(f"📦 Mapped {len(pypi_mapping)} imports to PyPI packages")

        # Sort by frequency for priority collection
        sorted_imports = sorted(pypi_mapping.items(),
                              key=lambda x: import_frequency[x[0]],
                              reverse=True)

        print(f"\\n🔝 Top imports to collect:")
        for i, (imp, pypi) in enumerate(sorted_imports[:15]):
            freq = import_frequency[imp]
            print(f"   {i+1:2d}. {pypi:20} (import: {imp:15}) - {freq:2d} scripts")

        # Collect package data
        collected_data = {}
        successful = 0
        failed = 0

        print(f"\\n📦 Collecting package data...")
        print("-" * 50)

        for i, (import_name, pypi_name) in enumerate(sorted_imports[:max_packages]):
            usage_count = import_frequency[import_name]

            print(f"\\n[{i+1:3d}/{min(max_packages, len(sorted_imports)):3d}] {pypi_name}")
            print(f"   Import: {import_name}, Used in: {usage_count} scripts")

            package_data = self.collect_package_data(pypi_name, import_name, usage_count)

            if package_data:
                collected_data[import_name] = package_data
                info = package_data['package_info']
                print(f"   ✅ Rank: #{info['rank']:,} | Dependents: {info['dependents_count']:,}")
                print(f"   🔗 Dependencies: {package_data['dependency_count']} | Latest: {info['latest_stable_release']}")
                successful += 1
            else:
                print(f"   ❌ Failed to collect data")
                failed += 1

        print(f"\\n" + "=" * 70)
        print(f"📊 Collection Summary:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📈 Success rate: {(successful/(successful+failed)*100):.1f}%")
        print(f"   💾 Cache size: {len(self.package_cache)} packages")

        return collected_data, script_imports

    def save_comprehensive_dataset(self, collected_data: Dict, script_imports: Dict,
                                 output_dir: str = "comprehensive_libraries_io_data"):
        """Save the complete dataset"""

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        print(f"\\n💾 Saving comprehensive dataset to {output_dir}/")

        # 1. Complete package data
        with open(output_path / "complete_libraries_io_data.json", 'w') as f:
            json.dump(collected_data, f, indent=2, default=str)

        # 2. Script imports
        with open(output_path / "all_script_imports.json", 'w') as f:
            json.dump(script_imports, f, indent=2)

        # 3. Summary CSV
        summary_data = []
        for import_name, data in collected_data.items():
            info = data['package_info']
            summary_data.append({
                'import_name': import_name,
                'pypi_name': data['pypi_name'],
                'usage_frequency': data['usage_frequency'],
                'rank': info['rank'],
                'dependents_count': info['dependents_count'],
                'dependency_count': data['dependency_count'],
                'latest_version': info['latest_stable_release'],
                'stars': info.get('stars', 0),
                'forks': info.get('forks', 0),
                'created_at': info['created_at'][:10] if info['created_at'] else '',
                'description': info['description'][:200] if info['description'] else ''
            })

        df = pd.DataFrame(summary_data)
        df = df.sort_values('usage_frequency', ascending=False)
        df.to_csv(output_path / "comprehensive_package_summary.csv", index=False)

        # 4. Dependency relationships
        dep_relationships = []
        for import_name, data in collected_data.items():
            for dep in data['dependencies']:
                if isinstance(dep, dict):
                    dep_relationships.append({
                        'package': data['pypi_name'],
                        'depends_on': dep.get('project_name', ''),
                        'requirement': dep.get('requirements', ''),
                        'kind': dep.get('kind', 'runtime'),
                        'optional': dep.get('optional', False)
                    })

        if dep_relationships:
            dep_df = pd.DataFrame(dep_relationships)
            dep_df.to_csv(output_path / "all_dependency_relationships.csv", index=False)

        # 5. Statistics
        stats = {
            'collection_summary': {
                'total_scripts_analyzed': len(script_imports),
                'total_packages_collected': len(collected_data),
                'total_unique_imports': len(set().union(*script_imports.values())),
                'total_dependency_relationships': len(dep_relationships),
                'collection_timestamp': time.time(),
                'api_key_used': True
            },
            'top_packages_by_usage': [
                {'import': imp, 'usage': data['usage_frequency'], 'pypi': data['pypi_name']}
                for imp, data in sorted(collected_data.items(),
                                      key=lambda x: x[1]['usage_frequency'],
                                      reverse=True)[:20]
            ],
            'ecosystem_stats': {
                'avg_dependencies_per_package': sum(d['dependency_count'] for d in collected_data.values()) / len(collected_data) if collected_data else 0,
                'avg_dependents_per_package': sum(d['package_info']['dependents_count'] for d in collected_data.values()) / len(collected_data) if collected_data else 0,
                'packages_with_high_usage': len([d for d in collected_data.values() if d['usage_frequency'] >= 5])
            }
        }

        with open(output_path / "collection_statistics.json", 'w') as f:
            json.dump(stats, f, indent=2, default=str)

        print(f"✅ Comprehensive dataset saved!")
        print(f"   📄 Files created:")
        print(f"      • complete_libraries_io_data.json ({len(collected_data)} packages)")
        print(f"      • all_script_imports.json ({len(script_imports)} scripts)")
        print(f"      • comprehensive_package_summary.csv")
        print(f"      • all_dependency_relationships.csv ({len(dep_relationships)} relationships)")
        print(f"      • collection_statistics.json")

        return output_path, stats

def main():
    """Comprehensive data collection"""
    print("🛡️  Robust Libraries.io Data Collection for DepLLM")
    print("=" * 80)

    # Initialize collector
    API_KEY = "b6a94607560db5e63b31153f41d37c68"
    collector = RobustLibrariesIOCollector(API_KEY)

    # Collect ALL packages (increase limit as needed)
    collected_data, script_imports = collector.collect_all_packages(max_packages=50)

    # Save comprehensive dataset
    output_path, stats = collector.save_comprehensive_dataset(collected_data, script_imports)

    print(f"\\n🎉 Comprehensive Collection Complete!")
    print(f"\\n📊 Final Statistics:")
    print(f"   • Scripts analyzed: {stats['collection_summary']['total_scripts_analyzed']}")
    print(f"   • Packages collected: {stats['collection_summary']['total_packages_collected']}")
    print(f"   • Dependency relationships: {stats['collection_summary']['total_dependency_relationships']}")
    print(f"   • Average dependencies per package: {stats['ecosystem_stats']['avg_dependencies_per_package']:.1f}")
    print(f"   • High-usage packages (5+ scripts): {stats['ecosystem_stats']['packages_with_high_usage']}")

    print(f"\\n📂 Complete dataset available in: {output_path}/")
    print(f"🚀 Ready for DepLLM development and analysis!")

if __name__ == "__main__":
    main()