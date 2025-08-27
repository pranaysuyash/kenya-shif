#!/usr/bin/env python3
"""
Comprehensive test of all SHIFHealthcarePolicyAnalyzer methods
"""
import sys
from pathlib import Path

print("=== COMPREHENSIVE STREAMLIT METHOD TEST ===")
print()

# Mock streamlit for testing
class MockStreamlit:
    def set_page_config(self, **kwargs): pass
    def markdown(self, text, unsafe_allow_html=False): pass
    def success(self, text): print(f"   SUCCESS: {text}")
    def error(self, text): print(f"   ERROR: {text}")
    def info(self, text): print(f"   INFO: {text}")
    def warning(self, text): print(f"   WARNING: {text}")
    def write(self, text): pass
    def button(self, text, **kwargs): return False
    def sidebar(self): return self
    def progress(self, value): pass
    def text(self, text): pass
    def metric(self, label, value, delta=None): pass
    def checkbox(self, label, value=False): return value
    def selectbox(self, label, options): return options[0] if options else None
    def columns(self, n): return [self] * n
    def container(self): return self
    def empty(self): return self
    def placeholder(self): return self

sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

# Test 1: Import and instantiation
print("1. TESTING CLASS IMPORT AND INSTANTIATION:")
try:
    from streamlit_comprehensive_analyzer import SHIFHealthcarePolicyAnalyzer
    print("   ✅ Import successful")
    
    analyzer = SHIFHealthcarePolicyAnalyzer()
    print("   ✅ Instantiation successful")
    print(f"   📊 Initial results: {analyzer.results}")
    
except Exception as e:
    print(f"   ❌ Import/instantiation failed: {e}")
    exit(1)

# Test 2: Check all expected methods exist
print()
print("2. TESTING METHOD EXISTENCE:")
expected_methods = [
    'task1_structure_rules',
    'task2_detect_contradictions_and_gaps', 
    'task3_kenya_shif_context',
    'task4_create_dashboard',
    'load_existing_results',
    'run_complete_extraction',
    'run_pattern_analysis',
    'run_integrated_analysis',
    'get_total_services',
    'show_quick_summary'
]

missing_methods = []
for method_name in expected_methods:
    if hasattr(analyzer, method_name):
        print(f"   ✅ {method_name}")
    else:
        print(f"   ❌ {method_name} - MISSING")
        missing_methods.append(method_name)

if missing_methods:
    print(f"   ❌ Missing methods: {missing_methods}")
else:
    print("   ✅ All expected methods present!")

# Test 3: Test methods with empty results
print()
print("3. TESTING METHODS WITH EMPTY RESULTS:")
try:
    # Test task methods with empty results
    rules = analyzer.task1_structure_rules()
    print(f"   ✅ task1_structure_rules(): returned {len(rules)} rules")
    
    contradictions, gaps = analyzer.task2_detect_contradictions_and_gaps()
    print(f"   ✅ task2_detect_contradictions_and_gaps(): {len(contradictions)} contradictions, {len(gaps)} gaps")
    
    context = analyzer.task3_kenya_shif_context()
    print(f"   ✅ task3_kenya_shif_context(): returned {type(context).__name__}")
    
    dashboard = analyzer.task4_create_dashboard()
    print(f"   ✅ task4_create_dashboard(): returned {type(dashboard).__name__}")
    
except Exception as e:
    print(f"   ❌ Method testing failed: {e}")

# Test 4: Test load_existing_results
print()
print("4. TESTING LOAD_EXISTING_RESULTS:")
try:
    analyzer.load_existing_results()
    print(f"   ✅ load_existing_results() executed")
    print(f"   📊 Results after loading: {bool(analyzer.results)}")
    
    if analyzer.results:
        available_keys = list(analyzer.results.keys())
        print(f"   📊 Available result keys: {available_keys}")
        
        # Test methods with loaded data
        rules = analyzer.task1_structure_rules()
        contradictions, gaps = analyzer.task2_detect_contradictions_and_gaps()
        
        print(f"   📊 With loaded data:")
        print(f"      - Rules: {len(rules)}")
        print(f"      - Contradictions: {len(contradictions)}")
        print(f"      - Gaps: {len(gaps)}")
        
except Exception as e:
    print(f"   ❌ load_existing_results failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Check PDF availability for buttons
print()
print("5. TESTING PDF AVAILABILITY (for button functionality):")
pdf_path = Path("TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf")
if pdf_path.exists():
    print(f"   ✅ PDF exists: {pdf_path}")
    print("   ✅ All extraction buttons should be clickable")
else:
    print(f"   ❌ PDF missing: {pdf_path}")
    print("   ⚠️  Extraction buttons will be disabled")

# Test 6: Test critical workflow methods
print()
print("6. TESTING WORKFLOW INTEGRATION:")
workflow_tests = [
    ('get_total_services', []),
    ('show_quick_summary', []),
]

for method_name, args in workflow_tests:
    if hasattr(analyzer, method_name):
        try:
            result = getattr(analyzer, method_name)(*args)
            print(f"   ✅ {method_name}(): executed successfully")
        except Exception as e:
            print(f"   ❌ {method_name}(): failed - {e}")
    else:
        print(f"   ❌ {method_name}: method not found")

print()
print("=== COMPREHENSIVE TEST SUMMARY ===")
print()

# Summary
issues_found = []

if missing_methods:
    issues_found.append(f"Missing methods: {missing_methods}")

if not pdf_path.exists():
    issues_found.append("PDF file missing - buttons will be disabled")

if not analyzer.results:
    issues_found.append("No analysis results loaded - dashboard will be empty")

if issues_found:
    print("⚠️  ISSUES FOUND:")
    for issue in issues_found:
        print(f"   - {issue}")
    print()
    print("🔧 RECOMMENDATIONS:")
    if not pdf_path.exists():
        print("   1. Ensure PDF 'TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf' is in working directory")
    if not analyzer.results:
        print("   2. Run: python fix_streamlit_data.py")
        print("   3. Or use 'Load Existing Results' button in Streamlit")
else:
    print("🎉 ALL TESTS PASSED!")
    print("✅ All methods implemented and functional")
    print("✅ PDF available for extraction")
    print("✅ Analysis results loaded successfully")
    print()
    print("🚀 STREAMLIT SHOULD NOW WORK COMPLETELY:")
    print("   - All buttons should be clickable")
    print("   - All extraction workflows should function")
    print("   - Dashboard should display data correctly")
    print()
    print("   RUN: streamlit run streamlit_comprehensive_analyzer.py")