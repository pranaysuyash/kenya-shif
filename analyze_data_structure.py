#!/usr/bin/env python3
"""
Analyze the actual data structure to fix field mappings
"""
import json
from pathlib import Path

print("=== ANALYZING ACTUAL DATA STRUCTURE ===")
print()

# Load the data
data_file = Path("outputs/shif_healthcare_pattern_complete_analysis.json")
with open(data_file) as f:
    data = json.load(f)

print("📊 TOP LEVEL KEYS:")
for key in data.keys():
    if isinstance(data[key], list):
        print(f"   {key}: list with {len(data[key])} items")
    elif isinstance(data[key], dict):
        print(f"   {key}: dict with {len(data[key])} keys")
    else:
        print(f"   {key}: {type(data[key])}")

print()
print("🔍 TASK 1 STRUCTURED RULES:")
task1_rules = data.get('task1_structured_rules', [])
if task1_rules:
    print(f"   Count: {len(task1_rules)}")
    sample_rule = task1_rules[0]
    print(f"   Sample rule fields: {list(sample_rule.keys())}")
    print(f"   Sample values:")
    for key, value in sample_rule.items():
        if isinstance(value, str) and len(value) > 50:
            print(f"      {key}: '{value[:50]}...'")
        else:
            print(f"      {key}: {value}")

print()
print("🔍 TASK 2 CONTRADICTIONS & GAPS:")
contradictions = data.get('task2_contradictions', [])
gaps = data.get('task2_gaps', [])
print(f"   Contradictions: {len(contradictions)}")
print(f"   Gaps: {len(gaps)}")
if contradictions:
    print(f"   Sample contradiction fields: {list(contradictions[0].keys())}")
if gaps:
    print(f"   Sample gap fields: {list(gaps[0].keys())}")

print()
print("🔍 TASK 3 CONTEXT ANALYSIS:")
context = data.get('task3_context_analysis', {})
if context:
    print(f"   Context keys: {list(context.keys())}")
    
print()
print("🔍 TASK 4 DASHBOARD:")
dashboard = data.get('task4_dashboard', {})
if dashboard:
    print(f"   Dashboard keys: {list(dashboard.keys())}")

print()
print("🔍 EXTRACTION RESULTS:")
extraction = data.get('extraction_results', {})
if extraction:
    print(f"   Extraction keys: {list(extraction.keys())}")
    
print()
print("💡 MAPPING REQUIREMENTS:")
print("   Current display expects: service_name, rule_type, facility_level, tariff_amount, payment_method")
print("   Actual data has: ", list(task1_rules[0].keys()) if task1_rules else "No data")

print()
print("🎯 FIELD MAPPING STRATEGY:")
if task1_rules:
    actual_fields = task1_rules[0].keys()
    mapping_suggestions = {
        'service_name': None,
        'rule_type': None, 
        'facility_level': None,
        'tariff_amount': None,
        'payment_method': None
    }
    
    # Try to find best matches
    for expected in mapping_suggestions.keys():
        for actual in actual_fields:
            if expected.lower() in actual.lower() or actual.lower() in expected.lower():
                mapping_suggestions[expected] = actual
                break
    
    # Manual mappings based on context
    if 'service' in actual_fields:
        mapping_suggestions['service_name'] = 'service'
    if 'access_point' in actual_fields:
        mapping_suggestions['facility_level'] = 'access_point'  
    if 'item_tariff' in actual_fields or 'block_tariff' in actual_fields:
        mapping_suggestions['tariff_amount'] = 'item_tariff'
    if 'mapping_type' in actual_fields:
        mapping_suggestions['rule_type'] = 'mapping_type'
        
    print("   Suggested mappings:")
    for expected, actual in mapping_suggestions.items():
        print(f"      {expected} -> {actual}")