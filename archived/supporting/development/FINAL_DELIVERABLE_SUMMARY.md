# SHIF Benefits Analyzer – Final Deliverable Summary

All outputs are flagged for validation. Findings are evidence-linked to PDF pages and snippets.

## What’s Included
- outputs_regexFinal/: Baseline (regex-only)
  - rules.csv, contradictions.csv, gaps.csv, SHIF_clinical_dashboard.xlsx
- outputs_aiFinal/: OpenAI-gated (primary gpt-5-mini, fallback gpt-4.1-mini)
  - rules.csv, contradictions.csv, gaps.csv, SHIF_clinical_dashboard.xlsx
- SHIF_Analyzer_Review_CA_20250824.md: Adversarial product/code review with prescriptive fixes

## How to Run
```bash
source .venv/bin/activate
# Baseline
python shif_analyzer.py --file "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf" \
  --no-openai --openai-mode never --output outputs_regexFinal
# OpenAI-gated
python shif_analyzer.py --file "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf" \
  --openai-mode auto --openai-primary gpt-5-mini --openai-fallback gpt-4.1-mini \
  --output outputs_aiFinal
```

## Acceptance Checklist (to verify)
- Rules: service, service_key, tariff/tariff_value, tariff_unit, facility_levels, coverage_status, limits, page, raw_text, evidence_snippet, extraction_method, model_used, confidence
- Contradictions: Tariff/Limit/Coverage/Facility-exclusion with left/right page and ≥200-char snippets
- Gaps: YAML-driven (e.g., Stroke rehabilitation) with expected services list
- Dashboard: Excel has Summary & Methods sheet; language “flagged for validation”

## Current Snapshot (from local runs)
- Rules parsed: 101 (both modes)
- Unit population (tariff_unit ≠ "unspecified"): ~13.86% (needs AI gating to lift)
- Contradictions: Tariff=1; Limit/Coverage/Facility-exclusion observed=0 (depends on document content)
- Dialysis weekly conflict: Not detected in current source sample
- Evidence snippet length: ~26 chars (baseline) → Methods tab added; extraction set to 240 chars going forward

## Next Steps to Show Success Criteria (fast)
- Ensure OpenAI credentials/model provisioning; re-run `outputs_aiFinal` to raise unit population ≥80%
- Validate contradictions by type against PDF pages; add any missed facility synonyms into profile
- Keep Streamlit optional for demo: `streamlit run shif_analyzer.py -- --streamlit --file "...pdf"`

All findings require expert validation prior to policy action.
