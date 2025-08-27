#!/usr/bin/env python3
"""
Direct PDF analysis to understand what rules are being missed
"""

import pdfplumber
import re
import os

def analyze_pdf_content():
    """Analyze PDF to find missed rules and content patterns"""
    
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF not found at {pdf_path}")
        return
    
    print("=== DIRECT PDF CONTENT ANALYSIS ===")
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        # Sample key pages to understand structure
        sample_pages = [1, 5, 10, 15, 20, 25, 30]  # Representative sample
        
        for page_num in sample_pages:
            if page_num > len(pdf.pages):
                continue
                
            page = pdf.pages[page_num - 1]  # 0-indexed
            text = page.extract_text()
            
            if not text:
                continue
                
            print(f"\n=== PAGE {page_num} ANALYSIS ===")
            
            # Look for service-like content that might be missed
            lines = text.split('\n')
            service_lines = []
            
            for line in lines:
                line = line.strip()
                if len(line) < 10:  # Skip short lines
                    continue
                
                # Look for potential service descriptions
                service_indicators = [
                    # Medical procedures
                    r'\b(?:treatment|procedure|therapy|care|service|consultation|examination)\b',
                    # Healthcare specialties
                    r'\b(?:dental|optical|physiotherapy|laboratory|radiology|pathology)\b',
                    # Medical conditions
                    r'\b(?:diabetes|hypertension|asthma|cancer|cardiac|renal|mental)\b',
                    # Healthcare facilities
                    r'\b(?:hospital|clinic|dispensary|centre|center|facility)\b',
                    # Coverage terms
                    r'\b(?:covered|included|excluded|benefit|package)\b'
                ]
                
                if any(re.search(pattern, line, re.IGNORECASE) for pattern in service_indicators):
                    service_lines.append(line[:100])  # Truncate for readability
            
            # Show potential services on this page
            if service_lines:
                print(f"Potential services found: {len(service_lines)}")
                for i, line in enumerate(service_lines[:5]):  # Show first 5
                    print(f"  {i+1}. {line}...")
            
            # Look for tables
            tables = page.extract_tables()
            if tables:
                print(f"Tables found: {len(tables)}")
                for i, table in enumerate(tables[:2]):  # Show first 2 tables
                    if table and len(table) > 1:
                        print(f"  Table {i+1} structure: {len(table)} rows, {len(table[0]) if table[0] else 0} columns")
                        # Show header row if available
                        if table[0]:
                            header = [str(cell)[:20] if cell else "" for cell in table[0]]
                            print(f"    Headers: {header}")
        
        # Look for specific content types that might indicate missed rules
        print(f"\n=== CONTENT PATTERN ANALYSIS ===")
        
        # Search for common healthcare terms across all pages
        all_text = ""
        for page in pdf.pages[:10]:  # First 10 pages for analysis
            page_text = page.extract_text()
            if page_text:
                all_text += page_text + "\n"
        
        # Count occurrences of key healthcare terms
        healthcare_terms = {
            'dental': r'\b(?:dental|tooth|oral health|dentist)\b',
            'laboratory': r'\b(?:laboratory|lab test|blood test|specimen)\b',
            'vaccination': r'\b(?:vaccination|vaccine|immunization|KEPI)\b',
            'physiotherapy': r'\b(?:physiotherapy|physio|rehabilitation|physical therapy)\b',
            'nutrition': r'\b(?:nutrition|dietetic|diet|nutritionist)\b',
            'family planning': r'\b(?:family planning|contraceptive|reproductive health)\b',
            'mental health': r'\b(?:mental health|psychiatric|psychology|counseling)\b',
            'chronic disease': r'\b(?:chronic disease|diabetes|hypertension|NCDs)\b',
            'preventive care': r'\b(?:preventive|prevention|screening|health promotion)\b'
        }
        
        print("Healthcare service mentions in document:")
        for term, pattern in healthcare_terms.items():
            matches = len(re.findall(pattern, all_text, re.IGNORECASE))
            print(f"  {term}: {matches} mentions")
        
        # Look for pricing patterns that might be missed
        print("\nPricing patterns found:")
        
        # Various KES patterns
        kes_patterns = [
            r'KES\.?\s*[\d,]+',
            r'[\d,]+\s*KES',
            r'[\d,]+\s*/\-',
            r'Ksh\.?\s*[\d,]+',
            r'cost.*[\d,]+',
            r'tariff.*[\d,]+',
            r'fee.*[\d,]+',
            r'charge.*[\d,]+'
        ]
        
        for i, pattern in enumerate(kes_patterns):
            matches = len(re.findall(pattern, all_text, re.IGNORECASE))
            print(f"  Pattern {i+1} ({pattern[:20]}...): {matches} matches")

if __name__ == "__main__":
    analyze_pdf_content()
