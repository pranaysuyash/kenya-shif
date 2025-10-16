#!/usr/bin/env python3
"""
Complete SHIF Benefits Analyzer - Streamlit Application (Fixed Version)
One-stop solution: Upload PDF → Get complete analysis with graphs, inferences, and downloadable results

Author: Pranay for Dr. Rishi  
Date: August 25, 2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import tempfile
import zipfile
from io import BytesIO
import json

# Add current directory to path for imports
sys.path.append('.')

# Page configuration
st.set_page_config(
    page_title="SHIF Complete Analyzer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_analysis_modules():
    """Load analysis modules with proper error handling"""
    modules = {}
    
    try:
        from enhanced_analyzer import parse_pdf_enhanced
        modules['parse_pdf'] = parse_pdf_enhanced
        st.sidebar.success("✅ Enhanced analyzer loaded")
    except ImportError as e:
        st.sidebar.error(f"Enhanced analyzer failed: {e}")
        return None
    
    try:
        from disease_treatment_gap_analysis import analyze_disease_treatment_gaps
        modules['disease_gaps'] = analyze_disease_treatment_gaps
        st.sidebar.success("✅ Disease gap analysis loaded")
    except ImportError as e:
        st.sidebar.error(f"Disease gap analysis failed: {e}")
    
    try:
        from comprehensive_gap_analysis import comprehensive_gap_analysis
        modules['gap_analysis'] = comprehensive_gap_analysis
        st.sidebar.success("✅ Gap analysis loaded")
    except ImportError as e:
        st.sidebar.error(f"Gap analysis failed: {e}")
    
    try:
        from annex_tariff_extractor import extract_annex_tariffs
        modules['annex_tariffs'] = extract_annex_tariffs
        st.sidebar.success("✅ Annex extractor loaded")
    except ImportError as e:
        st.sidebar.error(f"Annex extractor failed: {e}")
    
    try:
        from kenya_healthcare_context_analysis import analyze_with_kenya_context
        modules['kenya_context'] = analyze_with_kenya_context
        st.sidebar.success("✅ Kenya context loaded")
    except ImportError as e:
        st.sidebar.error(f"Kenya context failed: {e}")
    
    try:
        from enhanced_contradiction_detector import EnhancedContradictionDetector
        detector = EnhancedContradictionDetector()
        modules['contradictions'] = detector.detect_all_contradictions
        st.sidebar.success("✅ Enhanced contradiction detector loaded")
    except ImportError as e:
        st.sidebar.error(f"Enhanced contradiction detector failed: {e}")
    
    return modules

def main():
    st.title("🏥 SHIF Benefits Package Complete Analyzer")
    st.markdown("**One-stop solution for Kenya SHIF policy analysis**")
    st.markdown("Upload your SHIF PDF → Get complete analysis with visualizations and downloadable results")
    
    # Load analysis modules
    modules = load_analysis_modules()
    if modules is None or 'parse_pdf' not in modules:
        st.error("❌ Critical analysis modules failed to load. Cannot proceed.")
        st.info("Please ensure all required Python files are in the current directory.")
        return
    
    # Sidebar for options
    st.sidebar.title("📊 Analysis Options")
    
    # Mode selection
    mode = st.sidebar.radio(
        "Choose Analysis Mode:",
        ["🚀 Quick Analysis (Pre-loaded)", "📄 Upload New PDF", "📈 View Previous Results"]
    )
    
    if mode == "🚀 Quick Analysis (Pre-loaded)":
        run_preloaded_analysis(modules)
    elif mode == "📄 Upload New PDF":
        run_upload_analysis(modules)
    elif mode == "📈 View Previous Results":
        view_previous_results()

def run_preloaded_analysis(modules):
    st.header("🚀 Quick Analysis with Pre-loaded SHIF PDF")
    
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    
    if not os.path.exists(pdf_path):
        st.error(f"Pre-loaded PDF not found: {pdf_path}")
        st.info("Please upload a PDF using the 'Upload New PDF' option")
        return
    
    st.success(f"✅ Found SHIF PDF: {pdf_path}")
    
    # Analysis mode selection
    analysis_mode = st.radio(
        "Choose Analysis Mode:",
        ["📊 Use Pre-computed Results (Recommended)", "🔄 Run Fresh Analysis"]
    )
    
    if analysis_mode == "📊 Use Pre-computed Results (Recommended)":
        st.info("Loading comprehensive analysis results from previous high-performance run (669 rules, 5 gaps, 281 annex tariffs)")
        
        if st.button("📊 Load Pre-computed Results", type="primary"):
            load_and_display_cached_results()
    
    else:  # Fresh Analysis
        # Analysis options
        st.subheader("Select Analysis Tasks:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            task1 = st.checkbox("📋 Task 1: Extract Rules", value=True)
        with col2:
            task2 = st.checkbox("🔍 Task 2: Find Contradictions", value=True)  
        with col3:
            task3 = st.checkbox("📊 Task 3: Analyze Gaps", value=True)
        
        # Additional analysis options
        st.subheader("Enhanced Analysis:")
        col4, col5 = st.columns(2)
        
        with col4:
            extract_annex = st.checkbox("💰 Extract Annex Tariffs", value=True)
        with col5:
            kenya_context = st.checkbox("🇰🇪 Kenya Healthcare Context", value=True)
        
        # OpenAI API key input
        openai_key = st.text_input("OpenAI API Key (optional for enhanced extraction):", 
                                  value=os.getenv('OPENAI_API_KEY', ''), type="password")
        
        if st.button("🚀 Run Fresh Analysis", type="primary"):
            run_complete_analysis(modules, pdf_path, openai_key, task1, task2, task3, extract_annex, kenya_context)

def run_upload_analysis(modules):
    st.header("📄 Upload and Analyze New PDF")
    
    uploaded_file = st.file_uploader(
        "Choose SHIF benefits PDF file:",
        type=['pdf'],
        help="Upload the SHIF benefits package PDF for analysis"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.read())
            pdf_path = tmp_file.name
        
        st.success(f"✅ PDF uploaded successfully: {uploaded_file.name}")
        
        # Same analysis options as preloaded
        st.subheader("Select Analysis Tasks:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            task1 = st.checkbox("📋 Task 1: Extract Rules", value=True, key="upload_task1")
        with col2:
            task2 = st.checkbox("🔍 Task 2: Find Contradictions", value=True, key="upload_task2")
        with col3:
            task3 = st.checkbox("📊 Task 3: Analyze Gaps", value=True, key="upload_task3")
        
        # Additional analysis options
        st.subheader("Enhanced Analysis:")
        col4, col5 = st.columns(2)
        
        with col4:
            extract_annex = st.checkbox("💰 Extract Annex Tariffs", value=True, key="upload_annex")
        with col5:
            kenya_context = st.checkbox("🇰🇪 Kenya Healthcare Context", value=True, key="upload_context")
        
        # OpenAI API key input
        openai_key = st.text_input("OpenAI API Key (optional):", 
                                  value=os.getenv('OPENAI_API_KEY', ''), type="password", key="upload_key")
        
        if st.button("🚀 Analyze Uploaded PDF", type="primary"):
            run_complete_analysis(modules, pdf_path, openai_key, task1, task2, task3, extract_annex, kenya_context)
            
            # Clean up temporary file
            os.unlink(pdf_path)

def run_complete_analysis(modules, pdf_path, openai_key, task1, task2, task3, extract_annex, kenya_context):
    """Run complete analysis pipeline and display results"""
    
    results = {}
    
    # Set OpenAI key if provided
    if openai_key:
        os.environ['OPENAI_API_KEY'] = openai_key
    
    try:
        # Task 1: Rule Extraction
        if task1:
            with st.spinner("📋 Task 1: Extracting healthcare rules from PDF..."):
                try:
                    rules_df = modules['parse_pdf'](pdf_path, openai_key)
                    results['rules'] = rules_df
                    st.success(f"✅ Task 1 Complete: {len(rules_df)} rules extracted")
                except Exception as e:
                    st.error(f"Task 1 failed: {e}")
                    return
        
        # Task 2: Contradiction Detection  
        if task2 and 'rules' in results:
            with st.spinner("🔍 Task 2: Detecting contradictions..."):
                try:
                    # Enhanced contradiction detection
                    contradictions_df = pd.DataFrame()
                    if 'contradictions' in modules:
                        contradictions_df = modules['contradictions'](results['rules'])
                        results['contradictions'] = contradictions_df
                        
                    # Disease-treatment gap analysis (part of contradiction analysis)
                    disease_gaps_df = pd.DataFrame()
                    if 'disease_gaps' in modules:
                        disease_gaps_df = modules['disease_gaps'](results['rules'])
                        results['disease_gaps'] = disease_gaps_df
                        
                    st.success(f"✅ Task 2 Complete: {len(contradictions_df)} service contradictions + {len(disease_gaps_df)} disease gaps found")
                except Exception as e:
                    st.error(f"Task 2 failed: {e}")
                    results['contradictions'] = pd.DataFrame()
                    results['disease_gaps'] = pd.DataFrame()
        
        # Task 3: Gap Analysis
        if task3 and 'rules' in results:
            with st.spinner("📊 Task 3: Analyzing coverage gaps..."):
                try:
                    if 'gap_analysis' in modules:
                        gaps_df = modules['gap_analysis'](results['rules'])
                        results['gaps'] = gaps_df
                        st.success(f"✅ Task 3 Complete: {len(gaps_df)} coverage gaps identified")
                    else:
                        st.warning("Gap analysis module not available")
                        results['gaps'] = pd.DataFrame()
                except Exception as e:
                    st.error(f"Task 3 failed: {e}")
                    results['gaps'] = pd.DataFrame()
        
        # Annex Tariff Extraction
        if extract_annex:
            with st.spinner("💰 Extracting specialty tariffs from annex..."):
                try:
                    if 'annex_tariffs' in modules:
                        annex_df = modules['annex_tariffs'](pdf_path)
                        results['annex_tariffs'] = annex_df
                        st.success(f"✅ Annex Analysis Complete: {len(annex_df)} specialty tariffs extracted")
                    else:
                        st.warning("Annex tariff extraction module not available")
                        results['annex_tariffs'] = pd.DataFrame()
                except Exception as e:
                    st.error(f"Annex extraction failed: {e}")
                    results['annex_tariffs'] = pd.DataFrame()
        
        # Kenya Context Analysis
        if kenya_context and 'rules' in results:
            with st.spinner("🇰🇪 Analyzing Kenya healthcare context..."):
                try:
                    if 'kenya_context' in modules:
                        annex_df = results.get('annex_tariffs', pd.DataFrame())
                        context_analysis = modules['kenya_context'](results['rules'], annex_df if not annex_df.empty else None)
                        results['kenya_context'] = context_analysis
                        st.success("✅ Kenya Context Analysis Complete")
                    else:
                        st.warning("Kenya context analysis module not available")
                except Exception as e:
                    st.error(f"Kenya context analysis failed: {e}")
        
        # Display results
        display_analysis_results(results)
        
        # Provide download options
        provide_download_options(results)
        
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        st.error(f"Error details: {str(e)}")

def display_analysis_results(results):
    """Display comprehensive analysis results with visualizations"""
    
    st.header("📊 Analysis Results")
    
    # Executive Summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        rules_count = len(results.get('rules', []))
        st.metric("Rules Extracted", rules_count, "Task 1")
    
    with col2:
        contradictions_count = len(results.get('contradictions', [])) + len(results.get('disease_gaps', []))
        st.metric("Contradictions Found", contradictions_count, "Task 2")
    
    with col3:
        gaps_count = len(results.get('gaps', []))
        st.metric("Coverage Gaps", gaps_count, "Task 3")
    
    with col4:
        tariffs_count = len(results.get('annex_tariffs', []))
        st.metric("Specialty Tariffs", tariffs_count, "Annex")
    
    # Tabs for detailed results
    tabs = st.tabs(["📋 Rules Analysis", "🔍 Contradictions", "📊 Coverage Gaps", "💰 Tariffs", "🎯 Simple Dashboard"])
    
    # Rules Analysis Tab
    with tabs[0]:
        if 'rules' in results and not results['rules'].empty:
            show_rules_analysis_tab(results['rules'])
        else:
            st.info("Task 1 (Rule Extraction) was not run or returned no results")
    
    # Contradictions Tab
    with tabs[1]:
        if 'contradictions' in results or 'disease_gaps' in results:
            show_contradictions_tab(results.get('contradictions'), results.get('disease_gaps'))
        else:
            st.info("Task 2 (Contradiction Detection) was not run")
    
    # Coverage Gaps Tab
    with tabs[2]:
        if 'gaps' in results and not results['gaps'].empty:
            show_gaps_tab(results['gaps'])
        else:
            st.info("Task 3 (Gap Analysis) was not run or returned no results")
    
    # Tariffs Tab
    with tabs[3]:
        if 'annex_tariffs' in results and not results['annex_tariffs'].empty:
            show_tariffs_tab(results['annex_tariffs'])
        else:
            st.info("Annex tariff extraction was not run or returned no results")
    
    # Simple Dashboard Tab
    with tabs[4]:
        show_simple_dashboard_tab(results)

def show_rules_analysis_tab(rules_df):
    st.subheader("📋 Healthcare Rules Extraction Results")
    
    # Category breakdown chart
    if 'category' in rules_df.columns:
        category_counts = rules_df['category'].value_counts()
        fig = px.bar(
            x=category_counts.values,
            y=category_counts.index,
            orientation='h',
            title="Healthcare Rules by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tariff coverage analysis
    if 'tariff' in rules_df.columns:
        tariff_coverage = (rules_df['tariff'].notna() & (rules_df['tariff'] > 0)).sum()
        total_rules = len(rules_df)
        
        st.subheader("Tariff Coverage Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rules with Tariffs", tariff_coverage)
        with col2:
            st.metric("Coverage %", f"{tariff_coverage/total_rules*100:.1f}%")
    
    # Sample rules table
    st.subheader("Sample Extracted Rules")
    display_cols = ['service', 'category', 'tariff', 'source_page', 'confidence']
    available_cols = [col for col in display_cols if col in rules_df.columns]
    
    st.dataframe(rules_df[available_cols].head(20), use_container_width=True)

def show_contradictions_tab(contradictions_df, disease_gaps_df):
    st.subheader("🔍 Contradictions and Conflicts Detected")
    
    # Disease-treatment gaps (main finding)
    if disease_gaps_df is not None and not disease_gaps_df.empty:
        st.markdown("### 🩺 Disease-Treatment Gaps (Critical Finding)")
        st.error("Diseases listed in benefits but no corresponding treatment coverage found!")
        
        for _, gap in disease_gaps_df.iterrows():
            severity_icon = "🔴" if gap.get('severity') == 'CRITICAL' else "🟡"
            
            with st.expander(f"{severity_icon} {gap['disease']} - {gap['gap_type']}"):
                st.write(f"**Medical Context:** {gap.get('medical_context', 'N/A')}")
                st.write(f"**Disease Mentions:** {gap['disease_mentions']} times in document")
                st.write(f"**Treatment Coverage:** {gap['treatment_rules']} rules found")
                st.write(f"**Gap Description:** {gap['description']}")
    else:
        st.info("No disease-treatment gaps found in analysis")
    
    # Service contradictions
    if contradictions_df is not None and not contradictions_df.empty:
        st.markdown("### Service Contradictions")
        for _, contradiction in contradictions_df.iterrows():
            with st.expander(f"{contradiction['type']}: {contradiction.get('severity', 'MEDIUM')} Priority"):
                st.write(f"**Conflict:** {contradiction['conflict_description']}")
                st.write(f"**Evidence:** {contradiction.get('evidence_1', 'N/A')}")
    else:
        st.info("No service contradictions found")

def show_gaps_tab(gaps_df):
    st.subheader("📊 Coverage Gap Analysis")
    
    # Gap severity distribution
    if 'severity' in gaps_df.columns:
        severity_counts = gaps_df['severity'].value_counts()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Critical Gaps", severity_counts.get('CRITICAL', 0))
        with col2:
            st.metric("High Priority", severity_counts.get('HIGH', 0))
        with col3:
            st.metric("Medium Priority", severity_counts.get('MEDIUM', 0))
    
    # Gap types chart
    if 'gap_type' in gaps_df.columns:
        gap_types = gaps_df['gap_type'].value_counts()
        fig = px.pie(values=gap_types.values, names=gap_types.index, title="Gap Types Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed gaps
    st.subheader("Detailed Gap Analysis")
    for _, gap in gaps_df.head(10).iterrows():
        severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}.get(gap.get('severity'), "⚪")
        
        with st.expander(f"{severity_icon} {gap.get('service', 'Unknown Service')} ({gap.get('category', 'Unknown')})"):
            st.write(f"**Gap Type:** {gap.get('gap_type', 'N/A')}")
            st.write(f"**Description:** {gap.get('description', 'N/A')}")
            if 'recommendation' in gap:
                st.write(f"**Recommendation:** {gap['recommendation']}")

def show_tariffs_tab(tariffs_df):
    st.subheader("💰 Specialty Tariffs from Annex")
    
    # Specialty distribution
    if 'specialty' in tariffs_df.columns:
        specialty_counts = tariffs_df['specialty'].value_counts()
        fig = px.bar(
            x=specialty_counts.values,
            y=specialty_counts.index,
            orientation='h',
            title="Services by Medical Specialty"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Price statistics
    if 'tariff' in tariffs_df.columns:
        st.subheader("Price Range Analysis")
        specialty_stats = tariffs_df.groupby('specialty')['tariff'].agg(['min', 'max', 'mean']).round(0)
        specialty_stats.columns = ['Min (KES)', 'Max (KES)', 'Average (KES)']
        st.dataframe(specialty_stats, use_container_width=True)
    
    # Most expensive procedures
    st.subheader("Most Expensive Procedures")
    top_procedures = tariffs_df.nlargest(10, 'tariff')
    st.dataframe(top_procedures[['service', 'specialty', 'tariff']], use_container_width=True)

def show_simple_dashboard_tab(results):
    st.subheader("🎯 Simple Results Dashboard")
    
    # Create simple table as requested in assignment
    dashboard_data = {
        'METRIC': [
            'Rules Parsed',
            'Contradictions Flagged',
            'Disease-Treatment Gaps',
            'Coverage Gaps Total',
            'Specialty Tariffs',
            'Critical Issues'
        ],
        'COUNT': [
            len(results.get('rules', [])),
            len(results.get('contradictions', [])) + len(results.get('disease_gaps', [])),
            len(results.get('disease_gaps', [])),
            len(results.get('gaps', [])),
            len(results.get('annex_tariffs', [])),
            len([g for g in results.get('gaps', []) if isinstance(g, dict) and g.get('severity') == 'CRITICAL']) if results.get('gaps') is not None else 0
        ],
        'DETAILS': [
            'Healthcare rules extracted from SHIF PDF',
            'Service variations and policy conflicts detected',
            'Diseases listed but no treatment coverage',
            'Missing services across healthcare categories',
            'Specialized procedures from PDF annex',
            'Life-threatening coverage gaps identified'
        ]
    }
    
    dashboard_df = pd.DataFrame(dashboard_data)
    st.dataframe(dashboard_df, use_container_width=True)

def provide_download_options(results):
    """Provide download options for all results"""
    
    st.header("📥 Download Results")
    
    # Create download package
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        
        # Add CSV files
        if 'rules' in results and not results['rules'].empty:
            csv_buffer = BytesIO()
            results['rules'].to_csv(csv_buffer, index=False)
            zip_file.writestr('rules_extracted.csv', csv_buffer.getvalue())
        
        if 'contradictions' in results and not results['contradictions'].empty:
            csv_buffer = BytesIO()
            results['contradictions'].to_csv(csv_buffer, index=False)
            zip_file.writestr('contradictions_found.csv', csv_buffer.getvalue())
        
        if 'disease_gaps' in results and not results['disease_gaps'].empty:
            csv_buffer = BytesIO()
            results['disease_gaps'].to_csv(csv_buffer, index=False)
            zip_file.writestr('disease_treatment_gaps.csv', csv_buffer.getvalue())
        
        if 'gaps' in results and not results['gaps'].empty:
            csv_buffer = BytesIO()
            results['gaps'].to_csv(csv_buffer, index=False)
            zip_file.writestr('coverage_gaps.csv', csv_buffer.getvalue())
        
        if 'annex_tariffs' in results and not results['annex_tariffs'].empty:
            csv_buffer = BytesIO()
            results['annex_tariffs'].to_csv(csv_buffer, index=False)
            zip_file.writestr('annex_specialty_tariffs.csv', csv_buffer.getvalue())
        
        # Add summary report
        summary = create_summary_report(results)
        zip_file.writestr('ANALYSIS_SUMMARY.md', summary)
    
    zip_buffer.seek(0)
    
    # Download button
    st.download_button(
        label="📥 Download Complete Results (ZIP)",
        data=zip_buffer.getvalue(),
        file_name=f"SHIF_Analysis_Results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.zip",
        mime="application/zip",
        type="primary"
    )

def create_summary_report(results):
    """Create a summary report of all findings"""
    
    summary = f"""# SHIF Benefits Package Analysis Summary

**Analysis Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
**Generated by:** SHIF Complete Analyzer

## Executive Summary

- **Rules Extracted:** {len(results.get('rules', []))}
- **Contradictions Found:** {len(results.get('contradictions', [])) + len(results.get('disease_gaps', []))}
- **Coverage Gaps Identified:** {len(results.get('gaps', []))}
- **Specialty Tariffs:** {len(results.get('annex_tariffs', []))}

## Key Findings

### Task 1: Rule Extraction
Successfully extracted {len(results.get('rules', []))} healthcare rules from the SHIF benefits package PDF.

### Task 2: Contradiction Detection
Found {len(results.get('contradictions', []))} service contradictions and {len(results.get('disease_gaps', []))} disease-treatment gaps.

### Task 3: Coverage Gap Analysis
Identified {len(results.get('gaps', []))} coverage gaps across different healthcare categories and service types.

---
*Analysis completed using SHIF Complete Analyzer by Pranay for Dr. Rishi*
"""
    
    return summary

def load_and_display_cached_results():
    """Load and display the pre-computed comprehensive analysis results"""
    try:
        # Load comprehensive results from cached files
        results = {}
        result_dir = 'results/outputs_comprehensive/'
        
        if not os.path.exists(result_dir):
            st.error(f"Results directory not found: {result_dir}")
            return
        
        # Load main rules
        rules_path = f'{result_dir}rules_comprehensive.csv'
        if os.path.exists(rules_path):
            rules_df = pd.read_csv(rules_path)
            results['rules'] = rules_df
            st.success(f"✅ Loaded {len(rules_df)} comprehensive rules")
        
        # Load disease gaps
        disease_gaps_path = f'{result_dir}disease_treatment_gaps.csv'
        if os.path.exists(disease_gaps_path):
            disease_gaps_df = pd.read_csv(disease_gaps_path)
            results['disease_gaps'] = disease_gaps_df
            st.success(f"✅ Loaded {len(disease_gaps_df)} disease treatment gaps")
        
        # Load comprehensive gaps
        gaps_path = f'{result_dir}comprehensive_gaps.csv'
        if os.path.exists(gaps_path):
            gaps_df = pd.read_csv(gaps_path)
            results['gaps'] = gaps_df
            st.success(f"✅ Loaded {len(gaps_df)} comprehensive gaps")
        
        # Load annex tariffs
        annex_path = f'{result_dir}annex_tariffs.csv'
        if os.path.exists(annex_path):
            annex_df = pd.read_csv(annex_path)
            results['annex_tariffs'] = annex_df
            st.success(f"✅ Loaded {len(annex_df)} annex tariffs")
        
        # Load Kenya context
        context_path = f'{result_dir}kenya_context_analysis.json'
        if os.path.exists(context_path):
            with open(context_path, 'r') as f:
                context_data = json.load(f)
            results['kenya_context'] = context_data
            st.success("✅ Loaded Kenya healthcare context analysis")
        
        # Dummy contradictions data (since we didn't find significant service contradictions)
        results['contradictions'] = pd.DataFrame()
        
        # Display results
        display_analysis_results(results)
        
        # Provide download options  
        provide_download_options(results)
        
    except Exception as e:
        st.error(f"Failed to load cached results: {e}")

def view_previous_results():
    st.header("📈 View Previous Analysis Results")
    
    # Look for existing result files
    result_dirs = ['results/outputs_comprehensive/', 'results/outputs/', 'outputs_comprehensive/', 'outputs/']
    
    available_results = []
    for dir_path in result_dirs:
        if os.path.exists(dir_path):
            files = [f for f in os.listdir(dir_path) if f.endswith('.csv')]
            if files:
                available_results.append(dir_path)
    
    if not available_results:
        st.info("No previous analysis results found. Run a new analysis first.")
        return
    
    # Select result directory
    selected_dir = st.selectbox("Select Results Directory:", available_results)
    
    if selected_dir:
        # Load and display previous results
        try:
            results = {}
            
            # Try to load various result files
            files_to_load = [
                ('rules_comprehensive.csv', 'rules'),
                ('enhanced_contradictions.csv', 'contradictions'),
                ('disease_treatment_gaps.csv', 'disease_gaps'),
                ('comprehensive_gaps.csv', 'gaps'),
                ('annex_tariffs.csv', 'annex_tariffs')
            ]
            
            for filename, key in files_to_load:
                filepath = os.path.join(selected_dir, filename)
                if os.path.exists(filepath):
                    results[key] = pd.read_csv(filepath)
                    st.success(f"✅ Loaded {filename}: {len(results[key])} records")
            
            if results:
                display_analysis_results(results)
                provide_download_options(results)
            else:
                st.warning("No valid result files found in selected directory")
                
        except Exception as e:
            st.error(f"Error loading previous results: {e}")

if __name__ == "__main__":
    main()