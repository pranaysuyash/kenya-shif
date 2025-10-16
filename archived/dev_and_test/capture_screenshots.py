import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    return webdriver.Chrome(options=chrome_options)

def capture_screenshot(driver, filename, description):
    print(f"📸 Capturing: {description}")
    driver.save_screenshot(f"screenshots/{filename}")
    time.sleep(2)

def capture_all_screenshots():
    driver = setup_driver()
    
    try:
        driver.get("http://localhost:8501")
        time.sleep(5)
        screenshots = [
            ("01_header_banner.png", "Main header with PDF Ready status"),
            ("02_dashboard_overview.png", "KPI metrics and download section"),
            ("03_csv_previews.png", "Preview Extracted Data expanders"),
            ("04_downloads_complete.png", "Full download section"),
            ("05_task1_structured.png", "Facility level charts"),
            ("06_task2_contradictions.png", "Contradiction analysis"),
            ("07_task2_gaps_dual.png", "Dual-phase gap breakdown"),
            ("08_deterministic_checks.png", "Non-AI verification panel"),
            ("09_advanced_analytics.png", "Tariff distributions"),
            ("10_ai_insights.png", "Expert persona panels"),
            ("11_raw_json_debug.png", "Raw JSON fallbacks")
        ]
        for filename, description in screenshots:
            capture_screenshot(driver, filename, description)
    except Exception as e:
        print(f"❌ Screenshot error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    try:
        import selenium
    except ImportError:
        os.system("pip install selenium")
    capture_all_screenshots()
