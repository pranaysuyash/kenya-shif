#!/usr/bin/env python3
"""
Simple working extraction with basic deglue that produces clean output
"""

import re
import pandas as pd
import tabula
from pathlib import Path

PDF_PATH = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
OUT_DIR = Path("outputs_clean"); OUT_DIR.mkdir(parents=True, exist_ok=True)

def simple_deglue(text: str) -> str:
    """Simple but effective deglue that handles common patterns"""
    if not isinstance(text, str) or not text.strip():
        return ""
    
    # Basic cleanup
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"[ \t]+", " ", text).strip()
    
    # Common word fixes - handle the most problematic cases
    fixes = {
        "Healtheducationandwellness": "Health education and wellness",
        "supportas": "support as", 
        "sup portas": "support as",
        "Prescribedlaboratory": "Prescribed laboratory",
        "Pre scri bed": "Prescribed",
        "Basicradiological": "Basic radiological",
        "drugadministration": "drug administration", 
        "ManagementofNCDs": "Management of NCDs",
        "Man age men tofNCDs": "Management of NCDs",
        "neglectedtropical": "neglected tropical",
        "familyplanning": "family planning",
        "family plan ning": "family planning",
        "antimalarials": "anti-malarials",
        "anti mal ari als": "anti-malarials",
        "antiTBs": "anti-TBs",
        "guidelines": "guidelines",
        "guide lines": "guidelines",
        "Eachfacilitywillbemappedtoa": "Each facility will be mapped to a",
        "bemappedtoa": "be mapped to a",
        "Allregisteredhouseholdswillbe": "All registered households will be",
        "household swillbe": "households will be",
        "all ocated": "allocated",
        "all ocat ion": "allocation",
        "DistributionoftheFundsshallbe": "Distribution of the Funds shall be",
        "Distributionof the Fund sshallbe": "Distribution of the Funds shall be",
        "associatedtests": "associated tests",
        "andongoingsupport": "and ongoing support", 
        "radiologicalexaminations": "radiological examinations",
    }
    
    # Apply fixes
    for wrong, right in fixes.items():
        text = text.replace(wrong, right)
    
    # Fix spacing around punctuation
    text = re.sub(r",(?=\S)", ", ", text)
    text = re.sub(r";(?=\S)", "; ", text)
    text = re.sub(r":(?=\S)", ": ", text)
    text = re.sub(r"(?<=\w)/(?=\w)", " / ", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    text = re.sub(r"[ \t]+", " ", text).strip()
    
    return text

def _clean_cell(s): 
    return simple_deglue(str(s)) if pd.notna(s) else ""

# Extraction logic (same as manual but with simple deglue)
FUND_RE = re.compile(r"FUND$", re.I)
SECTION_RE = re.compile(r"[A-Z0-9 ,&()'/-]{6,}(SERVICES|PACKAGE)$")
TOKENS = ["scope","access point","tariff","access rules"]

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

def extract_rules_clean(pages="1-18"):
    dfs = read_tables_raw(pages)
    
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

if __name__ == "__main__":
    rules_df = extract_rules_clean("1-18")
    OUT_DIR.joinpath("rules_clean.csv").write_text(rules_df.to_csv(index=False))
    print(f"✅ Clean extraction: {len(rules_df)} rows")
    print(f"First scope: {rules_df.iloc[0]['scope'][:150]}")
    print(f"Saved to: {OUT_DIR}/rules_clean.csv")