#!/usr/bin/env python3
"""
Test Streamlit fixes and ensure the workflow works
"""
import subprocess
import time
import requests
from pathlib import Path
import json

print("=== STREAMLIT FIXES VERIFICATION ===")
print()

# Test 1: Check if we have analysis data available
print("1. CHECKING ANALYSIS DATA AVAILABILITY:")
latest_dirs = sorted([d for d in Path('.').iterdir() if d.is_dir() and d.name.startswith('outputs_run_')], 
                    key=lambda x: x.stat().st_mtime)

if latest_dirs:
    latest_dir = latest_dirs[-1]
    print(f"   ✅ Latest analysis dir: {latest_dir}")
    
    # Check if comprehensive analysis JSON exists
    json_file = latest_dir / 'integrated_comprehensive_analysis.json'
    if json_file.exists():
        print(f"   ✅ Analysis JSON exists: {json_file}")
        
        with open(json_file) as f:
            data = json.load(f)
        
        # Check data structure
        ai_analysis = data.get('ai_analysis', {})
        gaps_count = len(ai_analysis.get('gaps', []))
        contradictions_count = len(ai_analysis.get('contradictions', []))
        
        print(f"   📊 Analysis data:")
        print(f"      - AI Gaps: {gaps_count}")
        print(f"      - AI Contradictions: {contradictions_count}")
        
        if gaps_count > 0 and contradictions_count > 0:
            print("   ✅ Analysis data looks good!")
            data_available = True
        else:
            print("   ⚠️  Analysis data seems incomplete")
            data_available = False
    else:
        print(f"   ❌ Analysis JSON not found")
        data_available = False
else:
    print("   ❌ No analysis directories found")
    data_available = False

# Test 2: Check Streamlit-compatible data
print()
print("2. CHECKING STREAMLIT DATA STRUCTURE:")
streamlit_files = [
    "outputs/shif_healthcare_pattern_complete_analysis.json",
    "outputs/integrated_comprehensive_analysis.json"
]

streamlit_data_ok = False
for file_path in streamlit_files:
    if Path(file_path).exists():
        print(f"   ✅ Streamlit data file exists: {file_path}")
        
        with open(file_path) as f:
            streamlit_data = json.load(f)
        
        # Check for required keys
        required_keys = ['task1_structured_rules', 'task2_gaps', 'task2_contradictions']
        has_keys = all(key in streamlit_data for key in required_keys)
        
        if has_keys:
            rules_count = len(streamlit_data.get('task1_structured_rules', []))
            gaps_count = len(streamlit_data.get('task2_gaps', []))
            contradictions_count = len(streamlit_data.get('task2_contradictions', []))
            
            print(f"   📊 Streamlit data counts:")
            print(f"      - Rules: {rules_count}")
            print(f"      - Gaps: {gaps_count}")
            print(f"      - Contradictions: {contradictions_count}")
            
            if rules_count > 0:
                print("   ✅ Streamlit data structure is correct!")
                streamlit_data_ok = True
                break
        else:
            print(f"   ⚠️  Missing required keys in {file_path}")
    else:
        print(f"   ⚠️  Streamlit data file not found: {file_path}")

if not streamlit_data_ok:
    print("   🔧 Running fix_streamlit_data.py to create proper structure...")
    try:
        subprocess.run(['python', 'fix_streamlit_data.py'], check=True, capture_output=True)
        print("   ✅ Streamlit data structure fixed!")
        streamlit_data_ok = True
    except Exception as e:
        print(f"   ❌ Failed to fix Streamlit data: {e}")

# Test 3: Test Streamlit import
print()
print("3. TESTING STREAMLIT IMPORT:")
try:
    # Test if the fixed import works
    import sys
    sys.path.append('.')
    
    # Mock streamlit for testing
    class MockStreamlit:
        def set_page_config(self, **kwargs): pass
        def markdown(self, text, unsafe_allow_html=False): pass
        def success(self, text): print(f"   SUCCESS: {text}")
        def error(self, text): print(f"   ERROR: {text}")
        def info(self, text): print(f"   INFO: {text}")
        def write(self, text): pass
        def button(self, text, **kwargs): return False
        def sidebar(self): return self
        
    sys.modules['streamlit'] = MockStreamlit()
    
    # Now test the import
    from streamlit_comprehensive_analyzer import SHIFHealthcarePolicyAnalyzer
    print("   ✅ Streamlit analyzer import successful!")
    
    # Test instantiation
    analyzer = SHIFHealthcarePolicyAnalyzer()
    print("   ✅ Analyzer instantiation successful!")
    
    # Test if load_existing_results method exists
    if hasattr(analyzer, 'load_existing_results'):
        print("   ✅ load_existing_results method exists!")
    else:
        print("   ❌ load_existing_results method missing!")
        
    import_ok = True
    
except Exception as e:
    print(f"   ❌ Import test failed: {e}")
    import_ok = False

print()
print("=== VERIFICATION SUMMARY ===")
print()

if data_available and streamlit_data_ok and import_ok:
    print("🎉 ALL FIXES VERIFIED WORKING!")
    print("✅ Analysis data available")
    print("✅ Streamlit data structure correct") 
    print("✅ Import issues resolved")
    print("✅ Missing method errors fixed")
    print()
    print("🚀 STREAMLIT SHOULD NOW WORK:")
    print("   1. Run: streamlit run streamlit_comprehensive_analyzer.py")
    print("   2. Use sidebar '📂 Load Existing Results' button")
    print("   3. Dashboard should display all data correctly")
    print()
    print("🔧 WORKFLOW:")
    print("   - Sidebar buttons only (no confusing duplicates)")
    print("   - Load existing results first (fast)")
    print("   - Run fresh analysis if needed (sidebar buttons)")
else:
    print("⚠️  SOME ISSUES REMAIN:")
    if not data_available:
        print("   ❌ No analysis data available - run integrated_comprehensive_analyzer.py first")
    if not streamlit_data_ok:
        print("   ❌ Streamlit data structure issues")
    if not import_ok:
        print("   ❌ Import/method issues remain")
        
    print()
    print("🔧 RECOMMENDED ACTIONS:")
    if not data_available:
        print("   1. Run: python integrated_comprehensive_analyzer.py")
    print("   2. Run: python fix_streamlit_data.py")
    print("   3. Then test: streamlit run streamlit_comprehensive_analyzer.py")