#!/usr/bin/env python3
"""
Enhanced Clinical Excel Dashboard Generator
Creates Excel dashboards optimized for healthcare professionals and clinical reviewers

Author: Pranay for Dr. Rishi
Date: August 24, 2025
"""

import pandas as pd
import xlsxwriter
from datetime import datetime
from typing import Dict, List, Optional
import json
import numpy as np

class ClinicalExcelDashboard:
    """Creates healthcare-focused Excel dashboards"""
    
    def __init__(self):
        self.workbook = None
        self.formats = {}
    
    def setup_formats(self, workbook: xlsxwriter.Workbook):
        """Setup Excel formatting styles for clinical use"""
        self.formats = {
            'title': workbook.add_format({
                'bold': True, 
                'font_size': 18, 
                'bg_color': '#2E8B57',  # Clinical green
                'font_color': 'white',
                'align': 'center'
            }),
            'header': workbook.add_format({
                'bold': True, 
                'bg_color': '#90EE90',  # Light green
                'border': 1,
                'align': 'center'
            }),
            'subheader': workbook.add_format({
                'bold': True, 
                'bg_color': '#F0F8FF',  # Alice blue
                'border': 1
            }),
            'money': workbook.add_format({
                'num_format': 'KES #,##0.00',
                'border': 1
            }),
            'number': workbook.add_format({
                'num_format': '#,##0',
                'border': 1
            }),
            'percentage': workbook.add_format({
                'num_format': '0.0%',
                'border': 1
            }),
            'critical': workbook.add_format({
                'bg_color': '#FFB6C1',  # Light pink for critical items
                'border': 1
            }),
            'warning': workbook.add_format({
                'bg_color': '#FFFFE0',  # Light yellow for warnings
                'border': 1
            }),
            'good': workbook.add_format({
                'bg_color': '#98FB98',  # Pale green for good status
                'border': 1
            }),
            'text_wrap': workbook.add_format({
                'text_wrap': True,
                'border': 1,
                'valign': 'top'
            })
        }
    
    def create_clinical_overview_sheet(self, workbook: xlsxwriter.Workbook, 
                                     rules_df: pd.DataFrame, 
                                     contradictions_df: pd.DataFrame):
        """Create clinical overview sheet for healthcare professionals"""
        sheet = workbook.add_worksheet('Clinical Overview')
        
        # Title
        sheet.merge_range('A1:F1', 'SHIF Benefits Analysis - Clinical Overview', self.formats['title'])
        sheet.write('A2', f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        
        row = 4
        
        # Healthcare Service Categories Analysis
        sheet.write(f'A{row}', 'HEALTHCARE SERVICE CATEGORIES', self.formats['header'])
        row += 1
        
        # Analyze by medical categories
        if 'category' in rules_df.columns:
            # Check which tariff column exists
            tariff_col = 'tariff_value' if 'tariff_value' in rules_df.columns else 'tariff'
            
            category_stats = rules_df.groupby('category').agg({
                'service': 'count',
                tariff_col: ['mean', 'min', 'max']
            }).round(2)
            
            sheet.write(f'A{row}', 'Category', self.formats['subheader'])
            sheet.write(f'B{row}', 'Rule Count', self.formats['subheader'])
            sheet.write(f'C{row}', 'Avg Tariff', self.formats['subheader'])
            sheet.write(f'D{row}', 'Min Tariff', self.formats['subheader'])
            sheet.write(f'E{row}', 'Max Tariff', self.formats['subheader'])
            row += 1
            
            for category, stats in category_stats.iterrows():
                sheet.write(f'A{row}', category)
                sheet.write(f'B{row}', int(stats[('service', 'count')]), self.formats['number'])
                
                avg_tariff = stats[(tariff_col, 'mean')]
                min_tariff = stats[(tariff_col, 'min')]
                max_tariff = stats[(tariff_col, 'max')]
                
                if not np.isnan(avg_tariff):
                    sheet.write(f'C{row}', avg_tariff, self.formats['money'])
                    sheet.write(f'D{row}', min_tariff, self.formats['money'])
                    sheet.write(f'E{row}', max_tariff, self.formats['money'])
                else:
                    sheet.write(f'C{row}', 'N/A')
                    sheet.write(f'D{row}', 'N/A')
                    sheet.write(f'E{row}', 'N/A')
                
                row += 1
        
        row += 2
        
        # Critical Healthcare Areas
        sheet.write(f'A{row}', 'CRITICAL HEALTHCARE AREAS STATUS', self.formats['header'])
        row += 1
        
        critical_areas = {
            'Emergency Services': ['emergency', 'trauma', 'urgent'],
            'Chronic Disease Management': ['dialysis', 'diabetes', 'hypertension'],
            'Maternal Health': ['delivery', 'maternity', 'pregnancy', 'caesarean'],
            'Cancer Care': ['chemotherapy', 'oncology', 'radiation'],
            'Surgical Procedures': ['surgery', 'surgical', 'operation'],
            'Diagnostic Imaging': ['mri', 'ct scan', 'x-ray', 'ultrasound']
        }
        
        sheet.write(f'A{row}', 'Healthcare Area', self.formats['subheader'])
        sheet.write(f'B{row}', 'Rules Found', self.formats['subheader'])
        sheet.write(f'C{row}', 'Contradictions', self.formats['subheader'])
        sheet.write(f'D{row}', 'Status', self.formats['subheader'])
        row += 1
        
        for area, keywords in critical_areas.items():
            # Count rules in this area
            area_rules = 0
            area_contradictions = 0
            
            for keyword in keywords:
                area_rules += rules_df['service'].str.contains(keyword, case=False, na=False).sum()
                if not contradictions_df.empty and 'service' in contradictions_df.columns:
                    area_contradictions += contradictions_df['service'].str.contains(keyword, case=False, na=False).sum()
            
            sheet.write(f'A{row}', area)
            sheet.write(f'B{row}', area_rules, self.formats['number'])
            sheet.write(f'C{row}', area_contradictions, self.formats['number'])
            
            # Status assessment
            if area_rules == 0:
                status = "No Coverage Found"
                status_format = self.formats['critical']
            elif area_contradictions > 0:
                status = "Needs Review"
                status_format = self.formats['warning']
            else:
                status = "Appears Complete"
                status_format = self.formats['good']
            
            sheet.write(f'D{row}', status, status_format)
            row += 1
        
        # Column widths
        sheet.set_column('A:A', 25)
        sheet.set_column('B:E', 15)
    
    def create_facility_level_analysis(self, workbook: xlsxwriter.Workbook, rules_df: pd.DataFrame):
        """Analyze coverage by healthcare facility levels"""
        sheet = workbook.add_worksheet('Facility Level Analysis')
        
        sheet.merge_range('A1:E1', 'Healthcare Facility Level Coverage Analysis', self.formats['title'])
        
        row = 3
        sheet.write(f'A{row}', 'COVERAGE BY FACILITY LEVEL', self.formats['header'])
        row += 2
        
        # Parse facility levels from rules
        facility_coverage = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        service_by_level = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
        
        for _, rule in rules_df.iterrows():
            v = rule.get('facility_levels', None)
            if v is None:
                continue
            try:
                # Accept both JSON string and list
                if isinstance(v, str):
                    v = v.strip()
                    if not v:
                        continue
                    try:
                        levels = json.loads(v)
                    except Exception:
                        # Fallback: extract digits if string is like "Level 2-3"
                        import re as _re
                        nums = [int(x) for x in _re.findall(r"[1-6]", v)]
                        levels = sorted(set(nums))
                elif isinstance(v, (list, tuple)):
                    levels = list(v)
                else:
                    # Unsupported type
                    continue

                if isinstance(levels, list):
                    for level in levels:
                        try:
                            lvl = int(level)
                        except Exception:
                            continue
                        if 1 <= lvl <= 6:
                            facility_coverage[lvl] += 1
                            service_by_level[lvl].append(rule.get('service', 'Unknown'))
            except Exception:
                continue
        
        # Write facility level summary
        sheet.write(f'A{row}', 'Facility Level', self.formats['subheader'])
        sheet.write(f'B{row}', 'Services Count', self.formats['subheader'])
        sheet.write(f'C{row}', 'Coverage Description', self.formats['subheader'])
        sheet.write(f'D{row}', 'Clinical Significance', self.formats['subheader'])
        row += 1
        
        level_descriptions = {
            1: "Community Health Units",
            2: "Dispensaries", 
            3: "Health Centres",
            4: "Sub-County Hospitals",
            5: "County Referral Hospitals",
            6: "National Referral Hospitals"
        }
        
        clinical_significance = {
            1: "Primary care, health promotion",
            2: "Basic outpatient services",
            3: "Comprehensive outpatient, basic inpatient",
            4: "Specialized services, surgery",
            5: "Advanced specialist care",
            6: "Highly specialized, tertiary care"
        }
        
        for level in range(1, 7):
            sheet.write(f'A{row}', f"Level {level}")
            sheet.write(f'B{row}', facility_coverage[level], self.formats['number'])
            sheet.write(f'C{row}', level_descriptions[level])
            sheet.write(f'D{row}', clinical_significance[level])
            row += 1
        
        # Add service details for each level
        row += 2
        sheet.write(f'A{row}', 'DETAILED SERVICES BY LEVEL', self.formats['header'])
        row += 2
        
        for level in range(1, 7):
            if facility_coverage[level] > 0:
                sheet.write(f'A{row}', f'Level {level} Services:', self.formats['subheader'])
                row += 1
                
                # List services (up to 10 per level)
                services = service_by_level[level][:10]
                for service in services:
                    sheet.write(f'B{row}', service[:50] + "..." if len(service) > 50 else service)
                    row += 1
                
                if len(service_by_level[level]) > 10:
                    sheet.write(f'B{row}', f"... and {len(service_by_level[level]) - 10} more")
                    row += 1
                
                row += 1
        
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:D', 30)
    
    def create_clinical_contradictions_sheet(self, workbook: xlsxwriter.Workbook, 
                                           contradictions_df: pd.DataFrame):
        """Create clinician-friendly contradictions analysis"""
        sheet = workbook.add_worksheet('Clinical Contradictions')
        
        sheet.merge_range('A1:G1', 'Clinical Contradictions Requiring Review', self.formats['title'])
        
        row = 3
        
        # Priority classification
        if not contradictions_df.empty:
            sheet.write(f'A{row}', 'PRIORITY CLASSIFICATION', self.formats['header'])
            row += 2
            
            # Classify by clinical priority
            high_priority_services = ['dialysis', 'emergency', 'delivery', 'surgery', 'chemotherapy']
            medium_priority_services = ['consultation', 'imaging', 'laboratory']
            
            contradictions_df['clinical_priority'] = 'Low'
            
            for service in high_priority_services:
                mask = contradictions_df['service'].str.contains(service, case=False, na=False)
                contradictions_df.loc[mask, 'clinical_priority'] = 'High'
            
            for service in medium_priority_services:
                mask = contradictions_df['service'].str.contains(service, case=False, na=False)
                high_mask = contradictions_df['clinical_priority'] == 'High'
                contradictions_df.loc[mask & ~high_mask, 'clinical_priority'] = 'Medium'
            
            # Priority summary
            priority_counts = contradictions_df['clinical_priority'].value_counts()
            
            sheet.write(f'A{row}', 'Priority Level', self.formats['subheader'])
            sheet.write(f'B{row}', 'Count', self.formats['subheader'])
            sheet.write(f'C{row}', 'Clinical Impact', self.formats['subheader'])
            row += 1
            
            priority_impact = {
                'High': 'Patient safety, life-threatening conditions',
                'Medium': 'Diagnosis, treatment effectiveness', 
                'Low': 'Administrative, process efficiency'
            }
            
            for priority in ['High', 'Medium', 'Low']:
                count = priority_counts.get(priority, 0)
                sheet.write(f'A{row}', priority)
                sheet.write(f'B{row}', count, self.formats['number'])
                sheet.write(f'C{row}', priority_impact[priority])
                row += 1
            
            row += 2
            
            # Detailed contradictions by priority
            for priority in ['High', 'Medium', 'Low']:
                priority_contradictions = contradictions_df[contradictions_df['clinical_priority'] == priority]
                
                if not priority_contradictions.empty:
                    sheet.write(f'A{row}', f'{priority} Priority Contradictions', self.formats['header'])
                    row += 1
                    
                    # Headers
                    headers = ['Service', 'Type', 'Details', 'Evidence Page', 'Clinical Notes']
                    for col, header in enumerate(headers):
                        sheet.write(row, col, header, self.formats['subheader'])
                    row += 1
                    
                    # Data
                    for _, contradiction in priority_contradictions.head(10).iterrows():
                        sheet.write(row, 0, contradiction.get('service', '')[:40])
                        sheet.write(row, 1, contradiction.get('type', ''))
                        sheet.write(row, 2, contradiction.get('details', '')[:60])
                        sheet.write(row, 3, str(contradiction.get('left_page', '')))
                        
                        # Clinical notes based on contradiction type
                        clinical_note = ""
                        if contradiction.get('type') == 'Tariff':
                            clinical_note = "Review pricing impact on patient access"
                        elif contradiction.get('type') == 'Limit':
                            clinical_note = "Verify clinical appropriateness of limits"
                        elif contradiction.get('type') == 'Coverage':
                            clinical_note = "Clarify coverage eligibility criteria"
                        elif contradiction.get('type') == 'Facility':
                            clinical_note = "Check facility capability requirements"
                        
                        sheet.write(row, 4, clinical_note)
                        row += 1
                    
                    row += 2
        
        sheet.set_column('A:A', 25)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 35)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 35)
    
    def create_validation_tracking_sheet(self, workbook: xlsxwriter.Workbook, rules_df: pd.DataFrame):
        """Create validation tracking sheet for clinical review workflow"""
        sheet = workbook.add_worksheet('Validation Tracking')
        
        sheet.merge_range('A1:F1', 'Clinical Validation Tracking Worksheet', self.formats['title'])
        
        row = 3
        sheet.write(f'A{row}', 'VALIDATION CHECKLIST', self.formats['header'])
        row += 2
        
        # Headers for validation tracking
        headers = ['Service Name', 'Category', 'Tariff (KES)', 'Source Page', 'Clinical Reviewer', 'Validation Status', 'Notes']
        for col, header in enumerate(headers):
            sheet.write(row, col, header, self.formats['subheader'])
        row += 1
        
        # Sample of rules to validate (first 20)
        sample_rules = rules_df.head(20) if len(rules_df) > 20 else rules_df
        
        for _, rule in sample_rules.iterrows():
            sheet.write(row, 0, rule.get('service', '')[:40])
            sheet.write(row, 1, rule.get('category', ''))
            
            tariff = rule.get('tariff_value')
            if pd.notna(tariff):
                sheet.write(row, 2, float(tariff), self.formats['money'])
            else:
                sheet.write(row, 2, 'N/A')
            
            sheet.write(row, 3, str(rule.get('source_page', '')))
            
            # Empty cells for clinical reviewer to fill
            sheet.write(row, 4, '')  # Clinical Reviewer
            sheet.write(row, 5, '')  # Validation Status  
            sheet.write(row, 6, '')  # Notes
            
            row += 1
        
        # Add validation status dropdown
        row += 2
        sheet.write(f'A{row}', 'VALIDATION STATUS OPTIONS:', self.formats['header'])
        row += 1
        
        validation_options = [
            '✓ Verified Correct',
            '⚠ Needs Clarification', 
            '✗ Incorrect - Needs Fix',
            '? Unable to Verify',
            '- Not Applicable'
        ]
        
        for option in validation_options:
            sheet.write(f'A{row}', option)
            row += 1
        
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 15) 
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 12)
        sheet.set_column('E:F', 20)
        sheet.set_column('G:G', 40)
    
    def create_dashboard(self, rules_df: pd.DataFrame, contradictions_df: pd.DataFrame, 
                        gaps_df: pd.DataFrame, output_path: str):
        """Create the complete clinical Excel dashboard"""
        
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            self.setup_formats(workbook)
            
            # Create all sheets
            self.create_clinical_overview_sheet(workbook, rules_df, contradictions_df)
            self.create_facility_level_analysis(workbook, rules_df)
            
            if not contradictions_df.empty:
                self.create_clinical_contradictions_sheet(workbook, contradictions_df)
            
            self.create_validation_tracking_sheet(workbook, rules_df)

            # Summary & Methods sheet
            summary = workbook.add_worksheet('Summary & Methods')
            summary.write('A1', 'Summary & Methods (Flagged for Validation)', self.formats['title'])
            row = 3
            bullets = [
                'Hybrid extraction: regex + OpenAI (gpt-5-mini primary; gpt-4.1-mini fallback) per line/row.',
                'Evidence: page number with 200–240 character snippet for context.',
                'Units: normalized to per_session/visit/day/scan/month/year; household/beneficiary as limits.',
                'Facility levels: normalized to lists of 1–6; ranges (e.g., 4–6) expanded.',
                'Contradictions: Tariff, Limit, Coverage, Facility-exclusion; tariff grouped by (service_key, tariff_unit).',
                'Gaps: YAML-driven expectations; statuses are NO COVERAGE FOUND / MINIMAL COVERAGE.',
                'All findings flagged for validation; not confirmed without expert review.'
            ]
            summary.write(row, 0, 'Methods & Assumptions', self.formats['header']); row += 1
            for b in bullets:
                summary.write(row, 0, f'- {b}'); row += 1
            row += 1
            summary.write(row, 0, 'Worked Example (Illustrative)', self.formats['header']); row += 1
            summary.write(row, 0, 'Example: Tariff conflict for the same service/unit with KES variance across pages.'); row += 1
            summary.write(row, 0, 'Note: All figures are flagged for validation and require expert confirmation.'); row += 1
            
            # Add original data sheets with formatting
            rules_sheet = workbook.add_worksheet('Raw Rules Data')
            rules_df.to_excel(writer, sheet_name='Raw Rules Data', index=False, startrow=1)
            rules_sheet.write('A1', 'Complete Rules Dataset - Raw Data', self.formats['header'])
            
            if not contradictions_df.empty:
                contradictions_sheet = workbook.add_worksheet('Raw Contradictions')
                contradictions_df.to_excel(writer, sheet_name='Raw Contradictions', index=False, startrow=1)
                contradictions_sheet.write('A1', 'Detected Contradictions - Raw Data', self.formats['header'])
            
            if not gaps_df.empty:
                gaps_sheet = workbook.add_worksheet('Coverage Gaps')
                gaps_df.to_excel(writer, sheet_name='Coverage Gaps', index=False, startrow=1)
                gaps_sheet.write('A1', 'Identified Coverage Gaps', self.formats['header'])
        
        print(f"✅ Enhanced clinical Excel dashboard created: {output_path}")
        print(f"📊 {len(rules_df)} rules, {len(contradictions_df)} contradictions analyzed")

# Example usage function
def create_clinical_excel_dashboard(rules_df: pd.DataFrame, contradictions_df: pd.DataFrame,
                                  gaps_df: pd.DataFrame, output_path: str = "clinical_shif_analysis.xlsx"):
    """Convenience function to create clinical dashboard"""
    dashboard = ClinicalExcelDashboard()
    dashboard.create_dashboard(rules_df, contradictions_df, gaps_df, output_path)

if __name__ == "__main__":
    # Example usage
    print("🏥 Clinical Excel Dashboard Generator")
    print("Use create_clinical_excel_dashboard() function to generate enhanced dashboards")
