# Data Integrity Analysis - Complete Documentation

This directory contains comprehensive analysis of data integrity issues found in the healthcare analyzer system.

## Analysis Documents

### 1. **DATA_FLOW_INTEGRITY_ANALYSIS.md** (19 KB)
Comprehensive technical analysis covering:
- Executive summary of the data integrity issue
- Detailed deduplication flow analysis (Lines 2566-2900)
- Root cause identification (_parse_deduplication_results function)
- Gap file generation process
- all_gaps_before_dedup.csv analysis
- Historical run consistency checks
- Complete data flow mapping and diagrams
- Download functionality verification
- Impact assessment
- Line-by-line reference guide

**Best for:** Understanding the complete system architecture and where data corruption occurs

### 2. **DATA_INTEGRITY_FINDINGS.md** (8.5 KB)
Quick reference document with direct answers to critical questions:
- Deduplication flow (where called, what returns, saves to CSV)
- Gap file generation specifics
- all_gaps_before_dedup.csv purpose and usage
- Historical run consistency patterns
- Data flow mapping
- Download functionality details
- Root cause explanation with code snippet
- Evidence from JSON structure
- Impact assessment
- Files affected (corrupted vs clean)
- Absolute file paths

**Best for:** Quick lookup of specific findings and file locations

### 3. **CONCRETE_EXAMPLES.md** (9.3 KB)
Real data examples from actual runs showing:
- Example 1: Run 20251017_142114 contradiction analysis
- Example 2: Different duplicates in each run
- Example 3: CSV file inspection with duplicate rows
- Example 4: Dashboard display of duplicates
- Example 5: Working backup file (all_gaps_before_dedup.csv)
- Example 6: JSON metadata evidence
- Example 7: Output directory structure
- Example 8: Cross-run comparison of gap_id duplicates
- Example 9: Clean contradictions (not affected)
- Example 10: Before vs after deduplication comparison
- Summary table of all three runs

**Best for:** Understanding the concrete impact with real data examples

---

## Key Findings Summary

### The Issue
Duplicate gap entries in output CSV files. The deduplication process fails to remove gaps; instead, it creates duplicate rows with the same gap_id.

### Data Affected
- **Corrupted:** comprehensive_gaps_analysis.csv (29 rows with 27 unique gap_ids)
- **Corrupted:** gaps_deduplication_analysis.json (contains buggy deduplicated_gaps array)
- **Clean:** all_gaps_before_dedup.csv, ai_gaps.csv, clinical_gaps.csv, coverage_gaps.csv, ai_contradictions.csv

### Root Cause
**File:** `/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/integrated_comprehensive_analyzer.py`
**Lines:** 2902-2950 (_parse_deduplication_results function)
**Issue:** Function adds gaps from both "duplicates_removed" and "unique_gaps" sections of OpenAI response without checking if the same gap appears in both sections

### Scale
- **All runs affected:** Every analysis run (outputs_run_20251017_*) shows this issue
- **Contradictions clean:** 6 contradictions across all runs (not affected)
- **Gaps corrupted:** 2-4 duplicate gap_ids per run
- **Data exported as-is:** Users download CSV files with duplicates included

### Evidence
1. **CSV inspection:** comprehensive_gaps_analysis.csv has 29 rows but only 27-26 unique gap_ids
2. **JSON comparison:** openai_analysis.summary.final_count differs from deduplicated_gaps_count
3. **Run consistency:** Gap before dedup always 29, AI final count always 27-24, CSV always has duplicates
4. **Metadata:** gaps_deduplication_analysis.json proves overlapping gap_ids in both JSON sections

---

## File Locations

### Analysis Documentation
- `/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/DATA_FLOW_INTEGRITY_ANALYSIS.md`
- `/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/DATA_INTEGRITY_FINDINGS.md`
- `/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/CONCRETE_EXAMPLES.md`

### Code With Issues
- `/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/integrated_comprehensive_analyzer.py` (Lines 2566, 2570, 2774-2900, 2902-2950)
- `/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/streamlit_comprehensive_analyzer.py` (Lines 1383, 1761-1959)

### Affected Output Files
- `/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/outputs_run_20251017_142114/comprehensive_gaps_analysis.csv`
- `/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/outputs_run_20251017_135257/comprehensive_gaps_analysis.csv`
- `/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/outputs_run_20251017_132228/comprehensive_gaps_analysis.csv`
- `/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/outputs_run_20251017_*/gaps_deduplication_analysis.json`

### Clean Reference Files
- `/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/outputs_run_20251017_*/all_gaps_before_dedup.csv` (always clean)
- `/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/outputs_run_20251017_*/clinical_gaps_analysis.csv` (always clean)
- `/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/outputs_run_20251017_*/coverage_gaps_analysis.csv` (always clean)

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Total analysis documents | 3 |
| Lines analyzed | 500+ |
| Runs examined | 3 (142114, 135257, 132228) |
| Contradictions (all clean) | 6 |
| Gaps before dedup (all runs) | 29 |
| Gaps AI says should exist | 24-27 |
| CSV rows exported | 29-30 (with duplicates) |
| Unique gap_ids in exported CSVs | 24-27 (duplicates present) |
| Files with integrity issues | 2 per run |
| Files that are clean | 8+ per run |

---

## Reading Recommendations

1. **Start here:** DATA_INTEGRITY_FINDINGS.md (quick reference)
2. **For details:** DATA_FLOW_INTEGRITY_ANALYSIS.md (comprehensive technical analysis)
3. **For proof:** CONCRETE_EXAMPLES.md (real data from runs)

---

## Verification Method

To verify the issue yourself:

```bash
# Check for duplicates in CSV
python3 << 'VERIFY'
import pandas as pd

df = pd.read_csv('outputs_run_20251017_142114/comprehensive_gaps_analysis.csv')
print(f"Total rows: {len(df)}")
print(f"Unique gap_ids: {df['gap_id'].nunique()}")
print(f"\nDuplicate gap_ids:")
duplicates = df[df.duplicated(subset=['gap_id'], keep=False)]
print(duplicates[['gap_id', 'description']].to_string())
VERIFY
```

Expected output:
```
Total rows: 29
Unique gap_ids: 27

Duplicate gap_ids:
                gap_id                           description
COVERAGE_SERVICE_CATEGORY_08  Rehabilitation services...
COVERAGE_GEOGRAPHIC_ACCESS_01  Geographic access inequities...
```

---

## Notes

- This analysis does NOT propose fixes, only documents existing behavior
- All findings verified against actual data in outputs_run_* directories
- All line numbers verified in source code
- All file paths are absolute paths
- Documentation preserves complete analysis for reference
