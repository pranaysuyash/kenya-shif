#!/usr/bin/env python3
"""
Quick PDF page sampler to understand content structure
"""

import pdfplumber
import os

def sample_pdf_pages():
    """Sample key pages to understand what content exists"""
    
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF not found at {pdf_path}")
        return
    
    print("=== SAMPLING PDF PAGES ===")
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        # Sample specific pages that likely contain different types of content
        key_pages = [3, 8, 15, 25, 35, 45]  # Strategic sampling
        
        for page_num in key_pages:
            if page_num > len(pdf.pages):
                continue
                
            page = pdf.pages[page_num - 1]
            text = page.extract_text()
            
            if not text or len(text) < 100:
                print(f"\nPage {page_num}: Minimal text content (likely table/image heavy)")
                continue
            
            print(f"\n{'='*20} PAGE {page_num} {'='*20}")
            
            # Show first few lines to understand content type
            lines = [line.strip() for line in text.split('\n') if line.strip()][:10]
            for i, line in enumerate(lines):
                print(f"{i+1:2d}. {line}")
            
            # Look for specific patterns that indicate services
            potential_services = []
            for line in text.split('\n'):
                line = line.strip()
                # Look for lines that might be service descriptions
                if any(keyword in line.lower() for keyword in [
                    'treatment', 'procedure', 'service', 'care', 'examination',
                    'therapy', 'consultation', 'screening', 'test'
                ]) and len(line) > 20:
                    potential_services.append(line[:80])
            
            if potential_services:
                print(f"\nPotential services on page {page_num}:")
                for service in potential_services[:3]:
                    print(f"  • {service}...")
            
            # Check for tables
            tables = page.extract_tables()
            if tables:
                print(f"\nTables: {len(tables)} found")
                for i, table in enumerate(tables):
                    if table and len(table) > 0:
                        rows, cols = len(table), len(table[0]) if table[0] else 0
                        print(f"  Table {i+1}: {rows} rows × {cols} cols")

if __name__ == "__main__":
    sample_pdf_pages()
