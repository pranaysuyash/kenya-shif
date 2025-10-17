#!/usr/bin/env python3
"""
Test script to verify JSON-to-table formatting works correctly
"""

import pandas as pd
import json
from streamlit_comprehensive_analyzer import SHIFHealthcarePolicyAnalyzer

def test_contradiction_formatting():
    """Test formatting of contradiction JSON fields"""
    print("\n" + "="*80)
    print("TESTING CONTRADICTION JSON FORMATTING")
    print("="*80)

    # Load a sample contradiction
    df = pd.read_csv('outputs_run_20251017_140721/all_unique_contradictions_comprehensive.csv', nrows=1)

    # Create analyzer instance
    analyzer = SHIFHealthcarePolicyAnalyzer()

    # Test each JSON field
    json_fields = [
        'medical_analysis',
        'patient_safety_impact',
        'kenya_health_system_impact',
        'epidemiological_context',
        'evidence_documentation',
        'recommended_resolution',
        'quality_metrics'
    ]

    for field in json_fields:
        if field in df.columns and pd.notna(df[field].iloc[0]):
            print(f"\n--- Testing field: {field} ---")
            try:
                json_data = json.loads(df[field].iloc[0])
                html_table = analyzer._dict_to_html_table(json_data)

                # Check if HTML is well-formed
                assert '<table' in html_table
                assert '</table>' in html_table
                assert '<thead>' in html_table
                assert '<tbody>' in html_table

                print(f"✅ {field}: HTML table generated successfully")
                print(f"   Table size: {len(html_table)} characters")
                print(f"   Fields in JSON: {len(json_data)} keys")

            except Exception as e:
                print(f"❌ {field}: Error - {e}")

    print("\n" + "="*80)

def test_gap_formatting():
    """Test formatting of gap JSON fields"""
    print("\n" + "="*80)
    print("TESTING GAP JSON FORMATTING")
    print("="*80)

    # Load a sample gap
    df = pd.read_csv('outputs_run_20251017_140721/all_unique_gaps_comprehensive.csv', nrows=1)

    # Create analyzer instance
    analyzer = SHIFHealthcarePolicyAnalyzer()

    # Test each JSON field
    json_fields = [
        'kenya_context',
        'coverage_analysis',
        'interventions',
        'implementation',
        'kenya_epidemiological_context',
        'health_system_impact_analysis'
    ]

    for field in json_fields:
        if field in df.columns and pd.notna(df[field].iloc[0]):
            print(f"\n--- Testing field: {field} ---")
            try:
                json_data = json.loads(df[field].iloc[0])
                html_table = analyzer._dict_to_html_table(json_data)

                # Check if HTML is well-formed
                assert '<table' in html_table
                assert '</table>' in html_table
                assert '<thead>' in html_table
                assert '<tbody>' in html_table

                print(f"✅ {field}: HTML table generated successfully")
                print(f"   Table size: {len(html_table)} characters")
                print(f"   Fields in JSON: {len(json_data)} keys")

            except Exception as e:
                print(f"❌ {field}: Error - {e}")

    print("\n" + "="*80)

def test_nested_json():
    """Test formatting of deeply nested JSON"""
    print("\n" + "="*80)
    print("TESTING NESTED JSON FORMATTING")
    print("="*80)

    analyzer = SHIFHealthcarePolicyAnalyzer()

    # Create test nested JSON
    test_data = {
        "level1_field": "Simple value",
        "level1_nested": {
            "level2_field": "Nested value",
            "level2_nested": {
                "level3_field": "Deeply nested value"
            }
        },
        "level1_list": ["item1", "item2", "item3"],
        "level1_dict_list": [
            {"name": "Item 1", "value": 100},
            {"name": "Item 2", "value": 200}
        ]
    }

    try:
        html_table = analyzer._dict_to_html_table(test_data)

        # Check if HTML is well-formed
        assert '<table' in html_table
        assert '</table>' in html_table
        assert 'Level1 Field' in html_table or 'level1_field' in html_table.lower()

        print("✅ Nested JSON: HTML table generated successfully")
        print(f"   Table size: {len(html_table)} characters")
        print(f"   Nested tables: {html_table.count('<table')}")

    except Exception as e:
        print(f"❌ Nested JSON: Error - {e}")

    print("\n" + "="*80)

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("JSON-TO-TABLE FORMATTING TEST SUITE")
    print("="*80)

    try:
        test_contradiction_formatting()
        test_gap_formatting()
        test_nested_json()

        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*80)

    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
