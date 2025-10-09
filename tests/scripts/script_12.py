# File System Operations and Path Handling
import os
import shutil
import glob
import pathlib
from pathlib import Path
import tempfile
import zipfile
import tarfile
import json
import csv
import configparser

def file_operations():
    """Basic file operations"""
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "test.txt")
    
    # Create and write file
    with open(temp_file, 'w') as f:
        f.write("Hello, World!\nThis is a test file.")
    
    # Read file
    with open(temp_file, 'r') as f:
        content = f.read()
    
    # File stats
    stats = os.stat(temp_file)
    size = stats.st_size
    
    # Cleanup
    shutil.rmtree(temp_dir)
    
    return {'size': size, 'content_length': len(content)}

def path_operations():
    """Path handling with pathlib"""
    current_path = Path.cwd()
    temp_path = Path(tempfile.gettempdir())
    
    # Create directory structure
    test_dir = temp_path / "test_directory"
    test_dir.mkdir(exist_ok=True)
    
    # Create files
    for i in range(3):
        file_path = test_dir / f"file_{i}.txt"
        file_path.write_text(f"Content of file {i}")
    
    # List files
    files = list(test_dir.glob("*.txt"))
    
    # Cleanup
    shutil.rmtree(test_dir)
    
    return {'current_path': str(current_path), 'files_created': len(files)}

def archive_operations():
    """Archive file operations"""
    temp_dir = tempfile.mkdtemp()
    
    # Create some files
    files = []
    for i in range(3):
        file_path = os.path.join(temp_dir, f"document_{i}.txt")
        with open(file_path, 'w') as f:
            f.write(f"Document {i} content\nLine 2\nLine 3")
        files.append(file_path)
    
    # Create ZIP archive
    zip_path = os.path.join(temp_dir, "archive.zip")
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for file_path in files:
            zip_file.write(file_path, os.path.basename(file_path))
    
    # Create TAR archive
    tar_path = os.path.join(temp_dir, "archive.tar.gz")
    with tarfile.open(tar_path, 'w:gz') as tar_file:
        for file_path in files:
            tar_file.add(file_path, arcname=os.path.basename(file_path))
    
    # Check archive contents
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        zip_contents = zip_file.namelist()
    
    # Cleanup
    shutil.rmtree(temp_dir)
    
    return {'zip_files': len(zip_contents), 'original_files': len(files)}

def config_file_handling():
    """Configuration file handling"""
    temp_dir = tempfile.mkdtemp()
    
    # JSON config
    json_config = {
        'database': {'host': 'localhost', 'port': 5432},
        'logging': {'level': 'INFO', 'file': 'app.log'}
    }
    json_path = os.path.join(temp_dir, 'config.json')
    with open(json_path, 'w') as f:
        json.dump(json_config, f, indent=2)
    
    # INI config
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'debug': 'false', 'timeout': '30'}
    config['server'] = {'host': '127.0.0.1', 'port': '8080'}
    ini_path = os.path.join(temp_dir, 'config.ini')
    with open(ini_path, 'w') as f:
        config.write(f)
    
    # CSV data
    csv_path = os.path.join(temp_dir, 'data.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Age', 'City'])
        writer.writerow(['Alice', '25', 'New York'])
        writer.writerow(['Bob', '30', 'San Francisco'])
    
    # Read back
    with open(json_path, 'r') as f:
        loaded_json = json.load(f)
    
    loaded_config = configparser.ConfigParser()
    loaded_config.read(ini_path)
    
    with open(csv_path, 'r') as f:
        csv_reader = csv.reader(f)
        csv_rows = list(csv_reader)
    
    # Cleanup
    shutil.rmtree(temp_dir)
    
    return {
        'json_keys': len(loaded_json),
        'ini_sections': len(loaded_config.sections()),
        'csv_rows': len(csv_rows)
    }

if __name__ == "__main__":
    print("File system operations...")
    
    file_result = file_operations()
    print(f"File operations: {file_result}")
    
    path_result = path_operations()
    print(f"Path operations: {path_result}")
    
    archive_result = archive_operations()
    print(f"Archive operations: {archive_result}")
    
    config_result = config_file_handling()
    print(f"Config handling: {config_result}")
