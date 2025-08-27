#!/usr/bin/env python3
"""
Test that Task 1 tables are now populated correctly
"""
import sys

class MockStreamlit:
    def set_page_config(self, **kwargs): pass
    def markdown(self, text, unsafe_allow_html=False): pass
    def success(self, text): print(f'SUCCESS: {text}')
    def error(self, text): print(f'ERROR: {text}')
    def info(self, text): print(f'INFO: {text}')
    def warning(self, text): print(f'WARNING: {text}')
    def write(self, text): pass
    def button(self, text, **kwargs): return False
    def sidebar(self): return self
    def progress(self, value): pass
    def text(self, text): pass
    def metric(self, label, value, delta=None): pass
    def checkbox(self, label, value=False): return value
    def selectbox(self, label, options): return options[0] if options else None
    def columns(self, n): return [self] * n
    def container(self): return self
    def empty(self): return self
    def placeholder(self): return self
    def dataframe(self, data): 
        if hasattr(data, 'shape'):
            print(f'   DATAFRAME: {data.shape[0]} rows x {data.shape[1]} columns')
            if data.shape[0] > 0:
                print(f'   SAMPLE DATA: {list(data.columns)[:3]}')
            else:
                print('   DATAFRAME IS EMPTY!')
    def plotly_chart(self, fig, **kwargs): 
        print('   PLOTLY CHART rendered')

sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

print("=== TESTING TASK 1 TABLES FIX ===")
print()

try:
    from streamlit_comprehensive_analyzer import SHIFHealthcarePolicyAnalyzer
    
    # Test instantiation and data loading
    analyzer = SHIFHealthcarePolicyAnalyzer()
    print("✅ Analyzer created")
    
    analyzer.load_existing_results() 
    print("✅ Results loaded")
    
    # Test the corrected task1 method
    rules = analyzer.task1_structure_rules()
    print(f"✅ task1_structure_rules: {len(rules)} rules")
    
    if rules:
        print(f"   📋 First rule keys: {list(rules[0].keys())}")
        print(f"   📋 Sample data: {rules[0].get('service_name', 'N/A')[:50]}")
        
        # Test other task methods
        contradictions, gaps = analyzer.task2_detect_contradictions_and_gaps()
        print(f"✅ task2: {len(contradictions)} contradictions, {len(gaps)} gaps")
        
        context = analyzer.task3_kenya_shif_context()
        print(f"✅ task3: {type(context)} context data")
        
        dashboard = analyzer.task4_create_dashboard()
        print(f"✅ task4: {type(dashboard)} dashboard data")
        
        print()
        print("🎯 TESTING DISPLAY LOGIC:")
        
        # Test the display transformation
        display_rules = []
        for rule in rules[:3]:  # Test first 3
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
        
        # Check if display data has content
        has_content = any(
            any(v for v in rule.values() if v not in ['', 'N/A', 0, '...']) 
            for rule in display_rules
        )
        
        if has_content:
            print("✅ Display data contains content - tables should not be empty!")
            for i, rule in enumerate(display_rules):
                print(f"   Rule {i+1}: Service='{rule['Service Name'][:30]}', Type='{rule['Rule Type']}', Facility='{rule['Facility Level']}'")
        else:
            print("❌ Display data still appears empty")
            
        print()
        print("🚀 EXPECTED RESULTS:")
        print("   - Task 1 tables should now show populated data")
        print("   - Charts should show meaningful distributions")
        print("   - No more 'Unknown' only values")
        
    else:
        print("❌ No rules loaded - still an issue with data access")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()