# Kenya SHIF Healthcare Policy Analyzer

## System Overview

This system analyzes the Kenya Social Health Insurance Fund (SHIF) benefit package document to extract healthcare services, detect contradictions, identify coverage gaps, and provide AI-enhanced insights.

## Key Components

1. **Integrated Comprehensive Medical Analyzer** - Main extraction and analysis engine
2. **SHIF Healthcare Pattern Analyzer** - Non-AI fallback analysis
3. **Streamlit Dashboard** - Interactive visualization interface
4. **Deterministic Checker** - Validation without AI dependencies

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

All results are saved in the `outputs/` directory:

- `rules_p1_18_structured.csv` - Structured policy services
- `annex_procedures.csv` - Annex surgical procedures
- `ai_contradictions.csv` - Detected policy contradictions
- `ai_gaps.csv` - Identified coverage gaps
- Timestamped folders contain complete analysis results

## Accessing Results

- **Streamlit Dashboard**: http://localhost:8504
- **Direct CSV Access**: Files in `outputs/` directory
- **Complete JSON**: `outputs/integrated_comprehensive_analysis.json`

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
