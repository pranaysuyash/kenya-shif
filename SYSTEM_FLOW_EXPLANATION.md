# Kenya SHIF Healthcare Policy Analyzer - System Flow & Explanation

---

## 1. High-Level Flow (Non-Technical)

**User Journey:**

1. **Start with the PDF**: User provides the official SHIF benefit package PDF (`TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf`).
2. **Run Analysis**: User launches the Streamlit dashboard (`streamlit_comprehensive_analyzer.py`).
3. **Extraction & Analysis**: System extracts all healthcare services, detects contradictions, finds gaps, and provides AI-powered insights.
4. **View Results**: User sees interactive charts, tables, and can download all results (CSV, ZIP, JSON).
5. **Historical Access**: User can browse previous runs, load old results, or provide a custom path to restore history.
6. **Deployment**: Works locally, on Replit, Vercel, or Streamlit Cloud. Downloads are always available.

---

## 2. Technical Flow (File-by-File)

### **A. Entry Point: `streamlit_comprehensive_analyzer.py`**

- **Role**: Main dashboard UI. Handles user interaction, file uploads, analysis triggers, and visualization.
- **Flow:**
  1. Loads environment variables and sets up OpenAI client.
  2. Imports analyzers (`integrated_comprehensive_analyzer.py`, `shif_healthcare_pattern_analyzer.py`).
  3. Presents sidebar controls (run extraction, load results, enable AI, etc).
  4. User triggers analysis (pattern-based or AI-enhanced).
  5. Calls analyzer to process PDF and generate results.
  6. Displays results in 6 main tabs:
     - Dashboard Overview
     - Task 1: Structured Rules
     - Task 2: Contradictions & Gaps
     - Task 3: Kenya Context
     - Advanced Analytics (includes Downloads & Historical)
     - AI Insights
  7. Handles downloads, historical browsing, and custom path input via OutputManager/DownloadManager.

### **B. Core Analysis: `integrated_comprehensive_analyzer.py`**

- **Role**: Main engine for PDF extraction, AI analysis, contradiction/gap detection, and context integration.
- **Flow:**
  1. Loads PDF and builds vocabulary for text processing.
  2. Extracts policy services (pages 1-18) and annex procedures (pages 19-54) using Tabula and custom logic.
  3. Runs AI-powered contradiction and gap analysis (OpenAI, deterministic settings).
  4. Integrates Kenya-specific health context and epidemiology.
  5. Saves all results (CSV, JSON) in timestamped output folders.
  6. Tracks unique insights across runs (UniqueInsightTracker).
  7. Returns results to Streamlit app for visualization and download.

### **C. Pattern-Based Analysis: `shif_healthcare_pattern_analyzer.py`**

- **Role**: Non-AI fallback analyzer. Uses regex/patterns to extract, structure, and analyze data.
- **Flow:**
  1. Extracts rules and procedures using pattern matching.
  2. Detects contradictions and gaps using rule comparison.
  3. Integrates Kenya/SHIF domain knowledge.
  4. Saves results in output folders for dashboard access.
  5. Used when OpenAI quota is exceeded or for fast, offline analysis.

### **D. Output Management: `output_manager.py`**

- **Role**: Handles all file operations, downloads, ZIP creation, and historical browsing.
- **Flow:**
  1. Creates timestamped output directories for each run.
  2. Saves DataFrames and JSONs to disk (local) or memory (cloud).
  3. Provides download buttons for CSV, JSON, ZIP (via Streamlit UI).
  4. Lists all previous runs and loads historical data.
  5. Allows user to specify custom path for restoring history.
  6. Works seamlessly across local/cloud platforms.

### **E. Download & Historical Features (UI)**

- **Role**: User-facing features for exporting results and browsing history.
- **Flow:**
  1. Downloads tab: Export individual CSVs, complete ZIP, or save locally.
  2. Historical tab: Browse all previous runs, view summaries, load any run, or input custom path.
  3. All features work on local, Replit, Vercel, and Streamlit Cloud.

---

## 3. Data Flow (Step-by-Step)

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

## 4. Deployment & Platform Support

- **Local**: Full features, persistent storage, all history available.
- **Replit**: Ephemeral storage, must download results before session ends.
- **Vercel**: No persistent storage, download-only model, history restored via upload.
- **Streamlit Cloud**: Session-only storage, download-only model.

---

## 5. User & Technical Explanation (Q&A Style)

### **Q: Where do I start?**

- Run `streamlit_comprehensive_analyzer.py` and upload the PDF.

### **Q: What happens after I upload the PDF?**

- The system extracts all services and procedures, analyzes for contradictions/gaps, and integrates Kenya context.

### **Q: How do I get the results?**

- Results are shown in the dashboard and can be downloaded as CSV, JSON, or ZIP. All files are saved in `outputs/`.

### **Q: Can I see previous analyses?**

- Yes! Use the Historical tab to browse all previous runs or load any output folder.

### **Q: What if I'm on Replit or Vercel?**

- Download results immediately. History can be restored by uploading previous ZIPs.

### **Q: Is the AI analysis deterministic?**

- Yes. All OpenAI calls use `temperature=0` and `seed=42` for reproducible results.

### **Q: What files should I look at for technical details?**

- Main flow: `streamlit_comprehensive_analyzer.py`, `integrated_comprehensive_analyzer.py`, `output_manager.py`, `shif_healthcare_pattern_analyzer.py`.

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

## 7. Key Takeaways

- **Start with Streamlit app, upload PDF, run analysis.**
- **All results are downloadable and saved in timestamped folders.**
- **Historical runs and custom path loading are supported everywhere.**
- **Works on all platforms, with deterministic AI analysis.**
- **Technical and non-technical users can both use and explain the flow easily.**

---

## 8. For Assignment/Interview Prep

- **Explain the flow from user and technical perspective.**
- **Highlight platform support and deterministic outputs.**
- **Show how historical and download features work.**
- **Reference main files for technical deep dive.**

---

## 9. References

- See `README.md`, `IMPLEMENTATION_SUMMARY.md`, and `DEPLOYMENT_GUIDE.md` for more details.

---
