#!/usr/bin/env python3
"""
AI-Enhanced Hierarchical Service Extractor
Combines the proven hierarchical extraction with AI analysis for better results
"""

import re
import pdfplumber
import pandas as pd
import json
from openai import OpenAI
from typing import List, Dict, Tuple, Optional

class AIEnhancedHierarchicalExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.api_key = ""OPENAI_API_KEY_REMOVED""
        self.client = OpenAI(api_key=self.api_key)
        self.super_headings = []
        self.service_categories = []
        self.services = []
        self.current_hierarchy = {
            'super_heading': None,
            'service_category': None,
            'page_number': 1
        }
    
    def extract_with_ai_enhancement(self) -> Dict:
        """Extract services with AI-enhanced hierarchical structure"""
        
        print("🤖 AI-ENHANCED HIERARCHICAL EXTRACTION")
        print("=" * 50)
        
        with pdfplumber.open(self.pdf_path) as pdf:
            # Focus on critical pages (19-30) first
            critical_pages = list(range(19, 31))
            
            for page_num in critical_pages:
                if page_num <= len(pdf.pages):
                    print(f"   📄 Processing page {page_num} with AI...")
                    page = pdf.pages[page_num - 1]  # pdfplumber is 0-indexed
                    
                    text = page.extract_text()
                    if text:
                        # Process page with AI enhancement
                        self._process_page_with_ai(text, page_num)
        
        # Process final results
        results = {
            'super_headings': self.super_headings,
            'service_categories': self.service_categories, 
            'services': self.services,
            'summary': {
                'total_super_headings': len(self.super_headings),
                'total_service_categories': len(self.service_categories),
                'total_services': len(self.services)
            }
        }
        
        return results
    
    def _process_page_with_ai(self, page_text: str, page_num: int):
        """Process page text with AI to identify hierarchical structure"""
        
        # Break page into manageable chunks for AI processing
        lines = page_text.split('\\n')
        chunks = self._create_text_chunks(lines, 50)  # 50 lines per chunk
        
        for chunk_idx, chunk in enumerate(chunks):
            chunk_text = '\\n'.join(chunk)
            
            if len(chunk_text.strip()) < 100:  # Skip very small chunks
                continue
            
            # Use AI to analyze this chunk
            ai_analysis = self._analyze_chunk_with_ai(chunk_text, page_num, chunk_idx)
            
            if ai_analysis and isinstance(ai_analysis, dict):
                self._process_ai_results(ai_analysis, page_num)
    
    def _create_text_chunks(self, lines: List[str], chunk_size: int) -> List[List[str]]:
        """Break lines into chunks for AI processing"""
        chunks = []
        for i in range(0, len(lines), chunk_size):
            chunk = lines[i:i + chunk_size]
            chunks.append(chunk)
        return chunks
    
    def _analyze_chunk_with_ai(self, chunk_text: str, page_num: int, chunk_idx: int) -> Optional[Dict]:
        """Analyze text chunk with AI for hierarchical structure"""
        
        prompt = f"""Analyze this Kenya SHIF healthcare policy text for hierarchical structure.

TEXT FROM PAGE {page_num} (Chunk {chunk_idx}):
{chunk_text}

IDENTIFY:
1. **Super Headings**: Major categories like "PRIMARY HEALTHCARE FUND", "SURGICAL SERVICES PACKAGE" (usually ALL CAPS)
2. **Service Category Headers**: Lines containing "Scope" + "Access Point" + "Tariff" + "Access Rule" with a service category name
3. **Individual Services**: Specific healthcare services (often with arrows ➢ or bullets •)
4. **Medical Specialties**: Like "Cardiology", "Orthopedic", "Urology" (for annex sections)

RETURN JSON:
{{
  "super_headings": ["FOUND SUPER HEADING" or null],
  "service_categories": [
    {{
      "category_name": "SERVICE CATEGORY NAME",
      "has_column_structure": true/false
    }}
  ],
  "individual_services": [
    {{
      "service_name": "SERVICE NAME",
      "tariff": "KES amount or null",
      "access_rules": "rules or null",
      "facility_level": "Level X or null"
    }}
  ],
  "medical_specialties": ["Specialty1", "Specialty2"] or []
}}

BE COMPREHENSIVE - extract all hierarchical elements found."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            
            ai_result = json.loads(result_text.strip())
            return ai_result
            
        except Exception as e:
            print(f"   ⚠️ AI analysis failed for page {page_num} chunk {chunk_idx}: {e}")
            return None
    
    def _process_ai_results(self, ai_analysis: Dict, page_num: int):
        """Process AI analysis results into structured data"""
        
        # Process super headings
        if 'super_headings' in ai_analysis and ai_analysis['super_headings']:
            for heading in ai_analysis['super_headings']:
                if heading and heading.strip():
                    self._add_super_heading(heading.strip(), page_num)
        
        # Process service categories
        if 'service_categories' in ai_analysis and ai_analysis['service_categories']:
            for category_data in ai_analysis['service_categories']:
                if isinstance(category_data, dict) and 'category_name' in category_data:
                    category_name = category_data['category_name'].strip()
                    if category_name:
                        self._add_service_category(category_name, page_num, 
                                                 category_data.get('has_column_structure', False))
        
        # Process individual services
        if 'individual_services' in ai_analysis and ai_analysis['individual_services']:
            for service_data in ai_analysis['individual_services']:
                if isinstance(service_data, dict) and 'service_name' in service_data:
                    service_name = service_data['service_name'].strip()
                    if service_name and len(service_name) > 5:
                        self._add_ai_service(service_data, page_num)
        
        # Process medical specialties (for annex data)
        if 'medical_specialties' in ai_analysis and ai_analysis['medical_specialties']:
            for specialty in ai_analysis['medical_specialties']:
                if specialty and specialty.strip():
                    # Treat specialty as both super heading and service category
                    self._add_super_heading(f"{specialty.strip()} Services", page_num)
    
    def _add_super_heading(self, line: str, page_num: int):
        """Add a super heading - avoid duplicates"""
        
        # Check if already exists
        existing = [sh for sh in self.super_headings if sh['heading_text'].lower() == line.lower()]
        if existing:
            return
        
        super_heading = {
            'heading_text': line,
            'heading_type': 'super_heading',
            'page_number': page_num,
            'services_count': 0,
            'categories_count': 0,
            'extraction_method': 'ai_enhanced'
        }
        
        self.super_headings.append(super_heading)
        self.current_hierarchy['super_heading'] = line
        
        print(f"   📊 AI found super heading: {line} (page {page_num})")
    
    def _add_service_category(self, category_name: str, page_num: int, has_columns: bool = False):
        """Add a service category - avoid duplicates"""
        
        # Check if already exists
        existing = [sc for sc in self.service_categories if sc['category_name'].lower() == category_name.lower()]
        if existing:
            return
        
        service_category = {
            'category_name': category_name,
            'super_heading': self.current_hierarchy['super_heading'],
            'page_number': page_num,
            'has_column_structure': has_columns,
            'services_count': 0,
            'extraction_method': 'ai_enhanced'
        }
        
        self.service_categories.append(service_category)
        self.current_hierarchy['service_category'] = category_name
        
        # Update super heading count
        if self.super_headings:
            self.super_headings[-1]['categories_count'] += 1
        
        print(f"   📋 AI found service category: {category_name} (page {page_num})")
    
    def _add_ai_service(self, service_data: Dict, page_num: int):
        """Add an individual service from AI analysis"""
        
        service = {
            'service_name': service_data['service_name'],
            'super_heading': self.current_hierarchy['super_heading'],
            'service_category': self.current_hierarchy['service_category'],
            'page_number': page_num,
            'tariff': service_data.get('tariff', ''),
            'access_rules': service_data.get('access_rules', ''),
            'facility_level': service_data.get('facility_level', ''),
            'extraction_method': 'ai_enhanced_hierarchical'
        }
        
        self.services.append(service)
        
        # Update counts
        if self.service_categories:
            self.service_categories[-1]['services_count'] += 1
        if self.super_headings:
            self.super_headings[-1]['services_count'] += 1
    
    def save_ai_enhanced_results(self, results: Dict, output_dir: str):
        """Save AI-enhanced results"""
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save super headings
        super_df = pd.DataFrame(results['super_headings'])
        super_df.to_csv(f"{output_dir}/ai_enhanced_super_headings.csv", index=False)
        
        # Save service categories
        categories_df = pd.DataFrame(results['service_categories'])
        categories_df.to_csv(f"{output_dir}/ai_enhanced_service_categories.csv", index=False)
        
        # Save individual services
        services_df = pd.DataFrame(results['services'])
        services_df.to_csv(f"{output_dir}/ai_enhanced_services.csv", index=False)
        
        # Save complete results as JSON
        with open(f"{output_dir}/ai_enhanced_complete_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📁 AI-enhanced results saved to: {output_dir}")
        return output_dir

def main():
    """Run AI-enhanced hierarchical extraction"""
    
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    output_dir = f"ai_enhanced_hierarchical_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
    
    extractor = AIEnhancedHierarchicalExtractor(pdf_path)
    results = extractor.extract_with_ai_enhancement()
    
    print(f"\\n📊 AI-ENHANCED EXTRACTION RESULTS:")
    print(f"   Super headings: {results['summary']['total_super_headings']}")
    print(f"   Service categories: {results['summary']['total_service_categories']}")
    print(f"   Individual services: {results['summary']['total_services']}")
    
    # Save results
    extractor.save_ai_enhanced_results(results, output_dir)
    
    # Display hierarchical structure
    print(f"\\n🎯 AI-ENHANCED HIERARCHY FOUND:")
    for super_heading in results['super_headings']:
        print(f"   📊 {super_heading['heading_text']} (page {super_heading['page_number']})")
        
        # Show related categories
        related_categories = [cat for cat in results['service_categories'] 
                            if cat['super_heading'] == super_heading['heading_text']]
        
        for category in related_categories:
            print(f"      📋 └── {category['category_name']} ({category['services_count']} services)")

if __name__ == "__main__":
    main()