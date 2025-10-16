#!/usr/bin/env python3
"""
Enhanced SHIF analyzer with improved rule extraction for missed services
"""

import os
import sys

# Add the current directory to path to import the main analyzer
sys.path.insert(0, '.')

from shif_analyzer import *
import re

# Enhanced trigger keywords to capture missed services
ENHANCED_TRIGGER_KEYWORDS = {
    # Existing keywords
    'dialysis', 'consultation', 'outpatient', 'scan', 'mri', 'ct', 'surgery', 
    'treatment', 'maternity', 'delivery', 'oncology', 'emergency', 'ambulance',
    
    # Missing dental services
    'dental', 'oral', 'tooth', 'dentist', 'orthodontic', 'extraction',
    
    # Missing laboratory services  
    'laboratory', 'lab', 'test', 'specimen', 'blood', 'pathology', 'diagnostic',
    'culture', 'analysis', 'investigation',
    
    # Missing preventive care
    'vaccine', 'vaccination', 'immunization', 'screening', 'prevention', 
    'wellness', 'health promotion', 'check-up', 'monitoring',
    
    # Missing pharmaceutical
    'medicine', 'medication', 'drug', 'pharmaceutical', 'prescription',
    'dispensing', 'pharmacy',
    
    # Missing rehabilitation
    'physiotherapy', 'physio', 'rehabilitation', 'occupational therapy',
    'speech therapy', 'therapy',
    
    # Missing specialized services
    'nutrition', 'dietetic', 'counseling', 'counselling', 'education',
    'family planning', 'reproductive', 'pediatric', 'geriatric',
    
    # Service delivery terms
    'service', 'care', 'management', 'support', 'program', 'package'
}

# Patterns for free/bundled services
FREE_SERVICE_PATTERNS = [
    r'no additional cost',
    r'included in.*?(?:package|consultation|service)',
    r'free of charge',
    r'at no cost',
    r'no charge',
    r'covered under.*?package'
]

# Bundled service patterns  
BUNDLED_SERVICE_PATTERNS = [
    r'services include.*?:',
    r'comprehensive.*?(?:care|management|package)',
    r'as per.*?(?:schedule|protocol|guideline|list)',
    r'according to.*?(?:WHO|national|standard)',
    r'routine.*?(?:care|services|procedures)'
]

def enhanced_line_processing(text: str, page_num: int) -> List[Dict]:
    """Enhanced line processing to capture more services"""
    rules = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if len(line) < 5:
            continue
            
        # Check for ANY healthcare-related content, not just KES amounts
        is_healthcare_content = False
        
        # Check enhanced trigger keywords
        if any(keyword in line.lower() for keyword in ENHANCED_TRIGGER_KEYWORDS):
            is_healthcare_content = True
        
        # Check for service-like patterns
        service_patterns = [
            r'\b(?:treatment|procedure|therapy|care|service|consultation|examination)\b',
            r'\b(?:screening|test|check|detection|monitoring|assessment)\b',
            r'\b(?:management|support|program|intervention|protocol)\b'
        ]
        
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in service_patterns):
            is_healthcare_content = True
            
        # Check for medical condition mentions
        condition_patterns = [
            r'\b(?:diabetes|hypertension|asthma|cancer|cardiac|renal|mental)\b',
            r'\b(?:chronic|acute|emergency|urgent|routine|preventive)\b'
        ]
        
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in condition_patterns):
            is_healthcare_content = True
        
        if is_healthcare_content:
            # Extract service information
            service = line[:100].strip()  # First part as service name
            
            # Look for pricing (including free services)
            tariff = extract_money(line)
            is_free_service = any(re.search(pattern, line, re.IGNORECASE) 
                                for pattern in FREE_SERVICE_PATTERNS)
            
            if tariff or is_free_service or len(service) > 10:
                rule = {
                    'service': service,
                    'service_key': normalize_service_key(service),
                    'category': categorize_service(line),
                    'tariff': tariff if tariff else (0 if is_free_service else None),
                    'tariff_unit': extract_tariff_and_unit(line)[1],
                    'coverage_status': extract_coverage_status(line),
                    'facility_level': extract_facility_level(line),
                    'facility_levels': extract_facility_levels(line),
                    'exclusion': check_exclusion(line),
                    'coverage_condition': extract_coverage_condition(line),
                    'limits': extract_limits(line),
                    'source_page': page_num,
                    'evidence_snippet': create_evidence_snippet(line, max_length=200),
                    'raw_text': line[:500],
                    'source_type': 'enhanced_text',
                    'confidence': 'HIGH' if tariff else ('MEDIUM' if is_free_service else 'LOW'),
                    'is_free_service': is_free_service
                }
                rules.append(rule)
    
    return rules

def enhanced_table_processing(tables: List, page_num: int) -> List[Dict]:
    """Process ALL table content, not just triggered rows"""
    rules = []
    
    for table_idx, table in enumerate(tables):
        if not table or len(table) < 2:
            continue
            
        # Process ALL rows, including headers
        for row_idx, row in enumerate(table):
            if not row:
                continue
                
            row_text = ' '.join(str(cell) for cell in row if cell)
            
            if len(row_text) < 10:
                continue
                
            # Look for ANY healthcare content in table rows
            healthcare_indicators = [
                r'\b(?:treatment|procedure|service|care|consultation)\b',
                r'\b(?:test|screening|examination|therapy|management)\b',
                r'\bLevel\s*[1-6]\b',
                r'\b(?:KES|Ksh|cost|fee|tariff|charge)\b'
            ]
            
            if any(re.search(pattern, row_text, re.IGNORECASE) 
                   for pattern in healthcare_indicators):
                
                # Try to extract service from first meaningful cell
                service = ''
                for cell in row:
                    if cell and isinstance(cell, str) and len(str(cell).strip()) > 5:
                        service = str(cell).strip()
                        break
                
                if service:
                    tariff = extract_money(row_text)
                    
                    rule = {
                        'service': service[:200],
                        'service_key': normalize_service_key(service),
                        'category': categorize_service(row_text),
                        'tariff': tariff,
                        'tariff_unit': extract_tariff_and_unit(row_text)[1],
                        'coverage_status': extract_coverage_status(row_text),
                        'facility_level': extract_facility_level(row_text),
                        'facility_levels': extract_facility_levels(row_text),
                        'exclusion': check_exclusion(row_text),
                        'coverage_condition': extract_coverage_condition(row_text),
                        'limits': extract_limits(row_text),
                        'source_page': page_num,
                        'evidence_snippet': create_evidence_snippet(row_text, max_length=200),
                        'raw_text': row_text[:500],
                        'source_type': f'enhanced_table_{table_idx}_row_{row_idx}',
                        'confidence': 'HIGH' if tariff else 'MEDIUM'
                    }
                    rules.append(rule)
    
    return rules

def parse_pdf_enhanced(pdf_path: str, openai_key: str = None) -> pd.DataFrame:
    """Enhanced PDF parsing to capture more healthcare services"""
    
    rules = []
    
    print("=== ENHANCED EXTRACTION MODE ===")
    print("Capturing dental, laboratory, preventive, and pharmaceutical services...")
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"Processing page {page_num}/{len(pdf.pages)}...", end=' ')
            
            # Extract text with OCR fallback
            text = page.extract_text() or ""
            if not text.strip() or len(text.strip()) < 50:
                if OCR_AVAILABLE:
                    text = extract_text_with_ocr(pdf_path, page_num)
            
            # Enhanced line processing
            page_rules = enhanced_line_processing(text, page_num)
            rules.extend(page_rules)
            
            # Enhanced table processing
            tables = extract_tables_with_fallbacks(pdf_path, page_num)
            table_rules = enhanced_table_processing(tables, page_num)
            rules.extend(table_rules)
            
            print(f"Found {len(page_rules) + len(table_rules)} potential services")
    
    # Convert to DataFrame
    df = pd.DataFrame(rules)
    
    if not df.empty:
        # Remove duplicates more carefully
        df = df.drop_duplicates(subset=['service_key', 'tariff', 'facility_level'])
        df = df.reset_index(drop=True)
        
        print(f"\nTotal services extracted: {len(df)}")
        
        # Show category breakdown
        if 'category' in df.columns:
            category_counts = df['category'].value_counts()
            print("Services by category:")
            for category, count in category_counts.items():
                print(f"  {category}: {count}")
    
    return df

def main_enhanced():
    """Run enhanced extraction"""
    
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    # Get OpenAI key from environment
    openai_key = os.environ.get('OPENAI_API_KEY')
    
    if openai_key:
        print("✅ OpenAI API key found - will use enhanced extraction")
    else:
        print("⚠️ No OpenAI API key - using enhanced regex only")
    
    # Run enhanced extraction
    rules_df = parse_pdf_enhanced(pdf_path, openai_key)
    
    # Create output directory
    output_dir = 'outputs_comprehensive'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results
    rules_df.to_csv(os.path.join(output_dir, 'rules_comprehensive.csv'), index=False)
    
    # Run contradiction and gap detection
    contradictions_df = detect_contradictions_v2(rules_df)
    gaps_df = detect_gaps_with_yaml(rules_df)
    
    contradictions_df.to_csv(os.path.join(output_dir, 'contradictions_comprehensive.csv'), index=False)
    gaps_df.to_csv(os.path.join(output_dir, 'gaps_comprehensive.csv'), index=False)
    
    # Create enhanced dashboard
    excel_path = os.path.join(output_dir, 'SHIF_comprehensive_dashboard.xlsx')
    create_excel_dashboard(rules_df, contradictions_df, gaps_df, excel_path)
    
    print(f"\n✅ Enhanced extraction complete!")
    print(f"📊 Results saved to: {output_dir}/")
    print(f"📈 Rules extracted: {len(rules_df)}")
    print(f"⚠️ Contradictions found: {len(contradictions_df)}")
    print(f"🔍 Gaps identified: {len(gaps_df)}")

if __name__ == "__main__":
    main_enhanced()
