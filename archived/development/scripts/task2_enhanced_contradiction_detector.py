#!/usr/bin/env python3
"""
Enhanced AI Contradiction Detection System for Task 2
Specifically designed to detect the types of contradictions mentioned:
- 'Dialysis covered 2x/week' vs 'Dialysis excluded in Level 5'
- Service availability conflicts across facility levels
- Tariff inconsistencies for same services
- Coverage vs exclusion conflicts

Author: Pranay for Dr. Rishi
Task: Task 2 - Contradiction Detection
Date: August 25, 2025
"""

import pandas as pd
import openai
import os
from dotenv import load_dotenv
import json
import time
import re
from collections import defaultdict
from typing import List, Dict, Tuple

load_dotenv()

class EnhancedContradictionDetector:
    """Enhanced AI-powered contradiction detection specifically for Task 2"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.contradictions_found = []
        self.service_groups = {}
        
    def analyze_all_contradictions(self, rules_file: str) -> pd.DataFrame:
        """Complete contradiction analysis as required for Task 2"""
        
        print("🔍 TASK 2: Enhanced Contradiction Detection")
        print("=" * 60)
        
        # Load rules data
        if os.path.exists(rules_file):
            rules_df = pd.read_csv(rules_file)
            print(f"📊 Loaded {len(rules_df)} rules for analysis")
        else:
            print(f"❌ Rules file not found: {rules_file}")
            print("🔄 Will run enhanced extraction first...")
            return self._run_extraction_and_detect()
        
        # Multi-layered contradiction detection
        all_contradictions = []
        
        # 1. Facility Level Coverage Contradictions
        print("\n1️⃣ Analyzing Facility Level Coverage Conflicts...")
        facility_contradictions = self._detect_facility_level_conflicts(rules_df)
        all_contradictions.extend(facility_contradictions)
        
        # 2. Service Limit Contradictions (like dialysis frequency)
        print("2️⃣ Analyzing Service Limit Conflicts...")
        limit_contradictions = self._detect_service_limit_conflicts(rules_df)
        all_contradictions.extend(limit_contradictions)
        
        # 3. Tariff Inconsistencies
        print("3️⃣ Analyzing Tariff Inconsistencies...")
        tariff_contradictions = self._detect_tariff_conflicts(rules_df)
        all_contradictions.extend(tariff_contradictions)
        
        # 4. Coverage vs Exclusion Conflicts
        print("4️⃣ Analyzing Coverage vs Exclusion Conflicts...")
        coverage_contradictions = self._detect_coverage_exclusion_conflicts(rules_df)
        all_contradictions.extend(coverage_contradictions)
        
        # 5. AI-Powered Semantic Analysis
        print("5️⃣ Running AI-Powered Semantic Analysis...")
        ai_contradictions = self._ai_semantic_analysis(rules_df)
        all_contradictions.extend(ai_contradictions)
        
        # Convert to DataFrame and save
        if all_contradictions:
            contradictions_df = pd.DataFrame(all_contradictions)
            contradictions_df = self._rank_and_prioritize(contradictions_df)
            
            # Save results
            output_file = 'outputs_comprehensive/task2_contradictions_enhanced.csv'
            os.makedirs('outputs_comprehensive', exist_ok=True)
            contradictions_df.to_csv(output_file, index=False)
            
            print(f"\n✅ Found {len(contradictions_df)} contradictions")
            print(f"💾 Results saved to: {output_file}")
            
            return contradictions_df
        else:
            print("\nℹ️ No contradictions detected")
            return pd.DataFrame()
    
    def _detect_facility_level_conflicts(self, rules_df: pd.DataFrame) -> List[Dict]:
        """Detect conflicts like 'Service X available in Level 3' vs 'Service X excluded from Level 3'"""
        
        conflicts = []
        
        # Group services by normalized name
        service_groups = defaultdict(list)
        
        for _, rule in rules_df.iterrows():
            service_key = self._normalize_service_name(rule.get('service', ''))
            if service_key:
                service_groups[service_key].append(rule)
        
        # Check each service group for facility conflicts
        for service_key, service_rules in service_groups.items():
            if len(service_rules) < 2:
                continue
                
            facility_coverage = {}  # facility_level -> (covered, excluded)
            
            for rule in service_rules:
                facilities = self._parse_facility_levels(rule.get('facility_levels', ''))
                coverage = rule.get('coverage_status', '').lower()
                exclusion = rule.get('exclusion', False)
                
                for facility in facilities:
                    if facility not in facility_coverage:
                        facility_coverage[facility] = {'covered': [], 'excluded': []}
                    
                    if exclusion or 'exclud' in coverage:
                        facility_coverage[facility]['excluded'].append(rule)
                    elif 'cover' in coverage or rule.get('tariff'):
                        facility_coverage[facility]['covered'].append(rule)
            
            # Find conflicts
            for facility, coverage_info in facility_coverage.items():
                if coverage_info['covered'] and coverage_info['excluded']:
                    conflicts.append({
                        'type': 'Facility_Coverage_Conflict',
                        'service_name': service_key,
                        'facility_level': facility,
                        'conflict_description': f"{service_key} is both covered and excluded in {facility}",
                        'covered_rules': len(coverage_info['covered']),
                        'excluded_rules': len(coverage_info['excluded']),
                        'evidence_covered': coverage_info['covered'][0].get('evidence_snippet', ''),
                        'evidence_excluded': coverage_info['excluded'][0].get('evidence_snippet', ''),
                        'page_covered': coverage_info['covered'][0].get('source_page', ''),
                        'page_excluded': coverage_info['excluded'][0].get('source_page', ''),
                        'severity': 'HIGH',
                        'confidence': 'HIGH'
                    })
        
        print(f"   Found {len(conflicts)} facility-level conflicts")
        return conflicts
    
    def _detect_service_limit_conflicts(self, rules_df: pd.DataFrame) -> List[Dict]:
        """Detect conflicts like 'Dialysis 2x/week' vs 'Dialysis 3x/week'"""
        
        conflicts = []
        
        # Group services and check for limit conflicts
        service_groups = defaultdict(list)
        
        for _, rule in rules_df.iterrows():
            service_key = self._normalize_service_name(rule.get('service', ''))
            limits = rule.get('limits', '')
            
            if service_key and limits and limits.strip():
                service_groups[service_key].append(rule)
        
        for service_key, service_rules in service_groups.items():
            if len(service_rules) < 2:
                continue
            
            # Extract numeric limits
            limit_patterns = []
            for rule in service_rules:
                limits_text = str(rule.get('limits', ''))
                
                # Look for patterns like "2x/week", "3 per month", "once daily"
                patterns = re.findall(r'(\d+)\s*(?:x|times?|per)\s*(?:week|month|day|year)', limits_text.lower())
                if patterns:
                    limit_patterns.append({
                        'rule': rule,
                        'limit_value': patterns[0],
                        'limit_text': limits_text
                    })
            
            # Find conflicts in limits
            if len(limit_patterns) > 1:
                for i, pattern1 in enumerate(limit_patterns):
                    for pattern2 in limit_patterns[i+1:]:
                        if pattern1['limit_value'] != pattern2['limit_value']:
                            conflicts.append({
                                'type': 'Service_Limit_Conflict',
                                'service_name': service_key,
                                'conflict_description': f"{service_key} has conflicting limits: '{pattern1['limit_text']}' vs '{pattern2['limit_text']}'",
                                'limit_1': pattern1['limit_text'],
                                'limit_2': pattern2['limit_text'],
                                'evidence_1': pattern1['rule'].get('evidence_snippet', ''),
                                'evidence_2': pattern2['rule'].get('evidence_snippet', ''),
                                'page_1': pattern1['rule'].get('source_page', ''),
                                'page_2': pattern2['rule'].get('source_page', ''),
                                'severity': 'HIGH',
                                'confidence': 'HIGH'
                            })
        
        print(f"   Found {len(conflicts)} service limit conflicts")
        return conflicts
    
    def _detect_tariff_conflicts(self, rules_df: pd.DataFrame) -> List[Dict]:
        """Detect same services with different tariffs"""
        
        conflicts = []
        
        # Group by service and facility level
        service_tariffs = defaultdict(lambda: defaultdict(list))
        
        for _, rule in rules_df.iterrows():
            service_key = self._normalize_service_name(rule.get('service', ''))
            tariff = rule.get('tariff')
            facility = rule.get('facility_level', 'General')
            
            if service_key and tariff and pd.notna(tariff) and tariff > 0:
                service_tariffs[service_key][facility].append(rule)
        
        # Find tariff conflicts
        for service_key, facility_tariffs in service_tariffs.items():
            for facility, tariff_rules in facility_tariffs.items():
                if len(tariff_rules) < 2:
                    continue
                
                tariffs = [rule.get('tariff') for rule in tariff_rules]
                unique_tariffs = set(tariffs)
                
                if len(unique_tariffs) > 1:
                    rule1, rule2 = tariff_rules[0], tariff_rules[1]
                    conflicts.append({
                        'type': 'Tariff_Conflict',
                        'service_name': service_key,
                        'facility_level': facility,
                        'conflict_description': f"{service_key} has different tariffs: KES {rule1.get('tariff')} vs KES {rule2.get('tariff')}",
                        'tariff_1': rule1.get('tariff'),
                        'tariff_2': rule2.get('tariff'),
                        'evidence_1': rule1.get('evidence_snippet', ''),
                        'evidence_2': rule2.get('evidence_snippet', ''),
                        'page_1': rule1.get('source_page', ''),
                        'page_2': rule2.get('source_page', ''),
                        'severity': 'MEDIUM',
                        'confidence': 'HIGH'
                    })
        
        print(f"   Found {len(conflicts)} tariff conflicts")
        return conflicts
    
    def _detect_coverage_exclusion_conflicts(self, rules_df: pd.DataFrame) -> List[Dict]:
        """Detect services that are both covered and excluded"""
        
        conflicts = []
        
        # Group services by normalized name
        service_groups = defaultdict(list)
        
        for _, rule in rules_df.iterrows():
            service_key = self._normalize_service_name(rule.get('service', ''))
            if service_key:
                service_groups[service_key].append(rule)
        
        for service_key, service_rules in service_groups.items():
            covered_rules = []
            excluded_rules = []
            
            for rule in service_rules:
                coverage = rule.get('coverage_status', '').lower()
                exclusion = rule.get('exclusion', False)
                has_tariff = pd.notna(rule.get('tariff')) and rule.get('tariff') > 0
                
                if exclusion or 'exclud' in coverage or 'not cover' in coverage:
                    excluded_rules.append(rule)
                elif 'cover' in coverage or has_tariff:
                    covered_rules.append(rule)
            
            if covered_rules and excluded_rules:
                conflicts.append({
                    'type': 'Coverage_Exclusion_Conflict',
                    'service_name': service_key,
                    'conflict_description': f"{service_key} is both covered and excluded",
                    'covered_instances': len(covered_rules),
                    'excluded_instances': len(excluded_rules),
                    'evidence_covered': covered_rules[0].get('evidence_snippet', ''),
                    'evidence_excluded': excluded_rules[0].get('evidence_snippet', ''),
                    'page_covered': covered_rules[0].get('source_page', ''),
                    'page_excluded': excluded_rules[0].get('source_page', ''),
                    'severity': 'HIGH',
                    'confidence': 'HIGH'
                })
        
        print(f"   Found {len(conflicts)} coverage/exclusion conflicts")
        return conflicts
    
    def _ai_semantic_analysis(self, rules_df: pd.DataFrame, batch_size: int = 15) -> List[Dict]:
        """Use AI to find semantic contradictions that rule-based detection might miss"""
        
        ai_conflicts = []
        
        # Process in batches to avoid token limits
        for i in range(0, min(len(rules_df), 100), batch_size):  # Limit to first 100 rules for efficiency
            batch = rules_df.iloc[i:i+batch_size]
            
            print(f"   AI analyzing batch {i//batch_size + 1}...")
            
            batch_conflicts = self._analyze_batch_with_ai(batch)
            ai_conflicts.extend(batch_conflicts)
            
            time.sleep(0.5)  # Rate limiting
        
        print(f"   AI found {len(ai_conflicts)} semantic conflicts")
        return ai_conflicts
    
    def _analyze_batch_with_ai(self, batch_df: pd.DataFrame) -> List[Dict]:
        """AI analysis of a batch of rules"""
        
        rules_text = ""
        for _, rule in batch_df.iterrows():
            service = str(rule.get('service', ''))[:100]
            tariff = rule.get('tariff', 'N/A')
            coverage = rule.get('coverage_status', 'N/A')
            facilities = rule.get('facility_levels', 'N/A')
            limits = rule.get('limits', 'N/A')
            exclusion = rule.get('exclusion', False)
            page = rule.get('source_page', 'N/A')
            
            rules_text += f"""Service: {service}
Tariff: KES {tariff}
Coverage: {coverage}
Facilities: {facilities}
Limits: {limits}
Excluded: {exclusion}
Page: {page}
---
"""
        
        prompt = f"""You are a healthcare policy expert analyzing SHIF benefit contradictions.

TASK: Find contradictions in these rules that indicate policy inconsistencies.

FOCUS ON:
1. FACILITY CONFLICTS: Same service covered in one facility level but excluded in another
2. LIMIT CONFLICTS: Same service with different frequency/quantity limits 
3. TARIFF CONFLICTS: Identical services with different costs
4. COVERAGE CONFLICTS: Service both included and explicitly excluded

RULES:
{rules_text}

Return JSON array of contradictions found:
[
  {{
    "type": "Facility|Limit|Tariff|Coverage",
    "service_name": "service name",
    "conflict_description": "detailed conflict description",
    "evidence": "supporting evidence text",
    "severity": "HIGH|MEDIUM|LOW",
    "confidence": "HIGH|MEDIUM|LOW"
  }}
]

Only return high-confidence contradictions. If none found, return [].
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            if result_text.startswith('[') and result_text.endswith(']'):
                return json.loads(result_text)
            else:
                return []
                
        except Exception as e:
            print(f"   ⚠️ AI analysis error: {e}")
            return []
    
    def _normalize_service_name(self, service: str) -> str:
        """Normalize service names for comparison"""
        if not service or pd.isna(service):
            return ""
        
        # Clean and normalize
        service = str(service).lower().strip()
        
        # Remove common prefixes/suffixes
        service = re.sub(r'^(the|a|an)\s+', '', service)
        service = re.sub(r'\s+(service|care|treatment|procedure)$', '', service)
        
        # Standardize terms
        replacements = {
            'haemodialysis': 'hemodialysis',
            'ct scan': 'ct imaging',
            'mri scan': 'mri imaging',
            'x-ray': 'xray',
            'ultra-sound': 'ultrasound'
        }
        
        for old, new in replacements.items():
            service = service.replace(old, new)
        
        return service[:50]  # Limit length
    
    def _parse_facility_levels(self, facility_text: str) -> List[str]:
        """Parse facility level information"""
        if not facility_text or pd.isna(facility_text):
            return ['General']
        
        facility_text = str(facility_text).lower()
        levels = []
        
        # Look for explicit level mentions
        level_matches = re.findall(r'level\s*(\d+)', facility_text)
        for match in level_matches:
            levels.append(f"Level {match}")
        
        # Look for facility types
        if 'hospital' in facility_text:
            levels.append('Hospital')
        if 'clinic' in facility_text:
            levels.append('Clinic')
        if 'dispensary' in facility_text:
            levels.append('Dispensary')
        
        return levels if levels else ['General']
    
    def _rank_and_prioritize(self, contradictions_df: pd.DataFrame) -> pd.DataFrame:
        """Rank contradictions by importance and confidence"""
        
        # Calculate priority score
        priority_scores = []
        
        for _, contradiction in contradictions_df.iterrows():
            score = 0
            
            # Type priority
            type_scores = {
                'Facility_Coverage_Conflict': 10,
                'Coverage_Exclusion_Conflict': 9,
                'Service_Limit_Conflict': 8,
                'Tariff_Conflict': 6
            }
            score += type_scores.get(contradiction.get('type', ''), 5)
            
            # Severity priority
            severity_scores = {'HIGH': 5, 'MEDIUM': 3, 'LOW': 1}
            score += severity_scores.get(contradiction.get('severity', 'LOW'), 1)
            
            # Confidence priority
            confidence_scores = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            score += confidence_scores.get(contradiction.get('confidence', 'LOW'), 1)
            
            priority_scores.append(score)
        
        contradictions_df['priority_score'] = priority_scores
        contradictions_df = contradictions_df.sort_values('priority_score', ascending=False)
        
        return contradictions_df
    
    def _run_extraction_and_detect(self) -> pd.DataFrame:
        """Run extraction first if no rules file exists"""
        
        print("🔄 Running enhanced extraction first...")
        
        # Import and run enhanced analyzer
        try:
            from enhanced_analyzer import parse_pdf_enhanced
            
            pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
            if os.path.exists(pdf_path):
                rules_df = parse_pdf_enhanced(pdf_path)
                
                # Save rules
                os.makedirs('outputs_comprehensive', exist_ok=True)
                rules_df.to_csv('outputs_comprehensive/rules_comprehensive.csv', index=False)
                
                # Now run contradiction detection
                return self.analyze_all_contradictions('outputs_comprehensive/rules_comprehensive.csv')
            else:
                print(f"❌ PDF not found: {pdf_path}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Error in extraction: {e}")
            return pd.DataFrame()

def main():
    """Main execution for Task 2"""
    
    print("🎯 TASK 2: Enhanced Contradiction Detection")
    print("Detecting conflicts like 'Dialysis covered 2x/week' vs 'Dialysis excluded in Level 5'")
    print("=" * 80)
    
    detector = EnhancedContradictionDetector()
    
    # Try to load existing rules or run extraction
    rules_files = [
        'outputs_comprehensive/rules_comprehensive.csv',
        'outputs/rules_comprehensive.csv'
    ]
    
    rules_file = None
    for file_path in rules_files:
        if os.path.exists(file_path):
            rules_file = file_path
            break
    
    if rules_file:
        contradictions_df = detector.analyze_all_contradictions(rules_file)
    else:
        contradictions_df = detector._run_extraction_and_detect()
    
    # Display results
    if not contradictions_df.empty:
        print(f"\n🎯 TASK 2 RESULTS:")
        print(f"✅ Total contradictions found: {len(contradictions_df)}")
        
        # Show by type
        type_counts = contradictions_df['type'].value_counts()
        for conflict_type, count in type_counts.items():
            print(f"  {conflict_type}: {count}")
        
        # Show top conflicts
        print(f"\n🔥 TOP PRIORITY CONTRADICTIONS:")
        for i, (_, contradiction) in enumerate(contradictions_df.head(5).iterrows(), 1):
            print(f"{i}. {contradiction.get('type', 'Unknown')}: {contradiction.get('service_name', 'Unknown')}")
            print(f"   {contradiction.get('conflict_description', 'No description')}")
            print(f"   Severity: {contradiction.get('severity', 'Unknown')} | Confidence: {contradiction.get('confidence', 'Unknown')}")
            print()
        
        # Save enhanced report
        report_file = 'outputs_comprehensive/TASK2_CONTRADICTION_REPORT.txt'
        with open(report_file, 'w') as f:
            f.write("TASK 2: CONTRADICTION DETECTION REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total Contradictions Found: {len(contradictions_df)}\n\n")
            
            for conflict_type, count in type_counts.items():
                f.write(f"{conflict_type}: {count}\n")
            
            f.write("\n" + "=" * 50 + "\n")
            f.write("DETAILED CONTRADICTIONS:\n\n")
            
            for _, contradiction in contradictions_df.iterrows():
                f.write(f"Type: {contradiction.get('type', 'Unknown')}\n")
                f.write(f"Service: {contradiction.get('service_name', 'Unknown')}\n") 
                f.write(f"Description: {contradiction.get('conflict_description', 'No description')}\n")
                f.write(f"Severity: {contradiction.get('severity', 'Unknown')}\n")
                f.write(f"Confidence: {contradiction.get('confidence', 'Unknown')}\n")
                f.write("-" * 30 + "\n")
        
        print(f"📄 Detailed report saved to: {report_file}")
    else:
        print("\nℹ️ No contradictions detected in the current analysis")
    
    print(f"\n✅ TASK 2 COMPLETE")

if __name__ == "__main__":
    main()
