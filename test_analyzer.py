#!/usr/bin/env python3
"""
TEST SCRIPT for the Integrated Comprehensive Medical Analyzer
This tests that all components are working correctly
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required components can be imported"""
    print("Testing imports...")
    
    try:
        import pandas as pd
        import re
        import json
        print("  ✓ Standard libraries imported")
        
        # Test tabula import (optional)
        try:
            import tabula
            print("  ✓ tabula-py available")
        except ImportError:
            print("  ! tabula-py not available (extraction will be limited)")
        
        # Test OpenAI import (optional)  
        try:
            import openai
            print("  ✓ openai library available")
        except ImportError:
            print("  ! openai library not available (AI analysis disabled)")
            
        print("✓ Import test passed")
        return True
        
    except ImportError as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_analyzer_creation():
    """Test that analyzer can be created"""
    print("Testing analyzer creation...")
    
    try:
        from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
        analyzer = IntegratedComprehensiveMedicalAnalyzer()
        print("✓ Analyzer created successfully")
        return True
        
    except Exception as e:
        print(f"✗ Analyzer creation failed: {e}")
        return False

def test_helper_functions():
    """Test that key helper functions work"""
    print("Testing helper functions...")
    
    try:
        from integrated_comprehensive_analyzer import (
            deglue_dynamic, split_bullets, primary_amount, 
            labeled_amount_pairs, build_structures
        )
        
        # Test deglue_dynamic
        result = deglue_dynamic("Healthcareservices")
        print(f"  ✓ deglue_dynamic works: {result}")
        
        # Test split_bullets
        result = split_bullets("• First item • Second item")
        print(f"  ✓ split_bullets works: {len(result)} items")
        
        # Test primary_amount  
        result = primary_amount("KES 5,000")
        print(f"  ✓ primary_amount works: {result}")
        
        print("✓ Helper functions test passed")
        return True
        
    except Exception as e:
        print(f"✗ Helper functions test failed: {e}")
        return False

def test_pdf_existence():
    """Check if default PDF exists"""
    print("Testing PDF file availability...")
    
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    if os.path.exists(pdf_path):
        print(f"✓ Default PDF found: {pdf_path}")
        return True
    else:
        print(f"! Default PDF not found: {pdf_path}")
        print("  You'll need to provide the PDF path when running the analyzer")
        return False

def run_all_tests():
    """Run all tests"""
    print("INTEGRATED ANALYZER - COMPONENT TESTS")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Analyzer Creation", test_analyzer_creation), 
        ("Helper Functions", test_helper_functions),
        ("PDF Availability", test_pdf_existence)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        results.append(test_func())
    
    print(f"\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ ALL TESTS PASSED ({passed}/{total})")
        print("The analyzer is ready to use!")
        return True
    else:
        print(f"! {passed}/{total} tests passed")
        print("Some components may not work correctly")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\nTo run the analyzer:")
        print("  python run_analyzer.py <path_to_pdf>")
        print("  or")
        print("  python run_analyzer.py  # uses default PDF if found")
    
    sys.exit(0 if success else 1)
