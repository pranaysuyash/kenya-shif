#!/usr/bin/env python3
"""
Local server runner for development and testing
Runs the Streamlit app locally with proper configuration
"""

import subprocess
import sys
import os
from pathlib import Path

def run_streamlit():
    """Run Streamlit app locally"""
    print("🚀 Starting Kenya SHIF Healthcare Analyzer...")
    print("=" * 60)
    
    # Check if streamlit_comprehensive_analyzer.py exists
    app_file = Path("streamlit_comprehensive_analyzer.py")
    if not app_file.exists():
        print(f"❌ Error: {app_file} not found")
        print("Please run this from the project root directory")
        sys.exit(1)
    
    # Check environment
    if not Path(".env").exists():
        print("⚠️  Warning: .env file not found")
        print("Please copy .env.example to .env and add your OPENAI_API_KEY")
        print()
        print("Creating .env template...")
        with open(".env", "w") as f:
            f.write("# Add your OpenAI API key here\n")
            f.write("OPENAI_API_KEY=sk-your-key-here\n")
        print("✓ .env created. Please edit it with your API key.")
        return
    
    # Run streamlit
    try:
        cmd = [sys.executable, "-m", "streamlit", "run", str(app_file)]
        print(f"Running: {' '.join(cmd)}")
        print("=" * 60)
        print()
        print("App should open at: http://localhost:8501")
        print()
        
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\n✓ App stopped")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running app: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_streamlit()
