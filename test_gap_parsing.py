#!/usr/bin/env python3
"""
Test the enhanced gap parsing with real AI response
"""

import json
from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer

# Load the actual gap analysis from the latest run
results_file = "outputs_run_20250826_015714/integrated_comprehensive_analysis.json"

print("🧪 TESTING ENHANCED GAP PARSING")
print("="*50)

try:
    with open(results_file) as f:
        results = json.load(f)
    
    full_analysis = results['analysis_results']['full_ai_analysis']
    
    # Extract just the gaps analysis section
    if 'GAPS ANALYSIS:' in full_analysis:
        gaps_section = full_analysis.split('GAPS ANALYSIS:')[1]
        print(f"✅ Found gaps analysis section ({len(gaps_section)} characters)")
        print(f"📝 Preview: {gaps_section[:300]}...")
        
        # Test the enhanced parsing
        analyzer = IntegratedComprehensiveMedicalAnalyzer()
        extracted_gaps = analyzer._extract_ai_gaps(gaps_section)
        
        print(f"\n🎯 PARSING RESULTS:")
        print(f"📊 Extracted gaps: {len(extracted_gaps)}")
        
        if extracted_gaps:
            print(f"\n📋 Gap Details:")
            for i, gap in enumerate(extracted_gaps, 1):
                print(f"   {i}. {gap.get('gap_category', 'Unknown')}")
                print(f"      ID: {gap.get('gap_id', 'N/A')}")
                print(f"      Priority: {gap.get('clinical_priority', 'N/A')}")
                print(f"      Method: {gap.get('detection_method', 'N/A')}")
                if 'description' in gap:
                    desc = gap['description'][:100] + "..." if len(gap['description']) > 100 else gap['description']
                    print(f"      Description: {desc}")
                print()
                
            print(f"🎉 SUCCESS: Enhanced parsing extracted {len(extracted_gaps)} gaps!")
        else:
            print("❌ No gaps extracted - parsing needs further improvement")
            
    else:
        print("❌ No gaps analysis section found")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()