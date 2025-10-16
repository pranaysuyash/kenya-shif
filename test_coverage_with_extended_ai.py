#!/usr/bin/env python3
"""
QUICK TEST: Coverage Analysis with Extended AI
Tests if coverage analysis works with run_extended_ai=True
"""

import sys
import os
import time
from pathlib import Path

sys.path.append('.')
from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer

def main():
    print("🧪 TESTING COVERAGE ANALYSIS WITH EXTENDED AI")
    print("=" * 60)
    
    analyzer = IntegratedComprehensiveMedicalAnalyzer()
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    
    print("🚀 Running analysis with run_extended_ai=True...")
    start_time = time.time()
    
    results = analyzer.analyze_complete_document(pdf_path, run_extended_ai=True)
    
    analysis_time = time.time() - start_time
    print(f"⏱️ Analysis completed in {analysis_time:.2f} seconds")
    
    # Check results
    clinical_gaps = results.get('total_ai_gaps', 0)
    coverage_gaps = results.get('total_coverage_gaps', 0)
    total_gaps = results.get('total_all_gaps', 0)
    contradictions = results.get('total_ai_contradictions', 0)
    
    print(f"\n📊 RESULTS:")
    print(f"   • Clinical Priority Gaps: {clinical_gaps}")
    print(f"   • Coverage Analysis Gaps: {coverage_gaps}") 
    print(f"   • Total Comprehensive Gaps: {total_gaps}")
    print(f"   • Contradictions: {contradictions}")
    
    # Check latest output directory
    output_dirs = list(Path('.').glob('outputs_run_*'))
    if output_dirs:
        latest_dir = max(output_dirs, key=os.path.getctime)
        print(f"\n📁 Latest output directory: {latest_dir}")
        
        # Check for coverage analysis files
        coverage_files = [
            'clinical_gaps_analysis.csv',
            'coverage_gaps_analysis.csv', 
            'comprehensive_gaps_analysis.csv'
        ]
        
        print("\n📋 Checking for coverage analysis files:")
        for file in coverage_files:
            file_path = latest_dir / file
            if file_path.exists():
                lines = sum(1 for line in open(file_path)) - 1  # -1 for header
                print(f"✅ {file} ({lines} gaps)")
            else:
                print(f"❌ {file} - MISSING")
    
    if total_gaps >= 25:
        print(f"\n🎉 SUCCESS: Found {total_gaps} total gaps (target: ~30-35)")
        return True
    else:
        print(f"\n⚠️ CONCERN: Only found {total_gaps} total gaps (target: ~30-35)")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)