#!/usr/bin/env python3
"""
Quick test of the current analyzer status
"""

import sys
import os
from pathlib import Path

print("🧪 TESTING CURRENT ANALYZER STATUS")
print("="*50)

# Test 1: Import check
try:
    from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
    print("✅ Main analyzer imports successfully")
except Exception as e:
    print(f"❌ Main analyzer import failed: {e}")
    sys.exit(1)

# Test 2: Enhanced prompts check
try:
    from integrated_comprehensive_analyzer import UpdatedHealthcareAIPrompts
    prompts = UpdatedHealthcareAIPrompts()
    print("✅ Enhanced prompts class available")
except Exception as e:
    print(f"❌ Enhanced prompts failed: {e}")

# Test 3: Check if PDF exists
pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
if Path(pdf_path).exists():
    print(f"✅ PDF file found: {pdf_path}")
else:
    print(f"❌ PDF file missing: {pdf_path}")

# Test 4: API key check
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print("✅ OpenAI API key found")
else:
    print("❌ OpenAI API key missing")

# Test 5: Initialize analyzer
try:
    analyzer = IntegratedComprehensiveMedicalAnalyzer()
    print("✅ Analyzer initialization successful")
    print(f"   Primary model: {analyzer.primary_model}")
    print(f"   Fallback model: {analyzer.fallback_model}")
    print(f"   API client: {'Available' if analyzer.client else 'Missing'}")
    print(f"   Output dir: {analyzer.output_dir}")
except Exception as e:
    print(f"❌ Analyzer initialization failed: {e}")

# Test 6: Check latest results
output_dirs = sorted([d for d in Path(".").glob("outputs_run_*") if d.is_dir()], reverse=True)
if output_dirs:
    latest_dir = output_dirs[0]
    print(f"✅ Latest results: {latest_dir}")
    
    # Check for results file
    results_file = latest_dir / "integrated_comprehensive_analysis.json"
    if results_file.exists():
        import json
        try:
            with open(results_file) as f:
                results = json.load(f)
            
            ai_results = results.get('analysis_results', {})
            contradictions = len(ai_results.get('ai_contradictions', []))
            gaps = len(ai_results.get('ai_gaps', []))
            
            print(f"   📊 Last run results:")
            print(f"      • Contradictions: {contradictions}")
            print(f"      • Gaps: {gaps}")
            print(f"      • File size: {results_file.stat().st_size} bytes")
            
            # Check if gaps analysis is present in full_analysis
            full_analysis = ai_results.get('full_ai_analysis', '')
            has_gaps_section = 'GAPS ANALYSIS:' in full_analysis
            print(f"      • Gaps section in full analysis: {'Yes' if has_gaps_section else 'No'}")
            
        except Exception as e:
            print(f"   ⚠️ Could not parse results: {e}")
    else:
        print(f"   ⚠️ No results file found in {latest_dir}")
else:
    print("❌ No output directories found")

print("\n🎯 STATUS SUMMARY:")
print("="*50)
print("The analyzer has been enhanced with:")
print("✅ Your sophisticated Kenya health prompts")
print("✅ Fixed variable scoping for gap analysis")
print("✅ Enhanced JSON parsing logic")
print("✅ Real-time debugging output")
print("\nNext step: Test with a full run to verify gaps are detected!")