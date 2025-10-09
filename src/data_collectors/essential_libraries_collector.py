#!/usr/bin/env python3
"""
Essential Libraries.io Data Collector
Focuses on getting basic package info for ALL your imports - no complex dependencies
"""

import requests
import json
import time
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import ast
from collections import Counter

class EssentialLibrariesCollector:
    """Simple, reliable collector for essential package data"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://libraries.io/api"
        self.session = requests.Session()
        self.session.params['api_key'] = api_key
        self.session.timeout = 15

    def get_all_imports(self) -> Dict[str, List[str]]:
        """Get all imports from all scripts"""
        script_imports = {}
        code_path = Path("../code_scripts")

        for script_file in code_path.glob("script_*.py"):
            imports = []
            try:
                with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Simple AST parsing
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom) and node.module:
                            imports.append(node.module.split('.')[0])
                except:
                    pass

                script_imports[script_file.name] = list(set(imports))
            except:
                pass

        return script_imports

    def map_to_pypi(self, imports: List[str]) -> Dict[str, str]:
        """Map imports to PyPI names"""
        mapping = {
            'cv2': 'opencv-python', 'PIL': 'Pillow', 'sklearn': 'scikit-learn',
            'yaml': 'PyYAML', 'bs4': 'beautifulsoup4', 'psycopg2': 'psycopg2-binary'
        }

        stdlib = {
            'os', 'sys', 'json', 'time', 'datetime', 'math', 'random', 're',
            'collections', 'itertools', 'pathlib', 'urllib', 'http', 'socket',
            'threading', 'subprocess', 'pickle', 'csv', 'sqlite3', 'hashlib',
            'logging', 'unittest', 'argparse', 'tempfile', 'shutil', 'glob',
            'contextlib', 'secrets', 'queue', 'concurrent', 'typing', 'dataclasses'
        }

        result = {}
        for imp in set(imports):
            if imp not in stdlib and imp.strip():
                result[imp] = mapping.get(imp, imp)

        return result

    def get_basic_package_info(self, pypi_name: str) -> Optional[Dict]:
        """Get just basic package info - no dependencies"""
        try:
            url = f"{self.base_url}/pypi/{pypi_name}"
            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data.get('name', pypi_name),
                    'description': data.get('description', ''),
                    'homepage': data.get('homepage', ''),
                    'repository_url': data.get('repository_url', ''),
                    'rank': data.get('rank', 0),
                    'dependents_count': data.get('dependents_count', 0),
                    'latest_version': data.get('latest_stable_release_number', ''),
                    'created_at': data.get('created_at', ''),
                    'stars': data.get('stars', 0),
                    'language': data.get('language', ''),
                    'licenses': data.get('normalized_licenses', [])
                }
            return None
        except:
            return None

    def collect_all_essential_data(self):
        """Collect essential data for ALL imports"""
        print("🎯 Essential Libraries.io Data Collection")
        print("=" * 60)

        # Get all imports
        script_imports = self.get_all_imports()
        all_imports = []
        for imports in script_imports.values():
            all_imports.extend(imports)

        import_frequency = Counter(all_imports)
        pypi_mapping = self.map_to_pypi(list(import_frequency.keys()))

        print(f"📊 Found {len(script_imports)} scripts with {len(pypi_mapping)} unique PyPI packages")

        # Collect data for each package
        collected_data = {}
        successful = 0

        sorted_packages = sorted(pypi_mapping.items(),
                               key=lambda x: import_frequency[x[0]],
                               reverse=True)

        for i, (import_name, pypi_name) in enumerate(sorted_packages):
            usage_count = import_frequency[import_name]
            print(f"[{i+1:3d}/{len(sorted_packages)}] {pypi_name:20} (used {usage_count:2d}x)", end="")

            # Add small delay to respect rate limits
            if i > 0:
                time.sleep(1.2)  # Just over 1 second = under 60/minute

            package_info = self.get_basic_package_info(pypi_name)

            if package_info:
                collected_data[import_name] = {
                    'import_name': import_name,
                    'pypi_name': pypi_name,
                    'usage_frequency': usage_count,
                    'usage_percentage': round((usage_count / len(script_imports)) * 100, 1),
                    'package_info': package_info
                }
                print(f" ✅ Rank: {package_info['rank']:,} | Deps: {package_info['dependents_count']:,}")
                successful += 1
            else:
                print(f" ❌")

        print(f"\\n✅ Successfully collected {successful}/{len(sorted_packages)} packages")
        return collected_data, script_imports

    def save_essential_dataset(self, collected_data: Dict, script_imports: Dict):
        """Save the essential dataset"""
        output_dir = Path("essential_libraries_data")
        output_dir.mkdir(exist_ok=True)

        print(f"\\n💾 Saving essential dataset...")

        # 1. Complete package data
        with open(output_dir / "essential_libraries_data.json", 'w') as f:
            json.dump(collected_data, f, indent=2, default=str)

        # 2. Script imports
        with open(output_dir / "script_imports.json", 'w') as f:
            json.dump(script_imports, f, indent=2)

        # 3. Easy-to-read CSV
        csv_data = []
        for import_name, data in collected_data.items():
            info = data['package_info']
            csv_data.append({
                'import_name': import_name,
                'pypi_name': data['pypi_name'],
                'usage_frequency': data['usage_frequency'],
                'usage_percentage': data['usage_percentage'],
                'rank': info['rank'],
                'dependents_count': info['dependents_count'],
                'latest_version': info['latest_version'],
                'stars': info['stars'],
                'language': info['language'],
                'created_year': info['created_at'][:4] if info['created_at'] else '',
                'description': info['description'][:150] if info['description'] else '',
                'homepage': info['homepage'],
                'repository_url': info['repository_url']
            })

        df = pd.DataFrame(csv_data)
        df = df.sort_values('usage_frequency', ascending=False)
        df.to_csv(output_dir / "essential_packages.csv", index=False)

        # 4. Summary statistics
        stats = {
            'summary': {
                'total_scripts': len(script_imports),
                'total_packages_collected': len(collected_data),
                'success_rate': f"{len(collected_data)/len(set().union(*script_imports.values()) - {'os', 'sys', 'json', 'time', 'datetime', 'math', 'random'}) * 100:.1f}%",
                'collection_date': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'top_packages_by_usage': [
                {
                    'import_name': data['import_name'],
                    'pypi_name': data['pypi_name'],
                    'usage_frequency': data['usage_frequency'],
                    'rank': data['package_info']['rank'],
                    'dependents': data['package_info']['dependents_count']
                }
                for data in sorted(collected_data.values(),
                                 key=lambda x: x['usage_frequency'],
                                 reverse=True)[:20]
            ],
            'ecosystem_insights': {
                'avg_rank': sum(d['package_info']['rank'] for d in collected_data.values() if d['package_info']['rank'] > 0) / len([d for d in collected_data.values() if d['package_info']['rank'] > 0]) if collected_data else 0,
                'total_dependents': sum(d['package_info']['dependents_count'] for d in collected_data.values()),
                'packages_with_high_usage': len([d for d in collected_data.values() if d['usage_frequency'] >= 3])
            }
        }

        with open(output_dir / "collection_summary.json", 'w') as f:
            json.dump(stats, f, indent=2, default=str)

        print(f"✅ Essential dataset saved to {output_dir}/")
        print(f"   📄 Files:")
        print(f"      • essential_libraries_data.json - Complete data ({len(collected_data)} packages)")
        print(f"      • essential_packages.csv - Easy-to-read summary")
        print(f"      • script_imports.json - All script imports ({len(script_imports)} scripts)")
        print(f"      • collection_summary.json - Statistics and insights")

        return output_dir, stats

def main():
    """Main collection process"""
    print("🎯 Essential Libraries.io Data Collection for DepLLM")
    print("Collecting basic info for ALL your imports...")
    print()

    # Initialize
    API_KEY = "b6a94607560db5e63b31153f41d37c68"
    collector = EssentialLibrariesCollector(API_KEY)

    # Collect all data
    collected_data, script_imports = collector.collect_all_essential_data()

    # Save dataset
    output_path, stats = collector.save_essential_dataset(collected_data, script_imports)

    print(f"\\n🎉 Essential Collection Complete!")
    print(f"\\n📊 Final Results:")
    print(f"   • Scripts analyzed: {stats['summary']['total_scripts']}")
    print(f"   • Packages collected: {stats['summary']['total_packages_collected']}")
    print(f"   • Success rate: {stats['summary']['success_rate']}")
    print(f"   • Total dependents: {stats['ecosystem_insights']['total_dependents']:,}")
    print(f"   • High-usage packages: {stats['ecosystem_insights']['packages_with_high_usage']}")

    print(f"\\n📂 Complete essential data saved in: {output_path}/")
    print(f"🚀 Ready for DepLLM analysis!")

if __name__ == "__main__":
    main()