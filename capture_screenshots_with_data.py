#!/usr/bin/env python3
"""Capture screenshots with actual data by running the analysis first"""

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

def wait_for_element(driver, by, value, timeout=10):
    """Wait for element to be present"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        print(f"⚠️ Element not found: {value}")
        return None

def click_button(driver, button_text, partial=False):
    """Click a button by its text"""
    try:
        if partial:
            xpath = f"//button[contains(., '{button_text}')]"
        else:
            xpath = f"//button[text()='{button_text}']"
        
        button = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(1)
        button.click()
        return True
    except NoSuchElementException:
        print(f"⚠️ Button not found: {button_text}")
        return False

def expand_expander(driver, expander_text):
    """Click on an expander to open it"""
    try:
        # Try to find expander by partial text match
        xpath = f"//div[contains(@class, 'streamlit-expanderHeader')]//p[contains(text(), '{expander_text}')]"
        expander = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].scrollIntoView(true);", expander)
        time.sleep(0.5)
        expander.click()
        time.sleep(1)
        return True
    except:
        try:
            # Alternative: Click on the parent div
            xpath = f"//div[contains(@class, 'streamlit-expanderHeader')][contains(., '{expander_text}')]"
            expander = driver.find_element(By.XPATH, xpath)
            expander.click()
            time.sleep(1)
            return True
        except:
            print(f"⚠️ Could not expand: {expander_text}")
            return False

def capture_full_screenshots(output_dir="demo_release_20250827_FINAL_VALIDATED/screenshots"):
    """Capture screenshots with actual data"""
    
    os.makedirs(output_dir, exist_ok=True)
    driver = setup_driver()
    
    try:
        # Navigate to app
        print("🌐 Opening Streamlit app...")
        driver.get("http://localhost:8502")
        time.sleep(5)
        
        # PHASE 1: RUN THE INTEGRATED ANALYZER
        print("\n📊 PHASE 1: Running Integrated Analyzer...")
        
        # Look for the Run Integrated Analyzer button in sidebar
        sidebar_button_clicked = False
        try:
            # Try to find and click the integrated analyzer button
            buttons_to_try = [
                "🧠 Run Integrated Analyzer (Extended AI)",
                "Run Integrated Analyzer",
                "Run Integrated Analyzer (Extended AI)",
                "🧠 Run Integrated Analyzer"
            ]
            
            for btn_text in buttons_to_try:
                if click_button(driver, btn_text, partial=True):
                    print(f"✅ Clicked: {btn_text}")
                    sidebar_button_clicked = True
                    break
            
            if sidebar_button_clicked:
                # Wait for analysis to complete (look for success message or results)
                print("⏳ Waiting for analysis to complete (this may take 60-90 seconds)...")
                
                # Wait for completion - look for success indicators
                max_wait = 90
                wait_interval = 5
                elapsed = 0
                
                while elapsed < max_wait:
                    try:
                        # Check if analysis is complete by looking for success message
                        success_indicator = driver.find_element(By.XPATH, "//*[contains(text(), 'Analysis complete')]")
                        print("✅ Analysis complete detected!")
                        break
                    except:
                        try:
                            # Also check for data presence (e.g., KPI metrics)
                            kpi_element = driver.find_element(By.XPATH, "//div[contains(@class, 'metric')]")
                            print("✅ KPI metrics detected - analysis likely complete")
                            time.sleep(5)  # Give it a bit more time
                            break
                        except:
                            pass
                    
                    print(f"   Waiting... ({elapsed}s / {max_wait}s)")
                    time.sleep(wait_interval)
                    elapsed += wait_interval
                
                if elapsed >= max_wait:
                    print("⚠️ Analysis may not have completed fully, but continuing with screenshots...")
            else:
                print("⚠️ Could not find integrated analyzer button - may already be run")
        except Exception as e:
            print(f"⚠️ Issue with integrated analyzer: {e}")
        
        # PHASE 2: CAPTURE SCREENSHOTS WITH DATA
        print("\n📸 PHASE 2: Capturing screenshots with data...")
        
        # 1. Header and main dashboard
        print("📸 Capturing: Header with PDF status...")
        screenshot_path = f"{output_dir}/01_header_pdf_ready.png"
        driver.save_screenshot(screenshot_path)
        print(f"   ✅ Saved: {screenshot_path}")
        
        # 2. Dashboard Tab with KPIs
        try:
            # Click on Dashboard tab if available
            dashboard_tab = driver.find_element(By.XPATH, "//button[contains(., 'Dashboard')]")
            dashboard_tab.click()
            time.sleep(2)
        except:
            pass
        
        # Scroll to show KPIs
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(1)
        screenshot_path = f"{output_dir}/02_dashboard_kpis.png"
        driver.save_screenshot(screenshot_path)
        print(f"   ✅ Saved: Dashboard with KPIs")
        
        # 3. Expand CSV Previews
        print("📸 Expanding CSV previews...")
        expand_expander(driver, "Preview Extracted Data")
        expand_expander(driver, "Policy Services")
        expand_expander(driver, "Annex Procedures")
        time.sleep(2)
        screenshot_path = f"{output_dir}/03_csv_previews_expanded.png"
        driver.save_screenshot(screenshot_path)
        print(f"   ✅ Saved: CSV previews")
        
        # 4. Download section
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        screenshot_path = f"{output_dir}/04_download_section.png"
        driver.save_screenshot(screenshot_path)
        print(f"   ✅ Saved: Download section")
        
        # 5. Task 1 - Structured Rules
        try:
            task1_tab = driver.find_element(By.XPATH, "//button[contains(., 'Task 1')]")
            task1_tab.click()
            time.sleep(3)
            screenshot_path = f"{output_dir}/05_task1_structured_rules.png"
            driver.save_screenshot(screenshot_path)
            print(f"   ✅ Saved: Task 1 - Structured Rules")
        except:
            print("   ⚠️ Could not access Task 1 tab")
        
        # 6. Task 2 - Contradictions
        try:
            task2_tab = driver.find_element(By.XPATH, "//button[contains(., 'Task 2')]")
            task2_tab.click()
            time.sleep(3)
            
            # Scroll to show contradictions
            driver.execute_script("window.scrollTo(0, 400);")
            time.sleep(1)
            screenshot_path = f"{output_dir}/06_task2_contradictions.png"
            driver.save_screenshot(screenshot_path)
            print(f"   ✅ Saved: Task 2 - Contradictions")
            
            # Scroll to gaps
            driver.execute_script("window.scrollTo(0, 800);")
            time.sleep(1)
            screenshot_path = f"{output_dir}/07_task2_gaps.png"
            driver.save_screenshot(screenshot_path)
            print(f"   ✅ Saved: Task 2 - Gaps")
            
            # Try to run deterministic checks
            if click_button(driver, "Run Deterministic Checks", partial=True):
                time.sleep(5)
                screenshot_path = f"{output_dir}/08_deterministic_checks.png"
                driver.save_screenshot(screenshot_path)
                print(f"   ✅ Saved: Deterministic checks")
        except:
            print("   ⚠️ Could not access Task 2 tab")
        
        # 7. Task 3 - Kenya Context
        try:
            task3_tab = driver.find_element(By.XPATH, "//button[contains(., 'Task 3')]")
            task3_tab.click()
            time.sleep(3)
            screenshot_path = f"{output_dir}/09_task3_kenya_context.png"
            driver.save_screenshot(screenshot_path)
            print(f"   ✅ Saved: Task 3 - Kenya Context")
        except:
            print("   ⚠️ Could not access Task 3 tab")
        
        # 8. Advanced Analytics (if available)
        try:
            advanced_tab = driver.find_element(By.XPATH, "//button[contains(., 'Advanced')]")
            advanced_tab.click()
            time.sleep(3)
            screenshot_path = f"{output_dir}/10_advanced_analytics.png"
            driver.save_screenshot(screenshot_path)
            print(f"   ✅ Saved: Advanced Analytics")
        except:
            print("   ⚠️ Could not access Advanced Analytics tab")
        
        # 9. AI Insights
        try:
            ai_tab = driver.find_element(By.XPATH, "//button[contains(., 'AI')]")
            ai_tab.click()
            time.sleep(3)
            
            # Try to expand some AI sections
            expand_expander(driver, "Contradiction Analysis")
            expand_expander(driver, "Gap Analysis")
            time.sleep(2)
            
            screenshot_path = f"{output_dir}/11_ai_insights.png"
            driver.save_screenshot(screenshot_path)
            print(f"   ✅ Saved: AI Insights")
        except:
            print("   ⚠️ Could not access AI Insights tab")
        
        # 10. Sidebar with controls
        try:
            # Open sidebar if closed
            driver.execute_script("""
                var sidebar = document.querySelector('.stSidebar');
                if (sidebar) {
                    sidebar.style.display = 'block';
                    sidebar.style.width = '21rem';
                }
            """)
            time.sleep(1)
            screenshot_path = f"{output_dir}/12_sidebar_controls.png"
            driver.save_screenshot(screenshot_path)
            print(f"   ✅ Saved: Sidebar with controls")
        except:
            print("   ⚠️ Could not capture sidebar")
        
        # 11. Raw JSON Debug (if available)
        try:
            # Go back to Task 2 and expand JSON
            task2_tab = driver.find_element(By.XPATH, "//button[contains(., 'Task 2')]")
            task2_tab.click()
            time.sleep(2)
            
            expand_expander(driver, "Raw JSON")
            expand_expander(driver, "Contradictions JSON")
            expand_expander(driver, "Gaps JSON")
            time.sleep(2)
            
            driver.execute_script("window.scrollTo(0, 1500);")
            time.sleep(1)
            screenshot_path = f"{output_dir}/13_raw_json_debug.png"
            driver.save_screenshot(screenshot_path)
            print(f"   ✅ Saved: Raw JSON debug")
        except:
            print("   ⚠️ Could not capture JSON debug")
        
        print(f"\n✅ Screenshots captured successfully!")
        print(f"📁 Location: {output_dir}")
        
        # List all captured screenshots
        import glob
        screenshots = glob.glob(f"{output_dir}/*.png")
        print(f"📊 Total screenshots: {len(screenshots)}")
        for ss in sorted(screenshots):
            size = os.path.getsize(ss) / 1024  # KB
            print(f"   ✅ {os.path.basename(ss)} ({size:.1f} KB)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("\n🔚 Browser closed")

if __name__ == "__main__":
    print("🎯 Starting screenshot capture with actual data...")
    print("=" * 60)
    capture_full_screenshots()