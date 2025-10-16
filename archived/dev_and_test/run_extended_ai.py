#!/usr/bin/env python3
"""
CLI to run the Integrated Comprehensive Analyzer with optional extended AI modes.

Usage:
  python run_extended_ai.py --pdf "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf" \
      --extended --even-more --question "Any serious dialysis issues?"

Requires OPENAI_API_KEY in environment or .env.
"""

import argparse
import os
from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pdf', required=True, help='Path to the SHIF PDF')
    ap.add_argument('--extended', action='store_true', help='Run extended AI analyses')
    ap.add_argument('--even-more', action='store_true', help='Run additional AI analyses (summaries, canonicalization, equity)')
    ap.add_argument('--question', help='Optional user question for conversational analysis')
    args = ap.parse_args()

    analyzer = IntegratedComprehensiveMedicalAnalyzer()
    results = analyzer.analyze_complete_document(args.pdf, run_extended_ai=args.extended)

    # optionally run even more AI passes
    if args.even_more and analyzer.client:
        print("\n🔎 Running additional AI analyses (even more)…")
        policy = {'structured': results.get('policy_structured', results.get('policy_raw', None))}
        # adapt to stored keys in analyzer (we return dicts via _integrate_comprehensive_results)
        # Fallback to reusing earlier internal variables if available is not guaranteed here.
        # For CLI simplicity, recompute minimal containers if missing.
        annex = {'procedures': results.get('annex_procedures')}
        extra = analyzer.run_even_more_ai(policy, annex)
        results['even_more_ai'] = extra

    # Optional conversational answer
    if args.question and analyzer.client:
        from updated_prompts import UpdatedHealthcareAIPrompts as P
        context = "Use extracted summaries and Kenya 2024 context (56.4M pop, 47 counties)."
        prompt = P.get_conversational_analysis_prompt(args.question, context)
        print("\n💬 Conversational Response:")
        print(analyzer._call_openai(prompt))

    print("\n✅ Done. Outputs saved under timestamped outputs_run_*/ and printed to console where applicable.")


if __name__ == '__main__':
    main()

