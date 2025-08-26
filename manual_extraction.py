#!/usr/bin/env python3
"""
Manual extraction fallbacks and CSV loaders.
If integrated extraction yields empty results, we can pull from the CSVs produced by
the manual notebook-based pipeline in outputs/.
"""
from pathlib import Path
from typing import Dict, Tuple
import pandas as pd


def load_manual_outputs_if_available() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load manual CSV outputs if present.

    Returns: (policy_df, annex_df)
    - policy_df: rules_p1_18_structured.csv if available, else empty
    - annex_df: annex_surgical_tariffs_all.csv if available, else empty
    """
    base = Path('outputs')
    policy_csvs = [
        base / 'rules_p1_18_structured.csv',
        base / 'rules_p1_18_structured_wide.csv',
        base / 'rules_p1_18_structured_exploded.csv',
        base / 'rules_p1_18_raw.csv',
    ]
    annex_csvs = [
        base / 'annex_surgical_tariffs_all.csv',
    ]
    policy_df = pd.DataFrame()
    annex_df = pd.DataFrame()
    for p in policy_csvs:
        if p.exists():
            try:
                policy_df = pd.read_csv(p)
                break
            except Exception:
                continue
    for a in annex_csvs:
        if a.exists():
            try:
                annex_df = pd.read_csv(a)
                break
            except Exception:
                continue
    return policy_df, annex_df

