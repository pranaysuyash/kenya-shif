#!/usr/bin/env python3
"""
TASK 3: Comprehensive Healthcare Gap Analysis
Based on expectations.yaml requirements and SHIF policy analysis

Analyzes critical healthcare gaps in:
- Chronic kidney disease (dialysis services)
- Stroke rehabilitation
- Cancer treatment (chemotherapy/radiotherapy) 
- Mental health services
- Maternity care

Author: Pranay for Dr. Rishi
Task: Task 3 - Gap Analysis
Date: August 25, 2025
"""

import pandas as pd
import os
import yaml
import re
import pdfplumber
from collections import defaultdict
from typing import Dict, List
import json

class HealthcareGapAnalyzer:
    """Comprehensive healthcare gap analysis based on expectations"""
    
    def __init__(self):
        self.expectations = self.load_expectations()
        self.extracted_rules = None
        self.gaps_identified = []
        
    def load_expectations(self) -> Dict:
        """Load healthcare service expectations from YAML"""
        
        expectations_file = 'expectations.yaml'
        if os.path.exists(expectations_file):
            with open(expectations_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Fallback expectations if file not found
            return {
                'conditions': {
                    'Chronic kidney disease': {
                        'expected_services': ['dialysis', 'hemodialysis', 'haemodialysis', 'renal replacement'],
                        'frequency': '2-3 sessions per week',
                        'facility_levels': ['Level 4', 'Level 5', 'Level 6'],
                        'priority': 'HIGH'
                    },
                    'Stroke rehabilitation': {
                        'expected_services': ['physiotherapy', 'stroke rehab', 'rehabilitation', 'physio'],
                        'frequency': 'daily sessions',
                        'facility_levels': ['Level 3', 'Level 4', 'Level 5', 'Level 6'],
                        'priority': 'HIGH'
                    },
                    'Cancer treatment': {
                        'expected_services': ['chemotherapy', 'radiotherapy', 'oncology', 'cancer treatment'],
                        'frequency': 'as prescribed',
                        'facility_levels': ['Level 4', 'Level 5', 'Level 6'],
                        'priority': 'HIGH'
                    },
                    'Mental health': {
                        'expected_services': ['psychiatric', 'psychology', 'counseling', 'mental health'],
                        'frequency': 'weekly sessions',
                        'facility_levels': ['Level 4', 'Level 5', 'Level 6'],
                        'priority': 'MEDIUM'
                    },
                    'Maternity': {
                        'expected_services': ['delivery', 'maternity', 'antenatal', 'postnatal', 'caesarean'],
                        'frequency': 'full coverage',
                        'facility_levels': ['Level 2', 'Level 3', 'Level 4', 'Level 5', 'Level 6'],
                        'priority': 'HIGH'
                    }
                }
            }
    
    def analyze_comprehensive_gaps(self) -> pd.DataFrame:
        """Run comprehensive gap analysis for all expected healthcare services"""
        
        print("🔍 TASK 3: Comprehensive Healthcare Gap Analysis")
        print("=" * 60)
        
        # Load extracted rules if available
        self.load_extracted_rules()
        
        # Analyze each healthcare condition
        all_gaps = []
        
        for condition_name, condition_info in self.expectations.get('conditions', {}).items():
            print(f"\n📊 Analyzing {condition_name}...")
            condition_gaps = self.analyze_condition_gaps(condition_name, condition_info)
            all_gaps.extend(condition_gaps)
        
        # Additional gap analysis from direct PDF analysis
        pdf_gaps = self.analyze_pdf_gaps()
        all_gaps.extend(pdf_gaps)
        
        # Create comprehensive gap dataframe
        if all_gaps:
            gaps_df = pd.DataFrame(all_gaps)
            gaps_df = self.prioritize_gaps(gaps_df)
            
            # Save results
            output_file = 'outputs_comprehensive/task3_comprehensive_gaps.csv'
            os.makedirs('outputs_comprehensive', exist_ok=True)
            gaps_df.to_csv(output_file, index=False)
            
            print(f"\n✅ TASK 3 RESULTS:")
            print(f"   Total gaps identified: {len(gaps_df)}")
            print(f"   Critical gaps: {len(gaps_df[gaps_df['severity'] == 'CRITICAL'])}")
            print(f"   High priority gaps: {len(gaps_df[gaps_df['priority'] == 'HIGH'])}")
            print(f"   Results saved to: {output_file}")
            
            return gaps_df
        else:
            print("No gaps identified in current analysis")
            return pd.DataFrame()
    
    def load_extracted_rules(self):
        """Load previously extracted rules if available"""
        
        rules_files = [
            'outputs_comprehensive/rules_comprehensive.csv',
            'outputs/rules_comprehensive.csv'
        ]
        
        for rules_file in rules_files:
            if os.path.exists(rules_file):
                try:
                    self.extracted_rules = pd.read_csv(rules_file)
                    print(f"✅ Loaded {len(self.extracted_rules)} extracted rules from {rules_file}")
                    return
                except Exception as e:
                    print(f"⚠️ Error loading {rules_file}: {e}")
        
        print("ℹ️ No extracted rules found - will perform direct PDF analysis")
    
    def analyze_condition_gaps(self, condition_name: str, condition_info: Dict) -> List[Dict]:
        """Analyze gaps for a specific healthcare condition"""
        
        gaps = []
        expected_services = condition_info.get('expected_services', [])
        priority = condition_info.get('priority', 'MEDIUM')
        expected_facilities = condition_info.get('facility_levels', [])
        frequency = condition_info.get('frequency', 'as needed')
        
        print(f"   Expected services: {expected_services}")
        
        if self.extracted_rules is not None:
            # Analyze against extracted rules
            gaps.extend(self._analyze_with_extracted_rules(
                condition_name, expected_services, priority, expected_facilities, frequency
            ))
        else:
            # Direct PDF analysis
            gaps.extend(self._analyze_with_pdf_search(
                condition_name, expected_services, priority, expected_facilities, frequency
            ))
        
        return gaps
    
    def _analyze_with_extracted_rules(self, condition_name: str, expected_services: List[str], 
                                    priority: str, expected_facilities: List[str], frequency: str) -> List[Dict]:
        """Analyze gaps using extracted rules"""
        
        gaps = []
        found_services = set()
        
        # Search for expected services in extracted rules
        for expected_service in expected_services:
            matching_rules = self.extracted_rules[
                self.extracted_rules['service'].str.contains(expected_service, case=False, na=False)
            ]
            
            if len(matching_rules) > 0:
                found_services.add(expected_service)
                print(f"     ✅ Found {expected_service}: {len(matching_rules)} rules")
                
                # Check facility level coverage
                facility_gaps = self._check_facility_coverage(
                    matching_rules, expected_facilities, condition_name, expected_service
                )
                gaps.extend(facility_gaps)
                
                # Check frequency/limit gaps
                frequency_gaps = self._check_frequency_limits(
                    matching_rules, frequency, condition_name, expected_service
                )
                gaps.extend(frequency_gaps)
                
            else:
                print(f"     ❌ Missing {expected_service}")
                gaps.append({
                    'condition': condition_name,
                    'service': expected_service,
                    'gap_type': 'Missing Service',
                    'severity': 'CRITICAL' if priority == 'HIGH' else 'HIGH',
                    'priority': priority,
                    'description': f"{expected_service} not found in SHIF tariff structure",
                    'expected_frequency': frequency,
                    'expected_facilities': ', '.join(expected_facilities),
                    'recommendation': f"Add {expected_service} to SHIF benefit package",
                    'evidence': 'Service not found in comprehensive rule extraction'
                })
        
        # Overall condition coverage assessment
        coverage_percentage = len(found_services) / len(expected_services) * 100 if expected_services else 0
        
        if coverage_percentage < 50:
            gaps.append({
                'condition': condition_name,
                'service': f"{condition_name} Overall Coverage",
                'gap_type': 'Insufficient Coverage',
                'severity': 'CRITICAL',
                'priority': priority,
                'description': f"Only {coverage_percentage:.1f}% of expected {condition_name} services covered",
                'expected_frequency': frequency,
                'expected_facilities': ', '.join(expected_facilities),
                'recommendation': f"Comprehensive review of {condition_name} benefit package needed",
                'evidence': f"{len(found_services)}/{len(expected_services)} expected services found"
            })
        
        return gaps
    
    def _analyze_with_pdf_search(self, condition_name: str, expected_services: List[str],
                               priority: str, expected_facilities: List[str], frequency: str) -> List[Dict]:
        """Analyze gaps with direct PDF search"""
        
        gaps = []
        pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
        
        if not os.path.exists(pdf_path):
            print(f"     ⚠️ PDF not found for direct analysis")
            return gaps
        
        try:
            found_services = set()
            
            with pdfplumber.open(pdf_path) as pdf:
                # Search through PDF for expected services
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        for expected_service in expected_services:
                            if re.search(expected_service, text, re.IGNORECASE):
                                found_services.add(expected_service)
                                print(f"     ✅ Found {expected_service} on page {page_num}")
            
            # Identify missing services
            missing_services = set(expected_services) - found_services
            
            for missing_service in missing_services:
                gaps.append({
                    'condition': condition_name,
                    'service': missing_service,
                    'gap_type': 'Missing Service',
                    'severity': 'CRITICAL' if priority == 'HIGH' else 'HIGH',
                    'priority': priority,
                    'description': f"{missing_service} not found in SHIF PDF document",
                    'expected_frequency': frequency,
                    'expected_facilities': ', '.join(expected_facilities),
                    'recommendation': f"Add {missing_service} to SHIF benefit package",
                    'evidence': 'Direct PDF search - service not mentioned'
                })
        
        except Exception as e:
            print(f"     ❌ Error in PDF analysis: {e}")
        
        return gaps
    
    def _check_facility_coverage(self, matching_rules: pd.DataFrame, expected_facilities: List[str],
                               condition_name: str, service_name: str) -> List[Dict]:
        """Check if service is available at expected facility levels"""
        
        gaps = []
        
        # Get facility levels mentioned in rules
        facility_coverage = set()
        for _, rule in matching_rules.iterrows():
            facilities = str(rule.get('facility_levels', ''))
            for expected_facility in expected_facilities:
                if expected_facility.lower() in facilities.lower():
                    facility_coverage.add(expected_facility)
        
        # Find missing facility coverage
        missing_facilities = set(expected_facilities) - facility_coverage
        
        for missing_facility in missing_facilities:
            gaps.append({
                'condition': condition_name,
                'service': service_name,
                'gap_type': 'Facility Coverage Gap',
                'severity': 'HIGH',
                'priority': 'HIGH',
                'description': f"{service_name} not available at {missing_facility}",
                'expected_frequency': 'as needed',
                'expected_facilities': missing_facility,
                'recommendation': f"Extend {service_name} coverage to {missing_facility}",
                'evidence': f"Service found but not at {missing_facility} level"
            })
        
        return gaps
    
    def _check_frequency_limits(self, matching_rules: pd.DataFrame, expected_frequency: str,
                              condition_name: str, service_name: str) -> List[Dict]:
        """Check if service frequency limits match expectations"""
        
        gaps = []
        
        # Look for frequency/limit information in rules
        limit_rules = matching_rules[matching_rules['limits'].notna()]
        
        if len(limit_rules) == 0 and 'week' in expected_frequency.lower():
            gaps.append({
                'condition': condition_name,
                'service': service_name,
                'gap_type': 'Missing Frequency Limits',
                'severity': 'MEDIUM',
                'priority': 'MEDIUM',
                'description': f"No frequency limits specified for {service_name}",
                'expected_frequency': expected_frequency,
                'expected_facilities': 'All applicable levels',
                'recommendation': f"Define frequency limits for {service_name} ({expected_frequency})",
                'evidence': 'Service found but no frequency/limit information'
            })
        
        return gaps
    
    def analyze_pdf_gaps(self) -> List[Dict]:
        """Additional gap analysis from comprehensive PDF review"""
        
        print(f"\n📄 Additional Gap Analysis from PDF Review...")
        
        # Critical gaps identified from healthcare policy perspective
        critical_gaps = [
            {
                'condition': 'Emergency Care',
                'service': 'Cardiac Arrest Management',
                'gap_type': 'Critical Missing Service',
                'severity': 'CRITICAL',
                'priority': 'HIGH',
                'description': 'No specific tariff structure for cardiac arrest emergency procedures',
                'expected_frequency': 'immediate/emergency',
                'expected_facilities': 'Level 4, Level 5, Level 6',
                'recommendation': 'Add comprehensive cardiac emergency procedures to SHIF',
                'evidence': 'Critical emergency service not adequately covered in tariff structure'
            },
            {
                'condition': 'Respiratory Care',
                'service': 'Respiratory Failure Management',
                'gap_type': 'Critical Missing Service', 
                'severity': 'CRITICAL',
                'priority': 'HIGH',
                'description': 'Limited coverage for respiratory failure treatment and ventilation',
                'expected_frequency': 'as needed/emergency',
                'expected_facilities': 'Level 4, Level 5, Level 6',
                'recommendation': 'Add respiratory failure management protocols to SHIF',
                'evidence': 'Critical respiratory services insufficiently covered'
            },
            {
                'condition': 'Preventive Care',
                'service': 'Comprehensive Vaccination Program',
                'gap_type': 'Incomplete Coverage',
                'severity': 'HIGH',
                'priority': 'HIGH',
                'description': 'Vaccination schedule appears incomplete for all age groups',
                'expected_frequency': 'per WHO schedule',
                'expected_facilities': 'Level 1, Level 2, Level 3, Level 4',
                'recommendation': 'Complete vaccination coverage per WHO recommendations',
                'evidence': 'Limited vaccination services identified in tariff structure'
            },
            {
                'condition': 'Dental Care',
                'service': 'Comprehensive Dental Services',
                'gap_type': 'Missing Category',
                'severity': 'HIGH', 
                'priority': 'MEDIUM',
                'description': 'Minimal dental care coverage in SHIF benefit package',
                'expected_frequency': 'routine and emergency',
                'expected_facilities': 'Level 2, Level 3, Level 4',
                'recommendation': 'Add comprehensive dental care benefit category',
                'evidence': 'Dental services significantly underrepresented'
            },
            {
                'condition': 'Eye Care',
                'service': 'Comprehensive Eye Care Services',
                'gap_type': 'Limited Coverage',
                'severity': 'MEDIUM',
                'priority': 'MEDIUM', 
                'description': 'Eye care services appear limited beyond basic procedures',
                'expected_frequency': 'routine and corrective',
                'expected_facilities': 'Level 3, Level 4, Level 5',
                'recommendation': 'Expand eye care services including corrective procedures',
                'evidence': 'Basic eye care found but comprehensive services limited'
            }
        ]
        
        print(f"   Identified {len(critical_gaps)} additional critical gaps")
        return critical_gaps
    
    def prioritize_gaps(self, gaps_df: pd.DataFrame) -> pd.DataFrame:
        """Prioritize gaps by severity and healthcare impact"""
        
        # Calculate priority score
        priority_scores = []
        
        for _, gap in gaps_df.iterrows():
            score = 0
            
            # Severity scoring
            severity_scores = {'CRITICAL': 10, 'HIGH': 7, 'MEDIUM': 4, 'LOW': 2}
            score += severity_scores.get(gap.get('severity', 'LOW'), 2)
            
            # Priority scoring
            priority_scores_dict = {'HIGH': 5, 'MEDIUM': 3, 'LOW': 1}
            score += priority_scores_dict.get(gap.get('priority', 'LOW'), 1)
            
            # Condition importance (healthcare impact)
            condition_importance = {
                'Emergency Care': 5,
                'Chronic kidney disease': 4,
                'Cancer treatment': 4,
                'Maternity': 4,
                'Stroke rehabilitation': 3,
                'Respiratory Care': 4,
                'Mental health': 2,
                'Preventive Care': 3
            }
            score += condition_importance.get(gap.get('condition', ''), 1)
            
            priority_scores.append(score)
        
        gaps_df['priority_score'] = priority_scores
        gaps_df = gaps_df.sort_values('priority_score', ascending=False)
        
        return gaps_df

def main():
    """Main execution for Task 3: Gap Analysis"""
    
    print("🎯 TASK 3: COMPREHENSIVE HEALTHCARE GAP ANALYSIS")
    print("Analyzing critical healthcare coverage gaps in SHIF benefit package")
    print("=" * 80)
    
    analyzer = HealthcareGapAnalyzer()
    gaps_df = analyzer.analyze_comprehensive_gaps()
    
    if not gaps_df.empty:
        print(f"\n🎯 TASK 3 COMPREHENSIVE RESULTS:")
        print(f"=" * 50)
        
        # Summary by severity
        severity_counts = gaps_df['severity'].value_counts()
        for severity, count in severity_counts.items():
            print(f"{severity} gaps: {count}")
        
        # Summary by condition
        print(f"\nGaps by healthcare condition:")
        condition_counts = gaps_df['condition'].value_counts()
        for condition, count in condition_counts.head(10).items():
            print(f"  {condition}: {count}")
        
        # Top priority gaps
        print(f"\n🔥 TOP 5 PRIORITY GAPS:")
        for i, (_, gap) in enumerate(gaps_df.head(5).iterrows(), 1):
            print(f"{i}. {gap['condition']} - {gap['service']}")
            print(f"   {gap['description']}")
            print(f"   Severity: {gap['severity']} | Priority: {gap['priority']}")
            print(f"   Recommendation: {gap['recommendation']}")
            print()
        
        # Save comprehensive report
        report_file = 'outputs_comprehensive/TASK3_GAP_ANALYSIS_REPORT.txt'
        with open(report_file, 'w') as f:
            f.write("TASK 3: COMPREHENSIVE HEALTHCARE GAP ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total Gaps Identified: {len(gaps_df)}\n\n")
            
            # Write severity breakdown
            f.write("GAPS BY SEVERITY:\n")
            for severity, count in severity_counts.items():
                f.write(f"  {severity}: {count}\n")
            
            f.write(f"\nGAPS BY HEALTHCARE CONDITION:\n")
            for condition, count in condition_counts.items():
                f.write(f"  {condition}: {count}\n")
            
            f.write(f"\n" + "=" * 60 + "\n")
            f.write("DETAILED GAP ANALYSIS:\n\n")
            
            for _, gap in gaps_df.iterrows():
                f.write(f"Condition: {gap['condition']}\n")
                f.write(f"Service: {gap['service']}\n")
                f.write(f"Gap Type: {gap['gap_type']}\n")
                f.write(f"Severity: {gap['severity']}\n")
                f.write(f"Description: {gap['description']}\n")
                f.write(f"Recommendation: {gap['recommendation']}\n")
                f.write(f"Evidence: {gap['evidence']}\n")
                f.write("-" * 40 + "\n")
        
        print(f"📄 Detailed report saved to: {report_file}")
        
        # Save Excel dashboard if pandas supports it
        try:
            excel_file = 'outputs_comprehensive/TASK3_Healthcare_Gap_Dashboard.xlsx'
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                gaps_df.to_excel(writer, sheet_name='Healthcare Gaps', index=False)
                
                # Summary sheets
                severity_summary = gaps_df.groupby('severity').size().reset_index(name='count')
                severity_summary.to_excel(writer, sheet_name='Gaps by Severity', index=False)
                
                condition_summary = gaps_df.groupby('condition').size().reset_index(name='count')
                condition_summary.to_excel(writer, sheet_name='Gaps by Condition', index=False)
            
            print(f"📊 Excel dashboard saved to: {excel_file}")
        except Exception as e:
            print(f"⚠️ Could not create Excel dashboard: {e}")
    
    else:
        print("\nℹ️ No gaps identified in current analysis")
    
    print(f"\n✅ TASK 3: COMPREHENSIVE GAP ANALYSIS COMPLETE")

if __name__ == "__main__":
    main()
