#!/usr/bin/env python3
"""
Prepare AI prompt files (contradictions + gaps) from extracted CSVs using
the same Kenya-aware prompt templates used by the app.

Writes:
- prompts/contradictions.txt
- prompts/gaps.txt
"""
from pathlib import Path
import pandas as pd
from updated_prompts import UpdatedHealthcareAIPrompts as P


def short_policy_summary(df: pd.DataFrame) -> str:
    if df.empty:
        return "No policy data extracted"
    parts = []
    if 'service' in df.columns:
        parts.append(f"Policy entries: {len(df)}; Top services: {df['service'].value_counts().head(8).to_dict()}")
    else:
        parts.append(f"Policy entries: {len(df)}")
    if 'scope' in df.columns:
        scopes = df['scope'].dropna().astype(str).head(5).tolist()
        if scopes:
            parts.append("Sample scopes:\n- " + "\n- ".join(s[:120] for s in scopes))
    return "\n".join(parts)


def short_annex_summary(df: pd.DataFrame) -> str:
    if df.empty:
        return "No annex data extracted"
    spec = df['specialty'].value_counts().head(10).to_dict() if 'specialty' in df.columns else {}
    if 'tariff' in df.columns:
        t = df['tariff'].dropna()
        tstats = f"Tariffs: min={t.min():,.0f}, max={t.max():,.0f}, avg={t.mean():,.0f}"
    else:
        tstats = "Tariffs: not found"
    return f"Annex procedures: {len(df)}; Top specialties: {spec}; {tstats}"


def main():
    out_dir = Path("prompts"); out_dir.mkdir(exist_ok=True)
    policy_csv = Path("outputs/rules_p1_18_structured.csv")
    annex_csv = Path("outputs/annex_procedures.csv")
    if not policy_csv.exists() or not annex_csv.exists():
        raise SystemExit("Missing extracted CSVs. Run the integrated analyzer first.")

    policy = pd.read_csv(policy_csv)
    annex = pd.read_csv(annex_csv)

    extracted_data = (
        "POLICY STRUCTURE:\n" + short_policy_summary(policy) +
        "\n\nANNEX:\n" + short_annex_summary(annex)
    )
    specialties_data = (
        "ANNEX specialty breakdown:\n" +
        str(annex['specialty'].value_counts().to_dict() if 'specialty' in annex.columns else {})
    )

    contradiction_prompt = P.get_advanced_contradiction_prompt(extracted_data, specialties_data)
    gap_prompt = P.get_comprehensive_gap_analysis_prompt(
        extracted_data,
        "Kenya 2024: 56.4M pop, 47 counties, Pneumonia #1, Cancer #2, CVD #3, HTN 24%",
    )

    (out_dir / "contradictions.txt").write_text(contradiction_prompt, encoding="utf-8")
    (out_dir / "gaps.txt").write_text(gap_prompt, encoding="utf-8")
    print("✅ Wrote prompts/contradictions.txt and prompts/gaps.txt")


if __name__ == "__main__":
    main()

