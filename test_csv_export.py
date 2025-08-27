#!/usr/bin/env python3
"""
Test CSV export functionality with latest results
"""

import json
from pathlib import Path
from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer

# Find latest results with actual JSON files
results_files = sorted([Path(f) for f in Path(".").glob("*/integrated_comprehensive_analysis.json")], 
                      key=lambda x: x.parent.name, reverse=True)
if not results_files:
    print("❌ No results files found")
    exit(1)

results_file = results_files[0]
latest_dir = results_file.parent

print(f"🧪 TESTING CSV EXPORT")
print(f"📁 Using results from: {latest_dir}")
print("=" * 50)

try:
    # Load results
    with open(results_file) as f:
        results = json.load(f)
    
    print(f"✅ Loaded results: {results_file.stat().st_size} bytes")
    
    # Extract gaps from full AI analysis (using our enhanced parser)
    analyzer = IntegratedComprehensiveMedicalAnalyzer()
    
    # Get the full AI analysis
    full_analysis = results.get('analysis_results', {}).get('full_ai_analysis', '')
    
    if 'GAPS ANALYSIS:' in full_analysis:
        gaps_section = full_analysis.split('GAPS ANALYSIS:')[1]
        
        print(f"🔍 Parsing gaps from full analysis ({len(gaps_section)} characters)...")
        extracted_gaps = analyzer._extract_ai_gaps(gaps_section)
        
        # Update the results with extracted gaps
        if 'analysis_results' not in results:
            results['analysis_results'] = {}
        results['analysis_results']['ai_gaps'] = extracted_gaps
        
        print(f"📊 Extracted {len(extracted_gaps)} gaps")
    
    # Create CSV export
    # Set the analyzer's output_dir to the same directory as the JSON results
    analyzer.output_dir = latest_dir
    
    print(f"\n📊 Exporting to CSV format...")
    csv_files = analyzer.export_to_csv(results)
    
    if csv_files:
        print(f"\n✅ CSV Export Complete!")
        print(f"📊 {len(csv_files)} CSV files created:")
        for file_type, file_path in csv_files.items():
            file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
            print(f"   • {file_type.title()}: {file_path} ({file_size} bytes)")
    else:
        print(f"\n⚠️ No CSV files created")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()