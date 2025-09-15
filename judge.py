import openai
import re
from secretkey import RIFT_API_KEY

client = openai.OpenAI(
    api_key=RIFT_API_KEY,
    base_url="https://inference.cloudrift.ai/v1"
)

def judge(question: str, code: str, result: str) -> dict:
    """
    Judge whether the code is runnable and the result is correct.
    
    Args:
        question: The math question
        code: The Python code that was executed
        result: The output from running the code
        
    Returns:
        dict with 'code' (bool), 'correct' (bool), and 'reasoning' (str) keys
    """
    
    # Check if code is runnable (basic check for Python syntax)
    has_code = bool(code.strip())
    has_python_syntax = bool(re.search(r'```python\s*\n.*?\n```', code, re.DOTALL))
    
    # Check if result contains meaningful output
    has_numeric_output = bool(re.search(r'\d+\.?\d*', result))
    has_math_keywords = any(keyword in result.lower() for keyword in 
                           ['answer', 'result', 'solution', '=', 'equals', 'is', 'equals'])
    
    # Code is runnable if it has Python syntax in markdown format
    code_runnable = has_code and has_python_syntax
    
    # Use LLM to verify correctness
    try:
        prompt = f"""
        Question: {question}
        Result: {result}
        
        Is this result correct for the given question? Consider:
        1. Is the mathematical answer accurate?
        2. Does the result make sense for the question?
        3. Is the format appropriate (numbers, units, etc.)?
        
        Please provide:
        1. Your judgment: YES or NO
        2. Brief reasoning for your decision
        
        Format your response as:
        JUDGMENT: [YES/NO]
        REASONING: [Your explanation]
        """
        
        completion = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-70B-Instruct-FP8",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.1
        )
        
        response = completion.choices[0].message.content.strip()
        
        # Parse the response
        lines = response.split('\n')
        judgment = "NO"  # Default
        reasoning = "Unable to parse LLM response"
        
        for line in lines:
            if line.startswith("JUDGMENT:"):
                judgment = line.split("JUDGMENT:")[1].strip().upper()
            elif line.startswith("REASONING:"):
                reasoning = line.split("REASONING:")[1].strip()
        
        correct = judgment == "YES"
        
    except Exception as e:
        print(f"LLM verification failed: {e}")
        # Fallback to basic validation
        correct = has_numeric_output or has_math_keywords
        reasoning = f"LLM verification failed: {e}"
    
    return {
        'code': code_runnable,
        'correct': correct,
        'reasoning': reasoning
    }