#!/usr/bin/env python3
"""
Fixed manual.ipynb logic for pages 1-18 extraction
"""

def _extract_rules_pdfplumber_p1_18_FIXED(self, pdf_path: str):
    """Fixed manual.ipynb-equivalent extractor for pages 1–18.
    
    Uses tabula with lattice=True first, then stream=True fallback.
    Produces columns: fund, service, scope, access_point, tariff_raw, access_rules
    """
    import re
    
    try:
        import tabula
    except ImportError:
        print("❌ tabula-py not available")
        return pd.DataFrame()
        
    # Use exact manual.ipynb logic
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

    def _clean_cell(s):
        return self._deglue_dynamic(s) if isinstance(s, str) else (s or "")

    # Try lattice first, then stream (exact manual logic)
    try:
        dfs = tabula.read_pdf(pdf_path, pages="1-18", lattice=True, multiple_tables=True,
                            pandas_options={"header": None}) or []
        print(f"   📊 Extracted {len(dfs)} tables with lattice method")
    except Exception as e:
        print(f"   ⚠️ Lattice method failed: {e}")
        dfs = []
        
    if not dfs:
        try:
            dfs = tabula.read_pdf(pdf_path, pages="1-18", stream=True, multiple_tables=True,
                                pandas_options={"header": None}) or []
            print(f"   📊 Extracted {len(dfs)} tables with stream method")
        except Exception as e:
            print(f"   ❌ Stream method failed: {e}")
            dfs = []

    if not dfs:
        print("   ❌ No tables extracted from pages 1-18")
        return pd.DataFrame()

    # Build vocabulary (manual logic)
    doc_vocab = set()
    for df in dfs:
        if df is None or df.empty: continue
        try:
            for val in df.values.ravel():
                if isinstance(val, str):
                    for w in re.findall(r"[A-Za-z][A-Za-z\-']{2,}", val):
                        doc_vocab.add(w.lower())
        except Exception:
            continue

    print(f"   📚 Built document vocabulary: {len(doc_vocab)} terms")

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

            # Check for fund/service labels
            lab = _label_row(vals)
            if lab:
                if current_row: 
                    rows.append(current_row)
                    current_row = None
                kind, txt = lab
                if kind == "fund": 
                    current_fund = txt
                    current_service = None
                    print(f"   💰 Found fund: {txt}")
                else: 
                    current_service = txt
                    print(f"   🏥 Found service: {txt}")
                seen_header = False
                continue

            # Check for header row
            if _is_header_row(vals):
                seen_header = True
                if current_row: 
                    rows.append(current_row)
                    current_row = None
                print(f"   📋 Found header row")
                continue

            if not seen_header: 
                continue

            # Pad to 4 columns
            vals = vals[:4] + [""]*(4-len(vals))
            scope, ap, tarif, rule = vals
            if not any([scope, ap, tarif, rule]): 
                continue

            # Handle carryover from previous iteration
            if carryover and scope and not any([ap, tarif, rule]):
                carryover["scope"] = (carryover["scope"] + " " + scope).strip()
                continue
            if carryover:
                rows.append(carryover)
                carryover = None

            empties = sum(1 for v in (scope, ap, tarif, rule) if not v)
            
            if current_row is None:
                # Start new row
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
                    # Continuation line - merge
                    if scope: current_row["scope"] = (current_row["scope"] + " " + scope).strip()
                    if ap:    current_row["access_point"] = (current_row["access_point"] + " " + ap).strip()
                    if tarif: current_row["tariff_raw"] = (current_row["tariff_raw"] + " " + tarif).strip()
                    if rule:  current_row["access_rules"] = (current_row["access_rules"] + " " + rule).strip()
                else:
                    # New row - save current and start new
                    rows.append(current_row)
                    current_row = {
                        "fund": current_fund,
                        "service": current_service,
                        "scope": scope,
                        "access_point": ap,
                        "tariff_raw": tarif,
                        "access_rules": rule
                    }

        # End of this df - carry over current_row
        if current_row: 
            carryover = current_row
            current_row = None

    # Add final carryover
    if carryover: 
        rows.append(carryover)

    print(f"   ✅ Extracted {len(rows)} policy services")

    # Convert to DataFrame and add tariff_num
    import pandas as pd
    result_df = pd.DataFrame(rows)
    if not result_df.empty and 'tariff_raw' in result_df.columns:
        def extract_primary_amount(tariff_raw):
            if not isinstance(tariff_raw, str): return None
            # Look for KES amounts
            m = re.search(r"KES[^0-9]{0,10}(\d{1,3}(?:,\d{3})+|\d+)", tariff_raw, flags=re.IGNORECASE)
            if m: return float(m.group(1).replace(",", ""))
            m = re.search(r"(\d{1,3}(?:,\d{3})+|\d+)[^0-9]{0,10}KES", tariff_raw, flags=re.IGNORECASE)
            if m: return float(m.group(1).replace(",", ""))
            # Just look for numbers
            nums = re.findall(r"(\d{1,3}(?:,\d{3})+|\d+)", tariff_raw)
            if nums:
                return max(float(n.replace(",", "")) for n in nums)
            return None
            
        result_df["tariff_num"] = result_df["tariff_raw"].apply(extract_primary_amount)

    return result_df

# Test the function
if __name__ == "__main__":
    print("🧪 Testing manual logic fix...")