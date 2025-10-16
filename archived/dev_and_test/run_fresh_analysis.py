#!/usr/bin/env python3
"""Run a fresh comprehensive analysis"""

import sys
import os
sys.path.append('.')

# Import and run the main function directly
from integrated_comprehensive_analyzer import main

print("🚀 Starting Fresh Comprehensive Analysis...")
try:
    results = main()
    
    # Find the latest output directory
    import glob
    output_dirs = glob.glob('outputs_run_*')
    if output_dirs:
        latest_dir = sorted(output_dirs)[-1]
        print(f"✅ Analysis completed. Results in: {latest_dir}")
        
        # Count files
        files = os.listdir(latest_dir)
        print(f"📊 Files generated: {len(files)}")
        
        # Check for key files
        key_files = ['integrated_comprehensive_analysis.json', 'rules_p1_18_raw.csv', 'annex_procedures.csv']
        for kf in key_files:
            if kf in files:
                print(f"   ✅ {kf}")
            else:
                print(f"   ❌ {kf} missing")
    else:
        print("❌ No output directory created")
        
except Exception as e:
    print(f"❌ Analysis failed: {e}")
    import traceback
    traceback.print_exc()
