Dataset Comparison Analysis
==================================================

# TINYGSM DATASET COMPARISON  

## MODEL FAMILY COMPARISONS  

### **GPT-4 Models**  
- **Best performing variant**: `o4-mini` (Microsoft's optimized GPT-4 variant)  
  - **Why**: Provides explicit step-by-step *reasoning* before code (e.g., car loan calculation), making it ideal for education. Code is precise, with clear variable names and mathematical formulas.  
- **Quality differences**:  
  - Full `GPT-4`/`GPT-4.1`: Concise code with inline comments (e.g., apple problem), but lacks explicit reasoning steps.  
  - `GPT-4.1-mini`/`4.1-nano`: Slightly more verbose than full GPT-4 but less structured than `o4-mini`.  
  - **Code quality**: All GPT-4 variants produce correct code. `o4-mini` excels in explaining *why* (e.g., "monthly_rate = 0.05 / 12" with context), while others focus on *how*.  
- **Mathematical accuracy**: **100% accurate** across all GPT-4 variants.  

### **Llama Models**  
- **Size impact**: **70B is worse than 8B** for this task.  
  - `Llama3.3-70b`: Incorrectly assumed all remaining students scored <40 marks (problem only gave 25% >90 and 30% 60–80; 45% remaining could include 40–59 scores).  
  - `Llama3.1-8b`: Correctly calculated pizza circumference using `2 * pi * radius`.  
- **Code quality differences**:  
  - 70B: Poor reasoning (e.g., "assuming remaining students scored less than 40" without evidence).  
  - 8B: Clean, minimal code with valid math (no flawed assumptions).  
- **Mathematical accuracy**:  
  - 70B: **Incorrect** (critical logical error).  
  - 8B: **Correct**.  

### **Mixtral Models**  
- **Critical issues**:  
  - `Mixtral-8x7B` (example mode): **Incomplete code** (only `total_pencils = 336` – no solution).  
  - `Mixtral-8x7B-no-example`: Includes `print(simple_math_problem())` *outside the function* – invalid for production code (though correct mathematically).  
- **Error patterns**:  
  - Example mode fails to generate full code (critical bug).  
  - No-example mode over-engineers responses (extra `print` + explanations in code block).  
- **Code quality problems**:  
  - Mixtral's example version is broken; no-example version is functional but unclean (mixing code and explanations).  

### **DeepSeek (deepseek-r1)**  
- **Performance vs others**: **Top-tier** – matches `o4-mini` in clarity but with even more detailed step-by-step reasoning (e.g., cafeteria tax calculation: "subtotal = 400", "tax = 24", "total = 424").  
- **Unique characteristics**:  
  - Verbal reasoning precedes code (e.g., "Calculate total sandwiches revenue: 120 * 2 = $240").  
  - Better for educational contexts than pure code-focused models.  

---

## EXAMPLE VS NO-EXAMPLE COMPARISONS  

### **GPT4.1 vs GPT4.1-no-example**  
- **Key differences**:  
  - `GPT4.1`: Simple code with minimal comments (e.g., "apples_per_bag = 7").  
  - `GPT4.1-no-example`: **Detailed step-by-step comments** (e.g., "# Calculate total sales revenue", "# Calculate number of salesmen needed").  
- **Code structure**: No-example mode adds explicit intermediate steps as comments, improving readability.  
- **Performance impact**: **No-example mode is better** – structured steps reduce ambiguity for learners.  

### **GPT-4.1-mini vs GPT-4.1-mini-no-example**  
- **Quality comparison**: Minimal difference. Both are concise and correct (e.g., sticker problem: `stars = 60 * 2/5`).  
- **Efficiency**: No-example mode is slightly more verbose but same functionality.  

### **Mixtral-8x7B vs Mixtral-8x7B-no-example**  
- **Error differences**:  
  - Example mode: **Broken** (incomplete code).  
  - No-example mode: Functional but includes non-essential `print` and explanations.  
- **Quality degradation**: Example mode is **catastrophically worse** – no solution at all. No-example mode is usable but unpolished.  

---

## RANKINGS & RECOMMENDATIONS  

### **Model Ranking (1-11, best to worst)**  
1. **`TinyGSM-o4-mini`** – Best balance of reasoning + code clarity.  
2. **`deepseek-r1`** – Superior step-by-step explanations; ideal for teaching.  
3. **`TinyGSM-GPT-4.1`** / **`TinyGSM-4.1-nano`** – Clean, accurate code.  
4. **`TinyGSM-Llama3.1-8b`** – Correct for simple problems.  
5. **`TinyGSM-Mixtral-8x7B-no-example`** – Functional but messy output.  
6. **`TinyGSM-GPT-4.1-mini`** – Adequate but less structured than `o4-mini`.  
7. **`TinyGSM-Llama3.3-70b`** – Logical errors (e.g., flawed assumptions).  
8. **`TinyGSM-Mixtral-8x7B`** – **Broken code** (incomplete).  

### **Example vs No-Example Effectiveness**  
- **When to use examples**:  
  - **Not recommended** for Mixtral (example mode fails) or Llama (70B has errors).  
  - Only useful for GPT-4 when minimal comments suffice (e.g., simple arithmetic).  
- **When to use no-example**:  
  - **Always preferred for GPT-4 models** – structured step-by-step comments improve clarity.  
  - Critical for Mixtral (example mode is broken; no-example is salvageable).  
- **General recommendation**: **"No-example" mode is better overall** – it enforces detailed code explanations without relying on faulty example prompts.  

### **Use Case Recommendations**  
- **Production math tasks**: `o4-mini` or `deepseek-r1` (most reliable, explicit logic).  
- **Educational purposes**: `deepseek-r1` (best for teaching problem-solving steps).  
- **Resource-constrained**: `GPT-4.1-mini` or `Llama3.1-8b` (smaller model size, still accurate).  

---

## KEY INSIGHTS  
- **Most surprising finding**: **Larger models (70B Llama) are less reliable** than smaller ones (8B Llama) for logical reasoning – size ≠ capability.  
- **Critical issues**:  
  - Mixtral’s "example" mode **fails to generate code** (unusable).  
  - Llama 70B makes **unjustified assumptions** (e.g., "all remaining students scored <40").  
- **Model patterns**:  
  - GPT-4 variants and DeepSeek prioritize **structured reasoning**.  
  - Mixtral and Llama show **poor error handling** – often missing code or making incorrect inferences.  
- **Takeaway**: **"No-example" mode is safer** for all models except GPT-4 (where it’s marginally better). For critical tasks, **avoid Mixtral example mode entirely** and **skip Llama 70B**.