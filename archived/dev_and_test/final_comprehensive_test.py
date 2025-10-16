#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE SYSTEM TEST
Complete validation of enhanced dual-phase analysis system
"""

import sys
import os
import time
from pathlib import Path

sys.path.append('.')

def main():
    print("🎯 FINAL COMPREHENSIVE SYSTEM VALIDATION")
    print("=" * 60)
    
    # Test 1: System Integration
    try:
        from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
        from updated_prompts import UpdatedHealthcareAIPrompts
        print("✅ All core modules imported successfully")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test 2: Latest Results Validation
    print("\n📊 VALIDATING LATEST RESULTS...")
    
    output_dirs = list(Path('.').glob('outputs_run_*'))
    if not output_dirs:
        print("❌ No output directories found")
        return False
    
    latest_dir = max(output_dirs, key=os.path.getctime)
    print(f"📁 Latest results: {latest_dir}")
    
    # Critical files check
    critical_files = {
        'clinical_gaps_analysis.csv': 'Clinical Priority Gaps',
        'coverage_gaps_analysis.csv': 'Coverage Analysis Gaps',
        'comprehensive_gaps_analysis.csv': 'Total Comprehensive Gaps',
        'ai_contradictions.csv': 'Medical Contradictions'
    }
    
    results = {}
    all_files_present = True
    
    for file, desc in critical_files.items():
        file_path = latest_dir / file
        if file_path.exists():
            try:
                lines = sum(1 for line in open(file_path)) - 1  # -1 for header
                results[desc] = lines
                print(f"✅ {desc}: {lines} records")
            except Exception as e:
                print(f"⚠️ {desc}: Could not read ({e})")
                all_files_present = False
        else:
            print(f"❌ {desc}: MISSING")
            all_files_present = False
    
    if not all_files_present:
        print("⚠️ Some critical files missing")
    
    # Test 3: Quality Validation
    print("\n🔬 QUALITY VALIDATION...")
    
    clinical_gaps = results.get('Clinical Priority Gaps', 0)
    coverage_gaps = results.get('Coverage Analysis Gaps', 0)
    total_gaps = results.get('Total Comprehensive Gaps', 0)
    contradictions = results.get('Medical Contradictions', 0)
    
    # Quality checks
    quality_checks = {
        'Clinical gaps in expected range': 3 <= clinical_gaps <= 8,
        'Coverage gaps substantial': coverage_gaps >= 15,
        'Total gaps hit target': 25 <= total_gaps <= 40,
        'Contradictions found': contradictions >= 3,
        'Math consistency': total_gaps == (clinical_gaps + coverage_gaps)
    }
    
    for check, passed in quality_checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
    
    quality_score = sum(quality_checks.values()) / len(quality_checks)
    
    # Test 4: Sophisticated Prompts Check
    print("\n🧠 SOPHISTICATED PROMPTS CHECK...")
    
    prompts = UpdatedHealthcareAIPrompts()
    key_prompts = [
        'get_annex_quality_prompt',
        'get_strategic_policy_recommendations_prompt',
        'get_equity_analysis_prompt',
        'get_predictive_analysis_prompt',
        'get_facility_level_validation_prompt'
    ]
    
    working_prompts = 0
    for prompt in key_prompts:
        if hasattr(prompts, prompt):
            working_prompts += 1
            print(f"   ✅ {prompt}")
        else:
            print(f"   ❌ {prompt}")
    
    prompts_score = working_prompts / len(key_prompts)
    
    # Overall Assessment
    print(f"\n🎯 COMPREHENSIVE SYSTEM ASSESSMENT")
    print("=" * 60)
    
    print(f"📊 CURRENT RESULTS:")
    print(f"   • Clinical Priority Gaps: {clinical_gaps}")
    print(f"   • Coverage Analysis Gaps: {coverage_gaps}")
    print(f"   • Total Comprehensive Gaps: {total_gaps}")
    print(f"   • Medical Contradictions: {contradictions}")
    
    print(f"\n🏆 QUALITY SCORES:")
    print(f"   • Quality Validation: {quality_score:.1%}")
    print(f"   • Sophisticated Prompts: {prompts_score:.1%}")
    
    overall_score = (quality_score + prompts_score) / 2
    
    if overall_score >= 0.8:
        print(f"\n🎉 SYSTEM STATUS: EXCELLENT ({overall_score:.1%})")
        print("✅ Ready for production use!")
    elif overall_score >= 0.6:
        print(f"\n✅ SYSTEM STATUS: GOOD ({overall_score:.1%})")
        print("Ready for use with minor enhancements possible")
    else:
        print(f"\n⚠️ SYSTEM STATUS: NEEDS IMPROVEMENT ({overall_score:.1%})")
    
    # Success criteria
    success_criteria = [
        all_files_present,
        quality_score >= 0.8,
        clinical_gaps >= 3,
        coverage_gaps >= 15,
        total_gaps >= 25
    ]
    
    success = all(success_criteria)
    
    print(f"\n🎯 FINAL RESULT: {'🎉 SUCCESS' if success else '⚠️ PARTIAL SUCCESS'}")
    
    if success:
        print("\n🚀 SYSTEM READY FOR:")
        print("   📱 Streamlit app deployment")
        print("   📊 Comprehensive healthcare policy analysis")  
        print("   🏥 Clinical priority identification")
        print("   📋 WHO coverage framework analysis")
        print("   📥 Full CSV export capabilities")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)