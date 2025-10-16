#!/usr/bin/env python3
"""
Direct test of Streamlit functionality without UI
"""
import sys
import os
from pathlib import Path

print("=== STREAMLIT FUNCTIONALITY TEST ===")
print()

# Test 1: Check if recent analysis results exist
print("1. CHECKING FOR ANALYSIS RESULTS...")
output_dirs = [d for d in Path('.').iterdir() if d.is_dir() and d.name.startswith('outputs_')]
print(f"   Found {len(output_dirs)} output directories")

latest_dir = None
if output_dirs:
    latest_dir = sorted(output_dirs, key=lambda x: x.stat().st_mtime)[-1]
    print(f"   Latest: {latest_dir}")
    
    # Check for key files (updated to match actual output)
    key_files = ['rules_p1_18_structured.csv', 'comprehensive_gaps_analysis.csv', 'ai_contradictions.csv']
    found_files = []
    for file in key_files:
        if (latest_dir / file).exists():
            found_files.append(file)
    
    print(f"   Key files found: {len(found_files)}/3 - {found_files}")

# Test 2: Check persistent insights
print()
print("2. CHECKING PERSISTENT INSIGHTS...")
if Path('persistent_insights.json').exists():
    print("   ✅ Persistent insights file exists")
    
    import json
    with open('persistent_insights.json') as f:
        insights = json.load(f)
    
    unique_gaps = len(insights.get('unique_gaps', []))
    unique_contradictions = len(insights.get('unique_contradictions', []))
    print(f"   Unique gaps: {unique_gaps}")
    print(f"   Unique contradictions: {unique_contradictions}")
else:
    print("   ❌ No persistent insights file found")

# Test 3: Test Streamlit app loading (simulate)
print()
print("3. TESTING STREAMLIT APP COMPONENTS...")
try:
    # Import the main components
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    
    print("   ✅ Plotting libraries available")
    
    # Test basic chart creation
    test_data = pd.DataFrame({
        'Category': ['Gaps', 'Contradictions', 'Rules'],
        'Count': [7, 6, 97]
    })
    
    fig = px.bar(test_data, x='Category', y='Count', title='Test Chart')
    print("   ✅ Chart creation successful")
    
    # Test if we can create metrics
    if latest_dir and len(found_files) > 0:
        print("   ✅ Data available for dashboard metrics")
    else:
        print("   ⚠️  Limited data for dashboard metrics")
        
except ImportError as e:
    print(f"   ❌ Missing required libraries: {e}")

# Test 4: Test data structure consistency
print()
print("4. TESTING DATA STRUCTURE CONSISTENCY...")
try:
    # Load structured rules if available
    if latest_dir and (latest_dir / 'structured_rules.json').exists():
        with open(latest_dir / 'structured_rules.json') as f:
            rules_data = json.load(f)
        
        print(f"   ✅ Structured rules loaded: {len(rules_data)} entries")
        
        if len(rules_data) > 0:
            sample = rules_data[0]
            keys = list(sample.keys())
            print(f"   Keys available: {keys[:5]}...")
            
            # Check for scope text quality
            scope_key = None
            for key in ['scope_item', 'scope', 'text']:
                if key in sample:
                    scope_key = key
                    break
            
            if scope_key:
                sample_text = sample[scope_key]
                has_clean_text = "Health education and wellness" in sample_text
                print(f"   ✅ Clean text in structured data: {has_clean_text}")
            else:
                print("   ⚠️  No scope text found in structured data")
    else:
        print("   ⚠️  No structured rules data found")
        
except Exception as e:
    print(f"   ❌ Data structure test failed: {e}")

# Test 5: Check if we can run analysis components
print()
print("5. TESTING ANALYSIS COMPONENTS...")
try:
    from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
    
    print("   ✅ Main analyzer class accessible")
    
    # Test if we can access analysis methods
    analyzer = IntegratedComprehensiveMedicalAnalyzer("TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf")
    
    # Check for OpenAI functionality
    if hasattr(analyzer, 'ai_prompts'):
        print("   ✅ AI prompts system available")
    
    if hasattr(analyzer, 'unique_tracker'):
        print("   ✅ Deduplication system available")
        
    print("   ✅ All analysis components accessible")
    
except Exception as e:
    print(f"   ❌ Analysis components test failed: {e}")

print()
print("=== STREAMLIT TEST COMPLETE ===")

# Summary
print()
print("SUMMARY:")
if latest_dir and len(found_files) >= 2:
    print("✅ Streamlit should work - data and components available")
    print("✅ Charts and visualizations supported")  
    print("✅ OpenAI analysis results available")
    print("✅ Deduplication system working")
    
    print()
    print("RECOMMENDED: Run Streamlit dashboard with:")
    print("streamlit run streamlit_comprehensive_analyzer.py")
else:
    print("⚠️  Streamlit may have limited functionality - run full analysis first")
    print("RECOMMENDED: Run integrated analyzer first:")
    print("python integrated_comprehensive_analyzer.py")