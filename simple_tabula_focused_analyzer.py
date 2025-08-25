#!/usr/bin/env python3
"""
Simple Tabula-Focused Medical Analyzer
Prioritizes your simple tabula approach with minimal AI dependencies
"""

import pandas as pd
import re
import tabula
import json
import os
from typing import List, Dict, Optional

class SimpleTabulaFocusedAnalyzer:
    def __init__(self):
        self.annex_procedures = []
        self.specialties_analysis = {}
        
    def analyze_medical_document(self, pdf_path: str) -> Dict:
        """Main analysis focusing on simple tabula extraction"""
        
        print("🚀 SIMPLE TABULA-FOCUSED MEDICAL ANALYZER")
        print("=" * 60)
        print("   📊 Prioritizing proven simple tabula approach")
        print("   🎯 Focus: Annex procedures with complete specialty/tariff data")
        
        results = {}
        
        # PHASE 1: Simple tabula extraction (your proven method)
        print("\n📊 PHASE 1: Simple Tabula Extraction (Annex Pages 19-54)")
        self.annex_procedures = self._extract_annex_tabula_simple(pdf_path, "19-54")
        print(f"   ✅ Extracted {len(self.annex_procedures)} procedures")
        
        # PHASE 2: Specialty analysis
        print("\n🏥 PHASE 2: Specialty Analysis")
        self.specialties_analysis = self._analyze_specialties()
        print(f"   ✅ Analyzed {len(self.specialties_analysis)} specialties")
        
        # PHASE 3: Cost analysis  
        print("\n💰 PHASE 3: Cost Analysis")
        cost_analysis = self._analyze_costs()
        print(f"   ✅ Analyzed cost distribution across procedures")
        
        # PHASE 4: Compile results
        results = {
            'total_procedures': len(self.annex_procedures),
            'total_specialties': len(self.specialties_analysis),
            'procedures': self.annex_procedures.to_dict('records') if not self.annex_procedures.empty else [],
            'specialties_analysis': self.specialties_analysis,
            'cost_analysis': cost_analysis,
            'extraction_method': 'simple_tabula_focused',
            'source_pages': '19-54',
            'data_quality': 'high_confidence'
        }
        
        return results
    
    def _extract_annex_tabula_simple(self, path: str, pages: str = "19-54"):
        """
        Your proven simple tabula approach for annex extraction
        Handles continuations and specialty forward-filling perfectly
        """
        import tabula
        import pandas as pd
        import re
        
        print(f"   📋 Extracting tables from pages {pages}...")
        
        dfs = tabula.read_pdf(
            path,
            pages=pages,
            multiple_tables=True,
            pandas_options={"header": None}
        ) or []
        
        print(f"   📊 Found {len(dfs)} tables to process")
        results = []

        for df_idx, df in enumerate(dfs):
            if df is None or df.empty or df.shape[1] < 3:
                continue

            df = df.iloc[:, :4].copy()
            df.columns = ["num","specialty","intervention","tariff"]

            # forward fill specialty
            df["specialty"] = df["specialty"].ffill()

            merged_rows = []
            current = None
            pre_buffer = []  # holds continuation lines that appear BEFORE a numbered row

            for _, row in df.iterrows():
                num = row["num"]
                spec = str(row["specialty"]).strip() if pd.notna(row["specialty"]) else ""
                interv = str(row["intervention"]).strip() if pd.notna(row["intervention"]) else ""
                tariff_raw = str(row["tariff"]).strip() if pd.notna(row["tariff"]) else ""

                if pd.notna(num):  # start of a new entry
                    # flush previous
                    if current:
                        merged_rows.append(current)

                    # stitch any text collected ABOVE the number into the new intervention
                    start_text = " ".join(pre_buffer + ([interv] if interv else []))
                    pre_buffer = []  # reset buffer

                    current = {
                        "id": int(num) if str(num).isdigit() else num,
                        "specialty": spec,
                        "intervention": start_text.strip(),
                        "tariff_text": tariff_raw
                    }
                else:
                    # continuation row
                    if current is None:
                        # no current yet → this line belongs to the NEXT numbered row
                        if interv:
                            pre_buffer.append(interv)
                        # sometimes tariff appears on a pre-line, keep last seen
                        if tariff_raw:
                            # stash on buffer end marker so it can override later if needed
                            pre_buffer.append(f"[TARIFF:{tariff_raw}]")
                        continue

                    if interv:
                        current["intervention"] = (current["intervention"] + " " + interv).strip()
                    if tariff_raw:
                        current["tariff_text"] = tariff_raw

            if current:
                merged_rows.append(current)

            # clean any accidental tariff markers in pre_buffer merges
            for r in merged_rows:
                if "[TARIFF:" in r["intervention"]:
                    # drop those markers from text; tariff already handled by numbered line normally
                    r["intervention"] = re.sub(r"\[TARIFF:.*?\]", "", r["intervention"]).strip()

            results.extend(merged_rows)
            print(f"   📋 Table {df_idx + 1}: {len(merged_rows)} procedures")

        # Convert to DataFrame and clean
        df_result = pd.DataFrame(results, columns=["id","specialty","intervention","tariff_text"])
        
        if not df_result.empty:
            # tidy tariff to numeric
            df_result["tariff"] = (
                df_result["tariff_text"]
                .fillna("").astype(str)
                .str.replace(r"[^\d.]", "", regex=True)
                .replace("", pd.NA)
                .astype(float)
            )
            df_result = df_result.drop(columns=["tariff_text"])

            # optional tidying
            df_result["specialty"] = df_result["specialty"].str.strip()
            df_result["intervention"] = (
                df_result["intervention"]
                .str.replace(r"\s+", " ", regex=True)
                .str.replace(r"\s*/\s*", " / ", regex=True)
                .str.replace(r"\s*-\s*", " - ", regex=True)
                .str.strip()
            )
            # make id a nullable integer
            df_result["id"] = pd.to_numeric(df_result["id"], errors="coerce").astype("Int64")

            # drop obviously empty rows
            df_result = df_result[(df_result["specialty"] != "") & (df_result["intervention"] != "")]

            # sort & dedupe
            df_result = df_result.drop_duplicates().sort_values(["specialty","id","intervention"], na_position="last").reset_index(drop=True)

        return df_result
    
    def _analyze_specialties(self) -> Dict:
        """Analyze procedures by medical specialty"""
        
        if self.annex_procedures.empty:
            return {}
        
        specialties = {}
        
        for _, row in self.annex_procedures.iterrows():
            specialty = row['specialty']
            tariff = row['tariff'] if pd.notna(row['tariff']) else 0
            
            if specialty not in specialties:
                specialties[specialty] = {
                    'procedure_count': 0,
                    'total_cost': 0,
                    'procedures': [],
                    'min_tariff': float('inf'),
                    'max_tariff': 0
                }
            
            specialties[specialty]['procedure_count'] += 1
            specialties[specialty]['total_cost'] += tariff
            specialties[specialty]['procedures'].append({
                'id': row.get('id'),
                'intervention': row['intervention'],
                'tariff': tariff
            })
            
            if tariff > 0:
                specialties[specialty]['min_tariff'] = min(specialties[specialty]['min_tariff'], tariff)
                specialties[specialty]['max_tariff'] = max(specialties[specialty]['max_tariff'], tariff)
        
        # Calculate averages and finalize
        for specialty_data in specialties.values():
            if specialty_data['procedure_count'] > 0:
                specialty_data['avg_tariff'] = specialty_data['total_cost'] / specialty_data['procedure_count']
            else:
                specialty_data['avg_tariff'] = 0
            
            # Fix infinite min values
            if specialty_data['min_tariff'] == float('inf'):
                specialty_data['min_tariff'] = 0
        
        return specialties
    
    def _analyze_costs(self) -> Dict:
        """Analyze cost distribution and patterns"""
        
        if self.annex_procedures.empty:
            return {}
        
        tariffs = self.annex_procedures['tariff'].dropna()
        
        if tariffs.empty:
            return {}
        
        cost_analysis = {
            'total_procedures_with_tariffs': len(tariffs),
            'min_tariff': float(tariffs.min()),
            'max_tariff': float(tariffs.max()),
            'avg_tariff': float(tariffs.mean()),
            'median_tariff': float(tariffs.median()),
            'std_tariff': float(tariffs.std()),
            'tariff_ranges': {
                'low_cost': len(tariffs[tariffs < 50000]),
                'medium_cost': len(tariffs[(tariffs >= 50000) & (tariffs < 200000)]),
                'high_cost': len(tariffs[(tariffs >= 200000) & (tariffs < 500000)]),
                'very_high_cost': len(tariffs[tariffs >= 500000])
            },
            'top_10_expensive': self.annex_procedures.nlargest(10, 'tariff')[['specialty', 'intervention', 'tariff']].to_dict('records'),
            'top_10_affordable': self.annex_procedures.nsmallest(10, 'tariff')[['specialty', 'intervention', 'tariff']].to_dict('records')
        }
        
        return cost_analysis
    
    def save_results(self, results: Dict, output_dir: str):
        """Save all results to files"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Save complete results as JSON
        with open(f"{output_dir}/simple_tabula_focused_results.json", 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save procedures CSV
        if not self.annex_procedures.empty:
            self.annex_procedures.to_csv(f"{output_dir}/annex_procedures_complete.csv", index=False)
        
        # Save specialty analysis
        specialty_summary = []
        for specialty, data in results['specialties_analysis'].items():
            summary = {
                'specialty': specialty,
                'procedure_count': data['procedure_count'],
                'min_tariff': data['min_tariff'],
                'max_tariff': data['max_tariff'], 
                'avg_tariff': round(data['avg_tariff'], 2),
                'total_cost': data['total_cost']
            }
            specialty_summary.append(summary)
        
        specialty_df = pd.DataFrame(specialty_summary)
        specialty_df = specialty_df.sort_values('procedure_count', ascending=False)
        specialty_df.to_csv(f"{output_dir}/specialty_analysis.csv", index=False)
        
        print(f"📁 Results saved to: {output_dir}")
        return output_dir

def main():
    """Run simple tabula-focused analysis"""
    
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    output_dir = f"simple_tabula_focused_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    # Run analysis
    analyzer = SimpleTabulaFocusedAnalyzer()
    results = analyzer.analyze_medical_document(pdf_path)
    
    # Display summary
    print(f"\n🎯 ANALYSIS COMPLETE")
    print(f"   Total procedures: {results['total_procedures']}")
    print(f"   Total specialties: {results['total_specialties']}")
    
    if results['specialties_analysis']:
        print(f"\n🏥 TOP SPECIALTIES BY VOLUME:")
        sorted_specialties = sorted(results['specialties_analysis'].items(), 
                                  key=lambda x: x[1]['procedure_count'], reverse=True)
        
        for specialty, data in sorted_specialties[:10]:
            print(f"   • {specialty}: {data['procedure_count']} procedures (avg: KES {data['avg_tariff']:,.0f})")
    
    if results['cost_analysis']:
        cost_data = results['cost_analysis']
        print(f"\n💰 COST ANALYSIS:")
        print(f"   • Price range: KES {cost_data['min_tariff']:,.0f} - {cost_data['max_tariff']:,.0f}")
        print(f"   • Average: KES {cost_data['avg_tariff']:,.0f}")
        print(f"   • High-cost procedures (>500K): {cost_data['tariff_ranges']['very_high_cost']}")
    
    # Save results
    analyzer.save_results(results, output_dir)

if __name__ == "__main__":
    main()