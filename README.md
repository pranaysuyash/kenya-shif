# Kenya SHIF Healthcare Policy Analyzer

## System Overview

This system analyzes the Kenya Social Health Insurance Fund (SHIF) benefit package document to extract healthcare services, detect contradictions, identify coverage gaps, and provide AI-enhanced insights.

## Key Components

1. **Integrated Comprehensive Medical Analyzer** - Main extraction and analysis engine
2. **SHIF Healthcare Pattern Analyzer** - Non-AI fallback analysis
3. **Streamlit Dashboard** - Interactive visualization interface
4. **Deterministic Checker** - Validation without AI dependencies

## Data Flow & Storage

### Fresh Extraction Output

When you run a fresh analysis:

1. PDF is extracted and analyzed
2. All results are saved to a timestamped folder: `outputs_run_YYYYMMDD_HHMMSS/`
3. Contains: `rules_p1_18_structured.csv`, `annex_procedures.csv`, `ai_contradictions.csv`, `ai_gaps.csv`, etc.

### Data Loading Priority

In `load_existing_results()`:

```text
PRIORITY 1: Fresh CSV Data from Latest Run
- Searches for most recent outputs_run_*/ folder
- Loads: rules_p1_18_structured.csv (policy services)
- Loads: annex_procedures.csv (annex procedures)
- Sets source_type = 'fresh_extraction_csv'
- Syncs to session state for persistence

PRIORITY 2: Historical JSON Archive (Fallback)
- Only if no fresh run found
- Loads from: outputs_generalized/generalized_complete_analysis.json
- Sets source_type = 'historical_archive'
```

### Usage Scenarios

#### Scenario 1: First Run

- Click "Run Fresh Analysis" → PDF extracted → `outputs_run_20251017_112838/`
- Analysis completes → 97 policy + 728 annex = 825 services
- Results displayed in tabs → Session state persists data

#### Scenario 2: Load Previous Results

- Click "Load Existing Results"
- System checks latest `outputs_run_*/` folder
- Loads fresh CSVs if found (825 services)
- Falls back to historical JSON if no fresh run (629 services from old extraction)
- Data persists in session across tab switches

#### Scenario 3: Multiple Runs

- First run → `outputs_run_20251017_112838/` → 825 services loaded
- Switch tabs → Data persists via `st.session_state`
- Run fresh analysis again → `outputs_run_20251017_120000/` (new folder)
- Click Load Existing → Loads from new folder automatically

## Prerequisites

- Python 3.8+
- Java (for tabula PDF extraction)
- Virtual environment with required packages
- OpenAI API key (for AI analysis)

## Quick Start

1. Ensure the PDF is named: `TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf`
2. Activate virtual environment: `source .venv/bin/activate`
3. Run analysis: `python run_analyzer.py`
4. View dashboard: `streamlit run streamlit_comprehensive_analyzer.py`

## Output Files

All fresh results are saved in timestamped folders `outputs_run_YYYYMMDD_HHMMSS/`:

- `rules_p1_18_structured.csv` - 97 policy services
- `annex_procedures.csv` - 728 annex procedures
- `ai_contradictions.csv` - Detected policy contradictions
- `ai_gaps.csv` - Identified coverage gaps
- `integrated_comprehensive_analysis.json` - Complete analysis
- `analysis_summary.csv` - Summary metrics

Historical data is stored in `outputs_generalized/` for fallback access.

## Accessing Results

- **Streamlit Dashboard**: http://localhost:8501
- **Fresh CSV Data**: `outputs_run_*/` folders (latest = most recent run)
- **Direct CSV Access**: `rules_p1_18_structured.csv`, `annex_procedures.csv`
- **Complete JSON**: `outputs_run_*/integrated_comprehensive_analysis.json`
- **Deterministic Validation**: `python deterministic_checker.py` (shows current counts)

## Analysis Capabilities

## System Architecture & Flow

---

### Main Functionalities

- **PDF Extraction**: Reads and processes the official SHIF benefit package PDF.
- **Service Structuring**: Structures all healthcare services and procedures into clean, analyzable formats.
- **Contradiction Detection**: Identifies policy contradictions (e.g., facility, tariff, coverage).
- **Gap Analysis**: Detects missing or insufficient coverage areas using Kenya-specific health context.
- **AI-Enhanced Insights**: Uses OpenAI for advanced contradiction/gap analysis (deterministic outputs).
- **Interactive Dashboard**: Streamlit app for visualization, downloads, and historical browsing.
- **Output Management**: Saves all results in timestamped folders, supports downloads (CSV, JSON, ZIP), and historical access.
- **Platform Support**: Works locally, on Replit, Vercel, and Streamlit Cloud.

---

### File-by-File Architecture

#### `streamlit_comprehensive_analyzer.py`

- Main dashboard UI and entry point.
- Loads environment variables and sets up OpenAI client.
- Imports analyzers and output manager utilities.
- Presents sidebar controls for running analysis, loading results, and enabling AI.
- Handles user interaction, analysis triggers, and visualization.
- Displays results in multiple tabs (Dashboard, Structured Rules, Contradictions & Gaps, Kenya Context, Advanced Analytics, AI Insights).
- Manages downloads and historical browsing via OutputManager/DownloadManager.

#### `integrated_comprehensive_analyzer.py`

- Main engine for PDF extraction and AI analysis.
- Loads and processes the PDF using Tabula and custom logic.
- Extracts policy services and annex procedures.
- Runs AI-powered contradiction and gap analysis (OpenAI, deterministic settings).
- Integrates Kenya-specific health context and epidemiology.
- Tracks unique insights across runs.
- Saves all results in timestamped output folders.

#### `shif_healthcare_pattern_analyzer.py`

- Pattern-based, non-AI fallback analyzer.
- Extracts and structures rules and procedures using regex/patterns.
- Detects contradictions and gaps using rule comparison.
- Integrates Kenya/SHIF domain knowledge.
- Saves results for dashboard access.
- Used when OpenAI quota is exceeded or for fast, offline analysis.

#### `output_manager.py`

- Output management and historical access utility.
- Creates timestamped output directories for each run.
- Saves DataFrames and JSONs to disk (local) or memory (cloud).
- Provides download buttons for CSV, JSON, ZIP (via Streamlit UI).
- Lists previous runs and loads historical data.
- Allows user to specify custom path for restoring history.
- Works seamlessly across local/cloud platforms.

---

### Data Flow

1. **PDF Ingestion**: PDF is loaded by analyzer (Tabula for tables, custom text logic for complex pages).
2. **Extraction**: Services and procedures are extracted into DataFrames.
3. **Structuring**: Data is cleaned, structured, and mapped to healthcare rules.
4. **Analysis**:
   - Contradictions detected by comparing rules (facility, tariff, coverage).
   - Gaps identified by matching against Kenya health context and epidemiology.
   - AI-enhanced analysis uses OpenAI (deterministic: temperature=0, seed=42).
5. **Results Saving**: All outputs saved in timestamped folders (`outputs_run_YYYYMMDD_HHMMSS`).
6. **Visualization**: Streamlit app displays metrics, charts, tables, and summaries.
7. **Download/Export**: User can download any result (CSV, JSON, ZIP) or save locally.
8. **Historical Access**: User can browse previous runs, load any folder, or restore from ZIP.

---

### Platform Support

- **Local**: Full features, persistent storage, all history available.
- **Replit**: Ephemeral storage, must download results before session ends.
- **Vercel**: No persistent storage, download-only model, history restored via upload.
- **Streamlit Cloud**: Session-only storage, download-only model.

---

### Visual Flow Diagram

```
[User] → [Streamlit Dashboard]
	    ↓
    [PDF Upload]
	    ↓
    [Analyzer: integrated_comprehensive_analyzer.py]
	    ↓
    [Extraction & AI Analysis]
	    ↓
    [OutputManager: Save Results]
	    ↓
    [Dashboard: Show Results]
	    ↓
    [Downloads Tab] ←→ [Historical Tab]
	    ↓
    [User Downloads/Restores History]
```

---

### References

- See `IMPLEMENTATION_SUMMARY.md` and `DEPLOYMENT_GUIDE.md` for more details.
