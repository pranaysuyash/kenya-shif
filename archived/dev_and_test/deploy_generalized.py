#!/usr/bin/env python3
"""
DEPLOYMENT SCRIPT: Generalized Medical AI Analyzer
Run this to get comprehensive extraction + generalized medical expertise across ALL specialties
"""

import sys
import os
import subprocess

def main():
    """Main deployment function"""
    print("🚀 GENERALIZED MEDICAL AI ANALYZER DEPLOYMENT")
    print("Comprehensive extraction + AI medical expertise across ALL specialties")
    print("=" * 70)
    
    # Check for PDF file
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        print("Please ensure the SHIF PDF is in the current directory")
        return False
    
    print(f"✅ PDF found: {pdf_path}")
    
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("✅ OpenAI API key found")
        print("   🩺 Generalized medical analysis across ALL specialties enabled")
    else:
        print("⚠️ No OpenAI API key found")
        print("   Pattern matching will work, but AI medical expertise will be skipped")
        print("   To enable AI: export OPENAI_API_KEY=your_key")
    
    # Install requirements if needed
    try:
        import openai, pandas, PyPDF2
        print("✅ All required packages available")
    except ImportError as e:
        print(f"📦 Installing missing packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'openai', 'pandas', 'PyPDF2', 'python-dotenv'])
        print("✅ Packages installed")
    
    # Import and run analyzer
    try:
        from generalized_medical_analyzer import GeneralizedMedicalAnalyzer
        
        print("\n🚀 Starting Generalized Medical Analysis...")
        print("=" * 50)
        
        # Initialize and run
        analyzer = GeneralizedMedicalAnalyzer()
        results = analyzer.analyze_complete_document(pdf_path)
        output_path = analyzer.save_combined_results()
        
        # Success summary
        summary = results['summary']
        
        print(f"\n🎉 DEPLOYMENT SUCCESSFUL!")
        print(f"📊 Services: {summary['total_services']} (comprehensive)")
        print(f"💰 Tariffs: {summary['total_tariffs']} (comprehensive)")  
        print(f"🔍 Total Contradictions: {summary['total_contradictions']}")
        print(f"   • Pattern-based: {summary['pattern_contradictions_found']}")
        print(f"   • AI medical analysis: {summary['ai_contradictions_found']}")
        
        specialties = summary.get('medical_specialties_analyzed', [])
        if specialties and specialties != ['general_medical_analysis']:
            print(f"🤖 Medical specialties analyzed: {', '.join(specialties)}")
        
        print(f"📁 Results saved to: {output_path}")
        
        print(f"\n🏆 KEY IMPROVEMENTS:")
        print(f"   ✅ Comprehensive extraction: {summary['total_services']} services, {summary['total_tariffs']} tariffs")
        print(f"   ✅ Generalized AI: Medical expertise across ALL specialties (not just dialysis)")
        print(f"   ✅ One-shot learning: Clinical reasoning with medical examples")
        print(f"   ✅ Best of both worlds: Pattern matching + broad medical AI")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
