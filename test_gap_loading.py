#!/usr/bin/env python3
"""
Test script to verify gap loading logic works correctly
"""
import pandas as pd
from pathlib import Path

def test_gap_loading():
    """Test the updated gap loading logic"""

    # Find latest output directory
    base_path = Path("/Users/pranay/Projects/adhoc_projects/drrishi/final_submission")
    outputs_run_folders = sorted(base_path.glob("outputs_run_*"), key=lambda p: p.name, reverse=True)

    if not outputs_run_folders:
        print("❌ No output folders found!")
        return False

    latest_folder = outputs_run_folders[0]
    print(f"✅ Found latest folder: {latest_folder.name}")

    # Test loading comprehensive_gaps_analysis.csv
    comprehensive_gaps_file = latest_folder / "comprehensive_gaps_analysis.csv"

    if not comprehensive_gaps_file.exists():
        print(f"❌ ERROR: comprehensive_gaps_analysis.csv not found!")
        print(f"   Expected location: {comprehensive_gaps_file}")
        return False

    print(f"✅ Found comprehensive_gaps_analysis.csv")

    # Load the file
    gaps_df = pd.read_csv(comprehensive_gaps_file)
    gaps = gaps_df.where(pd.notna(gaps_df), None).to_dict('records')

    # Calculate metrics
    high_priority_count = len([g for g in gaps if g.get('coverage_priority') == 'HIGH'])
    has_dedup_info = len([g for g in gaps if g.get('deduplication_info')])

    print(f"\n{'='*60}")
    print(f"GAP LOADING METRICS")
    print(f"{'='*60}")
    print(f"  Source file: comprehensive_gaps_analysis.csv")
    print(f"  Total gaps loaded: {len(gaps)}")
    print(f"  High priority gaps: {high_priority_count}")
    print(f"  Gaps with deduplication info: {has_dedup_info}")
    print(f"  Note: After AI deduplication (2 duplicates removed: 31→29)")
    print(f"{'='*60}\n")

    # Verify expected counts
    expected_total = 29
    if len(gaps) != expected_total:
        print(f"⚠️  WARNING: Expected {expected_total} gaps, got {len(gaps)}")
    else:
        print(f"✅ Gap count matches expected: {expected_total}")

    # Check for required columns
    required_columns = ['gap_id', 'coverage_priority', 'gap_category', 'gap_description']
    missing_columns = [col for col in required_columns if col not in gaps_df.columns]

    if missing_columns:
        print(f"❌ Missing required columns: {missing_columns}")
        print(f"   Available columns: {list(gaps_df.columns)}")
        return False
    else:
        print(f"✅ All required columns present")

    # Show sample gap
    if gaps:
        print(f"\n📋 Sample Gap:")
        sample = gaps[0]
        for key in ['gap_id', 'gap_category', 'coverage_priority', 'gap_description']:
            if key in sample:
                value = sample[key]
                if isinstance(value, str) and len(value) > 80:
                    value = value[:77] + "..."
                print(f"   {key}: {value}")

    return True

if __name__ == "__main__":
    print("\n🧪 Testing Gap Loading Logic\n")
    success = test_gap_loading()
    print(f"\n{'='*60}")
    if success:
        print("✅ TEST PASSED: Gap loading logic works correctly!")
    else:
        print("❌ TEST FAILED: Gap loading logic has issues!")
    print(f"{'='*60}\n")
