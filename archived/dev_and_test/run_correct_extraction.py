#!/usr/bin/env python3
"""
Run the CORRECT extraction from manual.ipynb
"""

import re, math
import pandas as pd
import tabula
from pathlib import Path

# OPTIONAL: improves word splitting if installed (pip install wordfreq)
try:
    from wordfreq import zipf_frequency
except Exception:
    zipf_frequency = None

PDF_PATH = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
OUT_DIR = Path("outputs_corrected")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ========== Dynamic de-glue (learns vocab from the PDF) ==========
DOC_VOCAB = set()
WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']{2,}")

def build_doc_vocab_from_tables(dfs):
    vocab = set()
    for df in dfs or []:
        try:
            for val in df.values.ravel():
                if not isinstance(val, str): continue
                for w in WORD_RE.findall(val):
                    vocab.add(w.lower())
        except Exception:
            continue
    return vocab

def english_score(w):
    if not zipf_frequency: return 0.0
    try:
        z = zipf_frequency(w, "en")
        return max(0.0, z - 3.0)
    except Exception:
        return 0.0

def word_score(w):
    s = 0.0
    wl = w.lower()
    if wl in DOC_VOCAB:
        s += 4.0
    s += english_score(wl)
    if len(w) >= 4:
        s += 0.25
    return s

def segment_glued_token(tok, max_parts=4):
    """DP split of a long alpha token into likely words."""
    if not tok or len(tok) < 8: return tok
    if not re.fullmatch(r"[A-Za-z][A-Za-z\-']+", tok): return tok
    n = len(tok)
    dp = [[(-math.inf, []) for _ in range(max_parts + 1)] for __ in range(n + 1)]
    dp[0][0] = (0.0, [])
    for i in range(1, n + 1):
        for k in range(1, max_parts + 1):
            for L in range(3, min(20, i) + 1):
                j = i - L
                piece = tok[j:i]
                sc = word_score(piece)
                if sc <= 0: continue
                prev = dp[j][k - 1][0]
                if prev == -math.inf: continue
                cand = prev + sc
                if cand > dp[i][k][0]:
                    dp[i][k] = (cand, dp[j][k - 1][1] + [piece])
    best_score, best_parts = -math.inf, None
    for k in range(2, max_parts + 1):
        sc, parts = dp[n][k]
        if sc > best_score:
            best_score, best_parts = sc, parts
    if best_parts:
        whole = word_score(tok)
        if best_score > max(whole, 0.5):
            return " ".join(best_parts)
    return tok

WORD_OR_OTHER = re.compile(r"[A-Za-z][A-Za-z\-']+|[0-9]+|[^\sA-Za-z0-9]+")

def deglue_dynamic(text):
    """Normalize spacing and segment glued words, preserving punctuation."""
    if not isinstance(text, str): return ""
    t = text.replace("\r", " ").replace("\n", " ")
    t = re.sub(r"[ \t]+", " ", t)
    # space after punctuation if missing, and around slashes
    t = re.sub(r",(?=\S)", ", ", t)
    t = re.sub(r";(?=\S)", "; ", t)
    t = re.sub(r":(?=\S)", ": ", t)
    t = re.sub(r"(?<=\w)/(?=\w)", " / ", t)

    parts = WORD_OR_OTHER.findall(t)
    segged = []
    for p in parts:
        if re.fullmatch(r"[A-Za-z][A-Za-z\-']+", p) and len(p) >= 8:
            segged.append(segment_glued_token(p))
        else:
            segged.append(p)
    # Reassemble with smart spacing
    s = " ".join(segged)
    s = re.sub(r"\s+([,.;:])", r"\1", s)       # no space before punctuation
    s = re.sub(r"([,;:])(?=\S)", r"\1 ", s)    # ensure 1 space after
    s = re.sub(r"[ \t]+", " ", s).strip()
    return s

def _clean_cell(s): 
    return deglue_dynamic(s)

# ========== Pages 1–18 extraction ==========
FUND_RE    = re.compile(r"FUND$", re.I)
SECTION_RE = re.compile(r"[A-Z0-9 ,&()'/-]{6,}(SERVICES|PACKAGE)$")
TOKENS     = ["scope","access point","tariff","access rules"]

def _is_header_row(vals):
    joined = " ".join(v.lower() for v in vals if v)
    return all(tok in joined for tok in TOKENS)

def _label_row(vals):
    non = [v for v in vals if v]
    if len(non) != 1: return None
    txt = non[0]
    if FUND_RE.search(txt): return ("fund", txt)
    if SECTION_RE.search(txt) and "fund" not in txt.lower(): return ("section", txt)
    return None

def read_tables_raw(pages="1-18"):
    dfs = tabula.read_pdf(PDF_PATH, pages=pages, lattice=True, multiple_tables=True,
                          pandas_options={"header": None}) or []
    if not dfs:
        dfs = tabula.read_pdf(PDF_PATH, pages=pages, stream=True, multiple_tables=True,
                              pandas_options={"header": None}) or []
    return dfs

def extract_rules_p1_18(pages="1-18"):
    global DOC_VOCAB
    dfs = read_tables_raw(pages)
    DOC_VOCAB = build_doc_vocab_from_tables(dfs)  # learn vocab
    print(f"Built vocabulary: {len(DOC_VOCAB)} terms")

    rows = []
    current_fund = None
    current_service = None
    seen_header = False
    current_row = None
    carryover = None

    for df in dfs:
        if df is None or df.empty: continue
        df = df.dropna(how="all", axis=1).reset_index(drop=True)
        df = df.map(_clean_cell)

        for _, row in df.iterrows():
            vals = row.tolist()

            lab = _label_row(vals)
            if lab:
                if current_row: rows.append(current_row); current_row = None
                kind, txt = lab
                if kind == "fund": 
                    current_fund = txt
                    current_service = None
                    print(f"  Found FUND: {txt}")
                else: 
                    current_service = txt
                    print(f"  Found SERVICE: {txt}")
                seen_header = False
                continue

            if _is_header_row(vals):
                seen_header = True
                if current_row: rows.append(current_row); current_row = None
                continue

            if not seen_header: continue

            vals = vals[:4] + [""]*(4-len(vals))
            scope, ap, tarif, rule = vals
            if not any([scope, ap, tarif, rule]): continue

            if carryover and scope and not any([ap, tarif, rule]):
                carryover["scope"] = (carryover["scope"] + " " + scope).strip()
                continue
            if carryover:
                rows.append(carryover); carryover = None

            empties = sum(1 for v in (scope, ap, tarif, rule) if not v)
            if current_row is None:
                current_row = {
                    "fund": current_fund,
                    "service": current_service,
                    "scope": scope,
                    "access_point": ap,
                    "tariff_raw": tarif,
                    "access_rules": rule
                }
            else:
                if empties >= 2:
                    if scope: current_row["scope"] = (current_row["scope"] + " " + scope).strip()
                    if ap:    current_row["access_point"] = (current_row["access_point"] + " " + ap).strip()
                    if tarif: current_row["tariff_raw"] = (current_row["tariff_raw"] + " " + tarif).strip()
                    if rule:  current_row["access_rules"] = (current_row["access_rules"] + " " + rule).strip()
                else:
                    rows.append(current_row)
                    current_row = {
                        "fund": current_fund,
                        "service": current_service,
                        "scope": scope,
                        "access_point": ap,
                        "tariff_raw": tarif,
                        "access_rules": rule
                    }

        if current_row: carryover = current_row; current_row = None

    if carryover: rows.append(carryover)
    return pd.DataFrame(rows)

# ========== Pages 19–54 Annex (EXACT from provided code) ==========
def extract_annex_tabula_simple(path, pages="19-54"):
    dfs = tabula.read_pdf(
        path,
        pages=pages,
        multiple_tables=True,
        pandas_options={"header": None}
    ) or []

    results = []

    for df in dfs:
        if df is None or df.empty or df.shape[1] < 3:
            continue

        df = df.iloc[:, :4].copy()
        df.columns = ["num","specialty","intervention","tariff"]

        # forward fill specialty
        df["specialty"] = df["specialty"].ffill()

        merged_rows = []
        current = None
        pre_buffer = []  # holds continuation lines that appear BEFORE a numbered row

        for _, row in df.iterrows():
            num = row["num"]
            spec = str(row["specialty"]).strip() if pd.notna(row["specialty"]) else ""
            interv = str(row["intervention"]).strip() if pd.notna(row["intervention"]) else ""
            tariff_raw = str(row["tariff"]).strip() if pd.notna(row["tariff"]) else ""

            if pd.notna(num):  # start of a new entry
                # flush previous
                if current:
                    merged_rows.append(current)

                # stitch any text collected ABOVE the number into the new intervention
                start_text = " ".join(pre_buffer + ([interv] if interv else []))
                pre_buffer = []  # reset buffer

                current = {
                    "id": int(num) if str(num).isdigit() else num,
                    "specialty": spec,
                    "intervention": start_text.strip(),
                    "tariff_text": tariff_raw
                }
            else:
                # continuation row
                if current is None:
                    # no current yet → this line belongs to the NEXT numbered row
                    if interv:
                        pre_buffer.append(interv)
                    # sometimes tariff appears on a pre-line, keep last seen
                    if tariff_raw:
                        # stash on buffer end marker so it can override later if needed
                        pre_buffer.append(f"[TARIFF:{tariff_raw}]")
                    continue

                if interv:
                    current["intervention"] = (current["intervention"] + " " + interv).strip()
                if tariff_raw:
                    current["tariff_text"] = tariff_raw

        if current:
            merged_rows.append(current)

        # clean any accidental tariff markers in pre_buffer merges
        for r in merged_rows:
            if "[TARIFF:" in r["intervention"]:
                # drop those markers from text; tariff already handled by numbered line normally
                r["intervention"] = re.sub(r"\[TARIFF:.*?\]", "", r["intervention"]).strip()

        results.extend(merged_rows)

    df_out = pd.DataFrame(results, columns=["id","specialty","intervention","tariff_text"])
    
    # tidy tariff to numeric
    df_out["tariff"] = (
        df_out["tariff_text"]
        .fillna("").astype(str)
        .str.replace(r"[^\d.]", "", regex=True)
        .replace("", pd.NA)
        .astype(float)
    )
    df_out = df_out.drop(columns=["tariff_text"])

    # optional tidying
    df_out["specialty"] = df_out["specialty"].str.strip()
    df_out["intervention"] = (
        df_out["intervention"]
        .str.replace(r"\s+", " ", regex=True)
        .str.replace(r"\s*/\s*", " / ", regex=True)
        .str.replace(r"\s*-\s*", " - ", regex=True)
        .str.strip()
    )
    # make id a nullable integer
    df_out["id"] = pd.to_numeric(df_out["id"], errors="coerce").astype("Int64")

    # drop obviously empty rows
    df_out = df_out[(df_out["specialty"] != "") & (df_out["intervention"] != "")]

    # sort & dedupe
    df_out = df_out.drop_duplicates().sort_values(["specialty","id","intervention"], na_position="last").reset_index(drop=True)
    
    return df_out

# ========== Main ==========
if __name__ == "__main__":
    print("Running CORRECT extraction from manual.ipynb...")
    
    # Extract pages 1–18
    print("\n📊 Extracting Pages 1-18...")
    rules_df = extract_rules_p1_18("1-18")
    rules_df.to_csv(OUT_DIR / "rules_p1_18_raw.csv", index=False)
    print(f"✅ Pages 1–18 extracted: {len(rules_df)} rows")
    
    # Check service distribution
    service_counts = rules_df['service'].value_counts()
    print(f"\n📈 Service distribution:")
    print(service_counts.to_string())
    
    # Extract annex
    print("\n📊 Extracting Pages 19-54 (Annex)...")
    annex_df = extract_annex_tabula_simple(PDF_PATH, "19-54")
    annex_df.to_csv(OUT_DIR / "annex_procedures.csv", index=False)
    print(f"✅ Annex extracted: {len(annex_df)} procedures")
    
    print(f"\n✅ All outputs saved to: {OUT_DIR}")
    print(f"   • Policy rules: {len(rules_df)} rows")
    print(f"   • Annex procedures: {len(annex_df)} rows")