# TinyGSM-Filter

A comprehensive analysis and filtering tool for the TinyGSM (Tiny Grade School Math) dataset, designed to evaluate and compare different language models' mathematical reasoning capabilities.

## Overview

This repository provides tools to analyze, extract, and evaluate code solutions from various language models on mathematical problems. It focuses on the TinyGSM dataset, which contains grade school math problems with code-based solutions.

## Background

The TinyGSM dataset contains synthetically generated mathematical problems where:
- **User column**: Contains a math question/problem
- **Assistant column**: Contains the model's response with code blocks used to generate the answer

## Features

### 🔍 **Dataset Analysis**
- Compare multiple language models side-by-side
- Extract and execute Python code from model responses
- Validate mathematical correctness
- Generate comprehensive comparison reports

### 🤖 **Supported Models**
- **GPT-4 Family**: gpt4.1, GPT-4.1-mini, 4.1-nano, o4-mini
- **Llama Models**: Llama3.3-70b, llama3.1-8b
- **Mixtral Models**: Mixtral-8x7B (with/without examples)
- **DeepSeek**: deepseek-r1
- **No-Example Variants**: Compare models with and without examples

### 📊 **Code Extraction & Execution**
- Automatically extract Python code from model responses
- Execute code safely with timeout protection
- Validate mathematical accuracy
- Generate detailed execution reports

## Installation

```bash
git clone https://github.com/yourusername/TinyGSM-Filter.git
cd TinyGSM-Filter
pip install -r requirements.txt
```

### Requirements
- Python 3.8+
- datasets
- openai
- json
- re
- subprocess

## Usage

### 1. Download and Sample Datasets

```bash
python3 sample.py
```

This will:
- Download all TinyGSM datasets from Hugging Face
- Sample 1000 records from each dataset
- Save samples to `sample/` directory
- Generate comparison analysis

### 2. Extract and Execute Code

```bash
python3 decipher.py
```

This will:
- Download datasets directly from Hugging Face
- Extract Python code from model responses
- Execute code and validate results
- Save results to `code_extracted/` directory

### 3. Filter and Judge Responses

```bash
python3 filter.py
python3 judge.py
```

## File Structure

```
TinyGSM-Filter/
├── sample.py              # Main dataset sampling script
├── decipher.py            # Code extraction and execution
├── filter.py              # Response filtering
├── judge.py               # Response quality judging
├── secretkey.py           # API key configuration
├── sample/                # Downloaded dataset samples
├── code_extracted/        # Extracted code and results
└── README.md             # This file
```

## Output Format

### Dataset Samples (`sample/`)
```json
{
  "user": "Maria was going to the store to buy apples...",
  "assistant": "def simple_math_problem() -> int:\n    return 42",
  "dataset": "ThomasTheMaker/TinyGSM-gpt4.1",
  "original_index": 123
}
```

### Code Extraction (`code_extracted/`)
```json
{
  "index": 0,
  "response": "def simple_math_problem() -> int:\n    return 42",
  "code": "def simple_math_problem() -> int:\n    return 42",
  "result": 42
}
```

## Configuration

Edit `sample.py` to modify:
- `SAMPLES_PER_DATASET`: Number of samples per dataset (default: 1000)
- `LLM_MODEL`: Model for analysis (default: "Qwen/Qwen3-Next-80B-A3B-Thinking")
- `LLM_MAX_TOKENS`: Maximum tokens for analysis
- `LLM_TEMPERATURE`: Temperature for analysis

## API Setup

Create `secretkey.py` with your API key:
```python
RIFT_API_KEY = "your-api-key-here"
```

Or set environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Analysis Results

The tool provides comprehensive analysis including:

### Model Performance Comparison
- Mathematical accuracy rates
- Code quality assessment
- Response structure analysis
- Error pattern identification

### Example vs No-Example Analysis
- Performance impact of examples
- Quality differences between variants
- Use case recommendations

### Model Rankings
- Best performing models for math tasks
- Resource-constrained recommendations
- Educational vs production use cases

## Key Insights

Based on analysis results:
- **GPT-4.1 and o4-mini** show highest execution success rates
- **4.1-nano** has some formatting issues but correct math
- **Mixtral models** show significant error patterns
- **No-example variants** generally perform worse

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- TinyGSM dataset creators
- Hugging Face for dataset hosting
- OpenAI for API access
- Community contributors

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{tinygsm_filter,
  title={TinyGSM-Filter: A Tool for Analyzing Mathematical Reasoning in Language Models},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/TinyGSM-Filter}
}
```