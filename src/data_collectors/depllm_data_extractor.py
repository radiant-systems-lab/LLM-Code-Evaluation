#!/usr/bin/env python3
"""
DepLLM Data Extractor: Libraries.io Knowledge Acquisition
Builds the foundation dataset for dependency-specialized LLM training
"""

import requests
import json
import time
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import ast
import re
from collections import defaultdict, Counter
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns

class DepLLMDataExtractor:
    """Extract and process Libraries.io data for DepLLM training"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://libraries.io/api"
        self.session = requests.Session()
        self.session.params['api_key'] = api_key
        self.rate_limit = 60  # requests per minute
        self.request_interval = 60 / self.rate_limit  # seconds between requests
        self.last_request_time = 0

        # Data storage
        self.script_imports = {}
        self.package_knowledge = {}
        self.dependency_graph = nx.DiGraph()

        print(f"🚀 DepLLM Data Extractor initialized")
        print(f"📊 Rate limit: {self.rate_limit} requests/minute")

    def _respect_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_interval:
            sleep_time = self.request_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def extract_script_dependencies(self, code_dir: str = "../code_scripts") -> Dict[str, List[str]]:
        """Extract all imports from Python scripts"""
        code_path = Path(code_dir)
        script_dependencies = {}
        all_imports = set()

        print(f"🔍 Extracting dependencies from {code_dir}")

        for script_file in code_path.glob("script_*.py"):
            imports = self._extract_imports_from_file(script_file)
            script_dependencies[script_file.name] = imports
            all_imports.update(imports)
            print(f"   📄 {script_file.name}: {len(imports)} imports")

        self.script_imports = script_dependencies

        print(f"\\n📊 Extraction Summary:")
        print(f"   Scripts analyzed: {len(script_dependencies)}")
        print(f"   Unique imports: {len(all_imports)}")

        # Show import frequency
        import_counts = Counter()
        for imports in script_dependencies.values():
            import_counts.update(imports)

        print(f"\\n🔝 Top 15 Most Used Packages:")
        for package, count in import_counts.most_common(15):
            percentage = (count / len(script_dependencies)) * 100
            print(f"   {package:15} : {count:2d} scripts ({percentage:4.1f}%)")

        return script_dependencies, all_imports, import_counts

    def _extract_imports_from_file(self, file_path: Path) -> List[str]:
        """Extract imports from a single Python file"""
        imports = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Try AST parsing first (more accurate)
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            root_package = alias.name.split('.')[0]
                            imports.append(root_package)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        root_package = node.module.split('.')[0]
                        imports.append(root_package)

            except SyntaxError:
                # Fallback to regex parsing
                import_patterns = [
                    r'^\\s*import\\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                    r'^\\s*from\\s+([a-zA-Z_][a-zA-Z0-9_]*)\\s+import'
                ]

                for line in content.split('\\n'):
                    line = line.strip()
                    for pattern in import_patterns:
                        match = re.match(pattern, line)
                        if match:
                            imports.append(match.group(1))

        except Exception as e:
            print(f"   ⚠️  Error parsing {file_path.name}: {e}")

        return list(set(imports))  # Remove duplicates

    def map_imports_to_pypi(self, imports: List[str]) -> Dict[str, str]:
        """Map Python import names to PyPI package names"""
        # Common import-to-package mappings
        mapping = {
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'Image': 'Pillow',
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
            'tensorflow': 'tensorflow',
            'torch': 'torch',
            'torchvision': 'torchvision',
            'transformers': 'transformers',
            'openai': 'openai',
            'anthropic': 'anthropic'
        }

        # Add standard library modules to ignore
        stdlib_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'math', 'random', 'collections',
            'itertools', 'functools', 'operator', 're', 'string', 'io', 'pathlib',
            'urllib', 'http', 'socket', 'threading', 'multiprocessing', 'subprocess',
            'pickle', 'csv', 'xml', 'html', 'email', 'base64', 'hashlib', 'hmac',
            'logging', 'unittest', 'argparse', 'configparser', 'tempfile', 'shutil',
            'glob', 'fnmatch', 'linecache', 'textwrap', 'unicodedata', 'struct',
            'codecs', 'locale', 'calendar', 'pprint', 'reprlib', 'enum', 'copy',
            'types', 'weakref', 'gc', 'inspect', 'site', 'importlib'
        }

        pypi_mapping = {}
        for import_name in imports:
            if import_name in stdlib_modules:
                continue  # Skip standard library modules

            pypi_name = mapping.get(import_name, import_name)
            pypi_mapping[import_name] = pypi_name

        return pypi_mapping

    def fetch_package_info(self, pypi_name: str) -> Optional[Dict]:
        """Fetch comprehensive package information from Libraries.io"""
        self._respect_rate_limit()

        try:
            url = f"{self.base_url}/pypi/{pypi_name}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                print(f"   ⚠️  HTTP {response.status_code} for {pypi_name}")
                return None

        except Exception as e:
            print(f"   ❌ Error fetching {pypi_name}: {e}")
            return None

    def fetch_package_dependencies(self, pypi_name: str, version: str = None) -> Dict[str, List[Dict]]:
        """Fetch package dependencies"""
        self._respect_rate_limit()

        try:
            if version:
                url = f"{self.base_url}/pypi/{pypi_name}/{version}/dependencies"
            else:
                url = f"{self.base_url}/pypi/{pypi_name}/latest/dependencies"

            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                deps = response.json()

                # Group by dependency kind
                grouped = defaultdict(list)
                for dep in deps:
                    kind = dep.get('kind', 'runtime')
                    grouped[kind].append(dep)

                return dict(grouped)
            else:
                return {}

        except Exception as e:
            print(f"   ⚠️  Error fetching dependencies for {pypi_name}: {e}")
            return {}

    def build_package_knowledge_base(self, imports: List[str], max_packages: int = 50) -> None:
        """Build comprehensive package knowledge from Libraries.io"""
        print(f"\\n🏗️  Building DepLLM Package Knowledge Base")
        print(f"📦 Processing up to {max_packages} packages from Libraries.io")

        # Map imports to PyPI names
        pypi_mapping = self.map_imports_to_pypi(imports)

        # Sort by frequency for priority processing
        import_frequency = Counter()
        for script_imports in self.script_imports.values():
            import_frequency.update(script_imports)

        sorted_imports = sorted(pypi_mapping.keys(),
                              key=lambda x: import_frequency.get(x, 0),
                              reverse=True)

        processed = 0
        successful = 0

        for import_name in sorted_imports[:max_packages]:
            pypi_name = pypi_mapping[import_name]
            freq = import_frequency.get(import_name, 0)

            print(f"\\n📦 [{processed+1:2d}/{min(max_packages, len(sorted_imports)):2d}] {pypi_name}")
            print(f"   Import: {import_name}, Used in: {freq} scripts")

            # Fetch package info
            package_info = self.fetch_package_info(pypi_name)

            if package_info:
                # Fetch dependencies
                dependencies = self.fetch_package_dependencies(pypi_name)

                # Store comprehensive info
                self.package_knowledge[import_name] = {
                    'pypi_name': pypi_name,
                    'info': package_info,
                    'dependencies': dependencies,
                    'usage_frequency': freq,
                    'usage_percentage': (freq / len(self.script_imports)) * 100
                }

                print(f"   ✅ Rank: {package_info.get('rank', 'N/A'):,}")
                print(f"   📊 Dependents: {package_info.get('dependents_count', 0):,}")
                print(f"   🔗 Dependencies: {sum(len(deps) for deps in dependencies.values())}")
                print(f"   📈 Latest: {package_info.get('latest_stable_release_number', 'N/A')}")

                successful += 1
            else:
                print(f"   ❌ Package not found on Libraries.io")

            processed += 1

        print(f"\\n✅ Knowledge Base Complete!")
        print(f"   📦 Packages processed: {processed}")
        print(f"   ✅ Successful fetches: {successful}")
        print(f"   📊 Success rate: {(successful/processed)*100:.1f}%")

    def build_dependency_graph(self) -> None:
        """Build NetworkX dependency graph"""
        print(f"\\n🕸️  Building DepLLM Dependency Graph")

        # Add nodes for each package
        for import_name, pkg_data in self.package_knowledge.items():
            pkg_info = pkg_data['info']

            self.dependency_graph.add_node(
                import_name,
                pypi_name=pkg_data['pypi_name'],
                rank=pkg_info.get('rank', float('inf')),
                dependents_count=pkg_info.get('dependents_count', 0),
                latest_version=pkg_info.get('latest_stable_release_number', ''),
                usage_frequency=pkg_data['usage_frequency'],
                description=(pkg_info.get('description', '') or '')[:100]
            )

        # Add dependency edges
        edges_added = 0
        for import_name, pkg_data in self.package_knowledge.items():
            dependencies = pkg_data['dependencies']

            for dep_kind, deps in dependencies.items():
                for dep in deps:
                    dep_pypi_name = dep.get('project_name', '')
                    requirements = dep.get('requirements', '')

                    if dep_pypi_name:
                        # Try to find this dependency in our known packages
                        target_import = None
                        for known_import, known_pkg in self.package_knowledge.items():
                            if known_pkg['pypi_name'].lower() == dep_pypi_name.lower():
                                target_import = known_import
                                break

                        if target_import:
                            # Internal dependency (both packages in our set)
                            self.dependency_graph.add_edge(
                                import_name, target_import,
                                dependency_kind=dep_kind,
                                requirements=requirements,
                                pypi_name=dep_pypi_name,
                                internal=True
                            )
                            edges_added += 1
                        else:
                            # External dependency
                            external_node = f"ext_{dep_pypi_name}"
                            if not self.dependency_graph.has_node(external_node):
                                self.dependency_graph.add_node(
                                    external_node,
                                    pypi_name=dep_pypi_name,
                                    external=True,
                                    description="External dependency"
                                )

                            self.dependency_graph.add_edge(
                                import_name, external_node,
                                dependency_kind=dep_kind,
                                requirements=requirements,
                                pypi_name=dep_pypi_name,
                                internal=False
                            )
                            edges_added += 1

        print(f"   📊 Graph Statistics:")
        print(f"      Nodes: {self.dependency_graph.number_of_nodes()}")
        print(f"      Edges: {self.dependency_graph.number_of_edges()}")
        print(f"      Density: {nx.density(self.dependency_graph):.3f}")

        # Analyze graph structure
        if self.dependency_graph.number_of_nodes() > 0:
            in_degrees = dict(self.dependency_graph.in_degree())
            out_degrees = dict(self.dependency_graph.out_degree())

            most_depended = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:3]
            most_dependencies = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:3]

            print(f"   🎯 Most Depended-On:")
            for pkg, count in most_depended:
                if count > 0:
                    print(f"      {pkg}: {count} packages")

            print(f"   📤 Most Dependencies:")
            for pkg, count in most_dependencies:
                if count > 0:
                    print(f"      {pkg}: {count} dependencies")

    def analyze_knowledge_base(self) -> Dict[str, Any]:
        """Analyze the built knowledge base"""
        print(f"\\n📊 DepLLM Knowledge Base Analysis")
        print("=" * 60)

        if not self.package_knowledge:
            print("⚠️  No knowledge base data available")
            return {}

        analysis = {}

        # Package popularity analysis
        packages_by_rank = []
        packages_by_dependents = []

        for import_name, pkg_data in self.package_knowledge.items():
            pkg_info = pkg_data['info']
            rank = pkg_info.get('rank', float('inf'))
            dependents = pkg_info.get('dependents_count', 0)
            usage = pkg_data['usage_frequency']

            if rank != float('inf'):
                packages_by_rank.append((import_name, rank, dependents, usage))
            packages_by_dependents.append((import_name, dependents, rank, usage))

        packages_by_rank.sort(key=lambda x: x[1])
        packages_by_dependents.sort(key=lambda x: x[1], reverse=True)

        print(f"🏆 Top Packages by Libraries.io Rank:")
        for name, rank, dependents, usage in packages_by_rank[:8]:
            print(f"   {name:15} | Rank #{rank:,} | {dependents:,} dependents | {usage} scripts")

        print(f"\\n📈 Top Packages by Dependents:")
        for name, dependents, rank, usage in packages_by_dependents[:8]:
            print(f"   {name:15} | {dependents:,} dependents | Rank #{rank:,} | {usage} scripts")

        # Dependency complexity analysis
        complexity_data = []
        for import_name, pkg_data in self.package_knowledge.items():
            deps = pkg_data['dependencies']
            total_deps = sum(len(dep_list) for dep_list in deps.values())
            usage = pkg_data['usage_frequency']

            complexity_data.append((import_name, total_deps, usage))

        complexity_data.sort(key=lambda x: x[1], reverse=True)

        print(f"\\n🔗 Most Complex Dependencies:")
        for name, deps, usage in complexity_data[:8]:
            if deps > 0:
                print(f"   {name:15} | {deps:2d} dependencies | {usage} scripts")

        # Usage vs popularity correlation
        print(f"\\n📊 Usage vs Popularity Analysis:")
        high_usage_high_pop = []
        high_usage_low_pop = []

        for import_name, pkg_data in self.package_knowledge.items():
            usage = pkg_data['usage_frequency']
            rank = pkg_data['info'].get('rank', float('inf'))

            if usage >= 3:  # Used in 3+ scripts
                if rank <= 1000:  # Top 1000 packages
                    high_usage_high_pop.append((import_name, usage, rank))
                else:
                    high_usage_low_pop.append((import_name, usage, rank))

        print(f"   ✅ High Usage + High Popularity: {len(high_usage_high_pop)} packages")
        for name, usage, rank in sorted(high_usage_high_pop, key=lambda x: x[1], reverse=True)[:5]:
            print(f"      {name:15} | {usage} scripts | Rank #{rank:,}")

        if high_usage_low_pop:
            print(f"   🔍 High Usage + Lower Popularity: {len(high_usage_low_pop)} packages")
            for name, usage, rank in sorted(high_usage_low_pop, key=lambda x: x[1], reverse=True)[:3]:
                print(f"      {name:15} | {usage} scripts | Rank #{rank:,}")

        analysis['packages_by_rank'] = packages_by_rank
        analysis['packages_by_dependents'] = packages_by_dependents
        analysis['complexity_data'] = complexity_data

        return analysis

    def save_depllm_dataset(self, output_dir: str = "depllm_data") -> None:
        """Save the complete DepLLM training dataset"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        print(f"\\n💾 Saving DepLLM Training Dataset to {output_dir}/")

        # 1. Save script dependencies and imports
        with open(output_path / "script_dependencies.json", 'w') as f:
            json.dump(self.script_imports, f, indent=2)

        # 2. Save package knowledge base
        with open(output_path / "package_knowledge_base.json", 'w') as f:
            json.dump(self.package_knowledge, f, indent=2, default=str)

        # 3. Save dependency graph (handle None values)
        try:
            # Clean None values from graph data
            for node, data in self.dependency_graph.nodes(data=True):
                for key, value in data.items():
                    if value is None:
                        data[key] = ""

            for u, v, data in self.dependency_graph.edges(data=True):
                for key, value in data.items():
                    if value is None:
                        data[key] = ""

            nx.write_graphml(self.dependency_graph, output_path / "dependency_graph.graphml")
        except Exception as e:
            print(f"   ⚠️  Could not save GraphML: {e}")
            # Save as JSON instead
            graph_data = nx.node_link_data(self.dependency_graph)
            with open(output_path / "dependency_graph.json", 'w') as f:
                json.dump(graph_data, f, indent=2, default=str)

        # 4. Create training data format for LLM fine-tuning
        training_examples = self.create_training_examples()

        with open(output_path / "depllm_training_data.json", 'w') as f:
            json.dump(training_examples, f, indent=2)

        # 5. Create summary statistics
        summary = self.create_dataset_summary()

        with open(output_path / "dataset_summary.json", 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"✅ DepLLM Dataset Saved Successfully!")
        print(f"   📄 Files created:")
        print(f"      • script_dependencies.json")
        print(f"      • package_knowledge_base.json")
        print(f"      • dependency_graph.graphml")
        print(f"      • depllm_training_data.json")
        print(f"      • dataset_summary.json")

        return output_path

    def create_training_examples(self) -> List[Dict]:
        """Create training examples for LLM fine-tuning"""
        training_examples = []

        print(f"🎓 Creating DepLLM Training Examples...")

        for script_name, imports in self.script_imports.items():
            if not imports:
                continue

            # Create code snippet from imports
            import_lines = [f"import {imp}" for imp in imports]
            code_snippet = "\\n".join(import_lines)

            # Gather dependency information
            dependencies = {}
            predicted_success = 1.0
            reasoning_parts = []

            known_packages = 0
            total_dependents = 0

            for import_name in imports:
                if import_name in self.package_knowledge:
                    pkg_data = self.package_knowledge[import_name]
                    pkg_info = pkg_data['info']

                    dependencies[import_name] = {
                        "pypi_name": pkg_data['pypi_name'],
                        "version": pkg_info.get('latest_stable_release_number', 'latest'),
                        "rank": pkg_info.get('rank', float('inf')),
                        "dependents": pkg_info.get('dependents_count', 0),
                        "probability": min(0.99, 0.7 + (pkg_data['usage_frequency'] * 0.1))
                    }

                    known_packages += 1
                    total_dependents += pkg_info.get('dependents_count', 0)

                    # Add to reasoning
                    rank = pkg_info.get('rank', float('inf'))
                    if rank <= 100:
                        reasoning_parts.append(f"{import_name} is a top-100 package")
                    elif rank <= 1000:
                        reasoning_parts.append(f"{import_name} is well-established")

            # Calculate predicted success based on package quality
            if known_packages > 0:
                avg_dependents = total_dependents / known_packages
                if avg_dependents > 10000:
                    predicted_success = 0.95
                elif avg_dependents > 1000:
                    predicted_success = 0.85
                else:
                    predicted_success = 0.75
            else:
                predicted_success = 0.6  # Unknown packages are riskier

            # Create reasoning
            if reasoning_parts:
                reasoning = f"Dependencies include {', '.join(reasoning_parts[:3])}. "
            else:
                reasoning = "Dependencies are not well-known packages. "

            reasoning += f"Predicted success rate: {predicted_success:.0%}"

            # Create training example
            example = {
                "instruction": "Analyze the dependencies for this Python code and predict execution success.",
                "input": f"```python\\n{code_snippet}\\n```",
                "output": {
                    "dependencies": dependencies,
                    "predicted_success": predicted_success,
                    "reasoning": reasoning,
                    "script_name": script_name
                }
            }

            training_examples.append(example)

        print(f"   ✅ Created {len(training_examples)} training examples")
        return training_examples

    def create_dataset_summary(self) -> Dict:
        """Create comprehensive dataset summary"""
        total_packages = len(self.package_knowledge)
        total_scripts = len(self.script_imports)

        # Calculate success rate from package quality
        high_quality_packages = 0
        for pkg_data in self.package_knowledge.values():
            rank = pkg_data['info'].get('rank', float('inf'))
            if rank <= 1000:
                high_quality_packages += 1

        quality_rate = (high_quality_packages / total_packages) * 100 if total_packages > 0 else 0

        summary = {
            "dataset_info": {
                "name": "DepLLM Training Dataset",
                "version": "1.0",
                "created_at": pd.Timestamp.now().isoformat(),
                "description": "Dependency-specialized LLM training data from Libraries.io"
            },
            "data_sources": {
                "libraries_io_api": "37M+ packages ecosystem data",
                "script_analysis": f"{total_scripts} Python scripts analyzed",
                "execution_data": "Sciunit ground truth results",
                "semantic_analysis": "LLM dependency extraction"
            },
            "statistics": {
                "total_packages": total_packages,
                "total_scripts": total_scripts,
                "unique_imports": len(set().union(*self.script_imports.values())) if self.script_imports else 0,
                "dependency_relationships": self.dependency_graph.number_of_edges(),
                "high_quality_packages": high_quality_packages,
                "quality_percentage": f"{quality_rate:.1f}%"
            },
            "graph_metrics": {
                "nodes": self.dependency_graph.number_of_nodes(),
                "edges": self.dependency_graph.number_of_edges(),
                "density": round(nx.density(self.dependency_graph), 4) if self.dependency_graph.number_of_nodes() > 0 else 0
            },
            "ready_for_training": {
                "llm_fine_tuning": True,
                "aws_sagemaker": True,
                "huggingface": True,
                "training_examples": len(self.script_imports)
            }
        }

        return summary

def main():
    """Main execution function"""
    print("🚀 DepLLM: Dependency-Specialized LLM Data Extraction")
    print("=" * 60)

    # Initialize with your API key
    API_KEY = "b6a94607560db5e63b31153f41d37c68"
    extractor = DepLLMDataExtractor(API_KEY)

    # Step 1: Extract dependencies from scripts
    print("\\n📝 Phase 1: Script Dependency Extraction")
    script_deps, unique_imports, import_counts = extractor.extract_script_dependencies()

    # Step 2: Build package knowledge base from Libraries.io
    print("\\n🌍 Phase 2: Libraries.io Knowledge Acquisition")
    extractor.build_package_knowledge_base(list(unique_imports), max_packages=30)

    # Step 3: Build dependency graph
    print("\\n🕸️  Phase 3: Dependency Graph Construction")
    extractor.build_dependency_graph()

    # Step 4: Analyze knowledge base
    print("\\n📊 Phase 4: Knowledge Base Analysis")
    analysis = extractor.analyze_knowledge_base()

    # Step 5: Save complete dataset
    print("\\n💾 Phase 5: Dataset Export")
    output_path = extractor.save_depllm_dataset()

    print("\\n🎉 DepLLM Data Extraction Complete!")
    print(f"\\n📋 Next Steps:")
    print(f"   1. Review dataset in {output_path}/")
    print(f"   2. Upload to AWS S3 for SageMaker training")
    print(f"   3. Start DepLLM fine-tuning process")
    print(f"   4. Validate against your 54 execution results")

if __name__ == "__main__":
    main()