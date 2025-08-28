# Manual Screenshot Testing Guide

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
