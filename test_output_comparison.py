#!/usr/bin/env python3
"""
Test that both programs produce identical clean output
"""
import sys
import pandas as pd
from pathlib import Path

print("=== Kenya SHIF Policy Analyzer Output Comparison ===")
print()

# Test 1: Run simple working extraction
print("1. Running simple working extraction...")
try:
    import simple_working_extraction
    simple_df = simple_working_extraction.extract_rules_clean("1-18")
    simple_count = len(simple_df)
    simple_first_scope = simple_df.iloc[0]['scope'][:100] + "..." if len(simple_df) > 0 else "NO DATA"
    print(f"   ✅ Simple extraction: {simple_count} rows")
    print(f"   First scope sample: {simple_first_scope}")
except Exception as e:
    print(f"   ❌ Simple extraction failed: {e}")
    simple_df = None
    simple_count = 0

print()

# Test 2: Run integrated analyzer extraction only 
print("2. Running integrated analyzer extraction...")
try:
    from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
    analyzer = IntegratedComprehensiveMedicalAnalyzer("TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf")
    
    # Extract rules using the pages 1-18 method
    result = analyzer._extract_policy_structure("TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf", "1-18")
    
    if result:
        print(f"   Available keys in result: {list(result.keys())}")
        
        # Look for rules data in different possible keys
        rules_data = None
        if 'structured' in result:
            rules_data = result['structured']
        elif 'structured_rules' in result:
            rules_data = result['structured_rules']
        elif 'rules' in result:
            rules_data = result['rules']
        elif 'policy_rules' in result:
            rules_data = result['policy_rules']
        elif 'raw' in result:
            rules_data = result['raw']
        
        if rules_data is not None:
            if isinstance(rules_data, pd.DataFrame):
                integrated_df = rules_data
            else:
                integrated_df = pd.DataFrame(rules_data)
            
            integrated_count = len(integrated_df)
            
            if integrated_count > 0:
                print(f"   Available columns: {list(integrated_df.columns)}")
                
                # Try different possible scope column names
                scope_col = None
                for col in ['scope', 'scope_item', 'text', 'content']:
                    if col in integrated_df.columns:
                        scope_col = col
                        break
                
                if scope_col:
                    integrated_first_scope = str(integrated_df.iloc[0][scope_col])[:100] + "..."
                else:
                    # Show first row data
                    integrated_first_scope = str(integrated_df.iloc[0].to_dict())[:100] + "..."
            else:
                integrated_first_scope = "NO DATA"
                
            print(f"   ✅ Integrated extraction: {integrated_count} rows")
            print(f"   First scope sample: {integrated_first_scope}")
        else:
            print(f"   ❌ No rules data found in result keys: {list(result.keys())}")
            integrated_df = None
            integrated_count = 0
    else:
        print(f"   ❌ Integrated extraction failed: No result returned")
        integrated_df = None
        integrated_count = 0
        
except Exception as e:
    print(f"   ❌ Integrated extraction failed: {e}")
    integrated_df = None
    integrated_count = 0

print()

# Test 3: Compare outputs
print("3. Comparing outputs...")

if simple_df is not None and integrated_df is not None:
    if simple_count == integrated_count:
        print(f"   ✅ Row count match: Both have {simple_count} rows")
        
        # Compare first few text samples
        print("   \nText quality comparison (first row scope):")
        print(f"   Simple:     '{simple_df.iloc[0]['scope'][:150]}...'")
        print(f"   Integrated: '{integrated_df.iloc[0].get('scope', 'NO SCOPE')[:150]}...'")
        
        # Basic text quality check
        simple_text = simple_df.iloc[0]['scope']
        integrated_text = integrated_df.iloc[0].get('scope', '')
        
        # Check for common quality indicators
        simple_has_wellness = "Health education and wellness" in simple_text
        integrated_has_wellness = "Health education and wellness" in integrated_text
        
        if simple_has_wellness and integrated_has_wellness:
            print("   ✅ Both contain clean 'Health education and wellness' text")
        elif simple_has_wellness and not integrated_has_wellness:
            print("   ❌ Simple has clean text, integrated still has broken text")
        elif integrated_has_wellness and not simple_has_wellness:
            print("   ✅ Integrated has clean text, simple might be different extraction")
        else:
            print("   ⚠️  Neither contains the expected text pattern")
            
    else:
        print(f"   ❌ Row count mismatch: Simple={simple_count}, Integrated={integrated_count}")
else:
    print("   ❌ Cannot compare: One or both extractions failed")

print()
print("=== Test Complete ===")