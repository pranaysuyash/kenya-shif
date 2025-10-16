#!/usr/bin/env python3
"""
Simple test of the specific methods that were missing
"""
print("=== TESTING SPECIFIC MISSING METHODS ===")
print()

# Test by examining the code directly
with open('streamlit_comprehensive_analyzer.py', 'r') as f:
    content = f.read()

# Check if the methods we added are present
required_methods = [
    'def task1_structure_rules(self):',
    'def task2_detect_contradictions_and_gaps(self):',
    'def task3_kenya_shif_context(self):',
    'def task4_create_dashboard(self):'
]

print("1. CHECKING METHOD DEFINITIONS IN CODE:")
for method in required_methods:
    if method in content:
        print(f"   ✅ {method.replace('def ', '').replace('(self):', '')} - FOUND")
    else:
        print(f"   ❌ {method.replace('def ', '').replace('(self):', '')} - MISSING")

# Check the specific line that was failing
print()
print("2. CHECKING SPECIFIC ERROR LOCATIONS:")

error_patterns = [
    ('task1_structure_rules()', 'structured_rules = analyzer.task1_structure_rules()'),
    ('task2_detect_contradictions_and_gaps()', 'contradictions, gaps = analyzer.task2_detect_contradictions_and_gaps()'),
    ('task3_kenya_shif_context()', 'context_analysis = analyzer.task3_kenya_shif_context()'),
    ('task4_create_dashboard()', 'dashboard = analyzer.task4_create_dashboard()')
]

for method_name, call_pattern in error_patterns:
    if call_pattern in content:
        print(f"   ✅ {method_name} call found in code")
        # Check if method definition exists
        method_def = f"def {method_name.replace('()', '(self):')}:"
        if method_def in content:
            print(f"   ✅ {method_name} method definition exists")
        else:
            print(f"   ❌ {method_name} method definition MISSING")
    else:
        print(f"   ⚠️  {method_name} call not found")

# Check PDF availability
print()
print("3. CHECKING REQUIREMENTS:")
from pathlib import Path

pdf_path = Path("TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf")
if pdf_path.exists():
    print(f"   ✅ PDF exists: {pdf_path}")
else:
    print(f"   ❌ PDF missing: {pdf_path}")

# Check if we have Streamlit data
data_files = [
    "outputs/shif_healthcare_pattern_complete_analysis.json",
    "outputs/integrated_comprehensive_analysis.json"
]

data_available = False
for file_path in data_files:
    if Path(file_path).exists():
        print(f"   ✅ Streamlit data exists: {file_path}")
        data_available = True
        break

if not data_available:
    print("   ❌ No Streamlit-compatible data files found")

print()
print("=== ANALYSIS SUMMARY ===")
print()

# Count methods in content
method_count = len([m for m in required_methods if m in content])
call_count = len([p for _, p in error_patterns if p in content])

print(f"📊 Method Definitions Found: {method_count}/4")
print(f"📊 Method Calls Found: {call_count}/4")

if method_count == 4 and call_count == 4:
    print("✅ ALL MISSING METHODS HAVE BEEN IMPLEMENTED!")
    print()
    print("🎯 WHAT THIS FIXES:")
    print("   - 'task1_structure_rules' AttributeError: RESOLVED")
    print("   - 'task2_detect_contradictions_and_gaps' AttributeError: RESOLVED") 
    print("   - 'task3_kenya_shif_context' AttributeError: RESOLVED")
    print("   - 'task4_create_dashboard' AttributeError: RESOLVED")
    print()
    print("🚀 NEXT STEPS:")
    if pdf_path.exists():
        print("   1. Run: streamlit run streamlit_comprehensive_analyzer.py")
        print("   2. Click sidebar '📂 Load Existing Results' button")
        print("   3. Try 'Run Complete Extraction' button - should now work!")
    else:
        print("   1. Ensure PDF file is in working directory")
        print("   2. Then run Streamlit and test buttons")
        
    if data_available:
        print("   ✅ Data is available for dashboard display")
    else:
        print("   4. Or run: python fix_streamlit_data.py first")
        
else:
    print("❌ SOME ISSUES REMAIN:")
    if method_count < 4:
        print(f"   - Only {method_count}/4 method definitions found")
    if call_count < 4:
        print(f"   - Only {call_count}/4 method calls found")
        
print()
print("=" * 50)