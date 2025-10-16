#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHIF Policy Dashboard — Cached Runs with Dated Folders, Self-Contained, Optional AI

This removes filename rigidity and makes the Streamlit app look FIRST at its own cached runs:
- Scans a runs/ directory for dated subfolders (e.g., 2025-08-27_17-45-12 or any name).
- Auto-detects which CSV is annex / exploded / wide / raw by schema, not by filename.
- "Latest run" is picked by most recent mtime that contains required files.
- Optional "Run extractor now" creates a fresh dated folder, runs YOUR python file, then reloads.

Conventions:
- A run folder is any subdirectory inside RUNS_ROOT that contains one or more CSVs. 
- If a run contains a manifest.json with explicit file paths, those are used.
- Otherwise, we classify CSVs by columns:
    * ANNEX: has {'specialty','intervention','tariff'}
    * WIDE: has 'tariff_pairs' column (plus typical {'service','fund','access_point'})
    * EXPLODED: has 'item_label' (and usually 'item_tariff')
    * RAW: has at least {'service','fund','access_point'} but neither 'tariff_pairs' nor 'item_label'
- Required to render most charts: ANNEX + WIDE + EXPLODED. RAW is optional.

Extractor integration:
- In the sidebar, provide the path to your extractor (your "same python file").
- Click "Run extractor now", we create runs/<timestamp>/ as the working OUT dir.
- We pass environment variable SHIF_RUN_DIR pointing to that folder.
- Optionally, we append a CLI flag like --out <run_dir> for extractors expecting that.
- After completion, the dashboard reloads and selects the new run.

This design matches your ask:
- Streamlit looks for its OWN cached outputs in dated folders first.
- No surprises from different filenames; we infer roles by schema, not names.
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

import streamlit as st

# ----------------- Config -----------------
DEFAULT_RUNS_ROOT = Path("runs").resolve()
REQUIRED_ROLES = ("annex", "wide", "exploded")  # raw is optional

# ----------------- Page setup -----------------
st.set_page_config(page_title="Kenya SHIF — Cached Runs", page_icon="🏥", layout="wide")
st.title("Kenya SHIF Policy Dashboard")
st.caption("Cached runs with dated folders, schema‑based file detection, and optional AI insights.")

# ----------------- Helpers -----------------
def _is_csv(path: Path) -> bool:
    return path.suffix.lower() == ".csv" and path.is_file()

def _read_head(path: Path, n: int = 2000) -> Optional[pd.DataFrame]:
    try:
        # read only a bit to detect columns; low_memory avoids dtype churn
        return pd.read_csv(path, nrows=n, low_memory=False)
    except Exception:
        return None

def _detect_role(df: pd.DataFrame) -> Optional[str]:
    cols = set([c.strip() for c in df.columns])
    # ANNEX signature
    if {"specialty", "intervention", "tariff"}.issubset(cols):
        return "annex"
    # WIDE signature
    if "tariff_pairs" in cols and "service" in cols:
        return "wide"
    # EXPLODED signature
    if "item_label" in cols:
        return "exploded"
    # RAW signature (fallback)
    if {"service", "fund", "access_point"}.issubset(cols) and "tariff_pairs" not in cols and "item_label" not in cols:
        return "raw"
    return None

def _num(x) -> Optional[float]:
    try:
        if pd.isna(x): 
            return None
        if isinstance(x, (int, float)):
            return float(x)
        s = str(x).replace(",", "").replace("KES", "").strip()
        return float(s) if s else None
    except Exception:
        return None

def _load_manifest(run_dir: Path) -> Optional[Dict[str, str]]:
    mf = run_dir / "manifest.json"
    if not mf.exists():
        return None
    try:
        j = json.loads(mf.read_text())
        # expected form: {"annex": "annex.csv", "wide": "wide.csv", "exploded": "exploded.csv", "raw": "raw.csv"}
        out = {}
        for k in ("annex", "wide", "exploded", "raw"):
            v = j.get(k)
            if v:
                p = (run_dir / v).resolve()
                if p.exists():
                    out[k] = str(p)
        return out or None
    except Exception:
        return None

def _classify_run_files(run_dir: Path) -> Dict[str, str]:
    """
    Return mapping from role -> absolute path, using manifest.json if present, else schema-based detection.
    """
    by_role: Dict[str, str] = {}

    manifest = _load_manifest(run_dir)
    if manifest:
        return manifest

    # Scan CSVs
    for csv in sorted(run_dir.glob("*.csv")):
        df = _read_head(csv, n=1500)
        if df is None or df.empty:
            continue
        role = _detect_role(df)
        if role and role not in by_role:
            by_role[role] = str(csv.resolve())
        # if multiple candidates for same role appear, keep the first by name sort

    return by_role

def _run_dirs(root: Path) -> List[Path]:
    if not root.exists():
        return []
    return [p for p in root.iterdir() if p.is_dir()]

def _dir_mtime(p: Path) -> float:
    try:
        return max((f.stat().st_mtime for f in p.rglob("*")), default=p.stat().st_mtime)
    except Exception:
        return p.stat().st_mtime

def _pretty_run_label(run_dir: Path, roles: Dict[str, str]) -> str:
    stamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(_dir_mtime(run_dir)))
    flags = " ".join(f"{r}✔" for r in ("annex", "wide", "exploded") if r in roles)
    return f"{stamp} · {run_dir.name} · {flags or 'partial'}"

@st.cache_data(show_spinner=False)
def list_runs(root: str, require_complete: bool) -> List[Tuple[str, str]]:
    """
    Return a list of (label, abs_path) for run selection.
    Cached on root + flag for fast UI.
    """
    root_path = Path(root).expanduser().resolve()
    items: List[Tuple[str, str]] = []
    for d in _run_dirs(root_path):
        roles = _classify_run_files(d)
        if require_complete and not all(r in roles for r in REQUIRED_ROLES):
            continue
        items.append((_pretty_run_label(d, roles), str(d)))
    # sort by mtime desc
    items.sort(key=lambda t: _dir_mtime(Path(t[1])), reverse=True)
    return items

@st.cache_data(show_spinner=False)
def load_role_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)

def _wide_to_long_tariff(wide_df: pd.DataFrame) -> pd.DataFrame:
    if wide_df is None or wide_df.empty or "tariff_pairs" not in wide_df.columns:
        return pd.DataFrame()

    def parse_pairs(val):
        if isinstance(val, list):
            return val
        s = str(val)
        try:
            return json.loads(s)
        except Exception:
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

def _annex_top_procedures_by_tariff(annex_df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    if annex_df is None or annex_df.empty:
        return pd.DataFrame()
    df = annex_df.copy()
    if "tariff_num" not in df.columns:
        df["tariff_num"] = df["tariff"].apply(_num) if "tariff" in df.columns else np.nan
    df = df.dropna(subset=["tariff_num"]).sort_values("tariff_num", ascending=False)
    keep = [c for c in ["specialty", "intervention", "tariff_num"] if c in df.columns]
    return df.head(n)[keep]

# ----------------- Sidebar: Run selection & controls -----------------
st.sidebar.header("Runs & Controls")

runs_root = st.sidebar.text_input(
    "Runs root folder",
    value=str(DEFAULT_RUNS_ROOT),
    help="Where cached runs are stored, each run in a dated subfolder."
)

require_complete = st.sidebar.checkbox("Only show complete runs (annex, wide, exploded present)", value=True)
if st.sidebar.button("🔄 Refresh run list"):
    list_runs.clear()
runs = list_runs(runs_root, require_complete=require_complete)

if not runs:
    st.sidebar.warning("No runs found. Create one with the extractor below, or point to the correct runs root.")
    selected_run = None
else:
    labels = [lbl for lbl, _ in runs]
    default_idx = 0  # most recent already sorted
    selected_label = st.sidebar.selectbox("Select a run", labels, index=default_idx)
    selected_run = dict(runs)[selected_label]

# ----------------- Sidebar: Extractor integration -----------------
st.sidebar.markdown("---")
st.sidebar.subheader("Run extractor (optional)")

extractor_path = st.sidebar.text_input("Path to your extractor .py", value="", help="Your 'same python file'.")
user_args = st.sidebar.text_input("Optional extra CLI args", value="", help="E.g., --pdf 'path/to/file.pdf'")
append_out_flag = st.sidebar.checkbox("Append --out <run_dir> automatically", value=True)
if st.sidebar.button("▶️ Run extractor now"):
    if not extractor_path.strip():
        st.sidebar.error("Provide the extractor .py path first.")
    else:
        try:
            out_root = Path(runs_root).expanduser().resolve()
            out_root.mkdir(parents=True, exist_ok=True)
            ts = time.strftime("%Y-%m-%d_%H-%M-%S")
            run_dir = (out_root / ts).resolve()
            run_dir.mkdir(parents=True, exist_ok=True)

            cmd = [sys.executable, extractor_path]
            if user_args.strip():
                cmd.extend(user_args.split())
            if append_out_flag:
                cmd.extend(["--out", str(run_dir)])

            env = os.environ.copy()
            env["SHIF_RUN_DIR"] = str(run_dir)  # extractor can read this if it prefers env over cli

            with st.spinner(f"Running extractor into {run_dir.name} …"):
                proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(out_root), env=env)

            if proc.returncode != 0:
                st.sidebar.error(f"Extractor failed ({proc.returncode}).\nSTDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}")
            else:
                st.sidebar.success(f"Extractor finished, created run: {run_dir.name}")
                # invalidate run list cache and rerun
                list_runs.clear()
                st.rerun()

        except Exception as e:
            st.sidebar.error(f"Extractor error: {e}")

# ----------------- Load selected run -----------------
run_mapping = {}
if selected_run:
    run_dir = Path(selected_run).resolve()
    run_mapping = _classify_run_files(run_dir)

# Diagnostics for the chosen run
with st.expander("ℹ️ Selected run details", expanded=False):
    if not selected_run:
        st.write("No run selected.")
    else:
        st.write(f"**Run folder:** {selected_run}")
        st.json(run_mapping or {"warning": "No recognized files yet"})

# Short-circuit if nothing to show
if not run_mapping:
    st.info("Select a run that contains CSV outputs, or generate a new one from the sidebar.")
    st.stop()

# Load role DataFrames
dfs: Dict[str, pd.DataFrame] = {}
load_errors = []
for role, path in run_mapping.items():
    try:
        dfs[role] = load_role_csv(path)
    except Exception as e:
        load_errors.append(f"{role}: failed to read {path} — {e}")

if load_errors:
    st.error("Some files failed to load:")
    for e in load_errors:
        st.code(e)

annex_df    = dfs.get("annex")
wide_df     = dfs.get("wide")
exploded_df = dfs.get("exploded")
raw_df      = dfs.get("raw")

# ----------------- Overview metrics -----------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Services (wide)", 0 if wide_df is None or wide_df.empty else int(wide_df["service"].nunique()))
with col2:
    st.metric("Exploded rows", 0 if exploded_df is None or exploded_df.empty else len(exploded_df))
with col3:
    st.metric("Funds", 0 if wide_df is None or wide_df.empty or "fund" not in wide_df.columns else int(wide_df["fund"].nunique()))
with col4:
    st.metric("Annex procedures", 0 if annex_df is None or annex_df.empty else len(annex_df))

st.markdown("---")

# ----------------- Tabs -----------------
tab_overview, tab_structured, tab_annex, tab_ai = st.tabs(
    ["Overview", "Task 1: Structured Rules", "Annex (19–54)", "AI Insights (optional)"]
)

# ----------------- Overview -----------------
with tab_overview:
    st.subheader("Quick Checks")

    if exploded_df is not None and wide_df is not None and not exploded_df.empty and not wide_df.empty:
        g = exploded_df.groupby("service")["item_label"].count().reset_index(name="exploded_items")
        w = wide_df[["service"]].copy()
        merged = w.merge(g, on="service", how="left").fillna({"exploded_items": 0})
        st.write("Exploded item counts per service:")
        st.dataframe(merged.sort_values("exploded_items", ascending=False), use_container_width=True, hide_index=True)

    st.subheader("Distributions")
    if wide_df is not None and not wide_df.empty:
        if "fund" in wide_df.columns:
            fig = px.bar(
                wide_df["fund"].value_counts().reset_index(),
                x="index", y="fund",
                labels={"index": "Fund", "fund": "Count"},
                title="Services by Fund"
            )
            st.plotly_chart(fig, use_container_width=True)

        if "access_point" in wide_df.columns:
            fig = px.bar(
                wide_df["access_point"].fillna("Not specified").value_counts().reset_index(),
                x="index", y="access_point",
                labels={"index": "Access Point / Facility Level", "access_point": "Count"},
                title="Services by Access Point"
            )
            st.plotly_chart(fig, use_container_width=True)

        if "mapping_type" in wide_df.columns:
            fig = px.pie(
                wide_df["mapping_type"].fillna("Unknown"),
                title="Mapping Type split"
            )
            st.plotly_chart(fig, use_container_width=True)

# ----------------- Structured Rules -----------------
with tab_structured:
    st.subheader("Structured, Exploded View")
    if exploded_df is not None and not exploded_df.empty:
        st.dataframe(exploded_df, use_container_width=True, hide_index=True)

        # optional top tariffs chart
        cols = set(exploded_df.columns)
        if "item_tariff" in cols or "item_tariff_num" in cols:
            tmp = exploded_df.copy()
            if "item_tariff_num" not in tmp.columns:
                tmp["item_tariff_num"] = tmp["item_tariff"].apply(_num) if "item_tariff" in tmp.columns else np.nan
            top = tmp.dropna(subset=["item_tariff_num"]).sort_values("item_tariff_num", ascending=False).head(25)
            if not top.empty:
                fig = px.bar(top, x="item_label", y="item_tariff_num", color="service", title="Top 25 Item Tariffs")
                fig.update_layout(xaxis_title="Item Label", yaxis_title="Tariff (KES)")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No exploded file detected in this run.")

    st.subheader("Structured, Wide View")
    if wide_df is not None and not wide_df.empty:
        st.dataframe(wide_df, use_container_width=True, hide_index=True)

        # derive long from tariff_pairs
        long_tariff = _wide_to_long_tariff(wide_df)
        if not long_tariff.empty:
            st.markdown("**Derived from wide.tariff_pairs → long rows**")
            st.dataframe(long_tariff, use_container_width=True, hide_index=True)
    else:
        st.info("No wide file detected in this run.")

# ----------------- Annex -----------------
with tab_annex:
    st.subheader("Annex Surgical Procedures (Pages 19–54)")
    if annex_df is not None and not annex_df.empty:
        st.dataframe(annex_df, use_container_width=True, hide_index=True)

        st.markdown("**Top procedures by tariff**")
        top = _annex_top_procedures_by_tariff(annex_df, n=20)
        if not top.empty:
            xcol = "intervention" if "intervention" in top.columns else top.columns[0]
            ycol = "tariff_num" if "tariff_num" in top.columns else top.columns[-1]
            color = "specialty" if "specialty" in top.columns else None
            fig = px.bar(top, x=xcol, y=ycol, color=color, title="Top 20 Annex Procedures by Tariff")
            fig.update_layout(xaxis_title="Procedure", yaxis_title="Tariff (KES)")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No annex file detected in this run.")

# ----------------- AI Insights (optional) -----------------
with tab_ai:
    st.subheader("AI-generated narrative (optional)")
    openai_key = st.text_input("OpenAI API key", type="password")
    if not openai_key:
        st.info("Provide your API key to enable this section.")
    else:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)

            context_bits = []
            if wide_df is not None and not wide_df.empty:
                context_bits.append({
                    "services": int(wide_df["service"].nunique()) if "service" in wide_df.columns else 0,
                    "funds": int(wide_df["fund"].nunique()) if "fund" in wide_df.columns else 0,
                    "mapping_types": wide_df["mapping_type"].value_counts().to_dict() if "mapping_type" in wide_df.columns else {}
                })
            if annex_df is not None and not annex_df.empty:
                sample = _annex_top_procedures_by_tariff(annex_df, n=10).to_dict(orient="records")
            else:
                sample = []

            prompt = (
                "You are analyzing a Kenyan SHIF policy dataset extracted from a PDF. "
                "Write 5–8 crisp bullets, factual only, using the aggregates below. "
                "Skip any bullet if a number is 0 or missing.\n\n"
                f"Aggregates:\n{json.dumps({'overview': context_bits, 'annex_top_10': sample}, ensure_ascii=False, indent=2)}"
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

st.markdown("---")
st.caption("This app prioritizes cached dated runs, detects file roles by schema, and stays aligned with your extractor outputs.")
