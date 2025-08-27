#!/usr/bin/env python3
"""Capture screenshots of Streamlit app"""

import time
import os
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    print("✅ Selenium imported successfully")
except ImportError:
    print("Installing selenium...")
    os.system("pip install selenium")
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

def capture_streamlit_screenshots():
    """Capture screenshots using Chrome in headless mode"""
    
    output_dir = "demo_release_20250827_FINAL_VALIDATED/screenshots"
    os.makedirs(output_dir, exist_ok=True)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--force-device-scale-factor=1")
    
    try:
        # Try to use Chrome
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Chrome WebDriver initialized")
    except Exception as e:
        print(f"Chrome not available: {e}")
        print("Trying Safari...")
        try:
            # Fallback to Safari
            driver = webdriver.Safari()
            driver.set_window_size(1920, 1080)
            print("✅ Safari WebDriver initialized")
        except Exception as e2:
            print(f"❌ No browser available: {e2}")
            print("\n⚠️ ALTERNATIVE: Use built-in macOS screenshot tool")
            print("1. Open http://localhost:8501 in browser")
            print("2. Press Cmd+Shift+4 for area screenshot")
            print("3. Save to demo_release_20250827_FINAL_VALIDATED/screenshots/")
            return False
    
    try:
        # Navigate to Streamlit app
        driver.get("http://localhost:8501")
        print("📍 Navigated to Streamlit app")
        
        # Wait for app to load
        time.sleep(5)
        
        # Capture main dashboard
        screenshot_path = f"{output_dir}/01_main_dashboard.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 Captured: Main Dashboard → {screenshot_path}")
        
        # Try to click through tabs (if visible)
        tabs_to_capture = [
            ("Dashboard", "02_dashboard_tab.png"),
            ("Task 1", "03_task1_structured.png"),
            ("Task 2", "04_task2_contradictions.png"),
            ("Task 3", "05_task3_kenya_context.png"),
            ("AI Insights", "06_ai_insights.png"),
            ("Demo Mode", "07_demo_mode.png")
        ]
        
        for tab_name, filename in tabs_to_capture:
            try:
                # Try to find and click tab
                tab_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{tab_name}')]")
                tab_element.click()
                time.sleep(2)
                
                screenshot_path = f"{output_dir}/{filename}"
                driver.save_screenshot(screenshot_path)
                print(f"📸 Captured: {tab_name} → {screenshot_path}")
            except Exception as e:
                print(f"⚠️ Could not capture {tab_name}: {e}")
        
        # Capture sidebar
        try:
            # Expand sidebar if needed
            sidebar = driver.find_element(By.CLASS_NAME, "stSidebar")
            screenshot_path = f"{output_dir}/08_sidebar.png"
            driver.execute_script("arguments[0].scrollIntoView();", sidebar)
            driver.save_screenshot(screenshot_path)
            print(f"📸 Captured: Sidebar → {screenshot_path}")
        except:
            print("⚠️ Could not capture sidebar")
        
        print(f"\n✅ Screenshots saved to: {output_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Error capturing screenshots: {e}")
        return False
    finally:
        driver.quit()
        print("🔚 Browser closed")

def capture_with_playwright():
    """Alternative using Playwright (more reliable)"""
    try:
        from playwright.sync_api import sync_playwright
        print("Using Playwright for screenshots...")
        
        output_dir = "demo_release_20250827_FINAL_VALIDATED/screenshots"
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            page.goto("http://localhost:8501")
            page.wait_for_timeout(5000)
            
            # Capture full page
            page.screenshot(path=f"{output_dir}/01_full_page.png", full_page=True)
            print(f"📸 Captured: Full page screenshot")
            
            # Capture viewport
            page.screenshot(path=f"{output_dir}/02_viewport.png")
            print(f"📸 Captured: Viewport screenshot")
            
            browser.close()
            return True
    except ImportError:
        print("Playwright not installed. Install with: pip install playwright && playwright install")
        return False
    except Exception as e:
        print(f"Playwright error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Attempting to capture Streamlit screenshots...")
    print("=" * 50)
    
    # Check if Streamlit is running
    import requests
    try:
        response = requests.get("http://localhost:8501", timeout=2)
        if response.status_code == 200:
            print("✅ Streamlit is running at http://localhost:8501")
        else:
            print("⚠️ Streamlit returned status:", response.status_code)
    except:
        print("❌ Streamlit is not accessible at http://localhost:8501")
        print("Please start it with: streamlit run streamlit_comprehensive_analyzer.py")
        exit(1)
    
    # Try Selenium first
    success = capture_streamlit_screenshots()
    
    if not success:
        print("\n🔄 Trying Playwright as alternative...")
        success = capture_with_playwright()
    
    if not success:
        print("\n📝 MANUAL SCREENSHOT INSTRUCTIONS:")
        print("1. Open http://localhost:8501 in Chrome/Safari")
        print("2. Use macOS screenshot tool: Cmd+Shift+4")
        print("3. Capture these views:")
        print("   - Main dashboard with header")
        print("   - Each tab (Dashboard, Task 1, Task 2, etc.)")
        print("   - Sidebar with controls")
        print("   - Download section")
        print("4. Save all to: demo_release_20250827_FINAL_VALIDATED/screenshots/")
    else:
        # Count captured screenshots
        import glob
        screenshots = glob.glob("demo_release_20250827_FINAL_VALIDATED/screenshots/*.png")
        print(f"\n📊 Total screenshots captured: {len(screenshots)}")
        for ss in screenshots:
            print(f"   ✅ {os.path.basename(ss)}")