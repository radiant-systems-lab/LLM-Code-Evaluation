#!/usr/bin/env python3
"""
Dependency Manager with Ollama Integration

This script processes multiple Python scripts by:
1. Detecting libraries (via AST and Ollama LLM) to generate requirements.txt files.
2. Using Ollama to determine how to distribute the scripts across available GPUs.
3. Optionally installing dependencies and executing the scripts.

Usage Examples:
    Generate requirements using Ollama models:
        python ollama_dependency_manager.py script1.py script2.py --model gpt-oss-20b --install --execute
"""

import ast
import re
import subprocess
import sys
import os
import json
import logging
import argparse
import pathlib
import time
import requests
from typing import Set, Dict, List
import torch
import pkg_resources
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

# Built-in modules (to filter out from dependency detection)
STANDARD_LIBRARIES: Set[str] = set(sys.builtin_module_names)

# Ollama API configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def ollama_generate(model: str, prompt: str, max_tokens: int = 100) -> str:
    """
    Generate text using Ollama API
    """
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.7
            }
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama API request failed: {e}")
        return ""
    except Exception as e:
        logger.error(f"Error during Ollama generation: {e}")
        return ""

def check_ollama_model(model_name: str) -> bool:
    """
    Check if model is available in Ollama
    """
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            return model_name in result.stdout
        return False
    except Exception as e:
        logger.error(f"Error checking Ollama models: {e}")
        return False

def extract_imports(file_path: pathlib.Path) -> Set[str]:
    """
    Extract explicitly imported libraries from a Python script.
    """
    try:
        code = file_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return set()

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        logger.error(f"Syntax error in {file_path}: {e}")
        return set()

    imports: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    return imports - STANDARD_LIBRARIES

def infer_missing_libraries(code: str, model_name: str, num_queries: int) -> Set[str]:
    """
    Use Ollama to infer libraries that are used in the code but not explicitly imported.
    """
    if not check_ollama_model(model_name):
        logger.error(f"Model {model_name} not found in Ollama. Please pull it first.")
        return set()
    
    queries = [
        f"Identify external libraries used in the following Python code that are not explicitly imported:\n\n{code}",
        f"List any missing dependencies that should be installed for this Python script:\n\n{code}",
        f"Determine which external libraries (if any) are required for this code but not imported:\n\n{code}",
    ][:num_queries]

    logger.info(f"Using Ollama model '{model_name}' for LLM inference")

    inferred_libraries: Set[str] = set()
    for query in queries:
        try:
            response = ollama_generate(model_name, query, max_tokens=100)
            if not response.strip():
                logger.warning("Ollama returned an empty response.")
                continue
                
            # Try to extract library names from response
            libs = set()
            # Split by common delimiters
            for delimiter in [",", "\n", " "]:
                parts = [part.strip() for part in response.split(delimiter) if part.strip()]
                libs.update(parts)
            
            # Filter tokens that look like valid library names
            parsed_libs = {lib for lib in libs if re.fullmatch(r"[\w\-\_]+", lib)}
            if parsed_libs:
                inferred_libraries.update(parsed_libs)
            else:
                logger.warning("Could not parse any libraries from Ollama response.")
                
        except Exception as e:
            logger.error(f"Error during Ollama inference: {e}")

    return inferred_libraries

def get_installed_package_versions() -> Dict[str, str]:
    """
    Returns a mapping from package name (lowercase) to its 'pip freeze' line.
    """
    package_versions: Dict[str, str] = {}
    try:
        output = subprocess.run(["pip", "freeze"], capture_output=True, text=True, check=True).stdout.splitlines()
        for line in output:
            if "==" in line:
                try:
                    pkg, _ = line.split("==", 1)
                    package_versions[pkg.lower()] = line.strip()
                except ValueError:
                    logger.warning(f"Could not parse package version from line: {line}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running pip freeze: {e}")
    return package_versions

def generate_requirements(file_path: pathlib.Path, output_file: pathlib.Path, model_name: str, num_queries: int) -> None:
    """
    Generates a requirements file for a given Python script using explicit and inferred libraries.
    """
    logger.info(f"Processing {file_path} to generate requirements using Ollama.")
    explicit_imports = extract_imports(file_path)
    try:
        code = file_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return

    inferred_libraries = infer_missing_libraries(code, model_name=model_name, num_queries=num_queries)
    # Check against locally installed packages
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    valid_libraries = {lib for lib in explicit_imports.union(inferred_libraries) if lib.lower() in installed_packages}
    package_versions = get_installed_package_versions()

    try:
        with output_file.open("w", encoding="utf-8") as f:
            for lib in sorted(valid_libraries):
                line = package_versions.get(lib.lower(), lib)
                f.write(line + "\n")
        logger.info(f"Generated requirements file at {output_file}.")
    except Exception as e:
        logger.error(f"Error writing requirements file {output_file}: {e}")

def install_missing_dependencies(requirements_file: pathlib.Path) -> None:
    """
    Installs dependencies from the given requirements file.
    """
    logger.info(f"Installing dependencies from {requirements_file}...")
    try:
        subprocess.run(["pip", "install", "-r", str(requirements_file)], check=True)
        logger.info("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies from {requirements_file}: {e}. Please install manually.")

def determine_gpu_distribution(scripts: List[pathlib.Path], model_name: str, available_devices: List[int]) -> Dict[pathlib.Path, int]:
    """
    Uses Ollama to decide how to distribute the scripts across available GPUs.
    """
    script_info = []
    for script in scripts:
        try:
            code = script.read_text(encoding="utf-8")
            num_lines = len(code.splitlines())
        except Exception:
            num_lines = 0
        script_info.append(f"{script.name}: {num_lines} lines")
    
    # Build available GPU info (ignoring CPU placeholder -1)
    gpu_info = ", ".join(
        f"GPU-{i}: {torch.cuda.get_device_name(i)}" for i in available_devices if i != -1
    ) or "No GPU"
    
    prompt = (
        f"Available GPUs: {gpu_info}\n"
        f"Given the following scripts (with file names and number of lines):\n"
        + "\n".join(script_info) +
        "\n\n"
        "Please provide a JSON mapping of each script file name to a GPU index (0, 1, etc.) "
        "that optimizes parallel execution. Return only a valid JSON object."
    )
    
    logger.info("Deciding GPU distribution for the scripts using Ollama.")
    
    try:
        response = ollama_generate(model_name, prompt, max_tokens=200)
        
        # Try to extract JSON substring from Ollama response
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start != -1 and json_end > 0:
            json_str = response[json_start:json_end]
            mapping = json.loads(json_str)
            result = {}
            for script in scripts:
                gpu_index = mapping.get(script.name)
                if gpu_index is None or gpu_index not in available_devices:
                    gpu_index = available_devices[scripts.index(script) % len(available_devices)]
                result[script] = gpu_index
            logger.info("Ollama GPU distribution decision obtained successfully.")
            return result
        else:
            logger.warning("No JSON found in Ollama response, using round-robin distribution")
            return {script: available_devices[i % len(available_devices)] for i, script in enumerate(scripts)}
    except Exception as e:
        logger.error(f"Error parsing Ollama GPU distribution decision: {e}")
        return {script: available_devices[i % len(available_devices)] for i, script in enumerate(scripts)}

def execute_script(script_path: pathlib.Path, device_id: int) -> None:
    """
    Executes the provided Python script on the assigned GPU (or CPU if device_id is -1).
    """
    logger.info(f"Executing script {script_path} on device {device_id}...")
    start_time = time.perf_counter()
    env = os.environ.copy()
    if device_id != -1:
        env["CUDA_VISIBLE_DEVICES"] = str(device_id)
        logger.info(f"Script {script_path} switched to GPU-{device_id}: {torch.cuda.get_device_name(device_id)}")
    else:
        logger.info(f"Script {script_path} executing on CPU.")
    try:
        subprocess.run([sys.executable, str(script_path)], check=True, env=env)
        elapsed = time.perf_counter() - start_time
        logger.info(f"Script {script_path} executed successfully in {elapsed:.2f} seconds.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing script {script_path}: {e}")

def validate_script_paths(script_paths: List[str]) -> List[pathlib.Path]:
    """
    Validates that the provided paths exist and point to Python (.py) files.
    """
    valid_paths: List[pathlib.Path] = []
    for path_str in script_paths:
        path = pathlib.Path(path_str)
        if not path.exists():
            logger.error(f"Script file {path} does not exist.")
            continue
        if path.suffix.lower() != ".py":
            logger.error(f"File {path} is not a Python (.py) file.")
            continue
        valid_paths.append(path)
    return valid_paths

def main() -> None:
    overall_start = time.perf_counter()
    parser = argparse.ArgumentParser(
        description="Automate dependency management and GPU-distributed execution using Ollama."
    )
    parser.add_argument("scripts", nargs="+", help="Paths to Python script files.")
    parser.add_argument("--model", type=str, default="gpt-oss-20b",
                        help="Ollama model name for inference.")
    parser.add_argument("--num_queries", type=int, default=3,
                        help="Number of Ollama queries per script for dependency detection.")
    parser.add_argument("--install", action="store_true",
                        help="Automatically install dependencies from requirements.")
    parser.add_argument("--execute", action="store_true",
                        help="Execute the scripts after processing.")
    parser.add_argument("--combined", action="store_true",
                        help="Generate a single combined requirements file for all scripts.")
    parser.add_argument("--log_level", type=str, default="INFO",
                        help="Set logging level (DEBUG, INFO, WARNING, ERROR).")
    args = parser.parse_args()

    # Set logging level
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        logger.error(f"Invalid log level: {args.log_level}")
        numeric_level = logging.INFO
    logger.setLevel(numeric_level)

    valid_scripts = validate_script_paths(args.scripts)
    if not valid_scripts:
        logger.error("No valid Python scripts provided. Exiting.")
        return

    # Check if Ollama is running
    try:
        requests.get("http://localhost:11434", timeout=5)
        logger.info("Ollama service is running.")
    except requests.exceptions.RequestException:
        logger.error("Ollama service is not running. Please start it with 'ollama serve'")
        return

    # Determine available devices (GPUs if available; otherwise, use CPU with device_id -1)
    if torch.cuda.is_available():
        num_gpus = torch.cuda.device_count()
        available_devices = list(range(num_gpus))
        logger.info("Detected {} GPU(s): {}".format(
            num_gpus, ", ".join(f"GPU-{i} ({torch.cuda.get_device_name(i)})" for i in available_devices)
        ))
    else:
        available_devices = [-1]
        logger.info("No GPUs available; defaulting to CPU.")

    # Generate requirements files (either combined or per script)
    requirements_files: List[pathlib.Path] = []
    if args.combined:
        combined_requirements = pathlib.Path("combined_requirements.txt")
        all_valid_libs: Set[str] = set()
        for script in valid_scripts:
            explicit_imports = extract_imports(script)
            try:
                code = script.read_text(encoding="utf-8")
            except Exception as e:
                logger.error(f"Error reading {script}: {e}")
                continue
            inferred_libraries = infer_missing_libraries(code, model_name=args.model, num_queries=args.num_queries)
            installed_packages = {pkg.key for pkg in pkg_resources.working_set}
            valid_libraries = {lib for lib in explicit_imports.union(inferred_libraries)
                               if lib.lower() in installed_packages}
            all_valid_libs.update(valid_libraries)
        package_versions = get_installed_package_versions()
        try:
            with combined_requirements.open("w", encoding="utf-8") as f:
                for lib in sorted(all_valid_libs):
                    line = package_versions.get(lib.lower(), lib)
                    f.write(line + "\n")
            logger.info(f"Generated combined requirements file at {combined_requirements}.")
            requirements_files.append(combined_requirements)
        except Exception as e:
            logger.error(f"Error writing combined requirements file: {e}")
    else:
        for script in valid_scripts:
            output_file = script.parent / f"requirements_{script.stem}.txt"
            generate_requirements(script, output_file, model_name=args.model, num_queries=args.num_queries)
            requirements_files.append(output_file)

    if args.install:
        for req_file in requirements_files:
            install_missing_dependencies(req_file)

    # Use Ollama to determine GPU distribution for executing the scripts
    gpu_allocation = determine_gpu_distribution(valid_scripts, model_name=args.model, available_devices=available_devices)

    # Execute scripts
    if args.execute:
        if sys.stdin.isatty() and len(valid_scripts) > 1:
            logger.warning("Interactive input detected. Running scripts sequentially to avoid input conflicts.")
            for script in valid_scripts:
                device_id = gpu_allocation.get(script, available_devices[0])
                execute_script(script, device_id)
        else:
            logger.info("Executing scripts concurrently on assigned GPUs...")
            with ThreadPoolExecutor(max_workers=len(valid_scripts)) as executor:
                future_to_script = {
                    executor.submit(execute_script, script, gpu_allocation.get(script, available_devices[0])): script
                    for script in valid_scripts
                }
                for future in as_completed(future_to_script):
                    script = future_to_script[future]
                    try:
                        future.result()
                    except Exception as exc:
                        logger.error(f"Script {script} generated an exception: {exc}")

    overall_elapsed = time.perf_counter() - overall_start
    logger.info(f"All tasks completed successfully in {overall_elapsed:.2f} seconds!")

if __name__ == "__main__":
    main()