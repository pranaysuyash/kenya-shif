#!/bin/bash
cd "/Users/pranay/Projects/adhoc_projects/drrishi/final_submission"
echo "🚀 Running Integrated Comprehensive Medical Analyzer"
echo "Working directory: $(pwd)"
echo "Python path: $(which python3)"
echo "Virtual env python: .venv/bin/python3"
echo "=================================="

# Run using virtual environment
./.venv/bin/python3 test_and_run.py
