#!/usr/bin/env python3
"""
Script 446: File Operations
File management and processing
"""

from pathlib import Path\nimport glob\nimport gzip\nimport json\nimport logging\nimport shutil\nimport sys\nimport tarfile\nimport time\nimport toml\nimport zipfile

def create_sample_files(directory):
    """Create sample files for testing"""
    Path(directory).mkdir(exist_ok=True)
    for i in range(20):
        filepath = Path(directory) / f'file_{i}.txt'
        with open(filepath, 'w') as f:
            f.write(f"Sample content for file {i}\n")
            f.write(f"Timestamp: {datetime.now()}\n")

def process_files(directory):
    """Process files in directory"""
    files = list(Path(directory).glob('*.txt'))
    results = []
    for filepath in files:
        with open(filepath, 'r') as f:
            content = f.read()
            results.append({
                'filename': filepath.name,
                'size': filepath.stat().st_size,
                'lines': len(content.splitlines())
            })
    return results

def compress_directory(source_dir, output_file):
    """Compress directory to zip file"""
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in Path(source_dir).rglob('*'):
            if file.is_file():
                zipf.write(file, file.relative_to(source_dir))

def analyze_files(results):
    """Analyze file statistics"""
    df = pd.DataFrame(results)
    stats = {
        'total_files': len(df),
        'total_size': df['size'].sum(),
        'avg_size': df['size'].mean(),
        'total_lines': df['lines'].sum()
    }
    return stats

if __name__ == "__main__":
    print("File operations...")
    test_dir = 'test_files'
    create_sample_files(test_dir)
    results = process_files(test_dir)
    stats = analyze_files(results)
    print(f"Processed {stats['total_files']} files, total size: {stats['total_size']} bytes")
    compress_directory(test_dir, 'test_files.zip')
    print("Files compressed successfully")
