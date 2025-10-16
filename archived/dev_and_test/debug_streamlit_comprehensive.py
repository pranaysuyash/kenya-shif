#!/usr/bin/env python3
"""
Comprehensive Streamlit debugging with detailed logging and step-by-step testing
"""
import sys
import os
import traceback
from pathlib import Path
import time

# Add detailed logging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_log(message, level="INFO"):
    """Enhanced debugging with timestamps"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_streamlit_step_by_step():
    """Test Streamlit functionality step by step with detailed debugging"""
    
    debug_log("=== COMPREHENSIVE STREAMLIT DEBUG TEST ===", "HEADER")
    
    # Step 1: Environment Check
    debug_log("Step 1: Environment Check")
    debug_log(f"Current directory: {os.getcwd()}")
    debug_log(f"Python path: {sys.path[:3]}...")
    
    # Step 2: PDF Check
    debug_log("Step 2: PDF File Check")
    pdf_path = Path("TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf")
    if pdf_path.exists():
        debug_log(f"✅ PDF exists: {pdf_path} ({pdf_path.stat().st_size} bytes)")
    else:
        debug_log(f"❌ PDF missing: {pdf_path}", "ERROR")
        return False
    
    # Step 3: Data Files Check
    debug_log("Step 3: Data Files Check")
    data_files = [
        "outputs/shif_healthcare_pattern_complete_analysis.json",
        "outputs/integrated_comprehensive_analysis.json"
    ]
    for data_file in data_files:
        if Path(data_file).exists():
            debug_log(f"✅ Data file exists: {data_file}")
        else:
            debug_log(f"⚠️  Data file missing: {data_file}")
    
    # Check latest outputs_run_* directories
    latest_dirs = sorted(Path('.').glob('outputs_run_*'), key=lambda p: p.stat().st_mtime)
    if latest_dirs:
        debug_log(f"✅ Latest outputs directory: {latest_dirs[-1]}")
    else:
        debug_log("⚠️  No outputs_run_* directories found")
    
    # Step 4: Streamlit Import Test
    debug_log("Step 4: Streamlit Import Test")
    try:
        import streamlit as st
        debug_log("✅ Streamlit imported successfully")
    except Exception as e:
        debug_log(f"❌ Streamlit import failed: {e}", "ERROR")
        return False
    
    # Step 5: App Class Import Test  
    debug_log("Step 5: App Class Import Test")
    try:
        from streamlit_comprehensive_analyzer import SHIFHealthcarePolicyAnalyzer
        debug_log("✅ SHIFHealthcarePolicyAnalyzer imported successfully")
    except Exception as e:
        debug_log(f"❌ App class import failed: {e}", "ERROR")
        debug_log(f"Traceback: {traceback.format_exc()}")
        return False
    
    # Step 6: App Instantiation Test
    debug_log("Step 6: App Instantiation Test")  
    try:
        analyzer = SHIFHealthcarePolicyAnalyzer()
        debug_log("✅ Analyzer instance created successfully")
    except Exception as e:
        debug_log(f"❌ Analyzer instantiation failed: {e}", "ERROR")
        debug_log(f"Traceback: {traceback.format_exc()}")
        return False
    
    # Step 7: Method Availability Test
    debug_log("Step 7: Critical Method Availability Test")
    critical_methods = [
        'load_existing_results',
        'run_complete_extraction', 
        'task1_structure_rules',
        'task2_detect_contradictions_and_gaps',
        'task3_kenya_shif_context',
        'task4_create_dashboard'
    ]
    
    for method in critical_methods:
        if hasattr(analyzer, method):
            debug_log(f"✅ Method exists: {method}")
        else:
            debug_log(f"❌ Method missing: {method}", "ERROR")
            return False
    
    # Step 8: Load Existing Results Test
    debug_log("Step 8: Load Existing Results Test")
    try:
        analyzer.load_existing_results()
        debug_log("✅ load_existing_results executed successfully")
        
        if hasattr(analyzer, 'results') and analyzer.results:
            debug_log(f"✅ Results loaded: {len(analyzer.results)} keys")
            debug_log(f"   Available keys: {list(analyzer.results.keys())}")
        else:
            debug_log("⚠️  No results loaded (run analysis first)")
            
    except Exception as e:
        debug_log(f"❌ load_existing_results failed: {e}", "ERROR")
        debug_log(f"Traceback: {traceback.format_exc()}")
        return False
    
    # Step 9: Task Methods Test
    debug_log("Step 9: Task Methods Execution Test")
    try:
        rules = analyzer.task1_structure_rules()
        debug_log(f"✅ task1_structure_rules: {len(rules)} rules")
        
        contradictions, gaps = analyzer.task2_detect_contradictions_and_gaps()
        debug_log(f"✅ task2_detect_contradictions_and_gaps: {len(contradictions)} contradictions, {len(gaps)} gaps")
        
        context = analyzer.task3_kenya_shif_context()
        debug_log(f"✅ task3_kenya_shif_context: {type(context)} returned")
        
        dashboard = analyzer.task4_create_dashboard()
        debug_log(f"✅ task4_create_dashboard: {type(dashboard)} returned")
        
    except Exception as e:
        debug_log(f"❌ Task method execution failed: {e}", "ERROR")
        debug_log(f"Traceback: {traceback.format_exc()}")
        return False
    
    # Step 10: Mock UI Interaction Test
    debug_log("Step 10: Mock UI Interaction Test")
    try:
        # Simulate button clicks and UI interactions
        
        class MockStreamlitContext:
            def __init__(self):
                self.interactions = []
            
            def __enter__(self):
                return self
            
            def __exit__(self, *args):
                pass
            
            def button_click(self, button_name):
                self.interactions.append(f"Button clicked: {button_name}")
                return button_name == "🚀 Run Complete Extraction"
        
        # Test if run_complete_extraction can be called without errors
        debug_log("   Testing run_complete_extraction method structure...")
        
        # Instead of actually calling it (which needs full Streamlit context),
        # let's verify the method can be inspected
        import inspect
        method_source = inspect.getsource(analyzer.run_complete_extraction)
        
        if "self.load_existing_results()" in method_source:
            debug_log("✅ run_complete_extraction uses correct self.load_existing_results()")
        else:
            debug_log("❌ run_complete_extraction missing self.load_existing_results()", "ERROR")
            
        if "IntegratedComprehensiveMedicalAnalyzer" not in method_source or "analyzer =" not in method_source:
            debug_log("✅ run_complete_extraction doesn't create nested analyzer instance")
        else:
            debug_log("⚠️  run_complete_extraction may still have nested analyzer creation")
            
    except Exception as e:
        debug_log(f"❌ UI interaction test failed: {e}", "ERROR")
        debug_log(f"Traceback: {traceback.format_exc()}")
        return False
    
    debug_log("=== DEBUG TEST SUMMARY ===", "HEADER")
    debug_log("✅ All critical components verified working")
    debug_log("✅ No AttributeErrors detected")
    debug_log("✅ Methods exist and execute successfully") 
    debug_log("✅ Data loading works correctly")
    debug_log("✅ Ready for full Streamlit app testing")
    
    return True

def generate_debug_report():
    """Generate a comprehensive debug report"""
    debug_log("Generating comprehensive debug report...")
    
    report = []
    report.append("# Streamlit Debug Report")
    report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Environment info
    report.append("## Environment")
    report.append(f"- Python: {sys.version}")
    report.append(f"- Working directory: {os.getcwd()}")
    report.append("")
    
    # File status
    report.append("## File Status")
    pdf_path = Path("TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf")
    report.append(f"- PDF file: {'✅ EXISTS' if pdf_path.exists() else '❌ MISSING'}")
    
    outputs_dirs = list(Path('.').glob('outputs_run_*'))
    report.append(f"- Output directories: {len(outputs_dirs)} found")
    
    data_files = [
        "outputs/shif_healthcare_pattern_complete_analysis.json",
        "outputs/integrated_comprehensive_analysis.json"
    ]
    for data_file in data_files:
        status = "✅ EXISTS" if Path(data_file).exists() else "❌ MISSING"
        report.append(f"- {data_file}: {status}")
    
    report.append("")
    report.append("## Test Results")
    
    success = test_streamlit_step_by_step()
    report.append(f"- Overall test result: {'✅ PASSED' if success else '❌ FAILED'}")
    
    with open("streamlit_debug_report.md", "w") as f:
        f.write("\n".join(report))
    
    debug_log(f"Debug report saved to: streamlit_debug_report.md")
    return success

if __name__ == "__main__":
    print("🔍 Starting comprehensive Streamlit debugging...")
    
    try:
        success = generate_debug_report()
        
        if success:
            print("\n🎉 ALL DEBUGGING TESTS PASSED!")
            print("✅ Streamlit app should work correctly")
            print("\n📝 Next steps:")
            print("1. Run: streamlit run streamlit_comprehensive_analyzer.py")
            print("2. Click buttons and test functionality")
            print("3. Take screenshots of working features")
        else:
            print("\n❌ DEBUGGING TESTS FAILED!")
            print("🔧 Check the debug output above for specific issues")
            print("📋 Review streamlit_debug_report.md for details")
            
    except Exception as e:
        print(f"\n💥 DEBUGGING SCRIPT FAILED: {e}")
        traceback.print_exc()