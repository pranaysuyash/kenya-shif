#!/usr/bin/env python3
"""
Quick test of the enhanced AI-first analyzer to verify integration
"""

import sys
import os
sys.path.append('/Users/pranay/Projects/adhoc_projects/drrishi/final_submission')

from ai_first_enhanced import EnhancedAIFirstAnalyzer

def test_enhanced_analyzer():
    """Test the enhanced analyzer with basic functionality"""
    print("🧪 Testing Enhanced AI-First Analyzer Integration")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = EnhancedAIFirstAnalyzer()
    
    # Test sample text with dialysis contradiction
    sample_text = """
    RENAL CARE PACKAGE
    
    Haemodialysis
    - Maximum of 3 sessions per week for adequate clearance
    - Tariff: KES 10,650 per session
    
    Hemodiafiltration
    - Maximum of 2 sessions per week with enhanced clearance
    - Tariff: KES 12,000 per session
    """
    
    print("📋 Running enhanced analysis on sample data...")
    
    try:
        # Run the enhanced analysis
        results = analyzer.analyze_full_document_enhanced(sample_text, "Test_Policy")
        
        print(f"\n✅ Analysis completed successfully!")
        print(f"Services extracted: {len(results.get('services', []))}")
        print(f"Contradictions found: {len(results.get('contradictions', []))}")
        print(f"Gaps identified: {len(results.get('gaps', []))}")
        
        # Check for dialysis contradiction specifically
        contradictions = results.get('contradictions', [])
        dialysis_found = any('dialysis' in str(c).lower() for c in contradictions)
        
        print(f"\n🎯 CRITICAL TEST: Dialysis contradiction detection")
        print(f"Status: {'✅ DETECTED' if dialysis_found else '❌ MISSED'}")
        
        if dialysis_found:
            print("🏆 Enhanced AI-First approach working correctly!")
        else:
            print("⚠️ May need further investigation")
            
        # Check prompts integration
        print(f"\n🧠 Enhanced Prompts Integration Check:")
        print(f"Medical expertise prompts: {'✅ INTEGRATED' if hasattr(analyzer, '_get_enhanced_medical_extraction_prompt') else '❌ MISSING'}")
        print(f"Contradiction prompts: {'✅ INTEGRATED' if hasattr(analyzer, '_get_enhanced_contradiction_prompt') else '❌ MISSING'}")
        print(f"Kenya gap prompts: {'✅ INTEGRATED' if hasattr(analyzer, '_get_enhanced_kenya_gap_prompt') else '❌ MISSING'}")
        
        return results
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_enhanced_analyzer()
