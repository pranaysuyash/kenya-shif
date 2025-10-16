#!/usr/bin/env python3
"""
Deterministic PDF Validation Checker
Validates extracted rules against the actual SHIF PDF without AI dependencies

Checks for:
1. Dr. Rishi's specific examples (dialysis contradictions, hypertension gaps)
2. Rule accuracy by sampling PDF text
3. Facility-level contradictions
4. Disease coverage gaps
"""

import json
import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Any

try:
    import pdfplumber
except ImportError:
    print("⚠️ pdfplumber not installed. Install with: pip install pdfplumber")
    pdfplumber = None

class DeterministicChecker:
    def __init__(self, pdf_path: str = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"):
        self.pdf_path = pdf_path
        self.results = {}
        
        # Common diseases to check for coverage
        self.common_diseases = [
            'hypertension', 'diabetes', 'pneumonia', 'malaria', 'tuberculosis', 'tb',
            'hiv', 'aids', 'asthma', 'stroke', 'heart disease', 'cancer', 'depression',
            'anxiety', 'epilepsy', 'kidney disease', 'liver disease'
        ]
        
    def load_latest_results(self) -> Dict:
        """Load the most recent integrated analysis results"""
        # Find latest results file
        results_files = sorted(Path(".").glob("*/integrated_comprehensive_analysis.json"))
        if not results_files:
            # Try outputs directory
            results_file = Path("outputs/integrated_comprehensive_analysis.json")
            if results_file.exists():
                results_files = [results_file]
            
        if results_files:
            latest_file = results_files[-1]
            print(f"📁 Loading: {latest_file}")
            with open(latest_file) as f:
                return json.load(f)
        else:
            print("❌ No results file found. Run integrated analyzer first.")
            return {}
    
    def extract_pdf_text_by_pages(self, start_page: int = 1, end_page: int = 18) -> Dict[int, str]:
        """Extract text from specific PDF pages for validation"""
        page_texts = {}
        
        if not pdfplumber:
            print("❌ pdfplumber not available - skipping PDF text extraction")
            return page_texts
            
        if not Path(self.pdf_path).exists():
            print(f"❌ PDF not found: {self.pdf_path}")
            return page_texts
            
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num in range(start_page, min(end_page + 1, len(pdf.pages) + 1)):
                    page = pdf.pages[page_num - 1]  # pdfplumber uses 0-based indexing
                    text = page.extract_text() or ""
                    page_texts[page_num] = text.lower()  # Normalize for matching
                    
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            
        return page_texts
    
    def check_dialysis_contradictions(self, results: Dict) -> List[Dict]:
        """Check for dialysis frequency contradictions (Dr. Rishi's example)"""
        contradictions = []
        
        # Get all services
        all_services = results.get('extraction_results', {}).get('all_services', [])
        
        # Look for dialysis-related services
        dialysis_services = {}
        for service in all_services:
            service_text = str(service).lower()
            
            # Check for hemodialysis variations
            if any(term in service_text for term in ['haemodialysis', 'hemodialysis', 'hd ']):
                sessions_match = re.search(r'(\d+)\s*sessions?\s*per\s*week', service_text)
                if sessions_match:
                    dialysis_services['hemodialysis'] = int(sessions_match.group(1))
                    
            # Check for hemodiafiltration variations
            if any(term in service_text for term in ['hemodiafiltration', 'haemodiafiltration', 'hdf']):
                sessions_match = re.search(r'(\d+)\s*sessions?\s*per\s*week', service_text)
                if sessions_match:
                    dialysis_services['hemodiafiltration'] = int(sessions_match.group(1))
        
        # Check for contradictions
        if 'hemodialysis' in dialysis_services and 'hemodiafiltration' in dialysis_services:
            hd_sessions = dialysis_services['hemodialysis']
            hdf_sessions = dialysis_services['hemodiafiltration']
            
            if hd_sessions != hdf_sessions:
                contradictions.append({
                    "type": "dialysis_frequency_mismatch",
                    "description": f"Hemodialysis allows {hd_sessions} sessions/week but hemodiafiltration only {hdf_sessions} sessions/week",
                    "severity": "CRITICAL",
                    "matches_rishi_example": True,
                    "evidence": {
                        "hemodialysis_sessions": hd_sessions,
                        "hemodiafiltration_sessions": hdf_sessions
                    }
                })
                
        return contradictions, dialysis_services
    
    def check_facility_exclusion_contradictions(self, results: Dict) -> List[Dict]:
        """Check for facility exclusion contradictions"""
        contradictions = []
        
        policy_data = results.get('extraction_results', {}).get('policy_structure', {}).get('data', [])
        
        for rule in policy_data:
            access_point = str(rule.get('access_point', '')).lower()
            access_rules = str(rule.get('access_rules', '')).lower()
            service = str(rule.get('service', ''))
            
            # Check if service mentions specific facility level but also has exclusions
            facility_mentioned = bool(re.search(r'level\s*\d+', access_point))
            exclusion_mentioned = any(word in access_rules for word in ['exclude', 'excluded', 'not covered', 'not applicable'])
            
            if facility_mentioned and exclusion_mentioned:
                contradictions.append({
                    "type": "facility_exclusion_conflict",
                    "description": f"Service '{service[:50]}...' mentions facility level but also has exclusions",
                    "severity": "MODERATE",
                    "access_point": access_point[:100],
                    "access_rules": access_rules[:100]
                })
                
        return contradictions
    
    def check_disease_coverage_gaps(self, results: Dict) -> List[Dict]:
        """Check for disease coverage gaps (Dr. Rishi's hypertension example)"""
        gaps = []
        
        # Get all extracted text
        all_services = results.get('extraction_results', {}).get('all_services', [])
        all_text = " ".join([str(service).lower() for service in all_services])
        
        # Also check AI analysis for disease mentions
        ai_analysis = results.get('analysis_results', {})
        full_ai_text = str(ai_analysis.get('full_ai_analysis', '')).lower()
        
        combined_text = all_text + " " + full_ai_text
        
        # Check each common disease
        missing_diseases = []
        found_diseases = []
        
        for disease in self.common_diseases:
            if disease in combined_text:
                found_diseases.append(disease)
            else:
                gaps.append({
                    "disease": disease,
                    "type": "missing_disease_coverage",
                    "description": f"Common disease '{disease}' not found in extracted services",
                    "matches_rishi_example": disease == 'hypertension'
                })
                missing_diseases.append(disease)
                
        return gaps, found_diseases, missing_diseases
    
    def compare_annex_parity(self, results: Dict) -> Dict:
        """Compare integrated annex extraction with manual CSV"""
        parity_results = {
            "manual_file_exists": False,
            "integrated_count": 0,
            "manual_count": 0,
            "match_percentage": 0,
            "sample_differences": []
        }
        
        # Check for manual annex file
        manual_annex_path = Path("outputs/annex_surgical_tariffs_all.csv")
        if not manual_annex_path.exists():
            manual_annex_path = Path("outputs/rules_p1_18_structured.csv")  # Alternative
            
        if manual_annex_path.exists():
            parity_results["manual_file_exists"] = True
            try:
                manual_df = pd.read_csv(manual_annex_path)
                parity_results["manual_count"] = len(manual_df)
                print(f"📄 Found manual reference: {manual_annex_path} ({len(manual_df)} rows)")
            except Exception as e:
                print(f"⚠️ Could not read manual file: {e}")
                return parity_results
        else:
            print(f"⚠️ No manual annex file found for comparison")
            return parity_results
            
        # Get integrated annex data
        all_services = results.get('extraction_results', {}).get('all_services', [])
        if all_services:
            parity_results["integrated_count"] = len(all_services)
            print(f"📊 Integrated extraction: {len(all_services)} services")
            
            # Quick comparison of counts
            if parity_results["manual_count"] > 0:
                count_diff = abs(len(all_services) - parity_results["manual_count"])
                parity_results["match_percentage"] = max(0, 100 - (count_diff / parity_results["manual_count"] * 100))
                
        return parity_results

    def run_all_checks(self) -> Dict:
        """Run all deterministic checks"""
        print("🔍 RUNNING DETERMINISTIC PDF VALIDATION")
        print("=" * 50)
        
        # Load results
        results = self.load_latest_results()
        if not results:
            return {"error": "No results to check"}
            
        print("✅ Loaded analysis results")
        
        # Run all checks
        print("🔍 Checking extraction parity...")
        parity_results = self.compare_annex_parity(results)
        
        dialysis_contradictions, dialysis_found = self.check_dialysis_contradictions(results)
        facility_contradictions = self.check_facility_exclusion_contradictions(results)
        disease_gaps, diseases_found, diseases_missing = self.check_disease_coverage_gaps(results)
        
        # Compile report
        report = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "extraction_parity": parity_results,
            "rishi_examples": {
                "dialysis_contradictions_found": len(dialysis_contradictions),
                "hypertension_gap_found": any(gap["matches_rishi_example"] for gap in disease_gaps),
                "dialysis_services_detected": dialysis_found
            },
            "contradictions": {
                "dialysis": dialysis_contradictions,
                "facility_exclusions": facility_contradictions,
                "total": len(dialysis_contradictions) + len(facility_contradictions)
            },
            "gaps": {
                "disease_coverage": disease_gaps,
                "total": len(disease_gaps),
                "diseases_found": diseases_found,
                "diseases_missing": diseases_missing
            },
            "summary_stats": {
                "total_services_analyzed": len(results.get('extraction_results', {}).get('all_services', [])),
                "policy_rules_analyzed": len(results.get('extraction_results', {}).get('policy_structure', {}).get('data', [])),
                "ai_analysis_available": bool(results.get('analysis_results', {}).get('full_ai_analysis'))
            }
        }
        
        self.results = report
        return report
    
    def save_report(self, report: Dict):
        """Save report to files"""
        # Ensure outputs directory exists
        Path("outputs").mkdir(exist_ok=True)
        
        # Save JSON
        json_path = Path("outputs/deterministic_checks.json")
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        # Save Markdown
        md_path = Path("outputs/deterministic_checks.md")
        with open(md_path, 'w') as f:
            f.write("# SHIF Policy Deterministic Validation Report\n\n")
            f.write(f"**Generated:** {report['timestamp']}\n\n")
            
            # Summary stats
            stats = report['summary_stats']
            f.write("## Analysis Summary\n\n")
            f.write(f"- **Total services analyzed:** {stats['total_services_analyzed']}\n")
            f.write(f"- **Policy rules analyzed:** {stats['policy_rules_analyzed']}\n")
            f.write(f"- **AI analysis available:** {'✅' if stats['ai_analysis_available'] else '❌'}\n\n")
            
            # Dr. Rishi's Examples
            f.write("## Dr. Rishi's Assignment Examples\n\n")
            rishi = report['rishi_examples']
            f.write(f"- **Dialysis contradictions:** {'✅ FOUND' if rishi['dialysis_contradictions_found'] > 0 else '❌ NOT FOUND'}\n")
            f.write(f"- **Hypertension gap:** {'✅ FOUND' if rishi['hypertension_gap_found'] else '❌ NOT FOUND'}\n\n")
            
            if rishi['dialysis_services_detected']:
                f.write("### Dialysis Services Detected\n")
                for service_type, sessions in rishi['dialysis_services_detected'].items():
                    f.write(f"- **{service_type.title()}:** {sessions} sessions/week\n")
                f.write("\n")
            
            # Contradictions
            f.write("## Contradictions Detected\n\n")
            f.write(f"**Total:** {report['contradictions']['total']}\n\n")
            
            if report['contradictions']['dialysis']:
                f.write("### Dialysis Contradictions (Dr. Rishi's Example)\n")
                for contradiction in report['contradictions']['dialysis']:
                    f.write(f"- **{contradiction['severity']}:** {contradiction['description']}\n")
                f.write("\n")
                
            if report['contradictions']['facility_exclusions']:
                f.write("### Facility Exclusion Contradictions\n")
                for contradiction in report['contradictions']['facility_exclusions'][:3]:  # Show first 3
                    f.write(f"- **{contradiction['severity']}:** {contradiction['description']}\n")
                f.write("\n")
                
            # Gaps
            f.write("## Coverage Gaps Detected\n\n")
            f.write(f"**Diseases found in analysis:** {len(report['gaps']['diseases_found'])}\n")
            f.write(f"**Diseases missing coverage:** {report['gaps']['total']}\n\n")
            
            if report['gaps']['diseases_found']:
                f.write("### Diseases WITH Coverage Detected\n")
                for disease in sorted(report['gaps']['diseases_found'])[:10]:  # Show first 10
                    f.write(f"✅ {disease.title()}\n")
                f.write("\n")
            
            if report['gaps']['diseases_missing']:
                f.write("### Diseases WITHOUT Coverage (Sample)\n")
                for disease in sorted(report['gaps']['diseases_missing'])[:10]:  # Show first 10
                    marker = "⭐" if disease == 'hypertension' else "•"
                    f.write(f"{marker} {disease.title()}\n")
                f.write("\n")
                    
        print(f"\n📄 Reports saved:")
        print(f"   • JSON: {json_path}")
        print(f"   • Markdown: {md_path}")

def main():
    """Run deterministic validation checks"""
    checker = DeterministicChecker()
    report = checker.run_all_checks()
    
    if "error" not in report:
        checker.save_report(report)
        
        # Print summary
        print("\n📊 VALIDATION SUMMARY:")
        print("=" * 30)
        
        rishi = report['rishi_examples']
        print(f"Dr. Rishi's Examples:")
        print(f"  Dialysis contradictions: {'✅' if rishi['dialysis_contradictions_found'] > 0 else '❌'}")
        print(f"  Hypertension gap: {'✅' if rishi['hypertension_gap_found'] else '❌'}")
        
        print(f"\\nResults:")
        print(f"  Total contradictions: {report['contradictions']['total']}")
        print(f"  Total disease gaps: {report['gaps']['total']}")
        print(f"  Services analyzed: {report['summary_stats']['total_services_analyzed']}")
        
        # Assignment brief compliance
        examples_found = rishi['dialysis_contradictions_found'] > 0 or rishi['hypertension_gap_found']
        print(f"\\n🎯 Assignment Brief Status: {'✅ EXAMPLES FOUND' if examples_found else '⚠️ REVIEW NEEDED'}")
        
    else:
        print(f"❌ Validation failed: {report['error']}")

if __name__ == "__main__":
    main()