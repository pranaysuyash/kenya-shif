#!/usr/bin/env python3
"""
MAIN EXECUTION SCRIPT for Integrated Comprehensive Medical Analyzer
Run this to analyze the Kenya SHIF PDF document
"""

import sys
import os

# Add missing main execution for the integrated analyzer
if __name__ == "__main__":
    # Check for PDF argument
    if len(sys.argv) < 2:
        pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
        if not os.path.exists(pdf_path):
            print("Default PDF not found. Usage: python run_analyzer.py <path_to_pdf>")
            sys.exit(1)
    else:
        pdf_path = sys.argv[1]
    
    # Initialize analyzer
    print("INTEGRATED COMPREHENSIVE MEDICAL ANALYZER")
    print("=" * 60)
    
    # Import and create analyzer instance
    try:
        from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
        analyzer = IntegratedComprehensiveMedicalAnalyzer()
    except ImportError as e:
        print(f"Error importing analyzer: {e}")
        print("Make sure integrated_comprehensive_analyzer.py is in the same directory")
        sys.exit(1)
    
    # Run complete analysis
    try:
        results = analyzer.analyze_complete_document(pdf_path, run_extended_ai=False)
        
        print(f"\nANALYSIS SUCCESSFULLY COMPLETED")
        print(f"   Policy Services: {results.get('total_policy_services', 0)}")
        print(f"   Annex Procedures: {results.get('total_annex_procedures', 0)}")
        print(f"   AI Contradictions: {results.get('total_ai_contradictions', 0)}")
        print(f"   AI Gaps: {results.get('total_ai_gaps', 0)}")
        print(f"   Time: {results.get('analysis_metadata', {}).get('analysis_time_seconds', 0):.1f}s")
        print(f"\nResults saved to outputs/ folder for direct access")
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
