#!/usr/bin/env python3
"""
Compare original vs enhanced extraction results
"""

import pandas as pd
import os
from collections import Counter

def compare_extraction_results():
    """Compare all extraction approaches"""
    
    print("=== COMPREHENSIVE EXTRACTION COMPARISON ===")
    
    # Define all possible output locations
    extraction_results = {
        'Original (Regex-only)': 'outputs/rules.csv',
        'AI Enhanced': 'outputs_aiFinal/rules.csv', 
        'Comprehensive Enhanced': 'outputs_comprehensive/rules_comprehensive.csv'
    }
    
    comparison_data = {}
    
    for name, path in extraction_results.items():
        if os.path.exists(path):
            df = pd.read_csv(path)
            comparison_data[name] = {
                'dataframe': df,
                'count': len(df),
                'path': path
            }
            print(f"✅ {name}: {len(df)} rules")
        else:
            print(f"❌ {name}: File not found at {path}")
    
    if len(comparison_data) < 2:
        print("Need at least 2 datasets for comparison")
        return
    
    # Detailed comparison
    print(f"\n=== DETAILED COMPARISON ===")
    
    for name, data in comparison_data.items():
        df = data['dataframe']
        count = data['count']
        
        print(f"\n{name} ({count} rules):")
        
        # Category breakdown
        if 'category' in df.columns:
            category_counts = df['category'].value_counts()
            print("  Categories:")
            for cat, cnt in category_counts.head(8).items():
                print(f"    {cat}: {cnt}")
        
        # Unit extraction success
        if 'tariff_unit' in df.columns:
            specified_units = df[df['tariff_unit'] != 'unspecified'].shape[0]
            unit_rate = (specified_units / count) * 100 if count > 0 else 0
            print(f"  Unit extraction: {unit_rate:.1f}% ({specified_units}/{count})")
        
        # Extraction methods (if available)
        if 'extraction_method' in df.columns:
            method_counts = df['extraction_method'].value_counts()
            print("  Methods:")
            for method, cnt in method_counts.items():
                print(f"    {method}: {cnt}")
        
        # Check for key service types we were missing
        key_services = {
            'dental': ['dental', 'tooth', 'oral'],
            'laboratory': ['laboratory', 'lab', 'test', 'specimen'],
            'vaccination': ['vaccination', 'vaccine', 'immunization'],
            'pharmaceutical': ['medicine', 'medication', 'drug', 'pharmacy'],
            'nutrition': ['nutrition', 'diet', 'nutritionist'],
            'rehabilitation': ['physiotherapy', 'rehabilitation', 'physio']
        }
        
        print("  Key service coverage:")
        for service_type, keywords in key_services.items():
            matches = df[df['service'].str.contains('|'.join(keywords), case=False, na=False)]
            print(f"    {service_type}: {len(matches)} rules")
    
    # Show improvements
    if len(comparison_data) >= 2:
        datasets = list(comparison_data.keys())
        baseline = comparison_data[datasets[0]]
        
        for i in range(1, len(datasets)):
            enhanced = comparison_data[datasets[i]]
            improvement = enhanced['count'] - baseline['count']
            pct_improvement = (improvement / baseline['count']) * 100
            
            print(f"\n📈 {datasets[i]} vs {datasets[0]}:")
            print(f"   Additional rules: +{improvement} ({pct_improvement:.1f}% improvement)")
    
    # Create summary report
    with open('extraction_evolution_report.txt', 'w') as f:
        f.write("SHIF ANALYZER EXTRACTION EVOLUTION\n")
        f.write("="*50 + "\n\n")
        
        for name, data in comparison_data.items():
            f.write(f"{name}: {data['count']} rules\n")
        
        if len(comparison_data) >= 2:
            datasets = list(comparison_data.keys())
            baseline_count = comparison_data[datasets[0]]['count']
            final_count = comparison_data[datasets[-1]]['count']
            total_improvement = final_count - baseline_count
            total_pct = (total_improvement / baseline_count) * 100
            
            f.write(f"\nTotal Evolution: {baseline_count} → {final_count} rules\n")
            f.write(f"Net Improvement: +{total_improvement} rules ({total_pct:.1f}%)\n")
    
    print(f"\nExtraction evolution report saved: extraction_evolution_report.txt")

if __name__ == "__main__":
    compare_extraction_results()
