# SHIF Analyzer Review – CA – 20250824

Role: Senior product‑minded reviewer for healthcare/insurance. Adversarial, specific, prescriptive.

Source PDF (truth): https://health.go.ke/sites/default/files/2024-11/TARIFFS%20TO%20THE%20BENEFIT%20PACKAGE%20TO%20THE%20SHI.pdf

---

## 1. A. Top Risks

1) Blocker — OpenAI extractor effectively not used; unit population 13.86% (target ≥80%)
- Evidence: Two runs (regex‑only and OpenAI auto) both show `tariff_unit` non‑unspecified at ~13.86% (101 rows). `extraction_method`=regex_only for all rows.
- Impact: Weak product credibility; contradictions can compare mismatched units or miss entirely.
- Fix: Gate AI on missing unit/tariff/levels (not category), ensure call path is reached, add small RPM/TPM scheduler + jitter backoff, and prompt types return native JSON. Verify model provisioning.

2) Blocker — Evidence snippets too short (avg ≈ 26 chars; target ≥200)
- Evidence: `contradictions.csv` left/right snippet average ≈ 26 chars; barely usable.
- Impact: Reviewers cannot validate flags quickly; weak traceability.
- Fix: Standardize 200–240 chars; prefer multi‑sentence capture; ensure source spans are correctly trimmed and not header‑only.

3) Major — Only Tariff contradiction detected; Limit/Coverage/Facility‑exclusion absent
- Evidence: Counts by type: Tariff=1; others=0 for both runs.
- Impact: Misses clinically important conflicts (e.g., dialysis 2 vs 3/week; excluded at Level N when included elsewhere).
- Fix: Strengthen limit parsing (weekly/monthly/day caps), facility level normalization/synonyms, and Coverage/Facility cross‑checks; unit guard prevents per‑session vs per‑day mixing.

4) Major — Service normalization brittle; risk of generic keys
- Evidence: Keys like `other_*` and long bullets; historical “level” collision noted in code comments.
- Impact: Grouping errors → false/negative contradictions.
- Fix: Enforce category‑prefixed `service_key` consistently; split bullets into atomic services; maintain a controlled dictionary for high‑risk categories (dialysis, imaging, maternity).

5) Major — TLS verification disabled on download
- Evidence: `download_pdf()` sets `session.verify=False` (current code).
- Impact: Security/privacy risk; unacceptable default for healthcare compliance.
- Fix: Remove; add `--insecure-download` flag only for local debugging.

---

## 2. B. Code Findings (by file/function)

- shif_analyzer.py
  - extract_with_openai():
    - Prompt schema uses quoted type hints (e.g., "tariff_value": "number|null"): model may output strings/lists as strings.
    - No RPM/TPM throttling; no jittered exponential backoff; no Retry‑After honor.
    - Model defaults now aligned to `gpt-5-mini` primary, `gpt-4.1-mini` fallback (good), but per‑item fallback rate cannot be measured reliably (model_used not set to fallback on fallback path).
  - should_use_openai():
    - Auto gating too strict; ties unit_unspecified to category OTHER, starving AI calls even when unit is missing.
  - parse_pdf_with_pdfplumber():
    - Calls AI per line/row without de‑dup caching; no scheduler; risk of burst 429s.
    - Facility levels mixed types (strings vs lists) across the pipeline; final normalization exists but downstream tooling expects consistent types.
  - extract_facility_levels()/extract_facility_level():
    - Numeric ranges + some Kenya keywords present, but synonyms (“tier”, “primary care”, “county/national referral”, “dispensary/health centre”) not consistently normalized.
  - merge_extractions():
    - Compares `tariff_value` fields; ensure `regex_result['tariff_value']` is always set to avoid None comparisons.
  - create_evidence_snippet():
    - Default 240 chars; several callers still pass shorter max lengths (observed 26‑char snippets in output) — standardize to ≥200.
  - download_pdf():
    - `session.verify=False` — remove; unacceptable default.
- clinical_excel_dashboard.py
  - Works, but Summary/Methods not guaranteed; ensure a “Methods & Assumptions + Worked Example” sheet.
  - Avoid savings claims unless clearly marked “illustrative only.”
- profiles/shif_ke.yaml
  - Good starting profile; extend synonyms for facility levels and exclusions; add normalization map.

---

## 3. C. Logic / Algorithm Issues

- Unit guard for Tariff conflicts:
  - Must group by (service_key, tariff_unit) and never compare per_session vs per_day.
- Limit conflicts:
  - Weekly vs monthly parsing must not collide; normalize keys to per_week/per_month/per_year/max_days/days_per_year.
- Coverage vs Facility‑exclusion:
  - Facility‑exclusion requires overlap of the same level between excluded and included entries; ensure levels are lists of ints everywhere before set operations.
- Duplicate/near‑duplicate lines:
  - Same sentence may appear in text and table; add de‑dup caching before calling AI.
- Negative rules:
  - Avoid misclassifying “services covered at Level …” as exclusion due to naive “covered at level” regex hits.

---

## 4. D. Evidence & Outputs Assessment

- Runs performed on local SHIF PDF using venv (regex‑only and OpenAI auto). Results:

| Metric | Regex Only | OpenAI+Regex (auto) |
|---|---:|---:|
| Rules parsed | 101 | 101 |
| Unit population (non‑unspecified) | 13.86% | 13.86% |
| Contradictions (Tariff) | 1 | 1 |
| Contradictions (Limit) | 0 | 0 |
| Contradictions (Coverage) | 0 | 0 |
| Contradictions (Facility‑exclusion) | 0 | 0 |
| Dialysis weekly conflict detected | No | No |
| Avg evidence snippet length | ~26 chars | ~26 chars |
| Gaps (YAML) | Stroke rehabilitation; Mental health | Stroke rehabilitation; Mental health |
| AI rows (extraction_method openai+regex) | 0 | 0 |

- Findings:
  - Evidence snippets are too short to be useful.
  - Only one Tariff contradiction found; others absent.
  - OpenAI path not exercised (likely gating + model access/backoff issues) → all rows are regex_only.

---

## 5. E. Product / Docs Feedback

- README and in‑repo docs are strong on disclaimers; keep “flagged for validation” language everywhere.
- Add a concise “Methods & Assumptions” (6–8 bullets) and a worked example (e.g., CT tariff variance) into the Excel Summary.
- Remove or clearly label any savings estimates as illustrative only; avoid numeric claims without validated evidence.
- Streamlit: good optional path; ensure it does not gate CSV/Excel deliverables.

Suggested Methods bullets:
- Hybrid extraction: regex + OpenAI (gpt‑5‑mini primary; gpt‑4.1‑mini fallback), per‑line/row scope.
- Evidence: page index + 200–240 char snippet; deterministic trimming.
- Units: normalized to per_session/visit/day/scan/month/year; household/beneficiary handled as limits.
- Facility levels: normalized to integer lists [1..6]; range handling (e.g., 4–6) expanded.
- Contradictions: 4 classes; grouped by (service_key, tariff_unit) for tariff.
- Gaps: YAML‑driven expectations; “NO COVERAGE FOUND”/“MINIMAL COVERAGE.”
- Validation: human review required; tool flags for triage only.

---

## 6. F. Quick Wins (≤2h) & Next Sprint (2–5 days)

Quick Wins (≤2h)
- Gate AI calls: trigger when `tariff_unit == 'unspecified'` OR `tariff_value missing` OR `facility_levels empty`.
- Standardize evidence_snippet length to 200–240 everywhere.
- Remove `session.verify=False`; add `--insecure-download` if you need a local override.
- Ensure `regex_result['tariff_value']` is always set before merge to make >10% discrepancy checks reliable.

Next Sprint (2–5 days)
- Add simple RPM/TPM scheduler + jitter backoff; honor Retry‑After.
- Add per‑run de‑dup caching (hash normalized line/row text) to reduce AI calls.
- Extend facility synonyms (tier/primary care/dispensary/health centre/county/national referral) and normalize to levels.
- Tighten limit parsing; ensure dialysis weekly conflicts are surfaced.
- Add golden‑file tests: CSV column order/headers; unit parsing; exclusion parsing; 4 contradiction classes; YAML gaps.
- Add an “AI scope” flag (`page|line|row`) for batch scenarios.

---

## 7. G. File Coverage (reviewed)

Code & Config
- shif_analyzer.py — Main pipeline; extraction, AI merge, contradictions/gaps, exports.
- clinical_excel_dashboard.py — Excel generation; needs Summary/Methods sheet and cautious savings messaging.
- expert_validation_interface.py — Streamlit validation; appears optional and fine.
- expert_validation_cli.py — CLI validator; fine.
- profiles/shif_ke.yaml — Profile keywords/categories; extend facility synonyms.
- requirements.txt — Dependencies; OK.

Outputs (from runs)
- outputs_regex/rules.csv — 101 rows; unit rate 13.86%; extraction_method=regex_only.
- outputs_regex/contradictions.csv — 1 Tariff contradiction; short snippets.
- outputs_regex/gaps.csv — Stroke rehab, Mental health.
- outputs_regex/SHIF_clinical_dashboard.xlsx — Generated; review needed for Summary/Methods.
- outputs_ai/rules.csv — Same metrics; AI path not exercised.
- outputs_ai/contradictions.csv — Same as regex.
- outputs_ai/gaps.csv — Same as regex.
- outputs_ai/SHIF_clinical_dashboard.xlsx — Generated.

Docs
- README.md — Clear; add Methods & Worked Example; avoid savings unless illustrative.
- VALIDATION_INTERFACES.md — Solid; add note on profile influence.
- TECHNICAL_LIMITATIONS_REPORT.md — Good; update with AI gating/scheduler gap and evidence snippet length standard.
- Other summaries (EXECUTIVE_* etc.) — Messaging mostly OK; keep “flagged for validation.”

Other
- communication_prep/* — Useful for narrative/Q&A; align claims with current metrics.

---

## Before vs After Comparison Table (from runs)

| Metric | Before (Regex Only) | After (OpenAI+Regex Auto) | Improvement? |
|---|---:|---:|:--:|
| Unit Population Rate | 13.86% | 13.86% | – |
| Tariff Conflicts | 1 | 1 | – |
| Limit Conflicts | 0 | 0 | – |
| Coverage Conflicts | 0 | 0 | – |
| Facility‑exclusion | 0 | 0 | – |
| Dialysis Conflict Found | No | No | – |
| Avg Snippet Length | ~26 chars | ~26 chars | – |
| YAML Gaps Detected | Stroke rehab; Mental health | Stroke rehab; Mental health | Same |
| Fallback Hit Rate | n/a | Not measurable (AI not exercised) | – |

---

## Executive Summary (3–5 bullets)
- The current run behaves as regex‑only in practice; OpenAI path is not exercised, leading to low unit population (~14%) and weak contradictions (only one Tariff conflict).
- Evidence snippets (~26 chars) are too short for validation; standardize to ≥200 chars with multi‑sentence context.
- To meet success criteria (≥80% unit population; >5% contradictions; dialysis limit if present; ≥200‑char snippets; <10% fallback), implement AI gating by need, modest RPM/TPM scheduling with backoff, de‑dup caching, and prompt typing cleanup.
- Strengthen facility synonyms/normalization and limit parsing; add Methods & Worked Example to the Excel Summary; remove or clearly label any savings as illustrative.
- With these targeted fixes, the pipeline should satisfy the assignment and produce reviewer‑credible outputs within one iteration.

*** End of Review ***
