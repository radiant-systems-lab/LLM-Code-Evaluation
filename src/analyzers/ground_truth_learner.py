#!/usr/bin/env python3
"""
Ground Truth Dependency Learner

Extracts transitive dependency mappings from sciunit runtime execution data.
This enables AI-powered dependency prediction informed by actual runtime behavior.

For reproducibility research - bridges the gap between static analysis and runtime reality.
"""

import re
import json
import subprocess
from pathlib import Path
from typing import Dict, Set, List, Tuple
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroundTruthLearner:
    """
    Learns transitive dependency patterns from sciunit ground truth data.

    Approach:
    1. Extract pip freeze data from all completed sciunit runs
    2. Analyze which packages always appear together
    3. Build transitive dependency mapping
    4. Generate realistic few-shot examples for LLM prompting
    """

    def __init__(self, namespace="gp-engine-mizzou-radiant"):
        self.namespace = namespace
        self.transitive_map = defaultdict(set)
        self.package_frequencies = defaultdict(int)
        self.script_dependencies = {}  # script_name -> set of packages

    def fetch_ground_truth_from_k8s(self) -> Dict[str, Set[str]]:
        """Fetch all .requirements.txt files from Kubernetes PVC"""
        logger.info("Fetching ground truth data from Kubernetes PVC...")

        # Get list of completed scripts
        result = subprocess.run(
            f'kubectl exec results-collector -n {self.namespace} -- sh -c "cd /results && ls *.requirements.txt 2>/dev/null"',
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logger.error(f"Failed to list files: {result.stderr}")
            return {}

        req_files = result.stdout.strip().split('\n')
        logger.info(f"Found {len(req_files)} requirement files")

        # Fetch each file
        ground_truth = {}
        for req_file in req_files:
            if not req_file:
                continue

            script_name = req_file.replace('.requirements.txt', '')

            # Get requirements.txt content
            result = subprocess.run(
                f'kubectl exec results-collector -n {self.namespace} -- cat /results/{req_file}',
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                packages = self._parse_requirements(result.stdout)
                ground_truth[script_name] = packages
                logger.info(f"  {script_name}: {len(packages)} packages")

        return ground_truth

    def _parse_requirements(self, req_content: str) -> Set[str]:
        """Parse pip freeze output into package names"""
        packages = set()
        for line in req_content.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Extract package name (before == or other version specifier)
            match = re.match(r'^([a-zA-Z0-9][a-zA-Z0-9._-]*)', line)
            if match:
                pkg_name = match.group(1).lower()
                # Normalize package names
                pkg_name = pkg_name.replace('_', '-')
                packages.add(pkg_name)

        return packages

    def analyze_script_imports(self, script_path: str) -> Set[str]:
        """Get direct imports from a script using AST"""
        import ast

        try:
            with open(script_path, 'r') as f:
                tree = ast.parse(f.read())

            direct_imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        direct_imports.add(alias.name.split('.')[0].lower())
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        direct_imports.add(node.module.split('.')[0].lower())

            return direct_imports
        except Exception as e:
            logger.warning(f"Failed to parse {script_path}: {e}")
            return set()

    def build_transitive_mapping(self, ground_truth: Dict[str, Set[str]],
                                 scripts_dir: Path) -> Dict[str, Set[str]]:
        """
        Build transitive dependency mapping by comparing direct imports to runtime packages.

        For each script:
        1. Get direct imports from AST
        2. Get runtime packages from pip freeze
        3. The difference = transitive dependencies
        """
        logger.info("\nBuilding transitive dependency mapping...")

        transitive_deps = defaultdict(set)
        stdlib = self._get_stdlib_modules()

        for script_name, runtime_packages in ground_truth.items():
            script_path = scripts_dir / f"{script_name}.py"
            if not script_path.exists():
                script_path = scripts_dir / f"{script_name}"

            if not script_path.exists():
                continue

            # Get direct imports
            direct_imports = self.analyze_script_imports(script_path)

            # Normalize import names to package names
            import_to_package = {
                'cv2': 'opencv-python',
                'sklearn': 'scikit-learn',
                'pil': 'pillow',
                'yaml': 'pyyaml',
                # Add more as discovered
            }

            direct_packages = set()
            for imp in direct_imports:
                if imp in stdlib:
                    continue
                pkg = import_to_package.get(imp, imp)
                direct_packages.add(pkg.lower())

            # Transitive = runtime - direct
            for direct_pkg in direct_packages:
                transitive = runtime_packages - direct_packages - stdlib
                if transitive:
                    transitive_deps[direct_pkg].update(transitive)

            # Track frequency
            for pkg in runtime_packages:
                self.package_frequencies[pkg] += 1

        # Filter to keep only frequently occurring transitive deps (appear in 10%+ of scripts)
        min_frequency = max(2, len(ground_truth) * 0.1)
        filtered_deps = {}

        for pkg, deps in transitive_deps.items():
            frequent_deps = {d for d in deps if self.package_frequencies[d] >= min_frequency}
            if frequent_deps:
                filtered_deps[pkg] = frequent_deps

        logger.info(f"Found transitive mappings for {len(filtered_deps)} packages")

        return filtered_deps

    def _get_stdlib_modules(self) -> Set[str]:
        """Get Python standard library module names"""
        return {
            'os', 'sys', 'json', 'time', 'datetime', 'random', 'math', 're',
            'collections', 'itertools', 'functools', 'pathlib', 'typing',
            'asyncio', 'concurrent', 'unittest', 'logging', 'argparse',
            'subprocess', 'threading', 'multiprocessing', 'socket', 'http',
            'urllib', 'email', 'xml', 'html', 'csv', 'io', 'tempfile',
            'shutil', 'glob', 'pickle', 'copy', 'pprint', 'traceback',
            'warnings', 'contextlib', 'abc', 'enum', 'dataclasses'
        }

    def generate_few_shot_examples(self, ground_truth: Dict[str, Set[str]],
                                   num_examples: int = 3) -> List[Tuple[str, Set[str]]]:
        """
        Generate realistic few-shot examples for LLM prompting.

        Select diverse scripts with varying dependency counts.
        """
        # Sort by number of dependencies
        sorted_scripts = sorted(ground_truth.items(), key=lambda x: len(x[1]))

        # Pick small, medium, large examples
        examples = []
        if len(sorted_scripts) >= 3:
            indices = [
                len(sorted_scripts) // 4,      # Small
                len(sorted_scripts) // 2,      # Medium
                3 * len(sorted_scripts) // 4   # Large
            ]
            examples = [sorted_scripts[i] for i in indices[:num_examples]]
        else:
            examples = sorted_scripts[:num_examples]

        logger.info(f"\nSelected {len(examples)} few-shot examples:")
        for script_name, deps in examples:
            logger.info(f"  {script_name}: {len(deps)} dependencies")

        return examples

    def export_learned_mappings(self, output_path: Path):
        """Export learned transitive dependencies as JSON"""
        data = {
            'transitive_dependencies': {k: list(v) for k, v in self.transitive_map.items()},
            'package_frequencies': dict(self.package_frequencies),
            'total_scripts_analyzed': len(self.script_dependencies)
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"\nExported learned mappings to {output_path}")

    def run_learning_pipeline(self, scripts_dir: Path, output_path: Path):
        """Complete learning pipeline"""
        logger.info("=" * 60)
        logger.info("GROUND TRUTH LEARNING PIPELINE")
        logger.info("=" * 60)

        # Step 1: Fetch from Kubernetes
        ground_truth = self.fetch_ground_truth_from_k8s()
        if not ground_truth:
            logger.error("No ground truth data found!")
            return

        self.script_dependencies = ground_truth

        # Step 2: Build transitive mapping
        self.transitive_map = self.build_transitive_mapping(ground_truth, scripts_dir)

        # Step 3: Generate few-shot examples
        few_shot = self.generate_few_shot_examples(ground_truth)

        # Step 4: Export results
        self.export_learned_mappings(output_path)

        # Step 5: Print summary
        logger.info("\n" + "=" * 60)
        logger.info("LEARNING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Scripts analyzed: {len(ground_truth)}")
        logger.info(f"Total unique packages: {len(self.package_frequencies)}")
        logger.info(f"Transitive mappings: {len(self.transitive_map)}")
        logger.info(f"\nTop 10 most common packages:")
        top_packages = sorted(self.package_frequencies.items(),
                            key=lambda x: x[1], reverse=True)[:10]
        for pkg, freq in top_packages:
            logger.info(f"  {pkg}: {freq} scripts ({100*freq/len(ground_truth):.1f}%)")

        return {
            'ground_truth': ground_truth,
            'transitive_map': self.transitive_map,
            'few_shot_examples': few_shot
        }


def main():
    """Run the ground truth learning pipeline"""
    learner = GroundTruthLearner()

    scripts_dir = Path(r"D:\LLM Dependency Manager\LLM-Dependency-Manager\LLM_Dependency_Manager\tests\scripts")
    output_path = Path(r"D:\LLM Dependency Manager\LLM-Dependency-Manager\LLM_Dependency_Manager\src\analyzers\learned_dependencies.json")

    results = learner.run_learning_pipeline(scripts_dir, output_path)

    if results:
        logger.info("\n✅ Ground truth learning complete!")
        logger.info(f"Results saved to: {output_path}")


if __name__ == '__main__':
    main()
