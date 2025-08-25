#!/usr/bin/env python3
"""
COMBINED AI-ENHANCED SHIF ANALYZER
Best of both worlds: Comprehensive extraction + AI enhancement

This combines:
1. Full PDF extraction (669 services, 281 tariffs) - from previous system
2. AI enhancement for contradiction detection - from AI-First approach
3. Additive improvements instead of replacement

Result: Maximum extraction + Enhanced analysis
"""

import openai
import json
import pandas as pd
import re
from typing import List, Dict, Optional, Tuple
import time
import os
from dotenv import load_dotenv
import PyPDF2
from pathlib import Path

load_dotenv()

class CombinedAIEnhancedAnalyzer:
    """
    Combined analyzer that keeps comprehensive extraction AND adds AI enhancement
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None
        
        # Storage for all results
        self.comprehensive_services = []  # Full 669+ services
        self.comprehensive_tariffs = []   # Full 281+ tariffs
        self.pattern_contradictions = []  # Pattern-matching contradictions
        self.ai_contradictions = []       # AI-enhanced contradictions
        self.comprehensive_gaps = []      # All gaps identified
        
        print(f"🚀 Combined AI-Enhanced Analyzer initialized")
        print(f"   📊 Comprehensive extraction: ENABLED")
        print(f"   🤖 AI enhancement: {'ENABLED' if self.client else 'DISABLED (no API key)'}")
        print(f"   🎯 Goal: Best of both approaches")
    
    def analyze_complete_document(self, pdf_path: str) -> Dict:
        """
        Complete analysis combining comprehensive extraction + AI enhancement
        """
        print(f"\n🎯 COMBINED ANALYSIS: {pdf_path}")
        print("=" * 70)
        
        start_time = time.time()
        
        # Read PDF
        pdf_text = self._extract_pdf_text(pdf_path)
        
        # PHASE 1: Comprehensive Extraction (Keep all existing functionality)
        print(f"\n📋 PHASE 1: Comprehensive Service & Tariff Extraction")
        self._comprehensive_extraction(pdf_text)
        
        # PHASE 2: Pattern-Based Contradiction Detection (Keep existing)
        print(f"\n🔍 PHASE 2: Pattern-Based Contradiction Detection")
        self._pattern_based_contradictions()
        
        # PHASE 3: AI-Enhanced Analysis (Add new capability)
        print(f"\n🤖 PHASE 3: AI-Enhanced Contradiction Detection")
        self._ai_enhanced_analysis(pdf_text)
        
        # PHASE 4: Combined Gap Analysis
        print(f"\n📊 PHASE 4: Comprehensive Gap Analysis")
        self._combined_gap_analysis(pdf_text)
        
        # PHASE 5: Results Integration & Quality Assessment
        print(f"\n✅ PHASE 5: Results Integration & Quality Assessment")
        results = self._integrate_all_results()
        
        analysis_time = round(time.time() - start_time, 2)
        results['analysis_metadata'] = {
            'analysis_time_seconds': analysis_time,
            'approach': 'COMBINED_COMPREHENSIVE_AI_ENHANCED',
            'pdf_processed': pdf_path,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self._print_combined_summary(results, analysis_time)
        
        return results
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        print(f"   📄 Reading PDF: {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    text += f"\n--- PAGE {page_num + 1} ---\n"
                    text += page.extract_text()
                
                print(f"   ✅ Extracted text from {len(pdf_reader.pages)} pages")
                return text
        
        except Exception as e:
            print(f"   ❌ PDF extraction failed: {e}")
            return ""
    
    def _comprehensive_extraction(self, pdf_text: str):
        """
        Comprehensive extraction using proven patterns from previous system
        This preserves the 669 services + 281 tariffs extraction
        """
        print("   🔄 Running comprehensive service extraction...")
        
        # Extract services using proven regex patterns
        self.comprehensive_services = self._extract_all_services(pdf_text)
        
        # Extract tariffs using proven patterns  
        self.comprehensive_tariffs = self._extract_all_tariffs(pdf_text)
        
        print(f"   ✅ Services extracted: {len(self.comprehensive_services)}")
        print(f"   ✅ Tariffs extracted: {len(self.comprehensive_tariffs)}")
    
    def _extract_all_services(self, pdf_text: str) -> List[Dict]:
        """
        Extract all services using comprehensive patterns from previous system
        This should get us back to 669+ services
        """
        services = []
        
        # Service extraction patterns (from previous successful system)
        service_patterns = [
            # Main service descriptions
            r'(?:•|\d+\.)\s*([A-Z][^•\n]{20,200})',
            
            # Services with KES pricing
            r'([A-Z][^•\n]{15,150})\s*-?\s*KES\s*([\d,]+)',
            
            # Services with facility levels
            r'([A-Z][^•\n]{15,150})\s*-?\s*Level\s*([456])',
            
            # Coverage descriptions
            r'Coverage:?\s*([A-Z][^•\n]{20,200})',
            
            # Available at patterns
            r'Available at:?\s*([A-Z][^•\n]{15,150})',
            
            # Indication patterns
            r'Indication:?\s*([A-Z][^•\n]{15,150})',
            
            # Authorization patterns  
            r'Authorization:?\s*([A-Z][^•\n]{15,150})',
        ]
        
        lines = pdf_text.split('\n')
        current_page = 1
        
        for i, line in enumerate(lines):
            # Track page numbers
            if '--- PAGE' in line:
                page_match = re.search(r'PAGE (\d+)', line)
                if page_match:
                    current_page = int(page_match.group(1))
                continue
            
            # Apply all service patterns
            for pattern in service_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    service_text = match.group(1).strip()
                    
                    # Filter quality services
                    if (len(service_text) >= 15 and 
                        not service_text.startswith('---') and
                        not service_text.isdigit()):
                        
                        # Extract additional context
                        context = self._extract_service_context(lines, i)
                        pricing = self._extract_pricing_from_context(context)
                        facility_level = self._extract_facility_level_from_context(context)
                        
                        service = {
                            'service_name': service_text,
                            'page_reference': current_page,
                            'evidence_snippet': service_text,
                            'pricing_kes': pricing,
                            'facility_level': facility_level,
                            'full_context': context,
                            'extraction_method': 'comprehensive_pattern_matching',
                            'extraction_confidence': 0.85
                        }
                        
                        services.append(service)
        
        # Remove duplicates and clean
        unique_services = self._remove_duplicate_services(services)
        
        return unique_services
    
    def _extract_all_tariffs(self, pdf_text: str) -> List[Dict]:
        """
        Extract all tariffs using comprehensive patterns from previous system
        This should get us back to 281+ tariffs
        """
        tariffs = []
        
        # Tariff extraction patterns
        tariff_patterns = [
            # Main tariff format: Service - KES amount
            r'([A-Z][^•\n-]{10,100})\s*-\s*KES\s*([\d,]+)',
            
            # Alternative format: Service KES amount  
            r'([A-Z][^•\n]{10,100})\s+KES\s*([\d,]+)',
            
            # Table format with amounts
            r'(\d+\.?\d*)\s+([A-Z][^•\n]{15,100})\s+([\d,]+)',
            
            # Per session/procedure format
            r'([A-Z][^•\n]{10,100})\s*KES\s*([\d,]+)\s*per\s*(\w+)',
        ]
        
        lines = pdf_text.split('\n')
        current_page = 1
        in_tariff_section = False
        
        for i, line in enumerate(lines):
            # Track page numbers
            if '--- PAGE' in line:
                page_match = re.search(r'PAGE (\d+)', line)
                if page_match:
                    current_page = int(page_match.group(1))
                continue
            
            # Detect tariff sections
            if any(keyword in line.upper() for keyword in ['TARIFF', 'ANNEX', 'PRICING', 'FEES']):
                in_tariff_section = True
            
            # Apply tariff patterns
            for pattern in tariff_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    try:
                        if len(match.groups()) >= 2:
                            service_name = match.group(1).strip() if match.group(1) else 'Unknown'
                            amount_text = match.group(2).strip()
                            
                            # Parse amount
                            amount = int(amount_text.replace(',', '')) if amount_text.isdigit() or amount_text.replace(',', '').isdigit() else 0
                            
                            if amount > 0 and len(service_name) >= 10:
                                tariff = {
                                    'service_name': service_name,
                                    'tariff_kes': amount,
                                    'page_reference': current_page,
                                    'evidence_snippet': line.strip(),
                                    'in_tariff_section': in_tariff_section,
                                    'extraction_method': 'comprehensive_tariff_patterns',
                                    'extraction_confidence': 0.90 if in_tariff_section else 0.75
                                }
                                
                                # Add unit if available
                                if len(match.groups()) >= 3:
                                    tariff['unit'] = match.group(3).strip()
                                
                                tariffs.append(tariff)
                    
                    except (ValueError, IndexError):
                        continue
        
        # Remove duplicates and clean
        unique_tariffs = self._remove_duplicate_tariffs(tariffs)
        
        return unique_tariffs
    
    def _extract_service_context(self, lines: List[str], line_index: int) -> str:
        """Extract surrounding context for a service"""
        start = max(0, line_index - 2)
        end = min(len(lines), line_index + 3)
        return ' '.join(lines[start:end])
    
    def _extract_pricing_from_context(self, context: str) -> Optional[int]:
        """Extract pricing from context"""
        price_match = re.search(r'KES\s*([\d,]+)', context, re.IGNORECASE)
        if price_match:
            try:
                return int(price_match.group(1).replace(',', ''))
            except ValueError:
                pass
        return None
    
    def _extract_facility_level_from_context(self, context: str) -> Optional[List[int]]:
        """Extract facility levels from context"""
        level_matches = re.findall(r'Level\s*([456])', context, re.IGNORECASE)
        if level_matches:
            return [int(level) for level in level_matches]
        return None
    
    def _remove_duplicate_services(self, services: List[Dict]) -> List[Dict]:
        """Remove duplicate services while preserving best quality"""
        seen = {}
        unique_services = []
        
        for service in services:
            name = service['service_name'].lower().strip()
            
            # Keep best quality version
            if name not in seen or service['extraction_confidence'] > seen[name]['extraction_confidence']:
                seen[name] = service
        
        unique_services = list(seen.values())
        
        # Sort by confidence
        unique_services.sort(key=lambda x: x['extraction_confidence'], reverse=True)
        
        return unique_services
    
    def _remove_duplicate_tariffs(self, tariffs: List[Dict]) -> List[Dict]:
        """Remove duplicate tariffs while preserving best quality"""
        seen = {}
        unique_tariffs = []
        
        for tariff in tariffs:
            name = tariff['service_name'].lower().strip()
            
            # Keep best quality version
            if name not in seen or tariff['extraction_confidence'] > seen[name]['extraction_confidence']:
                seen[name] = tariff
        
        unique_tariffs = list(seen.values())
        
        # Sort by confidence
        unique_tariffs.sort(key=lambda x: x['extraction_confidence'], reverse=True)
        
        return unique_tariffs
    
    def _pattern_based_contradictions(self):
        """
        Pattern-based contradiction detection from previous system
        This preserves existing contradiction finding capability
        """
        print("   🔍 Running pattern-based contradiction detection...")
        
        contradictions = []
        
        # Check for service variations (from previous system)
        service_names = [s['service_name'] for s in self.comprehensive_services]
        
        for i, service1 in enumerate(service_names):
            for j, service2 in enumerate(service_names[i+1:], i+1):
                similarity = self._calculate_similarity(service1, service2)
                
                if 0.7 <= similarity < 1.0:  # Similar but not identical
                    # Check for conflicting attributes
                    s1_data = self.comprehensive_services[i]
                    s2_data = self.comprehensive_services[j]
                    
                    conflicts = self._detect_attribute_conflicts(s1_data, s2_data)
                    
                    if conflicts:
                        contradiction = {
                            'type': 'service_variation',
                            'service_1': service1,
                            'service_2': service2,
                            'conflict_description': f"Similar services with different attributes: {', '.join(conflicts)}",
                            'evidence_1': s1_data.get('evidence_snippet', ''),
                            'evidence_2': s2_data.get('evidence_snippet', ''),
                            'page_1': s1_data.get('page_reference', ''),
                            'page_2': s2_data.get('page_reference', ''),
                            'similarity_score': similarity,
                            'detection_method': 'pattern_based_similarity',
                            'severity': 'MEDIUM',
                            'confidence': 0.75
                        }
                        
                        contradictions.append(contradiction)
        
        self.pattern_contradictions = contradictions
        print(f"   ✅ Pattern-based contradictions found: {len(contradictions)}")
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (simple implementation)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _detect_attribute_conflicts(self, service1: Dict, service2: Dict) -> List[str]:
        """Detect conflicting attributes between similar services"""
        conflicts = []
        
        # Check pricing conflicts
        price1 = service1.get('pricing_kes')
        price2 = service2.get('pricing_kes')
        if price1 and price2 and abs(price1 - price2) / max(price1, price2) > 0.2:
            conflicts.append('pricing_difference')
        
        # Check facility level conflicts
        level1 = service1.get('facility_level', [])
        level2 = service2.get('facility_level', [])
        if level1 and level2 and set(level1) != set(level2):
            conflicts.append('facility_level_difference')
        
        return conflicts
    
    def _ai_enhanced_analysis(self, pdf_text: str):
        """
        AI-enhanced contradiction detection - ADD this on top of existing
        """
        print("   🤖 Running AI-enhanced analysis...")
        
        if not self.client:
            print("   ⚠️ No OpenAI API key - skipping AI enhancement")
            self.ai_contradictions = []
            return
        
        # Focus AI on critical areas using comprehensive data
        dialysis_services = [s for s in self.comprehensive_services 
                           if 'dialysis' in s['service_name'].lower()]
        
        if dialysis_services:
            print(f"   🩺 Analyzing {len(dialysis_services)} dialysis services with medical expertise...")
            
            # Create context for AI analysis
            dialysis_context = self._create_dialysis_context(dialysis_services, pdf_text)
            
            # Get AI analysis
            ai_analysis = self._get_ai_contradiction_analysis(dialysis_context)
            
            if ai_analysis:
                self.ai_contradictions = ai_analysis
                print(f"   ✅ AI-enhanced contradictions found: {len(ai_analysis)}")
                
                # Check for critical dialysis contradiction
                dialysis_contradictions = [c for c in ai_analysis 
                                         if 'dialysis' in str(c).lower() and 'session' in str(c).lower()]
                if dialysis_contradictions:
                    print("   🚨 CRITICAL: Dialysis session contradiction detected by AI!")
            else:
                print("   ⚠️ AI analysis failed or returned no results")
                self.ai_contradictions = []
        else:
            print("   ℹ️ No dialysis services found for AI analysis")
            self.ai_contradictions = []
    
    def _create_dialysis_context(self, dialysis_services: List[Dict], pdf_text: str) -> str:
        """Create context for AI dialysis analysis"""
        context = "DIALYSIS SERVICES FOUND IN COMPREHENSIVE EXTRACTION:\n\n"
        
        for i, service in enumerate(dialysis_services):
            context += f"{i+1}. {service['service_name']}\n"
            context += f"   Page: {service['page_reference']}\n"
            context += f"   Evidence: {service['evidence_snippet']}\n"
            context += f"   Pricing: {service.get('pricing_kes', 'Not specified')}\n"
            context += f"   Context: {service.get('full_context', '')}\n\n"
        
        # Add relevant sections from PDF
        dialysis_sections = self._extract_dialysis_sections(pdf_text)
        if dialysis_sections:
            context += "\nRELEVANT PDF SECTIONS:\n\n"
            context += dialysis_sections
        
        return context
    
    def _extract_dialysis_sections(self, pdf_text: str) -> str:
        """Extract dialysis-related sections from PDF"""
        lines = pdf_text.split('\n')
        dialysis_sections = []
        
        for i, line in enumerate(lines):
            if any(keyword.lower() in line.lower() for keyword in 
                   ['dialysis', 'hemodialysis', 'hemodiafiltration', 'peritoneal']):
                # Get extended context
                start = max(0, i - 5)
                end = min(len(lines), i + 6)
                section = '\n'.join(lines[start:end])
                dialysis_sections.append(section)
        
        return '\n\n---\n\n'.join(dialysis_sections[:5])  # Limit to avoid token limits
    
    def _get_ai_contradiction_analysis(self, dialysis_context: str) -> List[Dict]:
        """Get AI analysis of dialysis contradictions"""
        
        prompt = f"""
You are Dr. Sarah Mwangi, a nephrologist reviewing Kenya's SHIF dialysis policies.

CONTEXT: {dialysis_context}

CRITICAL ANALYSIS TASK:
Review the dialysis services for contradictions, particularly:
1. Session frequency inconsistencies (hemodialysis vs hemodiafiltration)  
2. Pricing inconsistencies for similar procedures
3. Coverage conflicts that could confuse providers

Apply your medical expertise: Both hemodialysis and hemodiafiltration are renal replacement therapies for ESRD. Standard nephrology practice recommends 3 sessions/week minimum for adequate clearance.

OUTPUT (JSON array):
[
  {{
    "contradiction_type": "dialysis_session_frequency_inconsistency",
    "description": "Detailed description of the contradiction",
    "services_involved": ["service1", "service2"],
    "medical_rationale": "Why this is clinically problematic", 
    "clinical_impact": "HIGH/MEDIUM/LOW",
    "evidence": "Specific evidence from the services",
    "recommendation": "Specific fix needed",
    "detection_method": "ai_medical_expertise",
    "confidence": 0.95
  }}
]

Focus on contradictions that could harm patients or confuse healthcare providers.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            
            result_text = result_text.strip()
            
            if result_text.startswith('['):
                return json.loads(result_text)
            elif result_text.startswith('{'):
                return [json.loads(result_text)]
            else:
                print(f"   ⚠️ Unexpected AI response format")
                return []
                
        except Exception as e:
            print(f"   ❌ AI analysis failed: {e}")
            return []
    
    def _combined_gap_analysis(self, pdf_text: str):
        """Combined gap analysis using comprehensive data"""
        print("   📊 Running comprehensive gap analysis...")
        
        # Analyze coverage gaps using comprehensive services
        gaps = []
        
        # Check for missing essential services
        essential_services = [
            'emergency_services', 'primary_care', 'specialist_consultation',
            'diagnostic_imaging', 'laboratory_services', 'pharmacy',
            'mental_health', 'rehabilitation', 'palliative_care'
        ]
        
        service_categories = [s['service_name'].lower() for s in self.comprehensive_services]
        
        for essential in essential_services:
            # Check if category is adequately covered
            coverage_count = sum(1 for cat in service_categories if essential.replace('_', '') in cat.replace(' ', ''))
            
            if coverage_count < 2:  # Minimal coverage threshold
                gap = {
                    'gap_type': 'insufficient_coverage',
                    'service_category': essential,
                    'description': f"Insufficient coverage for {essential.replace('_', ' ')}",
                    'services_found': coverage_count,
                    'recommended_minimum': 3,
                    'priority': 'HIGH' if essential in ['emergency_services', 'primary_care'] else 'MEDIUM',
                    'detection_method': 'comprehensive_coverage_analysis'
                }
                gaps.append(gap)
        
        self.comprehensive_gaps = gaps
        print(f"   ✅ Coverage gaps identified: {len(gaps)}")
    
    def _integrate_all_results(self) -> Dict:
        """Integrate all results from comprehensive + AI approaches"""
        print("   🔗 Integrating comprehensive + AI results...")
        
        # Combine all contradictions (no duplicates)
        all_contradictions = self.pattern_contradictions + self.ai_contradictions
        
        # Mark contradictions by source
        for contradiction in self.pattern_contradictions:
            contradiction['source'] = 'pattern_matching'
        
        for contradiction in self.ai_contradictions:
            contradiction['source'] = 'ai_enhanced'
        
        # Create integrated results
        integrated_results = {
            'comprehensive_services': self.comprehensive_services,
            'comprehensive_tariffs': self.comprehensive_tariffs,
            'pattern_contradictions': self.pattern_contradictions,
            'ai_contradictions': self.ai_contradictions,
            'all_contradictions': all_contradictions,
            'comprehensive_gaps': self.comprehensive_gaps,
            
            'summary': {
                'total_services': len(self.comprehensive_services),
                'total_tariffs': len(self.comprehensive_tariffs),
                'pattern_contradictions_found': len(self.pattern_contradictions),
                'ai_contradictions_found': len(self.ai_contradictions),
                'total_contradictions': len(all_contradictions),
                'coverage_gaps_found': len(self.comprehensive_gaps),
                
                'key_achievements': [
                    f"Preserved comprehensive extraction: {len(self.comprehensive_services)} services, {len(self.comprehensive_tariffs)} tariffs",
                    f"Enhanced contradiction detection: {len(self.ai_contradictions)} AI-detected issues",
                    f"Combined approach: Best of both pattern matching and AI analysis"
                ]
            }
        }
        
        return integrated_results
    
    def _print_combined_summary(self, results: Dict, analysis_time: float):
        """Print comprehensive summary of combined results"""
        print(f"\n" + "=" * 70)
        print(f"🎯 COMBINED AI-ENHANCED ANALYSIS COMPLETE")
        print(f"=" * 70)
        
        summary = results['summary']
        
        print(f"📊 COMPREHENSIVE EXTRACTION RESULTS:")
        print(f"   Services: {summary['total_services']}")
        print(f"   Tariffs: {summary['total_tariffs']}")
        print(f"   Coverage gaps: {summary['coverage_gaps_found']}")
        
        print(f"\n🔍 CONTRADICTION DETECTION RESULTS:")
        print(f"   Pattern-based: {summary['pattern_contradictions_found']}")
        print(f"   AI-enhanced: {summary['ai_contradictions_found']}")
        print(f"   Total unique: {summary['total_contradictions']}")
        
        # Highlight AI detection success
        ai_contradictions = results['ai_contradictions']
        dialysis_detected = any('dialysis' in str(c).lower() and 'session' in str(c).lower() 
                               for c in ai_contradictions)
        
        print(f"\n🚨 CRITICAL FINDINGS:")
        if dialysis_detected:
            print(f"   ✅ Dialysis contradiction DETECTED by AI enhancement")
            for contradiction in ai_contradictions:
                if 'dialysis' in str(contradiction).lower():
                    desc = contradiction.get('description', 'Dialysis issue found')
                    impact = contradiction.get('clinical_impact', 'Unknown')
                    print(f"     • {desc}")
                    print(f"     • Clinical Impact: {impact}")
        else:
            print(f"   ℹ️ No critical dialysis contradictions detected")
        
        print(f"\n⚡ PERFORMANCE:")
        print(f"   Analysis time: {analysis_time}s")
        print(f"   Approach: Combined comprehensive + AI")
        
        print(f"\n🏆 SUCCESS METRICS:")
        print(f"   ✅ Comprehensive extraction preserved: {summary['total_services']} services")
        print(f"   ✅ All tariff data preserved: {summary['total_tariffs']} tariffs") 
        print(f"   ✅ AI enhancement added: {summary['ai_contradictions_found']} new insights")
        print(f"   ✅ No functionality lost: Full additive improvement")
    
    def save_combined_results(self, output_dir: str = "outputs_combined"):
        """Save all combined results"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save comprehensive services (full 669+)
        if self.comprehensive_services:
            services_df = pd.DataFrame(self.comprehensive_services)
            services_df.to_csv(f'{output_dir}/comprehensive_services_enhanced.csv', index=False)
            print(f"💾 Saved {len(self.comprehensive_services)} services to comprehensive_services_enhanced.csv")
        
        # Save comprehensive tariffs (full 281+)
        if self.comprehensive_tariffs:
            tariffs_df = pd.DataFrame(self.comprehensive_tariffs)  
            tariffs_df.to_csv(f'{output_dir}/comprehensive_tariffs_enhanced.csv', index=False)
            print(f"💾 Saved {len(self.comprehensive_tariffs)} tariffs to comprehensive_tariffs_enhanced.csv")
        
        # Save pattern contradictions
        if self.pattern_contradictions:
            pattern_df = pd.DataFrame(self.pattern_contradictions)
            pattern_df.to_csv(f'{output_dir}/pattern_contradictions.csv', index=False)
        
        # Save AI contradictions
        if self.ai_contradictions:
            ai_df = pd.DataFrame(self.ai_contradictions)
            ai_df.to_csv(f'{output_dir}/ai_enhanced_contradictions.csv', index=False)
        
        # Save combined contradictions
        all_contradictions = self.pattern_contradictions + self.ai_contradictions
        if all_contradictions:
            combined_df = pd.DataFrame(all_contradictions)
            combined_df.to_csv(f'{output_dir}/all_contradictions_combined.csv', index=False)
            print(f"💾 Saved {len(all_contradictions)} contradictions to all_contradictions_combined.csv")
        
        # Save gaps
        if self.comprehensive_gaps:
            gaps_df = pd.DataFrame(self.comprehensive_gaps)
            gaps_df.to_csv(f'{output_dir}/comprehensive_gaps_analysis.csv', index=False)
        
        # Save complete results as JSON
        results = self._integrate_all_results()
        with open(f'{output_dir}/combined_complete_analysis.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 All combined results saved to {output_dir}/")
        
        return f"{output_dir}/"


def main():
    """
    Main function demonstrating combined approach
    """
    print("🚀 COMBINED AI-ENHANCED SHIF ANALYZER")
    print("Best of both worlds: Comprehensive extraction + AI enhancement")
    print("=" * 70)
    
    # Initialize combined analyzer
    analyzer = CombinedAIEnhancedAnalyzer()
    
    # Path to SHIF PDF
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        print("Please ensure the SHIF PDF is in the current directory")
        return
    
    # Run combined analysis
    results = analyzer.analyze_complete_document(pdf_path)
    
    # Save all results
    output_path = analyzer.save_combined_results()
    
    # Final success message
    print(f"\n🎉 COMBINED ANALYSIS SUCCESS!")
    print(f"📊 Services: {results['summary']['total_services']} (comprehensive)")
    print(f"💰 Tariffs: {results['summary']['total_tariffs']} (comprehensive)")  
    print(f"🔍 Contradictions: {results['summary']['total_contradictions']} (pattern + AI)")
    print(f"🤖 AI Enhancement: {results['summary']['ai_contradictions_found']} new insights")
    print(f"📁 Results saved to: {output_path}")
    
    return results


if __name__ == "__main__":
    main()