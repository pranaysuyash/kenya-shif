#!/usr/bin/env python3
"""
Test the integrated comprehensive analyzer
"""

import os
import sys
from pathlib import Path

def test_basic_imports():
    """Test basic imports"""
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
        
        import tabula
        print("✅ tabula imported successfully")
        
        import openai
        print("✅ openai imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_pdf_exists():
    """Test if PDF file exists"""
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    if Path(pdf_path).exists():
        print(f"✅ PDF file found: {pdf_path}")
        return True
    else:
        print(f"❌ PDF file not found: {pdf_path}")
        return False

def test_analyzer_import():
    """Test analyzer import"""
    try:
        from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
        print("✅ IntegratedComprehensiveMedicalAnalyzer imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Analyzer import error: {e}")
        return False

def test_analyzer_init():
    """Test analyzer initialization"""
    try:
        from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
        analyzer = IntegratedComprehensiveMedicalAnalyzer()
        print("✅ Analyzer initialized successfully")
        print(f"   API key available: {'Yes' if analyzer.client else 'No'}")
        return True
    except Exception as e:
        print(f"❌ Analyzer initialization error: {e}")
        return False

def test_proven_extraction():
    """Test the proven extraction functions"""
    try:
        from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
        analyzer = IntegratedComprehensiveMedicalAnalyzer()
        
        # Test proven extraction function
        pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
        if not Path(pdf_path).exists():
            print("❌ Cannot test extraction - PDF not found")
            return False
            
        print("🔄 Testing proven extraction on pages 1-18...")
        results = analyzer.extract_rules_tables_proven(pdf_path, "1-18")
        print(f"✅ Proven extraction completed: {len(results)} entries")
        
        # Check for fund and service columns
        if not results.empty:
            funds = results['fund'].value_counts()
            services = results['service'].value_counts()
            print(f"   Funds found: {len(funds)}")
            print(f"   Services found: {len(services)}")
            
            # Show sample data
            if len(funds) > 0:
                print(f"   Sample fund: {funds.index[0]}")
            if len(services) > 0:
                print(f"   Sample service: {services.index[0]}")
        
        return True
    except Exception as e:
        print(f"❌ Proven extraction test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Integrated Comprehensive Analyzer Components")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("PDF File Existence", test_pdf_exists), 
        ("Analyzer Import", test_analyzer_import),
        ("Analyzer Initialization", test_analyzer_init),
        ("Proven Extraction Functions", test_proven_extraction),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print(f"\n🎯 TEST SUMMARY:")
    print("=" * 60)
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Analyzer is ready.")
    else:
        print("⚠️ Some tests failed. Check issues above.")

if __name__ == "__main__":
    main()
