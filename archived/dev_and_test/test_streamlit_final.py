#!/usr/bin/env python3
"""
Final test of Streamlit dashboard with clean data
"""
import sys
import pandas as pd
from pathlib import Path

print("=== Final Streamlit Dashboard Test ===")
print()

try:
    # Import streamlit components
    from streamlit_comprehensive_analyzer import SHIFHealthcarePolicyAnalyzer
    
    print("1. Creating SHIFHealthcarePolicyAnalyzer instance...")
    app = SHIFHealthcarePolicyAnalyzer()
    
    print("2. Loading results...")
    app.load_existing_results()
    
    print("3. Checking loaded data structure...")
    if hasattr(app, 'results') and app.results:
        print(f"   ✅ Results loaded with keys: {list(app.results.keys())}")
        
        # Check key metrics
        if 'structured_rules' in app.results:
            rules_count = len(app.results['structured_rules'])
            print(f"   ✅ Structured rules: {rules_count} entries")
            
            # Check text quality in first few entries
            if rules_count > 0:
                first_rule = app.results['structured_rules'][0]
                scope_text = first_rule.get('scope_item', 'NO SCOPE')
                print(f"   Text quality sample: '{scope_text[:150]}...'")
                
                # Check for clean text indicators
                if "Health education and wellness" in str(scope_text):
                    print("   ✅ Clean text confirmed: Contains 'Health education and wellness'")
                else:
                    print("   ⚠️  Text quality check: No 'Health education and wellness' found")
        
        if 'gaps' in app.results:
            gaps_count = len(app.results.get('gaps', []))
            print(f"   ✅ Policy gaps: {gaps_count} found")
        
        if 'contradictions' in app.results:
            contradictions_count = len(app.results.get('contradictions', []))
            print(f"   ✅ Contradictions: {contradictions_count} found")
            
        print("   ✅ Streamlit app successfully loaded and validated!")
        
    else:
        print("   ❌ No results loaded")
        
except Exception as e:
    print(f"   ❌ Streamlit test failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("=== Test Complete ===")

# Also test if we can import and run the integrated analyzer for consistency
print()
print("=== Quick Integration Test ===")

try:
    from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
    
    # Quick test without full run
    analyzer = IntegratedComprehensiveMedicalAnalyzer("TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf")
    print("✅ Integrated analyzer import successful")
    
    # Test simple deglue function directly
    from integrated_comprehensive_analyzer import simple_deglue_fixed
    
    test_broken_text = "Health educa tion and well ness, counsel ling, and ongoing suppo rtas needed."
    cleaned_text = simple_deglue_fixed(test_broken_text)
    
    print(f"Text processing test:")
    print(f"  Input:  '{test_broken_text}'")
    print(f"  Output: '{cleaned_text}'")
    
    if "Health education and wellness" in cleaned_text and "support as" in cleaned_text:
        print("✅ Text processing function working correctly!")
    else:
        print("❌ Text processing still has issues")
    
except Exception as e:
    print(f"❌ Integration test failed: {e}")

print()
print("=== All Tests Complete ===")