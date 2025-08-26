#!/usr/bin/env python3
"""
CREATE CURRENT BASELINE
Extract current excellent results and create validation baseline
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from validation_framework_agent import ValidationFrameworkAgent

def extract_current_excellent_results():
    """Extract current excellent results from CSV files"""
    
    # Find latest results
    contradictions_path = "outputs/ai_contradictions.csv"
    gaps_path = None
    
    # Look for latest gaps file
    for run_folder in sorted(Path(".").glob("outputs_run_*"), reverse=True):
        gaps_file = run_folder / "ai_gaps.csv"
        if gaps_file.exists():
            gaps_path = str(gaps_file)
            break
    
    if not gaps_path:
        print("No gaps file found, using empty gaps")
        clinical_gaps = []
    else:
        print(f"Loading gaps from: {gaps_path}")
        gaps_df = pd.read_csv(gaps_path)
        clinical_gaps = gaps_df.to_dict('records')
    
    print(f"Loading contradictions from: {contradictions_path}")
    contradictions_df = pd.read_csv(contradictions_path)
    clinical_contradictions = contradictions_df.to_dict('records')
    
    # Create formatted results
    current_results = {
        'clinical_gaps': clinical_gaps,
        'clinical_contradictions': clinical_contradictions,
        'analysis_metadata': {
            'personas': ['Dr. Grace Kiprotich', 'Dr. Amina Hassan'],
            'kenya_context': {
                'population': '56.4 million',
                'counties': 47,
                'facility_levels': '6-tier system'
            },
            'extraction_timestamp': datetime.now().isoformat(),
            'source_files': {
                'contradictions': contradictions_path,
                'gaps': gaps_path
            }
        }
    }
    
    print(f"Extracted {len(clinical_gaps)} gaps and {len(clinical_contradictions)} contradictions")
    return current_results

def main():
    """Create baseline from current excellent results"""
    
    # Extract current results
    current_results = extract_current_excellent_results()
    
    # Create validation framework
    validator = ValidationFrameworkAgent("current_system_baseline.json")
    
    # Create baseline
    baseline = validator.create_baseline(current_results)
    
    print(f"\n✅ BASELINE CREATED SUCCESSFULLY")
    print(f"Clinical Gaps: {len(baseline.clinical_gaps)}")
    print(f"Clinical Contradictions: {len(baseline.clinical_contradictions)}")
    print(f"Clinical Personas: {', '.join(baseline.clinical_personas)}")
    print(f"Kenya Context Elements: {len(baseline.kenya_context_elements)}")
    print(f"Baseline saved to: current_system_baseline.json")
    
    # Run validation against current system
    print(f"\n🔍 VALIDATING CURRENT SYSTEM...")
    passed, validation_results = validator.run_validation(current_results)
    
    overall_score = validation_results['summary']['overall_score']
    tests_passed = validation_results['summary']['tests_passed']
    tests_total = validation_results['summary']['tests_total']
    
    print(f"Validation Score: {overall_score:.3f}")
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    
    if passed:
        print("✅ CURRENT SYSTEM VALIDATION: PASSED")
    else:
        print("⚠️ CURRENT SYSTEM VALIDATION: SOME TESTS FAILED")
        for test_name in validation_results['summary']['failed_tests']:
            result = validation_results['test_results'][test_name]
            print(f"  ❌ {test_name}: {result['message']}")
    
    # Generate report
    report_content = validator.generate_validation_report(validation_results, "current_system_validation_report.md")
    print(f"\n📊 VALIDATION REPORT: current_system_validation_report.md")
    
    return passed

if __name__ == "__main__":
    success = main()
    print(f"\n{'='*60}")
    if success:
        print("🎉 CURRENT SYSTEM IS EXCELLENT - READY FOR COVERAGE INTEGRATION")
    else:
        print("⚠️ REVIEW CURRENT SYSTEM BEFORE PROCEEDING WITH INTEGRATION")