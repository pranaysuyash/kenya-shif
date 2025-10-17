#!/usr/bin/env python3
"""Simple test to see what's happening when we run the analyzer"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("Step 1: Loading .env...")
load_dotenv()
key = os.getenv('OPENAI_API_KEY')
print(f"✅ API Key loaded: {len(key) if key else 'NOT FOUND'} chars")

print("\nStep 2: Checking PDF file...")
pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
if Path(pdf_path).exists():
    print(f"✅ PDF found: {pdf_path}")
else:
    print(f"❌ PDF NOT found: {pdf_path}")
    sys.exit(1)

print("\nStep 3: Importing analyzer...")
from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
print("✅ Analyzer imported")

print("\nStep 4: Creating analyzer instance...")
analyzer = IntegratedComprehensiveMedicalAnalyzer(pdf_path=pdf_path)
print(f"✅ Analyzer created, output dir: {analyzer.output_dir}")

print("\nStep 5: Running analyze_complete_document()...")
print("(This may take a minute...)")
import signal

def timeout_handler(signum, frame):
    print("\n⏱️  TIMEOUT - analyzer is taking too long")
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)  # 60 second timeout

try:
    results = analyzer.analyze_complete_document(pdf_path)
    signal.alarm(0)  # Cancel alarm
    print(f"✅ Analysis complete!")
    
    print(f"\nStep 6: Checking results...")
    if 'ai_analysis' in results:
        gaps = results['ai_analysis'].get('gaps', [])
        contradictions = results['ai_analysis'].get('contradictions', [])
        print(f"   Gaps: {len(gaps)}")
        print(f"   Contradictions: {len(contradictions)}")
    
except Exception as e:
    signal.alarm(0)  # Cancel alarm
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All steps completed successfully!")
