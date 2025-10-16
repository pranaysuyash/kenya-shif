#!/usr/bin/env python3
"""
Simple Tabula-Only Annex Extractor
Based on user's discovery - much simpler and more effective than complex AI approaches
"""

import pandas as pd
import re
import tabula

pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"

def extract_annex_tabula_simple(path, pages="19-54"):
    """
    Tabula-only, header=None. Handles:
      - col0 = row anchor (number → new entry; NaN → continuation)
      - continuations that appear ABOVE the numbered line (pre-number)
      - continuations that appear BELOW the numbered line (post-number)
    Returns: DataFrame[id, specialty, intervention, tariff_text]
    """
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

    return pd.DataFrame(results, columns=["id","specialty","intervention","tariff_text"])

def main():
    """Run the simple tabula extraction and analyze results"""
    
    print("🔍 SIMPLE TABULA-ONLY ANNEX EXTRACTION")
    print("=" * 50)
    
    # Extract across ALL annex pages and post-process
    print("📊 Extracting annex data with tabula (pages 19-54)...")
    annex_df_all = extract_annex_tabula_simple(pdf_path, pages="19-54")
    
    print(f"   ✅ Raw extraction: {len(annex_df_all)} rows")
    
    # Tidy tariff to numeric
    print("🧹 Post-processing data...")
    annex_df_all["tariff"] = (
        annex_df_all["tariff_text"]
        .fillna("").astype(str)
        .str.replace(r"[^\d.]", "", regex=True)
        .replace("", pd.NA)
        .astype(float)
    )
    annex_df_all = annex_df_all.drop(columns=["tariff_text"])

    # Optional tidying
    annex_df_all["specialty"] = annex_df_all["specialty"].str.strip()
    annex_df_all["intervention"] = (
        annex_df_all["intervention"]
        .str.replace(r"\s+", " ", regex=True)
        .str.replace(r"\s*/\s*", " / ", regex=True)
        .str.replace(r"\s*-\s*", " - ", regex=True)
        .str.strip()
    )
    # Make id a nullable integer
    annex_df_all["id"] = pd.to_numeric(annex_df_all["id"], errors="coerce").astype("Int64")

    # Drop obviously empty rows
    annex_df_all = annex_df_all[(annex_df_all["specialty"] != "") & (annex_df_all["intervention"] != "")]

    # Sort & dedupe
    annex_df_all = annex_df_all.drop_duplicates().sort_values(["specialty","id","intervention"], na_position="last").reset_index(drop=True)
    
    print(f"   ✅ After cleaning: {len(annex_df_all)} unique procedures")
    
    # Analyze results
    specialty_counts = annex_df_all["specialty"].value_counts()
    print(f"\n📊 SIMPLE EXTRACTION RESULTS:")
    print(f"   Total procedures: {len(annex_df_all)}")
    print(f"   Unique specialties: {len(specialty_counts)}")
    print(f"   Procedures with tariffs: {annex_df_all['tariff'].notna().sum()}")
    
    # Show top specialties
    print(f"\n🏥 TOP SPECIALTIES FOUND:")
    for specialty, count in specialty_counts.head(10).items():
        avg_tariff = annex_df_all[annex_df_all["specialty"] == specialty]["tariff"].mean()
        if pd.notna(avg_tariff):
            print(f"   • {specialty}: {count} procedures (avg: KES {avg_tariff:,.0f})")
        else:
            print(f"   • {specialty}: {count} procedures")
    
    # Sample procedures
    print(f"\n📋 SAMPLE PROCEDURES:")
    sample_df = annex_df_all.head(10)
    for _, row in sample_df.iterrows():
        tariff_text = f"KES {row['tariff']:,.0f}" if pd.notna(row['tariff']) else "No tariff"
        print(f"   {row['id']} | {row['specialty']} | {row['intervention'][:60]}... | {tariff_text}")
    
    # Save results
    output_file = f"simple_tabula_annex_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
    annex_df_all.to_csv(output_file, index=False)
    
    print(f"\n📁 Results saved to: {output_file}")
    
    # Summary statistics
    print(f"\n📈 EXTRACTION STATISTICS:")
    print(f"   • Procedures with valid IDs: {annex_df_all['id'].notna().sum()}")
    print(f"   • Procedures with tariffs: {annex_df_all['tariff'].notna().sum()}")
    print(f"   • Average tariff: KES {annex_df_all['tariff'].mean():,.0f}")
    print(f"   • Min tariff: KES {annex_df_all['tariff'].min():,.0f}")
    print(f"   • Max tariff: KES {annex_df_all['tariff'].max():,.0f}")
    
    return annex_df_all

if __name__ == "__main__":
    results = main()