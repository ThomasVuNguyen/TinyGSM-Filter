
import os
import json
import random
from datasets import load_dataset
import openai
from typing import List, Dict, Any

# You'll need to set this environment variable or create a secretkey.py file
# export OPENAI_API_KEY="your-api-key-here"
# or create secretkey.py with: RIFT_API_KEY = "your-api-key"

try:
    from secretkey import RIFT_API_KEY
    API_KEY = RIFT_API_KEY
    BASE_URL = "https://inference.cloudrift.ai/v1"
except ImportError:
    API_KEY = os.getenv("OPENAI_API_KEY")
    BASE_URL = "https://api.openai.com/v1"

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

def download_and_sample_dataset(dataset_name: str, num_samples: int = 10) -> List[Dict[str, Any]]:
    """Download dataset and sample random records from train split."""
    # Check if samples already exist
    clean_name = dataset_name.replace('/', '_').replace('-', '_')
    sample_file = f"sample/{clean_name}_samples.json"
    
    if os.path.exists(sample_file):
        print(f"Samples already exist for {dataset_name}, loading from {sample_file}")
        try:
            with open(sample_file, 'r', encoding='utf-8') as f:
                samples = json.load(f)
            print(f"Loaded {len(samples)} existing samples from {dataset_name}")
            return samples
        except Exception as e:
            print(f"Error loading existing samples: {e}, will re-sample")
    
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

def save_samples_to_json(samples: List[Dict[str, Any]], dataset_name: str):
    """Save samples to JSON file in sample/ folder."""
    # Create sample directory if it doesn't exist
    os.makedirs('sample', exist_ok=True)
    
    # Clean dataset name for filename
    clean_name = dataset_name.replace('/', '_').replace('-', '_')
    filename = f"sample/{clean_name}_samples.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    
    print(f"Saved samples to {filename}")


def compare_datasets_with_llm(all_samples: Dict[str, List[Dict[str, Any]]]) -> str:
    """Use LLM to compare all datasets against each other."""
    
    if not API_KEY:
        return "No API key available for LLM comparison"
    
    client = openai.OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )
    
    # Prepare comparison data - use only 1 sample per dataset to reduce token usage
    comparison_data = []
    for dataset_name, samples in all_samples.items():
        # Take 1 sample from each dataset for comparison
        sample = samples[0]
        comparison_data.append({
            'dataset': dataset_name,
            'sample': f"User: {sample['user']}\nAssistant: {sample['assistant']}"
        })
    
    # Create comparison prompt
    comparison_text = ""
    for data in comparison_data:
        comparison_text += f"\n=== {data['dataset']} ===\n{data['sample']}\n"
    
    prompt = f"""
    Analyze these TinyGSM datasets and provide a focused comparison on model differences and example vs no-example modes.

    DATASETS:
    {comparison_text}

    Provide a structured analysis:

    # TINYGSM DATASET COMPARISON

    ## MODEL FAMILY COMPARISONS

    ### GPT-4 Models (gpt4.1, GPT-4.1-mini, 4.1-nano, o4-mini)
    - **Best performing GPT-4 variant**: [Which one and why]
    - **Quality differences**: [How do full vs mini vs nano compare]
    - **Code quality**: [Specific examples of good/bad code]
    - **Mathematical accuracy**: [Which GPT-4 variants are most accurate]

    ### Llama Models (Llama3.3-70b vs llama3.1-8b)
    - **Size impact**: [How does 70B vs 8B affect performance]
    - **Code quality differences**: [Specific examples]
    - **Mathematical accuracy**: [Which is more accurate]

    ### Mixtral Models (Mixtral-8x7B vs Mixtral-8x7B-no-example)
    - **Critical issues**: [What's wrong with Mixtral models]
    - **Error patterns**: [What types of mistakes do they make]
    - **Code quality problems**: [Specific examples of bad code]

    ### DeepSeek (deepseek-r1)
    - **Performance vs others**: [How does it compare to GPT-4 and Llama]
    - **Unique characteristics**: [What makes it different]

    ## EXAMPLE vs NO-EXAMPLE COMPARISONS

    ### GPT4.1 vs GPT4.1-no-example
    - **Key differences**: [Verbosity, approach, quality]
    - **Code structure**: [How does removing examples change the code]
    - **Performance impact**: [Does no-example help or hurt]

    ### GPT-4.1-mini vs GPT-4.1-mini-no-example
    - **Quality comparison**: [How do they compare]
    - **Efficiency**: [Which is more efficient]

    ### Mixtral-8x7B vs Mixtral-8x7B-no-example
    - **Error differences**: [Do both have similar issues]
    - **Quality degradation**: [Is no-example worse]

    ## RANKINGS & RECOMMENDATIONS

    ### Model Ranking (1-11, best to worst)
    1. [Model] - [Why it's best]
    2. [Model] - [Why it's second]
    [Continue for all models]

    ### Example vs No-Example Effectiveness
    - **When to use examples**: [Best use cases]
    - **When to use no-examples**: [Best use cases]
    - **General recommendation**: [Which mode is better overall]

    ### Use Case Recommendations
    - **Production math tasks**: [Best models]
    - **Educational purposes**: [Best models]
    - **Resource-constrained**: [Best lightweight models]

    ## KEY INSIGHTS
    - **Most surprising findings**: [Unexpected results]
    - **Critical issues**: [Major problems to address]
    - **Model patterns**: [Patterns by model family]

    Keep analysis concise but specific with examples.
    """
    
    try:
        completion = client.chat.completions.create(
            model="Qwen/Qwen3-Next-80B-A3B-Thinking",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=3000,
            stream=False,
            top_p=1.0,
            n=1,
            presence_penalty=0.0,
            frequency_penalty=0.0
        )
        
        message = completion.choices[0].message
        response = message.content
        
        # Handle thinking models that put content in reasoning_content
        if response is None and hasattr(message, 'reasoning_content') and message.reasoning_content:
            response = message.reasoning_content
        
        if response is None:
            return "LLM returned no response"
        
        analysis = response.strip()
        return analysis
        
    except Exception as e:
        return f"LLM comparison failed: {e}"

def main():
    """Main function to process all datasets."""
    print("Starting dataset sampling and analysis...")
    
    all_samples = {}
    
    for dataset_name in dataset_list:
        print(f"\nProcessing {dataset_name}...")
        
        # Download and sample dataset
        samples = download_and_sample_dataset(dataset_name, num_samples=10)
        
        if samples:
            # Save samples to JSON
            save_samples_to_json(samples, dataset_name)
            all_samples[dataset_name] = samples
        else:
            print(f"Skipping {dataset_name} due to download errors")
    
    # Compare all datasets with LLM
    if len(all_samples) > 1:
        print(f"\nComparing {len(all_samples)} datasets...")
        comparison_analysis = compare_datasets_with_llm(all_samples)
        
        # Save comparison analysis
        os.makedirs('sample', exist_ok=True)
        with open('sample/dataset_comparison_analysis.md', 'w', encoding='utf-8') as f:
            f.write("Dataset Comparison Analysis\n")
            f.write("=" * 50 + "\n\n")
            f.write(comparison_analysis)
        
        print("Saved comparison analysis to sample/dataset_comparison_analysis.md")
    
    # Create a summary file
    summary = {
        "total_datasets_processed": len(all_samples),
        "datasets": list(all_samples.keys()),
        "samples_per_dataset": 10,
        "comparison_analysis": "dataset_comparison_analysis.md" if len(all_samples) > 1 else None
    }
    
    with open('sample/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nCompleted processing {len(all_samples)} datasets")
    print("All files saved to sample/ folder")

if __name__ == "__main__":
    main()