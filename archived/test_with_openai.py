#!/usr/bin/env python3
"""
Test SHIF analyzer with working OpenAI API key
"""

import os
import sys

# Set the API key
os.environ['OPENAI_API_KEY'] = '"OPENAI_API_KEY_REMOVED"'

# Import the analyzer
from shif_analyzer import parse_pdf_with_pdfplumber, detect_contradictions_v2, detect_gaps_with_yaml

def test_openai_extraction():
    """Test extraction with OpenAI enabled"""
    
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF not found at {pdf_path}")
        return
    
    print("=== Testing SHIF Analyzer with OpenAI ===")
    print(f"API Key set: {'OPENAI_API_KEY' in os.environ}")
    
    try:
        # Run analysis with OpenAI enhancement
        print("\n1. Extracting rules with OpenAI enhancement...")
        rules_df = parse_pdf_with_pdfplumber(
            pdf_path, 
            openai_key=os.environ.get('OPENAI_API_KEY'),
            openai_mode='auto'  # Use OpenAI when regex is uncertain
        )
        
        print(f"   Total rules extracted: {len(rules_df)}")
        
        # Check extraction methods used
        if 'extraction_method' in rules_df.columns:
            method_counts = rules_df['extraction_method'].value_counts()
            print("   Extraction methods used:")
            for method, count in method_counts.items():
                print(f"     {method}: {count}")
        
        # Look for specific improvements
        print("\n2. Analyzing extraction quality...")
        
        # Unit extraction success rate
        units_specified = rules_df[rules_df['tariff_unit'] != 'unspecified'].shape[0]
        unit_success_rate = (units_specified / len(rules_df)) * 100 if len(rules_df) > 0 else 0
        print(f"   Unit extraction success: {unit_success_rate:.1f}% ({units_specified}/{len(rules_df)})")
        
        # Service categorization
        if 'category' in rules_df.columns:
            category_counts = rules_df['category'].value_counts()
            print("   Services by category:")
            for category, count in category_counts.items():
                print(f"     {category}: {count}")
        
        # Check for dialysis rules specifically
        dialysis_rules = rules_df[rules_df['service'].str.contains('dialysis', case=False, na=False)]
        print(f"\n   Dialysis rules found: {len(dialysis_rules)}")
        
        if len(dialysis_rules) > 0:
            print("   Sample dialysis extractions:")
            for idx, rule in dialysis_rules.head(3).iterrows():
                print(f"     - {rule['service'][:50]}...")
                print(f"       Tariff: {rule['tariff']}, Unit: {rule['tariff_unit']}")
                print(f"       Method: {rule.get('extraction_method', 'unknown')}")
        
        # Save enhanced results
        rules_df.to_csv('rules_with_openai.csv', index=False)
        print(f"\n   Enhanced results saved to: rules_with_openai.csv")
        
        return rules_df
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_openai_extraction()
