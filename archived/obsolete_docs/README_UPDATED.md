# SHIF Benefits Analyzer - Contradiction Detection Tool

## Quick Start (30 seconds)
```bash
# One command analysis
python shif_analyzer.py

# View results
open outputs/SHIF_dashboard_evidence_based.xlsx
```

## What This Tool Does

Analyzes Kenya's SHIF (Social Health Insurance Fund) benefits package PDF to detect **contradiction candidates** and coverage gaps with **traceable evidence requiring validation**.

### Key Capabilities
- **Extracts** benefit rules with page-level evidence tracking
- **Flags** contradiction candidates across 4 detection categories
- **Identifies** coverage gap candidates for critical conditions  
- **Provides** evidence snippets and confidence scores requiring validation
- **Generates** structured data for expert review and validation

## Detection Methodology

### Four Contradiction Detection Types
1. **TARIFF**: Same service, different KES values
   - Example: "CT scan: KES 3,000 (Page 12) vs KES 4,500 (Page 34)"
2. **LIMIT**: Same service, different quantity limits
   - Example: "Dialysis: 2/week (Page 23) vs 3/week (Page 41)"
3. **COVERAGE**: Service listed as both included and excluded
   - Example: "MRI included (Page 15) vs excluded at Level 5 (Page 48)"
4. **FACILITY**: General coverage with facility-level exceptions
   - Example: "Surgery covered vs not available at Level 1-3"

### Evidence Tracking
- **Source Page**: Exact page number for each finding
- **Evidence Snippet**: 150-character text excerpt
- **Confidence Score**: HIGH (>90%), MEDIUM (75-90%), LOW (<75%)
- **Validation Status**: All findings require manual validation

## Current Results Summary

### Contradiction Candidates Detected: 1
✅ **Tariff variance flagged** - Requires validation
- Service: Level pricing  
- Details: KES 3,500 vs KES 5,000 variance
- Evidence: Both found on page 6
- Status: **PENDING VALIDATION**

### Coverage Gap Candidates: 3
✅ **High-priority gaps identified** - Require review
- **Stroke rehabilitation**: No comprehensive coverage found
- **Chronic kidney disease**: Minimal coverage detected (1 service)
- **Mental health**: Minimal coverage detected (1 service)

### Validation Requirements

**CRITICAL**: All findings are candidates requiring validation:
1. Review evidence snippets against source pages
2. Confirm contradiction classifications with domain experts
3. Validate gap assessments with clinical teams
4. Prioritize based on patient impact and confidence scores

## Technical Approach

### Core Technology
- **PDF Processing**: pdfplumber with table extraction
- **Text Analysis**: Regex patterns + fuzzy matching
- **Evidence Chain**: Page tracking + snippet extraction
- **Output Format**: Excel dashboard with validation fields

### Current Limitations
Current prototype limitations requiring acknowledgment:
- **Table parsing**: Basic extraction (production requires Camelot/Tabula)
- **OCR capability**: None (would add Tesseract for scanned pages)
- **Language support**: English-only (would add Swahili)
- **Validation workflow**: Manual validation required for ALL findings
- **Service normalization**: May produce false positives requiring review

## Installation

### Requirements
```bash
pip install -r requirements.txt
```

### Optional Enhancements
```bash
# For advanced table extraction
pip install camelot-py[cv] tabula-py

# For OCR capabilities  
pip install pytesseract

# For OpenAI enhancement
pip install openai
```

## Usage Options

### 1. Command Line (Fastest)
```bash
# Basic analysis
python shif_analyzer.py

# Custom PDF
python shif_analyzer.py --file your_pdf.pdf

# With OpenAI enhancement
python shif_analyzer.py --openai-key YOUR_KEY
```

### 2. Streamlit Dashboard (Interactive)
```bash
streamlit run shif_analyzer.py -- --streamlit
```

### 3. Python Import
```python
from shif_analyzer import parse_pdf_with_pdfplumber, detect_contradictions_v2

# Analyze PDF
rules_df = parse_pdf_with_pdfplumber("shif.pdf")
contradictions_df = detect_contradictions_v2(rules_df)
```

## Output Files

### Excel Dashboard (`SHIF_dashboard_evidence_based.xlsx`)
- **Executive Summary**: Key metrics and findings requiring validation
- **Methodology**: Detection approach and limitations
- **Rules**: All extracted rules with evidence
- **Contradictions**: Flagged candidates with validation fields
- **Gaps**: Coverage gap candidates with risk assessment

### CSV Files (with evidence columns)
- `rules.csv` - All extracted rules with evidence
- `contradictions.csv` - Contradiction candidates requiring validation
- `gaps.csv` - Coverage gap candidates for review

## Validation Process

**MANDATORY**: All findings require validation before action:
1. **Evidence Review**: Check snippets against source pages
2. **Domain Validation**: Confirm with healthcare policy experts
3. **Clinical Review**: Assess gap priorities with medical teams
4. **Financial Analysis**: Validate any impact assessments
5. **Quality Assurance**: Review confidence scores and edge cases

## Business Value Proposition

### Process Improvements
- **Analysis acceleration**: Manual review time reduced for initial flagging
- **Systematic coverage**: Reduces risk of missed contradictions in manual review
- **Evidence tracking**: Full traceability for validation workflows
- **Structured output**: Standardized format for reviewer assessment

### Operational Benefits
- **Dispute preparedness**: Evidence-based contradiction analysis
- **Policy improvement**: Systematic gap identification
- **Quality assurance**: Repeatable detection methodology

## About This Solution

**Context**: Product-focused prototype demonstrating systematic contradiction detection with evidence tracking for healthcare policy analysis.

**Approach**: Balances automation capabilities with validation requirements - accelerates initial detection while maintaining evidence rigor.

**Philosophy**: A detection tool that transforms unstructured policy documents into structured validation workflows.

## Important Disclaimers

- **All findings require validation** by domain experts before any action
- **Financial impact estimates** require separate actuarial analysis
- **Clinical assessments** must be validated by healthcare professionals
- **Policy decisions** should not be made solely based on tool outputs

---

*Developed as a healthcare operations tool prototype with validation-first approach*