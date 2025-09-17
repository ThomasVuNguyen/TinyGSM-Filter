import json
import re
import subprocess
import sys
import tempfile
import os
import random
from datasets import load_dataset
from typing import List, Dict, Any, Tuple

def extract_python_code(response_text: str) -> str:
    """Extract the first clean Python function from response."""
    # Try to find code in ```python blocks first
    python_blocks = re.findall(r'```python\s*\n(.*?)\n```', response_text, re.DOTALL)
    if python_blocks:
        code = python_blocks[0].strip()
    else:
        # Try to find standalone function
        def_match = re.search(r'def\s+\w+\([^)]*\)\s*->\s*[^:]+:.*?(?=\n\ndef|\n\nclass|\n\nif|\n\nfor|\n\nwhile|\n\nimport|\n\nfrom|\Z)', response_text, re.DOTALL)
        if def_match:
            code = def_match.group(0).strip()
        else:
            return ""
    
    # Clean up markdown artifacts
    code = re.sub(r'```\s*$', '', code, flags=re.MULTILINE)
    
    # Fix indentation
    lines = code.split('\n')
    if lines and lines[0].startswith('def '):
        for i, line in enumerate(lines[1:], 1):
            if line.strip() and not line.startswith(' '):
                lines[i] = '    ' + line
            elif line.strip() and line.startswith(' '):
                break
        code = '\n'.join(lines)
    
    return code

def run_code(code: str) -> Any:
    """Run Python code and return the result."""
    if not code:
        return None
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        os.unlink(temp_file)
        
        if result.returncode == 0:
            # Try to get the function result
            try:
                exec_globals = {}
                exec(code, exec_globals)
                if 'simple_math_problem' in exec_globals:
                    return exec_globals['simple_math_problem']()
            except:
                pass
            return "Success"
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def download_and_sample_dataset(dataset_name: str, num_samples: int = 100) -> List[Dict[str, Any]]:
    """Download dataset and sample random records from train split."""
    print(f"Downloading dataset: {dataset_name}")
    
    try:
        # Load the dataset
        dataset = load_dataset(dataset_name)
        
        # Get the train split
        if 'train' in dataset:
            train_data = dataset['train']
        else:
            # If no train split, use the first available split
            train_data = dataset[list(dataset.keys())[0]]
        
        # Sample random records
        total_records = len(train_data)
        sample_indices = random.sample(range(total_records), min(num_samples, total_records))
        
        samples = []
        for idx in sample_indices:
            record = train_data[idx]
            # Extract user and assistant columns
            sample = {
                'user': record.get('user', ''),
                'assistant': record.get('assistant', ''),
                'dataset': dataset_name,
                'original_index': idx
            }
            samples.append(sample)
        
        print(f"Sampled {len(samples)} records from {dataset_name}")
        return samples
        
    except Exception as e:
        print(f"Error downloading {dataset_name}: {e}")
        return []

def process_dataset(dataset_name: str, output_name: str, num_samples: int = 100):
    """Process a single dataset from Hugging Face."""
    print(f"Processing {dataset_name}...")
    
    # Download and sample dataset
    data = download_and_sample_dataset(dataset_name, num_samples)
    
    if not data:
        print(f"No data available for {dataset_name}")
        return
    
    results = []
    
    for i, item in enumerate(data):
        response = item.get('assistant', '')
        code = extract_python_code(response)
        result = run_code(code)
        
        results.append({
            'index': i,
            'response': response,
            'code': code,
            'result': result
        })
    
    # Save to separate file
    output_path = f"code_extracted/{output_name}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(results)} items to {output_path}")

def main():
    """Process all datasets."""
    # Use the same dataset list as sample.py
    dataset_list = [
        "ThomasTheMaker/TinyGSM-gpt4.1",
        "ThomasTheMaker/TinyGSM-GPT4.1-no-example", 
        "ThomasTheMaker/TinyGSM-o4-mini",
        "ThomasTheMaker/TinyGSM-GPT-4.1-mini",
        "ThomasTheMaker/TinyGSM-GPT-4.1-mini-no-example",
        "ThomasTheMaker/TinyGSM-Llama3.3-70b",
        "ThomasTheMaker/TinyGSM-Llama3.3-70b-no-example",
        "ThomasTheMaker/TinyGSM-deepseek-r1",
        "ThomasTheMaker/TinyGSM-Mixtral-8x7B",
        "ThomasTheMaker/TinyGSM-Mixtral-8x7B-no-example",
        "ThomasTheMaker/TinyGSM-4.1-nano",
        "ThomasTheMaker/TinyGSM-llama3.1-8b"
    ]
    
    # Create output directory
    os.makedirs('code_extracted', exist_ok=True)
    
    for dataset_name in dataset_list:
        # Create clean output name from dataset name
        output_name = dataset_name.replace('/', '_').replace('-', '_').replace('ThomasTheMaker_TinyGSM_', '')
        process_dataset(dataset_name, output_name, num_samples=100)

if __name__ == "__main__":
    main()
