#!/usr/bin/env python3
"""
Comprehensive Data Consistency Verification Script
Checks reproducibility and data integrity across multiple analyzer runs
"""

import pandas as pd
import os
import glob
import json
from pathlib import Path
from collections import defaultdict
import hashlib

def get_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def count_csv_rows(filepath):
    """Count rows in CSV file (excluding header)"""
    try:
        df = pd.read_csv(filepath)
        return len(df)
    except Exception as e:
        return f"ERROR: {str(e)}"

def get_run_folders():
    """Get all output run folders"""
    base_dir = "/Users/pranay/Projects/adhoc_projects/drrishi/final_submission"
    folders = sorted(glob.glob(f"{base_dir}/outputs_run_*/"))
    return [Path(f).name for f in folders]

def check_1_count_files():
    """Check 1: Count Files Across Runs"""
    print("\n" + "="*80)
    print("CHECK 1: COUNT FILES ACROSS RUNS")
    print("="*80)

    base_dir = "/Users/pranay/Projects/adhoc_projects/drrishi/final_submission"
    runs = get_run_folders()

    files_to_check = [
        'ai_contradictions.csv',
        'ai_gaps.csv',
        'coverage_gaps_analysis.csv',
        'comprehensive_gaps_analysis.csv',
        'all_gaps_before_dedup.csv'
    ]

    results = []
    for run in runs:
        run_path = os.path.join(base_dir, run)
        row = {'run': run}
        for filename in files_to_check:
            filepath = os.path.join(run_path, filename)
            row[filename] = count_csv_rows(filepath)
        results.append(row)

    df_results = pd.DataFrame(results)
    print("\nRow Counts Across All Runs:")
    print(df_results.to_string(index=False))

    # Save to CSV
    output_file = os.path.join(base_dir, 'verification_row_counts.csv')
    df_results.to_csv(output_file, index=False)
    print(f"\nSaved to: {output_file}")

    return df_results

def check_2_contradiction_consistency():
    """Check 2: Verify Contradiction Consistency"""
    print("\n" + "="*80)
    print("CHECK 2: VERIFY CONTRADICTION CONSISTENCY")
    print("="*80)

    base_dir = "/Users/pranay/Projects/adhoc_projects/drrishi/final_submission"

    # Load from specific runs mentioned
    runs_to_check = ['outputs_run_20251017_142114',
                     'outputs_run_20251017_135257',
                     'outputs_run_20251017_132228',
                     'outputs_run_20251017_155604']

    contradictions_data = {}
    for run in runs_to_check:
        filepath = os.path.join(base_dir, run, 'ai_contradictions.csv')
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            contradictions_data[run] = df
            print(f"\n{run}: {len(df)} contradictions")
            if 'contradiction_id' in df.columns:
                print(f"  IDs: {sorted(df['contradiction_id'].tolist())}")
            if 'clinical_severity' in df.columns:
                print(f"  Severities: {df['clinical_severity'].tolist()}")

    # Check consistency across runs
    if contradictions_data:
        first_run = list(contradictions_data.keys())[0]
        first_df = contradictions_data[first_run]

        print("\n--- CONSISTENCY CHECK ---")
        all_consistent = True

        for run, df in contradictions_data.items():
            if run == first_run:
                continue

            # Check if same IDs
            if 'contradiction_id' in df.columns and 'contradiction_id' in first_df.columns:
                ids_match = sorted(df['contradiction_id'].tolist()) == sorted(first_df['contradiction_id'].tolist())
                print(f"\n{run} vs {first_run}:")
                print(f"  Same contradiction IDs: {ids_match}")
                if not ids_match:
                    all_consistent = False
                    print(f"    Run 1 IDs: {sorted(first_df['contradiction_id'].tolist())}")
                    print(f"    Run 2 IDs: {sorted(df['contradiction_id'].tolist())}")

            # Check clinical severity consistency
            if 'clinical_severity' in df.columns and 'clinical_severity' in first_df.columns:
                # Merge on contradiction_id to compare
                merged = pd.merge(first_df[['contradiction_id', 'clinical_severity']],
                                df[['contradiction_id', 'clinical_severity']],
                                on='contradiction_id',
                                suffixes=('_first', '_current'))
                severity_match = (merged['clinical_severity_first'] == merged['clinical_severity_current']).all()
                print(f"  Same clinical_severity values: {severity_match}")
                if not severity_match:
                    all_consistent = False
                    print(merged[merged['clinical_severity_first'] != merged['clinical_severity_current']])

        print(f"\n{'✓' if all_consistent else '✗'} Overall Consistency: {all_consistent}")

        # Save detailed comparison
        comparison_file = os.path.join(base_dir, 'verification_contradictions_comparison.csv')
        if len(contradictions_data) > 0:
            all_contradictions = pd.concat([df.assign(run=run) for run, df in contradictions_data.items()])
            all_contradictions.to_csv(comparison_file, index=False)
            print(f"\nSaved detailed comparison to: {comparison_file}")

    return contradictions_data

def check_3_gap_id_consistency():
    """Check 3: Verify Gap ID Consistency"""
    print("\n" + "="*80)
    print("CHECK 3: VERIFY GAP ID CONSISTENCY")
    print("="*80)

    base_dir = "/Users/pranay/Projects/adhoc_projects/drrishi/final_submission"
    runs = get_run_folders()

    ai_gaps_data = {}
    coverage_gaps_data = {}

    for run in runs:
        # Load ai_gaps.csv
        ai_gaps_path = os.path.join(base_dir, run, 'ai_gaps.csv')
        if os.path.exists(ai_gaps_path):
            df = pd.read_csv(ai_gaps_path)
            if 'gap_id' in df.columns:
                ai_gaps_data[run] = sorted(df['gap_id'].tolist())

        # Load coverage_gaps_analysis.csv
        coverage_gaps_path = os.path.join(base_dir, run, 'coverage_gaps_analysis.csv')
        if os.path.exists(coverage_gaps_path):
            df = pd.read_csv(coverage_gaps_path)
            if 'gap_id' in df.columns:
                coverage_gaps_data[run] = sorted(df['gap_id'].tolist())

    print(f"\nFound {len(ai_gaps_data)} runs with ai_gaps.csv")
    print(f"Found {len(coverage_gaps_data)} runs with coverage_gaps_analysis.csv")

    # Check ai_gaps consistency
    if ai_gaps_data:
        print("\n--- AI GAPS CONSISTENCY ---")
        unique_gap_sets = {}
        for run, gaps in ai_gaps_data.items():
            gap_tuple = tuple(gaps)
            if gap_tuple not in unique_gap_sets:
                unique_gap_sets[gap_tuple] = []
            unique_gap_sets[gap_tuple].append(run)

        print(f"\nNumber of unique gap ID sets: {len(unique_gap_sets)}")
        for i, (gaps, runs) in enumerate(unique_gap_sets.items(), 1):
            print(f"\nSet {i}: {gaps}")
            print(f"  Appears in {len(runs)} runs")
            if len(runs) <= 5:
                for run in runs:
                    print(f"    - {run}")

    # Check coverage gaps consistency
    if coverage_gaps_data:
        print("\n--- COVERAGE GAPS CONSISTENCY ---")
        unique_gap_sets = {}
        for run, gaps in coverage_gaps_data.items():
            gap_tuple = tuple(gaps)
            if gap_tuple not in unique_gap_sets:
                unique_gap_sets[gap_tuple] = []
            unique_gap_sets[gap_tuple].append(run)

        print(f"\nNumber of unique gap ID sets: {len(unique_gap_sets)}")
        for i, (gaps, runs) in enumerate(unique_gap_sets.items(), 1):
            print(f"\nSet {i}: {list(gaps)}")
            print(f"  Appears in {len(runs)} runs")
            if len(runs) <= 5:
                for run in runs:
                    print(f"    - {run}")

    # Save gap comparison
    gap_comparison = []
    for run in runs:
        ai_gaps = ai_gaps_data.get(run, [])
        coverage_gaps = coverage_gaps_data.get(run, [])
        gap_comparison.append({
            'run': run,
            'ai_gaps_ids': ','.join(map(str, ai_gaps)),
            'ai_gaps_count': len(ai_gaps),
            'coverage_gaps_ids': ','.join(map(str, coverage_gaps)),
            'coverage_gaps_count': len(coverage_gaps)
        })

    df_gap_comparison = pd.DataFrame(gap_comparison)
    comparison_file = os.path.join(base_dir, 'verification_gap_ids_comparison.csv')
    df_gap_comparison.to_csv(comparison_file, index=False)
    print(f"\nSaved gap ID comparison to: {comparison_file}")

    return ai_gaps_data, coverage_gaps_data

def check_4_field_consistency():
    """Check 4: Check Field Consistency"""
    print("\n" + "="*80)
    print("CHECK 4: FIELD CONSISTENCY")
    print("="*80)

    base_dir = "/Users/pranay/Projects/adhoc_projects/drrishi/final_submission"
    runs = get_run_folders()

    field_issues = []

    for run in runs:
        run_path = os.path.join(base_dir, run)

        # Check ai_contradictions.csv
        contradictions_path = os.path.join(run_path, 'ai_contradictions.csv')
        if os.path.exists(contradictions_path):
            df = pd.read_csv(contradictions_path)
            required_fields = ['contradiction_id', 'clinical_severity', 'description']
            for field in required_fields:
                if field not in df.columns:
                    field_issues.append({
                        'run': run,
                        'file': 'ai_contradictions.csv',
                        'issue': f'Missing field: {field}'
                    })
                elif df[field].isna().any():
                    field_issues.append({
                        'run': run,
                        'file': 'ai_contradictions.csv',
                        'issue': f'Null values in field: {field}',
                        'count': df[field].isna().sum()
                    })

        # Check ai_gaps.csv
        gaps_path = os.path.join(run_path, 'ai_gaps.csv')
        if os.path.exists(gaps_path):
            df = pd.read_csv(gaps_path)
            required_fields = ['gap_id', 'coverage_priority', 'description']
            for field in required_fields:
                if field not in df.columns:
                    field_issues.append({
                        'run': run,
                        'file': 'ai_gaps.csv',
                        'issue': f'Missing field: {field}'
                    })
                elif df[field].isna().any():
                    field_issues.append({
                        'run': run,
                        'file': 'ai_gaps.csv',
                        'issue': f'Null values in field: {field}',
                        'count': df[field].isna().sum()
                    })

    if field_issues:
        print(f"\n✗ Found {len(field_issues)} field issues:")
        df_issues = pd.DataFrame(field_issues)
        print(df_issues.to_string(index=False))

        issues_file = os.path.join(base_dir, 'verification_field_issues.csv')
        df_issues.to_csv(issues_file, index=False)
        print(f"\nSaved to: {issues_file}")
    else:
        print("\n✓ No field consistency issues found!")

    return field_issues

def check_5_file_integrity():
    """Check 5: File Integrity (Hash Comparison)"""
    print("\n" + "="*80)
    print("CHECK 5: FILE INTEGRITY (HASH COMPARISON)")
    print("="*80)

    base_dir = "/Users/pranay/Projects/adhoc_projects/drrishi/final_submission"
    runs = get_run_folders()

    files_to_check = [
        'ai_contradictions.csv',
        'ai_gaps.csv',
        'coverage_gaps_analysis.csv'
    ]

    hash_results = []
    for filename in files_to_check:
        print(f"\n--- {filename} ---")
        file_hashes = {}

        for run in runs:
            filepath = os.path.join(base_dir, run, filename)
            if os.path.exists(filepath):
                file_hash = get_file_hash(filepath)
                if file_hash:
                    if file_hash not in file_hashes:
                        file_hashes[file_hash] = []
                    file_hashes[file_hash].append(run)

        print(f"Found {len(file_hashes)} unique file versions")
        for i, (file_hash, runs_with_hash) in enumerate(file_hashes.items(), 1):
            print(f"\nVersion {i} (hash: {file_hash[:8]}...): {len(runs_with_hash)} runs")
            hash_results.append({
                'filename': filename,
                'hash': file_hash,
                'version': i,
                'run_count': len(runs_with_hash),
                'runs': ','.join(runs_with_hash[:3]) + ('...' if len(runs_with_hash) > 3 else '')
            })

    df_hashes = pd.DataFrame(hash_results)
    hash_file = os.path.join(base_dir, 'verification_file_hashes.csv')
    df_hashes.to_csv(hash_file, index=False)
    print(f"\nSaved hash comparison to: {hash_file}")

    return hash_results

def check_6_data_quality():
    """Check 6: Data Quality Checks"""
    print("\n" + "="*80)
    print("CHECK 6: DATA QUALITY CHECKS")
    print("="*80)

    base_dir = "/Users/pranay/Projects/adhoc_projects/drrishi/final_submission"
    runs = get_run_folders()[:5]  # Check first 5 runs for efficiency

    quality_issues = []

    for run in runs:
        run_path = os.path.join(base_dir, run)

        # Check ai_contradictions.csv
        contradictions_path = os.path.join(run_path, 'ai_contradictions.csv')
        if os.path.exists(contradictions_path):
            df = pd.read_csv(contradictions_path)

            # Check for duplicates
            if 'contradiction_id' in df.columns:
                duplicates = df['contradiction_id'].duplicated().sum()
                if duplicates > 0:
                    quality_issues.append({
                        'run': run,
                        'file': 'ai_contradictions.csv',
                        'issue': f'Duplicate contradiction_ids: {duplicates}'
                    })

            # Check for null values
            null_counts = df.isna().sum()
            for col, count in null_counts.items():
                if count > 0:
                    quality_issues.append({
                        'run': run,
                        'file': 'ai_contradictions.csv',
                        'issue': f'Null values in {col}: {count}'
                    })

        # Check ai_gaps.csv
        gaps_path = os.path.join(run_path, 'ai_gaps.csv')
        if os.path.exists(gaps_path):
            df = pd.read_csv(gaps_path)

            # Check for duplicates
            if 'gap_id' in df.columns:
                duplicates = df['gap_id'].duplicated().sum()
                if duplicates > 0:
                    quality_issues.append({
                        'run': run,
                        'file': 'ai_gaps.csv',
                        'issue': f'Duplicate gap_ids: {duplicates}'
                    })

            # Check for null values
            null_counts = df.isna().sum()
            for col, count in null_counts.items():
                if count > 0:
                    quality_issues.append({
                        'run': run,
                        'file': 'ai_gaps.csv',
                        'issue': f'Null values in {col}: {count}'
                    })

    if quality_issues:
        print(f"\n✗ Found {len(quality_issues)} data quality issues:")
        df_quality = pd.DataFrame(quality_issues)
        print(df_quality.to_string(index=False))

        quality_file = os.path.join(base_dir, 'verification_data_quality.csv')
        df_quality.to_csv(quality_file, index=False)
        print(f"\nSaved to: {quality_file}")
    else:
        print("\n✓ No data quality issues found!")

    return quality_issues

def check_7_summary_report():
    """Check 7: Create Summary Report"""
    print("\n" + "="*80)
    print("CHECK 7: SUMMARY REPORT")
    print("="*80)

    base_dir = "/Users/pranay/Projects/adhoc_projects/drrishi/final_submission"
    runs = get_run_folders()

    # Calculate consistency scores
    # For contradictions
    contradictions_hashes = set()
    for run in runs:
        filepath = os.path.join(base_dir, run, 'ai_contradictions.csv')
        if os.path.exists(filepath):
            file_hash = get_file_hash(filepath)
            if file_hash:
                contradictions_hashes.add(file_hash)

    # For gaps
    gaps_hashes = set()
    for run in runs:
        filepath = os.path.join(base_dir, run, 'ai_gaps.csv')
        if os.path.exists(filepath):
            file_hash = get_file_hash(filepath)
            if file_hash:
                gaps_hashes.add(file_hash)

    summary = {
        'total_runs_analyzed': len(runs),
        'unique_contradiction_versions': len(contradictions_hashes),
        'unique_gap_versions': len(gaps_hashes),
        'contradiction_consistency_score': f"{(1/len(contradictions_hashes) if contradictions_hashes else 0)*100:.1f}%",
        'gap_consistency_score': f"{(1/len(gaps_hashes) if gaps_hashes else 0)*100:.1f}%",
        'runs_list': ', '.join(runs[:5]) + ('...' if len(runs) > 5 else '')
    }

    print("\n--- SUMMARY ---")
    for key, value in summary.items():
        print(f"{key}: {value}")

    # Save summary
    summary_file = os.path.join(base_dir, 'verification_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved summary to: {summary_file}")

    return summary

def main():
    """Main execution"""
    print("="*80)
    print("DATA CONSISTENCY VERIFICATION")
    print("Checking reproducibility across analyzer runs")
    print("="*80)

    # Run all checks
    check_1_count_files()
    check_2_contradiction_consistency()
    check_3_gap_id_consistency()
    check_4_field_consistency()
    check_5_file_integrity()
    check_6_data_quality()
    summary = check_7_summary_report()

    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80)
    print("\nGenerated verification files:")
    print("  - verification_row_counts.csv")
    print("  - verification_contradictions_comparison.csv")
    print("  - verification_gap_ids_comparison.csv")
    print("  - verification_field_issues.csv (if issues found)")
    print("  - verification_file_hashes.csv")
    print("  - verification_data_quality.csv (if issues found)")
    print("  - verification_summary.json")

if __name__ == "__main__":
    main()
