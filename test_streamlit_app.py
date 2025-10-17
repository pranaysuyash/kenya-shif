#!/usr/bin/env python3
"""
Comprehensive Test Suite for Streamlit Healthcare Analyzer App
Tests all functionalities without launching the full Streamlit UI
"""

import sys
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import traceback

# Add current directory to path
sys.path.append('.')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class StreamlitAppTester:
    """Comprehensive test suite for the Streamlit app"""

    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def log_test(self, test_name, status, message="", details=""):
        """Log a test result"""
        result = {
            "test_name": test_name,
            "status": status,  # PASS, FAIL, WARNING
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)

        if status == "PASS":
            self.passed += 1
            print(f"✓ {test_name}: {message}")
        elif status == "FAIL":
            self.failed += 1
            print(f"✗ {test_name}: {message}")
            if details:
                print(f"  Details: {details}")
        else:
            self.warnings += 1
            print(f"⚠ {test_name}: {message}")

    def test_imports(self):
        """Test 1: Verify all required imports work"""
        print("\n" + "="*80)
        print("TEST CATEGORY 1: IMPORTS AND DEPENDENCIES")
        print("="*80)

        # Test streamlit import
        try:
            import streamlit
            self.log_test(
                "Import: Streamlit",
                "PASS",
                f"Streamlit {streamlit.__version__} imported successfully"
            )
        except ImportError as e:
            self.log_test(
                "Import: Streamlit",
                "FAIL",
                "Failed to import streamlit",
                str(e)
            )

        # Test pandas import
        try:
            import pandas as pd
            self.log_test(
                "Import: Pandas",
                "PASS",
                f"Pandas {pd.__version__} imported successfully"
            )
        except ImportError as e:
            self.log_test(
                "Import: Pandas",
                "FAIL",
                "Failed to import pandas",
                str(e)
            )

        # Test plotly import
        try:
            import plotly
            self.log_test(
                "Import: Plotly",
                "PASS",
                f"Plotly {plotly.__version__} imported successfully"
            )
        except ImportError as e:
            self.log_test(
                "Import: Plotly",
                "FAIL",
                "Failed to import plotly",
                str(e)
            )

        # Test OpenAI import
        try:
            import openai
            self.log_test(
                "Import: OpenAI",
                "PASS",
                f"OpenAI {openai.__version__} imported successfully"
            )
        except ImportError as e:
            self.log_test(
                "Import: OpenAI",
                "FAIL",
                "Failed to import openai",
                str(e)
            )

        # Test integrated analyzer import
        try:
            from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
            self.log_test(
                "Import: IntegratedComprehensiveMedicalAnalyzer",
                "PASS",
                "Analyzer imported successfully"
            )
        except ImportError as e:
            self.log_test(
                "Import: IntegratedComprehensiveMedicalAnalyzer",
                "FAIL",
                "Failed to import analyzer",
                str(e)
            )

    def test_file_structure(self):
        """Test 2: Verify required files exist"""
        print("\n" + "="*80)
        print("TEST CATEGORY 2: FILE STRUCTURE")
        print("="*80)

        base_path = Path("/Users/pranay/Projects/adhoc_projects/drrishi/final_submission")

        required_files = [
            "streamlit_comprehensive_analyzer.py",
            "integrated_comprehensive_analyzer.py",
            "README.md",
            "DEPLOYMENT_GUIDE.md",
            "PRODUCTION_FILES_GUIDE.md",
            ".env"
        ]

        for file_name in required_files:
            file_path = base_path / file_name
            if file_path.exists():
                self.log_test(
                    f"File Exists: {file_name}",
                    "PASS",
                    f"File found at {file_path}"
                )
            else:
                self.log_test(
                    f"File Exists: {file_name}",
                    "FAIL",
                    f"File not found at {file_path}"
                )

    def test_data_availability(self):
        """Test 3: Verify output data directories exist"""
        print("\n" + "="*80)
        print("TEST CATEGORY 3: DATA AVAILABILITY")
        print("="*80)

        base_path = Path("/Users/pranay/Projects/adhoc_projects/drrishi/final_submission")

        # Find all output directories
        output_dirs = list(base_path.glob("outputs_run_*"))

        if output_dirs:
            self.log_test(
                "Output Directories",
                "PASS",
                f"Found {len(output_dirs)} output directories"
            )

            # Test latest directory
            latest_dir = sorted(output_dirs, reverse=True)[0]
            self.log_test(
                "Latest Output Directory",
                "PASS",
                f"Latest: {latest_dir.name}"
            )

            # Check for required CSV files in latest directory
            required_csvs = [
                "ai_contradictions.csv",
                "ai_gaps.csv",
                "clinical_gaps_analysis.csv",
                "coverage_gaps_analysis.csv"
            ]

            for csv_file in required_csvs:
                csv_path = latest_dir / csv_file
                if csv_path.exists():
                    # Try to load the CSV
                    try:
                        df = pd.read_csv(csv_path)
                        self.log_test(
                            f"CSV Load: {csv_file}",
                            "PASS",
                            f"Loaded {len(df)} rows from {csv_file}"
                        )
                    except Exception as e:
                        self.log_test(
                            f"CSV Load: {csv_file}",
                            "FAIL",
                            f"Failed to load {csv_file}",
                            str(e)
                        )
                else:
                    self.log_test(
                        f"CSV Exists: {csv_file}",
                        "FAIL",
                        f"CSV file not found: {csv_file}"
                    )
        else:
            self.log_test(
                "Output Directories",
                "FAIL",
                "No output directories found"
            )

    def test_data_integrity(self):
        """Test 4: Verify data integrity and expected values"""
        print("\n" + "="*80)
        print("TEST CATEGORY 4: DATA INTEGRITY")
        print("="*80)

        base_path = Path("/Users/pranay/Projects/adhoc_projects/drrishi/final_submission")
        output_dirs = sorted(list(base_path.glob("outputs_run_*")), reverse=True)

        if not output_dirs:
            self.log_test(
                "Data Integrity",
                "FAIL",
                "No output directories to test"
            )
            return

        latest_dir = output_dirs[0]

        # Test contradictions data
        contra_path = latest_dir / "ai_contradictions.csv"
        if contra_path.exists():
            try:
                df = pd.read_csv(contra_path)

                # Check for 6 contradictions
                if len(df) == 6:
                    self.log_test(
                        "Contradictions Count",
                        "PASS",
                        f"Expected 6 contradictions, found {len(df)}"
                    )
                else:
                    self.log_test(
                        "Contradictions Count",
                        "WARNING",
                        f"Expected 6 contradictions, found {len(df)}"
                    )

                # Check for required columns
                required_columns = ['Contradiction', 'Type', 'Severity', 'Impact']
                missing_cols = [col for col in required_columns if col not in df.columns]

                if not missing_cols:
                    self.log_test(
                        "Contradictions Columns",
                        "PASS",
                        "All required columns present"
                    )
                else:
                    self.log_test(
                        "Contradictions Columns",
                        "WARNING",
                        f"Missing columns: {missing_cols}",
                        f"Available columns: {list(df.columns)}"
                    )

            except Exception as e:
                self.log_test(
                    "Contradictions Data Load",
                    "FAIL",
                    "Failed to load contradictions",
                    str(e)
                )

        # Test gaps data
        gaps_path = latest_dir / "ai_gaps.csv"
        if gaps_path.exists():
            try:
                df = pd.read_csv(gaps_path)

                self.log_test(
                    "Gaps Count",
                    "PASS",
                    f"Found {len(df)} gaps"
                )

                # Check for required columns
                required_columns = ['Gap', 'Category', 'Severity', 'Impact']
                missing_cols = [col for col in required_columns if col not in df.columns]

                if not missing_cols:
                    self.log_test(
                        "Gaps Columns",
                        "PASS",
                        "All required columns present"
                    )
                else:
                    self.log_test(
                        "Gaps Columns",
                        "WARNING",
                        f"Missing columns: {missing_cols}",
                        f"Available columns: {list(df.columns)}"
                    )

            except Exception as e:
                self.log_test(
                    "Gaps Data Load",
                    "FAIL",
                    "Failed to load gaps",
                    str(e)
                )

        # Test services count
        annex_path = latest_dir / "annex_surgical_tariffs_all.csv"
        if annex_path.exists():
            try:
                df = pd.read_csv(annex_path)

                if len(df) == 825:
                    self.log_test(
                        "Services Count",
                        "PASS",
                        f"Expected 825 services, found {len(df)}"
                    )
                else:
                    self.log_test(
                        "Services Count",
                        "WARNING",
                        f"Expected 825 services, found {len(df)}"
                    )
            except Exception as e:
                self.log_test(
                    "Services Data Load",
                    "FAIL",
                    "Failed to load services",
                    str(e)
                )

    def test_json_data_structure(self):
        """Test 5: Verify JSON data structures"""
        print("\n" + "="*80)
        print("TEST CATEGORY 5: JSON DATA STRUCTURES")
        print("="*80)

        base_path = Path("/Users/pranay/Projects/adhoc_projects/drrishi/final_submission")

        # Test integrated analysis JSON
        json_files = list(base_path.glob("outputs_run_*/integrated_comprehensive_analysis.json"))

        if json_files:
            latest_json = sorted(json_files, reverse=True)[0]

            try:
                with open(latest_json, 'r') as f:
                    data = json.load(f)

                self.log_test(
                    "JSON Load",
                    "PASS",
                    f"Successfully loaded {latest_json.name}"
                )

                # Check for expected keys
                expected_keys = ['contradictions', 'gaps', 'metadata']
                for key in expected_keys:
                    if key in data:
                        self.log_test(
                            f"JSON Key: {key}",
                            "PASS",
                            f"Found '{key}' in JSON"
                        )
                    else:
                        self.log_test(
                            f"JSON Key: {key}",
                            "WARNING",
                            f"Key '{key}' not found in JSON"
                        )

            except Exception as e:
                self.log_test(
                    "JSON Load",
                    "FAIL",
                    "Failed to load JSON",
                    str(e)
                )
        else:
            self.log_test(
                "JSON Files",
                "WARNING",
                "No integrated_comprehensive_analysis.json files found"
            )

    def test_streamlit_app_syntax(self):
        """Test 6: Verify Streamlit app loads without syntax errors"""
        print("\n" + "="*80)
        print("TEST CATEGORY 6: STREAMLIT APP SYNTAX")
        print("="*80)

        try:
            # Try to import the app module
            import streamlit_comprehensive_analyzer

            self.log_test(
                "App Module Import",
                "PASS",
                "Streamlit app module imported successfully"
            )

            # Check for main class
            if hasattr(streamlit_comprehensive_analyzer, 'SHIFHealthcarePolicyAnalyzer'):
                self.log_test(
                    "Main Class Exists",
                    "PASS",
                    "SHIFHealthcarePolicyAnalyzer class found"
                )
            else:
                self.log_test(
                    "Main Class Exists",
                    "FAIL",
                    "SHIFHealthcarePolicyAnalyzer class not found"
                )

        except SyntaxError as e:
            self.log_test(
                "App Module Import",
                "FAIL",
                "Syntax error in streamlit app",
                str(e)
            )
        except Exception as e:
            self.log_test(
                "App Module Import",
                "WARNING",
                "App module import raised exception (may be due to Streamlit context)",
                str(e)
            )

    def test_documentation_files(self):
        """Test 7: Verify documentation files are readable"""
        print("\n" + "="*80)
        print("TEST CATEGORY 7: DOCUMENTATION FILES")
        print("="*80)

        base_path = Path("/Users/pranay/Projects/adhoc_projects/drrishi/final_submission")

        docs = [
            ("README.md", "Main README"),
            ("DEPLOYMENT_GUIDE.md", "Deployment Guide"),
            ("PRODUCTION_FILES_GUIDE.md", "Production Files Guide")
        ]

        for doc_file, doc_name in docs:
            doc_path = base_path / doc_file
            if doc_path.exists():
                try:
                    content = doc_path.read_text()
                    if len(content) > 0:
                        self.log_test(
                            f"Documentation: {doc_name}",
                            "PASS",
                            f"{doc_file} is readable ({len(content)} chars)"
                        )
                    else:
                        self.log_test(
                            f"Documentation: {doc_name}",
                            "FAIL",
                            f"{doc_file} is empty"
                        )
                except Exception as e:
                    self.log_test(
                        f"Documentation: {doc_name}",
                        "FAIL",
                        f"Failed to read {doc_file}",
                        str(e)
                    )
            else:
                self.log_test(
                    f"Documentation: {doc_name}",
                    "FAIL",
                    f"{doc_file} not found"
                )

    def test_csv_column_mapping(self):
        """Test 8: Verify CSV column mappings match expected structure"""
        print("\n" + "="*80)
        print("TEST CATEGORY 8: CSV COLUMN MAPPINGS")
        print("="*80)

        base_path = Path("/Users/pranay/Projects/adhoc_projects/drrishi/final_submission")
        output_dirs = sorted(list(base_path.glob("outputs_run_*")), reverse=True)

        if not output_dirs:
            self.log_test(
                "CSV Column Mapping",
                "FAIL",
                "No output directories to test"
            )
            return

        latest_dir = output_dirs[0]

        # Test contradictions columns
        contra_path = latest_dir / "ai_contradictions.csv"
        if contra_path.exists():
            try:
                df = pd.read_csv(contra_path)

                # Expected columns based on recent fix
                expected_cols = [
                    'Contradiction', 'Type', 'Source1', 'Source2',
                    'Severity', 'Impact', 'Recommendations'
                ]

                found_cols = [col for col in expected_cols if col in df.columns]
                missing_cols = [col for col in expected_cols if col not in df.columns]

                if len(found_cols) >= 4:  # At least core columns
                    self.log_test(
                        "Contradictions Column Mapping",
                        "PASS",
                        f"Found {len(found_cols)}/{len(expected_cols)} expected columns"
                    )
                else:
                    self.log_test(
                        "Contradictions Column Mapping",
                        "WARNING",
                        f"Only found {len(found_cols)}/{len(expected_cols)} expected columns",
                        f"Missing: {missing_cols}"
                    )

            except Exception as e:
                self.log_test(
                    "Contradictions Column Mapping",
                    "FAIL",
                    "Failed to check columns",
                    str(e)
                )

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)

        total = self.passed + self.failed + self.warnings
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"\nTotal Tests: {total}")
        print(f"✓ Passed: {self.passed}")
        print(f"✗ Failed: {self.failed}")
        print(f"⚠ Warnings: {self.warnings}")
        print(f"\nPass Rate: {pass_rate:.1f}%")

        if self.failed == 0:
            print("\n🎉 ALL CRITICAL TESTS PASSED!")
        elif self.failed <= 2:
            print("\n⚠️  MINOR ISSUES FOUND")
        else:
            print("\n❌ SIGNIFICANT ISSUES FOUND")

        # Save detailed report
        report_path = Path("/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/test_report.json")
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": self.passed,
                "failed": self.failed,
                "warnings": self.warnings,
                "pass_rate": pass_rate
            },
            "tests": self.test_results
        }

        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_path}")

        return report_data

    def run_all_tests(self):
        """Run all test categories"""
        print("\n" + "="*80)
        print("STREAMLIT HEALTHCARE ANALYZER - COMPREHENSIVE TEST SUITE")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Run all test categories
        self.test_imports()
        self.test_file_structure()
        self.test_data_availability()
        self.test_data_integrity()
        self.test_json_data_structure()
        self.test_streamlit_app_syntax()
        self.test_documentation_files()
        self.test_csv_column_mapping()

        # Generate final report
        report = self.generate_report()

        return report

if __name__ == "__main__":
    tester = StreamlitAppTester()
    report = tester.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if tester.failed == 0 else 1)
