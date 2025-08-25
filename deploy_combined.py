#!/usr/bin/env python3
"""
DEPLOYMENT SCRIPT: Combined AI-Enhanced SHIF Analyzer
Run this to get the best of both worlds: 669+ services + AI enhancement
"""

import sys
import os
import subprocess

def main():
    """Main deployment function"""
    print("🚀 COMBINED AI-ENHANCED SHIF ANALYZER DEPLOYMENT")
    print("Best of both worlds: Comprehensive + AI Enhancement")
    print("=" * 60)
    
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
    else:
        print("⚠️ No OpenAI API key found")
        print("   Pattern matching will work, but AI enhancement will be skipped")
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
        from combined_analyzer import CombinedAIEnhancedAnalyzer
        
        print("\n🚀 Starting Combined Analysis...")
        print("=" * 50)
        
        # Initialize and run
        analyzer = CombinedAIEnhancedAnalyzer()
        results = analyzer.analyze_complete_document(pdf_path)
        output_path = analyzer.save_combined_results()
        
        # Success summary
        print(f"\n🎉 DEPLOYMENT SUCCESSFUL!")
        print(f"📊 Services: {results['summary']['total_services']}")
        print(f"💰 Tariffs: {results['summary']['total_tariffs']}")  
        print(f"🔍 Contradictions: {results['summary']['total_contradictions']}")
        print(f"🤖 AI Enhanced: {results['summary']['ai_contradictions_found']}")
        print(f"📁 Results: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
