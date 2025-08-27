#!/usr/bin/env python3
"""
Final assessment of missed rules and recommendations for improvement
"""

import pandas as pd
import os
import json

def final_assessment():
    """Provide final assessment of what rules are being missed"""
    
    print("=== FINAL ASSESSMENT: MISSED RULES AND IMPROVEMENTS ===")
    
    # Check if we have comparison results
    comparison_files = [
        'extraction_comparison.txt',
        'comprehensive_pdf_analysis.json'
    ]
    
    # Load the most recent extraction results
    latest_results = None
    if os.path.exists('outputs_aiFinal/rules.csv'):
        latest_results = pd.read_csv('outputs_aiFinal/rules.csv')
        print(f"Analyzing AI-enhanced extraction: {len(latest_results)} rules")
    elif os.path.exists('outputs/rules.csv'):
        latest_results = pd.read_csv('outputs/rules.csv')
        print(f"Analyzing regex-only extraction: {len(latest_results)} rules")
    else:
        print("❌ No extraction results found")
        return
    
    # Analyze current extraction patterns
    print(f"\n=== CURRENT EXTRACTION ANALYSIS ===")
    
    if 'category' in latest_results.columns:
        category_counts = latest_results['category'].value_counts()
        print("Services by category:")
        for category, count in category_counts.items():
            print(f"  {category}: {count}")
    
    if 'tariff_unit' in latest_results.columns:
        unit_counts = latest_results['tariff_unit'].value_counts()
        specified_units = len(latest_results[latest_results['tariff_unit'] != 'unspecified'])
        unit_rate = (specified_units / len(latest_results)) * 100
        print(f"\nUnit extraction success: {unit_rate:.1f}% ({specified_units}/{len(latest_results)})")
        print("Most common units:")
        for unit, count in unit_counts.head(5).items():
            print(f"  {unit}: {count}")
    
    # Identify systematic gaps based on healthcare service expectations
    print(f"\n=== SYSTEMATIC GAPS IDENTIFIED ===")
    
    expected_services = {
        'Dental Services': ['dental', 'tooth', 'oral', 'dentist'],
        'Laboratory Tests': ['laboratory', 'lab test', 'blood test', 'specimen'],
        'Preventive Care': ['vaccination', 'screening', 'prevention', 'immunization'],
        'Nutrition Services': ['nutrition', 'dietetic', 'diet', 'nutritionist'],
        'Rehabilitation': ['physiotherapy', 'rehabilitation', 'occupational therapy'],
        'Mental Health Detailed': ['psychiatric', 'psychology', 'counseling', 'therapy'],
        'Chronic Disease Specific': ['diabetes management', 'hypertension care', 'asthma treatment'],
        'Pediatric Services': ['pediatric', 'child health', 'infant', 'newborn'],
        'Elderly Care': ['geriatric', 'elderly', 'senior', 'age-related'],
        'Home Care Services': ['home care', 'community health', 'domiciliary'],
        'Pharmaceutical': ['medicines', 'drugs', 'pharmacy', 'medication'],
        'Medical Equipment': ['medical devices', 'equipment', 'prosthetics', 'orthotics']
    }
    
    # Check current extraction for these service types
    gaps_found = []
    partial_coverage = []
    
    for service_category, keywords in expected_services.items():
        # Check if any current rules contain these keywords
        matches = latest_results[
            latest_results['service'].str.contains('|'.join(keywords), case=False, na=False)
        ]
        
        if len(matches) == 0:
            gaps_found.append(service_category)
        elif len(matches) < 3:  # Minimal coverage
            partial_coverage.append((service_category, len(matches)))
    
    print("Complete gaps (no rules found):")
    for gap in gaps_found:
        print(f"  ❌ {gap}")
    
    print("\nPartial coverage (< 3 rules):")
    for service, count in partial_coverage:
        print(f"  ⚠️  {service}: {count} rule(s)")
    
    # Specific recommendations for improving extraction
    print(f"\n=== SPECIFIC RECOMMENDATIONS FOR IMPROVEMENT ===")
    
    recommendations = [
        {
            'issue': 'Restrictive trigger keywords',
            'solution': 'Expand TRIGGER_KEYWORDS to include comprehensive medical terminology',
            'impact': 'Could capture 30-50% more services'
        },
        {
            'issue': 'Line-by-line processing limitation',
            'solution': 'Implement section-based or paragraph-based processing',
            'impact': 'Better handling of multi-line service descriptions'
        },
        {
            'issue': 'Table processing dependencies',
            'solution': 'Process ALL table content, not just rows with trigger keywords',
            'impact': 'Capture services listed in tables without explicit pricing in each row'
        },
        {
            'issue': 'Missing free/bundled services',
            'solution': 'Add patterns for services without explicit KES amounts',
            'impact': 'Include preventive care and basic services'
        },
        {
            'issue': 'Limited medical terminology coverage',
            'solution': 'Integrate medical terminology databases (ICD-10, SNOMED)',
            'impact': 'Better recognition of medical services and conditions'
        },
        {
            'issue': 'Cross-reference handling',
            'solution': 'Implement logic to follow references to annexes and other sections',
            'impact': 'Capture services defined in separate sections'
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['issue']}")
        print(f"   Solution: {rec['solution']}")
        print(f"   Impact: {rec['impact']}")
    
    # Estimate current extraction completeness
    print(f"\n=== EXTRACTION COMPLETENESS ESTIMATE ===")
    
    # Based on a 54-page comprehensive healthcare policy document
    expected_rule_count = 300  # Reasonable estimate for comprehensive coverage
    current_count = len(latest_results)
    completeness = (current_count / expected_rule_count) * 100
    
    print(f"Current extraction: {current_count} rules")
    print(f"Expected for comprehensive coverage: {expected_rule_count} rules")
    print(f"Estimated completeness: {completeness:.1f}%")
    print(f"Missing approximately: {expected_rule_count - current_count} rules ({100 - completeness:.1f}%)")
    
    # Priority improvements
    print(f"\n=== PRIORITY IMPROVEMENTS ===")
    priority_improvements = [
        "1. Fix OpenAI API integration for intelligent extraction",
        "2. Expand trigger keywords for dental, laboratory, and preventive services", 
        "3. Implement comprehensive table processing",
        "4. Add patterns for free services (KES 0) and bundled services",
        "5. Process entire document sections rather than individual lines",
        "6. Add cross-reference resolution for services defined in annexes"
    ]
    
    for improvement in priority_improvements:
        print(f"  {improvement}")
    
    # Save assessment summary
    assessment_data = {
        'current_rule_count': len(latest_results),
        'estimated_completeness_percent': completeness,
        'complete_gaps': gaps_found,
        'partial_coverage': dict(partial_coverage),
        'priority_recommendations': [rec['solution'] for rec in recommendations],
        'estimated_missing_rules': expected_rule_count - current_count
    }
    
    with open('final_assessment.json', 'w') as f:
        json.dump(assessment_data, f, indent=2)
    
    print(f"\nFinal assessment saved to: final_assessment.json")

if __name__ == "__main__":
    final_assessment()
