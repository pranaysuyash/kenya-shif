# CLAUDE CODE AGENT INSTRUCTIONS
## Transform SHIF Analyzer to AI-First Dynamic System

### 📍 CURRENT LOCATION
Working directory: `/Users/pranay/Projects/adhoc_projects/drrishi/final_submission`

### 🎯 MISSION
Transform the rigid pattern-matching SHIF analyzer into an intelligent, dynamic system that actually works with the real SHIF PDF using AI-first approach.

### ⚠️ CRITICAL PROBLEMS TO SOLVE

**PROBLEM 1**: Current `shif_analyzer.py` uses hardcoded regex patterns that likely don't match the real SHIF PDF format
**PROBLEM 2**: No OCR fallback for scanned PDFs
**PROBLEM 3**: Brittle contradiction detection that may miss Dr. Rishi's specific "dialysis 2 vs 3 sessions" case
**PROBLEM 4**: System hasn't been validated against the actual SHIF PDF

### 🔧 REQUIRED IMPLEMENTATION

#### Phase 1: Replace Core Analysis Engine
1. **Replace `shif_analyzer.py`** with the new `intelligent_shif_analyzer.py` approach
2. **Implement missing methods** in the `IntelligentSHIFAnalyzer` class:
   - `_check_general_contradictions_ai()` - for non-dialysis contradictions
   - Error handling for API failures
   - Proper token management for large PDFs

#### Phase 2: Smart PDF Processing Pipeline
```python
# Implement this workflow:
def analyze_pdf(pdf_path):
    # 1. Try pdfplumber extraction
    text_chunks = extract_with_pdfplumber(pdf_path)
    
    # 2. If text is garbled/empty, use OCR
    if is_garbled_text(text_chunks):
        text_chunks = extract_with_ocr(pdf_path)
    
    # 3. Use AI to extract structured rules
    rules = extract_rules_with_ai(text_chunks)
    
    # 4. Use AI to detect contradictions semantically
    contradictions = detect_contradictions_with_ai(rules)
    
    return rules, contradictions
```

#### Phase 3: AI-Powered Rule Extraction
**Implement robust AI extraction that:**
- Chunks large PDFs appropriately for token limits
- Uses specific prompts for SHIF document structure
- Handles AI API failures gracefully with fallback
- Extracts: service names, tariffs (KES), session limits, facility levels, coverage conditions

**Critical AI Prompt Pattern:**
```python
prompt = f"""
Extract healthcare rules from this SHIF document text.
Focus on finding:
- Service names with exact text
- Tariffs in KES (look for patterns like "KES 15000", "Ksh. 2500")  
- Session limits (like "2 sessions per week", "3 times weekly")
- Facility levels (Level 1-6)

Text: {text_chunk}

Return structured JSON with evidence snippets.
"""
```

#### Phase 4: AI-Powered Contradiction Detection
**Implement dialysis-specific detection:**
- Search for dialysis/renal/kidney services first
- Use AI to identify session frequency conflicts
- Look specifically for "2 vs 3 sessions per week" pattern Dr. Rishi mentioned
- Provide page-level evidence for validation

#### Phase 5: Testing & Validation
**Create comprehensive test that:**
1. Downloads the actual SHIF PDF: `https://health.go.ke/sites/default/files/2024-11/TARIFFS%20TO%20THE%20BENEFIT%20PACKAGE%20TO%20THE%20SHI.pdf`
2. Runs the new intelligent analyzer
3. Validates it finds rules (not empty output)
4. Checks specifically for dialysis contradictions
5. Reports whether Dr. Rishi's expected contradiction is found

### 📋 SPECIFIC TASKS

#### Task 1: Update Dependencies
Add to `requirements.txt`:
```
openai>=1.3.0
pytesseract>=0.3.10
pdf2image>=3.1.0
Pillow>=10.0.0
```

#### Task 2: Implement Missing AI Methods
Complete these methods in `IntelligentSHIFAnalyzer`:
- `_check_general_contradictions_ai()` - compare services beyond dialysis
- Add proper error handling for OpenAI API calls
- Implement token counting and chunking for large PDFs

#### Task 3: Create Validation Script
Create `validate_real_pdf.py`:
```python
def test_with_real_shif_pdf():
    # Download real PDF
    # Run intelligent analyzer with OpenAI
    # Check for specific dialysis contradiction
    # Report success/failure with evidence
```

#### Task 4: Fix Session Limit Detection
Enhance AI prompts to catch dialysis session patterns like:
- "hemodialysis 2 sessions per week"
- "chronic dialysis 3 times weekly" 
- "renal replacement therapy twice weekly"

#### Task 5: Error Handling & Fallbacks
Implement robust fallbacks:
- If AI fails → use enhanced pattern matching
- If OCR fails → try different image processing
- If PDF can't be parsed → clear error messages

### 🎯 SUCCESS CRITERIA

**MUST ACHIEVE:**
1. ✅ System downloads and processes real SHIF PDF
2. ✅ Extracts actual rules (not empty output)
3. ✅ Finds dialysis-related contradictions if they exist
4. ✅ Provides page-level evidence for validation
5. ✅ Works with OR without OpenAI API key (graceful degradation)

**VALIDATION TEST:**
```bash
cd /Users/pranay/Projects/adhoc_projects/drrishi/final_submission
python intelligent_shif_analyzer.py --openai-key YOUR_KEY --output test_results
```
Should output:
- `test_results/extracted_rules.csv` with actual SHIF rules
- `test_results/detected_contradictions.csv` with flagged issues
- Console message about dialysis contradictions found/not found

### 🔥 CRITICAL POINTS

1. **NO HARDCODED DATA**: System must extract from actual PDF, not use sample CSVs
2. **EVIDENCE-BASED**: Every contradiction must include page numbers and text snippets
3. **DR. RISHI FOCUS**: Specifically test for "dialysis 2 vs 3 sessions" contradiction
4. **GRACEFUL DEGRADATION**: Work without AI, but warn about reduced accuracy

### 📁 DELIVERABLES

1. **Updated `intelligent_shif_analyzer.py`** - complete implementation
2. **`validate_real_pdf.py`** - test script that proves it works
3. **Updated `requirements.txt`** - with AI/OCR dependencies
4. **`test_results/`** directory with actual extraction outputs
5. **Brief summary** of what contradictions were found in real SHIF PDF

### ⚡ EXECUTION COMMAND

```bash
# Install dependencies
pip install openai pytesseract pdf2image Pillow

# Run the validation test
python validate_real_pdf.py

# Run the main analyzer (if API key available)
python intelligent_shif_analyzer.py --openai-key sk-... --output results
```

### 🎯 EXPECTED OUTCOME

A system that Dr. Rishi can run with confidence, knowing it:
- Actually processes his provided SHIF PDF
- Uses intelligent AI parsing (not brittle patterns)  
- Finds real contradictions with evidence
- Specifically addresses his dialysis sessions concern
- Provides actionable results with page references

**The goal is PROOF that the system works with the real data, not theoretical patterns.**
