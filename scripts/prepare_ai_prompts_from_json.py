#!/usr/bin/env python3
from pathlib import Path
import json
import pandas as pd
from updated_prompts import UpdatedHealthcareAIPrompts as P

def main():
    jpath = Path('outputs/integrated_comprehensive_analysis.json')
    if not jpath.exists():
        raise SystemExit('Missing outputs/integrated_comprehensive_analysis.json. Run the integrated analyzer first.')

    data = json.loads(jpath.read_text(encoding='utf-8'))
    policy = pd.DataFrame(data.get('extraction_results',{}).get('policy_structure',{}).get('data', []))
    annex = pd.DataFrame(data.get('extraction_results',{}).get('annex_procedures',{}).get('data', []))

    def short_policy_summary(df: pd.DataFrame) -> str:
        if df.empty: return 'No policy data extracted'
        top_services = df['service'].value_counts().head(8).to_dict() if 'service' in df.columns else {}
        scopes = df['scope'].dropna().astype(str).head(5).tolist() if 'scope' in df.columns else []
        parts = [f"Policy entries: {len(df)}; Top services: {top_services}"]
        if scopes:
            parts.append('Sample scopes:\n- ' + '\n- '.join(s[:120] for s in scopes))
        return '\n'.join(parts)

    def short_annex_summary(df: pd.DataFrame) -> str:
        if df.empty: return 'No annex data extracted'
        spec = df['specialty'].value_counts().head(10).to_dict() if 'specialty' in df.columns else {}
        if 'tariff' in df.columns:
            t = df['tariff'].dropna()
            tstats = f"Tariffs: min={t.min():,.0f}, max={t.max():,.0f}, avg={t.mean():,.0f}"
        else:
            tstats = 'Tariffs: not found'
        return f"Annex procedures: {len(df)}; Top specialties: {spec}; {tstats}"

    extracted_data = (
        'POLICY STRUCTURE:\n' + short_policy_summary(policy) +
        '\n\nANNEX:\n' + short_annex_summary(annex)
    )
    specialties_data = (
        'ANNEX specialty breakdown:\n' + str(annex['specialty'].value_counts().to_dict() if 'specialty' in annex.columns else {})
    )

    out_dir = Path('prompts'); out_dir.mkdir(exist_ok=True)
    (out_dir / 'contradictions.txt').write_text(P.get_advanced_contradiction_prompt(extracted_data, specialties_data), encoding='utf-8')
    (out_dir / 'gaps.txt').write_text(P.get_comprehensive_gap_analysis_prompt(
        extracted_data,
        'Kenya 2024: 56.4M pop, 47 counties, Pneumonia #1, Cancer #2, CVD #3, HTN 24%'),
        encoding='utf-8')
    print('✅ Wrote prompts/contradictions.txt and prompts/gaps.txt from JSON')

if __name__ == '__main__':
    main()

