# Kenya SHIF Analyzer — Streamlit App User Guide

This guide explains the Streamlit app’s features, inputs, outputs, and how each section works. The app provides an end‑to‑end workflow for extracting data from the SHIF PDF, running Kenya‑aware AI analyses, and exporting results for downstream use.

## Overview
- Purpose: Extract and analyze SHIF healthcare policy content with robust PDF table handling and clinical AI.
- Core Flow: Extract from PDF → compute contradictions/gaps → extended AI → visualize → export CSV/JSON/ZIP.
- Default PDF: `TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf` in the repo root.

## Inputs
- PDF File: The default PDF is used automatically (see top banner). Place it at the repo root.
- OpenAI API Key: Load via `.env` (`OPENAI_API_KEY`) or environment variable. Required for AI insights.
- Scenario Text (optional): Used by predictive analysis in the AI Insights tab.
- Cached Results: The app can load prior runs from the `outputs/` or timestamped `outputs_run_*` folders.

## Sidebar Controls
- PDF Status: Confirms the SHIF PDF is present and shows file size.
- Run Complete Extraction: Legacy, pattern‑based workflow (no AI required). Produces base CSV/JSON.
- Run Pattern Analysis: Alias of the legacy path above.
- Run Integrated Analyzer (Extended AI): Recommended path. Runs validated extraction (pages 1–18 and annex) and extended AI analyses, then saves CSV/JSON and a ZIP bundle.
- Load Existing Results: Loads prior outputs into the UI.
- OpenAI Status: Shows client availability and model fallback readiness.

## Tabs and What They Do

### 1) Dashboard Overview
- Shows KPIs and a quick status (services, contradictions, coverage gaps, tariff coverage).
- Provides a “Download Generated Files” section for CSV/JSON/ZIP outputs (both legacy and integrated pipelines).

### 2) Task 1: Structured Rules
- Displays services/rules parsed from the PDF with facility levels, tariffs, and rule complexity.
- Charts: Facility level distribution, payment methods, rule complexity.
- Download: “Structured Rules CSV.”

### 3) Task 2: Contradictions & Coverage Gaps
- Summarizes contradictions and gaps with severity/impact charts.
- Highlights high‑severity contradictions and high‑impact gaps.

### 4) Task 3: Kenya/SHIF Context Integration
- Kenya system context scaffolding and analysis hooks (6‑tier system, 47 counties, disease burden alignment).

### 5) Advanced Analytics
- Tariff distribution charts (histogram, cost buckets).
- Specialty coverage and averages.
- Rule complexity and “policy coherence” metrics.

### 6) AI‑Powered Insights
- Analyze Contradictions: Produces a clinical narrative on contradictions found. Persists to `ai_contradictions.md`. If the AI returns JSON‑like structures, the app also writes CSVs for parsed content.
- Analyze Coverage Gaps: Medical prioritization of gaps. Persists to `ai_gaps.md` and CSVs (if parseable).
- Kenya‑Specific Insights: Narrative insights tailored to Kenya’s context. Persists to `kenya_insights.md`.
- Executive Policy Recommendations: Uses updated prompts. Renders JSON if possible; persists to `executive_recommendations.json` + CSV breakdowns.
- Predictive Scenario Analysis: Enter a scenario, receive projections. Persists to `predictive_analysis.json` + CSV breakdowns.
- Integrated Extended AI Outputs: Shows JSON outputs produced during the integrated run — annex quality/outliers, rules contradiction map, batch service analysis, section summaries, name canonicalization, facility‑level validation, policy–annex alignment, and equity analysis.

## Integrated Analyzer (Recommended)
When you click “Run Integrated Analyzer (Extended AI)” in the sidebar:

1. Pages 1–18 Extraction
   - Validated detection of rule headers (“Scope | Access Point | Tariff | Access Rules”).
   - Multi‑line row merging and numeric tariff parsing.

2. Annex (Pages 19–54) Extraction
   - Validated Simple Tabula pipeline with “pre‑number continuation” handling.
   - Cleans and normalizes tariffs to numeric.

3. Extended AI Analyses
   - Annex Quality & Outliers (pricing anomalies, duplicates).
   - Rules Contradiction Map (fund/section view).
   - Batch Service Analysis (facility fit, risk/adequacy) in chunks.
   - Section Summaries; Name Canonicalization; Facility‑Level Validation; Policy–Annex Alignment; Equity Analysis.

4. Exports and Caching
   - JSON: `integrated_comprehensive_analysis.json`, `extended_ai.json`, `even_more_ai.json`.
   - CSV: `policy_structured.csv`, `annex_procedures.csv`, plus CSV breakdowns for AI outputs.
   - ZIP: `integrated_outputs.zip` contains all CSV/JSON.
   - AI caching in `ai_cache/` prevents repeat costs; panels also reuse saved JSON/MD/CSV where possible.

## Downloads
- Legacy (pattern) files under `outputs/` appear in “Download Generated Files.”
- Integrated outputs live in a timestamped `outputs_run_YYYYMMDD_HHMMSS/` and include:
  - `integrated_comprehensive_analysis.json`
  - `policy_structured.csv`, `annex_procedures.csv`
  - `extended_ai.json`, `even_more_ai.json` (+ CSV breakouts)
  - `executive_recommendations.json`, `predictive_analysis.json` (+ CSV breakouts)
  - `ai_contradictions.md`, `ai_gaps.md`, `kenya_insights.md`
  - `integrated_outputs.zip`

## Inputs/Outputs by Panel (Quick Reference)
- Input (global): SHIF PDF, API key.
- Structured Rules: Input = extracted tables; Output = charts + `structured_rules.csv`.
- Contradictions/Gaps: Input = parsed rules; Output = charts + summaries; AI panels create `.md` and CSV where parseable.
- Executive/Predictions: Input = summaries + scenario; Output = JSON/CSV.

## Troubleshooting
- Missing PDF: Add the SHIF PDF to repo root.
- Missing API Key: Set `OPENAI_API_KEY` in `.env`.
- Tabula/Java issues: The integrated pipeline handles missing Tabula gracefully; ensure Java is installed for optimal annex extraction.
- AI errors: The app shows warnings and reuses cached/saved results when available.

## Performance & Cost Notes
- AI calls are cached (model + prompt + tag) and saved; re‑runs often read from disk instead of calling the API.
- Extended AI uses sampled subsets (e.g., 40–60 rows per chunk) to keep tokens reasonable while producing actionable results.

## Customization
- Prompt suite: `updated_prompts.py` — adjust or add templates.
- Exports: Streamlit app writes CSVs for JSON structures with a normalizer; extend `_write_structured_csvs` for new shapes.
- Charts: Tune Plotly themes in the view functions if needed.

---
For a PDF version with screenshots per tab, ask to generate a “Step‑by‑Step Illustrated Guide.”

