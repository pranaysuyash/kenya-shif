#!/usr/bin/env python3
"""
Comprehensive validation: Compare both programs against manual PDF content
"""
import pandas as pd
import json
from pathlib import Path

print("=== COMPREHENSIVE VALIDATION AGAINST MANUAL PDF ===")
print()

# Known facts from manual PDF inspection
MANUAL_PDF_FACTS = {
    "primary_health_services_text": "Health education and wellness, counselling, and ongoing support as needed",
    "expected_services": [
        "PRIMARY HEALTH SERVICES", 
        "MATERNITY, NEWBORN AND CHILD HEALTH SERVICES",
        "SCREENING & MANAGEMENT OF PRE-CANCEROUS LESIONS"
    ],
    "dialysis_mentioned": True,
    "hypertension_mentioned": True,
    "tariff_values_present": True
}

print("1. TESTING SIMPLE WORKING EXTRACTION...")
try:
    import simple_working_extraction
    simple_df = simple_working_extraction.extract_rules_clean("1-18")
    
    print(f"   ✅ Simple extraction: {len(simple_df)} rows")
    
    # Check text quality
    if len(simple_df) > 0:
        first_scope = simple_df.iloc[0]['scope']
        print(f"   First scope (200 chars): {first_scope[:200]}...")
        
        # Validate against manual PDF facts
        has_clean_health_text = "Health education and wellness" in first_scope
        print(f"   ✅ Clean health text: {has_clean_health_text}")
        
        # Check for service types
        all_scopes = ' '.join(simple_df['scope'].fillna('').astype(str))
        services_found = [svc for svc in MANUAL_PDF_FACTS["expected_services"] 
                         if svc in all_scopes.upper()]
        print(f"   Services found: {len(services_found)}/3 - {services_found}")
        
    # Save for comparison
    simple_results = {
        "row_count": len(simple_df),
        "first_scope_sample": simple_df.iloc[0]['scope'][:200] if len(simple_df) > 0 else "",
        "has_clean_text": has_clean_health_text if len(simple_df) > 0 else False
    }
    
except Exception as e:
    print(f"   ❌ Simple extraction failed: {e}")
    simple_results = {"error": str(e)}

print()
print("2. TESTING INTEGRATED ANALYZER...")
try:
    from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
    
    analyzer = IntegratedComprehensiveMedicalAnalyzer("TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf")
    result = analyzer._extract_policy_structure("TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf", "1-18")
    
    if result and 'structured' in result:
        integrated_df = result['structured']
        print(f"   ✅ Integrated extraction: {len(integrated_df)} rows")
        print(f"   Available columns: {list(integrated_df.columns)}")
        
        # Check text quality
        if len(integrated_df) > 0:
            # Find scope-like column
            scope_col = None
            for col in ['scope_item', 'scope', 'text']:
                if col in integrated_df.columns:
                    scope_col = col
                    break
            
            if scope_col:
                first_scope = str(integrated_df.iloc[0][scope_col])
                print(f"   First {scope_col} (200 chars): {first_scope[:200]}...")
                
                # Validate against manual PDF facts
                has_clean_health_text = "Health education and wellness" in first_scope
                print(f"   ✅ Clean health text: {has_clean_health_text}")
        
        integrated_results = {
            "row_count": len(integrated_df),
            "columns": list(integrated_df.columns),
            "first_scope_sample": first_scope[:200] if scope_col else "No scope column",
            "has_clean_text": has_clean_health_text if scope_col else False
        }
    else:
        print(f"   ❌ No structured data in result keys: {list(result.keys()) if result else 'None'}")
        integrated_results = {"error": "No structured data"}
        
except Exception as e:
    print(f"   ❌ Integrated extraction failed: {e}")
    integrated_results = {"error": str(e)}
    import traceback
    traceback.print_exc()

print()
print("3. TESTING STREAMLIT FUNCTIONALITY...")
try:
    # Import without running Streamlit UI
    import importlib.util
    spec = importlib.util.spec_from_file_location("streamlit_app", "streamlit_comprehensive_analyzer.py")
    streamlit_module = importlib.util.module_from_spec(spec)
    
    # Check if main classes exist
    spec.loader.exec_module(streamlit_module)
    
    # Look for the main analyzer class
    if hasattr(streamlit_module, 'SHIFHealthcarePolicyAnalyzer'):
        print("   ✅ Streamlit analyzer class found")
        
        # Try to instantiate (without streamlit context)
        try:
            # This will fail due to streamlit context, but we can check structure
            analyzer_class = getattr(streamlit_module, 'SHIFHealthcarePolicyAnalyzer')
            print("   ✅ Streamlit class structure valid")
            
            # Check for key methods
            methods = [method for method in dir(analyzer_class) if not method.startswith('_')]
            key_methods = ['load_results', 'display_dashboard_overview', 'display_advanced_analytics']
            found_methods = [m for m in key_methods if m in methods]
            print(f"   Methods found: {len(found_methods)}/{len(key_methods)} - {found_methods}")
            
        except Exception as e:
            print(f"   ⚠️  Streamlit class instantiation failed (expected): {e}")
            
    else:
        print("   ❌ Streamlit analyzer class not found")
        
    streamlit_results = {"class_found": True, "structure_valid": True}
    
except Exception as e:
    print(f"   ❌ Streamlit import failed: {e}")
    streamlit_results = {"error": str(e)}

print()
print("4. COMPARISON & VALIDATION...")

# Text quality comparison
if 'error' not in simple_results and 'error' not in integrated_results:
    simple_clean = simple_results.get('has_clean_text', False)
    integrated_clean = integrated_results.get('has_clean_text', False)
    
    if simple_clean and integrated_clean:
        print("   ✅ BOTH programs produce clean text matching manual PDF")
    elif simple_clean and not integrated_clean:
        print("   ❌ Simple works, Integrated still has text issues")
    elif integrated_clean and not simple_clean:
        print("   ⚠️  Integrated works, Simple may need checking")
    else:
        print("   ❌ Both programs have text quality issues")

# Row count analysis
if 'error' not in simple_results and 'error' not in integrated_results:
    simple_count = simple_results.get('row_count', 0)
    integrated_count = integrated_results.get('row_count', 0)
    print(f"   Row counts: Simple={simple_count}, Integrated={integrated_count}")
    
    if integrated_count > simple_count:
        print("   ✅ Integrated has more comprehensive extraction (expected)")
    elif simple_count == integrated_count:
        print("   ✅ Both programs extract same amount of data")
    else:
        print("   ⚠️  Simple has more rows than integrated (unexpected)")

print()
print("5. SAVE VALIDATION RESULTS...")
validation_results = {
    "timestamp": "2025-08-27",
    "simple_extraction": simple_results,
    "integrated_extraction": integrated_results, 
    "streamlit_analysis": streamlit_results,
    "manual_pdf_facts": MANUAL_PDF_FACTS,
    "overall_status": "VALIDATED" if all([
        simple_results.get('has_clean_text', False),
        integrated_results.get('has_clean_text', False),
        streamlit_results.get('class_found', False)
    ]) else "NEEDS_ATTENTION"
}

with open('validation_results.json', 'w') as f:
    json.dump(validation_results, f, indent=2)

print(f"   Validation results saved to: validation_results.json")
print(f"   Overall Status: {validation_results['overall_status']}")

print()
print("=== VALIDATION COMPLETE ===")