#!/usr/bin/env python3
"""
Disease vs Treatment Coverage Gap Analysis for SHIF
Identifies diseases mentioned without corresponding treatment coverage
"""

import pandas as pd
import re
from typing import Dict, List

def analyze_disease_treatment_gaps(rules_df: pd.DataFrame) -> pd.DataFrame:
    """
    Find gaps where diseases are mentioned but treatments are not covered
    This addresses the specific example: "hypertension listed but no treatment coverage"
    """
    
    print("🩺 Disease vs Treatment Coverage Gap Analysis")
    print("=" * 60)
    print("Looking for diseases mentioned without corresponding treatment coverage...")
    
    # Define disease-treatment mappings based on standard medical practice
    disease_treatment_map = {
        'hypertension': {
            'treatments': ['antihypertensive', 'blood pressure medication', 'ace inhibitor', 'diuretic', 'bp drugs', 'losartan', 'amlodipine'],
            'severity': 'CRITICAL',
            'description': 'High blood pressure requiring ongoing medication'
        },
        'diabetes': {
            'treatments': ['insulin', 'metformin', 'diabetic medication', 'glucose strips', 'glucometer', 'oral hypoglycemic'],
            'severity': 'CRITICAL', 
            'description': 'Blood sugar disorder requiring medication and monitoring'
        },
        'asthma': {
            'treatments': ['bronchodilator', 'inhaler', 'salbutamol', 'steroid inhaler', 'nebulizer', 'ventolin'],
            'severity': 'HIGH',
            'description': 'Respiratory condition requiring rescue and controller medications'
        },
        'tuberculosis': {
            'treatments': ['anti-tb', 'rifampicin', 'isoniazid', 'ethambutol', 'pyrazinamide', 'tb treatment'],
            'severity': 'CRITICAL',
            'description': 'Infectious disease requiring specific antibiotic regimen'
        },
        'epilepsy': {
            'treatments': ['anticonvulsant', 'phenytoin', 'carbamazepine', 'sodium valproate', 'epilepsy drugs'],
            'severity': 'HIGH',
            'description': 'Neurological condition requiring ongoing medication'
        },
        'depression': {
            'treatments': ['antidepressant', 'counseling', 'therapy', 'psychiatric medication', 'ssri'],
            'severity': 'HIGH',
            'description': 'Mental health condition requiring medication and/or therapy'
        },
        'malaria': {
            'treatments': ['antimalarial', 'artemether', 'quinine', 'coartem', 'malaria treatment', 'act'],
            'severity': 'CRITICAL',
            'description': 'Parasitic infection requiring specific antimalarial drugs'
        }
    }
    
    gaps = []
    
    for disease, info in disease_treatment_map.items():
        treatments = info['treatments']
        severity = info['severity']
        description = info['description']
        
        print(f"\n📋 Analyzing: {disease.upper()}")
        
        # Find disease mentions
        disease_pattern = rf'\b{re.escape(disease)}\b'
        disease_mentions = rules_df[rules_df['service'].str.contains(disease_pattern, case=False, na=False)]
        
        print(f"   Disease mentions: {len(disease_mentions)}")
        
        # Show where disease is mentioned
        if len(disease_mentions) > 0:
            print(f"   Found on pages: {sorted(disease_mentions['source_page'].unique())}")
            for _, rule in disease_mentions.head(2).iterrows():
                print(f"     - Page {rule['source_page']}: {rule['service'][:80]}...")
        
        # Find treatment coverage
        treatment_matches = []
        treatments_found = []
        
        for treatment in treatments:
            treatment_pattern = rf'\b{re.escape(treatment)}\b'
            matches = rules_df[rules_df['service'].str.contains(treatment_pattern, case=False, na=False)]
            if len(matches) > 0:
                treatment_matches.extend(matches.to_dict('records'))
                treatments_found.append(treatment)
        
        # Remove duplicates
        unique_treatments = []
        seen_services = set()
        for treatment in treatment_matches:
            service = treatment['service']
            if service not in seen_services:
                unique_treatments.append(treatment)
                seen_services.add(service)
        
        print(f"   Treatment coverage: {len(unique_treatments)} unique treatment rules")
        
        if treatments_found:
            print(f"   Treatments found: {', '.join(treatments_found[:3])}")
            for treatment in unique_treatments[:2]:
                print(f"     - Page {treatment['source_page']}: {treatment['service'][:80]}...")
        
        # Identify gap
        gap_status = "NONE"
        
        if len(disease_mentions) > 0 and len(unique_treatments) == 0:
            gap_status = "CRITICAL_GAP"
            gap_desc = f"Disease '{disease}' mentioned in benefits but no corresponding treatment coverage found"
            
        elif len(disease_mentions) > 0 and len(unique_treatments) < 2:
            gap_status = "PARTIAL_GAP" 
            gap_desc = f"Disease '{disease}' mentioned but limited treatment options ({len(unique_treatments)} found)"
            
        elif len(disease_mentions) == 0 and len(unique_treatments) > 0:
            gap_status = "ORPHAN_TREATMENTS"
            gap_desc = f"Treatments available for '{disease}' but disease not explicitly covered in benefits"
            
        if gap_status != "NONE":
            gaps.append({
                'disease': disease.title(),
                'gap_type': gap_status,
                'disease_mentions': len(disease_mentions),
                'treatment_rules': len(unique_treatments),
                'severity': severity,
                'description': gap_desc,
                'medical_context': description,
                'sample_disease_page': disease_mentions.iloc[0]['source_page'] if len(disease_mentions) > 0 else None,
                'sample_treatment_page': unique_treatments[0]['source_page'] if unique_treatments else None,
                'treatments_available': ', '.join(treatments_found[:3]) if treatments_found else 'None'
            })
            
            print(f"   ❌ {gap_status}: {gap_desc}")
        else:
            print(f"   ✅ Coverage appears adequate")
    
    return pd.DataFrame(gaps)

def main():
    """Run disease-treatment gap analysis"""
    print("🩺 SHIF Disease-Treatment Coverage Gap Analysis")
    print("=" * 60)
    
    # Load rules
    rules_df = pd.read_csv('outputs_comprehensive/rules_comprehensive.csv')
    print(f"📊 Analyzing {len(rules_df)} healthcare rules for disease-treatment gaps")
    
    # Perform analysis
    gaps_df = analyze_disease_treatment_gaps(rules_df)
    
    if not gaps_df.empty:
        # Save results
        gaps_df.to_csv('outputs_comprehensive/disease_treatment_gaps.csv', index=False)
        
        print(f"\n📊 SUMMARY")
        print(f"=" * 30)
        print(f"Total disease-treatment gaps found: {len(gaps_df)}")
        
        # Break down by gap type
        print(f"\n📋 Gaps by type:")
        for gap_type, count in gaps_df['gap_type'].value_counts().items():
            print(f"   {gap_type}: {count}")
        
        print(f"\n📋 Gaps by severity:")
        for severity, count in gaps_df['severity'].value_counts().items():
            print(f"   {severity}: {count}")
        
        # Show critical gaps (diseases mentioned but no treatment)
        critical_gaps = gaps_df[gaps_df['gap_type'] == 'CRITICAL_GAP']
        if not critical_gaps.empty:
            print(f"\n🚨 CRITICAL GAPS - Diseases Listed Without Treatment Coverage:")
            print("   (This directly addresses the assignment example)")
            for _, gap in critical_gaps.iterrows():
                print(f"\n   • {gap['disease']}:")
                print(f"     - Medical context: {gap['medical_context']}")
                print(f"     - Disease mentioned: {gap['disease_mentions']} times")
                print(f"     - Treatment coverage: {gap['treatment_rules']} rules")
                print(f"     - Found on page: {gap['sample_disease_page']}")
                print(f"     - Recommendation: Add comprehensive {gap['disease'].lower()} treatment coverage")
        
        # Show partial gaps
        partial_gaps = gaps_df[gaps_df['gap_type'] == 'PARTIAL_GAP']
        if not partial_gaps.empty:
            print(f"\n⚠️ PARTIAL GAPS - Limited Treatment Options:")
            for _, gap in partial_gaps.iterrows():
                print(f"   • {gap['disease']}: {gap['treatment_rules']} treatment(s) found")
                print(f"     Available: {gap['treatments_available']}")
        
        print(f"\n💾 Detailed results saved to: outputs_comprehensive/disease_treatment_gaps.csv")
        
    else:
        print("\nℹ️ No disease-treatment gaps identified")
    
    print(f"\n✅ Disease-Treatment Gap Analysis Complete")

if __name__ == "__main__":
    main()