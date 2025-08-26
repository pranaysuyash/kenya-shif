# Integrated Comprehensive Medical Analyzer

A complete solution for analyzing Kenya's SHIF healthcare policy documents, combining proven extraction methods with AI-enhanced medical analysis.

## Overview

This analyzer processes the Kenya Social Health Insurance Fund (SHIF) tariff document to extract:
- **Pages 1-18**: Policy structure with fund hierarchies, services, tariffs, and access rules
- **Pages 19-54**: Annex surgical procedures with specialties and tariffs
- **AI Analysis**: Medical contradictions, healthcare gaps, and policy insights

## Key Features

- **Validated Extraction**: Uses exact functions from manual.ipynb for reliable data extraction
- **Dynamic Text Processing**: Intelligent de-glue algorithm for handling merged text
- **AI Enhancement**: Advanced medical reasoning for contradiction and gap analysis
- **Comprehensive Output**: Multiple CSV formats plus detailed analysis reports
- **Unique Insight Tracking**: Prevents duplicate findings across multiple runs

## File Structure

```
final_submission/
├── integrated_comprehensive_analyzer.py  # Main analyzer class
├── run_analyzer.py                      # Simple execution script
├── test_analyzer.py                     # Component testing script
├── complete_gap_extraction.py           # Standalone gap extraction function
├── missing_gap_extraction.py            # Additional gap parsing methods
└── README.md                            # This documentation
```

## Quick Start

### 1. Test the Installation
```bash
python test_analyzer.py
```

### 2. Run the Analyzer
```bash
# With default PDF (if available)
python run_analyzer.py

# With specific PDF path
python run_analyzer.py "path/to/your/SHIF_document.pdf"
```

### 3. Check Results
Results are saved to both:
- `outputs/` folder for direct access
- `outputs_run_YYYYMMDD_HHMMSS/` for timestamped runs

## Required Dependencies

### Essential
```bash
pip install pandas numpy python-dateutil
```

### For PDF Extraction (Recommended)
```bash
pip install tabula-py
# Requires Java: https://www.java.com/en/download/
```

### For AI Analysis (Optional)
```bash
pip install openai python-dotenv
```

## Output Files

### Core Data Extraction
- `rules_p1_18_structured.csv` - Policy services (main format)
- `rules_p1_18_structured_wide.csv` - Wide format with lists
- `rules_p1_18_structured_exploded.csv` - One row per service item
- `annex_surgical_tariffs_all.csv` - All surgical procedures

### AI Analysis (if enabled)
- `ai_contradictions.csv` - Detected policy contradictions
- `ai_gaps.csv` - Identified healthcare gaps
- `persistent_insights.json` - Unique findings tracker

## Configuration

### API Key Setup (Optional)
Create a `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

Or set environment variable:
```bash
export OPENAI_API_KEY="your_api_key_here"
```

## Key Functions

### Data Extraction
- **Policy Structure**: Extracts fund hierarchies, services, tariffs, access rules
- **Annex Procedures**: Surgical procedures with specialties and tariffs
- **Text Processing**: Dynamic de-glue for merged text, bullet point splitting

### AI Analysis
- **Contradiction Detection**: Medical inconsistencies using clinical expertise
- **Gap Analysis**: Missing services based on Kenya health burden data
- **Unique Tracking**: Prevents duplicate insights across runs

## Usage Examples

### Basic Analysis
```python
from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer

analyzer = IntegratedComprehensiveMedicalAnalyzer()
results = analyzer.analyze_complete_document("SHIF_document.pdf")

print(f"Extracted {results['total_policy_services']} policy services")
print(f"Extracted {results['total_annex_procedures']} procedures")
```

### With AI Analysis
```python
# Requires OpenAI API key
analyzer = IntegratedComprehensiveMedicalAnalyzer(api_key="your_key")
results = analyzer.analyze_complete_document("SHIF_document.pdf")

print(f"Found {results['total_ai_contradictions']} contradictions")
print(f"Identified {results['total_ai_gaps']} gaps")
```

## Troubleshooting

### Java/Tabula Issues
If tabula-py fails:
1. Install Java: https://www.java.com/en/download/
2. Verify: `java -version`
3. Restart terminal/IDE

### Missing Data
- Without tabula-py: Limited extraction capability
- Without OpenAI API: No AI analysis, but extraction still works

### Performance
- First run: ~30-60 seconds (builds vocabulary, caches AI responses)
- Subsequent runs: ~10-30 seconds (uses caches)

## Technical Details

### Extraction Method
- Uses exact code from manual.ipynb for validated results
- Handles fund/service hierarchies, continuation rows, merged text
- Dynamic vocabulary building for intelligent text processing

### AI Enhancement
- Real Kenya health data (WHO, KNBS, official sources)
- Clinical reasoning based on medical guidelines
- Structured output with evidence and recommendations

### Data Quality
- Deduplication of procedures and services
- Text normalization and cleaning
- Tariff extraction and validation

## Contributing

To extend the analyzer:
1. Add new extraction methods to the main class
2. Create additional AI prompts in the prompts module
3. Update output integration in `_integrate_comprehensive_results`

## Validation

The analyzer produces identical results to manual.ipynb for:
- Policy services extraction (pages 1-18)
- Annex procedures extraction (pages 19-54)
- Text processing and tariff extraction

AI analysis adds value without affecting core extraction reliability.
