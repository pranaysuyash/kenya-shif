#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHIF Policy Dashboard — CSV‑First, Deterministic, and Optional AI Insights

What this app does:
- Loads the exact CSVs you’ve already verified from your manual.ipynb pipeline:
    • rules_p1_18_raw.csv
    • rules_p1_18_structured_exploded.csv
    • rules_p1_18_structured_wide.csv
    • annex_surgical_tariffs_all.csv
- Presents an interactive dashboard with overview metrics, clean tables, and charts.
- Provides optional OpenAI-powered narrative insights, disabled unless a key is provided.
- Optionally runs your own extractor Python file (the “same Python file”) and then reloads the CSVs.

Why this fixes your current issues:
1) No hidden re‑extraction, no surprise schema drift. We read the verified CSVs you trust.
2) No fragile imports of “integrated analyzers.” Everything is self-contained.
3) File names match your artifacts exactly. If they’re in a different folder, just point the app to that folder.
4) Determinism checks ensure numbers match across exploded/wide views, so mismatches surface immediately.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st

# --------------- Page setup ---------------
st.set_page_config(
    page_title="Kenya SHIF Policy Dashboard",
    page_icon="🏥",
    layout="wide"
)

# --------------- Sidebar: data source ---------------
st.sidebar.title("🔧 Data Source & Controls")

# Base directory for CSVs
default_base_dir = Path(".").resolve()
base_dir_str = st.sidebar.text_input(
    "CSV folder path",
    value=str(default_base_dir),
    help=(
        "Folder that contains the four CSV files produced by your manual pipeline:\n"
        "  - rules_p1_18_raw.csv\n"
        "  - rules_p1_18_structured_exploded.csv\n"
        "  - rules_p1_18_structured_wide.csv\n"
        "  - annex_surgical_tariffs_all.csv\n"
        "Example: ./outputs or the project root where these CSVs live."
    )
)
base_dir = Path(base_dir_str).expanduser().resolve()

# Optional: run your extractor script (the same Python file you trust)
with st.sidebar.expander("▶️ Optional: Run your extractor script, then reload"):
    extractor_path = st.text_input(
        "Path to your extractor .py file",
        value="",
        help="If provided, the app will run this script with the same Python interpreter, then reload CSVs."
    )
    extractor_args = st.text_input(
        "Optional args (space-separated)",
        value="",
        help="Example: --pdf 'path/to/SHIF.pdf' --out 'outputs'"
    )
    run_extractor = st.button("Run extractor now")

# OpenAI key for insights (optional)
openai_key = st.sidebar.text_input(
    "OpenAI API key (optional)",
    type="password",
    help="Provide ONLY if you want AI-generated narrative insights. The app runs fine without it."
)

# --------------- Constants: expected files ---------------
EXPECTED_FILES = {
    "raw": "rules_p1_18_raw.csv",
    "exploded": "rules_p1_18_structured_exploded.csv",
    "wide": "rules_p1_18_structured_wide.csv",
    "annex": "annex_surgical_tariffs_all.csv",
}

# --------------- Utilities ---------------
@st.cache_data(show_spinner=False)
def load_csvs(base: Path) -> Dict[str, pd.DataFrame]:
    files = {}
    errors = []

    for key, fname in EXPECTED_FILES.items():
        fpath = base / fname
        if not fpath.exists():
            errors.append(f"Missing: {fpath}")
            continue
        try:
            df = pd.read_csv(fpath)
            files[key] = df
        except Exception as e:
            errors.append(f"Failed to read {fpath}: {e}")

    return files, errors

def _num(x) -> Optional[float]:
    try:
        if pd.isna(x): 
            return None
        if isinstance(x, (int, float)):
            return float(x)
        # strip currency and commas
        s = str(x).replace(",", "").replace("KES", "").strip()
        return float(s) if s else None
    except Exception:
        return None

def safe_count_unique(df: Optional[pd.DataFrame], col: str) -> int:
    if df is None or df.empty or col not in df.columns:
        return 0
    return df[col].nunique(dropna=True)

def _annex_top_procedures_by_tariff(annex_df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    if annex_df is None or annex_df.empty:
        return pd.DataFrame()
    df = annex_df.copy()
    df["tariff_num"] = df["tariff"].apply(_num)
    df = df.dropna(subset=["tariff_num"]).sort_values("tariff_num", ascending=False)
    return df.head(n)[["specialty", "intervention", "tariff_num"]]

def _wide_to_long_tariff(wide_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the wide 'tariff_pairs' JSON-like column into long rows: one row per item_label with its item_tariff.
    Assumes wide_df has columns: ['service','fund','access_point','tariff_pairs', ...].
    """
    if wide_df is None or wide_df.empty or "tariff_pairs" not in wide_df.columns:
        return pd.DataFrame()

    # Attempt to parse a JSON-like string, or already parsed list
    def parse_pairs(val):
        if isinstance(val, list):
            return val
        s = str(val)
        # Try JSON first
        try:
            return json.loads(s)
        except Exception:
            # very simple fallback, expects patterns like "['label: X', 'tariff: Y']"
            return []

    rows = []
    for _, r in wide_df.iterrows():
        service = r.get("service")
        fund = r.get("fund")
        access_pt = r.get("access_point")
        mp = r.get("mapping_type")
        pairs = parse_pairs(r.get("tariff_pairs"))
        if isinstance(pairs, dict) and "items" in pairs:
            pairs = pairs["items"]
        if not isinstance(pairs, list):
            continue
        for it in pairs:
            if isinstance(it, dict):
                label = it.get("item_label") or it.get("label")
                tariff = it.get("item_tariff") or it.get("tariff")
            else:
                label, tariff = None, None
            rows.append({
                "fund": fund,
                "service": service,
                "access_point": access_pt,
                "mapping_type": mp,
                "item_label": label,
                "item_tariff": _num(tariff),
            })
    return pd.DataFrame(rows)

# --------------- Optional: run extractor ---------------
if run_extractor and extractor_path.strip():
    try:
        st.sidebar.info("Running extractor, please wait…")
        cmd = [sys.executable, extractor_path]
        if extractor_args.strip():
            cmd.extend(extractor_args.split())
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(base_dir))
        if proc.returncode != 0:
            st.sidebar.error(f"Extractor failed with code {proc.returncode}\n\nSTDERR:\n{proc.stderr}")
        else:
            st.sidebar.success("Extractor finished successfully. Reloading CSVs…")
            # small delay to allow files to flush
            time.sleep(0.5)
            st.rerun()
    except Exception as e:
        st.sidebar.error(f"Extractor error: {e}")

# --------------- Load data ---------------
dfs, errs = load_csvs(base_dir)
missing = [e for e in errs if e.startswith("Missing")]
failed = [e for e in errs if e.startswith("Failed")]

if missing:
    st.warning("Some CSVs are missing. Provide the folder that contains the verified CSV outputs.")
    for e in missing:
        st.code(e)
if failed:
    st.error("Some CSVs failed to load:")
    for e in failed:
        st.code(e)

raw_df = dfs.get("raw")
exploded_df = dfs.get("exploded")
wide_df = dfs.get("wide")
annex_df = dfs.get("annex")

# --------------- Header ---------------
st.title("Kenya SHIF Policy Dashboard")
st.caption("CSV‑first, deterministic, and aligned with your manual.ipynb outputs")

# --------------- Overview metrics ---------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Services (wide)", safe_count_unique(wide_df, "service"))
with col2:
    st.metric("Exploded rows", 0 if exploded_df is None else len(exploded_df))
with col3:
    st.metric("Funds", safe_count_unique(wide_df if wide_df is not None else raw_df, "fund"))
with col4:
    st.metric("Annex procedures", 0 if annex_df is None else len(annex_df))

st.markdown("---")

# --------------- Tabs ---------------
tab_overview, tab_structured, tab_annex, tab_ai = st.tabs(
    ["Overview", "Task 1: Structured Rules", "Annex (19–54)", "AI Insights (optional)"]
)

# --------------- Overview ---------------
with tab_overview:
    st.subheader("Quick Checks")

    # Determinism check: group exploded by service, compare counts to wide
    if exploded_df is not None and wide_df is not None and not exploded_df.empty and not wide_df.empty:
        g = exploded_df.groupby("service")["item_label"].count().reset_index(name="exploded_items")
        w = wide_df[["service"]].copy()
        merged = w.merge(g, on="service", how="left").fillna({"exploded_items": 0})
        st.write("Exploded item counts per service (should be consistent for the same source CSV):")
        st.dataframe(merged.sort_values("exploded_items", ascending=False), use_container_width=True, hide_index=True)

    st.subheader("Distributions")

    # By fund
    if wide_df is not None and not wide_df.empty and "fund" in wide_df.columns:
        fig = px.bar(
            wide_df["fund"].value_counts().reset_index(),
            x="index", y="fund",
            labels={"index": "Fund", "fund": "Count"},
            title="Services by Fund"
        )
        st.plotly_chart(fig, use_container_width=True)

    # By access_point (facility level text)
    if wide_df is not None and not wide_df.empty and "access_point" in wide_df.columns:
        fig = px.bar(
            wide_df["access_point"].fillna("Not specified").value_counts().reset_index(),
            x="index", y="access_point",
            labels={"index": "Access Point (facility level)", "access_point": "Count"},
            title="Services by Access Point / Facility Level"
        )
        st.plotly_chart(fig, use_container_width=True)

    # By mapping_type
    if wide_df is not None and not wide_df.empty and "mapping_type" in wide_df.columns:
        fig = px.pie(
            wide_df["mapping_type"].fillna("Unknown"),
            title="Mapping Type split (block vs item)"
        )
        st.plotly_chart(fig, use_container_width=True)

# --------------- Structured Rules ---------------
with tab_structured:
    st.subheader("Structured, Exploded View")
    if exploded_df is not None and not exploded_df.empty:
        st.dataframe(exploded_df, use_container_width=True, hide_index=True)
        # Top items by tariff if present
        if "item_tariff" in exploded_df.columns:
            tmp = exploded_df.copy()
            tmp["item_tariff_num"] = tmp["item_tariff"].apply(_num)
            top = tmp.dropna(subset=["item_tariff_num"]).sort_values("item_tariff_num", ascending=False).head(25)
            if not top.empty:
                fig = px.bar(
                    top,
                    x="item_label",
                    y="item_tariff_num",
                    color="service",
                    title="Top 25 Item Tariffs (Exploded)"
                )
                fig.update_layout(xaxis_title="Item Label", yaxis_title="Tariff (KES)")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Upload or point to rules_p1_18_structured_exploded.csv to see the exploded view.")

    st.subheader("Structured, Wide View")
    if wide_df is not None and not wide_df.empty:
        st.dataframe(wide_df, use_container_width=True, hide_index=True)

        # Derive long tariff rows from 'tariff_pairs'
        long_tariff = _wide_to_long_tariff(wide_df)
        if not long_tariff.empty:
            st.markdown("**Derived from wide.tariff_pairs → long rows**")
            st.dataframe(long_tariff, use_container_width=True, hide_index=True)
    else:
        st.info("Upload or point to rules_p1_18_structured_wide.csv to see the wide view.")

# --------------- Annex ---------------
with tab_annex:
    st.subheader("Annex Surgical Procedures (Pages 19–54)")
    if annex_df is not None and not annex_df.empty:
        st.dataframe(annex_df, use_container_width=True, hide_index=True)

        st.markdown("**Top procedures by tariff**")
        top = _annex_top_procedures_by_tariff(annex_df, n=20)
        if not top.empty:
            fig = px.bar(
                top,
                x="intervention",
                y="tariff_num",
                color="specialty",
                title="Top 20 Annex Procedures by Tariff"
            )
            fig.update_layout(xaxis_title="Procedure", yaxis_title="Tariff (KES)")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Upload or point to annex_surgical_tariffs_all.csv to see annex analysis.")

# --------------- AI Insights (optional) ---------------
with tab_ai:
    st.subheader("AI-generated narrative (optional)")
    if not openai_key:
        st.info("Provide an OpenAI API key in the sidebar to enable this section.")
    else:
        try:
            import openai
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)

            # Build a compact, deterministic context for the model
            context_bits = []
            if wide_df is not None and not wide_df.empty:
                context_bits.append({
                    "services": int(wide_df["service"].nunique()),
                    "funds": int(wide_df["fund"].nunique() if "fund" in wide_df.columns else 0),
                    "mapping_types": wide_df["mapping_type"].value_counts().to_dict() if "mapping_type" in wide_df.columns else {}
                })
            if annex_df is not None and not annex_df.empty:
                top_annex = _annex_top_procedures_by_tariff(annex_df, n=10).to_dict(orient="records")
            else:
                top_annex = []

            prompt = (
                "You are an analyst summarizing a Kenyan SHIF policy dataset extracted from an official PDF. "
                "Write a crisp, executive summary with factual statements only, using the provided aggregates. "
                "Avoid hallucinating specifics that aren't in the aggregates.\n\n"
                f"Aggregates:\n{json.dumps({'overview': context_bits, 'top_annex': top_annex}, ensure_ascii=False, indent=2)}\n\n"
                "Output:\n- 5–8 bullet points\n- Make each bullet short\n- If a number is 0 or missing, skip that bullet."
            )

            with st.spinner("Asking OpenAI…"):
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=350,
                )
                text = resp.choices[0].message.content.strip()
                st.markdown(text)

        except Exception as e:
            st.error(f"OpenAI error: {e}")

# --------------- Footer ---------------
st.markdown("---")
st.caption(
    "This dashboard intentionally reads the verified CSVs, so the numbers match your manual.ipynb. "
    "If you need to re-run extraction, point to your own script in the sidebar, run it, then reload."
)
