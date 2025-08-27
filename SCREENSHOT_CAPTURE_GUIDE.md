# Screenshot Capture Guide - With Actual Data

## ⚠️ IMPORTANT: Wait for Analysis to Complete!

The key to getting screenshots with actual data (not 0 values or progress bars) is to:
1. Run the complete analysis FIRST
2. Wait for it to fully complete (90+ seconds)
3. THEN capture screenshots

---

## 📸 Manual Screenshot Capture Process

### Step 1: Start Streamlit App
```bash
streamlit run streamlit_comprehensive_analyzer.py
```
Open browser to http://localhost:8502

### Step 2: Run Complete Analysis
1. Click **"Run Complete Extraction"** button in sidebar
2. **WAIT** for extraction to complete (15-20 seconds)
3. You should see:
   - "✅ Extraction complete!" message
   - Numbers appearing in the dashboard

### Step 3: Run Integrated Analyzer
1. Click **"Run Integrated Analyzer (Extended AI)"** button
2. **WAIT** for analysis to complete (60-90 seconds)
3. You should see:
   - Progress messages updating
   - "✅ Analysis complete!" notification
   - Dashboard metrics updating with actual values

### Step 4: Capture Dashboard Screenshots
After analysis completes, the dashboard should show:
- Total Services: **97** (not 0)
- Contradictions: **6** (not 0)
- Coverage Gaps: **27** (not 0)
- Tariff Coverage: **98.8%**

**Screenshots to capture:**
1. Main dashboard with all metrics populated
2. Extraction summary showing 97 services, 728 procedures
3. Charts showing data distribution

### Step 5: Task 1 - Structured Rules
1. Click **"Task 1: Structured Rules"** tab
2. You should see a table with 97 rows of policy services
3. **Capture:**
   - Table header showing columns
   - First 10-15 rows of data
   - Scroll down and capture more rows

### Step 6: Task 2 - Contradictions & Gaps
1. Click **"Task 2: Contradictions & Gaps"** tab
2. You should see:
   - **6 contradictions** listed (including dialysis)
   - **27 gaps** listed (including hypertension)
3. **Capture:**
   - Contradictions section with actual items
   - Gaps section with actual items
   - Click "Run Deterministic Checks" and capture validation results

### Step 7: Task 3 - Kenya Context
1. Click **"Task 3: Kenya Context"** tab
2. Should show Kenya-specific analysis
3. **Capture:** Kenya healthcare context analysis

### Step 8: Advanced Analytics
1. Click **"Advanced Analytics"** tab
2. Should show charts and visualizations with data
3. **Capture:**
   - Service distribution chart
   - Gap analysis visualization
   - Coverage heatmap

### Step 9: AI Insights
1. Click **"AI Insights"** tab
2. Should show AI-generated insights
3. **Capture:**
   - Contradiction analysis details
   - Gap analysis details
   - Recommendations

---

## 🔍 How to Verify Data is Loaded

### Check for these indicators:
✅ Dashboard shows numbers > 0
✅ Tables have rows of data
✅ Charts show actual bars/points (not empty)
✅ No "Loading..." or progress bars visible
✅ Success messages displayed

### Common Issues:
❌ All values showing 0 = Analysis not complete
❌ Progress bars visible = Still processing
❌ Empty tables = Data not loaded
❌ "No data available" = Need to run analysis first

---

## 📁 Expected Screenshot Results

When done correctly, you should have screenshots showing:

1. **Dashboard:** 97 services, 6 contradictions, 27 gaps
2. **Tables:** Populated with actual data rows
3. **Charts:** Bars/lines with real values
4. **Validation:** "✅ Dialysis contradiction FOUND"
5. **AI Results:** Actual insights text, not placeholders

---

## 🚀 Automated Alternative

If manual capture is difficult, use this approach:

1. First run the complete analysis:
```bash
python run_complete_demo.py
```

2. Wait for completion (shows "✅ DEMO EXECUTION COMPLETE!")

3. Then start Streamlit and click "Load Existing Results":
```bash
streamlit run streamlit_comprehensive_analyzer.py
# In UI: Click "Load Existing Results" button
```

4. Now capture screenshots - data will be pre-loaded

---

## ✅ Validation Checklist

Before submitting screenshots, verify:
- [ ] Dashboard shows 97 services (not 0)
- [ ] Contradictions show 6 items
- [ ] Gaps show 27 items  
- [ ] Dialysis contradiction is visible
- [ ] Hypertension gap is visible
- [ ] Charts have actual data points
- [ ] No progress bars or loading indicators
- [ ] Deterministic validation shows "ALL CHECKS PASSED"

---

*Note: The key is patience - wait for analysis to fully complete before capturing!*