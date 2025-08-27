#!/usr/bin/env python3
"""
Comprehensive PDF analysis to identify missed healthcare services
"""

import pdfplumber
import re
import json

def comprehensive_pdf_analysis():
    """Systematically analyze PDF for all healthcare services"""
    
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"=== COMPREHENSIVE PDF ANALYSIS ===")
        print(f"Total pages: {len(pdf.pages)}")
        
        # Collect all text from document
        all_text = ""
        page_contents = {}
        
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                all_text += f"\n--- PAGE {page_num} ---\n" + text
                page_contents[page_num] = text
        
        print(f"Total text length: {len(all_text):,} characters")
        
        # Define comprehensive healthcare service patterns
        healthcare_services = {
            # Primary care services
            'consultation': r'\b(?:consultation|consult|visit|check-up|examination)\b',
            'diagnosis': r'\b(?:diagnosis|diagnostic|screening|assessment)\b',
            'treatment': r'\b(?:treatment|therapy|care|management)\b',
            
            # Preventive services  
            'vaccination': r'\b(?:vaccination|vaccine|immunization|immunisation|KEPI)\b',
            'screening': r'\b(?:screening|test|check|detection|monitoring)\b',
            'health_education': r'\b(?:health education|counseling|counselling|guidance)\b',
            
            # Specialized services
            'dental': r'\b(?:dental|tooth|oral|dentist|orthodontic)\b',
            'optical': r'\b(?:optical|eye|vision|glasses|spectacles|ophthalmology)\b',
            'physiotherapy': r'\b(?:physiotherapy|physio|rehabilitation|physical therapy)\b',
            'mental_health': r'\b(?:mental health|psychiatric|psychology|counseling)\b',
            
            # Diagnostic services
            'laboratory': r'\b(?:laboratory|lab test|blood test|specimen|pathology)\b',
            'radiology': r'\b(?:radiology|x-ray|imaging|scan|ultrasound|MRI|CT)\b',
            'pathology': r'\b(?:pathology|biopsy|tissue|cytology)\b',
            
            # Therapeutic services
            'surgery': r'\b(?:surgery|surgical|operation|procedure)\b',
            'medicine': r'\b(?:medicine|medication|drug|pharmaceutical)\b',
            'dialysis': r'\b(?:dialysis|renal|kidney)\b',
            
            # Maternal and child health
            'maternity': r'\b(?:maternity|pregnancy|delivery|antenatal|postnatal)\b',
            'pediatric': r'\b(?:pediatric|paediatric|child|infant|newborn)\b',
            'family_planning': r'\b(?:family planning|contraceptive|reproductive)\b',
            
            # Emergency and critical care
            'emergency': r'\b(?:emergency|urgent|acute|trauma|casualty)\b',
            'icu': r'\b(?:ICU|intensive care|critical care|HDU)\b',
            'ambulance': r'\b(?:ambulance|transport|evacuation)\b',
            
            # Chronic disease management
            'diabetes': r'\b(?:diabetes|diabetic|insulin|glucose)\b',
            'hypertension': r'\b(?:hypertension|blood pressure|antihypertensive)\b',
            'cancer': r'\b(?:cancer|oncology|chemotherapy|radiotherapy|tumor)\b',
            'hiv': r'\b(?:HIV|AIDS|antiretroviral|ARV)\b',
            
            # Rehabilitation services
            'physiotherapy': r'\b(?:physiotherapy|rehabilitation|physio)\b',
            'occupational_therapy': r'\b(?:occupational therapy|OT)\b',
            'speech_therapy': r'\b(?:speech therapy|speech pathology)\b',
            
            # Support services
            'nutrition': r'\b(?:nutrition|dietetic|diet|nutritionist)\b',
            'social_work': r'\b(?:social work|counseling|support)\b',
            'palliative': r'\b(?:palliative|hospice|end-of-life)\b'
        }
        
        print(f"\n=== HEALTHCARE SERVICE MENTIONS ===")
        service_counts = {}
        service_locations = {}
        
        for service_type, pattern in healthcare_services.items():
            matches = list(re.finditer(pattern, all_text, re.IGNORECASE))
            count = len(matches)
            service_counts[service_type] = count
            
            if count > 0:
                # Find which pages contain these services
                pages_with_service = set()
                for page_num, page_text in page_contents.items():
                    if re.search(pattern, page_text, re.IGNORECASE):
                        pages_with_service.add(page_num)
                service_locations[service_type] = sorted(list(pages_with_service))
        
        # Sort by frequency
        sorted_services = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)
        
        for service_type, count in sorted_services:
            if count > 0:
                pages = service_locations.get(service_type, [])
                pages_str = f"Pages {min(pages)}-{max(pages)}" if pages else ""
                print(f"  {service_type.replace('_', ' ').title()}: {count} mentions {pages_str}")
        
        # Look for pricing patterns
        print(f"\n=== PRICING PATTERNS ===")
        pricing_patterns = {
            'KES_explicit': r'KES\.?\s*[\d,]+',
            'KES_suffix': r'[\d,]+\s*KES',
            'dash_pricing': r'[\d,]+\s*/\-',
            'Ksh_variant': r'Ksh\.?\s*[\d,]+',
            'cost_mention': r'cost.*?[\d,]+',
            'fee_mention': r'fee.*?[\d,]+',
            'tariff_mention': r'tariff.*?[\d,]+',
            'charge_mention': r'charge.*?[\d,]+'
        }
        
        total_pricing_mentions = 0
        for pattern_name, pattern in pricing_patterns.items():
            matches = len(re.findall(pattern, all_text, re.IGNORECASE))
            if matches > 0:
                print(f"  {pattern_name}: {matches} instances")
                total_pricing_mentions += matches
        
        print(f"  Total pricing mentions: {total_pricing_mentions}")
        
        # Look for facility level mentions
        print(f"\n=== FACILITY LEVEL PATTERNS ===")
        facility_patterns = {
            'Level_explicit': r'Level\s*[1-6]',
            'Tier_mention': r'Tier\s*[1-6]',
            'Facility_type': r'(?:hospital|clinic|dispensary|centre|center)',
            'Primary_care': r'primary\s*(?:care|health)',
            'Secondary_care': r'secondary\s*(?:care|health)',
            'Tertiary_care': r'tertiary\s*(?:care|health)'
        }
        
        for pattern_name, pattern in facility_patterns.items():
            matches = len(re.findall(pattern, all_text, re.IGNORECASE))
            if matches > 0:
                print(f"  {pattern_name}: {matches} mentions")
        
        # Extract potential service lines that might be missed
        print(f"\n=== POTENTIAL MISSED SERVICES ANALYSIS ===")
        
        # Look for lines that contain service-like content but might not have been captured
        service_indicators = [
            r'treatment\s+of\s+\w+',
            r'management\s+of\s+\w+',
            r'care\s+for\s+\w+',
            r'therapy\s+for\s+\w+',
            r'screening\s+for\s+\w+',
            r'prevention\s+of\s+\w+',
            r'diagnosis\s+of\s+\w+'
        ]
        
        potential_services = set()
        for pattern in service_indicators:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            potential_services.update(matches)
        
        print(f"Found {len(potential_services)} potential service patterns:")
        for service in sorted(list(potential_services))[:10]:  # Show first 10
            print(f"  • {service}")
        
        # Save comprehensive analysis
        analysis_data = {
            'total_pages': len(pdf.pages),
            'total_text_length': len(all_text),
            'service_mentions': service_counts,
            'service_locations': service_locations,
            'total_pricing_mentions': total_pricing_mentions,
            'potential_services': list(potential_services)
        }
        
        with open('comprehensive_pdf_analysis.json', 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"\nComprehensive analysis saved to: comprehensive_pdf_analysis.json")
        
        # Estimate extraction completeness
        services_with_mentions = len([s for s, count in service_counts.items() if count > 0])
        total_service_types = len(healthcare_services)
        
        print(f"\n=== EXTRACTION COMPLETENESS ESTIMATE ===")
        print(f"Service types with mentions: {services_with_mentions}/{total_service_types} ({services_with_mentions/total_service_types*100:.1f}%)")
        print(f"Current extraction: 71 rules from {total_pricing_mentions} pricing mentions")
        print(f"Estimated extraction rate: {71/total_pricing_mentions*100:.1f}% of priced services" if total_pricing_mentions > 0 else "Cannot estimate")

if __name__ == "__main__":
    comprehensive_pdf_analysis()
