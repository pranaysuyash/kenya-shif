#!/usr/bin/env python3
"""
Compare extraction results between regex-only and AI-enhanced
"""

import pandas as pd
import os

def compare_extraction_results():
    """Compare the two extraction outputs"""
    
    original_path = "outputs/rules.csv"  
    ai_path = "outputs_aiFinal/rules.csv"
    
    if not os.path.exists(original_path) or not os.path.exists(ai_path):
        print("❌ Missing comparison files")
        return
    
    print("=== EXTRACTION COMPARISON ANALYSIS ===")
    
    # Load both datasets
    original_df = pd.read_csv(original_path)
    ai_df = pd.read_csv(ai_path)
    
    print(f"Original (regex-only): {len(original_df)} rules")
    print(f"AI-enhanced: {len(ai_df)} rules")
    print(f"Difference: {len(ai_df) - len(original_df)} rules ({((len(ai_df) - len(original_df)) / len(original_df) * 100):.1f}%)")
    
    # Check extraction methods if available
    if 'extraction_method' in ai_df.columns:
        method_counts = ai_df['extraction_method'].value_counts()
        print("\nExtraction methods used:")
        for method, count in method_counts.items():
            print(f"  {method}: {count}")
    
    # Check unit extraction improvement
    if 'tariff_unit' in ai_df.columns:
        original_units = original_df[original_df['tariff_unit'] != 'unspecified'].shape[0]
        ai_units = ai_df[ai_df['tariff_unit'] != 'unspecified'].shape[0]
        
        orig_rate = (original_units / len(original_df)) * 100 if len(original_df) > 0 else 0
        ai_rate = (ai_units / len(ai_df)) * 100 if len(ai_df) > 0 else 0
        
        print(f"\nUnit extraction success:")
        print(f"  Original: {orig_rate:.1f}% ({original_units}/{len(original_df)})")
        print(f"  AI-enhanced: {ai_rate:.1f}% ({ai_units}/{len(ai_df)})")
        print(f"  Improvement: {ai_rate - orig_rate:.1f} percentage points")
    
    # Check service categories
    if 'category' in ai_df.columns:
        print(f"\nService categories in AI-enhanced:")
        category_counts = ai_df['category'].value_counts()
        for category, count in category_counts.items():
            print(f"  {category}: {count}")
    
    # Look for new types of rules captured
    if len(ai_df) > len(original_df):
        print(f"\n=== NEWLY CAPTURED RULES (sample) ===")
        # This is approximate - would need more sophisticated matching
        print("Sample of potentially new extractions:")
        for idx, row in ai_df.tail(5).iterrows():
            print(f"  • {row['service'][:60]}...")
            print(f"    Tariff: {row['tariff']}, Unit: {row['tariff_unit']}")
            print(f"    Method: {row.get('extraction_method', 'unknown')}")
    
    # Check for specific medical categories that might be better captured
    medical_categories = ['dental', 'laboratory', 'vaccination', 'physiotherapy', 'nutrition']
    
    print(f"\n=== MEDICAL CATEGORY ANALYSIS ===")
    for category in medical_categories:
        # Check services that might contain these terms
        orig_matches = original_df[original_df['service'].str.contains(category, case=False, na=False)].shape[0]
        ai_matches = ai_df[ai_df['service'].str.contains(category, case=False, na=False)].shape[0]
        
        if orig_matches > 0 or ai_matches > 0:
            print(f"{category.capitalize()}:")
            print(f"  Original: {orig_matches}, AI-enhanced: {ai_matches}")
    
    # Save comparison summary
    with open('extraction_comparison.txt', 'w') as f:
        f.write("SHIF EXTRACTION COMPARISON SUMMARY\n")
        f.write("="*50 + "\n\n")
        f.write(f"Original rules: {len(original_df)}\n")
        f.write(f"AI-enhanced rules: {len(ai_df)}\n")
        f.write(f"Improvement: {len(ai_df) - len(original_df)} additional rules\n\n")
        
        if 'extraction_method' in ai_df.columns:
            f.write("Extraction methods:\n")
            for method, count in method_counts.items():
                f.write(f"  {method}: {count}\n")
    
    print(f"\nComparison summary saved to: extraction_comparison.txt")

if __name__ == "__main__":
    compare_extraction_results()
