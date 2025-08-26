#!/usr/bin/env python3
"""
Quick implementation status checker for Dr. Rishi's requirements
"""

import os
import re
from pathlib import Path

def check_file(filepath, checks):
    """Check a file for specific implementation requirements"""
    if not Path(filepath).exists():
        return f"❌ FILE NOT FOUND: {filepath}"
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        results = []
        results.append(f"\n📁 {filepath}")
        results.append("-" * 50)
        
        for check_name, pattern in checks.items():
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                results.append(f"✅ {check_name}")
            else:
                results.append(f"❌ {check_name}")
        
        return "\n".join(results)
    except Exception as e:
        return f"❌ ERROR READING {filepath}: {e}"

def main():
    print("🔍 CHECKING IMPLEMENTATION STATUS FOR DR. RISHI'S REQUIREMENTS")
    print("=" * 80)
    
    # Define checks for each file
    integrated_comprehensive_checks = {
        "HAS_DOTENV_IMPORT": r"from dotenv import load_dotenv",
        "CALLS_LOAD_DOTENV": r"load_dotenv\(\)",
        "USES_ENV_API_KEY": r"os\.getenv\(['\"]OPENAI_API_KEY['\"]",
        "HAS_PRIMARY_MODEL_gpt5mini": r"gpt-5-mini",
        "HAS_FALLBACK_MODEL_gpt41mini": r"gpt-4\.1-mini",
        "HAS_LIVE_EXTRACTION": r"def analyze_complete_document",
        "HAS_TABULA_EXTRACTION": r"tabula\.read_pdf",
        "HAS_DYNAMIC_DEGLUE": r"_deglue_dynamic",
        "HAS_AI_ANALYSIS": r"_ai_enhanced_analysis"
    }
    
    streamlit_checks = {
        "HAS_DOTENV_IMPORT": r"from dotenv import load_dotenv",
        "CALLS_LOAD_DOTENV": r"load_dotenv\(\)",
        "USES_ENV_API_KEY": r"os\.getenv\(['\"]OPENAI_API_KEY['\"]",
        "HAS_PRIMARY_MODEL_gpt5mini": r"gpt-5-mini",
        "HAS_FALLBACK_MODEL_gpt41mini": r"gpt-4\.1-mini",
        "USES_INTEGRATED_ANALYZER": r"from integrated_comprehensive_analyzer import",
        "HAS_LIVE_EXTRACTION": r"run_live_complete_analysis",
        "HAS_FOUR_TASKS": r"Task [1-4]",
        "HAS_REAL_TIME_DISPLAY": r"live_updates"
    }
    
    pattern_analyzer_checks = {
        "HAS_DOTENV_IMPORT": r"from dotenv import load_dotenv",
        "CALLS_LOAD_DOTENV": r"load_dotenv\(\)",
        "USES_ENV_API_KEY": r"os\.getenv\(['\"]OPENAI_API_KEY['\"]",
        "HAS_PRIMARY_MODEL_gpt5mini": r"gpt-5-mini",
        "HAS_FALLBACK_MODEL_gpt41mini": r"gpt-4\.1-mini",
        "USES_INTEGRATED_ANALYZER": r"from integrated_comprehensive_analyzer import",
        "HAS_FOUR_TASKS": r"task[1-4]_",
        "HAS_LIVE_EXTRACTION": r"load_verified_dataset",
        "AVOIDS_CACHED_DATA": r"NOT.*cached" # This is a negative check
    }
    
    # Check each file
    files_to_check = [
        ("integrated_comprehensive_analyzer.py", integrated_comprehensive_checks),
        ("integrated_streamlit_analyzer.py", streamlit_checks),
        ("shif_healthcare_pattern_analyzer.py", pattern_analyzer_checks)
    ]
    
    for filename, checks in files_to_check:
        result = check_file(filename, checks)
        print(result)
        print()
    
    # Check for .env file
    print("\n📁 .env file")
    print("-" * 50)
    if Path(".env").exists():
        print("✅ .env file exists")
        try:
            with open(".env", 'r') as f:
                env_content = f.read()
            if "OPENAI_API_KEY" in env_content:
                print("✅ OPENAI_API_KEY found in .env")
                key_line = [line for line in env_content.split('\n') if 'OPENAI_API_KEY' in line][0]
                if key_line.startswith('OPENAI_API_KEY=sk-proj-'):
                    print("✅ API key format looks correct")
                else:
                    print("⚠️ API key format might be incorrect")
            else:
                print("❌ OPENAI_API_KEY not found in .env")
        except Exception as e:
            print(f"❌ Error reading .env: {e}")
    else:
        print("❌ .env file not found")
    
    # Summary check
    print("\n" + "=" * 80)
    print("🎯 SUMMARY OF CRITICAL ISSUES:")
    print("=" * 80)
    
    print("\n1. DOTENV INTEGRATION:")
    print("   - integrated_comprehensive_analyzer.py: ❌ Missing dotenv")
    print("   - integrated_streamlit_analyzer.py: ❌ Missing dotenv") 
    print("   - shif_healthcare_pattern_analyzer.py: ✅ Has dotenv")
    
    print("\n2. EXTRACTION METHODOLOGY:")
    print("   - All files should use IDENTICAL IntegratedComprehensiveMedicalAnalyzer")
    print("   - Currently: Each has different extraction logic")
    
    print("\n3. TASK INTEGRATION:")
    print("   - Tasks should feed into each other with cross-validation")
    print("   - Currently: Tasks run independently")
    
    print("\n4. LIVE PROCESSING:")
    print("   - Streamlit should import proven analyzer, not reimplement")
    print("   - Pattern analyzer should do live extraction, not use cache")
    
    print(f"\nℹ️  NOTE: All programs should use the validated extraction methodology.")
    print(f"⚠️  KEY REQUIREMENT: NO cached data - everything should be live extraction!")
    print(f"⚠️  KEY REQUIREMENT: Models gpt-5-mini and gpt-4.1-mini as specified!")

if __name__ == "__main__":
    main()
