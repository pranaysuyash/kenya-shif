#!/usr/bin/env python3
"""
Screenshot capture utility for Streamlit app testing
"""
import subprocess
import time
import requests
import os
from pathlib import Path

def kill_existing_streamlit():
    """Kill any existing streamlit processes"""
    try:
        subprocess.run(['pkill', '-f', 'streamlit'], capture_output=True)
        time.sleep(2)
        print("✅ Cleared any existing Streamlit processes")
    except:
        pass

def start_streamlit_background():
    """Start Streamlit in background and return process"""
    kill_existing_streamlit()
    
    # Find an available port
    for port in [8504, 8505, 8506, 8507]:
        try:
            response = requests.get(f"http://localhost:{port}", timeout=1)
        except:
            # Port is available
            print(f"✅ Using port {port}")
            
            process = subprocess.Popen([
                'streamlit', 'run', 'streamlit_comprehensive_analyzer.py',
                '--server.port', str(port),
                '--server.headless', 'false'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for startup
            print("⏳ Waiting for Streamlit to start...")
            time.sleep(10)
            
            # Check if it's running
            try:
                response = requests.get(f"http://localhost:{port}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Streamlit running on http://localhost:{port}")
                    return process, port
            except:
                pass
    
    print("❌ Could not start Streamlit on any port")
    return None, None

def take_screenshot(url, filename):
    """Take a screenshot of the URL using a headless browser"""
    try:
        # Try using playwright if available
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(3000)  # Wait 3 seconds for page to load
            page.screenshot(path=filename, full_page=True)
            browser.close()
            return True
    except ImportError:
        print("⚠️ Playwright not available for screenshots")
        return False
    except Exception as e:
        print(f"❌ Screenshot failed: {e}")
        return False

def capture_streamlit_screenshots():
    """Capture screenshots of Streamlit app functionality"""
    print("📸 Starting Streamlit screenshot capture...")
    
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    # Start Streamlit
    process, port = start_streamlit_background()
    if not process:
        print("❌ Could not start Streamlit for screenshot capture")
        return False
    
    base_url = f"http://localhost:{port}"
    
    try:
        # Capture main page
        print("📸 Capturing main dashboard...")
        success = take_screenshot(base_url, screenshots_dir / "01_main_dashboard.png")
        if success:
            print("✅ Main dashboard screenshot captured")
        
        # Add artificial interactions by manipulating URL parameters if possible
        # Or use selenium for more complex interactions
        
        return True
        
    except Exception as e:
        print(f"❌ Screenshot capture failed: {e}")
        return False
    finally:
        if process:
            process.terminate()
            print("🛑 Streamlit process terminated")

def create_manual_screenshot_guide():
    """Create a guide for manual screenshot testing"""
    guide = """# Manual Screenshot Testing Guide

## Prerequisites
1. Ensure Streamlit app is working: `python debug_streamlit_comprehensive.py`
2. Start Streamlit: `streamlit run streamlit_comprehensive_analyzer.py`

## Screenshots to Capture

### 1. Main Dashboard (Initial Load)
- URL: http://localhost:8501
- Shows: App title, sidebar, main content area
- Expected: ✅ OpenAI Ready, PDF Ready indicators

### 2. Load Existing Results
- Click: "📂 Load Existing Results" button in sidebar
- Expected: ✅ Success message, data loaded (97 services, 26 gaps, 7 contradictions)

### 3. Dashboard Overview Tab
- Navigate to: "📊 Dashboard Overview" tab
- Expected: Metrics showing 97 services, 7 contradictions, 26 gaps

### 4. Task 1 Tab
- Navigate to: "📋 Task 1: Structured Rules" tab  
- Expected: Rules table with actual data, not empty

### 5. Task 2 Tab
- Navigate to: "🔍 Task 2: Contradictions & Gaps" tab
- Expected: List of 7 contradictions and 26 gaps with details

### 6. Run Complete Extraction Button
- Click: "🚀 Run Complete Extraction" in sidebar
- Expected: No AttributeError, either loads existing or runs analysis

### 7. File Downloads Section
- Scroll to: Downloads section in dashboard
- Expected: Available CSV files for download

## Verification Points
- ✅ No AttributeError exceptions in browser console
- ✅ Data displays correctly (not empty tables)
- ✅ Buttons are clickable and responsive
- ✅ Numbers match expected: 97 services, 26 gaps, 7 contradictions
- ✅ Key phrase visible in structured rules: "Health education and wellness..."

## Common Issues to Check
- ❌ Empty tables (data mapping issues)
- ❌ "File not found" errors in downloads
- ❌ AttributeError exceptions when clicking buttons
- ❌ Charts showing only "Unknown" values

## Report Format
For each screenshot, document:
1. What action was taken
2. What was expected
3. What actually happened
4. Any errors or issues observed

Save screenshots as: `screenshot_01_description.png`
"""
    
    with open("manual_screenshot_guide.md", "w") as f:
        f.write(guide)
    
    print("📋 Manual screenshot guide created: manual_screenshot_guide.md")

if __name__ == "__main__":
    print("🔍 Streamlit Screenshot Capture Utility")
    print()
    
    # Check if we can do automated screenshots
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright available for automated screenshots")
        automated = True
    except ImportError:
        print("⚠️ Playwright not available - creating manual testing guide instead")
        automated = False
    
    if automated:
        success = capture_streamlit_screenshots()
        if success:
            print("✅ Screenshot capture completed")
        else:
            print("❌ Screenshot capture failed - falling back to manual guide")
            create_manual_screenshot_guide()
    else:
        create_manual_screenshot_guide()
    
    print("\n📝 NEXT STEPS:")
    print("1. Follow manual_screenshot_guide.md for systematic testing")
    print("2. Start Streamlit: streamlit run streamlit_comprehensive_analyzer.py")
    print("3. Test each feature and capture evidence")
    print("4. Document any issues found")