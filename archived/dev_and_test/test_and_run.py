import sys
import os

# Add the project directory to Python path
project_dir = "/Users/pranay/Projects/adhoc_projects/drrishi/final_submission"
sys.path.insert(0, project_dir)
os.chdir(project_dir)

print("🚀 Starting basic test...")

try:
    # Test basic imports
    import pandas as pd
    print("✅ pandas imported successfully")
    
    # Test tabula import
    try:
        import tabula
        print("✅ tabula imported successfully")
    except ImportError as e:
        print(f"⚠️ tabula import failed: {e}")
    
    # Test OpenAI import
    try:
        import openai
        print("✅ openai imported successfully")
    except ImportError as e:
        print(f"⚠️ openai import failed: {e}")
    
    # Check if PDF exists
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    if os.path.exists(pdf_path):
        print(f"✅ PDF file found: {pdf_path}")
    else:
        print(f"❌ PDF file not found: {pdf_path}")
    
    # Try to import the analyzer
    try:
        from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
        print("✅ IntegratedComprehensiveMedicalAnalyzer imported successfully")
        
        # Initialize analyzer
        analyzer = IntegratedComprehensiveMedicalAnalyzer()
        print("✅ Analyzer initialized successfully")
        
        # Now try to run a basic analysis
        print("\n🎯 Starting basic analysis...")
        pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
        
        # Run the complete analysis
        results = analyzer.analyze_complete_document(pdf_path, run_extended_ai=False)
        
        print("\n✅ Analysis completed successfully!")
        
        # Print basic results
        if 'summary_statistics' in results:
            stats = results['summary_statistics']
            print(f"\n📊 SUMMARY:")
            print(f"   • Total services/procedures: {stats.get('total_services_procedures', 0)}")
            print(f"   • Services with tariffs: {stats.get('total_with_tariffs', 0)}")
            print(f"   • Tariff coverage: {stats.get('tariff_coverage_percent', 0):.1f}%")
        
        if 'analysis_results' in results:
            ai_results = results['analysis_results']
            print(f"\n🤖 AI RESULTS:")
            print(f"   • Contradictions: {len(ai_results.get('ai_contradictions', []))}")
            print(f"   • Gaps: {len(ai_results.get('ai_gaps', []))}")

        # Export to CSV
        try:
            csv_files = analyzer.export_to_csv(results)
            print(f"\n💾 CSV FILES CREATED: {len(csv_files)}")
            for name, path in csv_files.items():
                print(f"   • {name}: {path}")
        except Exception as e:
            print(f"⚠️ CSV export failed: {e}")
        
        print("\n🎉 FULL ANALYSIS COMPLETE!")
        
    except Exception as e:
        print(f"❌ Analyzer failed: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"❌ Basic setup failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("TEST COMPLETE!")
print("="*50)
