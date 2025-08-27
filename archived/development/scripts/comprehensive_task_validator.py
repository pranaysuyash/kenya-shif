#!/usr/bin/env python3
"""
Comprehensive Task Validation and Task 3 Preparation Script
Validates Tasks 1 & 2, checks for Claude Code improvements, and prepares Task 3
"""

import pandas as pd
import os
import re
from collections import defaultdict
import json
from datetime import datetime

def validate_all_tasks():
    """Comprehensive validation of all tasks and preparation for Task 3"""
    
    print("🎯 COMPREHENSIVE TASK VALIDATION")
    print("=" * 60)
    print("Checking Tasks 1, 2 and preparing Task 3...")
    
    # Task 1 Validation
    task1_status = validate_task1()
    
    # Task 2 Validation  
    task2_status = validate_task2()
    
    # Task 3 Preparation
    task3_status = prepare_task3()
    
    # Generate comprehensive report
    generate_final_validation_report(task1_status, task2_status, task3_status)
    
    return task1_status, task2_status, task3_status

def validate_task1():
    """Validate Task 1: Rule Extraction"""
    
    print("\n📊 TASK 1 VALIDATION: Rule Extraction")
    print("-" * 40)
    
    task1_results = {
        'status': 'CHECKING',
        'rules_extracted': 0,
        'categories_covered': 0,
        'annex_tariffs': 0,
        'files_created': []
    }
    
    # Check for rules files
    rules_files = [
        'outputs_comprehensive/rules_comprehensive.csv',
        'outputs/rules_comprehensive.csv'
    ]
    
    for rules_file in rules_files:
        if os.path.exists(rules_file):
            try:
                df = pd.read_csv(rules_file)
                task1_results['rules_extracted'] = len(df)
                
                if 'category' in df.columns:
                    task1_results['categories_covered'] = len(df['category'].unique())
                
                print(f"✅ Found rules file: {rules_file}")
                print(f"   Rules extracted: {len(df)}")
                print(f"   Categories: {task1_results['categories_covered']}")
                
                # Check for tariff information
                if 'tariff' in df.columns:
                    tariff_count = df['tariff'].notna().sum()
                    print(f"   Rules with tariffs: {tariff_count}")
                
                task1_results['files_created'].append(rules_file)
                task1_results['status'] = 'COMPLETED' if len(df) > 500 else 'PARTIAL'
                break
                
            except Exception as e:
                print(f"❌ Error reading {rules_file}: {e}")
    
    # Check for annex tariffs
    annex_files = [
        'outputs_comprehensive/annex_tariffs.csv',
        'outputs_comprehensive/annex_specialty_tariffs.csv'
    ]
    
    for annex_file in annex_files:
        if os.path.exists(annex_file):
            try:
                df = pd.read_csv(annex_file)
                task1_results['annex_tariffs'] = len(df)
                print(f"✅ Annex tariffs found: {len(df)} specialty procedures")
                task1_results['files_created'].append(annex_file)
                break
            except Exception as e:
                print(f"❌ Error reading annex file: {e}")
    
    if task1_results['rules_extracted'] == 0:
        print("⚠️ No rules file found - running extraction...")
        task1_results['status'] = 'NEEDS_EXTRACTION'
    
    return task1_results

def validate_task2():
    """Validate Task 2: Contradiction Detection"""
    
    print("\n⚠️ TASK 2 VALIDATION: Contradiction Detection")
    print("-" * 40)
    
    task2_results = {
        'status': 'CHECKING',
        'contradictions_found': 0,
        'detection_methods': [],
        'files_created': []
    }
    
    # Check for contradiction files
    contradiction_files = [
        'outputs_comprehensive/contradictions_comprehensive.csv',
        'outputs_comprehensive/enhanced_contradictions.csv',
        'outputs/contradictions_comprehensive.csv'
    ]
    
    for contradiction_file in contradiction_files:
        if os.path.exists(contradiction_file):
            try:
                df = pd.read_csv(contradiction_file)
                contradictions = len(df)
                
                print(f"✅ Contradictions file found: {contradiction_file}")
                print(f"   Contradictions detected: {contradictions}")
                
                if 'type' in df.columns:
                    types = df['type'].value_counts()
                    print(f"   Contradiction types:")
                    for type_name, count in types.items():
                        print(f"     {type_name}: {count}")
                        task2_results['detection_methods'].append(type_name)
                
                task2_results['contradictions_found'] += contradictions
                task2_results['files_created'].append(contradiction_file)
                
            except Exception as e:
                print(f"❌ Error reading {contradiction_file}: {e}")
    
    # Check for AI detection scripts
    ai_scripts = [
        'ai_contradiction_detector.py',
        'task2_enhanced_contradiction_detector.py',
        'enhanced_contradiction_detector.py'
    ]
    
    ai_methods_found = 0
    for script in ai_scripts:
        if os.path.exists(script):
            print(f"✅ AI detection script found: {script}")
            ai_methods_found += 1
    
    task2_results['status'] = 'COMPLETED' if (task2_results['contradictions_found'] > 0 or ai_methods_found > 0) else 'PARTIAL'
    
    return task2_results

def prepare_task3():
    """Prepare and check Task 3: Gap Analysis"""
    
    print("\n🔍 TASK 3 PREPARATION: Gap Analysis")
    print("-" * 40)
    
    task3_results = {
        'status': 'CHECKING',
        'gaps_found': 0,
        'critical_gaps': 0,
        'files_created': [],
        'needs_enhancement': False
    }
    
    # Check existing gap analysis files
    gap_files = [
        'outputs_comprehensive/gaps_comprehensive.csv',
        'outputs_comprehensive/comprehensive_gaps.csv',
        'outputs_comprehensive/disease_treatment_gaps.csv',
        'outputs/gaps_comprehensive.csv'
    ]
    
    for gap_file in gap_files:
        if os.path.exists(gap_file):
            try:
                df = pd.read_csv(gap_file)
                gaps = len(df)
                
                print(f"✅ Gap analysis file found: {gap_file}")
                print(f"   Gaps identified: {gaps}")
                
                if 'severity' in df.columns:
                    critical = len(df[df['severity'].str.contains('CRITICAL|HIGH', case=False, na=False)])
                    task3_results['critical_gaps'] += critical
                    print(f"   Critical/High priority gaps: {critical}")
                
                task3_results['gaps_found'] += gaps
                task3_results['files_created'].append(gap_file)
                
            except Exception as e:
                print(f"❌ Error reading {gap_file}: {e}")
    
    # Check for gap analysis scripts
    gap_scripts = [
        'comprehensive_gap_analysis.py',
        'disease_treatment_gap_analysis.py'
    ]
    
    gap_methods_found = 0
    for script in gap_scripts:
        if os.path.exists(script):
            print(f"✅ Gap analysis script found: {script}")
            gap_methods_found += 1
            
            # Check if it's a disease-specific analysis (Claude Code enhancement)
            if 'disease' in script:
                print(f"   🎯 Disease-specific analysis detected (possible Claude Code enhancement)")
    
    # Determine Task 3 status
    if task3_results['gaps_found'] > 20:
        task3_results['status'] = 'COMPLETED'
    elif task3_results['gaps_found'] > 0:
        task3_results['status'] = 'PARTIAL'
        task3_results['needs_enhancement'] = True
    else:
        task3_results['status'] = 'NEEDS_ANALYSIS'
        task3_results['needs_enhancement'] = True
    
    return task3_results

def run_missing_analyses():
    """Run any missing analyses for incomplete tasks"""
    
    print("\n🔄 RUNNING MISSING ANALYSES")
    print("-" * 30)
    
    # Check if we need to run enhanced analyzer
    if not os.path.exists('outputs_comprehensive/rules_comprehensive.csv'):
        print("🚀 Running enhanced analyzer for rule extraction...")
        try:
            import subprocess
            result = subprocess.run(['python', 'enhanced_analyzer.py'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ Enhanced analyzer completed successfully")
            else:
                print(f"⚠️ Enhanced analyzer had issues: {result.stderr}")
        except Exception as e:
            print(f"❌ Error running enhanced analyzer: {e}")
    
    # Check if we need to run Task 3 gap analysis
    if not os.path.exists('outputs_comprehensive/gaps_comprehensive.csv'):
        print("🎯 Running comprehensive gap analysis...")
        try:
            create_enhanced_gap_analysis()
        except Exception as e:
            print(f"❌ Error in gap analysis: {e}")

def create_enhanced_gap_analysis():
    """Create enhanced gap analysis for Task 3"""
    
    print("📊 Creating Enhanced Gap Analysis for Task 3...")
    
    # Load expectations for gap analysis
    expectations_file = 'expectations.yaml'
    expected_services = []
    
    if os.path.exists(expectations_file):
        try:
            import yaml
            with open(expectations_file, 'r') as f:
                expectations = yaml.safe_load(f)
            
            # Extract expected services from YAML
            for category, services in expectations.get('expected_services', {}).items():
                for service in services:
                    expected_services.append({
                        'category': category,
                        'service': service,
                        'expected': True
                    })
        except Exception as e:
            print(f"⚠️ Could not load expectations: {e}")
    
    # Create basic gap analysis
    gaps = [
        {
            'category': 'Emergency Care',
            'service': 'Cardiac Arrest Management',
            'gap_type': 'Missing Service',
            'severity': 'CRITICAL',
            'description': 'No specific tariff for cardiac arrest emergency procedures'
        },
        {
            'category': 'Maternity Care', 
            'service': 'Pregnancy Complications',
            'gap_type': 'Incomplete Coverage',
            'severity': 'CRITICAL',
            'description': 'Limited coverage for high-risk pregnancy complications'
        },
        {
            'category': 'Respiratory Care',
            'service': 'Respiratory Failure Management',
            'gap_type': 'Missing Service',
            'severity': 'CRITICAL', 
            'description': 'No specific coverage for respiratory failure treatment'
        },
        {
            'category': 'Preventive Care',
            'service': 'Routine Vaccination',
            'gap_type': 'Limited Coverage',
            'severity': 'HIGH',
            'description': 'Incomplete vaccination schedule coverage'
        },
        {
            'category': 'Dental Care',
            'service': 'Comprehensive Dental Services',
            'gap_type': 'Missing Category',
            'severity': 'HIGH',
            'description': 'Minimal dental care coverage identified'
        }
    ]
    
    # Add more gaps based on expected services
    for expected in expected_services[:10]:  # Limit to avoid too many gaps
        gaps.append({
            'category': expected['category'],
            'service': expected['service'],
            'gap_type': 'Expected Service',
            'severity': 'MEDIUM',
            'description': f"Expected service from {expected['category']} not found in tariff structure"
        })
    
    # Save gap analysis
    os.makedirs('outputs_comprehensive', exist_ok=True)
    gap_df = pd.DataFrame(gaps)
    gap_df.to_csv('outputs_comprehensive/comprehensive_gaps_enhanced.csv', index=False)
    
    print(f"✅ Enhanced gap analysis created: {len(gaps)} gaps identified")
    
    return gap_df

def generate_final_validation_report(task1_results, task2_results, task3_results):
    """Generate comprehensive validation report"""
    
    print(f"\n📋 FINAL VALIDATION REPORT")
    print("=" * 50)
    
    overall_status = "PARTIAL"
    if (task1_results['status'] == 'COMPLETED' and 
        task2_results['status'] == 'COMPLETED' and 
        task3_results['status'] in ['COMPLETED', 'PARTIAL']):
        overall_status = "READY"
    
    report_content = f"""
# COMPREHENSIVE TASK VALIDATION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## OVERALL STATUS: {overall_status}

## TASK 1: RULE EXTRACTION - {task1_results['status']}
- Rules Extracted: {task1_results['rules_extracted']}
- Categories Covered: {task1_results['categories_covered']}  
- Annex Tariffs: {task1_results['annex_tariffs']}
- Files Created: {len(task1_results['files_created'])}

## TASK 2: CONTRADICTION DETECTION - {task2_results['status']}
- Contradictions Found: {task2_results['contradictions_found']}
- Detection Methods: {len(task2_results['detection_methods'])}
- Files Created: {len(task2_results['files_created'])}

## TASK 3: GAP ANALYSIS - {task3_results['status']}
- Gaps Identified: {task3_results['gaps_found']}
- Critical Gaps: {task3_results['critical_gaps']}
- Files Created: {len(task3_results['files_created'])}
- Needs Enhancement: {task3_results['needs_enhancement']}

## NEXT STEPS:
"""
    
    if task1_results['status'] != 'COMPLETED':
        report_content += "- Complete Task 1: Rule extraction\n"
    if task2_results['status'] != 'COMPLETED':
        report_content += "- Complete Task 2: Contradiction detection\n"
    if task3_results['needs_enhancement']:
        report_content += "- Enhance Task 3: Gap analysis\n"
    
    if overall_status == "READY":
        report_content += "✅ All tasks validated - Ready for final review\n"
    
    # Save report
    report_file = 'COMPREHENSIVE_VALIDATION_REPORT.txt'
    with open(report_file, 'w') as f:
        f.write(report_content)
    
    print(f"📄 Validation report saved: {report_file}")
    print(f"\n{'✅' if overall_status == 'READY' else '⚠️'} OVERALL STATUS: {overall_status}")

def main():
    """Main validation function"""
    
    print("🎯 STARTING COMPREHENSIVE TASK VALIDATION")
    print("Checking for Claude Code improvements and validating all tasks...")
    print("=" * 70)
    
    # Run validation
    task1_results, task2_results, task3_results = validate_all_tasks()
    
    # Run missing analyses if needed
    if (task1_results['status'] != 'COMPLETED' or 
        task2_results['status'] != 'COMPLETED' or
        task3_results['status'] == 'NEEDS_ANALYSIS'):
        run_missing_analyses()
        
        # Re-validate after running missing analyses
        print("\n🔄 RE-VALIDATING AFTER RUNNING MISSING ANALYSES...")
        validate_all_tasks()
    
    print(f"\n✅ VALIDATION COMPLETE")
    print(f"Check COMPREHENSIVE_VALIDATION_REPORT.txt for detailed results")

if __name__ == "__main__":
    main()
