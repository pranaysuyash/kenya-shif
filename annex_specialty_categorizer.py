#!/usr/bin/env python3
"""
Annex Specialty Categorizer
Properly extracts and categorizes annex tariff data by medical specialties
Pages 19-54 contain structured data: ID | Specialty | Procedure | Tariff
"""

import pandas as pd
import pdfplumber
import re
import json
from typing import Dict, List

class AnnexSpecialtyCategorizer:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.specialty_data = {}
        
    def extract_annex_by_specialties(self) -> Dict:
        """Extract annex data organized by medical specialties"""
        
        print("🏥 ANNEX SPECIALTY CATEGORIZATION (Pages 19-54)")
        print("=" * 55)
        
        with pdfplumber.open(self.pdf_path) as pdf:
            # Focus on annex pages (19-54) where tariff tables are located
            for page_num in range(18, min(54, len(pdf.pages))):  # Pages 19-54
                print(f"   📄 Processing page {page_num + 1}...")
                page = pdf.pages[page_num]
                
                # Extract tables from this page
                tables = page.extract_tables()
                
                if tables:
                    for table_idx, table in enumerate(tables):
                        if table and len(table) > 1:
                            self._process_annex_table(table, page_num + 1, table_idx)
                
                # Also extract text for any missed structured data
                text = page.extract_text()
                if text:
                    self._process_annex_text(text, page_num + 1)
        
        # Organize and summarize results
        organized_results = self._organize_by_specialties()
        return organized_results
    
    def _process_annex_table(self, table: List, page_num: int, table_idx: int):
        """Process a single annex table to extract specialty-organized data"""
        
        for row_idx, row in enumerate(table):
            if not row or len(row) < 3:
                continue
            
            # Parse row: typically [ID, Specialty, Procedure, Tariff]
            row_data = self._parse_annex_row(row, page_num, table_idx, row_idx)
            
            if row_data and row_data['specialty']:
                specialty = row_data['specialty']
                
                # Initialize specialty if not exists
                if specialty not in self.specialty_data:
                    self.specialty_data[specialty] = {
                        'specialty_name': specialty,
                        'procedures': [],
                        'tariff_range': {'min': float('inf'), 'max': 0},
                        'total_procedures': 0,
                        'pages_found': set(),
                        'avg_tariff': 0
                    }
                
                # Add procedure to specialty
                self.specialty_data[specialty]['procedures'].append(row_data)
                self.specialty_data[specialty]['pages_found'].add(page_num)
                self.specialty_data[specialty]['total_procedures'] += 1
                
                # Update tariff range
                if row_data['tariff'] and row_data['tariff'] > 0:
                    current_min = self.specialty_data[specialty]['tariff_range']['min']
                    current_max = self.specialty_data[specialty]['tariff_range']['max']
                    
                    self.specialty_data[specialty]['tariff_range']['min'] = min(current_min, row_data['tariff'])
                    self.specialty_data[specialty]['tariff_range']['max'] = max(current_max, row_data['tariff'])
    
    def _parse_annex_row(self, row: List, page_num: int, table_idx: int, row_idx: int) -> Dict:
        """Parse a single row from annex table"""
        
        # Clean row data
        clean_row = [str(cell).strip() if cell else '' for cell in row]
        
        # Skip headers and empty rows
        if not any(clean_row) or any(header in ' '.join(clean_row).lower() for header in ['specialty', 'procedure', 'tariff']):
            return None
        
        # Typical structure: [ID, Specialty, Procedure, Tariff]
        row_data = {
            'procedure_id': '',
            'specialty': '',
            'procedure_name': '',
            'tariff': 0,
            'page_num': page_num,
            'table_idx': table_idx,
            'row_idx': row_idx,
            'raw_row': clean_row
        }
        
        if len(clean_row) >= 4:
            # Standard 4-column format
            row_data['procedure_id'] = clean_row[0]
            row_data['specialty'] = self._clean_specialty_name(clean_row[1])
            row_data['procedure_name'] = clean_row[2]
            row_data['tariff'] = self._parse_tariff(clean_row[3])
            
        elif len(clean_row) >= 3:
            # 3-column format (may be missing ID or merged columns)
            if clean_row[0].isdigit():
                row_data['procedure_id'] = clean_row[0]
                row_data['specialty'] = self._clean_specialty_name(clean_row[1])
                row_data['procedure_name'] = clean_row[2]
            else:
                row_data['specialty'] = self._clean_specialty_name(clean_row[0])
                row_data['procedure_name'] = clean_row[1]
                row_data['tariff'] = self._parse_tariff(clean_row[2])
        
        # Validate that we have meaningful data
        if row_data['specialty'] and row_data['procedure_name'] and len(row_data['procedure_name']) > 5:
            return row_data
        
        return None
    
    def _clean_specialty_name(self, specialty: str) -> str:
        """Clean and standardize specialty names"""
        if not specialty or not isinstance(specialty, str):
            return ''
        
        # Remove common artifacts
        specialty = specialty.strip()
        specialty = re.sub(r'^\d+\.?\s*', '', specialty)  # Remove leading numbers
        
        # Standardize common specialty names
        specialty_mapping = {
            'cardio': 'Cardiology',
            'cardiac': 'Cardiology', 
            'ophthalmic': 'Ophthalmology',
            'eye': 'Ophthalmology',
            'ortho': 'Orthopedic',
            'orthopedic': 'Orthopedic',
            'paediatric': 'Pediatric',
            'pediatric': 'Pediatric',
            'child': 'Pediatric',
            'neuro': 'Neurology',
            'neurological': 'Neurology',
            'general': 'General Surgery',
            'surgery': 'General Surgery',
            'dental': 'Dental',
            'oral': 'Dental'
        }
        
        specialty_lower = specialty.lower()
        for key, standard_name in specialty_mapping.items():
            if key in specialty_lower:
                return standard_name
        
        # Capitalize first letter for consistency
        return specialty.capitalize() if specialty else ''
    
    def _parse_tariff(self, tariff_text: str) -> float:
        """Parse tariff amount from text"""
        if not tariff_text or not isinstance(tariff_text, str):
            return 0
        
        # Remove KES, commas, and extract number
        tariff_clean = re.sub(r'[^\d,.]', '', tariff_text)
        tariff_clean = tariff_clean.replace(',', '')
        
        try:
            return float(tariff_clean) if tariff_clean else 0
        except:
            return 0
    
    def _process_annex_text(self, text: str, page_num: int):
        """Process page text for any missed specialty data"""
        
        # Look for tariff line patterns
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if len(line) < 20:
                continue
            
            # Look for pattern: ID Specialty Procedure Tariff
            match = re.match(r'(\d+)\s+([A-Za-z]+)\s+(.+?)\s+(\d{1,3},?\d{3})', line)
            if match:
                procedure_id, specialty, procedure, tariff_text = match.groups()
                
                row_data = {
                    'procedure_id': procedure_id,
                    'specialty': self._clean_specialty_name(specialty),
                    'procedure_name': procedure.strip(),
                    'tariff': self._parse_tariff(tariff_text),
                    'page_num': page_num,
                    'source': 'text_extraction'
                }
                
                if row_data['specialty'] and row_data['procedure_name']:
                    specialty = row_data['specialty']
                    
                    if specialty not in self.specialty_data:
                        self.specialty_data[specialty] = {
                            'specialty_name': specialty,
                            'procedures': [],
                            'tariff_range': {'min': float('inf'), 'max': 0},
                            'total_procedures': 0,
                            'pages_found': set(),
                            'avg_tariff': 0
                        }
                    
                    self.specialty_data[specialty]['procedures'].append(row_data)
                    self.specialty_data[specialty]['pages_found'].add(page_num)
                    self.specialty_data[specialty]['total_procedures'] += 1
                    
                    if row_data['tariff'] > 0:
                        current_min = self.specialty_data[specialty]['tariff_range']['min']
                        current_max = self.specialty_data[specialty]['tariff_range']['max']
                        
                        self.specialty_data[specialty]['tariff_range']['min'] = min(current_min, row_data['tariff'])
                        self.specialty_data[specialty]['tariff_range']['max'] = max(current_max, row_data['tariff'])
    
    def _organize_by_specialties(self) -> Dict:
        """Organize results by medical specialties"""
        
        # Calculate averages and finalize data
        for specialty in self.specialty_data:
            specialty_info = self.specialty_data[specialty]
            
            # Calculate average tariff
            tariffs = [p['tariff'] for p in specialty_info['procedures'] if p['tariff'] > 0]
            if tariffs:
                specialty_info['avg_tariff'] = sum(tariffs) / len(tariffs)
            
            # Fix infinite min values
            if specialty_info['tariff_range']['min'] == float('inf'):
                specialty_info['tariff_range']['min'] = 0
            
            # Convert set to list for JSON serialization
            specialty_info['pages_found'] = sorted(list(specialty_info['pages_found']))
        
        # Create summary
        summary = {
            'total_specialties': len(self.specialty_data),
            'total_procedures': sum(s['total_procedures'] for s in self.specialty_data.values()),
            'specialties_list': list(self.specialty_data.keys()),
            'pages_processed': list(range(19, 55))
        }
        
        return {
            'specialties': self.specialty_data,
            'summary': summary
        }
    
    def save_specialty_results(self, results: Dict, output_dir: str):
        """Save specialty-organized results"""
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save complete results as JSON
        with open(f"{output_dir}/annex_specialties_complete.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        # Create specialty summary CSV
        specialty_summaries = []
        for specialty_name, specialty_data in results['specialties'].items():
            summary = {
                'specialty': specialty_name,
                'total_procedures': specialty_data['total_procedures'],
                'min_tariff': specialty_data['tariff_range']['min'],
                'max_tariff': specialty_data['tariff_range']['max'],
                'avg_tariff': round(specialty_data['avg_tariff'], 2),
                'pages_found': ', '.join(map(str, specialty_data['pages_found']))
            }
            specialty_summaries.append(summary)
        
        specialty_df = pd.DataFrame(specialty_summaries)
        specialty_df = specialty_df.sort_values('total_procedures', ascending=False)
        specialty_df.to_csv(f"{output_dir}/specialty_summaries.csv", index=False)
        
        # Create detailed procedures CSV
        all_procedures = []
        for specialty_name, specialty_data in results['specialties'].items():
            for procedure in specialty_data['procedures']:
                procedure_row = {
                    'specialty': specialty_name,
                    'procedure_id': procedure.get('procedure_id', ''),
                    'procedure_name': procedure['procedure_name'],
                    'tariff_kes': procedure['tariff'],
                    'page_num': procedure['page_num']
                }
                all_procedures.append(procedure_row)
        
        procedures_df = pd.DataFrame(all_procedures)
        procedures_df = procedures_df.sort_values(['specialty', 'tariff_kes'], ascending=[True, False])
        procedures_df.to_csv(f"{output_dir}/annex_procedures_by_specialty.csv", index=False)
        
        print(f"📁 Specialty results saved to: {output_dir}")
        return output_dir

def main():
    """Run annex specialty categorization"""
    
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    output_dir = f"annex_specialties_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
    
    categorizer = AnnexSpecialtyCategorizer(pdf_path)
    results = categorizer.extract_annex_by_specialties()
    
    print(f"\n📊 ANNEX SPECIALTY CATEGORIZATION RESULTS:")
    print(f"   Total specialties found: {results['summary']['total_specialties']}")
    print(f"   Total procedures: {results['summary']['total_procedures']}")
    print(f"   Pages processed: {len(results['summary']['pages_processed'])}")
    
    print(f"\n🏥 SPECIALTIES FOUND:")
    for specialty in sorted(results['specialties'].keys()):
        specialty_data = results['specialties'][specialty]
        print(f"   • {specialty}: {specialty_data['total_procedures']} procedures")
        print(f"     └── Tariff range: KES {specialty_data['tariff_range']['min']:,.0f} - {specialty_data['tariff_range']['max']:,.0f}")
    
    # Save results
    categorizer.save_specialty_results(results, output_dir)

if __name__ == "__main__":
    main()