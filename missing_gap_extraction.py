    def _extract_ai_gaps(self, analysis_text: str) -> List[Dict]:
        """Extract gaps from AI analysis - Enhanced to handle both JSON and conversational formats"""
        gaps = []
        
        try:
            # Try to parse as JSON first
            import json
            if analysis_text.strip().startswith('[') or analysis_text.strip().startswith('{'):
                parsed = json.loads(analysis_text.strip())
                if isinstance(parsed, list):
                    gaps = parsed
                elif isinstance(parsed, dict) and 'gaps' in parsed:
                    gaps = parsed['gaps']
                    
            else:
                # Look for JSON arrays/objects embedded in text
                json_pattern = r'\[[\s\S]*?\]|\{[\s\S]*?\}'
                json_matches = re.findall(json_pattern, analysis_text)
                for match in json_matches:
                    try:
                        parsed = json.loads(match)
                        if isinstance(parsed, list) and parsed:
                            gaps.extend(parsed)
                        elif isinstance(parsed, dict) and (
                            'gap_type' in parsed or 
                            'gap_id' in parsed or
                            'gap_category' in parsed or
                            'missing' in parsed.get('description', '').lower()
                        ):
                            gaps.append(parsed)
                    except:
                        continue
                        
            # If JSON parsing found gaps, return them
            if gaps:
                print(f"   📋 Extracted {len(gaps)} AI gaps from JSON")
                
                # Track unique gaps using the tracker
                new_gaps_count = self.unique_tracker.add_gaps(gaps)
                print(f"   🔍 Added {new_gaps_count} new unique gaps to tracker (Total: {len(self.unique_tracker.unique_gaps)})")
                # Save the updated tracker
                self.unique_tracker.save_insights()
                
                return gaps

        except Exception as e:
            print(f"   ⚠️ JSON parsing failed, using text fallback: {e}")
        
        # Enhanced conversational text parsing for structured gap analysis
        print(f"   🔍 Parsing conversational gap analysis...")
        
        # Look for numbered priority gaps (like "1) Cardiovascular disease...")  
        numbered_pattern = r'(\d+\.?\s*)(.*?)(?=\n\d+\.?\s*|\nGAP\s*\d+|$)'
        numbered_matches = re.findall(numbered_pattern, analysis_text, re.DOTALL | re.MULTILINE)
        
        for num, content in numbered_matches:
            content = content.strip()
            if len(content) > 20:  # Filter out short/empty matches
                # Extract gap type from content
                gap_type = "service_gap"
                if any(keyword in content.lower() for keyword in ["cardiovascular", "cardiac", "heart"]):
                    gap_type = "cardiovascular_gap"
                elif any(keyword in content.lower() for keyword in ["mental", "psychiatric", "psychology"]):
                    gap_type = "mental_health_gap"
                elif any(keyword in content.lower() for keyword in ["emergency", "trauma", "critical"]):
                    gap_type = "emergency_care_gap"
                elif any(keyword in content.lower() for keyword in ["preventive", "screening", "early detection"]):
                    gap_type = "preventive_care_gap"
                    
                gaps.append({
                    'gap_id': f"CONVERSATIONAL_GAP_{len(gaps) + 1:03d}",
                    'gap_type': gap_type,
                    'description': content[:500],  # Limit length
                    'priority': 'high' if any(keyword in content.lower() for keyword in ["critical", "urgent", "essential"]) else 'medium',
                    'detection_method': 'ai_conversational_parsing'
                })
        
        # Look for bullet points with medical terminology
        bullet_pattern = r'[•\-\*]\s*([^\n•\-\*]+)'
        bullet_matches = re.findall(bullet_pattern, analysis_text)
        
        for bullet_content in bullet_matches:
            content = bullet_content.strip()
            if len(content) > 30 and any(keyword in content.lower() for keyword in [
                "missing", "lacking", "absent", "gap", "need", "should include", "not covered", "insufficient"
            ]):
                gaps.append({
                    'gap_id': f"BULLET_GAP_{len(gaps) + 1:03d}",
                    'gap_type': 'identified_service_gap',
                    'description': content[:400],
                    'priority': 'medium',
                    'detection_method': 'ai_bullet_parsing'
                })
        
        # Look for section headers indicating gaps
        section_pattern = r'(?:GAPS?|MISSING|ABSENT|LACKING|INSUFFICIENT).*?:(.*?)(?=\n[A-Z]{3,}|\n\n|$)'
        section_matches = re.findall(section_pattern, analysis_text, re.DOTALL | re.IGNORECASE)
        
        for section_content in section_matches:
            content = section_content.strip()
            if len(content) > 50:
                # Split into individual gap items
                gap_items = re.split(r'\n(?=\d+\.|\-|\*|•)', content)
                for item in gap_items:
                    item = item.strip()
                    if len(item) > 20:
                        gaps.append({
                            'gap_id': f"SECTION_GAP_{len(gaps) + 1:03d}",
                            'gap_type': 'policy_gap',
                            'description': item[:400],
                            'priority': 'medium',
                            'detection_method': 'ai_section_parsing'
                        })
        
        # Track unique gaps using the tracker
        if gaps:
            new_gaps_count = self.unique_tracker.add_gaps(gaps)
            print(f"   🔍 Added {new_gaps_count} new unique gaps to tracker (Total: {len(self.unique_tracker.unique_gaps)})")
            # Save the updated tracker
            self.unique_tracker.save_insights()
        
        return gaps

# Main execution function for the integrated analyzer
if __name__ == "__main__":
    import sys
    import os
    
    # Check for PDF argument
    if len(sys.argv) < 2:
        pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
        if not os.path.exists(pdf_path):
            print("❌ Default PDF not found. Usage: python integrated_comprehensive_analyzer.py <path_to_pdf>")
            sys.exit(1)
    else:
        pdf_path = sys.argv[1]
    
    # Initialize analyzer
    print("🚀 INTEGRATED COMPREHENSIVE MEDICAL ANALYZER")
    print("=" * 60)
    
    # Create analyzer instance
    analyzer = IntegratedComprehensiveMedicalAnalyzer()
    
    # Run complete analysis
    try:
        results = analyzer.analyze_complete_document(pdf_path, run_extended_ai=False)
        
        print(f"\n✅ ANALYSIS SUCCESSFULLY COMPLETED")
        print(f"   📊 Policy Services: {results.get('total_policy_services', 0)}")
        print(f"   📊 Annex Procedures: {results.get('total_annex_procedures', 0)}")
        print(f"   🤖 AI Contradictions: {results.get('total_ai_contradictions', 0)}")
        print(f"   🤖 AI Gaps: {results.get('total_ai_gaps', 0)}")
        print(f"   ⏱️ Time: {results.get('analysis_metadata', {}).get('analysis_time_seconds', 0):.1f}s")
        print(f"\n💾 Results saved to outputs/ folder for direct access")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
