import json
import os

# Check what deterministic checker is looking for
print("🔍 Checking deterministic validation issue...")

# 1. Check what's in sample_outputs
if os.path.exists('sample_outputs/integrated_comprehensive_analysis.json'):
    with open('sample_outputs/integrated_comprehensive_analysis.json', 'r') as f:
        data = json.load(f)
        print("✅ sample_outputs JSON exists")
        print(f"   - Has ai_analysis: {'ai_analysis' in data}")
        if 'ai_analysis' in data:
            print(f"   - Contradictions: {len(data['ai_analysis'].get('contradictions', []))}")
            # Check for dialysis
            for c in data['ai_analysis'].get('contradictions', []):
                if 'dial' in str(c).lower():
                    print("   - ✅ DIALYSIS contradiction found in AI output")
                    break
else:
    print("❌ sample_outputs/integrated_comprehensive_analysis.json NOT FOUND")

# 2. Check outputs_run directory
latest = 'outputs_run_20250827_151032'
if os.path.exists(f'{latest}/integrated_comprehensive_analysis.json'):
    with open(f'{latest}/integrated_comprehensive_analysis.json', 'r') as f:
        data = json.load(f)
        print(f"\n✅ {latest} JSON exists")
        print(f"   - Has ai_analysis: {'ai_analysis' in data}")
        if 'ai_analysis' in data:
            contradictions = data['ai_analysis'].get('contradictions', [])
            print(f"   - Contradictions: {len(contradictions)}")
            for c in contradictions:
                if 'dial' in str(c).lower():
                    print(f"   - ✅ DIALYSIS found: {c.get('contradiction_id', 'unknown')}")
                    break

print("\n⚠️ The issue: deterministic_checker.py is looking in wrong location or format")
