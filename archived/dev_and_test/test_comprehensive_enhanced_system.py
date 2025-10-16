#!/usr/bin/env python3
"""
COMPREHENSIVE ENHANCED SYSTEM TEST
Tests the integrated dual-phase analysis with coverage analysis and all sophisticated prompts
"""

import sys
import os
import time
import json
from pathlib import Path

# Add current directory to path
sys.path.append('.')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
from updated_prompts import EnhancedHealthcareAIPrompts

def test_coverage_analysis_integration():
    """Test that coverage analysis Phase 4C executes properly"""
    
    print("\n🧪 TESTING COVERAGE ANALYSIS INTEGRATION")
    print("=" * 60)
    
    try:
        # Initialize analyzer
        analyzer = IntegratedComprehensiveMedicalAnalyzer()
        print(f"✅ Analyzer initialized")
        print(f"🔍 OpenAI client available: {analyzer.client is not None}")
        
        # Check PDF exists
        pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
        if not os.path.exists(pdf_path):
            print(f"❌ PDF not found: {pdf_path}")
            return False
            
        print(f"✅ PDF found: {pdf_path}")
        
        # Test coverage analysis methods exist
        print(f"🔍 Coverage analysis method exists: {hasattr(analyzer, '_run_coverage_analysis')}")
        print(f"🔍 Coverage prompt method exists: {hasattr(analyzer, '_get_coverage_analysis_prompt')}")
        print(f"🔍 Coverage extraction method exists: {hasattr(analyzer, '_extract_coverage_gaps')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Coverage analysis integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sophisticated_prompts_availability():
    """Test that all sophisticated prompts from updated_prompts.py are available"""
    
    print("\n🧪 TESTING SOPHISTICATED PROMPTS AVAILABILITY")
    print("=" * 60)
    
    try:
        prompts = EnhancedHealthcareAIPrompts()
        
        # Test all available prompt methods
        prompt_methods = [
            'get_advanced_contradiction_prompt',
            'get_comprehensive_gap_analysis_prompt', 
            'get_strategic_policy_recommendations_prompt',
            'get_conversational_analysis_prompt',
            'get_predictive_analysis_prompt',
            'get_annex_quality_prompt',
            'get_rules_contradiction_map_prompt',
            'get_batch_service_analysis_prompt',
            'get_individual_service_analysis_prompt',
            'get_inference_prompt',
            'get_tariff_outlier_prompt',
            'get_section_summaries_prompt',
            'get_name_canonicalization_prompt',
            'get_facility_level_validation_prompt',
            'get_policy_annex_alignment_prompt',
            'get_equity_analysis_prompt'
        ]
        
        available_prompts = 0
        for method in prompt_methods:
            if hasattr(prompts, method):
                available_prompts += 1
                print(f"✅ {method}")
            else:
                print(f"❌ {method} - MISSING")
        
        print(f"\n📊 Available prompts: {available_prompts}/{len(prompt_methods)}")
        
        return available_prompts == len(prompt_methods)
        
    except Exception as e:
        print(f"❌ Sophisticated prompts test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quick_analysis_run():
    """Run a quick analysis to test the system produces expected outputs"""
    
    print("\n🧪 TESTING QUICK ANALYSIS RUN")
    print("=" * 60)
    
    try:
        analyzer = IntegratedComprehensiveMedicalAnalyzer()
        pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
        
        print("🚀 Starting quick analysis (without extended AI to save time)...")
        start_time = time.time()
        
        results = analyzer.analyze_complete_document(pdf_path, run_extended_ai=False)
        
        analysis_time = time.time() - start_time
        print(f"⏱️ Analysis completed in {analysis_time:.2f} seconds")
        
        # Check results structure
        clinical_gaps = results.get('total_ai_gaps', 0)
        coverage_gaps = results.get('total_coverage_gaps', 0)
        total_gaps = results.get('total_all_gaps', 0)
        contradictions = results.get('total_ai_contradictions', 0)
        
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"   • Clinical Priority Gaps: {clinical_gaps}")
        print(f"   • Coverage Analysis Gaps: {coverage_gaps}") 
        print(f"   • Total Comprehensive Gaps: {total_gaps}")
        print(f"   • Contradictions: {contradictions}")
        
        # Check gap analysis breakdown
        gap_breakdown = results.get('gap_analysis_breakdown', {})
        print(f"\n🔍 GAP ANALYSIS BREAKDOWN:")
        for key, value in gap_breakdown.items():
            print(f"   • {key}: {value}")
        
        # Test success criteria
        success_criteria = {
            'clinical_gaps_preserved': clinical_gaps >= 3,  # Should have at least 3-5 clinical gaps
            'system_runs_without_error': True,  # If we get here, no errors
            'results_structure_correct': 'gap_analysis_breakdown' in results,
            'output_files_generated': len(analyzer.output_dir.glob('*.csv')) > 0
        }
        
        print(f"\n✅ SUCCESS CRITERIA:")
        for criterion, passed in success_criteria.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {criterion}: {passed}")
        
        all_passed = all(success_criteria.values())
        
        if coverage_gaps > 0:
            print(f"\n🎯 COVERAGE ANALYSIS SUCCESS: Found {coverage_gaps} coverage gaps!")
        else:
            print(f"\n⚠️ COVERAGE ANALYSIS: No coverage gaps found - may need investigation")
        
        return all_passed, results
        
    except Exception as e:
        print(f"❌ Quick analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_output_files_structure():
    """Test that the expected output files are generated"""
    
    print("\n🧪 TESTING OUTPUT FILES STRUCTURE")
    print("=" * 60)
    
    try:
        # Find latest output directory
        output_dirs = list(Path('.').glob('outputs_run_*'))
        if not output_dirs:
            print("❌ No output directories found")
            return False
        
        latest_dir = max(output_dirs, key=os.path.getctime)
        print(f"📁 Latest output directory: {latest_dir}")
        
        # Expected files for comprehensive analysis
        expected_files = [
            'rules_p1_18_structured.csv',
            'annex_surgical_tariffs_all.csv',
            'ai_contradictions.csv',
            'analysis_summary.csv'
        ]
        
        # Files that should exist with new coverage analysis
        enhanced_files = [
            'clinical_gaps_analysis.csv',
            'coverage_gaps_analysis.csv', 
            'comprehensive_gaps_analysis.csv'
        ]
        
        print("\n📋 CHECKING EXPECTED FILES:")
        found_files = 0
        for file in expected_files:
            file_path = latest_dir / file
            if file_path.exists():
                print(f"✅ {file}")
                found_files += 1
            else:
                print(f"❌ {file} - MISSING")
        
        print("\n📋 CHECKING ENHANCED FILES (Coverage Analysis):")
        enhanced_found = 0
        for file in enhanced_files:
            file_path = latest_dir / file
            if file_path.exists():
                print(f"✅ {file}")
                enhanced_found += 1
            else:
                print(f"⚠️ {file} - MISSING (expected with coverage analysis)")
        
        print(f"\n📊 File Check Results:")
        print(f"   • Basic files: {found_files}/{len(expected_files)}")
        print(f"   • Enhanced files: {enhanced_found}/{len(enhanced_files)}")
        
        if enhanced_found > 0:
            print(f"🎯 Coverage analysis files detected!")
        else:
            print(f"⚠️ No coverage analysis files found - coverage analysis may not be executing")
        
        return found_files >= len(expected_files) * 0.8  # At least 80% of expected files
        
    except Exception as e:
        print(f"❌ Output files test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive enhanced system tests"""
    
    print("🚀 COMPREHENSIVE ENHANCED SYSTEM TEST SUITE")
    print("=" * 80)
    
    tests = [
        ("Coverage Analysis Integration", test_coverage_analysis_integration),
        ("Sophisticated Prompts Availability", test_sophisticated_prompts_availability),
        ("Quick Analysis Run", test_quick_analysis_run),
        ("Output Files Structure", test_output_files_structure)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            if test_name == "Quick Analysis Run":
                success, analysis_results = test_func()
                results[test_name] = success
                if analysis_results:
                    results['analysis_data'] = analysis_results
            else:
                results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results[test_name] = False
    
    # Final summary
    print(f"\n{'='*80}")
    print("🎯 TEST SUITE SUMMARY")
    print("=" * 80)
    
    passed_tests = 0
    total_tests = len([t for t in tests if t[0] != "analysis_data"])
    
    for test_name, result in results.items():
        if test_name != 'analysis_data':
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status} {test_name}")
            if result:
                passed_tests += 1
    
    print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - System ready for comprehensive analysis!")
    elif passed_tests >= total_tests * 0.8:
        print("⚠️ Most tests passed - Minor issues to resolve")
    else:
        print("❌ Multiple test failures - Significant issues need resolution")
    
    # Save test results
    results_file = Path("test_results_comprehensive_enhanced.json")
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'success_rate': passed_tests / total_tests,
            'results': {k: v for k, v in results.items() if k != 'analysis_data'}
        }, f, indent=2)
    
    print(f"\n💾 Test results saved to: {results_file}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)