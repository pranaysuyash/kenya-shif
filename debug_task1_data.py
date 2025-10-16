#!/usr/bin/env python3
"""
Debug Task 1 empty tables issue
"""
import json
import pandas as pd
from pathlib import Path

print("=== DEBUGGING TASK 1 EMPTY TABLES ===")
print()

# Check what data is available
data_file = Path("outputs/shif_healthcare_pattern_complete_analysis.json")
if data_file.exists():
    print(f"✅ Loading data from: {data_file}")
    
    with open(data_file) as f:
        data = json.load(f)
    
    print(f"📊 Available keys: {list(data.keys())}")
    
    # Check structured_rules specifically
    if 'structured_rules' in data:
        rules = data['structured_rules']
        print(f"📋 structured_rules: {len(rules)} rules")
        
        if rules:
            # Examine first rule
            first_rule = rules[0]
            print(f"📋 First rule keys: {list(first_rule.keys())}")
            print(f"📋 First rule sample:")
            for key, value in first_rule.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"   {key}: {value[:100]}...")
                else:
                    print(f"   {key}: {value}")
            
            print()
            print("🔍 CHECKING FOR DISPLAY ISSUES:")
            
            # Check the fields that the display expects
            expected_fields = ['service_name', 'rule_type', 'facility_level', 'tariff_amount', 'payment_method', 'conditions', 'exclusions']
            
            field_availability = {}
            for field in expected_fields:
                available_count = sum(1 for rule in rules if field in rule and rule[field])
                field_availability[field] = available_count
                print(f"   {field}: {available_count}/{len(rules)} rules have this field")
            
            # Check if all fields are missing or empty
            all_empty_fields = [field for field, count in field_availability.items() if count == 0]
            if all_empty_fields:
                print(f"⚠️  Fields that are empty in ALL rules: {all_empty_fields}")
            
            print()
            print("🎯 CREATING SAMPLE DISPLAY DATA:")
            
            # Simulate what the display logic does
            display_rules = []
            for rule in rules[:5]:  # Show first 5 for debugging
                display_rule = {
                    'Service Name': rule.get('service_name', '')[:50] + '...' if len(rule.get('service_name', '')) > 50 else rule.get('service_name', ''),
                    'Rule Type': rule.get('rule_type', ''),
                    'Facility Level': rule.get('facility_level', ''),
                    'Tariff Amount': f"KES {rule.get('tariff_amount', 0):,.0f}" if rule.get('tariff_amount') else 'N/A',
                    'Payment Method': rule.get('payment_method', ''),
                    'Conditions Count': len(rule.get('conditions', [])),
                    'Exclusions Count': len(rule.get('exclusions', []))
                }
                display_rules.append(display_rule)
                print(f"   Rule {len(display_rules)}: {display_rule}")
            
            print()
            if any(any(v for v in rule.values() if v not in ['', 'N/A', 0]) for rule in display_rules):
                print("✅ Display data looks populated!")
            else:
                print("❌ All display data appears empty - this explains the empty tables!")
                
        else:
            print("❌ structured_rules is empty!")
    else:
        print("❌ No structured_rules key found!")
        
else:
    print(f"❌ Data file not found: {data_file}")