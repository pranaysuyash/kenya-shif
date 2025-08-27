# Kenya SHIF Healthcare Policy Analyzer – ChatGPT Verification Packet

**Repository:** https://github.com/pranaysuyash/kenya-shif  
**Branch:** main  
**Date:** 2025-08-27 (IST)  
**Status:** SUBMISSION MODE - Current Run Counts (Not Cumulative)

## 0) One-time Setup
```bash
git clone https://github.com/pranaysuyash/kenya-shif.git
cd kenya-shif
python -V
pip install -r requirements.txt  # or uv/pipx, as you prefer
# Ensure the PDF exists in repo root:
ls -la | grep -i "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
```

If using AI features, create .env:
```bash
OPENAI_API_KEY=sk-...
```

## 1) "Submission Mode" to avoid cumulative counts

Your tracker accumulates insights across runs. For assignment numbers, use current run only:

```bash
# Submission mode: clear cumulative store
rm -f persistent_insights.json
```

Now the "dedup()" represents only this run.

## 2) Core Extraction Parity

**Goal:** manual/"simple" → 31 rows (raw) and integrated → 97 structured services, with clean text.

```bash
# Run simple extraction (produces 31 rows)
python simple_working_extraction.py

# Run integrated analyzer (produces 97 structured services, 728 annex procedures)
python integrated_comprehensive_analyzer.py
```

Verify counts and the fixed phrase:

```bash
# Find latest outputs folder
LATEST=$(ls -dt outputs_run_* | head -1)

# 31 raw services (minus header)
RAW_COUNT=$(($(wc -l < "$LATEST/rules_p1_18_raw.csv") - 1))
echo "RAW services: $RAW_COUNT"  # Expect 31

# 97 structured services (minus header)
STRUCT_COUNT=$(($(wc -l < "$LATEST/rules_p1_18_structured.csv") - 1))
echo "STRUCTURED services: $STRUCT_COUNT"  # Expect 97

# 728 annex procedures (minus header)
ANNEX_COUNT=$(($(wc -l < "$LATEST/annex_procedures.csv") - 1))
echo "ANNEX procedures: $ANNEX_COUNT"  # Expect 728

# Text quality: target sentence must exist at least once
grep -F "Health education and wellness, counselling, and ongoing support as needed" "$LATEST"/rules_p1_18_*csv && echo "✅ Phrase OK"
```

**Pass criteria:** 31, 97, 728, and ✅ phrase printed.

## 3) AI Analysis + Intelligent Dedup

Run (already done above) and verify current-run counts:

```bash
# AI gaps from current run (before deduplication)
jq -r '.ai_analysis.gaps | length' "$LATEST/integrated_comprehensive_analysis.json"
# Expected: 6

# Coverage gaps from current run 
jq -r '.coverage_analysis | length' "$LATEST/integrated_comprehensive_analysis.json"
# Expected: 20

# Final deduplicated gaps (current run)
DEDUP_COUNT=$(($(wc -l < "$LATEST/comprehensive_gaps_analysis.csv") - 1))
echo "Deduped gaps (current run): $DEDUP_COUNT"   # Expected: 20 (6 clinical + 20 coverage → dedup to 20)

# Contradictions from current run
jq -r '.ai_analysis.contradictions | length' "$LATEST/integrated_comprehensive_analysis.json"
# Expected: 7

# If needed: view dedup analysis provenance
ls "$LATEST/gaps_deduplication_analysis.json" && head -n 20 "$LATEST/gaps_deduplication_analysis.json"
```

**Note on discrepancies:**
- Current run numbers should be used for submission
- If you don't delete persistent_insights.json, your reports will show cumulative counts across historical runs
- **CORRECTED NUMBERS (Submission Mode):**
  - Raw services: **31**
  - Structured services: **97**  
  - Annex procedures: **728**
  - AI Gaps (current run): **20** (after deduplication)
  - AI Contradictions (current run): **7**

## 4) Deterministic Validators (Non-AI)

You must always find:
- Dialysis contradiction (frequency / coverage inconsistency)
- Hypertension gap (listed disease without mapped treatment coverage)

Verify artifacts:
```bash
# Search for dialysis and hypertension in analysis
grep -i "dialysis\|hypertension" "$LATEST/integrated_comprehensive_analysis.json" | head -5

# Expected to find mentions like:
# "Policy permits 3 haemodialysis (HD) sessions/week but restricts haemodiafiltration (HDF) to only 2 sessions/week"
```

## 5) Streamlit Dashboard Parity

First, ensure Streamlit has the correct data structure:
```bash
# Fix data structure for Streamlit
python fix_streamlit_data.py
```

Start the app:
```bash
streamlit run streamlit_comprehensive_analyzer.py
```

In the UI, verify:
- **Header metrics:** Services = 97, Procedures = 728, Gaps = 20, Contradictions = 7 (current run)
- **Tabs:**
  - Rules parsed: table lists 97 services; search finds the "Health education and wellness…" phrase
  - Contradictions: dialysis shows as High severity
  - Gaps: 20 gaps with various categories
- **Charts:**
  - Gap distribution by category
  - Cost/fund breakdown (from structured rules)
  - Risk/Severity histogram (AI outputs)
- **Exports:** CSV/PNG available; saved into the latest outputs folder

## 6) Security & Hygiene
```bash
# No hardcoded API keys in repo
grep -R "sk-[A-Za-z0-9]" -n || echo "✅ No API keys found"

# .env, outputs ignored
grep -E "(\.env|outputs_run_|__pycache__)" .gitignore && echo "✅ .gitignore OK"
```

## 7) Expected Numbers (Submission Mode - CORRECTED)

- **31** raw policy services
- **97** structured services  
- **728** annex procedures
- **20** gaps (deduplication, current run)
- **7** contradictions (current run)
- **Dialysis contradiction:** FOUND
- **Hypertension gap:** Present in analysis
- **Clean text phrase:** "Health education and wellness, counselling, and ongoing support as needed" - FOUND

## 8) Key Files for Verification

**Latest Run:** `outputs_run_20250827_222553/`

**Core Data Files:**
- `rules_p1_18_raw.csv` - 31 raw services
- `rules_p1_18_structured.csv` - 97 structured services  
- `annex_procedures.csv` - 728 procedures
- `comprehensive_gaps_analysis.csv` - 20 unique gaps (current run)
- `integrated_comprehensive_analysis.json` - Complete analysis with 7 contradictions

**Streamlit Data:**
- `outputs/shif_healthcare_pattern_complete_analysis.json` - Streamlit-compatible format

## Final Notes

✅ **All claims now match actual data**  
✅ **Submission mode prevents cumulative count confusion**  
✅ **Text processing fully functional with clean output**  
✅ **Both simple and integrated extractors work correctly**  
✅ **Streamlit dashboard operational with correct data mapping**  
✅ **AI analysis producing clinically relevant gaps and contradictions**  
✅ **Deterministic validators finding required examples (dialysis, hypertension)**  

**TL;DR Verification Commands:**
```bash
# Quick verification (after git clone and setup)
rm -f persistent_insights.json  # Submission mode
python simple_working_extraction.py  # Should show 31 rows
python integrated_comprehensive_analyzer.py  # Should show 97 structured, 728 procedures
LATEST=$(ls -dt outputs_run_* | head -1)
echo "Services: $(($(wc -l < "$LATEST/rules_p1_18_structured.csv") - 1))"  # 97
echo "Procedures: $(($(wc -l < "$LATEST/annex_procedures.csv") - 1))"  # 728
echo "Gaps: $(($(wc -l < "$LATEST/comprehensive_gaps_analysis.csv") - 1))"  # 20
grep -c dialysis "$LATEST/integrated_comprehensive_analysis.json"  # Should find dialysis
python fix_streamlit_data.py && streamlit run streamlit_comprehensive_analyzer.py  # Dashboard
```

---
**Validation Status:** ✅ VERIFIED  
**Numbers Corrected:** ✅ Match between claims and actual output  
**Ready for Submission:** ✅ All components functional