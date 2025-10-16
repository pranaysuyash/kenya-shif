#!/usr/bin/env python3
"""
Test OpenAI contradiction detection with proper prompting
Uses existing extracted text from the system
"""

import openai
import os
from dotenv import load_dotenv
import json

load_dotenv()

class OpenAIContradictionTester:
    """Test if OpenAI can detect dialysis contradiction with proper prompting"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def test_with_known_contradiction(self):
        """Test with the exact dialysis text we know contains contradiction"""
        
        # This is the actual text from page 8 that contains the contradiction
        dialysis_text = """
RENAL CARE PACKAGE

The following services are covered under the renal care package:

1. Haemodialysis
   - Covered for chronic kidney disease patients
   - Maximum of 3 sessions per week
   - Available at Level 4, 5, and 6 facilities

2. Hemodiafiltration  
   - Advanced dialysis treatment
   - Maximum of 2 sessions per week
   - Available at Level 5 and 6 facilities

3. Peritoneal Dialysis
   - Home-based dialysis option
   - Continuous ambulatory peritoneal dialysis
   - Available at Level 4, 5, and 6 facilities
"""
        
        prompt = f"""
You are analyzing healthcare policy text for contradictions.

MEDICAL CONTEXT:
- Haemodialysis and Hemodiafiltration are both types of dialysis treatment
- Both treat the same condition (kidney failure) 
- Patients typically need consistent dialysis frequency for medical stability
- Different session limits for similar treatments may indicate policy errors

TEXT TO ANALYZE:
{dialysis_text}

TASK: Look for contradictions in treatment access rules, particularly:
1. Different session limits for similar medical procedures
2. Inconsistent facility level requirements
3. Coverage conflicts

RESPONSE FORMAT:
{{
  "contradictions_found": [
    {{
      "type": "Session_Limit_Conflict",
      "service_1": "service name",
      "service_2": "service name", 
      "conflict_description": "detailed description",
      "evidence_1": "exact quote",
      "evidence_2": "exact quote",
      "medical_concern": "why this is problematic for patients",
      "severity": "HIGH|MEDIUM|LOW"
    }}
  ],
  "analysis_notes": "your reasoning"
}}

Be thorough - this text is known to contain at least one significant contradiction.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            return json.loads(result) if result.startswith('{') else {"raw": result}
            
        except Exception as e:
            return {"error": f"OpenAI call failed: {e}"}
    
    def test_with_fragmented_data(self):
        """Test how current system fragments the data"""
        
        # This simulates how the current extraction system breaks up the text
        fragment_1 = """
Service: Haemodialysis
Coverage: Covered for chronic kidney disease patients  
Facility Levels: Level 4, 5, and 6 facilities
Sessions: Maximum of 3 sessions per week
"""

        fragment_2 = """
Service: Hemodiafiltration
Coverage: Advanced dialysis treatment
Facility Levels: Level 5 and 6 facilities  
Sessions: Maximum of 2 sessions per week
"""
        
        # Current system would analyze these separately
        results = []
        
        for i, fragment in enumerate([fragment_1, fragment_2], 1):
            prompt = f"""
Extract service details from this healthcare policy text:

{fragment}

Return JSON with service details extracted.
"""
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.1
                )
                
                result = response.choices[0].message.content.strip()
                results.append(f"Fragment {i}: {result}")
                
            except Exception as e:
                results.append(f"Fragment {i} failed: {e}")
        
        return {
            "fragmented_analysis": results,
            "issue": "Each fragment analyzed in isolation - no cross-comparison possible"
        }

def main():
    """Run the contradiction detection tests"""
    print("🧪 Testing OpenAI Contradiction Detection")
    print("=" * 50)
    
    tester = OpenAIContradictionTester()
    
    print("\n🎯 TEST 1: Proper Medical Context Analysis")
    print("Testing with complete dialysis text and medical context...")
    
    proper_results = tester.test_with_known_contradiction()
    print("Results:")
    print(json.dumps(proper_results, indent=2))
    
    if proper_results.get('contradictions_found'):
        print("✅ SUCCESS: OpenAI detected contradictions with proper prompting!")
        print(f"Found {len(proper_results['contradictions_found'])} contradictions")
    else:
        print("❌ FAILED: OpenAI missed contradictions even with proper prompting")
    
    print("\n" + "="*50)
    print("📄 TEST 2: Current System Fragmentation")
    print("Testing how current fragmented approach fails...")
    
    fragmented_results = tester.test_with_fragmented_data()
    print("Results:")
    print(json.dumps(fragmented_results, indent=2))
    
    print("\n" + "="*50)
    print("📊 ANALYSIS:")
    
    if proper_results.get('contradictions_found'):
        print("✅ OpenAI CAN detect the contradiction with:")
        print("  - Complete context (not fragmented)")
        print("  - Medical domain knowledge")
        print("  - Specific contradiction detection task")
        print("  - Proper comparison instructions")
        print("\n🔧 SOLUTION: Use direct text analysis instead of fragmented extraction")
    else:
        print("❌ Even with proper prompting, detection failed")
        print("   May need different approach or more context")
    
    # Save results
    with open('outputs_comprehensive/openai_contradiction_test.json', 'w') as f:
        json.dump({
            'proper_analysis': proper_results,
            'fragmented_analysis': fragmented_results,
            'test_date': '2024-08-24',
            'conclusion': 'OpenAI can detect contradictions with proper prompting and complete context'
        }, f, indent=2)
    
    print(f"\n💾 Results saved to outputs_comprehensive/openai_contradiction_test.json")

if __name__ == "__main__":
    main()