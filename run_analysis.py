import sys
import os
from datetime import datetime
sys.path.append('.')

def run_comprehensive_analysis():
    try:
        from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
        
        print("🚀 Starting Integrated Comprehensive Analysis...")
        analyzer = IntegratedComprehensiveMedicalAnalyzer()
        
        # Run the main method that exists
        results = analyzer.run_comprehensive_analysis(
            pdf_path="TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
        )
        
        # Get the output directory from analyzer
        output_dir = analyzer.output_dir
        
        print(f"✅ Analysis completed. Results in: {output_dir}")
        return results, str(output_dir)
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    results, output_dir = run_comprehensive_analysis()
    if results and output_dir:
        print(f"📊 Analysis Results Summary:")
        print(f"   - Output Directory: {output_dir}")
        print(f"   - Files Generated: {len(os.listdir(output_dir)) if os.path.exists(output_dir) else 0}")
        
        # Check key metrics
        if isinstance(results, dict):
            if 'policy_results' in results:
                policy_count = results['policy_results'].get('total_services', 0)
                print(f"   - Policy Services: {policy_count}")
            if 'annex_results' in results:
                annex_count = len(results['annex_results'].get('procedures', []))
                print(f"   - Annex Procedures: {annex_count}")
            if 'ai_analysis' in results:
                contradictions = len(results['ai_analysis'].get('contradictions', []))
                gaps = len(results['ai_analysis'].get('gaps', []))
                print(f"   - AI Contradictions: {contradictions}")
                print(f"   - AI Gaps: {gaps}")
