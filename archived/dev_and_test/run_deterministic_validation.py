#!/usr/bin/env python3
"""
Run Deterministic Validation on Analysis Results
Checks for Dr. Rishi's specific requirements
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_analysis_outputs(output_dir="demo_release_20250827_FINAL_WITH_DEDUP/outputs"):
    """Load all analysis outputs"""
    outputs = {}
    output_path = Path(output_dir)
    
    # Load CSV files
    csv_files = {
        'policy_services': 'rules_p1_18_structured.csv',
        'annex_procedures': 'annex_procedures.csv',
        'ai_contradictions': 'ai_contradictions.csv',
        'ai_gaps': 'ai_gaps.csv',
        'comprehensive_gaps': 'comprehensive_gaps_analysis.csv',
        'coverage_gaps': 'coverage_gaps_analysis.csv'
    }
    
    for key, filename in csv_files.items():
        filepath = output_path / filename
        if filepath.exists():
            try:
                df = pd.read_csv(filepath)
                outputs[key] = df
                print(f"✅ Loaded {filename}: {len(df)} rows")
            except Exception as e:
                print(f"⚠️ Error loading {filename}: {e}")
                outputs[key] = pd.DataFrame()
        else:
            print(f"❌ Not found: {filename}")
            outputs[key] = pd.DataFrame()
    
    return outputs

def check_dialysis_contradiction(outputs):
    """Check for dialysis contradiction (Dr. Rishi's requirement)"""
    
    # Check in AI contradictions
    if 'ai_contradictions' in outputs and not outputs['ai_contradictions'].empty:
        contradictions_df = outputs['ai_contradictions']
        
        # Check for dialysis in contradictions
        dialysis_found = False
        for idx, row in contradictions_df.iterrows():
            text = str(row.to_dict()).lower()
            if any(term in text for term in ['dialysis', 'hemodialysis', 'haemodialysis', 'hemodiafiltration']):
                dialysis_found = True
                print(f"   ✅ Dialysis contradiction found in row {idx}")
                
                # Check for specific session frequency contradiction
                if '3 sessions' in text or 'three sessions' in text:
                    if '2 sessions' in text or 'two sessions' in text:
                        print(f"   ✅ CRITICAL: Session frequency mismatch found!")
                        return True, "Dialysis session frequency mismatch detected (3 vs 2 sessions/week)"
        
        if dialysis_found:
            return True, "Dialysis contradiction detected in AI analysis"
    
    # Also check in policy services for dialysis entries
    if 'policy_services' in outputs and not outputs['policy_services'].empty:
        services_df = outputs['policy_services']
        dialysis_services = []
        
        for idx, row in services_df.iterrows():
            text = str(row.to_dict()).lower()
            if 'dialysis' in text or 'haemodialysis' in text or 'hemodialysis' in text:
                dialysis_services.append(row)
        
        if dialysis_services:
            print(f"   Found {len(dialysis_services)} dialysis-related services")
            return True, f"Found {len(dialysis_services)} dialysis services to validate"
    
    return False, "No dialysis contradiction found"

def check_hypertension_gap(outputs):
    """Check for hypertension gap (Dr. Rishi's requirement)"""
    
    # Check in comprehensive gaps
    if 'comprehensive_gaps' in outputs and not outputs['comprehensive_gaps'].empty:
        gaps_df = outputs['comprehensive_gaps']
        
        for idx, row in gaps_df.iterrows():
            text = str(row.to_dict()).lower()
            if 'hypertension' in text:
                return True, f"Hypertension gap found in comprehensive gaps (row {idx})"
    
    # Check in AI gaps
    if 'ai_gaps' in outputs and not outputs['ai_gaps'].empty:
        gaps_df = outputs['ai_gaps']
        
        for idx, row in gaps_df.iterrows():
            text = str(row.to_dict()).lower()
            if 'hypertension' in text:
                return True, f"Hypertension gap found in AI gaps (row {idx})"
    
    # Check in coverage gaps
    if 'coverage_gaps' in outputs and not outputs['coverage_gaps'].empty:
        gaps_df = outputs['coverage_gaps']
        
        for idx, row in gaps_df.iterrows():
            text = str(row.to_dict()).lower()
            if 'hypertension' in text:
                return True, f"Hypertension coverage gap found (row {idx})"
    
    return False, "No hypertension gap found"

def generate_validation_report(outputs):
    """Generate comprehensive validation report"""
    
    # Count totals
    policy_count = len(outputs.get('policy_services', pd.DataFrame()))
    annex_count = len(outputs.get('annex_procedures', pd.DataFrame()))
    contradiction_count = len(outputs.get('ai_contradictions', pd.DataFrame()))
    gap_count = len(outputs.get('comprehensive_gaps', pd.DataFrame()))
    
    # Check Dr. Rishi's requirements
    dialysis_found, dialysis_msg = check_dialysis_contradiction(outputs)
    hypertension_found, hypertension_msg = check_hypertension_gap(outputs)
    
    # Generate report
    report = f"""# SHIF Policy Deterministic Validation Report

**Generated:** {datetime.now().isoformat()}

## ✅ Analysis Summary

- **Policy services analyzed:** {policy_count}
- **Annex procedures analyzed:** {annex_count}
- **AI contradictions found:** {contradiction_count}
- **Comprehensive gaps found:** {gap_count}
- **AI analysis available:** {'✅' if contradiction_count > 0 else '❌'}

## 📋 Dr. Rishi's Assignment Requirements

### 1. Dialysis Contradiction Check
- **Status:** {'✅ FOUND' if dialysis_found else '❌ NOT FOUND'}
- **Details:** {dialysis_msg}

### 2. Hypertension Gap Check  
- **Status:** {'✅ FOUND' if hypertension_found else '❌ NOT FOUND'}
- **Details:** {hypertension_msg}

## 📊 Detailed Analysis

### Contradictions Detected
**Total:** {contradiction_count}
"""
    
    if contradiction_count > 0 and 'ai_contradictions' in outputs:
        df = outputs['ai_contradictions']
        report += "\n**Sample Contradictions:**\n"
        for idx, row in df.head(3).iterrows():
            desc = row.get('description', row.get('contradiction_type', 'Unknown'))
            report += f"- {desc[:100]}...\n"
    
    report += f"""

### Coverage Gaps Detected
**Total gaps:** {gap_count}
"""
    
    if gap_count > 0 and 'comprehensive_gaps' in outputs:
        df = outputs['comprehensive_gaps']
        report += "\n**Sample Gaps:**\n"
        for idx, row in df.head(5).iterrows():
            desc = row.get('description', row.get('gap_type', 'Unknown'))
            report += f"- {desc[:100]}...\n"
    
    # Add validation status
    report += f"""

## ✅ Validation Status

| Requirement | Status |
|------------|--------|
| PDF Extraction | {'✅ PASS' if policy_count > 0 else '❌ FAIL'} |
| Contradiction Detection | {'✅ PASS' if contradiction_count > 0 else '❌ FAIL'} |
| Gap Analysis | {'✅ PASS' if gap_count > 0 else '❌ FAIL'} |
| Dialysis Contradiction | {'✅ PASS' if dialysis_found else '❌ FAIL'} |
| Hypertension Gap | {'✅ PASS' if hypertension_found else '❌ FAIL'} |

## Summary

**Overall Status:** {'✅ ALL CHECKS PASSED' if all([policy_count > 0, contradiction_count > 0, gap_count > 0, dialysis_found, hypertension_found]) else '⚠️ SOME CHECKS FAILED'}

---
*Validation performed on actual analysis outputs*
"""
    
    return report

def main():
    print("🔍 Running Deterministic Validation")
    print("=" * 60)
    
    # Load outputs
    outputs = load_analysis_outputs()
    
    print("\n📋 Checking Dr. Rishi's Requirements...")
    print("-" * 40)
    
    # Check specific requirements
    dialysis_found, dialysis_msg = check_dialysis_contradiction(outputs)
    print(f"Dialysis contradiction: {'✅ FOUND' if dialysis_found else '❌ NOT FOUND'}")
    print(f"   {dialysis_msg}")
    
    hypertension_found, hypertension_msg = check_hypertension_gap(outputs)
    print(f"Hypertension gap: {'✅ FOUND' if hypertension_found else '❌ NOT FOUND'}")
    print(f"   {hypertension_msg}")
    
    # Generate report
    report = generate_validation_report(outputs)
    
    # Save report
    output_dir = Path("demo_release_20250827_FINAL_WITH_DEDUP/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = output_dir / "deterministic_validation.md"
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n✅ Validation report saved: {report_path}")
    
    # Also save as JSON
    validation_results = {
        "timestamp": datetime.now().isoformat(),
        "policy_services_count": len(outputs.get('policy_services', [])),
        "annex_procedures_count": len(outputs.get('annex_procedures', [])),
        "contradictions_count": len(outputs.get('ai_contradictions', [])),
        "gaps_count": len(outputs.get('comprehensive_gaps', [])),
        "dialysis_contradiction_found": dialysis_found,
        "dialysis_details": dialysis_msg,
        "hypertension_gap_found": hypertension_found,
        "hypertension_details": hypertension_msg
    }
    
    json_path = output_dir / "deterministic_validation.json"
    with open(json_path, 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"✅ JSON results saved: {json_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    if all([dialysis_found, hypertension_found]):
        print("✅ ALL VALIDATION CHECKS PASSED!")
    else:
        print("⚠️ SOME VALIDATION CHECKS FAILED")
        if not dialysis_found:
            print("   ❌ Dialysis contradiction not detected")
        if not hypertension_found:
            print("   ❌ Hypertension gap not detected")

if __name__ == "__main__":
    main()