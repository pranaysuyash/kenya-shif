#!/usr/bin/env python3
"""
Comprehensive Gap Analysis for SHIF Healthcare Coverage
Identifies missing services and coverage gaps
"""

import pandas as pd
import yaml
from typing import List, Dict

def comprehensive_gap_analysis(rules_df: pd.DataFrame) -> pd.DataFrame:
    """Perform comprehensive gap analysis"""
    print("🔍 Comprehensive SHIF Gap Analysis")
    print("=" * 50)
    
    gaps = []
    
    # 1. Essential medical services gap analysis
    essential_services = {
        'Infectious Diseases': ['tuberculosis', 'malaria', 'hepatitis', 'typhoid'],
        'Chronic Diseases': ['diabetes', 'hypertension', 'asthma', 'copd'],
        'Preventive Care': ['vaccination', 'immunization', 'screening', 'check-up'],
        'Dental Care': ['dental', 'oral health', 'dentist', 'tooth'],
        'Eye Care': ['optometry', 'ophthalmology', 'eye exam', 'vision'],
        'Mental Health': ['psychiatry', 'psychology', 'counseling', 'mental'],
        'Rehabilitation': ['physiotherapy', 'occupational therapy', 'speech therapy'],
        'Specialty Care': ['cardiology', 'neurology', 'dermatology', 'endocrinology']
    }
    
    print("📋 Essential Services Coverage Analysis:")
    for category, services in essential_services.items():
        print(f"\n{category}:")
        category_coverage = 0
        
        for service in services:
            matches = rules_df[rules_df['service'].str.contains(service, case=False, na=False)]
            coverage_count = len(matches)
            category_coverage += coverage_count
            
            print(f"  {service.title()}: {coverage_count} rules")
            
            if coverage_count == 0:
                gaps.append({
                    'gap_type': 'Missing_Essential_Service',
                    'category': category,
                    'service': service.title(),
                    'description': f'No {service} services found in benefits package',
                    'severity': 'HIGH',
                    'recommendation': f'Add comprehensive {service} coverage'
                })
        
        if category_coverage < 5:
            print(f"  ⚠️ LOW COVERAGE: Only {category_coverage} total services in {category}")
    
    # 2. Facility level coverage gaps
    print(f"\n🏥 Facility Level Coverage Gaps:")
    facility_gaps = []
    
    for level in range(1, 7):
        level_rules = rules_df[rules_df['facility_levels'].str.contains(str(level), na=False)]
        service_count = len(level_rules)
        
        print(f"  Level {level}: {service_count} services")
        
        if service_count < 20:
            facility_gaps.append({
                'gap_type': 'Facility_Coverage_Gap',
                'category': f'Level {level} Facilities',
                'service': f'Level {level} Service Coverage',
                'description': f'Only {service_count} services available at Level {level} facilities',
                'severity': 'MEDIUM' if service_count > 10 else 'HIGH',
                'recommendation': f'Expand service availability at Level {level} facilities'
            })
    
    gaps.extend(facility_gaps)
    
    # 3. Tariff coverage gaps
    print(f"\n💰 Tariff Coverage Analysis:")
    rules_with_tariffs = rules_df[rules_df['tariff'].notna() & (rules_df['tariff'] > 0)]
    tariff_coverage = len(rules_with_tariffs) / len(rules_df) * 100
    
    print(f"  Services with tariffs: {len(rules_with_tariffs)}/{len(rules_df)} ({tariff_coverage:.1f}%)")
    
    if tariff_coverage < 80:
        gaps.append({
            'gap_type': 'Tariff_Documentation_Gap',
            'category': 'Pricing Information',
            'service': 'Service Tariff Documentation',
            'description': f'Only {tariff_coverage:.1f}% of services have documented tariffs',
            'severity': 'HIGH',
            'recommendation': 'Complete tariff documentation for all covered services'
        })
    
    # 4. High-priority medical conditions
    print(f"\n🚨 High-Priority Condition Coverage:")
    priority_conditions = [
        'emergency', 'trauma', 'cardiac arrest', 'stroke', 'pregnancy complications',
        'cancer', 'kidney failure', 'respiratory failure'
    ]
    
    for condition in priority_conditions:
        matches = rules_df[rules_df['service'].str.contains(condition, case=False, na=False)]
        coverage_count = len(matches)
        
        print(f"  {condition.title()}: {coverage_count} rules")
        
        if coverage_count == 0:
            gaps.append({
                'gap_type': 'Critical_Condition_Gap',
                'category': 'Emergency/Critical Care',
                'service': condition.title(),
                'description': f'No coverage found for {condition}',
                'severity': 'CRITICAL',
                'recommendation': f'Ensure comprehensive {condition} coverage'
            })
    
    # 5. Demographic-specific gaps
    print(f"\n👥 Demographic Coverage Analysis:")
    demographics = ['pediatric', 'geriatric', 'maternal', 'adolescent']
    
    for demographic in demographics:
        matches = rules_df[rules_df['service'].str.contains(demographic, case=False, na=False)]
        coverage_count = len(matches)
        
        print(f"  {demographic.title()}: {coverage_count} rules")
        
        if coverage_count < 5:
            gaps.append({
                'gap_type': 'Demographic_Coverage_Gap',
                'category': 'Population-Specific Care',
                'service': f'{demographic.title()} Care',
                'description': f'Limited {demographic} care services ({coverage_count} rules)',
                'severity': 'MEDIUM',
                'recommendation': f'Expand {demographic}-specific healthcare services'
            })
    
    return pd.DataFrame(gaps)

def main():
    """Run comprehensive gap analysis"""
    print("🔍 SHIF Comprehensive Gap Analysis")
    print("=" * 50)
    
    # Load rules
    rules_df = pd.read_csv('outputs_comprehensive/rules_comprehensive.csv')
    print(f"📊 Analyzing {len(rules_df)} healthcare rules")
    
    # Perform gap analysis
    gaps_df = comprehensive_gap_analysis(rules_df)
    
    # Save results
    if not gaps_df.empty:
        gaps_df.to_csv('outputs_comprehensive/comprehensive_gaps.csv', index=False)
        
        print(f"\n✅ Identified {len(gaps_df)} coverage gaps")
        
        # Show gap summary
        print(f"\n📊 Gaps by Type:")
        for gap_type, count in gaps_df['gap_type'].value_counts().items():
            print(f"  {gap_type}: {count}")
        
        print(f"\n📊 Gaps by Severity:")
        for severity, count in gaps_df['severity'].value_counts().items():
            print(f"  {severity}: {count}")
        
        # Show critical gaps
        critical_gaps = gaps_df[gaps_df['severity'] == 'CRITICAL']
        if not critical_gaps.empty:
            print(f"\n🚨 CRITICAL GAPS:")
            for _, gap in critical_gaps.iterrows():
                print(f"  {gap['service']}: {gap['description']}")
                print(f"    Recommendation: {gap['recommendation']}")
                print()
        
        # Show high priority gaps
        high_gaps = gaps_df[gaps_df['severity'] == 'HIGH']
        if not high_gaps.empty:
            print(f"\n⚠️ HIGH PRIORITY GAPS:")
            for _, gap in high_gaps.head(5).iterrows():
                print(f"  {gap['service']}: {gap['description']}")
    else:
        print("ℹ️ No significant gaps identified")
    
    print(f"\n✅ Gap Analysis Complete")

if __name__ == "__main__":
    main()