#!/usr/bin/env python3
"""
Tabula + AI Hierarchical Service Extractor
1. Use tabula-py to extract structured table data
2. Use OpenAI to understand and categorize the hierarchical structure
"""

import pandas as pd
import tabula
import json
import os
from openai import OpenAI
from typing import List, Dict

class TabulaAIHierarchicalExtractor:
    def __init__(self, pdf_path: str, api_key: str):
        self.pdf_path = pdf_path
        self.client = OpenAI(api_key=api_key)
        
    def extract_with_tabula_ai_pipeline(self) -> Dict:
        """Main extraction pipeline: Tabula → AI categorization"""
        
        print("🔍 TABULA + AI HIERARCHICAL EXTRACTION PIPELINE")
        print("=" * 60)
        
        # Step 1: Extract all tables with tabula
        print("📊 Step 1: Extracting tables with tabula-py...")
        raw_tables = self._extract_tables_with_tabula()
        print(f"   ✅ Extracted {len(raw_tables)} tables from PDF")
        
        # Step 2: Process each table with AI to identify hierarchy
        print("🤖 Step 2: AI processing for hierarchical structure...")
        hierarchical_data = self._process_tables_with_ai(raw_tables)
        
        # Step 3: Organize results
        organized_results = self._organize_hierarchical_results(hierarchical_data)
        
        return organized_results
    
    def _extract_tables_with_tabula(self) -> List[Dict]:
        """Extract all tables using tabula-py with comprehensive settings"""
        
        all_tables = []
        
        try:
            # Extract from key pages, focusing on annex service areas
            for page in range(19, 31):  # Focus on critical annex pages first
                try:
                    # Use multiple extraction methods for comprehensive coverage
                    tables_lattice = tabula.read_pdf(
                        self.pdf_path, 
                        pages=page, 
                        multiple_tables=True,
                        pandas_options={'header': None},
                        lattice=True
                    )
                    
                    tables_stream = tabula.read_pdf(
                        self.pdf_path,
                        pages=page,
                        multiple_tables=True, 
                        pandas_options={'header': None},
                        stream=True
                    )
                    
                    # Combine both extraction methods
                    page_tables = tables_lattice + tables_stream
                    
                    for table_idx, df in enumerate(page_tables):
                        if df is not None and not df.empty and len(df) > 1:
                            # Convert to text representation for AI processing
                            table_text = self._df_to_text(df, page, table_idx)
                            
                            table_data = {
                                'page': page,
                                'table_index': table_idx,
                                'dataframe': df,
                                'text_representation': table_text,
                                'row_count': len(df),
                                'col_count': len(df.columns)
                            }
                            all_tables.append(table_data)
                            
                except Exception as e:
                    continue  # Skip problematic pages
                    
        except Exception as e:
            print(f"   ❌ Tabula extraction failed: {e}")
            
        return all_tables
    
    def _df_to_text(self, df: pd.DataFrame, page: int, table_idx: int) -> str:
        """Convert DataFrame to clean text for AI processing"""
        
        text_lines = [f"PAGE {page} - TABLE {table_idx}:"]
        
        for _, row in df.iterrows():
            # Join non-null values with ' | ' separator
            row_text = ' | '.join([str(cell) for cell in row if pd.notna(cell) and str(cell).strip()])
            if len(row_text) > 10:  # Only meaningful rows
                text_lines.append(row_text)
        
        return '\n'.join(text_lines)
    
    def _process_tables_with_ai(self, raw_tables: List[Dict]) -> List[Dict]:
        """Process tables with AI to identify hierarchical structure"""
        
        hierarchical_results = []
        
        # Process in batches to manage context length
        batch_size = 3
        for i in range(0, len(raw_tables), batch_size):
            batch = raw_tables[i:i+batch_size]
            
            # Create comprehensive prompt for hierarchical analysis
            batch_text = self._create_batch_text(batch)
            
            ai_analysis = self._analyze_batch_with_ai(batch_text, batch)
            if ai_analysis:
                hierarchical_results.extend(ai_analysis)
        
        return hierarchical_results
    
    def _create_batch_text(self, batch: List[Dict]) -> str:
        """Create text representation of a batch of tables"""
        
        batch_lines = []
        for table_data in batch:
            batch_lines.append(table_data['text_representation'])
            batch_lines.append("")  # Separator
        
        return '\n'.join(batch_lines)
    
    def _analyze_batch_with_ai(self, batch_text: str, batch_tables: List[Dict]) -> List[Dict]:
        """Use AI to analyze table batch for hierarchical structure"""
        
        prompt = f"""You are analyzing Kenya SHIF healthcare policy tables to identify hierarchical structure.

TASK: Identify the 3-tier hierarchy in these tables:
1. **Super Headings**: Major categories like "PRIMARY HEALTHCARE FUND", "SURGICAL SERVICES PACKAGE"
2. **Service Category Headers**: Lines containing "ScopeAccessPointTariffAccessRule" with a service category name
3. **Individual Services**: Specific healthcare services with their details

TABLES TO ANALYZE:
{batch_text}

For each table, identify:
1. Any super headings (major fund/package names)
2. Any service category headers (with column structure)  
3. Individual services with their hierarchy

EXAMPLE OUTPUT FORMAT:
{{
  "page": 5,
  "super_heading": "PRIMARY HEALTHCARE FUND",
  "service_categories": [
    {{
      "category_name": "OPTICAL HEALTH SERVICES", 
      "has_column_headers": true,
      "services": [
        {{
          "service_name": "Eye examination",
          "scope": "Basic eye health",
          "access_point": "Level 2-4",
          "tariff": "KES 1500",
          "access_rules": "Annual screening"
        }}
      ]
    }}
  ]
}}

Return JSON array of analyzed table structures. Be comprehensive - capture the full hierarchical relationships."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
                
            try:
                ai_results = json.loads(result_text.strip())
                if not isinstance(ai_results, list):
                    ai_results = [ai_results]
                
                # Add original table data for reference
                for i, result in enumerate(ai_results):
                    if i < len(batch_tables):
                        result['original_table'] = {
                            'page': batch_tables[i]['page'],
                            'table_index': batch_tables[i]['table_index'],
                            'row_count': batch_tables[i]['row_count'],
                            'col_count': batch_tables[i]['col_count']
                        }
                
                return ai_results
                
            except json.JSONDecodeError:
                print(f"   ⚠️ AI returned invalid JSON for batch")
                return []
                
        except Exception as e:
            print(f"   ❌ AI analysis failed for batch: {e}")
            return []
    
    def _organize_hierarchical_results(self, hierarchical_data: List[Dict]) -> Dict:
        """Organize the AI results into clean hierarchical structure"""
        
        super_headings = []
        service_categories = []
        individual_services = []
        
        for table_analysis in hierarchical_data:
            # Extract super heading
            if 'super_heading' in table_analysis and table_analysis['super_heading']:
                super_heading = {
                    'heading_text': table_analysis['super_heading'],
                    'page': table_analysis.get('page', 0),
                    'source': 'ai_tabula_extraction'
                }
                super_headings.append(super_heading)
            
            # Extract service categories and their services
            if 'service_categories' in table_analysis:
                for category_data in table_analysis['service_categories']:
                    category = {
                        'category_name': category_data.get('category_name', ''),
                        'super_heading': table_analysis.get('super_heading', ''),
                        'has_column_headers': category_data.get('has_column_headers', False),
                        'page': table_analysis.get('page', 0),
                        'services_count': len(category_data.get('services', [])),
                        'source': 'ai_tabula_extraction'
                    }
                    service_categories.append(category)
                    
                    # Extract individual services
                    for service_data in category_data.get('services', []):
                        service = {
                            'service_name': service_data.get('service_name', ''),
                            'super_heading': table_analysis.get('super_heading', ''),
                            'service_category': category_data.get('category_name', ''),
                            'scope': service_data.get('scope', ''),
                            'access_point': service_data.get('access_point', ''),
                            'tariff': service_data.get('tariff', ''),
                            'access_rules': service_data.get('access_rules', ''),
                            'page': table_analysis.get('page', 0),
                            'extraction_method': 'tabula_ai_hierarchical',
                            'source': 'ai_tabula_extraction'
                        }
                        individual_services.append(service)
        
        # Remove duplicates
        super_headings = self._remove_duplicate_headings(super_headings)
        service_categories = self._remove_duplicate_categories(service_categories)
        individual_services = self._remove_duplicate_services(individual_services)
        
        return {
            'super_headings': super_headings,
            'service_categories': service_categories,
            'individual_services': individual_services,
            'summary': {
                'total_super_headings': len(super_headings),
                'total_service_categories': len(service_categories), 
                'total_individual_services': len(individual_services)
            }
        }
    
    def _remove_duplicate_headings(self, headings: List[Dict]) -> List[Dict]:
        """Remove duplicate super headings"""
        seen = set()
        unique_headings = []
        
        for heading in headings:
            key = heading['heading_text'].lower().strip()
            if key not in seen:
                seen.add(key)
                unique_headings.append(heading)
        
        return unique_headings
    
    def _remove_duplicate_categories(self, categories: List[Dict]) -> List[Dict]:
        """Remove duplicate service categories"""
        seen = set()
        unique_categories = []
        
        for category in categories:
            key = (category['category_name'].lower().strip(), category['super_heading'].lower().strip())
            if key not in seen:
                seen.add(key)
                unique_categories.append(category)
        
        return unique_categories
    
    def _remove_duplicate_services(self, services: List[Dict]) -> List[Dict]:
        """Remove duplicate individual services"""
        seen = set()
        unique_services = []
        
        for service in services:
            key = service['service_name'].lower().strip()
            if key not in seen and len(key) > 5:
                seen.add(key)
                unique_services.append(service)
        
        return unique_services
    
    def save_hierarchical_results(self, results: Dict, output_dir: str):
        """Save hierarchical results to files"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Save super headings
        super_df = pd.DataFrame(results['super_headings'])
        super_df.to_csv(f"{output_dir}/super_headings_tabula_ai.csv", index=False)
        
        # Save service categories
        categories_df = pd.DataFrame(results['service_categories'])
        categories_df.to_csv(f"{output_dir}/service_categories_tabula_ai.csv", index=False)
        
        # Save individual services
        services_df = pd.DataFrame(results['individual_services'])
        services_df.to_csv(f"{output_dir}/individual_services_tabula_ai.csv", index=False)
        
        # Save complete results as JSON
        with open(f"{output_dir}/tabula_ai_complete_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📁 Results saved to: {output_dir}")
        return output_dir

def main():
    """Test the Tabula + AI extraction"""
    
    # Use provided API key directly as instructed
    api_key = "OPENAI_API_KEY_REMOVED"
    
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    output_dir = f"tabula_ai_hierarchical_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("🚀 TABULA + AI HIERARCHICAL EXTRACTION")
    print("=" * 50)
    
    extractor = TabulaAIHierarchicalExtractor(pdf_path, api_key)
    results = extractor.extract_with_tabula_ai_pipeline()
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"   Super headings: {results['summary']['total_super_headings']}")
    print(f"   Service categories: {results['summary']['total_service_categories']}")
    print(f"   Individual services: {results['summary']['total_individual_services']}")
    
    # Save results
    extractor.save_hierarchical_results(results, output_dir)
    
    # Print hierarchy preview
    print(f"\n🎯 HIERARCHICAL STRUCTURE FOUND:")
    for super_heading in results['super_headings']:
        print(f"📊 {super_heading['heading_text']} (page {super_heading['page']})")
        
        # Show categories under this super heading
        related_categories = [cat for cat in results['service_categories'] 
                            if cat['super_heading'] == super_heading['heading_text']]
        
        for category in related_categories:
            print(f"   📋 └── {category['category_name']} ({category['services_count']} services)")

if __name__ == "__main__":
    main()