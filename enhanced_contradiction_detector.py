#!/usr/bin/env python3
"""
Enhanced Contradiction Detection for SHIF Healthcare Policies
Works with limited tariff data using comprehensive rule matching
"""

import pandas as pd
import re
from typing import List, Dict, Tuple
import difflib

class EnhancedContradictionDetector:
    """Enhanced contradiction detection that works with partial data"""
    
    def __init__(self):
        self.contradictions = []
        
    def detect_all_contradictions(self, rules_df: pd.DataFrame) -> pd.DataFrame:
        """Detect contradictions using multiple approaches"""
        print("🔍 Enhanced Contradiction Detection")
        print(f"📊 Analyzing {len(rules_df)} rules...")
        
        all_contradictions = []
        
        # 1. Service name variations (same service, different details)
        service_contradictions = self._find_service_variations(rules_df)
        all_contradictions.extend(service_contradictions)
        
        # 2. Facility level conflicts  
        facility_contradictions = self._find_facility_conflicts(rules_df)
        all_contradictions.extend(facility_contradictions)
        
        # 3. Coverage status conflicts
        coverage_contradictions = self._find_coverage_conflicts(rules_df)
        all_contradictions.extend(coverage_contradictions)
        
        # 4. Tariff conflicts (where available)
        tariff_contradictions = self._find_tariff_conflicts(rules_df)
        all_contradictions.extend(tariff_contradictions)
        
        # 5. Service limit conflicts 
        limit_contradictions = self._find_limit_conflicts(rules_df)
        all_contradictions.extend(limit_contradictions)
        
        if all_contradictions:
            contradictions_df = pd.DataFrame(all_contradictions)
            print(f"✅ Found {len(contradictions_df)} potential contradictions")
            return contradictions_df
        else:
            print("ℹ️ No contradictions detected")
            return pd.DataFrame()
    
    def _find_service_variations(self, rules_df: pd.DataFrame) -> List[Dict]:
        """Find similar services that might be duplicates or conflicts"""
        print("🔄 Checking service variations...")
        variations = []
        
        # Group similar service names
        services_by_category = rules_df.groupby('category')
        
        for category, group in services_by_category:
            if len(group) < 2:
                continue
                
            services = group['service'].tolist()
            service_keys = group['service_key'].tolist()
            
            # Find similar service names within each category
            for i in range(len(services)):
                for j in range(i + 1, len(services)):
                    service1, service2 = services[i], services[j]
                    key1, key2 = service_keys[i], service_keys[j]
                    
                    # Calculate similarity
                    similarity = difflib.SequenceMatcher(None, key1, key2).ratio()
                    
                    if similarity > 0.7:  # 70% similar
                        # Check if they have different attributes
                        rule1 = group.iloc[i]
                        rule2 = group.iloc[j]
                        
                        if self._rules_conflict(rule1, rule2):
                            variations.append({
                                'type': 'Service_Variation',
                                'service_1': service1[:100],
                                'service_2': service2[:100],
                                'conflict_description': f'Similar services with different attributes in {category}',
                                'evidence_1': f"Page {rule1['source_page']}: {rule1.get('evidence_snippet', '')[:100]}",
                                'evidence_2': f"Page {rule2['source_page']}: {rule2.get('evidence_snippet', '')[:100]}",
                                'severity': 'MEDIUM',
                                'confidence': 'MEDIUM',
                                'similarity_score': round(similarity, 2)
                            })
        
        print(f"  → Found {len(variations)} service variations")
        return variations
    
    def _find_facility_conflicts(self, rules_df: pd.DataFrame) -> List[Dict]:
        """Find facility level conflicts"""
        print("🏥 Checking facility level conflicts...")
        conflicts = []
        
        # Group by similar service keys
        for service_key in rules_df['service_key'].unique():
            if pd.isna(service_key):
                continue
                
            service_rules = rules_df[rules_df['service_key'] == service_key]
            
            if len(service_rules) > 1:
                # Check for facility level conflicts
                facility_levels = []
                for _, rule in service_rules.iterrows():
                    if rule['facility_levels'] and rule['facility_levels'] != '[]':
                        try:
                            levels = eval(rule['facility_levels']) if isinstance(rule['facility_levels'], str) else rule['facility_levels']
                            if levels:
                                facility_levels.append((rule, levels))
                        except:
                            continue
                
                # Compare facility levels for conflicts
                for i in range(len(facility_levels)):
                    for j in range(i + 1, len(facility_levels)):
                        rule1, levels1 = facility_levels[i]
                        rule2, levels2 = facility_levels[j]
                        
                        # Check if levels conflict
                        if not set(levels1).intersection(set(levels2)):
                            conflicts.append({
                                'type': 'Facility_Conflict',
                                'service_1': rule1['service'][:100],
                                'service_2': rule2['service'][:100],
                                'conflict_description': f'Same service available at different facility levels: {levels1} vs {levels2}',
                                'evidence_1': f"Page {rule1['source_page']}: Levels {levels1}",
                                'evidence_2': f"Page {rule2['source_page']}: Levels {levels2}",
                                'severity': 'HIGH',
                                'confidence': 'HIGH'
                            })
        
        print(f"  → Found {len(conflicts)} facility conflicts")
        return conflicts
    
    def _find_coverage_conflicts(self, rules_df: pd.DataFrame) -> List[Dict]:
        """Find coverage status conflicts"""
        print("📋 Checking coverage conflicts...")
        conflicts = []
        
        # Group by service key and look for coverage conflicts
        for service_key in rules_df['service_key'].unique():
            if pd.isna(service_key):
                continue
                
            service_rules = rules_df[rules_df['service_key'] == service_key]
            
            # Check for mixed coverage statuses
            coverage_statuses = service_rules['coverage_status'].unique()
            exclusions = service_rules['exclusion'].unique()
            
            if len(coverage_statuses) > 1:
                rule1 = service_rules.iloc[0]
                rule2 = service_rules.iloc[1]
                
                conflicts.append({
                    'type': 'Coverage_Conflict',
                    'service_1': rule1['service'][:100],
                    'service_2': rule2['service'][:100],
                    'conflict_description': f'Mixed coverage status: {coverage_statuses}',
                    'evidence_1': f"Page {rule1['source_page']}: {rule1['coverage_status']}",
                    'evidence_2': f"Page {rule2['source_page']}: {rule2['coverage_status']}",
                    'severity': 'HIGH',
                    'confidence': 'HIGH'
                })
        
        print(f"  → Found {len(conflicts)} coverage conflicts")
        return conflicts
    
    def _find_tariff_conflicts(self, rules_df: pd.DataFrame) -> List[Dict]:
        """Find tariff conflicts in services with pricing"""
        print("💰 Checking tariff conflicts...")
        conflicts = []
        
        # Only check rules with tariff values
        tariff_rules = rules_df[rules_df['tariff'].notna() & (rules_df['tariff'] > 0)]
        
        print(f"  → {len(tariff_rules)} rules have tariff values")
        
        # Group by similar service names
        for service_key in tariff_rules['service_key'].unique():
            if pd.isna(service_key):
                continue
                
            service_tariffs = tariff_rules[tariff_rules['service_key'] == service_key]
            
            if len(service_tariffs) > 1:
                # Check for different tariffs for same service
                tariffs = service_tariffs['tariff'].unique()
                if len(tariffs) > 1:
                    rule1 = service_tariffs.iloc[0] 
                    rule2 = service_tariffs.iloc[1]
                    
                    conflicts.append({
                        'type': 'Tariff_Conflict',
                        'service_1': rule1['service'][:100],
                        'service_2': rule2['service'][:100],
                        'conflict_description': f'Same service with different tariffs: KES {rule1["tariff"]} vs KES {rule2["tariff"]}',
                        'evidence_1': f"Page {rule1['source_page']}: KES {rule1['tariff']}",
                        'evidence_2': f"Page {rule2['source_page']}: KES {rule2['tariff']}",
                        'severity': 'HIGH',
                        'confidence': 'HIGH'
                    })
        
        print(f"  → Found {len(conflicts)} tariff conflicts")
        return conflicts
    
    def _find_limit_conflicts(self, rules_df: pd.DataFrame) -> List[Dict]:
        """Find service limit conflicts (e.g. dialysis sessions)"""
        print("📊 Checking service limit conflicts...")
        conflicts = []
        
        # Look for dialysis-specific conflicts first
        dialysis_rules = rules_df[rules_df['category'] == 'DIALYSIS']
        
        print(f"  → {len(dialysis_rules)} dialysis rules to analyze")
        
        # Check for session limit patterns in dialysis rules
        session_patterns = [
            r'(\d+)\s*(?:sessions?|times?)\s*(?:per|\/)\s*(?:week|month)',
            r'(\d+)x?\s*(?:weekly|monthly)',
            r'(\d+)\s*per\s*(?:week|month)'
        ]
        
        dialysis_with_limits = []
        for _, rule in dialysis_rules.iterrows():
            text_to_check = f"{rule['service']} {rule.get('raw_text', '')} {rule.get('evidence_snippet', '')}"
            
            for pattern in session_patterns:
                matches = re.findall(pattern, text_to_check, re.IGNORECASE)
                if matches:
                    dialysis_with_limits.append((rule, matches[0]))
                    break
        
        # Compare limits
        if len(dialysis_with_limits) > 1:
            for i in range(len(dialysis_with_limits)):
                for j in range(i + 1, len(dialysis_with_limits)):
                    rule1, limit1 = dialysis_with_limits[i]
                    rule2, limit2 = dialysis_with_limits[j]
                    
                    if limit1 != limit2:
                        conflicts.append({
                            'type': 'Limit_Conflict',
                            'service_1': rule1['service'][:100],
                            'service_2': rule2['service'][:100], 
                            'conflict_description': f'Dialysis session limits conflict: {limit1} vs {limit2}',
                            'evidence_1': f"Page {rule1['source_page']}: {limit1} sessions",
                            'evidence_2': f"Page {rule2['source_page']}: {limit2} sessions",
                            'severity': 'HIGH',
                            'confidence': 'MEDIUM'
                        })
        
        print(f"  → Found {len(conflicts)} limit conflicts")
        return conflicts
    
    def _rules_conflict(self, rule1: pd.Series, rule2: pd.Series) -> bool:
        """Check if two rules have conflicting attributes"""
        conflicts = []
        
        # Check tariff conflicts
        if (pd.notna(rule1['tariff']) and pd.notna(rule2['tariff']) and 
            rule1['tariff'] != rule2['tariff']):
            conflicts.append('tariff')
        
        # Check coverage conflicts
        if (rule1['coverage_status'] != rule2['coverage_status'] and 
            pd.notna(rule1['coverage_status']) and pd.notna(rule2['coverage_status'])):
            conflicts.append('coverage')
            
        # Check facility level conflicts
        try:
            levels1 = eval(rule1['facility_levels']) if isinstance(rule1['facility_levels'], str) else rule1['facility_levels']
            levels2 = eval(rule2['facility_levels']) if isinstance(rule2['facility_levels'], str) else rule2['facility_levels']
            
            if levels1 and levels2 and not set(levels1).intersection(set(levels2)):
                conflicts.append('facility')
        except:
            pass
        
        return len(conflicts) > 0

def main():
    """Run enhanced contradiction detection"""
    print("🔍 Enhanced SHIF Contradiction Detection System")
    print("=" * 50)
    
    # Load rules
    rules_df = pd.read_csv('outputs_comprehensive/rules_comprehensive.csv')
    print(f"📊 Loaded {len(rules_df)} rules")
    
    # Run enhanced detection
    detector = EnhancedContradictionDetector()
    contradictions_df = detector.detect_all_contradictions(rules_df)
    
    # Save results
    if not contradictions_df.empty:
        contradictions_df.to_csv('outputs_comprehensive/enhanced_contradictions.csv', index=False)
        print(f"\n💾 Saved {len(contradictions_df)} contradictions")
        
        # Show results by type
        print(f"\n📋 Contradictions by type:")
        for contradiction_type, count in contradictions_df['type'].value_counts().items():
            print(f"  {contradiction_type}: {count}")
            
        # Show sample high-severity contradictions
        high_severity = contradictions_df[contradictions_df['severity'] == 'HIGH']
        if not high_severity.empty:
            print(f"\n🚨 Sample High-Severity Contradictions:")
            for _, conflict in high_severity.head(3).iterrows():
                print(f"  {conflict['type']}: {conflict['conflict_description']}")
                print(f"    Service 1: {conflict['service_1'][:80]}...")
                print(f"    Service 2: {conflict['service_2'][:80]}...")
                print(f"    Confidence: {conflict['confidence']}")
                print()
    else:
        print("\nℹ️ No contradictions found with enhanced detection")
    
    print("\n✅ Enhanced Contradiction Detection Complete")

if __name__ == "__main__":
    main()