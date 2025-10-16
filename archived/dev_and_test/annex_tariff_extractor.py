#!/usr/bin/env python3
"""
Extract tariff data from SHIF PDF annex and find contradictions
"""

import pdfplumber
import pandas as pd
import re
from typing import List, Dict

def extract_annex_tariffs(pdf_path: str) -> pd.DataFrame:
    """Extract tariff tables from PDF annex (pages 40+)"""
    tariffs = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"📋 Extracting annex tariffs from {len(pdf.pages)} pages...")
        
        # Focus on pages 40+ where annex tables are located
        for page_num in range(39, len(pdf.pages)):  # Pages 40-54
            page = pdf.pages[page_num]
            tables = page.extract_tables()
            
            if tables:
                print(f"Processing page {page_num + 1}...")
                
                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue
                    
                    # Process each row in the table
                    for row in table[1:]:  # Skip header
                        if not row or len(row) < 4:
                            continue
                            
                        # Extract: ID, Specialty, Service, Tariff
                        try:
                            service_id = str(row[0]).strip()
                            specialty = str(row[1]).strip()
                            service_name = str(row[2]).strip()
                            tariff_text = str(row[3]).strip()
                            
                            # Extract numeric tariff
                            tariff = None
                            if tariff_text and tariff_text.replace(',', '').replace('.', '').isdigit():
                                tariff = float(tariff_text.replace(',', ''))
                            
                            if service_id and specialty and service_name and tariff:
                                tariffs.append({
                                    'service_id': service_id,
                                    'specialty': specialty,
                                    'service': service_name,
                                    'tariff': tariff,
                                    'source_page': page_num + 1,
                                    'source_type': 'annex_table',
                                    'service_key': service_name.lower().strip()
                                })
                                
                        except Exception as e:
                            continue
    
    df = pd.DataFrame(tariffs)
    print(f"✅ Extracted {len(df)} tariff entries from annex")
    
    if not df.empty:
        print(f"📊 Specialty breakdown:")
        for specialty, count in df['specialty'].value_counts().items():
            print(f"  {specialty}: {count} services")
    
    return df

def find_tariff_contradictions(main_rules_df: pd.DataFrame, annex_df: pd.DataFrame) -> List[Dict]:
    """Find contradictions between main document and annex tariffs"""
    print("🔍 Finding tariff contradictions between main document and annex...")
    
    contradictions = []
    
    # Get main document rules with tariffs
    main_with_tariffs = main_rules_df[main_rules_df['tariff'].notna() & (main_rules_df['tariff'] > 0)]
    print(f"📋 Main document: {len(main_with_tariffs)} rules with tariffs")
    print(f"📋 Annex: {len(annex_df)} specialty tariffs")
    
    # Look for service name matches between main and annex
    for _, main_rule in main_with_tariffs.iterrows():
        main_service = main_rule['service'].lower().strip()
        main_tariff = main_rule['tariff']
        
        # Find similar services in annex
        for _, annex_rule in annex_df.iterrows():
            annex_service = annex_rule['service'].lower().strip()
            annex_tariff = annex_rule['tariff']
            
            # Check for service name similarity
            similarity_score = 0
            
            # Direct substring match
            if len(main_service) > 10 and main_service in annex_service:
                similarity_score = 0.8
            elif len(annex_service) > 10 and annex_service in main_service:
                similarity_score = 0.8
            
            # Word overlap check
            main_words = set(main_service.split())
            annex_words = set(annex_service.split())
            
            if len(main_words) > 2 and len(annex_words) > 2:
                overlap = len(main_words.intersection(annex_words))
                total = len(main_words.union(annex_words))
                word_similarity = overlap / total if total > 0 else 0
                
                if word_similarity > 0.5:
                    similarity_score = max(similarity_score, word_similarity)
            
            # If similar services have different tariffs
            if similarity_score > 0.5 and main_tariff != annex_tariff:
                contradictions.append({
                    'type': 'Tariff_Document_Contradiction',
                    'service_1': main_rule['service'][:100],
                    'service_2': annex_rule['service'][:100],
                    'conflict_description': f'Same/similar service with different tariffs: KES {main_tariff:,.0f} (main) vs KES {annex_tariff:,.0f} (annex)',
                    'evidence_1': f"Page {main_rule['source_page']}: KES {main_tariff:,.0f}",
                    'evidence_2': f"Page {annex_rule['source_page']}: KES {annex_tariff:,.0f} ({annex_rule['specialty']})",
                    'severity': 'HIGH',
                    'confidence': 'HIGH' if similarity_score > 0.7 else 'MEDIUM',
                    'similarity_score': round(similarity_score, 2),
                    'specialty': annex_rule['specialty']
                })
    
    return contradictions

def find_annex_internal_contradictions(annex_df: pd.DataFrame) -> List[Dict]:
    """Find contradictions within the annex itself"""
    print("🔍 Finding internal contradictions within annex...")
    
    contradictions = []
    
    # Group by service name and look for duplicates with different tariffs
    for service_key in annex_df['service_key'].unique():
        service_group = annex_df[annex_df['service_key'] == service_key]
        
        if len(service_group) > 1:
            tariffs = service_group['tariff'].unique()
            
            if len(tariffs) > 1:
                # Found same service with different tariffs
                for i in range(len(service_group)):
                    for j in range(i + 1, len(service_group)):
                        rule1 = service_group.iloc[i]
                        rule2 = service_group.iloc[j]
                        
                        if rule1['tariff'] != rule2['tariff']:
                            contradictions.append({
                                'type': 'Annex_Internal_Contradiction',
                                'service_1': rule1['service'][:100],
                                'service_2': rule2['service'][:100],
                                'conflict_description': f'Same service in different specialties with different tariffs: KES {rule1["tariff"]:,.0f} vs KES {rule2["tariff"]:,.0f}',
                                'evidence_1': f"Page {rule1['source_page']}: {rule1['specialty']} - KES {rule1['tariff']:,.0f}",
                                'evidence_2': f"Page {rule2['source_page']}: {rule2['specialty']} - KES {rule2['tariff']:,.0f}",
                                'severity': 'HIGH',
                                'confidence': 'HIGH',
                                'specialty_1': rule1['specialty'],
                                'specialty_2': rule2['specialty']
                            })
    
    return contradictions

def main():
    """Extract annex tariffs and find contradictions"""
    print("📋 SHIF Annex Tariff Analysis")
    print("=" * 50)
    
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    
    # Extract annex tariffs
    annex_df = extract_annex_tariffs(pdf_path)
    
    if annex_df.empty:
        print("❌ No tariff data found in annex")
        return
    
    # Save annex data
    annex_df.to_csv('outputs_comprehensive/annex_tariffs.csv', index=False)
    print(f"💾 Saved {len(annex_df)} annex tariffs")
    
    # Load main document rules
    main_rules_df = pd.read_csv('outputs_comprehensive/rules_comprehensive.csv')
    
    # Find contradictions
    all_contradictions = []
    
    # 1. Main document vs Annex contradictions
    document_contradictions = find_tariff_contradictions(main_rules_df, annex_df)
    all_contradictions.extend(document_contradictions)
    
    # 2. Internal annex contradictions
    internal_contradictions = find_annex_internal_contradictions(annex_df)
    all_contradictions.extend(internal_contradictions)
    
    if all_contradictions:
        contradictions_df = pd.DataFrame(all_contradictions)
        contradictions_df.to_csv('outputs_comprehensive/tariff_contradictions.csv', index=False)
        
        print(f"\n✅ Found {len(contradictions_df)} tariff contradictions")
        
        # Show breakdown by type
        print(f"\n📊 Contradictions by type:")
        for contradiction_type, count in contradictions_df['type'].value_counts().items():
            print(f"  {contradiction_type}: {count}")
        
        # Show high-priority samples
        print(f"\n🚨 Sample High-Priority Contradictions:")
        for _, conflict in contradictions_df.head(5).iterrows():
            print(f"  {conflict['type']}: {conflict['conflict_description']}")
            print(f"    Evidence: {conflict['evidence_1']} | {conflict['evidence_2']}")
            print()
            
    else:
        print("\nℹ️ No tariff contradictions found")
    
    print(f"\n✅ Annex Analysis Complete")

if __name__ == "__main__":
    main()