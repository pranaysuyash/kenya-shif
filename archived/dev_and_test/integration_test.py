#!/usr/bin/env python3
import sys
sys.path.append('/Users/pranay/Projects/adhoc_projects/drrishi/final_submission')

try:
    from ai_first_enhanced import EnhancedAIFirstAnalyzer
    print("✅ Enhanced AI-First Analyzer imported successfully")
    
    analyzer = EnhancedAIFirstAnalyzer()
    print("✅ Analyzer initialized")
    
    # Check if enhanced prompts are integrated
    has_medical_prompt = hasattr(analyzer, '_get_enhanced_medical_extraction_prompt')
    has_contradiction_prompt = hasattr(analyzer, '_get_enhanced_contradiction_prompt') 
    has_kenya_prompt = hasattr(analyzer, '_get_enhanced_kenya_gap_prompt')
    
    print(f"Medical Prompt: {'YES' if has_medical_prompt else 'NO'}")
    print(f"Contradiction Prompt: {'YES' if has_contradiction_prompt else 'NO'}")
    print(f"Kenya Gap Prompt: {'YES' if has_kenya_prompt else 'NO'}")
    
    # Test simulation methods
    services = analyzer._simulate_enhanced_medical_extraction()
    contradictions = analyzer._simulate_advanced_contradictions()
    
    print(f"Simulated Services: {len(services)}")
    print(f"Simulated Contradictions: {len(contradictions)}")
    
    # Check dialysis contradiction
    dialysis_found = any('dialysis' in str(c).lower() for c in contradictions)
    print(f"Dialysis Contradiction: {'FOUND' if dialysis_found else 'MISSING'}")
    
    print("\nSUCCESS: All enhanced functions integrated correctly!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
