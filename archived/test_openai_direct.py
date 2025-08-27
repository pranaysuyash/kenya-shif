#!/usr/bin/env python3
"""
Test OpenAI API directly with healthcare text samples
"""

import openai
import os

def test_openai_api():
    """Test if OpenAI API is working with the provided key"""
    
    api_key = '"OPENAI_API_KEY_REMOVED"'
    
    print("=== TESTING OPENAI API ===")
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a sample healthcare text that might be in the PDF
        sample_text = """
        Dental Services Coverage:
        - Routine dental examination and cleaning
        - Tooth extraction (simple)
        - Dental fillings (composite)
        - Emergency dental care
        Level 2-4 facilities
        Pre-authorization required for complex procedures
        Limit: 2 visits per beneficiary per year
        """
        
        prompt = f"""You are extracting healthcare benefits from the Kenyan SHIF tariff document.

Return a SINGLE valid JSON object ONLY, no prose, no markdown, no commentary.

TEXT:
<<<
{sample_text}
>>>

REQUIRED JSON FIELDS (exact keys) with native JSON types:
{{
  "service": string,
  "tariff_value": number | null,
  "tariff_unit": "per_session"|"per_visit"|"per_consultation"|"per_procedure"|"per_scan"|"per_day"|"per_month"|"per_year"|"monthly"|"quarterly"|"annual"|"unspecified",
  "facility_levels": [number],
  "coverage_status": "included"|"excluded",
  "limits": {{
    "per_week": number | null,
    "per_month": number | null, 
    "per_year": number | null,
    "max_days": number | null
  }},
  "medical_category": "dialysis"|"maternity"|"oncology"|"imaging"|"surgery"|"mental"|"stroke"|"outpatient"|"emergency"|"dental"|"other"
}}

OUTPUT: Return ONLY the JSON object."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content.strip()
        print("\n=== OPENAI RESPONSE ===")
        print(response_text)
        
        # Try to parse as JSON
        import json
        try:
            result = json.loads(response_text)
            print("\n=== PARSED JSON ===")
            for key, value in result.items():
                print(f"{key}: {value}")
            print("\n✅ OpenAI API is working correctly!")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False

def run_enhanced_extraction():
    """Run the main analyzer with working OpenAI"""
    
    if not test_openai_api():
        print("OpenAI API test failed, cannot proceed with enhanced extraction")
        return
    
    print("\n" + "="*60)
    print("RUNNING ENHANCED EXTRACTION WITH OPENAI")
    print("="*60)
    
    os.system("python shif_analyzer.py --output outputs_with_openai")

if __name__ == "__main__":
    run_enhanced_extraction()
