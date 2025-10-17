# CONCRETE EXAMPLES - DATA INTEGRITY ISSUES

## Example 1: Run 20251017_142114

### The Contradiction (what AI says vs what's saved)

**In gaps_deduplication_analysis.json:**

AI Analysis Summary:
```json
{
  "original_count": 29,
  "final_count": 27,
  "duplicates_found": 2
}
```

AI found 2 duplicate pairs and says result should be 27 gaps.

### What Actually Got Saved

**deduplicated_gaps_count in JSON:** 29
**comprehensive_gaps_analysis.csv rows:** 29 (header + 29 data rows)
**Unique gap_ids in CSV:** 27

The duplicates:
```
Row 1: gap_id = "COVERAGE_SERVICE_CATEGORY_08"
Row 17: gap_id = "COVERAGE_SERVICE_CATEGORY_08"  ← DUPLICATE

Row 24: gap_id = "COVERAGE_GEOGRAPHIC_ACCESS_01"
Row 1: gap_id = "COVERAGE_GEOGRAPHIC_ACCESS_01"  ← DUPLICATE
```

### Why This Happened

**In gaps_deduplication_analysis.json, the openai_analysis shows:**

Duplicates Removed section:
```json
[
  {
    "master_gap_id": "gap_16",
    "merged_ids": ["gap_16", "gap_1"],
    "best_description": "Rehabilitation services..."
  },
  {
    "master_gap_id": "gap_23",
    "merged_ids": ["gap_23", "gap_28"],
    "best_description": "Geographic access inequities..."
  }
]
```

Unique Gaps section (excerpt):
```json
[
  {"gap_id": "gap_2", "description": "Late diagnosis and limited access..."},
  {"gap_id": "gap_3", "description": "Pneumonia is the leading..."},
  ...
  {"gap_id": "gap_16", "description": "Rehabilitation services..."},  ← SAME AS MASTER!
  ...
  {"gap_id": "gap_23", "description": "Geographic access inequities..."},  ← SAME AS MASTER!
  ...
]
```

**The parser added:**
- gap_16 from duplicates_removed section
- gap_16 AGAIN from unique_gaps section (because AI included it there)
- gap_23 from duplicates_removed section
- gap_23 AGAIN from unique_gaps section

**Result:** 2 + 27 = 29 items in final_gaps (should be 27)

---

## Example 2: Run 20251017_135257

### Different Duplicates Each Run

**Gaps that are duplicates in THIS run:**
- COVERAGE_SERVICE_CATEGORY_07 (gap_15) - appears twice
- PNEUMONIA_PREVENTION_TREATMENT_003 (gap_3) - appears twice
- COVERAGE_SERVICE_CATEGORY_05 (gap_12) - appears twice
- COVERAGE_GEOGRAPHIC_ACCESS_01 (gap_23) - appears twice

**CSV file:**
- 29 rows (30 lines with header)
- Only 25 unique gap_ids
- 4 gap_ids appear exactly twice

**AI said:** final_count = 25
**Parser returned:** 29 items
**CSV contains:** 29 rows with 4 duplicates

### Why Different Than Run 1?

OpenAI structured the response differently this run:
- Run 1: 2 master gaps in duplicates_removed, they also appear in unique_gaps
- Run 2: 4 master gaps in duplicates_removed, they also appear in unique_gaps
- Run 3: 4 master gaps in duplicates_removed, they also appear in unique_gaps

The bug is the SAME (parser doesn't check for duplicates), but OpenAI's response structure varies, so different gaps become duplicates each time.

---

## Example 3: CSV File Inspection

### What Users Download

**File:** comprehensive_gaps_analysis.csv from run 20251017_142114

```csv
gap_id,gap_category,gap_type,...
COVERAGE_SERVICE_CATEGORY_08,service_category,Rehabilitation services...
COVERAGE_GEOGRAPHIC_ACCESS_01,geographic_access,Facility distribution...
CANCER_EARLY_DETECTION_002,cancer_early_detection_and_access_to_curative_treatment,...
PNEUMONIA_PREVENTION_TREATMENT_003,pneumonia_prevention_and_oxygen_therapy,...
...
(27 unique gaps should be here)
...
COVERAGE_SERVICE_CATEGORY_08,service_category,Rehabilitation services...   ← DUPLICATE #1
...
COVERAGE_GEOGRAPHIC_ACCESS_01,geographic_access,Facility distribution...   ← DUPLICATE #2
```

**User sees:** 29 rows in CSV
**User assumes:** 29 unique gaps
**Reality:** Only 27 unique gaps (2 are exact duplicates)

---

## Example 4: Dashboard Display

### What Dashboard Shows

When user opens the dashboard and looks at the gaps section:

```
Total Gaps: 29

1. Rehabilitation services (COVERAGE_SERVICE_CATEGORY_08)
2. Geographic access inequities (COVERAGE_GEOGRAPHIC_ACCESS_01)
3. Late diagnosis and limited access (CANCER_EARLY_DETECTION_002)
...
27. (other gaps)
...
28. Rehabilitation services (COVERAGE_SERVICE_CATEGORY_08)    ← DUPLICATE
29. Geographic access inequities (COVERAGE_GEOGRAPHIC_ACCESS_01)  ← DUPLICATE
```

**User problem:** They see 29 items but 27 are unique. If they're building a report or recommendations, they're counting the same gap twice.

---

## Example 5: Backup File Works Correctly

**File:** all_gaps_before_dedup.csv from same run

```csv
gap_id,gap_category,gap_type,...
COVERAGE_SERVICE_CATEGORY_01,service_category,Frequent stockouts...
COVERAGE_SERVICE_CATEGORY_02,service_category,Primary care facilities...
...
(exactly 29 rows)
...
```

**This file:**
- Has 29 rows (correct - before deduplication)
- Has 29 unique gap_ids (no duplicates)
- Is clean and usable
- Is available as download but not shown by default

---

## Example 6: Evidence in JSON Metadata

**File:** gaps_deduplication_analysis.json from run 20251017_142114

Key evidence of the bug:

```python
# What the JSON contains:
{
  "timestamp": "2025-10-17T14:22:49.154417",
  "original_gaps_count": 29,
  "deduplicated_gaps_count": 29,           # ← SHOULD BE 27
  "reduction_percentage": 0.0,              # ← SHOULD BE 6.9%
  "openai_analysis": {
    "summary": {
      "original_count": 29,
      "final_count": 27,                    # ← AI is RIGHT
      "duplicates_found": 2                 # ← AI found the issues
    }
  },
  "deduplicated_gaps": [
    # 29 items here (should be 27)
    # Contains 2 duplicate gap_ids
  ]
}
```

**The discrepancy:**
- `deduplicated_gaps_count`: 29 (wrong - from buggy parser)
- `openai_analysis.summary.final_count`: 27 (correct - from AI)

This JSON is downloadable and shows the corruption clearly.

---

## Example 7: Files in Output Directory

### What gets created for a single run

```
outputs_run_20251017_142114/
├── ai_contradictions.csv                     (6 rows - CLEAN)
├── ai_gaps.csv                               (5-6 rows - CLEAN)  
├── all_gaps_before_dedup.csv                 (29 rows - CLEAN)
├── annex_procedures.csv                      (729 rows - CLEAN)
├── annex_surgical_tariffs_all.csv            (729 rows - CLEAN)
├── clinical_gaps_analysis.csv                (5-6 rows - CLEAN)
├── comprehensive_gaps_analysis.csv           (29 rows - HAS DUPLICATES)
├── coverage_gaps_analysis.csv                (24-25 rows - CLEAN)
├── gaps_deduplication_analysis.json          (metadata showing duplicates)
├── rules_p1_18_structured.csv                (98 rows - CLEAN)
├── rules_p1_18_structured_exploded.csv       (169 rows - CLEAN)
└── rules_p1_18_structured_wide.csv           (32 rows - CLEAN)
```

**Only these 2 files have data integrity issues:**
1. comprehensive_gaps_analysis.csv (29 rows with 2-4 duplicates)
2. gaps_deduplication_analysis.json (contains the buggy array)

---

## Example 8: Cross-Run Comparison

### Gap ID Duplicates Vary by Run

**Run 20251017_142114:**
```
Duplicate: COVERAGE_SERVICE_CATEGORY_08 (gap_16)
Duplicate: COVERAGE_GEOGRAPHIC_ACCESS_01 (gap_23)
Total duplicates: 2 gap_ids appearing twice
```

**Run 20251017_135257:**
```
Duplicates: COVERAGE_SERVICE_CATEGORY_07 (gap_15)
Duplicates: PNEUMONIA_PREVENTION_TREATMENT_003 (gap_3)
Duplicates: COVERAGE_SERVICE_CATEGORY_05 (gap_12)
Duplicates: COVERAGE_GEOGRAPHIC_ACCESS_01 (gap_23)
Total duplicates: 4 gap_ids appearing twice
```

**Run 20251017_132228:**
```
Duplicates: PNEUMONIA_PREVENTION_TREATMENT_003 (gap_3)
Duplicates: COVERAGE_SERVICE_CATEGORY_02 (gap_7)
Duplicates: COVERAGE_GEOGRAPHIC_ACCESS_01 (gap_23)
Duplicates: COVERAGE_SERVICE_CATEGORY_15 (gap_29)
Total duplicates: 4 gap_ids appearing twice
```

**Pattern:** gap_23 (geographic access) is a duplicate in ALL runs

---

## Example 9: Contradictions Are Clean

**File:** ai_contradictions.csv from run 20251017_142114

```csv
contradiction_id,type,policy_area,description
1,Coverage vs Tariff,Emergency Services,...
2,Service Level vs Facility Capacity,...
3,Policy Design vs Implementation,...
4,Coverage Design vs Financial Sustainability,...
5,Geographic Targeting vs Equity,...
6,Integration vs Vertical Silos,...
```

**Status:**
- All 3 runs have exactly 6 contradictions
- All 6 rows are unique (no duplicates)
- This file is NOT affected by the bug

---

## Example 10: Before vs After Deduplication Files

**Run 20251017_142114 CSV Comparison**

before_dedup: all_gaps_before_dedup.csv
```
29 rows total
29 unique gap_ids
NO duplicates
BEFORE deduplication process
```

after_dedup: comprehensive_gaps_analysis.csv  
```
29 rows total
27 unique gap_ids
2 DUPLICATES: gap_16, gap_23
AFTER deduplication (but dedup failed)
```

**User can tell something is wrong by comparing the files:**
- "after" file has MORE rows than "before" file (conceptually wrong)
- "after" file has FEWER unique IDs than rows (proves duplicates exist)

---

## SUMMARY TABLE: All Three Runs

| Metric | Run 142114 | Run 135257 | Run 132228 |
|--------|-----------|-----------|-----------|
| Before dedup rows | 29 | 29 | 29 |
| AI says final count | 27 | 25 | 24 |
| JSON deduplicated_gaps_count | 29 | 29 | 30 |
| CSV rows (actual) | 29 | 29 | 30 |
| Unique gap_ids in CSV | 27 | 25 | 26 |
| Duplicate count | 2 | 4 | 4 |
| Reduction % reported | 0.0% | 0.0% | -3.4% |
| Contradictions | 6 | 6 | 6 |

**Pattern:** Bug is systematic and reproducible across all runs
