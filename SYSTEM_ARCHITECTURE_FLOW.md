# Kenya SHIF Healthcare Policy Analyzer - System Architecture & Flow

---

## 1. Overview

This system analyzes the Kenya Social Health Insurance Fund (SHIF) benefit package PDF to extract healthcare services, detect contradictions, identify coverage gaps, and provide AI-powered insights. It is designed for robust, reproducible analysis and works across local and cloud platforms.

---

## 2. Main Functionalities

- **PDF Extraction**: Reads and processes the official SHIF benefit package PDF.
- **Service Structuring**: Structures all healthcare services and procedures into clean, analyzable formats.
- **Contradiction Detection**: Identifies policy contradictions (e.g., facility, tariff, coverage).
- **Gap Analysis**: Detects missing or insufficient coverage areas using Kenya-specific health context.
- **AI-Enhanced Insights**: Uses OpenAI for advanced contradiction/gap analysis (deterministic outputs).
- **Interactive Dashboard**: Streamlit app for visualization, downloads, and historical browsing.
- **Output Management**: Saves all results in timestamped folders, supports downloads (CSV, JSON, ZIP), and historical access.
- **Platform Support**: Works locally, on Replit, Vercel, and Streamlit Cloud.

---

## 3. File-by-File Architecture

### **A. `streamlit_comprehensive_analyzer.py`**

- **Role**: Main dashboard UI and entry point.
- **Responsibilities**:
  - Loads environment variables and sets up OpenAI client.
  - Imports analyzers and output manager utilities.
  - Presents sidebar controls for running analysis, loading results, and enabling AI.
  - Handles user interaction, analysis triggers, and visualization.
  - Displays results in multiple tabs (Dashboard, Structured Rules, Contradictions & Gaps, Kenya Context, Advanced Analytics, AI Insights).
  - Manages downloads and historical browsing via OutputManager/DownloadManager.

### **B. `integrated_comprehensive_analyzer.py`**

- **Role**: Main engine for PDF extraction and AI analysis.
- **Responsibilities**:
  - Loads and processes the PDF using Tabula and custom logic.
  - Extracts policy services and annex procedures.
  - Runs AI-powered contradiction and gap analysis (OpenAI, deterministic settings).
  - Integrates Kenya-specific health context and epidemiology.
  - Tracks unique insights across runs.
  - Saves all results in timestamped output folders.

### **C. `shif_healthcare_pattern_analyzer.py`**

- **Role**: Pattern-based, non-AI fallback analyzer.
- **Responsibilities**:
  - Extracts and structures rules and procedures using regex/patterns.
  - Detects contradictions and gaps using rule comparison.
  - Integrates Kenya/SHIF domain knowledge.
  - Saves results for dashboard access.
  - Used when OpenAI quota is exceeded or for fast, offline analysis.

### **D. `output_manager.py`**

- **Role**: Output management and historical access utility.
- **Responsibilities**:
  - Creates timestamped output directories for each run.
  - Saves DataFrames and JSONs to disk (local) or memory (cloud).
  - Provides download buttons for CSV, JSON, ZIP (via Streamlit UI).
  - Lists previous runs and loads historical data.
  - Allows user to specify custom path for restoring history.
  - Works seamlessly across local/cloud platforms.

---

## 4. Data Flow

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

## 5. Platform Support

- **Local**: Full features, persistent storage, all history available.
- **Replit**: Ephemeral storage, must download results before session ends.
- **Vercel**: No persistent storage, download-only model, history restored via upload.
- **Streamlit Cloud**: Session-only storage, download-only model.

---

## 6. Visual Flow Diagram (Text)

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

## 7. References

- See `README.md`, `IMPLEMENTATION_SUMMARY.md`, and `DEPLOYMENT_GUIDE.md` for more details.

---
