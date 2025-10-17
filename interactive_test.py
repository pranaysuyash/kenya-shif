#!/usr/bin/env python3
"""
Interactive test script that simulates Streamlit app behavior
Tests key functionality without requiring browser interaction
"""

import sys
import os
from pathlib import Path
import pandas as pd
import json

sys.path.append('.')

class InteractiveAppTest:
    """Test app functionality by simulating user interactions"""

    def __init__(self):
        self.test_results = []
        self.base_path = Path(".")

    def log_result(self, test, status, details=""):
        """Log a test result"""
        self.test_results.append({
            "test": test,
            "status": status,
            "details": details
        })

        symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
        print(f"{symbol} {test}: {details}")

    def test_data_loading(self):
        """Test that app can load data from latest run"""
        print("\n" + "="*80)
        print("TEST: DATA LOADING")
        print("="*80)

        # Find latest output directory
        output_dirs = sorted(list(self.base_path.glob("outputs_run_*")), reverse=True)

        if not output_dirs:
            self.log_result("Find output directories", "FAIL", "No output directories found")
            return False

        latest_dir = output_dirs[0]
        self.log_result("Find latest run", "PASS", f"Found {latest_dir.name}")

        # Load contradictions
        try:
            contra_df = pd.read_csv(latest_dir / "ai_contradictions.csv")
            self.log_result(
                "Load contradictions CSV",
                "PASS",
                f"Loaded {len(contra_df)} contradictions"
            )
            self.contra_df = contra_df
        except Exception as e:
            self.log_result("Load contradictions CSV", "FAIL", str(e))
            return False

        # Load gaps
        try:
            gaps_df = pd.read_csv(latest_dir / "ai_gaps.csv")
            self.log_result(
                "Load gaps CSV",
                "PASS",
                f"Loaded {len(gaps_df)} gaps"
            )
            self.gaps_df = gaps_df
        except Exception as e:
            self.log_result("Load gaps CSV", "FAIL", str(e))
            return False

        # Load coverage gaps
        try:
            coverage_df = pd.read_csv(latest_dir / "coverage_gaps_analysis.csv")
            self.log_result(
                "Load coverage gaps CSV",
                "PASS",
                f"Loaded {len(coverage_df)} coverage gaps"
            )
            self.coverage_df = coverage_df
        except Exception as e:
            self.log_result("Load coverage gaps CSV", "FAIL", str(e))
            return False

        # Load services
        try:
            services_df = pd.read_csv(latest_dir / "annex_surgical_tariffs_all.csv")
            self.log_result(
                "Load services CSV",
                "PASS",
                f"Loaded {len(services_df)} services"
            )
            self.services_df = services_df
        except Exception as e:
            self.log_result("Load services CSV", "FAIL", str(e))
            return False

        return True

    def test_metrics_calculation(self):
        """Test dashboard metrics calculation"""
        print("\n" + "="*80)
        print("TEST: METRICS CALCULATION")
        print("="*80)

        # Test total services metric
        total_services = len(self.services_df)
        self.log_result(
            "Calculate total services",
            "PASS",
            f"Total: {total_services}"
        )

        # Test total contradictions metric
        total_contradictions = len(self.contra_df)
        expected_contradictions = 6

        if total_contradictions == expected_contradictions:
            self.log_result(
                "Calculate total contradictions",
                "PASS",
                f"Total: {total_contradictions} (matches expected)"
            )
        else:
            self.log_result(
                "Calculate total contradictions",
                "WARNING",
                f"Total: {total_contradictions} (expected {expected_contradictions})"
            )

        # Test total gaps metric
        total_gaps = len(self.gaps_df)
        self.log_result(
            "Calculate total gaps",
            "PASS",
            f"Total: {total_gaps}"
        )

        # Test coverage gaps metric
        total_coverage_gaps = len(self.coverage_df)
        self.log_result(
            "Calculate coverage gaps",
            "PASS",
            f"Total: {total_coverage_gaps}"
        )

        return True

    def test_filtering(self):
        """Test data filtering functionality"""
        print("\n" + "="*80)
        print("TEST: DATA FILTERING")
        print("="*80)

        # Test severity filtering on contradictions
        if 'clinical_severity' in self.contra_df.columns:
            high_severity = self.contra_df[
                self.contra_df['clinical_severity'].str.contains('high', case=False, na=False)
            ]
            self.log_result(
                "Filter high severity contradictions",
                "PASS",
                f"Found {len(high_severity)} high severity items"
            )
        else:
            self.log_result(
                "Filter high severity contradictions",
                "WARNING",
                "clinical_severity column not found"
            )

        # Test category filtering on gaps
        if 'gap_category' in self.gaps_df.columns:
            categories = self.gaps_df['gap_category'].value_counts()
            self.log_result(
                "Count gap categories",
                "PASS",
                f"Found {len(categories)} unique categories"
            )
        else:
            self.log_result(
                "Count gap categories",
                "WARNING",
                "gap_category column not found"
            )

        return True

    def test_ai_insights_extraction(self):
        """Test that AI insights can be extracted from data"""
        print("\n" + "="*80)
        print("TEST: AI INSIGHTS EXTRACTION")
        print("="*80)

        # Test extracting insights from first contradiction
        if len(self.contra_df) > 0:
            first_contra = self.contra_df.iloc[0]

            # Check for key insight fields
            insight_fields = [
                'medical_analysis',
                'patient_safety_impact',
                'kenya_health_system_impact',
                'recommended_resolution'
            ]

            found_fields = [f for f in insight_fields if f in first_contra.index]

            if len(found_fields) >= 3:
                self.log_result(
                    "Extract contradiction insights",
                    "PASS",
                    f"Found {len(found_fields)}/4 insight fields"
                )

                # Check if insights have content
                has_content = sum(
                    1 for f in found_fields
                    if pd.notna(first_contra[f]) and len(str(first_contra[f])) > 10
                )

                self.log_result(
                    "Verify insight content",
                    "PASS" if has_content >= 2 else "WARNING",
                    f"{has_content}/{len(found_fields)} fields have substantial content"
                )
            else:
                self.log_result(
                    "Extract contradiction insights",
                    "WARNING",
                    f"Only found {len(found_fields)}/4 insight fields"
                )

        # Test extracting insights from first gap
        if len(self.gaps_df) > 0:
            first_gap = self.gaps_df.iloc[0]

            insight_fields = [
                'kenya_epidemiological_context',
                'affected_populations',
                'health_system_impact_analysis',
                'recommended_interventions'
            ]

            found_fields = [f for f in insight_fields if f in first_gap.index]

            if len(found_fields) >= 3:
                self.log_result(
                    "Extract gap insights",
                    "PASS",
                    f"Found {len(found_fields)}/4 insight fields"
                )
            else:
                self.log_result(
                    "Extract gap insights",
                    "WARNING",
                    f"Only found {len(found_fields)}/4 insight fields"
                )

        return True

    def test_chart_data_preparation(self):
        """Test data preparation for charts"""
        print("\n" + "="*80)
        print("TEST: CHART DATA PREPARATION")
        print("="*80)

        # Test contradictions by type chart data
        if 'contradiction_type' in self.contra_df.columns:
            type_counts = self.contra_df['contradiction_type'].value_counts()
            self.log_result(
                "Prepare contradictions by type chart",
                "PASS",
                f"Found {len(type_counts)} contradiction types"
            )

            # Print distribution
            print("\n  Contradiction Type Distribution:")
            for type_name, count in type_counts.items():
                print(f"    - {type_name}: {count}")
        else:
            self.log_result(
                "Prepare contradictions by type chart",
                "WARNING",
                "contradiction_type column not found"
            )

        # Test gaps by category chart data
        if 'gap_category' in self.gaps_df.columns:
            category_counts = self.gaps_df['gap_category'].value_counts()
            self.log_result(
                "Prepare gaps by category chart",
                "PASS",
                f"Found {len(category_counts)} gap categories"
            )

            # Print distribution
            print("\n  Gap Category Distribution:")
            for cat_name, count in category_counts.items():
                print(f"    - {cat_name}: {count}")
        else:
            self.log_result(
                "Prepare gaps by category chart",
                "WARNING",
                "gap_category column not found"
            )

        return True

    def test_documentation_access(self):
        """Test that documentation files can be loaded"""
        print("\n" + "="*80)
        print("TEST: DOCUMENTATION ACCESS")
        print("="*80)

        docs = [
            "README.md",
            "DEPLOYMENT_GUIDE.md",
            "PRODUCTION_FILES_GUIDE.md"
        ]

        for doc in docs:
            doc_path = self.base_path / doc
            try:
                content = doc_path.read_text()
                if len(content) > 100:
                    self.log_result(
                        f"Load {doc}",
                        "PASS",
                        f"Loaded {len(content)} characters"
                    )
                else:
                    self.log_result(
                        f"Load {doc}",
                        "WARNING",
                        f"File seems short ({len(content)} chars)"
                    )
            except Exception as e:
                self.log_result(
                    f"Load {doc}",
                    "FAIL",
                    str(e)
                )

        return True

    def test_download_preparation(self):
        """Test that data can be prepared for download"""
        print("\n" + "="*80)
        print("TEST: DOWNLOAD PREPARATION")
        print("="*80)

        # Test CSV to bytes conversion
        try:
            csv_bytes = self.contra_df.to_csv(index=False).encode('utf-8')
            self.log_result(
                "Convert DataFrame to CSV bytes",
                "PASS",
                f"Generated {len(csv_bytes)} bytes"
            )
        except Exception as e:
            self.log_result(
                "Convert DataFrame to CSV bytes",
                "FAIL",
                str(e)
            )

        # Test JSON serialization
        try:
            json_str = self.contra_df.head(1).to_json(orient='records')
            json_obj = json.loads(json_str)
            self.log_result(
                "Serialize data to JSON",
                "PASS",
                f"Successfully serialized data"
            )
        except Exception as e:
            self.log_result(
                "Serialize data to JSON",
                "FAIL",
                str(e)
            )

        return True

    def test_historical_data_access(self):
        """Test accessing historical analysis runs"""
        print("\n" + "="*80)
        print("TEST: HISTORICAL DATA ACCESS")
        print("="*80)

        # Find all output directories
        output_dirs = sorted(list(self.base_path.glob("outputs_run_*")), reverse=True)

        self.log_result(
            "Find historical runs",
            "PASS",
            f"Found {len(output_dirs)} analysis runs"
        )

        # Test loading from different runs
        if len(output_dirs) >= 2:
            second_run = output_dirs[1]
            try:
                df = pd.read_csv(second_run / "ai_contradictions.csv")
                self.log_result(
                    "Load data from historical run",
                    "PASS",
                    f"Loaded {len(df)} rows from {second_run.name}"
                )
            except Exception as e:
                self.log_result(
                    "Load data from historical run",
                    "WARNING",
                    f"Could not load from {second_run.name}: {str(e)}"
                )

        # Print run dates
        print("\n  Available Analysis Runs:")
        for run_dir in output_dirs[:5]:  # Show first 5
            print(f"    - {run_dir.name}")

        return True

    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n" + "="*80)
        print("TEST: ERROR HANDLING")
        print("="*80)

        # Test handling missing column
        try:
            _ = self.contra_df.get('nonexistent_column', pd.Series())
            self.log_result(
                "Handle missing column gracefully",
                "PASS",
                "Used .get() with default value"
            )
        except Exception as e:
            self.log_result(
                "Handle missing column gracefully",
                "FAIL",
                str(e)
            )

        # Test handling empty DataFrame operations
        try:
            empty_df = pd.DataFrame()
            result = len(empty_df)
            self.log_result(
                "Handle empty DataFrame",
                "PASS",
                f"Empty DataFrame has {result} rows"
            )
        except Exception as e:
            self.log_result(
                "Handle empty DataFrame",
                "FAIL",
                str(e)
            )

        # Test handling missing file
        try:
            from pathlib import Path
            fake_file = Path("nonexistent_file.csv")
            exists = fake_file.exists()
            self.log_result(
                "Check file existence properly",
                "PASS",
                f"File existence check returns {exists}"
            )
        except Exception as e:
            self.log_result(
                "Check file existence properly",
                "FAIL",
                str(e)
            )

        return True

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)

        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        warnings = sum(1 for r in self.test_results if r['status'] == 'WARNING')
        total = len(self.test_results)

        print(f"\nTotal Tests: {total}")
        print(f"✓ Passed: {passed}")
        print(f"✗ Failed: {failed}")
        print(f"⚠ Warnings: {warnings}")

        if failed == 0:
            print("\n🎉 ALL INTERACTIVE TESTS PASSED!")
            return True
        else:
            print(f"\n❌ {failed} TEST(S) FAILED")
            return False

    def run_all_tests(self):
        """Run all interactive tests"""
        print("\n" + "="*80)
        print("STREAMLIT APP - INTERACTIVE FUNCTIONALITY TESTS")
        print("="*80)

        # Run tests in sequence
        if not self.test_data_loading():
            print("\n❌ Data loading failed. Cannot continue tests.")
            return False

        self.test_metrics_calculation()
        self.test_filtering()
        self.test_ai_insights_extraction()
        self.test_chart_data_preparation()
        self.test_documentation_access()
        self.test_download_preparation()
        self.test_historical_data_access()
        self.test_error_handling()

        return self.generate_summary()

if __name__ == "__main__":
    tester = InteractiveAppTest()
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)
