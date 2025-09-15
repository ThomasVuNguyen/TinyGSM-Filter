#!/usr/bin/env python3
"""
TinyGSM-Filter: Filtering through the synthetically generated TinyGSM dataset

This script processes a dataset with user/assistant pairs where:
- user column contains a math question
- assistant column contains an answer with codeblock used to generate the answer

The script validates:
1. Presence of codeblocks in assistant responses
2. Whether Python codeblocks execute successfully
3. Correctness of results using LLM verification
"""

import json
import re
import subprocess
import tempfile
import os
import sys
from typing import Dict, List, Tuple, Optional
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import time
from judge import judge


class TinyGSMFilter:
    def __init__(self, data_file: str = "data.json"):
        self.data_file = data_file
        self.results = []
        self.dataset_name = self._get_dataset_name()
        self.progress_file = f"results/{self.dataset_name}_progress.json"
        
    def _get_dataset_name(self) -> str:
        """Extract dataset name from data.json file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both old format (string) and new format (object with dataset key)
            if isinstance(data, str):
                dataset_name = data
            elif isinstance(data, dict) and 'dataset' in data:
                dataset_name = data['dataset']
            else:
                return "unknown_dataset"
                
            # Clean up the dataset name for filename
            clean_name = dataset_name.replace('/', '_').replace('\\', '_')
            return clean_name
        except:
            return "unknown_dataset"
    
    def _generate_output_filename(self) -> str:
        """Generate output filename based on dataset name and timestamp"""
        # Create results directory if it doesn't exist
        results_dir = "results"
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(results_dir, f"{self.dataset_name}_filtered_{timestamp}.json")
    
    def _save_progress(self, processed_count: int, total_count: int, filtered_data: List[Dict]):
        """Save progress to resume later"""
        progress_data = {
            'processed_count': processed_count,
            'total_count': total_count,
            'filtered_data': filtered_data,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save progress: {e}")
    
    def _load_progress(self) -> Tuple[int, List[Dict]]:
        """Load progress from previous run"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                
                processed_count = progress_data.get('processed_count', 0)
                filtered_data = progress_data.get('filtered_data', [])
                
                print(f"Found previous progress: {processed_count} records processed, {len(filtered_data)} filtered")
                return processed_count, filtered_data
        except Exception as e:
            print(f"Could not load progress: {e}")
        
        return 0, []
    
    def _clear_progress(self):
        """Clear progress file after completion"""
        try:
            if os.path.exists(self.progress_file):
                os.remove(self.progress_file)
                print("Progress file cleared")
        except Exception as e:
            print(f"Warning: Could not clear progress file: {e}")
        
    def load_data(self) -> List[Dict]:
        """Load data from JSON file or download dataset"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            # Check if it's a dataset name (string) or dataset config (object) or actual data (list)
            if isinstance(content, str):
                print(f"Found dataset name: {content}")
                return self.download_dataset(content)
            elif isinstance(content, dict) and 'dataset' in content:
                print(f"Found dataset config: {content['dataset']}")
                return self.download_dataset(content['dataset'])
            elif isinstance(content, list):
                print(f"Loaded {len(content)} records from {self.data_file}")
                return content
            else:
                print(f"Unexpected data format in {self.data_file}")
                return []
                
        except FileNotFoundError:
            print(f"Error: {self.data_file} not found")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return []
    
    
    def download_dataset(self, dataset_name: str) -> List[Dict]:
        """Download dataset from Hugging Face"""
        try:
            from datasets import load_dataset
            print(f"Downloading dataset: {dataset_name}")
            
            # Load dataset from Hugging Face
            dataset = load_dataset(dataset_name)
            
            # Convert to list of dictionaries
            if 'train' in dataset:
                data = dataset['train'].to_list()
            elif 'test' in dataset:
                data = dataset['test'].to_list()
            else:
                # Use the first available split
                split_name = list(dataset.keys())[0]
                data = dataset[split_name].to_list()
            
            print(f"Downloaded {len(data)} records from {dataset_name}")
            return data
            
        except ImportError:
            print("Error: datasets library not found. Install with: pip install datasets")
            return []
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            return []
    
    def extract_codeblocks(self, text: str) -> List[str]:
        """Extract Python codeblocks from text"""
        # Pattern to match Python codeblocks
        pattern = r'```python\s*\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches
    
    def extract_codeblocks_with_markdown(self, text: str) -> List[str]:
        """Extract Python codeblocks with full markdown formatting"""
        # Pattern to match complete Python codeblocks with markdown
        pattern = r'```python\s*\n.*?\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches
    
    def has_codeblock(self, assistant_text: str) -> bool:
        """Check if assistant response contains a codeblock"""
        codeblocks = self.extract_codeblocks(assistant_text)
        return len(codeblocks) > 0
    
    def execute_python_code(self, code: str) -> Tuple[bool, str, str]:
        """Execute Python code and return success status, stdout, stderr"""
        try:
            # Create a temporary file to execute the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                # Add code to execute the function if it exists
                enhanced_code = code
                
                # Check if code defines a function and add execution
                if 'def ' in code and 'simple_math_problem' in code:
                    enhanced_code += '\n\n# Execute the function and print result\nresult = simple_math_problem()\nprint(result)\n'
                elif 'def ' in code:
                    # Try to find function name and call it
                    import re
                    func_match = re.search(r'def\s+(\w+)\s*\(', code)
                    if func_match:
                        func_name = func_match.group(1)
                        enhanced_code += f'\n\n# Execute the function and print result\ntry:\n    result = {func_name}()\n    print(result)\nexcept Exception as e:\n    print(f"Error executing function: {{e}}")\n'
                
                f.write(enhanced_code)
                temp_file = f.name
            
            # Execute the code
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            # Clean up
            os.unlink(temp_file)
            
            return result.returncode == 0, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Code execution timed out"
        except Exception as e:
            return False, "", str(e)
    
    def verify_with_llm(self, question: str, code: str, result: str) -> dict:
        """Verify correctness using LLM judge"""
        return judge(question, code, result)
    
    def process_record(self, record: Dict) -> Dict:
        """Process a single user/assistant record"""
        user_question = record.get('user', '')
        assistant_response = record.get('assistant', '')
        
        # Extract codeblocks (raw code for execution)
        codeblocks = self.extract_codeblocks(assistant_response)
        # Extract codeblocks with markdown (for LLM judge)
        codeblocks_with_markdown = self.extract_codeblocks_with_markdown(assistant_response)
        
        # Initialize result with original columns plus new ones
        result = {
            'user': user_question,
            'assistant': assistant_response,
            'code': False,  # New column: does the output contain runnable code
            'correct': False,  # New column: is the output correct
            'result': '',  # New column: result of code execution
            'reasoning': '',  # New column: LLM reasoning for judgment
            'has_codeblock': len(codeblocks) > 0,
            'codeblocks': codeblocks,
            'code_execution': {},
            'llm_verification': {}
        }
        
        # Test each codeblock
        for i, code in enumerate(codeblocks):
            print(f"  Executing codeblock {i+1}: {code[:50]}...")
            success, stdout, stderr = self.execute_python_code(code)
            result['code_execution'][f'codeblock_{i}'] = {
                'success': success,
                'stdout': stdout,
                'stderr': stderr
            }
            
            print(f"  Execution result: success={success}, stdout='{stdout.strip()}'")
            
            # Store the execution result (use the first successful execution)
            if success and not result['result']:
                result['result'] = stdout.strip()
            
            # Verify with LLM if code executed successfully
            if success and i < len(codeblocks_with_markdown):
                print(f"  Sending to LLM judge: question='{user_question[:50]}...', result='{stdout.strip()}'")
                llm_result = self.verify_with_llm(user_question, codeblocks_with_markdown[i], stdout)
                result['llm_verification'][f'codeblock_{i}'] = llm_result
                
                print(f"  LLM judge result: {llm_result}")
                
                # Update overall code and correct status
                result['code'] = result['code'] or llm_result['code']
                result['correct'] = result['correct'] or llm_result['correct']
                
                # Store reasoning from the first LLM judgment
                if not result['reasoning']:
                    result['reasoning'] = llm_result['reasoning']
        
        return result
    
    def filter_dataset(self) -> List[Dict]:
        """Filter the entire dataset"""
        data = self.load_data()
        if not data:
            return []
        
        # Try to load previous progress
        start_index, filtered_data = self._load_progress()
        
        if start_index > 0:
            print(f"Resuming from record {start_index + 1}/{len(data)}")
            print(f"Already have {len(filtered_data)} filtered records")
        else:
            print("Processing dataset from beginning...")
        
        output_file = self._generate_output_filename()
        
        # ETA tracking variables
        start_time = time.time()
        last_eta_update = start_time
        
        for i, record in enumerate(data[start_index:], start=start_index):
            current_time = time.time()
            
            # Calculate ETA every 5 records or every 30 seconds
            if i % 5 == 0 or (current_time - last_eta_update) > 30:
                if i > 0:
                    elapsed_time = current_time - start_time
                    avg_time_per_record = elapsed_time / i
                    remaining_records = len(data) - i
                    eta_seconds = remaining_records * avg_time_per_record
                    eta_time = datetime.now() + timedelta(seconds=eta_seconds)
                    
                    print(f"Processing record {i+1}/{len(data)} - ETA: {eta_time.strftime('%H:%M:%S')} ({remaining_records} records remaining)")
                else:
                    print(f"Processing record {i+1}/{len(data)}")
                
                last_eta_update = current_time
            else:
                print(f"Processing record {i+1}/{len(data)}")
            
            result = self.process_record(record)
            self.results.append(result)
            
            # Keep records that have codeblocks and execute successfully
            if (result['has_codeblock'] and 
                any(exec_result['success'] for exec_result in result['code_execution'].values())):
                # Add the processed record with new columns to filtered data
                filtered_record = {
                    'user': result['user'],
                    'assistant': result['assistant'],
                    'code': result['code'],
                    'correct': result['correct'],
                    'result': result['result'],
                    'reasoning': result['reasoning']
                }
                filtered_data.append(filtered_record)
                
                # Save incrementally every 10 records or at the end
                if len(filtered_data) % 10 == 0 or i == len(data) - 1:
                    self._save_incremental_results(filtered_data, output_file)
                    print(f"  Saved {len(filtered_data)} records so far...")
            
            # Save progress every 5 records
            if i % 5 == 0:
                self._save_progress(i + 1, len(data), filtered_data)
        
        # Final timing summary
        total_time = time.time() - start_time
        print(f"Filtered dataset: {len(filtered_data)}/{len(data)} records passed")
        print(f"Total processing time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        print(f"Average time per record: {total_time/len(data):.2f} seconds")
        
        # Clear progress file after completion
        self._clear_progress()
        
        return filtered_data
    
    def _save_incremental_results(self, filtered_data: List[Dict], output_file: str):
        """Save results incrementally to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save incremental results: {e}")
    
    def save_results(self, output_file: str = None):
        """Save filtered results to file"""
        if output_file is None:
            output_file = self._generate_output_filename()
            
        filtered_data = []
        for r in self.results:
            if r['has_codeblock'] and any(exec_result['success'] for exec_result in r['code_execution'].values()):
                filtered_record = {
                    'user': r['user'],
                    'assistant': r['assistant'],
                    'code': r['code'],
                    'correct': r['correct'],
                    'result': r['result'],
                    'reasoning': r['reasoning']
                }
                filtered_data.append(filtered_record)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(filtered_data)} filtered records to {output_file}")
        return output_file
    
    def generate_report(self):
        """Generate a summary report"""
        total = len(self.results)
        has_codeblock = sum(1 for r in self.results if r['has_codeblock'])
        successful_execution = sum(1 for r in self.results 
                                 if r['has_codeblock'] and 
                                 any(exec_result['success'] for exec_result in r['code_execution'].values()))
        has_runnable_code = sum(1 for r in self.results if r['code'])
        is_correct = sum(1 for r in self.results if r['correct'])
        
        print("\n" + "="*50)
        print("FILTERING REPORT")
        print("="*50)
        print(f"Total records processed: {total}")
        print(f"Records with codeblocks: {has_codeblock} ({has_codeblock/total*100:.1f}%)")
        print(f"Records with successful code execution: {successful_execution} ({successful_execution/total*100:.1f}%)")
        print(f"Records with runnable code: {has_runnable_code} ({has_runnable_code/total*100:.1f}%)")
        print(f"Records with correct results: {is_correct} ({is_correct/total*100:.1f}%)")
        print("="*50)


def main():
    parser = argparse.ArgumentParser(description='Filter TinyGSM dataset')
    parser.add_argument('data_file', help='Input data file containing dataset name')
    parser.add_argument('--output', help='Output file (auto-generated if not specified)')
    
    args = parser.parse_args()
    
    # Initialize filter
    filter_tool = TinyGSMFilter(args.data_file)
    
    print(f"Dataset: {filter_tool.dataset_name}")
    output_file = filter_tool._generate_output_filename()
    print(f"Output file: {output_file}")
    print("Results will be saved incrementally as processing continues...")
    print("All results will be saved in the 'results/' folder")
    
    # Process and filter dataset (downloads automatically and saves incrementally)
    filtered_data = filter_tool.filter_dataset()
    
    # Generate report
    filter_tool.generate_report()
    
    print(f"\nFiltering complete! Final results saved to: {output_file}")
    print(f"Total filtered records: {len(filtered_data)}")


if __name__ == "__main__":
    main()