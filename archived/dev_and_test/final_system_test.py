import os
import json
import pandas as pd
from datetime import datetime

def run_final_validation():
    print("🔍 Running Final System Validation...")
    
    validation_results = {
        "timestamp": datetime.now().isoformat(),
        "tests_passed": 0,
        "tests_failed": 0,
        "issues": []
    }
    
    # Test 1: Core files exist
    core_files = [
        "streamlit_comprehensive_analyzer.py",
        "integrated_comprehensive_analyzer.py", 
        "deterministic_checker.py",
        "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    ]
    
    for file in core_files:
        if os.path.exists(file):
            validation_results["tests_passed"] += 1
            print(f"✅ {file}")
        else:
            validation_results["tests_failed"] += 1
            validation_results["issues"].append(f"Missing core file: {file}")
            print(f"❌ {file}")
    
    # Test 2: Output directories exist
    output_dirs = [d for d in os.listdir('.') if d.startswith('outputs_run_')]
    if output_dirs:
        validation_results["tests_passed"] += 1
        latest = sorted(output_dirs)[-1]
        print(f"✅ Analysis outputs: {len(output_dirs)} runs (latest: {latest})")
        
        # Check content of latest
        latest_files = os.listdir(latest)
        if 'integrated_comprehensive_analysis.json' in latest_files:
            with open(os.path.join(latest, 'integrated_comprehensive_analysis.json')) as f:
                data = json.load(f)
                if 'annex_results' in data:
                    annex_count = len(data['annex_results'].get('procedures', []))
                    print(f"   • Annex procedures: {annex_count}")
                if 'ai_analysis' in data:
                    contradictions = len(data['ai_analysis'].get('contradictions', []))
                    gaps = len(data['ai_analysis'].get('gaps', []))
                    print(f"   • AI contradictions: {contradictions}")
                    print(f"   • AI gaps: {gaps}")
    else:
        validation_results["tests_failed"] += 1
        validation_results["issues"].append("No analysis output directories found")
        print("❌ No analysis outputs")
    
    # Test 3: Sample outputs ready
    if os.path.exists('sample_outputs_fresh'):
        sample_files = os.listdir('sample_outputs_fresh')
        validation_results["tests_passed"] += 1
        print(f"✅ Sample outputs: {len(sample_files)} files")
    else:
        validation_results["tests_failed"] += 1
        validation_results["issues"].append("Sample outputs directory missing")
        print("❌ Sample outputs missing")
    
    # Test 4: Release package ready
    release_dirs = [d for d in os.listdir('.') if d.startswith('demo_release_') and '_final' in d]
    if release_dirs:
        validation_results["tests_passed"] += 1
        print(f"✅ Release package: {release_dirs[0]}")
        
        # Check release contents
        release_contents = os.listdir(release_dirs[0])
        print(f"   • Contents: {', '.join(release_contents)}")
    else:
        validation_results["tests_failed"] += 1
        validation_results["issues"].append("Demo release package missing")
        print("❌ Release package missing")
    
    # Test 5: Streamlit running
    import subprocess
    try:
        result = subprocess.run(['pgrep', '-f', 'streamlit'], capture_output=True)
        if result.returncode == 0:
            validation_results["tests_passed"] += 1
            print(f"✅ Streamlit running (PID: {result.stdout.decode().strip()})")
        else:
            print("⚠️ Streamlit not running (optional)")
    except:
        print("⚠️ Cannot check Streamlit status")
    
    # Save validation results
    with open('final_validation_results.json', 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\n📊 Final Validation Summary:")
    print(f"   Tests Passed: {validation_results['tests_passed']}")
    print(f"   Tests Failed: {validation_results['tests_failed']}")
    
    if validation_results["issues"]:
        print(f"   Issues Found:")
        for issue in validation_results["issues"]:
            print(f"     - {issue}")
    
    return validation_results["tests_failed"] == 0

if __name__ == "__main__":
    success = run_final_validation()
    if success:
        print("\n🎉 System validation PASSED - Demo ready!")
    else:
        print("\n⚠️ System validation FAILED - Address issues above")
