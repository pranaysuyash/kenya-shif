# Expert Validation Interfaces

Two validation interfaces for healthcare experts to review SHIF analyzer extractions:

## 🖥️ Streamlit Web Interface

Interactive web-based validation with visual analytics.

```bash
# Install streamlit if needed
pip install streamlit

# Run the interface
streamlit run expert_validation_interface.py
```

**Features:**
- Progress tracking with visual metrics
- Individual rule validation with context
- Evidence snippet display
- Batch review capabilities  
- Real-time analytics dashboard
- Auto-save validation progress

## 💻 Command Line Interface

Terminal-based validation for experts who prefer CLI tools.

```bash
# Run validation on rules file
python expert_validation_cli.py rules.csv
```

**Features:**
- Step-by-step validation workflow
- Formatted rule display with evidence
- Built-in progress tracking
- Session statistics
- Correction input for incorrect extractions

## Output Files

Both interfaces generate:
- `expert_validations.jsonl` - Individual validation records
- `validation_progress.json` - Progress tracking
- Validation statistics and analytics

## Validation Outcomes

- **Correct Extraction** - Rule is accurate as extracted
- **Partially Correct** - Some fields correct, others need adjustment
- **Incorrect Extraction** - Major errors in extraction
- **Missing Information** - Important details missing
- **Duplicate Rule** - Rule appears elsewhere in dataset

## Expert Workflow

1. **Setup**: Enter name/ID and expertise area
2. **Review**: Examine rule details and original evidence
3. **Validate**: Select outcome and provide feedback
4. **Correct**: Provide corrected values if needed
5. **Progress**: Track validation statistics

This creates a systematic validation pipeline for building ground truth datasets and improving analyzer accuracy.

## Profiles in Validation

When running with a profile (e.g., `profiles/shif_ke.yaml`), the extraction uses profile-driven synonyms and categories.

- Confirm that profile mappings align with the payer's language.
- If misclassifications are systematic, update the profile YAML rather than changing code.
- Include the profile path in validation notes when findings are profile-dependent.
