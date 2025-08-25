#!/usr/bin/env python3
"""
Kenyan SHIF PDF extractor with dynamic de-glue, bullet splitting, and structured outputs.
- Pages 1–18: FUND → SERVICE → [Scope | Access Point | Tariff | Access Rules]
- Pages 19–54: Annex (specialty, intervention, tariff)
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
OUT_DIR = Path("outputs"); OUT_DIR.mkdir(parents=True, exist_ok=True)

# ========== Dynamic de-glue (learns vocab from the PDF) ==========
DOC_VOCAB: set[str] = set()
WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']{2,}")

def build_doc_vocab_from_tables(dfs: list[pd.DataFrame]) -> set[str]:
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

def english_score(w: str) -> float:
    if not zipf_frequency: return 0.0
    try:
        z = zipf_frequency(w, "en")
        return max(0.0, z - 3.0)
    except Exception:
        return 0.0

def word_score(w: str) -> float:
    s = 0.0
    wl = w.lower()
    if wl in DOC_VOCAB:
        s += 4.0
    s += english_score(wl)
    if len(w) >= 4:
        s += 0.25
    return s

def segment_glued_token(tok: str, max_parts: int = 4) -> str:
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

def deglue_dynamic(text: str) -> str:
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

def _clean_cell(s): return deglue_dynamic(s)

# ========== Bullets, tariffs, and mapping ==========
def split_bullets(text: str):
    """Split only on bullet glyphs; preserve semicolons inside items."""
    if not isinstance(text, str) or not text.strip(): return []
    t = deglue_dynamic(text)
    if any(sym in t for sym in ("➢", "", "•", "\u2022", "\u25cf", "\u25a0")):
        parts = re.split(r"(?:^|\s)[➢•\u2022\u25cf\u25a0]\s*", t)
        out = []
        for p in parts:
            if not p.strip(): continue
            out.append(deglue_dynamic(p).strip(" -–—·•\t"))
        return out
    return [re.sub(r"[ \t]+", " ", t).strip()]

_MONEY_RE = r"(\d{1,3}(?:,\d{3})+|\d+)"
def extract_money_all(s: str):
    if not isinstance(s, str): return []
    return [float(m.group(1).replace(",", "")) for m in re.finditer(_MONEY_RE, s)]

def primary_amount(tariff_raw: str):
    if not isinstance(tariff_raw, str): return None
    m = re.search(r"KES[^0-9]{0,10}" + _MONEY_RE, tariff_raw, flags=re.IGNORECASE)
    if m: return float(m.group(1).replace(",", ""))
    m = re.search(_MONEY_RE + r"[^0-9]{0,10}KES", tariff_raw, flags=re.IGNORECASE)
    if m: return float(m.group(1).replace(",", ""))
    nums = extract_money_all(tariff_raw)
    return max(nums) if nums else None

def labeled_amount_pairs(tariff_raw: str):
    pairs = []
    if not isinstance(tariff_raw, str) or not tariff_raw.strip(): return pairs
    lines = re.split(r"[➢•\u2022\u25cf\u25a0]|\n|;", tariff_raw.replace("\r", "\n"))
    for ln in lines:
        t = ln.strip()
        if not t: continue
        m = re.search(_MONEY_RE, t)
        if not m: continue
        amt = float(m.group(1).replace(",", ""))
        before = t[:m.start()].strip(" -:()")
        after  = t[m.end():].strip(" -:()")
        label = before if before else after
        label = re.sub(r"\b(KES|KSh|Shillings)\b", "", label, flags=re.IGNORECASE).strip(" -:()")
        if re.search(r"\bLevel\s*\d+\b", label, flags=re.IGNORECASE):
            label = ""
        pairs.append({"label": label, "amount": amt})
    return pairs

def tokset(s): return set(re.findall(r"[a-z0-9]+", (s or "").lower()))
def best_match(a, b):
    at, bt = tokset(a), tokset(b)
    if not at or not bt: return 0.0
    return len(at & bt) / (len(at)**0.5 * len(bt)**0.5)

def map_items_to_pairs(items, pairs, thresh=0.25):
    mapped, used = [], set()
    for it in items:
        best_i, best_s = None, 0.0
        for i, p in enumerate(pairs):
            if i in used: continue
            s = best_match(it, p["label"] or "")
            if s > best_s: best_s, best_i = s, i
        if best_i is not None and best_s >= thresh:
            used.add(best_i)
            mapped.append({"item": it, "label": pairs[best_i]["label"], "amount": pairs[best_i]["amount"]})
        else:
            mapped.append({"item": it, "label": None, "amount": None})
    return mapped

def split_rules_and_map(scope_items, rules_text):
    rules = split_bullets(rules_text)
    if not scope_items or not rules:
        return [[] for _ in scope_items], rules
    assigned = [[] for _ in scope_items]; leftovers = []
    for r in rules:
        scores = [best_match(it, r) for it in scope_items]
        k = int(max(range(len(scores)), key=lambda i: scores[i])) if scores else None
        if k is not None and scores[k] >= 0.25: assigned[k].append(r)
        else: leftovers.append(r)
    return assigned, leftovers

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

    rows = []
    current_fund = None
    current_service = None
    seen_header = False
    current_row = None
    carryover = None

    for df in dfs:
        if df is None or df.empty: continue
        df = df.dropna(how="all", axis=1).reset_index(drop=True)
        df = df.applymap(_clean_cell)

        for _, row in df.iterrows():
            vals = row.tolist()

            lab = _label_row(vals)
            if lab:
                if current_row: rows.append(current_row); current_row = None
                kind, txt = lab
                if kind == "fund": current_fund = txt; current_service = None
                else: current_service = txt
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

# ========== Pages 19–54 Annex ==========
def extract_annex_tabula_simple(pages="19-54"):
    dfs = tabula.read_pdf(PDF_PATH, pages=pages, multiple_tables=True,
                          pandas_options={"header": None}) or []
    results = []; current = None
    for df in dfs:
        if df.empty or df.shape[1] < 3: continue
        df = df.iloc[:, :4]; df.columns = ["num","specialty","intervention","tariff"]
        df["specialty"] = df["specialty"].ffill()
        for _, row in df.iterrows():
            if pd.notna(row["num"]):
                if current: results.append(current)
                current = {
                    "id": int(row["num"]) if str(row["num"]).isdigit() else row["num"],
                    "specialty": str(row["specialty"]).strip(),
                    "intervention": str(row["intervention"]).strip() if pd.notna(row["intervention"]) else "",
                    "tariff": str(row["tariff"]).strip() if pd.notna(row["tariff"]) else None
                }
            else:
                if current and pd.notna(row["intervention"]):
                    current["intervention"] += " " + str(row["intervention"]).strip()
                if current and pd.notna(row["tariff"]):
                    current["tariff"] = str(row["tariff"]).strip()
    if current: results.append(current)
    out = pd.DataFrame(results)
    if not out.empty:
        out["tariff"] = (
            out["tariff"].fillna("").astype(str)
            .str.replace(r"[^\d.]", "", regex=True)
            .replace("", pd.NA)
            .astype(float)
        )
    return out

# ========== Build structured outputs ==========
def build_structures(rules_df: pd.DataFrame):
    df = rules_df.copy()
    for c in ["fund","service","scope","access_point","tariff_raw","access_rules"]:
        df[c] = df[c].apply(deglue_dynamic)

    wide, exploded, structured = [], [], []
    for _, r in df.iterrows():
        fund, svc = r["fund"], r["service"]
        scope, ap, tarif, rule = r["scope"], r["access_point"], r["tariff_raw"], r["access_rules"]

        scope_items = split_bullets(scope)
        tariff_pairs = labeled_amount_pairs(tarif)
        block_tariff = primary_amount(tarif)
        item_rules, block_rule_left = split_rules_and_map(scope_items, rule)
        mapping = "itemized" if (scope_items and tariff_pairs and any(p["label"] for p in tariff_pairs)) else "block"
        item_tariffs = map_items_to_pairs(scope_items, tariff_pairs) if mapping == "itemized" \
                       else [{"item": it, "label": None, "amount": None} for it in scope_items]

        wide.append({
            "fund": fund, "service": svc, "access_point": ap,
            "scope_items": scope_items, "tariff_pairs": tariff_pairs,
            "block_tariff": block_tariff,
            "rules_items": item_rules, "rules_block": block_rule_left,
            "mapping_type": mapping,
            "tariff_raw": tarif, "access_rules_raw": rule
        })

        if scope_items:
            for idx, it in enumerate(scope_items):
                exploded.append({
                    "fund": fund, "service": svc, "scope_item": it, "access_point": ap,
                    "item_label": item_tariffs[idx]["label"], "item_tariff": item_tariffs[idx]["amount"],
                    "block_tariff": block_tariff,
                    "item_rules": item_rules[idx],
                    "block_rules": block_rule_left,
                    "mapping_type": mapping
                })
        else:
            exploded.append({
                "fund": fund, "service": svc, "scope_item": "", "access_point": ap,
                "item_label": None, "item_tariff": None, "block_tariff": block_tariff,
                "item_rules": [], "block_rules": block_rule_left, "mapping_type": mapping
            })

        if mapping == "itemized" and scope_items:
            for idx, it in enumerate(scope_items):
                structured.append({
                    "fund": fund, "service": svc, "access_point": ap, "mapping_type": mapping,
                    "scope_item": it, "item_label": item_tariffs[idx]["label"], "item_tariff": item_tariffs[idx]["amount"],
                    "block_tariff": block_tariff,
                    "item_rules": "; ".join(item_rules[idx]),
                    "block_rules": "; ".join(block_rule_left),
                    "tariff_raw": tarif, "access_rules_raw": rule
                })
        else:
            structured.append({
                "fund": fund, "service": svc, "access_point": ap, "mapping_type": mapping,
                "scope_item": "; ".join(scope_items) if scope_items else "",
                "item_label": None, "item_tariff": None,
                "block_tariff": block_tariff,
                "item_rules": "",
                "block_rules": "; ".join(block_rule_left),
                "tariff_raw": tarif, "access_rules_raw": rule
            })

    return pd.DataFrame(wide), pd.DataFrame(exploded), pd.DataFrame(structured)

# ========== Debug preview helpers ==========
def debug_preview_first_block(wide_df: pd.DataFrame, exploded_df: pd.DataFrame):
    print("\n--- DEBUG: First service block (wide view) ---")
    if wide_df.empty:
        print("No rows.")
        return
    w0 = wide_df.iloc[0]
    print("Fund:   ", w0["fund"])
    print("Service:", w0["service"])
    print("Access Point:", w0["access_point"])
    print("Block Tariff:", w0["block_tariff"])
    print("Scope bullets:")
    for i, it in enumerate(w0["scope_items"], 1):
        print(f"  {i}. {it}")
    print("Rules (block-level):", w0["rules_block"])

    print("\n--- DEBUG: First 8 exploded rows ---")
    print(exploded_df.head(8)[["fund","service","scope_item","item_label","item_tariff","block_tariff"]])

# ========== Analysis and Summary Functions ==========
def analyze_extraction_results(rules_df, wide_df, exploded_df, structured_df, annex_df):
    """Provide comprehensive analysis of extraction results"""
    
    print("\n🎯 COMPREHENSIVE EXTRACTION ANALYSIS")
    print("=" * 60)
    
    # Pages 1-18 Analysis
    if not rules_df.empty:
        funds = rules_df['fund'].value_counts()
        services = rules_df['service'].value_counts()
        
        print(f"\n📊 PAGES 1-18 (Policy Structure):")
        print(f"   • Total raw entries: {len(rules_df)}")
        print(f"   • Structured wide format: {len(wide_df)}")
        print(f"   • Exploded items: {len(exploded_df)}")
        print(f"   • Final structured: {len(structured_df)}")
        print(f"   • Healthcare funds: {len(funds)}")
        print(f"   • Service categories: {len(services)}")
        
        print(f"\n🏥 TOP HEALTHCARE FUNDS:")
        for fund, count in funds.head(5).items():
            if fund and str(fund) != 'nan':
                print(f"   • {fund}: {count} entries")
        
        # Tariff analysis for pages 1-18
        tariffs_p1_18 = []
        for _, row in structured_df.iterrows():
            if row.get('item_tariff'):
                tariffs_p1_18.append(row['item_tariff'])
            elif row.get('block_tariff'):
                tariffs_p1_18.append(row['block_tariff'])
        
        if tariffs_p1_18:
            print(f"\n💰 PAGES 1-18 TARIFF ANALYSIS:")
            print(f"   • Services with pricing: {len(tariffs_p1_18)}")
            print(f"   • Price range: KES {min(tariffs_p1_18):,.0f} - {max(tariffs_p1_18):,.0f}")
            print(f"   • Average price: KES {sum(tariffs_p1_18)/len(tariffs_p1_18):,.0f}")
    
    # Pages 19-54 Analysis (Annex)
    if not annex_df.empty:
        specialties = annex_df['specialty'].value_counts()
        tariffs_annex = annex_df['tariff'].dropna()
        
        print(f"\n📊 PAGES 19-54 (Annex Procedures):")
        print(f"   • Total procedures: {len(annex_df)}")
        print(f"   • Medical specialties: {len(specialties)}")
        print(f"   • Procedures with tariffs: {len(tariffs_annex)}")
        
        if len(tariffs_annex) > 0:
            print(f"   • Price range: KES {tariffs_annex.min():,.0f} - {tariffs_annex.max():,.0f}")
            print(f"   • Average price: KES {tariffs_annex.mean():,.0f}")
        
        print(f"\n🏥 TOP MEDICAL SPECIALTIES:")
        for specialty, count in specialties.head(10).items():
            if specialty and str(specialty) != 'nan':
                avg_tariff = annex_df[annex_df['specialty'] == specialty]['tariff'].mean()
                if pd.notna(avg_tariff):
                    print(f"   • {specialty}: {count} procedures (avg: KES {avg_tariff:,.0f})")
                else:
                    print(f"   • {specialty}: {count} procedures")
    
    # Combined Analysis
    total_services = len(structured_df) + len(annex_df)
    total_tariffs = len(tariffs_p1_18) + len(tariffs_annex) if 'tariffs_annex' in locals() else len(tariffs_p1_18)
    
    print(f"\n🎯 COMBINED TOTALS:")
    print(f"   • Total services/procedures: {total_services}")
    print(f"   • Total with pricing: {total_tariffs}")
    print(f"   • Coverage: {(total_tariffs/total_services)*100:.1f}% have pricing data")

# ========== Main ==========
def main():
    """Main execution function with comprehensive analysis"""
    
    print("🚀 KENYAN SHIF COMPREHENSIVE PDF EXTRACTOR")
    print("=" * 60)
    print("   📊 Pages 1-18: Policy structure with advanced text processing")  
    print("   📊 Pages 19-54: Annex procedures with your proven simple tabula")
    print("   🔧 Features: Dynamic de-glue, bullet splitting, tariff mapping")
    
    # Read raw tables once (to build vocab)
    print("\n📚 Building vocabulary from document...")
    raw_dfs = read_tables_raw("1-18")
    global DOC_VOCAB
    DOC_VOCAB = build_doc_vocab_from_tables(raw_dfs)
    print(f"   ✅ Learned {len(DOC_VOCAB)} vocabulary terms")

    # Extract pages 1–18 with dynamic cleaning
    print("\n📊 PROCESSING PAGES 1-18 (Policy Structure)...")
    rules_df = extract_rules_p1_18("1-18")
    OUT_DIR.joinpath("rules_p1_18_raw.csv").write_text(rules_df.to_csv(index=False))
    
    # Build structured formats
    print("   🔧 Building structured formats...")
    wide_df, exploded_df, structured_df = build_structures(rules_df)
    wide_df.to_csv(OUT_DIR / "rules_p1_18_structured_wide.csv", index=False)
    exploded_df.to_csv(OUT_DIR / "rules_p1_18_structured_exploded.csv", index=False)
    structured_df.to_csv(OUT_DIR / "rules_p1_18_structured.csv", index=False)
    print(f"   ✅ Pages 1–18 complete: raw={len(rules_df)}, wide={len(wide_df)}, exploded={len(exploded_df)}")

    # Extract Annex (19–54) using your proven simple tabula approach
    print("\n📊 PROCESSING PAGES 19-54 (Annex Procedures)...")
    print("   🔧 Using proven simple tabula approach...")
    annex_df = extract_annex_tabula_simple("19-54")
    annex_df.to_csv(OUT_DIR / "annex_surgical_tariffs_all.csv", index=False)
    print(f"   ✅ Annex complete: {len(annex_df)} procedures")

    # Show debug preview
    debug_preview_first_block(wide_df, exploded_df)
    
    # Comprehensive analysis
    analyze_extraction_results(rules_df, wide_df, exploded_df, structured_df, annex_df)
    
    print(f"\n📁 ALL RESULTS SAVED TO: {OUT_DIR}")
    print("   📄 rules_p1_18_raw.csv - Raw extracted data from pages 1-18")
    print("   📄 rules_p1_18_structured_wide.csv - Wide format with arrays")  
    print("   📄 rules_p1_18_structured_exploded.csv - One row per scope item")
    print("   📄 rules_p1_18_structured.csv - Final structured format")
    print("   📄 annex_surgical_tariffs_all.csv - All annex procedures (pages 19-54)")
    
    return {
        'pages_1_18': {
            'raw': rules_df,
            'wide': wide_df, 
            'exploded': exploded_df,
            'structured': structured_df
        },
        'pages_19_54': {
            'annex': annex_df
        },
        'summary': {
            'total_policy_entries': len(rules_df),
            'total_structured_services': len(structured_df),
            'total_annex_procedures': len(annex_df),
            'total_combined': len(structured_df) + len(annex_df)
        }
    }

if __name__ == "__main__":
    results = main()