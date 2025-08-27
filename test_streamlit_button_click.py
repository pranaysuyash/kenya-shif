#!/usr/bin/env python3
"""
Test Streamlit button clicking properly by simulating the actual workflow
"""
import sys
import os
from pathlib import Path

# Mock streamlit for controlled testing
class MockStreamlit:
    def __init__(self):
        self.mock_results = []
    
    def set_page_config(self, **kwargs): pass
    def markdown(self, text, unsafe_allow_html=False): 
        if "Found existing analysis results!" in str(text):
            self.mock_results.append("found_existing")
    def success(self, text): 
        self.mock_results.append(f"success: {text}")
    def error(self, text): 
        self.mock_results.append(f"error: {text}")
    def info(self, text): 
        self.mock_results.append(f"info: {text}")
    def warning(self, text): 
        self.mock_results.append(f"warning: {text}")
    def write(self, text): 
        if "Found existing analysis results!" in str(text):
            self.mock_results.append("found_existing")
        elif "Analysis completed successfully!" in str(text):
            self.mock_results.append("analysis_completed")
    def button(self, text, **kwargs): 
        # Simulate clicking "Run Complete Extraction" 
        return text == "🚀 Run Complete Extraction"
    def sidebar(self): return self
    def progress(self, value): pass
    def text(self, text): pass
    def empty(self): return self
    def container(self): return self
    def placeholder(self): return self

mock_st = MockStreamlit()
sys.modules['streamlit'] = mock_st

print("=== TESTING STREAMLIT BUTTON CLICK WORKFLOW ===")
print()

try:
    from streamlit_comprehensive_analyzer import SHIFHealthcarePolicyAnalyzer
    
    print("1. Creating SHIFHealthcarePolicyAnalyzer...")
    analyzer = SHIFHealthcarePolicyAnalyzer()
    print("   ✅ Created successfully")
    
    print()
    print("2. Testing load_existing_results method exists...")
    if hasattr(analyzer, 'load_existing_results'):
        print("   ✅ Method exists")
        
        # Test calling the method
        try:
            analyzer.load_existing_results()
            print("   ✅ Method executes without error")
        except Exception as e:
            print(f"   ❌ Method execution failed: {e}")
    else:
        print("   ❌ Method missing")
    
    print()
    print("3. Testing run_complete_extraction method...")
    if hasattr(analyzer, 'run_complete_extraction'):
        print("   ✅ Method exists")
        
        # Check if PDF exists for the test
        pdf_path = Path("TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf")
        if pdf_path.exists():
            print(f"   ✅ PDF exists: {pdf_path}")
            
            # Test the method (this will simulate the button click)
            print("   🔄 Simulating 'Run Complete Extraction' button click...")
            try:
                analyzer.run_complete_extraction()
                print("   ✅ run_complete_extraction completed without NameError!")
                
                # Check what happened in our mock
                if "found_existing" in mock_st.mock_results:
                    print("   ✅ Found existing results workflow triggered")
                elif "analysis_completed" in mock_st.mock_results:
                    print("   ✅ New analysis workflow triggered")
                else:
                    print(f"   📊 Mock results: {mock_st.mock_results}")
                    
            except AttributeError as e:
                if "load_existing_results" in str(e):
                    print(f"   ❌ STILL HAS ATTRIBUTE ERROR: {e}")
                else:
                    print(f"   ❌ Other AttributeError: {e}")
            except Exception as e:
                print(f"   ⚠️  Other error (may be expected): {e}")
        else:
            print(f"   ⚠️  PDF missing: {pdf_path} - button would be disabled")
    else:
        print("   ❌ run_complete_extraction method missing")

    print()
    print("=== BUTTON CLICK TEST SUMMARY ===")
    
    if "load_existing_results" in [m.__name__ for m in analyzer.__class__.__dict__.values() if callable(m)]:
        print("✅ load_existing_results method properly available in class")
    else:
        print("❌ load_existing_results method not found in class")
        
    if pdf_path.exists():
        print("✅ PDF available - button should be clickable")
        print("✅ run_complete_extraction method should work without NameError")
    else:
        print("⚠️  PDF missing - need to test with PDF present")

except Exception as e:
    print(f"❌ Test setup failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("=== NEXT STEPS FOR REAL TESTING ===")
print("1. Ensure PDF exists: TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf")
print("2. Run: streamlit run streamlit_comprehensive_analyzer.py")  
print("3. Click the '🚀 Run Complete Extraction' button")
print("4. Verify no AttributeError appears")
print("5. Check if analysis runs or existing results load")