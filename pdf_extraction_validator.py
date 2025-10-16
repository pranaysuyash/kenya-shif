#!/usr/bin/env python3
"""
PDF Extraction Package Validator
Compares pdfplumber, PyPDF2, and tabula-py for extracting healthcare tariffs and services
"""

import time
import pandas as pd
import sys
from typing import Dict, List, Tuple

def validate_pdfplumber_extraction() -> Tuple[int, float, List[str]]:
    """Validate pdfplumber extraction capability"""
    print("🔍 Testing pdfplumber...")
    start_time = time.time()
    
    try:
        import pdfplumber
        
        pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
        tariffs_found = []
        services_found = []
        
        with pdfplumber.open(pdf_path) as pdf:
            # Test on annex pages (19-54) where most tariffs are located
            for page_num in range(18, min(54, len(pdf.pages))):
                page = pdf.pages[page_num]
                text = page.extract_text()
                
                # Count potential tariff lines
                if text:
                    lines = text.split('\n')
                    for line in lines:
                        # Look for tariff pattern: number + text + price
                        if any(char.isdigit() for char in line) and any(price_indicator in line for price_indicator in ['KES', ',', '000']):
                            if len(line.strip()) > 20:
                                tariffs_found.append(line.strip()[:100])
                        
                        # Look for service patterns
                        if any(keyword in line.lower() for keyword in ['service', 'care', 'treatment', 'consultation', 'therapy']):
                            if len(line.strip()) > 15:
                                services_found.append(line.strip()[:100])
                
                # Test table extraction
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        if table and len(table) > 1:
                            for row in table:
                                if row and len(row) > 2:
                                    row_text = ' '.join(str(cell) for cell in row if cell)
                                    if any(char.isdigit() for char in row_text) and len(row_text) > 20:
                                        tariffs_found.append(row_text[:100])
        
        extraction_time = time.time() - start_time
        total_items = len(set(tariffs_found + services_found))
        
        print(f"   ✅ pdfplumber: {total_items} items in {extraction_time:.2f}s")
        return total_items, extraction_time, tariffs_found[:5]
        
    except Exception as e:
        print(f"   ❌ pdfplumber failed: {e}")
        return 0, 0, []

def validate_pypdf2_extraction() -> Tuple[int, float, List[str]]:
    """Validate PyPDF2 extraction capability"""
    print("🔍 Testing PyPDF2...")
    start_time = time.time()
    
    try:
        import PyPDF2
        
        pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
        tariffs_found = []
        services_found = []
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Test on annex pages (19-54)
            for page_num in range(18, min(54, len(reader.pages))):
                text = reader.pages[page_num].extract_text()
                
                if text:
                    lines = text.split('\n')
                    for line in lines:
                        # Look for tariff pattern
                        if any(char.isdigit() for char in line) and any(price_indicator in line for price_indicator in ['KES', ',', '000']):
                            if len(line.strip()) > 20:
                                tariffs_found.append(line.strip()[:100])
                        
                        # Look for service patterns
                        if any(keyword in line.lower() for keyword in ['service', 'care', 'treatment', 'consultation', 'therapy']):
                            if len(line.strip()) > 15:
                                services_found.append(line.strip()[:100])
        
        extraction_time = time.time() - start_time
        total_items = len(set(tariffs_found + services_found))
        
        print(f"   ✅ PyPDF2: {total_items} items in {extraction_time:.2f}s")
        return total_items, extraction_time, tariffs_found[:5]
        
    except Exception as e:
        print(f"   ❌ PyPDF2 failed: {e}")
        return 0, 0, []

def validate_tabula_extraction() -> Tuple[int, float, List[str]]:
    """Validate tabula-py extraction capability for structured tables"""
    print("🔍 Testing tabula-py...")
    start_time = time.time()
    
    try:
        import tabula
        
        pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
        tariffs_found = []
        
        # Test table extraction from annex pages (19-54)
        for page in range(19, 55):
            try:
                # Extract tables from this page
                tables = tabula.read_pdf(pdf_path, pages=page, multiple_tables=True, pandas_options={'header': None})
                
                for df in tables:
                    if df is not None and not df.empty:
                        # Process each row as potential tariff
                        for _, row in df.iterrows():
                            row_text = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                            
                            # Look for structured tariff data
                            if len(row_text) > 20 and any(char.isdigit() for char in row_text):
                                # Check if it looks like a tariff: ID + specialty + procedure + price
                                parts = row_text.split()
                                if len(parts) >= 3:
                                    tariffs_found.append(row_text[:100])
                                    
            except Exception as page_error:
                # Skip pages that can't be processed
                continue
        
        extraction_time = time.time() - start_time
        total_items = len(set(tariffs_found))
        
        print(f"   ✅ tabula-py: {total_items} table items in {extraction_time:.2f}s")
        return total_items, extraction_time, tariffs_found[:5]
        
    except Exception as e:
        print(f"   ❌ tabula-py failed: {e}")
        return 0, 0, []

def main():
    """Run validation comparison of PDF extraction packages"""
    print("📊 PDF Extraction Package Validation")
    print("=" * 50)
    
    # Test all three packages
    pdfplumber_count, pdfplumber_time, pdfplumber_samples = validate_pdfplumber_extraction()
    pypdf2_count, pypdf2_time, pypdf2_samples = validate_pypdf2_extraction()
    tabula_count, tabula_time, tabula_samples = validate_tabula_extraction()
    
    print("\n📋 COMPARISON RESULTS:")
    print("=" * 50)
    print(f"pdfplumber: {pdfplumber_count:4d} items in {pdfplumber_time:6.2f}s")
    print(f"PyPDF2:    {pypdf2_count:4d} items in {pypdf2_time:6.2f}s")  
    print(f"tabula-py:  {tabula_count:4d} items in {tabula_time:6.2f}s")
    
    print("\n🎯 RECOMMENDATIONS:")
    print("=" * 50)
    
    # Determine best package based on results
    if tabula_count > max(pdfplumber_count, pypdf2_count) * 0.8:
        print("✅ TABULA-PY: Best for structured table data (tariffs)")
        print("   - Superior table structure preservation")
        print("   - Handles complex table layouts")
        print("   - Ideal for annex tariff extraction")
        
    if pdfplumber_count > max(tabula_count, pypdf2_count) * 0.8:
        print("✅ PDFPLUMBER: Best for mixed content (text + tables)")
        print("   - Good balance of text and table extraction")
        print("   - Handles various content types")
        print("   - Good for service descriptions")
        
    print("\n💡 OPTIMAL STRATEGY:")
    print("   Use TABULA-PY for annex tables (pages 19-54)")
    print("   Use PDFPLUMBER for text content and mixed pages")
    print("   Use PyPDF2 as fallback for basic text extraction")
    
    print(f"\n📝 Sample extractions:")
    if pdfplumber_samples:
        print(f"pdfplumber: {pdfplumber_samples[0][:80]}...")
    if pypdf2_samples:
        print(f"PyPDF2:    {pypdf2_samples[0][:80]}...")
    if tabula_samples:
        print(f"tabula-py:  {tabula_samples[0][:80]}...")

if __name__ == "__main__":
    main()