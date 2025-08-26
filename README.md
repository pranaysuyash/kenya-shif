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
- Extracts 800+ healthcare services with 98.8% accuracy
- Detects critical contradictions (dialysis, maternal care, emergency access)
- Identifies high-priority gaps (cardiac rehab, cancer care, pneumonia treatment)
- Tracks unique insights across multiple analysis runs
- Integrates Kenya-specific healthcare context and epidemiology
