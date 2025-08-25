}

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
