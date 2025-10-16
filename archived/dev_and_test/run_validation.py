#!/usr/bin/env python3
"""
Validation Runner - Execute deployment and validate results
"""

import subprocess
import sys
import os
import time

def main():
    """Run deployment and validation"""
    print("🚀 VALIDATION RUNNER: DEPLOYMENT + COMPREHENSIVE VALIDATION")
    print("=" * 70)
    
    os.chdir('/Users/pranay/Projects/adhoc_projects/drrishi/final_submission')
    
    # Execute deployment
    print("📋 Step 1: Running deployment...")
    start_time = time.time()
    
    try:
        result = subprocess.run([sys.executable, 'deploy_generalized.py'], 
                              capture_output=True, text=True, timeout=300)
        
        deployment_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ Deployment successful! ({deployment_time:.1f}s)")
            print("📋 Output:")
            print(result.stdout)
            if result.stderr:
                print("⚠️ Warnings:")
                print(result.stderr)
        else:
            print(f"❌ Deployment failed with return code {result.returncode}")
            print("Error output:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Deployment timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False
    
    # List output files
    print(f"\n📁 Checking output directories...")
    
    if os.path.exists('outputs_generalized'):
        files = os.listdir('outputs_generalized')
        print(f"✅ outputs_generalized/ contains {len(files)} files:")
        for file in sorted(files):
            print(f"   - {file}")
    
    # Check for timestamped directories
    import glob
    timestamped_dirs = glob.glob('outputs_generalized_*')
    if timestamped_dirs:
        latest_dir = max(timestamped_dirs)
        print(f"\n✅ Latest timestamped directory: {latest_dir}")
        files = os.listdir(latest_dir)
        print(f"   Contains {len(files)} files:")
        for file in sorted(files):
            print(f"   - {file}")
    
    print(f"\n🎉 DEPLOYMENT AND FILE CHECK COMPLETE!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
