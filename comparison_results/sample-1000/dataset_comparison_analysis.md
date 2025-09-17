Dataset Comparison Analysis
==================================================

# TINYGSM DATASET COMPARISON

## MODEL FAMILY COMPARISONS

### GPT-4 Models (gpt4.1, GPT-4.1-mini, 4.1-nano, o4-mini)
- **Best performing GPT-4 variant**: **o4-mini** (correctly handles bookstore profit calculation with detailed reasoning steps and accurate math). Full GPT-4.1 also strong with correct bike savings logic.
- **Quality differences**:  
  - *o4-mini*: Best structured reasoning with clear step-by-step explanations before code.  
  - *GPT-4.1 (full)*: Correct complex logic (e.g., conditional bike purchase handling).  
  - *GPT-4.1-mini*: Accurate for simple division (gum: 15/2=7.5 days).  
  - *4.1-nano*: Critical error (forgot Sophia in sandwich count: 8 friends + Sophia = 9 people, code used only 8).  
- **Code quality**: o4-mini and GPT-4.1 show clear variable naming and logical flow. 4.1-nano has missing participant logic.  
- **Mathematical accuracy**: o4-mini (100%), GPT-4.1 (100%), GPT-4.1-mini (100%). 4.1-nano fails (8×2=16 sandwiches vs correct 9×2=18).

### Llama Models (Llama3.3-70b vs llama3.1-8b)
- **Size impact**: 70B model handles complex logic (multiplication problem with nested loops), while 8B handles basic arithmetic well.  
- **Code quality differences**:  
  - *Llama3.3-70b*: Correctly implements brute-force search for smallest multiplicand (10×100=1000).  
  - *Llama3.1-8b*: Clean code for simple pencil problem (9-4+2=7), but lacks complexity handling.  
- **Mathematical accuracy**: Both fully accurate for their problems. Llama3.3-70b demonstrates advanced algorithmic thinking.

### Mixtral Models (Mixtral-8x7B vs Mixtral-8x7B-no-example)
- **Critical issues**: **Both variants fail completely** - code cuts off mid-calculation (e.g., "tank_total_capacity = 4500" with no further steps).  
- **Error patterns**: Systematic failure to complete solutions, even for trivial problems (e.g., tank capacity requires only `4500 - 3200`).  
- **Code quality problems**: No meaningful variables or operations generated. Mixtral consistently produces incomplete code regardless of prompt type.

### DeepSeek (deepseek-r1)
- **Performance vs others**: Matches top models in correctness (12+8=20 fruits), with superior clarity.  
- **Unique characteristics**: Includes structured "Reasoning" section before code, making steps transparent. Code uses explicit `float(total_fruits)` for consistency.

## EXAMPLE vs NO-EXAMPLE COMPARISONS

### GPT4.1 vs GPT4.1-no-example
- **Key differences**:  
  - *Example mode*: Correct conditional logic for bike purchase (checks `bike_cost > money_invested` properly).  
  - *No-example*: Generates negative cookies (John has 40/9≈4.44, eats half → 2.22, then gives away 3 → -0.78).  
- **Code structure**: Example mode includes detailed mathematical reasoning steps. No-example lacks contextual validation.  
- **Performance impact**: Example mode prevents critical errors (e.g., negative values). No-example fails basic sanity checks.

### GPT-4.1-mini vs GPT-4.1-mini-no-example
- **Quality comparison**:  
  - *Mini example*: Correctly calculates gum days (15/2=7.5).  
  - *Mini no-example*: Misinterprets "buys 2/3 of them" as initial cherries (160×2/3=106.67) instead of remaining after giving away half (80×2/3≈53.33).  
- **Efficiency**: Example mode produces 100% accurate results; no-example introduces logical errors in basic fraction handling.

### Mixtral-8x7B vs Mixtral-8x7B-no-example
- **Error differences**: Identical failure modes - both stop mid-solution with incomplete code.  
- **Quality degradation**: No difference; Mixtral fundamentally cannot generate complete code regardless of prompt type.

## RANKINGS & RECOMMENDATIONS

### Model Ranking (1-11, best to worst)
1. **o4-mini** - Structured reasoning + perfect math (bookstore profit)  
2. **Llama3.3-70b** - Accurate complex logic (multiplication brute force)  
3. **deepseek-r1** - Clear reasoning + correct simple math  
4. **GPT-4.1 (full)** - Correct complex conditional logic (bike savings)  
5. **Llama3.1-8b** - Clean code for basic arithmetic (pencils)  
6. **GPT-4.1-mini** - Accurate simple division (gum)  
7. **GPT-4.1-no-example** - Flawed logic (negative cookies)  
8. **GPT-4.1-mini-no-example** - Misinterprets "them" in cherry problem  
9. **4.1-nano** - Missing participant (forgot Sophia)  
10. **Mixtral-8x7B** - Incomplete code (tank capacity cut off)  
11. **Mixtral-8x7B-no-example** - Same incomplete code failure  

### Example vs No-Example Effectiveness
- **When to use examples**: Always for multi-step problems (e.g., bookstore profit, bike savings). Critical for preventing logical errors and ensuring step-by-step validation.  
- **When to use no-examples**: Never recommended. Even simple problems (e.g., cherries) show errors without examples.  
- **General recommendation**: **Always use example-based prompts**. Example mode consistently improves accuracy by forcing structured reasoning.

### Use Case Recommendations
- **Production math tasks**: `o4-mini` (best structure) or `deepseek-r1` (clarity + correctness)  
- **Educational purposes**: `Llama3.3-70b` (complex problem-solving) or `GPT-4.1` (detailed explanations)  
- **Resource-constrained**: `GPT-4.1-mini` or `Llama3.1-8b` (accurate for simple problems)  

## KEY INSIGHTS
- **Most surprising findings**: Mixtral's complete failure despite MoE architecture, while smaller models (Llama3.1-8b, GPT-4.1-mini) handle simple problems flawlessly.  
- **Critical issues**: No-example mode consistently introduces errors (e.g., negative values, misinterpreted references), while example mode prevents these. Mixtral's code generation is fundamentally broken.  
- **Model patterns**:  
  - GPT-4 variants and Llama models excel with structured examples.  
  - DeepSeek's "Reasoning" section is a standout feature for clarity.  
  - Mixtral consistently fails to complete code, indicating severe architecture limitations.