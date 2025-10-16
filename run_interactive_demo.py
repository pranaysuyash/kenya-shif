#!/usr/bin/env python3
"""
Interactive Demo Runner - Quick demo validation and testing
"""

import subprocess
import sys
from pathlib import Path
import webbrowser
import time

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 TESTING MODULE IMPORTS")
    print("=" * 30)
    
    modules_to_test = [
        ('streamlit', 'Streamlit framework'),
        ('demo_enhancement', 'Demo enhancement features'),  
        ('updated_prompts', 'Enhanced AI prompts'),
        ('integrated_comprehensive_analyzer', 'Analysis engine')
    ]
    
    all_imports_successful = True
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}: {description}")
        except ImportError as e:
            print(f"❌ {module_name}: Import failed - {e}")
            all_imports_successful = False
        except Exception as e:
            print(f"⚠️ {module_name}: Warning - {e}")
    
    return all_imports_successful

def run_quick_validation():
    """Run quick system validation"""
    print("\\n🔍 RUNNING QUICK VALIDATION")
    print("=" * 35)
    
    # Check for required files
    required_files = [
        'streamlit_comprehensive_analyzer.py',
        'integrated_comprehensive_analyzer.py', 
        'updated_prompts.py',
        'demo_enhancement.py',
        'TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf'
    ]
    
    files_present = True
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} - Missing")
            files_present = False
    
    # Test environment
    env_path = Path('.env')
    if env_path.exists():
        print(f"✅ .env file present")
    else:
        print(f"⚠️ .env file missing - OpenAI features may not work")
    
    return files_present

def launch_streamlit_demo():
    """Launch the Streamlit demo application"""
    print("\\n🚀 LAUNCHING STREAMLIT DEMO")
    print("=" * 32)
    
    try:
        print("Starting Streamlit application...")
        print("URL: http://localhost:8501")
        print("\\n📋 Demo Instructions:")
        print("   1. Wait for app to load completely")
        print("   2. Click '🧠 Run Integrated Analyzer (Extended AI)'")  
        print("   3. Explore all 6 tabs for complete demo")
        print("   4. Test new demo features in Task 2")
        print("   5. Use screenshot helpers as needed")
        
        # Open browser after short delay
        print("\\nOpening browser in 3 seconds...")
        time.sleep(3)
        webbrowser.open('http://localhost:8501')
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_comprehensive_analyzer.py",
            "--server.headless", "false"
        ])
        
    except KeyboardInterrupt:
        print("\\n⏹️ Demo stopped by user")
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")

def generate_demo_materials():
    """Generate demo materials using the deliverables generator"""
    print("\\n📦 GENERATING DEMO MATERIALS")
    print("=" * 34)
    
    try:
        result = subprocess.run([
            sys.executable, "create_demo_deliverables.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ Error generating materials: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error running demo generator: {e}")

def main():
    """Main interactive demo runner"""
    print("🏥 KENYA SHIF HEALTHCARE POLICY ANALYZER")
    print("🎬 INTERACTIVE DEMO RUNNER")
    print("=" * 50)
    
    print("\\nChoose an option:")
    print("1. 🧪 Test System Components")
    print("2. 🚀 Launch Interactive Demo")  
    print("3. 📦 Generate Demo Materials")
    print("4. 🎯 Complete Demo Validation")
    print("5. 📖 Show Quick Start Guide")
    print("0. ❌ Exit")
    
    while True:
        try:
            choice = input("\\nEnter your choice (0-5): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
                
            elif choice == '1':
                imports_ok = test_imports()
                files_ok = run_quick_validation()
                
                if imports_ok and files_ok:
                    print("\\n✅ System validation passed!")
                else:
                    print("\\n⚠️ Some issues detected - review above")
                    
            elif choice == '2':
                print("\\n🚀 Launching demo...")
                launch_streamlit_demo()
                
            elif choice == '3':
                generate_demo_materials()
                
            elif choice == '4':
                print("\\n🎯 Running complete validation...")
                imports_ok = test_imports()
                files_ok = run_quick_validation()
                
                if imports_ok and files_ok:
                    print("\\n🎉 All validations passed! System ready for demo.")
                    launch_choice = input("\\nLaunch demo now? (y/N): ").strip().lower()
                    if launch_choice in ['y', 'yes']:
                        launch_streamlit_demo()
                else:
                    print("\\n❌ Validation issues found - resolve before demo")
                    
            elif choice == '5':
                print(\"\"\"
📖 QUICK START GUIDE
==================

1. **Prerequisites:**
   pip install -r requirements.txt
   echo "OPENAI_API_KEY=your-key" > .env

2. **Launch Demo:**
   streamlit run streamlit_comprehensive_analyzer.py

3. **Run Analysis:**  
   Click "🧠 Run Integrated Analyzer (Extended AI)"

4. **Explore Features:**
   - Dashboard Overview (metrics & CSV previews)
   - Task 2: Deterministic checks & JSON fallbacks  
   - AI Insights: Expert analysis & prompt downloads
   - All 6 tabs for comprehensive demo

5. **Demo Features:**
   ✅ 29 comprehensive gaps detected
   ✅ 100% expert-level prompts  
   ✅ Dual-phase analysis methodology
   ✅ Production-ready exports
                \"\"\")
                
            else:
                print("❌ Invalid choice. Please enter 0-5.")
                
        except KeyboardInterrupt:
            print("\\n\\n👋 Demo runner interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()