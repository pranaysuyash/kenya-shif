#!/usr/bin/env python3
"""
Streamlit Launch Script for Dr. Rishi Comprehensive Healthcare Analyzer

Usage:
python launch_streamlit.py

Or directly:
streamlit run streamlit_comprehensive_analyzer.py
"""

import subprocess
import sys
import os
from pathlib import Path

def launch_streamlit():
    """Launch the Streamlit app"""
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Set up environment
    env = os.environ.copy()
    
    # Launch Streamlit
    app_file = "streamlit_comprehensive_analyzer.py"
    
    if Path(app_file).exists():
        print(f"🚀 Launching Dr. Rishi Comprehensive Healthcare Analyzer...")
        print(f"📁 Working directory: {script_dir}")
        print(f"🌐 App will open at: http://localhost:8501")
        print(f"📱 To stop: Press Ctrl+C")
        
        # Launch command
        cmd = [sys.executable, "-m", "streamlit", "run", app_file, "--server.address", "0.0.0.0"]
        
        try:
            subprocess.run(cmd, env=env)
        except KeyboardInterrupt:
            print("\n👋 Streamlit app stopped")
        except Exception as e:
            print(f"❌ Error launching Streamlit: {e}")
    else:
        print(f"❌ App file not found: {app_file}")
        print(f"📁 Current directory: {os.getcwd()}")
        print(f"📄 Available files: {list(Path('.').glob('streamlit*.py'))}")

if __name__ == "__main__":
    launch_streamlit()