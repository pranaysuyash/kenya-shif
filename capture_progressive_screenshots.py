#!/usr/bin/env python3
"""Progressive screenshot capture - captures initial state, runs analysis, then captures results"""

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

def click_element_safe(driver, xpath, description):
    """Safely click an element"""
    try:
        element = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
        element.click()
        print(f"   ✅ Clicked: {description}")
        return True
    except Exception as e:
        print(f"   ⚠️ Could not click {description}: {e}")
        return False

def expand_section(driver, text):
    """Expand a streamlit expander section"""
    xpaths = [
        f"//div[contains(@class, 'streamlit-expanderHeader')]//p[contains(text(), '{text}')]",
        f"//div[contains(@class, 'streamlit-expanderHeader')][contains(., '{text}')]",
        f"//button[contains(., '{text}')]"
    ]
    for xpath in xpaths:
        if click_element_safe(driver, xpath, f"expander '{text}'"):
            return True
    return False

def capture_progressive_screenshots(output_dir="demo_release_20250827_FINAL_WITH_DEDUP/screenshots"):
    """Capture screenshots progressively as features are executed"""
    
    os.makedirs(output_dir, exist_ok=True)
    driver = setup_driver()
    
    try:
        # PHASE 1: INITIAL STATE CAPTURE
        print("\n📸 PHASE 1: Capturing Initial State")
        print("=" * 60)
        
        driver.get("http://localhost:8502")
        time.sleep(5)
        
        # 1. Main interface
        wait_and_capture(driver, output_dir, "01_initial_main.png", "Initial main interface", 2)
        
        # 2. Show sidebar
        driver.execute_script("""
            var sidebar = document.querySelector('.stSidebar');
            if (sidebar) {
                sidebar.style.display = 'block';
                sidebar.style.width = '21rem';
            }
        """)
        wait_and_capture(driver, output_dir, "02_initial_sidebar.png", "Sidebar with options", 2)
        
        # 3. Try to click Dashboard tab
        click_element_safe(driver, "//button[contains(., 'Dashboard')]", "Dashboard tab")
        wait_and_capture(driver, output_dir, "03_initial_dashboard_empty.png", "Empty dashboard", 2)
        
        # PHASE 2: RUN COMPLETE EXTRACTION
        print("\n📊 PHASE 2: Running Complete Extraction")
        print("=" * 60)
        
        if click_element_safe(driver, "//button[contains(., 'Run Complete Extraction')]", "Complete Extraction"):
            print("   ⏳ Waiting for extraction (15 seconds)...")
            time.sleep(15)
            wait_and_capture(driver, output_dir, "04_extraction_complete.png", "After extraction", 2)
            
            # Expand CSV previews
            expand_section(driver, "Policy Services")
            wait_and_capture(driver, output_dir, "05_policy_services_csv.png", "Policy Services CSV", 2)
            
            expand_section(driver, "Annex Procedures")
            wait_and_capture(driver, output_dir, "06_annex_procedures_csv.png", "Annex Procedures CSV", 2)
        
        # PHASE 3: RUN INTEGRATED ANALYZER
        print("\n🧠 PHASE 3: Running Integrated Analyzer")
        print("=" * 60)
        
        # Try multiple button variations
        buttons = [
            "//button[contains(., '🧠 Run Integrated Analyzer')]",
            "//button[contains(., 'Run Integrated Analyzer (Extended AI)')]",
            "//button[contains(., 'Run Integrated Analyzer')]"
        ]
        
        analyzer_clicked = False
        for btn_xpath in buttons:
            if click_element_safe(driver, btn_xpath, "Integrated Analyzer"):
                analyzer_clicked = True
                break
        
        if analyzer_clicked:
            print("   ⏳ Waiting for initial processing (20 seconds)...")
            time.sleep(20)
            wait_and_capture(driver, output_dir, "07_analyzer_running.png", "Analyzer running", 2)
            
            print("   ⏳ Waiting for results to populate (30 seconds)...")
            time.sleep(30)
            wait_and_capture(driver, output_dir, "08_analyzer_results.png", "Analyzer results", 2)
        
        # PHASE 4: CAPTURE TASK TABS
        print("\n📑 PHASE 4: Capturing Task Results")
        print("=" * 60)
        
        # Task 1 - Structured Rules
        if click_element_safe(driver, "//button[contains(., 'Task 1')]", "Task 1 tab"):
            time.sleep(3)
            wait_and_capture(driver, output_dir, "09_task1_structured.png", "Task 1 - Structured Rules", 2)
            
            # Scroll down for more content
            driver.execute_script("window.scrollBy(0, 500);")
            wait_and_capture(driver, output_dir, "10_task1_details.png", "Task 1 - Details", 2)
        
        # Task 2 - Contradictions & Gaps
        if click_element_safe(driver, "//button[contains(., 'Task 2')]", "Task 2 tab"):
            time.sleep(3)
            wait_and_capture(driver, output_dir, "11_task2_initial.png", "Task 2 - Initial view", 2)
            
            # Run deterministic checks
            if click_element_safe(driver, "//button[contains(., 'Run Deterministic Checks')]", "Deterministic Checks"):
                time.sleep(5)
                wait_and_capture(driver, output_dir, "12_task2_deterministic.png", "Deterministic checks", 2)
            
            # Scroll for gaps
            driver.execute_script("window.scrollBy(0, 500);")
            wait_and_capture(driver, output_dir, "13_task2_gaps.png", "Task 2 - Gaps", 2)
        
        # Task 3 - Kenya Context
        if click_element_safe(driver, "//button[contains(., 'Task 3')]", "Task 3 tab"):
            time.sleep(3)
            wait_and_capture(driver, output_dir, "14_task3_kenya.png", "Task 3 - Kenya Context", 2)
            
            driver.execute_script("window.scrollBy(0, 500);")
            wait_and_capture(driver, output_dir, "15_task3_details.png", "Task 3 - Details", 2)
        
        # PHASE 5: ADVANCED FEATURES
        print("\n🔬 PHASE 5: Advanced Features")
        print("=" * 60)
        
        # Advanced Analytics
        if click_element_safe(driver, "//button[contains(., 'Advanced')]", "Advanced Analytics"):
            time.sleep(3)
            wait_and_capture(driver, output_dir, "16_advanced_analytics.png", "Advanced Analytics", 2)
        
        # AI Insights
        if click_element_safe(driver, "//button[contains(., 'AI')]", "AI Insights"):
            time.sleep(3)
            wait_and_capture(driver, output_dir, "17_ai_insights.png", "AI Insights", 2)
            
            # Try to expand AI sections
            expand_section(driver, "Contradiction Analysis")
            wait_and_capture(driver, output_dir, "18_ai_contradictions.png", "AI Contradictions", 3)
            
            expand_section(driver, "Gap Analysis")
            wait_and_capture(driver, output_dir, "19_ai_gaps.png", "AI Gaps", 3)
        
        # PHASE 6: FINAL DASHBOARD STATE
        print("\n📊 PHASE 6: Final Dashboard State")
        print("=" * 60)
        
        if click_element_safe(driver, "//button[contains(., 'Dashboard')]", "Dashboard tab"):
            time.sleep(2)
            wait_and_capture(driver, output_dir, "20_final_dashboard.png", "Final dashboard with data", 2)
            
            # Scroll to show different sections
            driver.execute_script("window.scrollBy(0, 300);")
            wait_and_capture(driver, output_dir, "21_final_metrics.png", "Final metrics", 2)
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            wait_and_capture(driver, output_dir, "22_final_downloads.png", "Download section", 2)
        
        # Summary
        print("\n✅ Progressive screenshot capture complete!")
        print("=" * 60)
        
        # List all screenshots
        screenshots = sorted([f for f in os.listdir(output_dir) if f.endswith('.png')])
        print(f"📊 Total screenshots captured: {len(screenshots)}")
        for ss in screenshots:
            path = f"{output_dir}/{ss}"
            size = os.path.getsize(path) / 1024
            print(f"   ✅ {ss} ({size:.1f} KB)")
        
    except Exception as e:
        print(f"\n❌ Error during capture: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🔚 Closing browser...")
        driver.quit()
        print("✅ Done!")

if __name__ == "__main__":
    print("🎯 Starting Progressive Screenshot Capture")
    print("=" * 60)
    print("This will capture screenshots progressively as features are executed.")
    print("Make sure Streamlit app is running on http://localhost:8502")
    print("=" * 60)
    capture_progressive_screenshots()