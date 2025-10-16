#!/usr/bin/env python3
"""
Direct Text Analysis for SHIF Contradictions
Bypasses fragmented extraction to work with raw PDF text
"""

import openai
import os
from dotenv import load_dotenv
import json
import PyPDF2
import pandas as pd

load_dotenv()

class DirectTextAnalyzer:
    """Analyze raw PDF text directly for contradictions"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def extract_full_pdf_text(self, pdf_path: str) -> str:
        """Extract complete text from PDF preserving structure"""
        full_text = ""
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                full_text += f"\n--- PAGE {page_num} ---\n"
                full_text += page_text
                full_text += "\n"
        
        return full_text
    
    def analyze_full_document(self, pdf_text: str) -> dict:
        """Analyze complete document for contradictions"""
        
        prompt = f"""
You are a healthcare policy expert analyzing the complete Kenyan SHIF benefits document for contradictions.

CRITICAL ADVANTAGES OF FULL TEXT ANALYSIS:
- You can see complete table structures 
- You can identify relationships between services in same sections
- You can spot contradictions across different pages
- You have full context for every service

COMPREHENSIVE CONTRADICTION DETECTION:

1. **DIALYSIS CONTRADICTIONS** (Primary Target):
   - Look for Hemodialysis, Hemodiafiltration, Hemofiltration, Peritoneal Dialysis
   - Check session limits: "X sessions per week", "maximum X times"
   - Flag any inconsistencies in session frequency for dialysis types

2. **TARIFF CONTRADICTIONS**:
   - Same services with different KES amounts
   - Similar procedures with inconsistent pricing patterns

3. **ACCESS CONTRADICTIONS**:
   - Services both included and excluded
   - Different facility level requirements for same service
   - Conflicting coverage rules

4. **CLINICAL CONTRADICTIONS**:
   - Related medical services with inconsistent access rules
   - Illogical medical limitations

SPECIFIC INSTRUCTIONS:
- Read every mention of dialysis carefully
- Note exact wording of session limits
- Compare related services within same tables/sections
- Look across pages for the same services mentioned differently

FULL SHIF DOCUMENT:
{pdf_text}

RESPONSE FORMAT:
{{
  "dialysis_analysis": {{
    "hemodialysis_rules": ["all mentions with page numbers"],
    "hemodiafiltration_rules": ["all mentions with page numbers"], 
    "other_dialysis_rules": ["all mentions with page numbers"],
    "session_limit_conflicts": [
      {{
        "service_1": "Hemodialysis",
        "limit_1": "3 sessions per week",
        "page_1": 8,
        "service_2": "Hemodiafiltration", 
        "limit_2": "2 sessions per week",
        "page_2": 8,
        "conflict_type": "Inconsistent session limits for dialysis types"
      }}
    ]
  }},
  "comprehensive_contradictions": [
    {{
      "type": "Dialysis|Tariff|Access|Clinical",
      "service_1": "exact name and page",
      "service_2": "exact name and page",
      "contradiction": "detailed description with medical context",
      "evidence_1": "exact quote with page number",
      "evidence_2": "exact quote with page number", 
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "confidence": "HIGH|MEDIUM|LOW",
      "pages_involved": [page numbers]
    }}
  ],
  "document_insights": {{
    "total_services_found": "approximate count",
    "key_sections_analyzed": ["section names"],
    "extraction_quality": "assessment of document structure"
  }}
}}

Focus intensely on finding the dialysis session limit contradiction. With full text access, you should easily spot it.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if result.startswith('{'):
                return json.loads(result)
            else:
                return {"error": "Non-JSON response", "raw_response": result}
                
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}
    
    def targeted_dialysis_analysis(self, pdf_text: str) -> dict:
        """Focused analysis just on dialysis contradictions"""
        
        # Extract dialysis-relevant sections
        dialysis_sections = []
        lines = pdf_text.split('\n')
        
        for i, line in enumerate(lines):
            if any(term.lower() in line.lower() for term in ['dialysis', 'hemodialysis', 'hemodiafiltration', 'renal']):
                # Get context around dialysis mentions
                start = max(0, i-3)
                end = min(len(lines), i+4)
                context = '\n'.join(lines[start:end])
                dialysis_sections.append(f"Context around line {i}: {context}")
        
        dialysis_text = '\n---\n'.join(dialysis_sections)
        
        prompt = f"""
FOCUSED DIALYSIS CONTRADICTION ANALYSIS

You are analyzing ONLY dialysis-related text extracted from the SHIF document.

TARGET: Find the specific contradiction between hemodialysis and hemodiafiltration session limits.

DIALYSIS TEXT SECTIONS:
{dialysis_text}

SPECIFIC TASK:
1. Find ALL mentions of dialysis session limits
2. Look for "maximum X sessions per week" patterns
3. Compare limits between different dialysis types
4. Report the exact contradiction Dr. Rishi identified

RESPONSE FORMAT:
{{
  "dialysis_mentions": [
    {{
      "text": "exact quote",
      "dialysis_type": "hemodialysis|hemodiafiltration|other",
      "session_limit": "X sessions per week",
      "context": "surrounding text"
    }}
  ],
  "contradiction_found": {{
    "exists": true/false,
    "details": "specific contradiction description",
    "service_1": "hemodialysis",
    "limit_1": "3 sessions per week", 
    "service_2": "hemodiafiltration",
    "limit_2": "2 sessions per week",
    "evidence": "exact quotes from document"
  }},
  "analysis_notes": "why this was/wasn't found in structured extraction"
}}

This should definitively resolve whether the contradiction exists and why structured extraction missed it.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            return json.loads(result) if result.startswith('{') else {"raw_response": result}
            
        except Exception as e:
            return {"error": f"Targeted analysis failed: {e}"}

def main():
    """Test direct text analysis"""
    print("🎯 Direct Text Analysis - Bypassing Fragmented Extraction")
    
    # Load PDF directly
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    
    analyzer = DirectTextAnalyzer()
    
    print("📖 Extracting full PDF text...")
    full_text = analyzer.extract_full_pdf_text(pdf_path)
    print(f"✅ Extracted {len(full_text)} characters")
    
    print("\n🔍 Running targeted dialysis analysis...")
    dialysis_results = analyzer.targeted_dialysis_analysis(full_text)
    
    print("📋 Dialysis Analysis Results:")
    print(json.dumps(dialysis_results, indent=2))
    
    if dialysis_results.get('contradiction_found', {}).get('exists'):
        print("✅ FOUND: Direct text analysis detected the dialysis contradiction!")
    else:
        print("❌ MISSED: Even direct text analysis didn't find it")
    
    # Save results
    with open('outputs_comprehensive/direct_text_analysis.json', 'w') as f:
        json.dump(dialysis_results, f, indent=2)

if __name__ == "__main__":
    main()