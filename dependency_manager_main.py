#!/usr/bin/env python3
"""
Dependency Manager & GPU Distributor

This script processes multiple Python scripts by:
1. Detecting libraries (via AST and LLM) to generate requirements.txt files.
2. Using an LLM to determine how to distribute the scripts across available GPUs automatically.
3. Optionally installing dependencies and executing the scripts.
   If interactive input is detected, scripts are run sequentially to avoid input conflicts.

Usage Examples:
  Generate requirements and execute scripts concurrently (if non-interactive):
      python dependency_manager.py script1.py script2.py --install --execute
  Generate a combined requirements file for all scripts:
      python dependency_manager.py script1.py script2.py --combined
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
from typing import Set, Dict, List
import torch
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download
import pkg_resources
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

# Built-in modules (to filter out from dependency detection)
STANDARD_LIBRARIES: Set[str] = set(sys.builtin_module_names)

# Global variable to store the loaded pipeline
CACHED_LLM_PIPELINE = None

def get_or_load_model(model_name: str, device_id: int):
    """
    Load the model from local storage if available, otherwise download and save it.
    Returns a pipeline object for text generation.
    """
    global CACHED_LLM_PIPELINE
    
    # If pipeline is already loaded, return it
    if CACHED_LLM_PIPELINE is not None:
        return CACHED_LLM_PIPELINE
    
    # Define local model directory
    model_dir = pathlib.Path("models") / model_name.replace("/", "_")
    
    try:
        # Check if model files exist locally
        if model_dir.exists() and any(model_dir.glob("*.bin")) or any(model_dir.glob("*.safetensors")):
            # Load from local directory
            logger.info(f"Found cached model in: {model_dir}")
            logger.info(f"Loading model from local cache...")
            
            # For GPT-OSS models, we need special handling
            if "gpt-oss" in model_name.lower():
                logger.warning(f"GPT-OSS models require custom architecture support. Using fallback.")
                # Return a dummy pipeline or None for GPT-OSS models
                return None
            
            CACHED_LLM_PIPELINE = pipeline(
                "text-generation",
                model=str(model_dir),
                device=device_id if device_id != -1 else -1,
                torch_dtype="auto",
            )
        else:
            # Download model files first
            logger.info(f"Model not found locally. Downloading {model_name} to {model_dir}...")
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Use huggingface_hub to download all files
            try:
                snapshot_download(
                    repo_id=model_name,
                    local_dir=str(model_dir),
                    local_dir_use_symlinks=False,
                    resume_download=True
                )
                logger.info(f"Model files downloaded to {model_dir}")
                
                # Try to load the model
                if "gpt-oss" in model_name.lower():
                    logger.warning(f"GPT-OSS models require custom architecture support. Files downloaded but cannot load.")
                    return None
                
                CACHED_LLM_PIPELINE = pipeline(
                    "text-generation",
                    model=str(model_dir),
                    device=device_id if device_id != -1 else -1,
                    torch_dtype="auto",
                )
            except Exception as download_error:
                logger.error(f"Failed to download model: {download_error}")
                return None
                
    except torch.cuda.OutOfMemoryError:
        logger.error("CUDA out of memory during LLM loading. Switching to CPU.")
        if model_dir.exists():
            CACHED_LLM_PIPELINE = pipeline("text-generation", model=str(model_dir), device=-1)
        else:
            CACHED_LLM_PIPELINE = pipeline("text-generation", model=model_name, device=-1)
    except Exception as e:
        logger.error(f"Error loading model {model_name}: {e}")
        return None
    
    return CACHED_LLM_PIPELINE


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


def infer_missing_libraries(code: str, model_name: str, num_queries: int, device_id: int) -> Set[str]:
    """
    Use an LLM to infer libraries that are used in the code but not explicitly imported.
    """
    queries = [
        f"Identify external libraries used in the following Python code that are not explicitly imported:\n\n{code}",
        f"List any missing dependencies that should be installed for this Python script:\n\n{code}",
        f"Determine which external libraries (if any) are required for this code but not imported:\n\n{code}",
    ][:num_queries]

    # Log which device is used for LLM inference
    if device_id != -1:
        logger.info(f"LLM inference using '{model_name}' on GPU-{device_id}: {torch.cuda.get_device_name(device_id)}")
    else:
        logger.info(f"LLM inference using '{model_name}' on CPU.")

    # Use the cached model loading function
    llm = get_or_load_model(model_name, device_id)
    if llm is None:
        return set()

    inferred_libraries: Set[str] = set()
    try:
        responses = llm(queries, max_new_tokens=100)
        # Process each response and try to extract library names
        for resp in responses:
            # Handle both dict and list response formats
            if isinstance(resp, dict):
                generated_text = resp.get("generated_text", "")
            elif isinstance(resp, list) and len(resp) > 0:
                generated_text = resp[0].get("generated_text", "") if isinstance(resp[0], dict) else ""
            else:
                generated_text = str(resp)
            
            if not generated_text.strip():
                logger.warning("LLM returned an empty response.")
                continue
            libs = set()
            # Try splitting by common delimiters
            for delimiter in [",", "\n", " "]:
                parts = [part.strip() for part in generated_text.split(delimiter) if part.strip()]
                libs.update(parts)
            # Filter tokens that look like valid library names
            parsed_libs = {lib for lib in libs if re.fullmatch(r"[\w\-\_]+", lib)}
            if not parsed_libs:
                logger.warning("Could not parse any libraries from LLM response.")
            inferred_libraries.update(parsed_libs)
    except Exception as e:
        logger.error(f"Error during LLM inference: {e}")

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


def generate_requirements(file_path: pathlib.Path, output_file: pathlib.Path, model_name: str, num_queries: int, device_id: int) -> None:
    """
    Generates a requirements file for a given Python script using explicit and inferred libraries.
    """
    logger.info(f"Processing {file_path} on device {device_id} to generate requirements.")
    explicit_imports = extract_imports(file_path)
    try:
        code = file_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return

    inferred_libraries = infer_missing_libraries(code, model_name=model_name, num_queries=num_queries, device_id=device_id)
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


def determine_gpu_distribution(scripts: List[pathlib.Path], model_name: str, available_devices: List[int], llm_device: int) -> Dict[pathlib.Path, int]:
    """
    Uses an LLM to decide how to distribute the scripts across available GPUs.
    
    The LLM is provided with a summary of each script (name and number of lines)
    along with available GPU details. It is expected to return a JSON mapping of script names
    to GPU indices. If parsing fails, fall back to round-robin assignment.
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
    
    logger.info("Deciding GPU distribution for the scripts using LLM.")
    # Use the cached model loading function
    llm = get_or_load_model(model_name, llm_device)
    if llm is None:
        logger.error(f"Failed to load model for GPU distribution decision")
        return {script: available_devices[i % len(available_devices)] for i, script in enumerate(scripts)}
    
    try:
        response = llm(prompt, max_new_tokens=200)
        # Handle different response formats
        if isinstance(response, list) and len(response) > 0:
            text = response[0].get("generated_text", "") if isinstance(response[0], dict) else str(response[0])
        elif isinstance(response, dict):
            text = response.get("generated_text", "")
        else:
            text = str(response)
        
        # Try to extract JSON substring from LLM response
        json_start = text.find("{")
        json_end = text.rfind("}") + 1
        if json_start != -1 and json_end > 0:
            json_str = text[json_start:json_end]
            mapping = json.loads(json_str)
            result = {}
            for script in scripts:
                gpu_index = mapping.get(script.name)
                if gpu_index is None or gpu_index not in available_devices:
                    gpu_index = available_devices[scripts.index(script) % len(available_devices)]
                result[script] = gpu_index
            logger.info("LLM GPU distribution decision obtained successfully.")
            return result
        else:
            logger.warning("No JSON found in LLM response, using round-robin distribution")
            return {script: available_devices[i % len(available_devices)] for i, script in enumerate(scripts)}
    except Exception as e:
        logger.error(f"Error parsing LLM GPU distribution decision: {e}")
        return {script: available_devices[i % len(available_devices)] for i, script in enumerate(scripts)}


def execute_script(script_path: pathlib.Path, device_id: int) -> None:
    """
    Executes the provided Python script on the assigned GPU (or CPU if device_id is -1).
    Sets CUDA_VISIBLE_DEVICES to ensure the script runs on the correct GPU and logs execution time.
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
        description="Automate dependency management and GPU-distributed execution for Python scripts."
    )
    parser.add_argument("scripts", nargs="+", help="Paths to Python script files.")
    parser.add_argument("--model", type=str, default="openai/gpt-oss-20b",
                        help="LLM model name for inference.")
    parser.add_argument("--num_queries", type=int, default=3,
                        help="Number of LLM queries per script for dependency detection.")
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
        for idx, script in enumerate(valid_scripts):
            device_id = available_devices[idx % len(available_devices)]
            explicit_imports = extract_imports(script)
            try:
                code = script.read_text(encoding="utf-8")
            except Exception as e:
                logger.error(f"Error reading {script}: {e}")
                continue
            inferred_libraries = infer_missing_libraries(code, model_name=args.model,
                                                           num_queries=args.num_queries,
                                                           device_id=device_id)
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
        for idx, script in enumerate(valid_scripts):
            device_id = available_devices[idx % len(available_devices)]
            output_file = script.parent / f"requirements_{script.stem}.txt"
            generate_requirements(script, output_file, model_name=args.model,
                                  num_queries=args.num_queries, device_id=device_id)
            requirements_files.append(output_file)

    if args.install:
        for req_file in requirements_files:
            install_missing_dependencies(req_file)

    # Use LLM to determine GPU distribution for executing the scripts
    llm_device = available_devices[0] if available_devices else -1
    gpu_allocation = determine_gpu_distribution(valid_scripts, model_name=args.model,
                                                  available_devices=available_devices,
                                                  llm_device=llm_device)

    # Execute scripts
    if args.execute:
        # If interactive input is expected (i.e. sys.stdin is a TTY) and more than one script is to be run,
        # run them sequentially to avoid interleaved prompts.
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
