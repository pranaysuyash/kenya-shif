#!/usr/bin/env python3
"""
Hierarchical Service Extractor for Kenya SHIF Policy
Properly extracts the 3-tier structure:
1. Super headings (PRIMARY HEALTHCARE FUND)
2. Service category headers (SURGICAL SERVICES PACKAGE + ScopeAccessPointTariffAccessRule)
3. Individual services with structured data
"""

import re
import pdfplumber
import pandas as pd
from typing import List, Dict, Tuple, Optional

class HierarchicalServiceExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.super_headings = []
        self.service_categories = []
        self.services = []
        self.current_hierarchy = {
            'super_heading': None,
            'service_category': None,
            'page_number': 1
        }
    
    def extract_hierarchical_services(self) -> Dict:
        """Extract services with proper 3-tier hierarchical structure"""
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                self.current_hierarchy['page_number'] = page_num
                text = page.extract_text()
                
                if text:
                    lines = text.split('\n')
                    self._process_page_lines(lines, page_num)
        
        return {
            'super_headings': self.super_headings,
            'service_categories': self.service_categories,
            'services': self.services,
            'total_super_headings': len(self.super_headings),
            'total_service_categories': len(self.service_categories),
            'total_services': len(self.services)
        }
    
    def _process_page_lines(self, lines: List[str], page_num: int):
        """Process lines on a page to identify hierarchical structure"""
        
        for i, line in enumerate(lines):
            line = line.strip()
            if len(line) < 5:
                continue
            
            # Check for super headings (all caps, major fund/package names)
            if self._is_super_heading(line):
                self._add_super_heading(line, page_num)
            
            # Check for service category headers (with column structure)
            elif self._is_service_category_header(line):
                self._add_service_category(line, page_num)
            
            # Check for individual services (under categories)
            elif self._is_individual_service(line, lines, i):
                self._add_individual_service(line, page_num, lines, i)
    
    def _is_super_heading(self, line: str) -> bool:
        """Identify super headings like 'PRIMARY HEALTHCARE FUND'"""
        
        # Patterns for super headings
        super_heading_patterns = [
            r'^[A-Z][A-Z\s]+FUND$',
            r'^[A-Z][A-Z\s]+PACKAGE$', 
            r'^[A-Z][A-Z\s]+SERVICES$',
            r'^PRIMARY\s+HEALTHCARE\s+FUND$',
            r'^SURGICAL\s+SERVICES\s+PACKAGE$',
            r'^ONCOLOGY\s+SERVICES$',
            r'^MENTAL\s+WELLNESS\s+BENEFIT\s+PACKAGE$',
            r'^MATERNITY\s+SERVICES$'
        ]
        
        # Must be all caps and match patterns
        if line.isupper() and len(line) > 10:
            for pattern in super_heading_patterns:
                if re.match(pattern, line):
                    return True
        
        return False
    
    def _is_service_category_header(self, line: str) -> bool:
        """Identify service category headers with column structure"""
        
        # Must contain the column headers pattern
        column_pattern = r'.*Scope.*Access.*Point.*Tariff.*Access.*Rule'
        
        if re.search(column_pattern, line, re.IGNORECASE):
            # Extract the service category name (before the columns)
            service_part = re.sub(r'Scope.*Access.*Point.*Tariff.*Access.*Rule.*$', '', line, flags=re.IGNORECASE).strip()
            
            # Must have a meaningful service category name
            if len(service_part) > 5:
                return True
        
        return False
    
    def _is_individual_service(self, line: str, lines: List[str], index: int) -> bool:
        """Identify individual services under a category"""
        
        # Must be under a service category
        if not self.current_hierarchy['service_category']:
            return False
        
        # Look for service indicators
        service_indicators = [
            r'^➢\s+',  # Arrow bullet
            r'^•\s+',  # Bullet
            r'^\d+\.\s+', # Numbered list
            r'KES\s+\d+', # Contains pricing
            r'Level\s+\d+', # Facility level
        ]
        
        for pattern in service_indicators:
            if re.search(pattern, line):
                return True
        
        # Or if it looks like structured service data
        if len(line) > 15 and any(word in line.lower() for word in 
                                 ['service', 'treatment', 'consultation', 'care', 'therapy', 'procedure']):
            return True
        
        return False
    
    def _add_super_heading(self, line: str, page_num: int):
        """Add a super heading to hierarchy"""
        
        super_heading = {
            'heading_text': line,
            'heading_type': 'super_heading',
            'page_number': page_num,
            'services_count': 0,  # Will be updated
            'categories_count': 0  # Will be updated
        }
        
        self.super_headings.append(super_heading)
        self.current_hierarchy['super_heading'] = line
        self.current_hierarchy['service_category'] = None  # Reset
        
        print(f"   📊 Super heading found: {line} (page {page_num})")
    
    def _add_service_category(self, line: str, page_num: int):
        """Add a service category to hierarchy"""
        
        # Extract service category name (before column headers)
        category_name = re.sub(r'Scope.*Access.*Point.*Tariff.*Access.*Rule.*$', '', line, flags=re.IGNORECASE).strip()
        
        service_category = {
            'category_name': category_name,
            'full_header_line': line,
            'super_heading': self.current_hierarchy['super_heading'],
            'page_number': page_num,
            'has_column_structure': True,
            'services_count': 0  # Will be updated
        }
        
        self.service_categories.append(service_category)
        self.current_hierarchy['service_category'] = category_name
        
        # Update super heading count
        if self.super_headings:
            self.super_headings[-1]['categories_count'] += 1
        
        print(f"   📋 Service category found: {category_name} (page {page_num})")
    
    def _add_individual_service(self, line: str, page_num: int, lines: List[str], index: int):
        """Add an individual service with full context"""
        
        # Get surrounding context for better parsing
        context_start = max(0, index - 2)
        context_end = min(len(lines), index + 3)
        context = '\n'.join(lines[context_start:context_end])
        
        # Parse service components
        service_name = self._extract_service_name(line)
        pricing = self._extract_pricing(line)
        access_rules = self._extract_access_rules(line)
        scope = self._extract_scope(line)
        facility_level = self._extract_facility_level(line)
        
        service = {
            'service_name': service_name,
            'super_heading': self.current_hierarchy['super_heading'],
            'service_category': self.current_hierarchy['service_category'],
            'page_number': page_num,
            'pricing_kes': pricing,
            'access_rules': access_rules,
            'scope': scope,
            'facility_level': facility_level,
            'raw_text': line,
            'context': context,
            'extraction_method': 'hierarchical_structure_aware'
        }
        
        self.services.append(service)
        
        # Update counts
        if self.service_categories:
            self.service_categories[-1]['services_count'] += 1
        if self.super_headings:
            self.super_headings[-1]['services_count'] += 1
    
    def _extract_service_name(self, line: str) -> str:
        """Extract clean service name"""
        # Remove arrows, bullets, pricing, and clean up
        name = re.sub(r'^[➢•]\s*', '', line)
        name = re.sub(r'KES\s+[\d,]+.*$', '', name)
        name = re.sub(r'Level\s+\d+.*$', '', name)
        return name.strip()
    
    def _extract_pricing(self, line: str) -> Optional[float]:
        """Extract pricing information"""
        price_match = re.search(r'KES\s*([\d,]+)', line)
        if price_match:
            try:
                return float(price_match.group(1).replace(',', ''))
            except:
                return None
        return None
    
    def _extract_access_rules(self, line: str) -> str:
        """Extract access rules and restrictions"""
        rules = []
        
        # Look for common rule patterns
        if 'maximum' in line.lower():
            rule_match = re.search(r'maximum.*?(?:per|sessions|times)', line, re.IGNORECASE)
            if rule_match:
                rules.append(rule_match.group(0))
        
        if 'level' in line.lower():
            level_match = re.search(r'level\s+\d+[^,]*', line, re.IGNORECASE)
            if level_match:
                rules.append(level_match.group(0))
        
        return '; '.join(rules) if rules else ''
    
    def _extract_scope(self, line: str) -> str:
        """Extract scope information"""
        # This would need to be enhanced based on actual scope patterns in the document
        if 'coverage' in line.lower():
            return 'covered'
        elif 'emergency' in line.lower():
            return 'emergency'
        return ''
    
    def _extract_facility_level(self, line: str) -> str:
        """Extract facility level requirements"""
        level_match = re.search(r'level\s+(\d+)', line, re.IGNORECASE)
        if level_match:
            return f"Level {level_match.group(1)}"
        return ''
    
    def save_hierarchical_results(self, output_dir: str):
        """Save results with proper hierarchical structure"""
        
        # Save super headings
        super_df = pd.DataFrame(self.super_headings)
        super_df.to_csv(f"{output_dir}/super_headings.csv", index=False)
        
        # Save service categories
        categories_df = pd.DataFrame(self.service_categories)
        categories_df.to_csv(f"{output_dir}/service_categories.csv", index=False)
        
        # Save individual services with hierarchy
        services_df = pd.DataFrame(self.services)
        services_df.to_csv(f"{output_dir}/hierarchical_services.csv", index=False)
        
        # Create summary
        summary = {
            'super_headings_count': len(self.super_headings),
            'service_categories_count': len(self.service_categories),
            'individual_services_count': len(self.services),
            'super_headings': [sh['heading_text'] for sh in self.super_headings],
            'service_categories': [sc['category_name'] for sc in self.service_categories]
        }
        
        import json
        with open(f"{output_dir}/hierarchical_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary

def main():
    """Test the hierarchical extraction"""
    
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    output_dir = f"hierarchical_output_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    print("🔍 HIERARCHICAL SERVICE EXTRACTION")
    print("=" * 50)
    
    extractor = HierarchicalServiceExtractor(pdf_path)
    results = extractor.extract_hierarchical_services()
    
    print(f"\n📊 EXTRACTION RESULTS:")
    print(f"   Super headings: {results['total_super_headings']}")
    print(f"   Service categories: {results['total_service_categories']}")
    print(f"   Individual services: {results['total_services']}")
    
    # Save results
    summary = extractor.save_hierarchical_results(output_dir)
    
    print(f"\n📁 Results saved to: {output_dir}")
    print(f"\n🎯 HIERARCHY FOUND:")
    for super_heading in summary['super_headings']:
        print(f"   📊 {super_heading}")
    
    for category in summary['service_categories']:
        print(f"   📋   └── {category}")

if __name__ == "__main__":
    main()