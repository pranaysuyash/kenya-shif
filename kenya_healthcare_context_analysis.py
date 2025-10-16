#!/usr/bin/env python3
"""
Enhanced SHIF Analysis with Kenya Healthcare Context
Incorporates broader understanding of Kenya's healthcare system and SHIF-specific constructs
"""

import pandas as pd
import re
from typing import Dict, List

def analyze_with_kenya_context(rules_df: pd.DataFrame, annex_df: pd.DataFrame = None) -> Dict:
    """
    Enhanced analysis incorporating Kenya's healthcare system knowledge
    """
    
    print("🇰🇪 Enhanced SHIF Analysis with Kenya Healthcare Context")
    print("=" * 65)
    
    analysis_results = {
        'facility_level_analysis': {},
        'payment_mechanism_analysis': {},
        'coverage_gaps_by_kenyan_standards': {},
        'shif_specific_findings': {},
        'policy_recommendations': []
    }
    
    # 1. FACILITY LEVEL ANALYSIS (Kenya's 1-6 System)
    print("🏥 FACILITY LEVEL ANALYSIS (Kenya's 1-6 Healthcare System)")
    print("-" * 60)
    
    kenya_facility_levels = {
        1: {
            'name': 'Community Health Services',
            'description': 'Community-Based Health Workers (CHVs), serving ~5,000 people',
            'expected_services': ['vaccination', 'health education', 'first aid', 'basic sanitation'],
            'governance': 'Community Health Committees'
        },
        2: {
            'name': 'Dispensaries/Primary Care', 
            'description': 'Run by Clinical Officers, no inpatient services',
            'expected_services': ['outpatient', 'laboratory', 'pharmacy', 'basic care'],
            'governance': 'Sub-county health management teams'
        },
        3: {
            'name': 'Health Centers',
            'description': 'Run by doctors with inpatient services',
            'expected_services': ['dental', 'x-ray', 'diabetes care', 'maternity'],
            'governance': 'County level'
        },
        4: {
            'name': 'Sub-County/Sub-District Hospitals',
            'description': 'Primary referral hospitals, specialized services',
            'expected_services': ['comprehensive care', 'surgery', 'specialized clinics'],
            'governance': 'County/SHIF overlap'
        },
        5: {
            'name': 'County Referral Hospitals',
            'description': 'Former provincial hospitals, 100+ beds',
            'expected_services': ['specialized care', 'teaching', 'comprehensive surgery'],
            'governance': 'County level'
        },
        6: {
            'name': 'National Referral Hospitals',
            'description': 'Specialized treatments for Kenya and East/Central Africa',
            'expected_services': ['oncology', 'cardiothoracic', 'neurosurgery', 'transplants'],
            'governance': 'National government'
        }
    }
    
    # Analyze facility coverage in SHIF
    for level, info in kenya_facility_levels.items():
        level_rules = rules_df[rules_df['facility_levels'].str.contains(str(level), na=False)]
        service_count = len(level_rules)
        
        print(f"\nLevel {level}: {info['name']}")
        print(f"  Services covered: {service_count}")
        print(f"  Expected services: {', '.join(info['expected_services'][:3])}")
        
        # Check for expected services
        missing_services = []
        for expected_service in info['expected_services']:
            matches = level_rules[level_rules['service'].str.contains(expected_service, case=False, na=False)]
            if len(matches) == 0:
                missing_services.append(expected_service)
        
        if missing_services:
            print(f"  ⚠️ Missing expected services: {', '.join(missing_services)}")
        
        analysis_results['facility_level_analysis'][f'level_{level}'] = {
            'services_covered': service_count,
            'missing_services': missing_services,
            'governance': info['governance']
        }
    
    # 2. PAYMENT MECHANISM ANALYSIS (SHIF-specific)
    print(f"\n💰 PAYMENT MECHANISM ANALYSIS")
    print("-" * 40)
    
    # Analyze payment patterns in extracted rules
    payment_patterns = {
        'case_based': r'case\s*based|per\s*case',
        'per_session': r'per\s*session|session',
        'per_diem': r'per\s*diem|daily\s*rate',
        'fee_for_service': r'fee\s*for\s*service|ffs',
        'capitation': r'capitation|per\s*person',
        'package_rate': r'package|bundle'
    }
    
    for mechanism, pattern in payment_patterns.items():
        matches = rules_df[rules_df['raw_text'].str.contains(pattern, case=False, na=False)]
        
        print(f"  {mechanism.replace('_', ' ').title()}: {len(matches)} mentions")
        
        if len(matches) > 0:
            # Sample evidence
            sample = matches.iloc[0]
            print(f"    Example: Page {sample['source_page']} - {sample['service'][:60]}...")
        
        analysis_results['payment_mechanism_analysis'][mechanism] = len(matches)
    
    # 3. SHIF FUND STRUCTURE ANALYSIS
    print(f"\n🏛️ SHIF FUND STRUCTURE ANALYSIS")
    print("-" * 35)
    
    # Analyze coverage across SHIF's three funds
    fund_mappings = {
        'Primary Healthcare Fund (PHF)': {
            'levels': [1, 2, 3, 4],
            'focus': 'outpatient, preventive, primary care'
        },
        'Social Health Insurance Fund (SHIF)': {
            'levels': [4, 5, 6], 
            'focus': 'inpatient, specialized care'
        },
        'Emergency, Chronic, Critical Illness Fund (ECCIF)': {
            'levels': [4, 5, 6],
            'focus': 'emergency, chronic diseases, critical care'
        }
    }
    
    for fund_name, info in fund_mappings.items():
        print(f"\n{fund_name}:")
        
        # Count services by facility levels for this fund
        fund_services = 0
        for level in info['levels']:
            level_services = len(rules_df[rules_df['facility_levels'].str.contains(str(level), na=False)])
            fund_services += level_services
        
        print(f"  Services covered: {fund_services}")
        print(f"  Target levels: {info['levels']}")
        print(f"  Focus areas: {info['focus']}")
        
        analysis_results['shif_specific_findings'][fund_name] = {
            'services_covered': fund_services,
            'target_levels': info['levels']
        }
    
    # 4. KENYAN DISEASE BURDEN ANALYSIS
    print(f"\n🦠 KENYAN DISEASE BURDEN vs SHIF COVERAGE")
    print("-" * 45)
    
    kenya_priority_diseases = {
        'malaria': {'burden': 'HIGH', 'endemic': True, 'expected_coverage': 'Comprehensive'},
        'tuberculosis': {'burden': 'HIGH', 'endemic': True, 'expected_coverage': 'Comprehensive'},
        'hiv/aids': {'burden': 'HIGH', 'endemic': True, 'expected_coverage': 'Comprehensive'},
        'diabetes': {'burden': 'RISING', 'endemic': False, 'expected_coverage': 'Chronic care'},
        'hypertension': {'burden': 'RISING', 'endemic': False, 'expected_coverage': 'Chronic care'},
        'respiratory_infections': {'burden': 'HIGH', 'endemic': True, 'expected_coverage': 'Primary care'},
        'diarrheal_diseases': {'burden': 'HIGH', 'endemic': True, 'expected_coverage': 'Primary care'},
        'maternal_mortality': {'burden': 'HIGH', 'endemic': True, 'expected_coverage': 'Comprehensive'},
        'child_mortality': {'burden': 'HIGH', 'endemic': True, 'expected_coverage': 'Pediatric care'}
    }
    
    coverage_gaps = {}
    
    for disease, info in kenya_priority_diseases.items():
        disease_mentions = rules_df[rules_df['service'].str.contains(disease.replace('_', ' '), case=False, na=False)]
        coverage_count = len(disease_mentions)
        
        print(f"\n{disease.replace('_', ' ').title()}:")
        print(f"  Disease burden: {info['burden']}")
        print(f"  SHIF coverage: {coverage_count} rules")
        print(f"  Expected: {info['expected_coverage']}")
        
        if info['burden'] == 'HIGH' and coverage_count < 5:
            coverage_gaps[disease] = {
                'gap_severity': 'CRITICAL',
                'reason': f"High burden disease with only {coverage_count} coverage rules"
            }
            print(f"  ❌ CRITICAL GAP: High burden disease inadequately covered")
        elif info['burden'] == 'RISING' and coverage_count == 0:
            coverage_gaps[disease] = {
                'gap_severity': 'HIGH',
                'reason': f"Rising burden disease with no coverage"
            }
            print(f"  ⚠️ HIGH PRIORITY GAP: Rising disease burden not addressed")
    
    analysis_results['coverage_gaps_by_kenyan_standards'] = coverage_gaps
    
    # 5. POLICY RECOMMENDATIONS
    print(f"\n📋 POLICY RECOMMENDATIONS FOR SHIF")
    print("-" * 35)
    
    recommendations = []
    
    # Facility level gaps
    level1_services = analysis_results['facility_level_analysis']['level_1']['services_covered']
    if level1_services < 10:
        recommendations.append({
            'priority': 'HIGH',
            'area': 'Community Health',
            'recommendation': f'Strengthen Level 1 community health services (only {level1_services} covered)',
            'justification': 'Community health is foundation of Kenya\'s healthcare pyramid'
        })
    
    # Disease burden gaps
    if len(coverage_gaps) > 3:
        recommendations.append({
            'priority': 'CRITICAL',
            'area': 'Disease Coverage',
            'recommendation': f'Address {len(coverage_gaps)} critical disease coverage gaps',
            'justification': 'High-burden diseases inadequately covered in SHIF benefits'
        })
    
    # Payment mechanism analysis
    case_based_count = analysis_results['payment_mechanism_analysis']['case_based']
    if case_based_count < 10:
        recommendations.append({
            'priority': 'MEDIUM',
            'area': 'Payment Reform',
            'recommendation': 'Expand case-based payment mechanisms for predictable costs',
            'justification': 'Case-based payments improve cost predictability and quality outcomes'
        })
    
    analysis_results['policy_recommendations'] = recommendations
    
    for rec in recommendations:
        print(f"\n{rec['priority']} PRIORITY: {rec['area']}")
        print(f"  Recommendation: {rec['recommendation']}")
        print(f"  Justification: {rec['justification']}")
    
    return analysis_results

def main():
    """Run enhanced analysis with Kenya healthcare context"""
    print("🇰🇪 SHIF Analysis Enhanced with Kenya Healthcare Context")
    print("=" * 65)
    
    # Load data
    rules_df = pd.read_csv('outputs_comprehensive/rules_comprehensive.csv')
    
    try:
        annex_df = pd.read_csv('outputs_comprehensive/annex_tariffs.csv')
    except:
        annex_df = None
    
    print(f"📊 Analyzing {len(rules_df)} SHIF rules with Kenya healthcare context")
    
    # Run enhanced analysis
    results = analyze_with_kenya_context(rules_df, annex_df)
    
    # Save enhanced results
    import json
    with open('outputs_comprehensive/kenya_context_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Enhanced analysis saved to: outputs_comprehensive/kenya_context_analysis.json")
    print(f"\n✅ Kenya Healthcare Context Analysis Complete")

if __name__ == "__main__":
    main()