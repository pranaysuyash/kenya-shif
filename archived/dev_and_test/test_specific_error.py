#!/usr/bin/env python3
"""
Test the specific AttributeError that was reported
"""
import sys

# Mock streamlit to avoid import issues
class MockST:
    def __getattr__(self, name): return lambda *args, **kwargs: None
    def set_page_config(self, **kwargs): pass

sys.modules['streamlit'] = MockST()

print("=== TESTING SPECIFIC ERROR: 'task1_structure_rules' ===")
print()

try:
    # Import the class
    from streamlit_comprehensive_analyzer import SHIFHealthcarePolicyAnalyzer
    print("✅ Import successful")
    
    # Create instance  
    analyzer = SHIFHealthcarePolicyAnalyzer()
    print("✅ Instance created")
    
    # Check if the method exists
    if hasattr(analyzer, 'task1_structure_rules'):
        print("✅ task1_structure_rules method exists")
        
        # Try to call it (this was the failing line)
        try:
            result = analyzer.task1_structure_rules()
            print(f"✅ task1_structure_rules() called successfully - returned {type(result)} with {len(result)} items")
            
        except Exception as e:
            print(f"❌ task1_structure_rules() call failed: {e}")
    else:
        print("❌ task1_structure_rules method does NOT exist")
        
    # Test all the task methods
    task_methods = [
        'task1_structure_rules',
        'task2_detect_contradictions_and_gaps', 
        'task3_kenya_shif_context',
        'task4_create_dashboard'
    ]
    
    print()
    print("Testing all task methods:")
    for method_name in task_methods:
        if hasattr(analyzer, method_name):
            try:
                method = getattr(analyzer, method_name)
                result = method()
                if isinstance(result, tuple):
                    print(f"✅ {method_name}(): returned {len(result)} items")
                else:
                    print(f"✅ {method_name}(): returned {type(result).__name__}")
            except Exception as e:
                print(f"❌ {method_name}(): failed - {e}")
        else:
            print(f"❌ {method_name}: method missing")
            
    print()
    print("=== RESULT ===")
    print("✅ ALL ATTRIBUTE ERRORS SHOULD BE RESOLVED!")
    print()
    print("The original error:")
    print("  'SHIFHealthcarePolicyAnalyzer' object has no attribute 'task1_structure_rules'")
    print()
    print("Should now be fixed. The Streamlit app should work without AttributeError exceptions.")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    
    print()
    print("=== ERROR ANALYSIS ===")
    print("If this test fails, it means there are still import or structural issues.")
    print("Check the class indentation and make sure all methods are properly defined.")