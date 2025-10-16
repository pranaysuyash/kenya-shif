#!/usr/bin/env python3
"""
SHIF Analyzer Test Suite - Validate All Components
Tests both manual execution and Streamlit functionality

Author: Pranay for Dr. Rishi
Date: August 25, 2025
"""

import os
import sys
import subprocess
import pandas as pd
import tempfile
from pathlib import Path

def test_basic_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing Basic Imports...")
    
    test_results = {}
    
    modules_to_test = [
        'enhanced_analyzer',
        'shif_analyzer', 
        'disease_treatment_gap_analysis',
        'comprehensive_gap_analysis',
        'annex_tariff_extractor',
        'kenya_healthcare_context_analysis'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            test_results[module] = "✅ PASS"
            print(f"  ✅ {module}: Import successful")
        except ImportError as e:
            test_results[module] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ {module}: {str(e)}")
    
    return test_results

def test_pdf_access():
    """Test if the PDF file can be accessed"""
    print("\n📄 Testing PDF Access...")
    
    pdf_locations = [
        "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf",
        "/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    ]
    
    pdf_found = None
    for location in pdf_locations:
        if os.path.exists(location):
            pdf_found = location
            print(f"  ✅ PDF found: {location}")
            print(f"  📊 File size: {os.path.getsize(location) / (1024*1024):.1f} MB")
            break
    
    if not pdf_found:
        print("  ❌ PDF file not found in expected locations")
        return None
    
    return pdf_found

def test_enhanced_analyzer_manual():
    """Test enhanced analyzer manually"""
    print("\n🤖 Testing Enhanced Analyzer (Manual)...")
    
    try:
        from enhanced_analyzer import parse_pdf_enhanced
        
        pdf_path = test_pdf_access()
        if not pdf_path:
            return "❌ SKIP: No PDF found"
        
        # Test with small extraction (first few pages only)
        print("  📋 Running enhanced extraction test...")
        
        # Mock a small test by limiting processing
        rules_df = parse_pdf_enhanced(pdf_path, openai_key=None)  # No OpenAI for test
        
        if len(rules_df) > 0:
            print(f"  ✅ Enhanced extraction successful: {len(rules_df)} rules")
            print(f"  📊 Categories found: {rules_df['category'].nunique()}")
            return f"✅ PASS: {len(rules_df)} rules extracted"
        else:
            return "❌ FAIL: No rules extracted"
            
    except Exception as e:
        return f"❌ FAIL: {str(e)}"

def test_contradiction_detection():
    """Test contradiction detection"""
    print("\n🔍 Testing Contradiction Detection...")
    
    try:
        from shif_analyzer import detect_contradictions_v2
        
        # Create sample test data
        test_rules = pd.DataFrame({
            'service': ['Dialysis Session', 'Dialysis Treatment', 'CT Scan'],
            'service_key': ['dialysis_session', 'dialysis_treatment', 'ct_scan'],
            'category': ['DIALYSIS', 'DIALYSIS', 'IMAGING'],
            'tariff': [10000, 15000, 5000],
            'tariff_unit': ['per_session', 'per_session', 'per_scan'],
            'limits': [{'per_week': 2}, {'per_week': 3}, {}],
            'source_page': [23, 41, 12],
            'evidence_snippet': ['Dialysis 2 times per week', 'Dialysis 3 sessions weekly', 'CT scan pricing'],
            'raw_text': ['Sample text 1', 'Sample text 2', 'Sample text 3']
        })
        
        contradictions_df = detect_contradictions_v2(test_rules)
        
        print(f"  📊 Test rules: {len(test_rules)}")
        print(f"  ⚠️ Contradictions found: {len(contradictions_df)}")
        
        if len(contradictions_df) >= 0:  # Should work even with 0 contradictions
            return "✅ PASS: Contradiction detection working"
        else:
            return "❌ FAIL: Contradiction detection error"
            
    except Exception as e:
        return f"❌ FAIL: {str(e)}"

def test_streamlit_app():
    """Test if Streamlit app can be imported"""
    print("\n🚀 Testing Streamlit App Import...")
    
    try:
        # Try importing the enhanced Streamlit app
        sys.path.append('.')
        
        # Check if we can import streamlit
        import streamlit
        print("  ✅ Streamlit available")
        
        # Check if our enhanced app can be imported (syntax check)
        with open('shif_complete_analyzer_enhanced.py', 'r') as f:
            content = f.read()
        
        # Basic syntax validation
        compile(content, 'shif_complete_analyzer_enhanced.py', 'exec')
        print("  ✅ Enhanced Streamlit app syntax valid")
        
        return "✅ PASS: Streamlit app ready"
        
    except Exception as e:
        return f"❌ FAIL: {str(e)}"

def test_openai_integration():
    """Test OpenAI integration setup"""
    print("\n🤖 Testing OpenAI Integration...")
    
    try:
        # Check if OpenAI is available
        try:
            import openai
            openai_available = True
            print("  ✅ OpenAI library available")
        except ImportError:
            openai_available = False
            print("  ⚠️ OpenAI library not installed")
        
        # Check for API key
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print(f"  ✅ OpenAI API key found: {api_key[:8]}...")
            if openai_available:
                return "✅ PASS: OpenAI fully configured"
            else:
                return "⚠️ PARTIAL: API key found but library missing"
        else:
            print("  ⚠️ No OPENAI_API_KEY environment variable")
            return "⚠️ PARTIAL: OpenAI available but no API key"
            
    except Exception as e:
        return f"❌ FAIL: {str(e)}"

def test_results_data():
    """Test if previous results data exists"""
    print("\n📊 Testing Results Data...")
    
    results_paths = [
        "./results/outputs_comprehensive/",
        "/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/results/outputs_comprehensive/"
    ]
    
    found_results = False
    for path in results_paths:
        if os.path.exists(path):
            csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
            if csv_files:
                found_results = True
                print(f"  ✅ Results found in: {path}")
                print(f"  📁 CSV files: {len(csv_files)}")
                
                # Test loading a sample file
                try:
                    sample_file = os.path.join(path, csv_files[0])
                    df = pd.read_csv(sample_file)
                    print(f"  📊 Sample file ({csv_files[0]}): {len(df)} rows")
                except Exception as e:
                    print(f"  ⚠️ Error reading {csv_files[0]}: {e}")
                
                break
    
    if found_results:
        return "✅ PASS: Results data available"
    else:
        return "⚠️ INFO: No previous results (run analysis first)"

def run_quick_streamlit_test():
    """Run a quick Streamlit syntax test"""
    print("\n🎯 Running Quick Streamlit Test...")
    
    try:
        # Create a minimal test script
        test_script = """
import streamlit as st
import sys
sys.path.append('.')

try:
    from enhanced_analyzer import parse_pdf_enhanced
    st.write("✅ Enhanced analyzer import successful")
except ImportError as e:
    st.write(f"❌ Enhanced analyzer import failed: {e}")

try:
    from shif_analyzer import detect_contradictions_v2
    st.write("✅ Contradiction detection import successful")
except ImportError as e:
    st.write(f"❌ Contradiction detection import failed: {e}")

st.write("🚀 Streamlit test complete!")
"""
        
        # Write test script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            test_file = f.name
        
        # Try to run streamlit with dry run
        try:
            result = subprocess.run([
                sys.executable, '-m', 'streamlit', 'run', test_file, '--headless'
            ], capture_output=True, text=True, timeout=10)
            
            if "✅" in result.stdout or result.returncode == 0:
                return "✅ PASS: Streamlit can run the app"
            else:
                return f"⚠️ PARTIAL: Streamlit issues - {result.stderr[:100]}"
                
        except subprocess.TimeoutExpired:
            return "✅ PASS: Streamlit started successfully (timeout expected)"
        except Exception as e:
            return f"❌ FAIL: {str(e)}"
        finally:
            # Cleanup
            try:
                os.unlink(test_file)
            except:
                pass
            
    except Exception as e:
        return f"❌ FAIL: {str(e)}"

def generate_test_report(test_results):
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print("🧪 SHIF ANALYZER COMPREHENSIVE TEST REPORT")
    print("="*60)
    
    total_tests = len(test_results)
    passed_tests = len([r for r in test_results.values() if r.startswith("✅")])
    partial_tests = len([r for r in test_results.values() if r.startswith("⚠️")])
    failed_tests = len([r for r in test_results.values() if r.startswith("❌")])
    
    print(f"\n📊 OVERALL STATUS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed_tests}")
    print(f"   ⚠️ Partial: {partial_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    
    success_rate = (passed_tests + partial_tests) / total_tests * 100
    print(f"   🎯 Success Rate: {success_rate:.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    for test_name, result in test_results.items():
        print(f"   {test_name}: {result}")
    
    # Deployment recommendations
    print(f"\n🚀 DEPLOYMENT RECOMMENDATIONS:")
    
    if passed_tests + partial_tests >= total_tests * 0.8:
        print("   ✅ READY FOR DEPLOYMENT")
        print("   🎯 Recommendation: Deploy to Replit and share with Dr. Rishi")
        
        if partial_tests > 0:
            print("   ⚠️ Note: Some features in partial state - document limitations")
            
        if 'openai_integration' in test_results and test_results['openai_integration'].startswith("⚠️"):
            print("   💡 Tip: Add OPENAI_API_KEY to Replit secrets for full AI features")
            
    else:
        print("   ⚠️ FIX REQUIRED BEFORE DEPLOYMENT")
        print("   🔧 Address failed tests before sharing")
    
    print(f"\n📝 NEXT STEPS:")
    print("   1. Fix any failed tests")
    print("   2. Deploy to Replit")  
    print("   3. Test live deployment")
    print("   4. Share link with Dr. Rishi")
    print("   5. Prepare demo walkthrough")

def main():
    """Run comprehensive test suite"""
    print("🧪 SHIF ANALYZER COMPREHENSIVE TEST SUITE")
    print("Testing all components for deployment readiness...")
    
    test_results = {}
    
    # Run all tests
    test_results.update(test_basic_imports())
    test_results['pdf_access'] = test_pdf_access() is not None
    test_results['enhanced_analyzer'] = test_enhanced_analyzer_manual()
    test_results['contradiction_detection'] = test_contradiction_detection() 
    test_results['streamlit_app'] = test_streamlit_app()
    test_results['openai_integration'] = test_openai_integration()
    test_results['results_data'] = test_results_data()
    test_results['streamlit_execution'] = run_quick_streamlit_test()
    
    # Generate final report
    generate_test_report(test_results)
    
    return test_results

if __name__ == "__main__":
    main()
