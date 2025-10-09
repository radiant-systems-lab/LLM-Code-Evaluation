#!/usr/bin/env python3
"""
Libraries.io API Data Collector
Fetches real data from Libraries.io's 45M+ package database using their official API
"""

import requests
import json
import time
import ast
from pathlib import Path
from collections import Counter
from typing import Dict, List, Optional

class LibrariesIOAPICollector:
    """Official Libraries.io API collector"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://libraries.io/api"
        self.session = requests.Session()
        self.session.params['api_key'] = api_key
        self.session.headers.update({
            'User-Agent': 'DepLLM-Research/1.0'
        })

        # Rate limiting: 60 requests per minute
        self.requests_per_minute = 60
        self.request_interval = 60.0 / self.requests_per_minute
        self.last_request_time = 0

        print(f"🌍 Libraries.io API Collector initialized")
        print(f"📊 Rate limit: {self.requests_per_minute} requests/minute")
        print(f"🔗 API Base: {self.base_url}")

    def _wait_for_rate_limit(self):
        """Ensure we respect the 60 requests/minute limit"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_interval:
            sleep_time = self.request_interval - time_since_last + 0.1  # Small buffer
            print(f"   ⏱️  Rate limiting: waiting {sleep_time:.1f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def get_package_info(self, platform: str, name: str) -> Optional[Dict]:
        """Get package info from Libraries.io API

        Endpoint: GET https://libraries.io/api/:platform/:name
        """
        self._wait_for_rate_limit()

        try:
            url = f"{self.base_url}/{platform}/{name}"
            print(f"   🌐 GET {url}")

            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"   ❌ Package not found: {platform}/{name}")
                return None
            else:
                print(f"   ⚠️  HTTP {response.status_code}: {response.text[:100]}")
                return None

        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout fetching {platform}/{name}")
            return None
        except Exception as e:
            print(f"   ❌ Error fetching {platform}/{name}: {e}")
            return None

    def get_package_dependencies(self, platform: str, name: str, version: str = None) -> Optional[List]:
        """Get package dependencies from Libraries.io API

        Endpoint: GET https://libraries.io/api/:platform/:name/:version/dependencies
        or GET https://libraries.io/api/:platform/:name/latest/dependencies
        """
        self._wait_for_rate_limit()

        try:
            if version:
                url = f"{self.base_url}/{platform}/{name}/{version}/dependencies"
            else:
                url = f"{self.base_url}/{platform}/{name}/latest/dependencies"

            print(f"   🔗 GET {url}")

            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"   ⚠️  Dependencies HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"   ⚠️  Error fetching dependencies: {e}")
            return []

    def extract_all_imports(self) -> Dict[str, List[str]]:
        """Extract all imports from all Python scripts"""
        script_imports = {}
        code_path = Path("../code_scripts")

        print(f"🔍 Extracting imports from {code_path}")

        for script_file in code_path.glob("script_*.py"):
            imports = []
            try:
                with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Parse imports using AST
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module.split('.')[0])

                script_imports[script_file.name] = list(set(imports))
                print(f"   📄 {script_file.name}: {len(set(imports))} unique imports")

            except Exception as e:
                print(f"   ⚠️  Error parsing {script_file.name}: {e}")

        return script_imports

    def map_imports_to_pypi(self, imports: List[str]) -> Dict[str, str]:
        """Map Python import names to PyPI package names"""

        # Known import -> PyPI package mappings
        import_to_pypi = {
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'Image': 'Pillow',
            'ImageDraw': 'Pillow',
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
        }

        # Python standard library modules to skip
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

        pypi_mapping = {}
        for imp in imports:
            if imp not in stdlib_modules and imp.strip():
                pypi_name = import_to_pypi.get(imp, imp)
                pypi_mapping[imp] = pypi_name

        return pypi_mapping

    def collect_all_packages(self, max_packages: int = None) -> Dict[str, Dict]:
        """Collect data for ALL packages from Libraries.io API"""

        print(f"\n🚀 Starting Libraries.io API Collection")
        print("=" * 60)

        # Extract all imports
        script_imports = self.extract_all_imports()
        all_imports = []
        for imports in script_imports.values():
            all_imports.extend(imports)

        import_frequency = Counter(all_imports)
        pypi_mapping = self.map_imports_to_pypi(list(import_frequency.keys()))

        print(f"\n📊 Collection Summary:")
        print(f"   Scripts analyzed: {len(script_imports)}")
        print(f"   Unique imports found: {len(import_frequency)}")
        print(f"   PyPI packages to collect: {len(pypi_mapping)}")

        if max_packages:
            print(f"   Limited to: {max_packages} packages")

        # Sort by usage frequency
        sorted_imports = sorted(pypi_mapping.items(),
                              key=lambda x: import_frequency[x[0]],
                              reverse=True)

        print(f"\n🔝 Top packages to collect:")
        for i, (imp, pypi) in enumerate(sorted_imports[:15]):
            freq = import_frequency[imp]
            print(f"   {i+1:2d}. {pypi:20} (import: {imp:12}) - {freq} scripts")

        # Collect data from Libraries.io API
        collected_packages = {}
        successful = 0
        failed = 0

        packages_to_collect = sorted_imports[:max_packages] if max_packages else sorted_imports

        print(f"\n📦 Collecting from Libraries.io API...")
        print("-" * 60)

        for i, (import_name, pypi_name) in enumerate(packages_to_collect):
            usage_freq = import_frequency[import_name]
            usage_pct = round((usage_freq / len(script_imports)) * 100, 1)

            print(f"\n[{i+1:3d}/{len(packages_to_collect):3d}] {pypi_name}")
            print(f"   Import: {import_name} | Usage: {usage_freq} scripts ({usage_pct}%)")

            # Get package info from Libraries.io
            package_info = self.get_package_info('pypi', pypi_name)

            if package_info:
                # Get dependencies
                dependencies = self.get_package_dependencies('pypi', pypi_name)

                # Create the same structure as your existing data
                collected_packages[import_name] = {
                    "pypi_name": pypi_name,
                    "import_name": import_name,
                    "usage_frequency": usage_freq,
                    "usage_percentage": usage_pct,
                    "package_info": {
                        "name": package_info.get('name', ''),
                        "platform": package_info.get('platform', ''),
                        "description": package_info.get('description', ''),
                        "homepage": package_info.get('homepage', ''),
                        "repository_url": package_info.get('repository_url', ''),
                        "licenses": package_info.get('normalized_licenses', []),
                        "rank": package_info.get('rank', 0),
                        "dependents_count": package_info.get('dependents_count', 0),
                        "dependent_repos_count": package_info.get('dependent_repos_count', 0),
                        "latest_stable_release": package_info.get('latest_stable_release_number', ''),
                        "latest_stable_release_published_at": package_info.get('latest_stable_release_published_at', ''),
                        "created_at": package_info.get('created_at', ''),
                        "updated_at": package_info.get('updated_at', '')
                    },
                    "dependencies": dependencies if dependencies else []
                }

                # Print success info
                rank = package_info.get('rank', 0)
                dependents = package_info.get('dependents_count', 0)
                deps_count = len(dependencies) if dependencies else 0
                latest = package_info.get('latest_stable_release_number', 'N/A')

                print(f"   ✅ Rank: #{rank:,} | Dependents: {dependents:,} | Deps: {deps_count} | Latest: {latest}")
                successful += 1

            else:
                print(f"   ❌ Failed to fetch from Libraries.io")
                failed += 1

        print(f"\n" + "=" * 60)
        print(f"📊 Collection Results:")
        print(f"   ✅ Successfully collected: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📈 Success rate: {(successful/(successful+failed)*100):.1f}%")

        return collected_packages, script_imports

    def save_libraries_io_data(self, collected_packages: Dict, script_imports: Dict,
                              output_file: str = "complete_libraries_io_packages.json"):
        """Save the complete Libraries.io dataset"""

        print(f"\n💾 Saving Libraries.io data to {output_file}")

        # Save the main package data (same format as your existing file)
        with open(output_file, 'w') as f:
            json.dump(collected_packages, f, indent=2, default=str)

        # Save script imports separately
        with open("script_imports_mapping.json", 'w') as f:
            json.dump(script_imports, f, indent=2)

        # Create summary statistics
        stats = {
            "collection_info": {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "api_source": "Libraries.io Official API",
                "total_packages": len(collected_packages),
                "total_scripts": len(script_imports),
                "api_key_used": True
            },
            "package_summary": {
                "total_collected": len(collected_packages),
                "avg_dependents": sum(pkg['package_info']['dependents_count']
                                    for pkg in collected_packages.values()) / len(collected_packages) if collected_packages else 0,
                "total_dependencies": sum(len(pkg['dependencies'])
                                        for pkg in collected_packages.values()),
                "top_by_usage": [
                    {
                        "import_name": pkg['import_name'],
                        "pypi_name": pkg['pypi_name'],
                        "usage_frequency": pkg['usage_frequency'],
                        "rank": pkg['package_info']['rank']
                    }
                    for pkg in sorted(collected_packages.values(),
                                    key=lambda x: x['usage_frequency'],
                                    reverse=True)[:20]
                ]
            }
        }

        with open("libraries_io_collection_stats.json", 'w') as f:
            json.dump(stats, f, indent=2, default=str)

        print(f"✅ Saved Libraries.io dataset!")
        print(f"   📄 {output_file} - Main package data ({len(collected_packages)} packages)")
        print(f"   📄 script_imports_mapping.json - Script import mapping")
        print(f"   📄 libraries_io_collection_stats.json - Collection statistics")

        return stats

def main():
    """Main collection process"""
    print("🌍 Libraries.io Official API Data Collection")
    print("Accessing 45M+ packages from Libraries.io database")
    print("=" * 80)

    # Initialize with your API key
    API_KEY = "b6a94607560db5e63b31153f41d37c68"
    collector = LibrariesIOAPICollector(API_KEY)

    # Collect packages (adjust max_packages as needed)
    print("Starting collection... (use Ctrl+C to stop early if needed)")
    collected_packages, script_imports = collector.collect_all_packages(max_packages=100)

    # Save the data
    stats = collector.save_libraries_io_data(collected_packages, script_imports)

    print(f"\n🎉 Libraries.io Collection Complete!")
    print(f"\n📊 Final Statistics:")
    print(f"   • Total packages from Libraries.io: {stats['collection_info']['total_packages']}")
    print(f"   • Scripts analyzed: {stats['collection_info']['total_scripts']}")
    print(f"   • Average dependents per package: {stats['package_summary']['avg_dependents']:,.0f}")
    print(f"   • Total dependency relationships: {stats['package_summary']['total_dependencies']}")

    print(f"\n✅ Complete Libraries.io dataset ready for DepLLM!")

if __name__ == "__main__":
    main()