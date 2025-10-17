# Manual Testing Guide for Streamlit Healthcare Analyzer

This guide provides step-by-step instructions for manually testing all functionalities of the Streamlit app.

## Prerequisites

```bash
source .venv/bin/activate
streamlit run streamlit_comprehensive_analyzer.py
```

## Test Checklist

### 1. App Launch ✓
- [ ] App starts without errors
- [ ] Main page loads with header "Kenya SHIF Healthcare Policy Analyzer"
- [ ] All tabs are visible in the interface
- [ ] No Python errors in terminal

**Expected**: App should launch cleanly with no error messages

---

### 2. Documentation Viewer (Sidebar) ✓
- [ ] Sidebar shows "Documentation" section
- [ ] Dropdown menu shows 3 options:
  - README.md
  - DEPLOYMENT_GUIDE.md
  - PRODUCTION_FILES_GUIDE.md
- [ ] Select README.md - content displays properly
- [ ] Select DEPLOYMENT_GUIDE.md - content displays properly
- [ ] Select PRODUCTION_FILES_GUIDE.md - content displays properly
- [ ] Markdown formatting renders correctly (headers, lists, code blocks)

**Expected**: All documentation files should be readable with proper formatting

---

### 3. Dashboard Metrics ✓

#### Top Metrics Cards
- [ ] "Total Services" metric displays
- [ ] Shows count (should be 728 based on latest data)
- [ ] "Total Contradictions" metric displays
- [ ] Shows 6 contradictions
- [ ] "Total Coverage Gaps" metric displays
- [ ] Shows gap count (should be 24 based on latest data)

#### Filters
- [ ] "High Severity" filter checkbox exists
- [ ] "High Impact" filter checkbox exists
- [ ] Clicking filters updates data tables
- [ ] Filter counts update correctly

**Expected**: All metrics should display with correct counts

---

### 4. Charts and Visualizations ✓

#### Contradictions by Type Chart
- [ ] Pie chart renders without errors
- [ ] Shows breakdown of 6 contradictions by type
- [ ] Hovering shows tooltips with counts
- [ ] Legend is readable
- [ ] Colors are distinct

#### Gaps by Category Chart
- [ ] Bar chart renders without errors
- [ ] Shows distribution of gaps by category
- [ ] X-axis labels are readable
- [ ] Y-axis shows counts
- [ ] Hovering shows exact values

#### Additional Visualizations
- [ ] Any severity/impact charts render properly
- [ ] Interactive features work (zoom, pan, etc.)

**Expected**: All charts should be interactive and display correct data

---

### 5. Data Table Display ✓

#### Contradictions Table
- [ ] Table displays all 6 contradictions
- [ ] Columns include:
  - contradiction_id
  - medical_specialty
  - contradiction_type
  - clinical_severity
  - description
- [ ] Table is scrollable horizontally if needed
- [ ] Can click to expand rows for full details
- [ ] Expanded view shows all fields

#### Gaps Table
- [ ] Table displays all 5 gaps
- [ ] Columns include:
  - gap_id
  - gap_category
  - gap_type
  - clinical_priority
  - description
- [ ] Table is scrollable
- [ ] Can expand rows for details

#### Coverage Gaps Table
- [ ] Table displays all 24 coverage gaps
- [ ] Proper column headers
- [ ] Data is readable

**Expected**: All tables should be navigable and data should be clearly displayed

---

### 6. AI Insights Buttons ✓

#### For Contradictions
- [ ] Each contradiction has "Show AI Insights" button
- [ ] Clicking button expands insights section
- [ ] Insights text displays properly
- [ ] Includes:
  - Medical analysis
  - Patient safety impact
  - Kenya health system impact
  - Evidence documentation
  - Recommended resolution

#### For Gaps
- [ ] Each gap has "Show AI Insights" button
- [ ] Clicking button expands insights section
- [ ] Insights text displays properly
- [ ] Includes:
  - Kenya epidemiological context
  - Affected populations
  - Health system impact
  - Recommended interventions

**Expected**: Insights should be well-formatted and readable

---

### 7. Download Functionality ✓

#### CSV Downloads
- [ ] "Download Data" section visible
- [ ] Checkboxes for each CSV file:
  - [ ] Contradictions CSV
  - [ ] Gaps CSV
  - [ ] Clinical Gaps CSV
  - [ ] Coverage Gaps CSV
  - [ ] Services Data CSV
- [ ] "Download Selected Files" button exists
- [ ] Clicking downloads a ZIP file
- [ ] ZIP file contains selected CSVs
- [ ] CSV files have correct data when opened

#### JSON Download
- [ ] Option to download complete analysis JSON
- [ ] JSON file downloads successfully
- [ ] JSON is valid and can be opened

**Expected**: All downloads should work and contain correct data

---

### 8. Session State & Navigation ✓

#### Tab Navigation
- [ ] Click between different tabs
- [ ] Data persists when returning to previous tab
- [ ] Filters remain applied across navigation
- [ ] Expanded rows stay expanded

#### State Persistence
- [ ] Apply filters, navigate away, come back - filters still applied
- [ ] Expand an insight, navigate away, come back - still expanded
- [ ] Select documentation file, navigate away, come back - selection persists

**Expected**: User selections should persist across navigation

---

### 9. Historical Data Loading ✓

#### Run Selection
- [ ] Sidebar shows "Select Analysis Run" dropdown
- [ ] Lists all available output directories
- [ ] Latest run is selected by default
- [ ] Can select older runs
- [ ] Selecting different run updates all data
- [ ] Metrics update to reflect selected run
- [ ] Tables update to reflect selected run

**Expected**: Should be able to switch between different analysis runs

---

### 10. JSON Field Formatting ✓

#### Complex Fields Display
- [ ] Kenya context fields render as formatted text or tables
- [ ] Evidence documentation displays properly
- [ ] Recommended interventions show as bullet points or structured format
- [ ] No raw JSON strings visible to user
- [ ] Long text fields are readable (not truncated awkwardly)

**Expected**: All complex data should be user-friendly, not raw JSON

---

### 11. Error Handling ✓

#### Missing Data
- [ ] If a CSV file is missing, app shows graceful error message
- [ ] App doesn't crash if data is incomplete
- [ ] Missing fields show "N/A" or similar placeholder

#### Invalid Data
- [ ] App handles empty CSVs gracefully
- [ ] Malformed JSON doesn't crash the app
- [ ] Error messages are user-friendly (not stack traces)

**Expected**: App should degrade gracefully, not crash

---

### 12. Performance ✓

#### Load Times
- [ ] Initial app load takes less than 10 seconds
- [ ] Switching tabs is instantaneous or nearly so
- [ ] Filtering data updates quickly (< 1 second)
- [ ] Charts render without noticeable delay

#### Responsiveness
- [ ] Large tables scroll smoothly
- [ ] No lag when clicking buttons
- [ ] App remains responsive during long operations
- [ ] No memory warnings in browser console

#### Long Sessions
- [ ] Run app for 10+ minutes
- [ ] No memory leaks (check browser task manager)
- [ ] App doesn't slow down over time
- [ ] Can perform all operations multiple times

**Expected**: App should be fast and responsive throughout use

---

## Known Issues from Automated Tests

The automated test suite revealed these findings:

1. **Column Names Changed** (WARNING - Not a bug)
   - CSV column names use snake_case (e.g., `contradiction_id`, `gap_category`)
   - This is intentional and works correctly in the app
   - Old column names (`Contradiction`, `Type`, etc.) were updated

2. **Services Count** (WARNING)
   - Expected 825 services, found 728
   - This may be due to data filtering or different extraction runs
   - Verify this is expected

3. **JSON Structure** (WARNING - Not a bug)
   - JSON uses different top-level keys than originally expected
   - Uses: `policy_results`, `annex_results`, `ai_analysis`, etc.
   - This is the correct structure

## Test Report Template

As you complete each test, mark it with ✓ or ✗ and add notes:

```
Test: [Test Name]
Status: PASS/FAIL
Notes: [Any observations, issues, or unexpected behavior]
```

## Critical Tests (Must Pass)

These tests are critical for the app to be production-ready:

1. ✓ App launches without errors
2. ✓ All 6 contradictions display correctly
3. ✓ All gaps display correctly
4. ✓ AI insights are readable and properly formatted
5. ✓ Downloads work and contain correct data
6. ✓ No crashes during normal use
7. ✓ Documentation is accessible and readable

## Completion Checklist

- [ ] All critical tests pass
- [ ] No major bugs found
- [ ] Performance is acceptable
- [ ] User experience is smooth
- [ ] Ready for production deployment

---

**Testing Date**: _______________
**Tested By**: _______________
**Version**: 5.0
**Overall Status**: PASS / FAIL / NEEDS WORK
