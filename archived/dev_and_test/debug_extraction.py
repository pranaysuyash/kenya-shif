import pandas as pd
import re
import tabula

pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"

# Test extraction to see what services are being detected
def debug_extraction():
    FUND_RE = re.compile(r"FUND$", re.I)
    SECTION_RE = re.compile(r"[A-Z0-9 ,&()'/-]{6,}(SERVICES|PACKAGE)$")
    
    dfs = tabula.read_pdf(pdf_path, pages="1-18", lattice=True, multiple_tables=True,
                          pandas_options={"header": None}) or []
    
    print(f"Found {len(dfs)} tables")
    
    services_found = []
    funds_found = []
    
    for i, df in enumerate(dfs):
        if df is None or df.empty:
            continue
        
        # Clean the dataframe
        df = df.dropna(how="all", axis=1).reset_index(drop=True)
        
        for _, row in df.iterrows():
            vals = row.tolist()
            non_empty = [str(v).strip() for v in vals if pd.notna(v) and str(v).strip()]
            
            if len(non_empty) == 1:
                txt = non_empty[0]
                if FUND_RE.search(txt):
                    funds_found.append(txt)
                    print(f"Table {i}: FUND found: {txt}")
                elif SECTION_RE.search(txt) and "fund" not in txt.lower():
                    services_found.append(txt)
                    print(f"Table {i}: SERVICE found: {txt}")
    
    print(f"\nTotal funds: {len(funds_found)}")
    print(f"Total services: {len(services_found)}")
    return funds_found, services_found

funds, services = debug_extraction()
print("\n=== All Services Found ===")
for s in services:
    print(f"  - {s}")