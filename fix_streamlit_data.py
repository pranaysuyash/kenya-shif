#!/usr/bin/env python3
"""
Create Streamlit-compatible data structure from our analysis results
"""
import json
import pandas as pd
from pathlib import Path

print("=== FIXING STREAMLIT DATA STRUCTURE ===")
print()

# Load our comprehensive analysis
input_file = "outputs/integrated_comprehensive_analysis.json"
output_file = "outputs/shif_healthcare_pattern_complete_analysis.json"

print(f"1. Loading analysis from: {input_file}")
with open(input_file, 'r') as f:
    our_data = json.load(f)

print(f"   ✅ Loaded data with keys: {list(our_data.keys())}")

# Extract structured rules from policy_results
print()
print("2. Extracting structured rules...")
structured_rules = []

if 'policy_results' in our_data:
    # Try to parse the structured data
    policy_results = our_data['policy_results']
    
    # Check if we have CSV files we can load instead
    structured_csv = Path("outputs_run_20250827_215550/rules_p1_18_structured.csv")
    if structured_csv.exists():
        print("   Loading from CSV for better structure...")
        import pandas as pd
        rules_df = pd.read_csv(structured_csv)
        structured_rules = rules_df.to_dict('records')
        print(f"   ✅ Loaded {len(structured_rules)} structured rules from CSV")
    else:
        print("   ⚠️  Using JSON string data (limited)")
        
# Extract AI analysis
print()
print("3. Extracting AI analysis...")
ai_gaps = our_data.get('ai_analysis', {}).get('gaps', [])
ai_contradictions = our_data.get('ai_analysis', {}).get('contradictions', [])

print(f"   ✅ Found {len(ai_gaps)} AI gaps")
print(f"   ✅ Found {len(ai_contradictions)} AI contradictions")

# Create Streamlit-compatible structure
print()
print("4. Creating Streamlit-compatible structure...")
streamlit_data = {
    # Core analysis results
    'task1_structured_rules': structured_rules,
    'task2_gaps': ai_gaps,
    'task2_contradictions': ai_contradictions,
    
    # Context analysis
    'task3_context_analysis': {
        'total_services': our_data.get('total_policy_services', 0),
        'total_procedures': our_data.get('total_annex_procedures', 0),
        'coverage_gaps': our_data.get('total_coverage_gaps', 0)
    },
    
    # Dashboard data
    'task4_dashboard': {
        'metrics_overview': {
            'total_rules': len(structured_rules),
            'total_gaps': len(ai_gaps),
            'total_contradictions': len(ai_contradictions)
        }
    },
    
    # Extraction results
    'extraction_results': our_data.get('policy_results', {}),
    
    # Metadata
    'analysis_metadata': {
        'analysis_timestamp': our_data.get('analysis_metadata', {}).get('timestamp', 'Unknown'),
        'total_ai_gaps': our_data.get('total_ai_gaps', len(ai_gaps)),
        'total_ai_contradictions': our_data.get('total_ai_contradictions', len(ai_contradictions))
    }
}

print(f"   ✅ Created structure with:")
print(f"      - Structured rules: {len(streamlit_data['task1_structured_rules'])}")
print(f"      - Gaps: {len(streamlit_data['task2_gaps'])}")
print(f"      - Contradictions: {len(streamlit_data['task2_contradictions'])}")

# Save Streamlit-compatible file
print()
print("5. Saving Streamlit-compatible file...")
with open(output_file, 'w') as f:
    json.dump(streamlit_data, f, indent=2)

print(f"   ✅ Saved to: {output_file}")

# Verify the structure
print()
print("6. Verification...")
with open(output_file, 'r') as f:
    verify_data = json.load(f)

required_keys = ['task1_structured_rules', 'task2_gaps', 'task2_contradictions']
missing_keys = [key for key in required_keys if key not in verify_data]

if not missing_keys:
    print("   ✅ All required keys present")
    print("   ✅ Streamlit should now work with this data!")
else:
    print(f"   ❌ Missing keys: {missing_keys}")

# Test data quality
if len(streamlit_data['task1_structured_rules']) > 0:
    sample = streamlit_data['task1_structured_rules'][0]
    sample_keys = list(sample.keys()) if isinstance(sample, dict) else ['Not a dict']
    print(f"   Sample rule keys: {sample_keys[:5]}...")
    
    # Check for clean text
    if isinstance(sample, dict):
        for key in ['scope_item', 'scope', 'text']:
            if key in sample:
                text_sample = str(sample[key])
                if "Health education and wellness" in text_sample:
                    print("   ✅ Clean text confirmed in structured rules")
                    break

print()
print("=== STREAMLIT DATA FIX COMPLETE ===")