#!/usr/bin/env python3
"""
Focused test of Tabula + AI Hierarchical Extractor
Tests AI processing on a small subset to validate API key works
"""

import pandas as pd
import tabula
import json
import os
from openai import OpenAI
from typing import List, Dict

class FocusedTabulaAITest:
    def __init__(self, pdf_path: str, api_key: str):
        self.pdf_path = pdf_path
        self.client = OpenAI(api_key=api_key)
        
    def test_focused_extraction(self) -> Dict:
        """Test extraction on key pages only"""
        
        print("🔍 FOCUSED TABULA + AI TEST")
        print("=" * 40)
        
        # Test on key pages that should have hierarchical structure
        test_pages = [5, 10, 15, 20, 25]  # Sample pages
        
        all_tables = []
        
        for page in test_pages:
            print(f"   📄 Testing page {page}...")
            
            try:
                # Extract tables from this page
                tables = tabula.read_pdf(
                    self.pdf_path, 
                    pages=page, 
                    multiple_tables=True,
                    pandas_options={'header': None},
                    lattice=True
                )
                
                for table_idx, df in enumerate(tables):
                    if df is not None and not df.empty and len(df) > 1:
                        # Convert to text for AI processing
                        table_text = self._df_to_text(df, page, table_idx)
                        
                        table_data = {
                            'page': page,
                            'table_index': table_idx,
                            'text_representation': table_text,
                            'row_count': len(df),
                            'col_count': len(df.columns)
                        }
                        all_tables.append(table_data)
                        
            except Exception as e:
                print(f"   ⚠️ Error on page {page}: {e}")
                continue
        
        print(f"   ✅ Extracted {len(all_tables)} tables from {len(test_pages)} pages")
        
        if not all_tables:
            return {"error": "No tables extracted", "tables_found": 0}
        
        # Test AI processing on first table
        print("🤖 Testing AI processing...")
        
        test_table = all_tables[0]
        ai_result = self._test_ai_analysis(test_table)
        
        return {
            "tables_extracted": len(all_tables),
            "test_pages": test_pages,
            "first_table": test_table,
            "ai_test_result": ai_result,
            "api_working": ai_result is not None
        }
    
    def _df_to_text(self, df: pd.DataFrame, page: int, table_idx: int) -> str:
        """Convert DataFrame to text"""
        text_lines = [f"PAGE {page} - TABLE {table_idx}:"]
        
        for _, row in df.iterrows():
            row_text = ' | '.join([str(cell) for cell in row if pd.notna(cell) and str(cell).strip()])
            if len(row_text) > 10:
                text_lines.append(row_text)
        
        return '\n'.join(text_lines)
    
    def _test_ai_analysis(self, table_data: Dict) -> Dict:
        """Test AI analysis on single table"""
        
        prompt = f"""Analyze this healthcare policy table for hierarchical structure.

TABLE DATA:
{table_data['text_representation']}

Identify:
1. Any super headings (major fund/package names in ALL CAPS)
2. Service category headers (with column structure like "ScopeAccessPointTariffAccessRule")
3. Individual services listed

Return JSON format:
{{
  "super_heading": "found heading or null",
  "service_categories": [
    {{
      "category_name": "name",
      "services": ["service1", "service2"]
    }}
  ],
  "analysis": "brief description of what was found"
}}"""

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
            print(f"   ✅ AI processing successful")
            return ai_result
            
        except Exception as e:
            print(f"   ❌ AI processing failed: {e}")
            return None

def main():
    """Run focused test"""
    
    # Use provided API key directly
    api_key = "OPENAI_API_KEY_REMOVED"
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    
    tester = FocusedTabulaAITest(pdf_path, api_key)
    results = tester.test_focused_extraction()
    
    print(f"\n📊 FOCUSED TEST RESULTS:")
    print(f"   Tables extracted: {results.get('tables_extracted', 0)}")
    print(f"   API working: {results.get('api_working', False)}")
    
    if results.get('ai_test_result'):
        ai_result = results['ai_test_result']
        print(f"   AI found super heading: {ai_result.get('super_heading', 'None')}")
        print(f"   AI found categories: {len(ai_result.get('service_categories', []))}")
    
    # Save test results
    with open("focused_test_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Test results saved to: focused_test_results.json")

if __name__ == "__main__":
    main()