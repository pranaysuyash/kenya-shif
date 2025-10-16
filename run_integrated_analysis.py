#!/usr/bin/env python3
"""
Runner script for the Integrated Comprehensive Medical Analyzer
"""
import sys
import os
import subprocess
from pathlib import Path

def main():
    # Ensure we're in the right directory
    project_dir = Path("/Users/pranay/Projects/adhoc_projects/drrishi/final_submission")
    os.chdir(project_dir)
    
    # PDF file path
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print("🚀 Starting Integrated Comprehensive Medical Analysis")
    print(f"📄 PDF: {pdf_path}")
    print("="*70)
    
    try:
        # Import the analyzer
        sys.path.insert(0, str(project_dir))
        from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
        
        # Initialize analyzer
        analyzer = IntegratedComprehensiveMedicalAnalyzer()
        
        # Run complete analysis
        print("\n🎯 Running comprehensive analysis...")
        results = analyzer.analyze_complete_document(pdf_path, run_extended_ai=False)
        
        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE!")
        print("="*70)
        
        # Print summary statistics
        if 'summary_statistics' in results:
            stats = results['summary_statistics']
            print(f"\n📊 SUMMARY STATISTICS:")
            print(f"   • Total services/procedures: {stats.get('total_services_procedures', 0)}")
            print(f"   • Services with tariffs: {stats.get('total_with_tariffs', 0)}")
            print(f"   • Tariff coverage: {stats.get('tariff_coverage_percent', 0):.1f}%")
            
            if stats.get('tariff_range', {}).get('min') is not None:
                tr = stats['tariff_range']
                print(f"   • Tariff range: KES {tr['min']:,.0f} - {tr['max']:,.0f}")
                print(f"   • Average tariff: KES {tr['average']:,.0f}")
        
        # Print AI analysis results
        if 'analysis_results' in results:
            ai_results = results['analysis_results']
            print(f"\n🤖 AI ANALYSIS RESULTS:")
            print(f"   • Contradictions identified: {len(ai_results.get('ai_contradictions', []))}")
            print(f"   • Gaps identified: {len(ai_results.get('ai_gaps', []))}")
            print(f"   • Insights generated: {len(ai_results.get('ai_insights', []))}")
        
        # Export to CSV
        print(f"\n💾 Exporting results to CSV...")
        try:
            csv_files = analyzer.export_to_csv(results)
            print(f"   ✅ Created {len(csv_files)} CSV files:")
            for name, path in csv_files.items():
                print(f"      • {name}: {path}")
        except Exception as e:
            print(f"   ⚠️ CSV export failed: {e}")
        
        print(f"\n🎉 Analysis complete! Check the outputs directory for detailed results.")
        
        # Print sample contradictions and gaps
        if 'analysis_results' in results:
            ai_results = results['analysis_results']
            
            contradictions = ai_results.get('ai_contradictions', [])
            if contradictions:
                print(f"\n🚨 SAMPLE CONTRADICTIONS:")
                for i, contradiction in enumerate(contradictions[:3], 1):
                    desc = contradiction.get('description', 'No description')
                    print(f"   {i}. {desc[:100]}..." if len(desc) > 100 else f"   {i}. {desc}")
            
            gaps = ai_results.get('ai_gaps', [])
            if gaps:
                print(f"\n🏥 SAMPLE GAPS:")
                for i, gap in enumerate(gaps[:3], 1):
                    desc = gap.get('description', 'No description')
                    print(f"   {i}. {desc[:100]}..." if len(desc) > 100 else f"   {i}. {desc}")
        
        return results
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
