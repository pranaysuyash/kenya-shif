#!/usr/bin/env python3
"""Capture screenshots showing actual analysis results by loading existing data"""

import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver():
    """Setup Chrome driver with proper options"""
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def wait_and_capture(driver, output_dir, filename, description, wait_time=2):
    """Wait and capture screenshot with description"""
    time.sleep(wait_time)
    screenshot_path = f"{output_dir}/{filename}"
    driver.save_screenshot(screenshot_path)
    size_kb = os.path.getsize(screenshot_path) / 1024
    print(f"   ✅ {description} ({size_kb:.1f} KB)")
    return screenshot_path

def click_button_safe(driver, button_text, partial=False):
    """Safely click a button by its text"""
    try:
        if partial:
            xpath = f"//button[contains(., '{button_text}')]"
        else:
            xpath = f"//button[text()='{button_text}']"
        
        button = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(0.5)
        button.click()
        print(f"   ✅ Clicked: {button_text}")
        return True
    except Exception as e:
        print(f"   ⚠️ Could not click {button_text}")
        return False

def capture_results_screenshots(output_dir="demo_release_20250827_FINAL_WITH_DEDUP/screenshots_with_results"):
    """Capture screenshots showing analysis results"""
    
    os.makedirs(output_dir, exist_ok=True)
    driver = setup_driver()
    
    try:
        print("\n📸 CAPTURING SCREENSHOTS WITH EXISTING RESULTS")
        print("=" * 60)
        
        # Navigate to app
        driver.get("http://localhost:8502")
        time.sleep(5)
        
        # PHASE 1: Load existing results
        print("\n📁 PHASE 1: Loading Existing Analysis Results")
        print("-" * 40)
        
        # Click "Load Existing Results" button
        if click_button_safe(driver, "Load Existing Results", partial=True):
            time.sleep(3)
            wait_and_capture(driver, output_dir, "01_results_loaded.png", "Results loaded notification", 2)
        
        # PHASE 2: Dashboard Tab
        print("\n📊 PHASE 2: Dashboard with Metrics")
        print("-" * 40)
        
        # Dashboard should show metrics if results are loaded
        if click_button_safe(driver, "Dashboard", partial=True):
            time.sleep(2)
            wait_and_capture(driver, output_dir, "02_dashboard_metrics.png", "Dashboard with KPIs", 2)
            
            # Scroll to show extraction summary
            driver.execute_script("window.scrollBy(0, 400);")
            wait_and_capture(driver, output_dir, "03_extraction_summary.png", "Extraction summary", 2)
            
            # Scroll to download section
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            wait_and_capture(driver, output_dir, "04_download_section.png", "Download buttons", 2)
        
        # PHASE 3: Task 1 - Structured Rules
        print("\n📋 PHASE 3: Task 1 - Structured Rules")
        print("-" * 40)
        
        if click_button_safe(driver, "Task 1", partial=True):
            time.sleep(2)
            wait_and_capture(driver, output_dir, "05_task1_rules.png", "Structured rules table", 2)
            
            # Scroll to see more rules
            driver.execute_script("window.scrollBy(0, 500);")
            wait_and_capture(driver, output_dir, "06_task1_more_rules.png", "More rules", 2)
        
        # PHASE 4: Task 2 - Contradictions & Gaps
        print("\n🔍 PHASE 4: Task 2 - Contradictions & Gaps")
        print("-" * 40)
        
        if click_button_safe(driver, "Task 2", partial=True):
            time.sleep(2)
            wait_and_capture(driver, output_dir, "07_task2_contradictions.png", "Contradictions section", 3)
            
            # Scroll to gaps
            driver.execute_script("window.scrollBy(0, 600);")
            wait_and_capture(driver, output_dir, "08_task2_gaps.png", "Gaps section", 2)
            
            # Run deterministic checks
            if click_button_safe(driver, "Run Deterministic Checks", partial=True):
                time.sleep(5)
                wait_and_capture(driver, output_dir, "09_deterministic_results.png", "Deterministic validation", 2)
        
        # PHASE 5: Task 3 - Kenya Context
        print("\n🇰🇪 PHASE 5: Task 3 - Kenya Context")
        print("-" * 40)
        
        if click_button_safe(driver, "Task 3", partial=True):
            time.sleep(2)
            wait_and_capture(driver, output_dir, "10_task3_kenya.png", "Kenya context analysis", 2)
            
            driver.execute_script("window.scrollBy(0, 500);")
            wait_and_capture(driver, output_dir, "11_task3_recommendations.png", "Kenya recommendations", 2)
        
        # PHASE 6: Advanced Analytics
        print("\n📈 PHASE 6: Advanced Analytics")
        print("-" * 40)
        
        if click_button_safe(driver, "Advanced", partial=True):
            time.sleep(2)
            wait_and_capture(driver, output_dir, "12_advanced_charts.png", "Advanced analytics charts", 2)
            
            driver.execute_script("window.scrollBy(0, 500);")
            wait_and_capture(driver, output_dir, "13_advanced_details.png", "Analysis details", 2)
        
        # PHASE 7: AI Insights
        print("\n🤖 PHASE 7: AI Insights")
        print("-" * 40)
        
        if click_button_safe(driver, "AI", partial=True):
            time.sleep(2)
            wait_and_capture(driver, output_dir, "14_ai_overview.png", "AI insights overview", 2)
            
            # Scroll to see contradictions
            driver.execute_script("window.scrollBy(0, 400);")
            wait_and_capture(driver, output_dir, "15_ai_contradictions.png", "AI contradictions detail", 3)
            
            # Scroll to see gaps
            driver.execute_script("window.scrollBy(0, 400);")
            wait_and_capture(driver, output_dir, "16_ai_gaps.png", "AI gaps detail", 3)
        
        # PHASE 8: Final Dashboard State
        print("\n✅ PHASE 8: Final Dashboard Summary")
        print("-" * 40)
        
        if click_button_safe(driver, "Dashboard", partial=True):
            time.sleep(2)
            
            # Capture full dashboard
            wait_and_capture(driver, output_dir, "17_final_dashboard.png", "Final dashboard state", 2)
            
            # Show sidebar with controls
            driver.execute_script("""
                var sidebar = document.querySelector('.stSidebar');
                if (sidebar) {
                    sidebar.style.display = 'block';
                    sidebar.style.width = '21rem';
                }
            """)
            wait_and_capture(driver, output_dir, "18_sidebar_controls.png", "Sidebar with all options", 2)
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ Screenshot capture complete!")
        
        # List all screenshots
        screenshots = sorted([f for f in os.listdir(output_dir) if f.endswith('.png')])
        print(f"\n📊 Total screenshots: {len(screenshots)}")
        for ss in screenshots:
            path = f"{output_dir}/{ss}"
            size = os.path.getsize(path) / 1024
            print(f"   ✅ {ss} ({size:.1f} KB)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🔚 Closing browser...")
        driver.quit()

if __name__ == "__main__":
    print("🎯 Screenshot Capture with Existing Results")
    print("=" * 60)
    print("This will capture screenshots using already-analyzed data.")
    print("Make sure Streamlit app is running on http://localhost:8502")
    print("=" * 60)
    capture_results_screenshots()