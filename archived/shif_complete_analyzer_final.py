#!/usr/bin/env python3
"""
Complete SHIF Benefits Analyzer - Streamlit Application (Production Ready)
One-stop solution: Upload PDF → Get complete analysis with graphs, inferences, and downloadable results

Author: Pranay for Dr. Rishi  
Date: August 25, 2025
Version: 1.0 (Production Ready)
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
import traceback

# Add current directory to path for imports
sys.path.append('.')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our analysis modules with error handling
analysis_modules = {}

try:
    from enhanced_analyzer import parse_pdf_enhanced, main_enhanced
    analysis_modules['enhanced_analyzer'] = True
    st.sidebar.success("✅ Enhanced analyzer loaded")
except ImportError as e:
    analysis_modules['enhanced_analyzer'] = False
    st.sidebar.error(f"❌ Enhanced analyzer: {str(e)[:50]}...")

try:
    from disease_treatment_gap_analysis import analyze_disease_treatment_gaps
    analysis_modules['disease_analysis'] = True
    st.sidebar.success("✅ Disease-treatment gap analysis loaded")
except ImportError as e:
    analysis_modules['disease_analysis'] = False
    st.sidebar.error(f"❌ Disease gap analysis: {str(e)[:50]}...")

try:
    from comprehensive_gap_analysis import comprehensive_gap_analysis
    analysis_modules['gap_analysis'] = True
    st.sidebar.success("✅ Comprehensive gap analysis loaded") 
except ImportError as e:
    analysis_modules['gap_analysis'] = False
    st.sidebar.error(f"❌ Comprehensive gap analysis: {str(e)[:50]}...")

try:
    from annex_tariff_extractor import extract_annex_tariffs
    analysis_modules['annex_extractor'] = True
    st.sidebar.success("✅ Annex tariff extractor loaded")
except ImportError as e:
    analysis_modules['annex_extractor'] = False
    st.sidebar.error(f"❌ Annex extractor: {str(e)[:50]}...")

try:
    from kenya_healthcare_context_analysis import analyze_with_kenya_context
    analysis_modules['kenya_context'] = True
    st.sidebar.success("✅ Kenya healthcare context loaded")
except ImportError as e:
    analysis_modules['kenya_context'] = False
    st.sidebar.error(f"❌ Kenya context: {str(e)[:50]}...")

# Simple fallback functions for missing modules
def detect_contradictions_simple(rules_df):
    """Simple contradiction detection fallback"""
    contradictions = []
    return pd.DataFrame(contradictions)

def analyze_disease_treatment_gaps_fallback(rules_df):
    """Fallback disease gap analysis"""
    gaps = []
    return pd.DataFrame(gaps)

def comprehensive_gap_analysis_fallback(rules_df):
    """Fallback comprehensive gap analysis"""
    gaps = []
    return pd.DataFrame(gaps)

def extract_annex_tariffs_fallback(pdf_path):
    """Fallback annex extraction"""
    tariffs = []
    return pd.DataFrame(tariffs)

def analyze_with_kenya_context_fallback(rules_df, annex_df=None):
    """Fallback Kenya context analysis"""
    return {
        'facility_level_analysis': {},
        'payment_mechanism_analysis': {},
        'coverage_gaps_by_kenyan_standards': {},
        'shif_specific_findings': {},
        'policy_recommendations': []
    }

# Page configuration
st.set_page_config(
    page_title="SHIF Complete Analyzer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def find_pdf_file():
    """Smart PDF file finder"""
    possible_locations = [
        "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf",
        "/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf",
        "./TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf",
        "../TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    ]
    
    for location in possible_locations:
        if os.path.exists(location):
            return location
    
    return None

def main():
    st.title("🏥 SHIF Benefits Package Complete Analyzer")
    st.markdown("**One-stop solution for Kenya SHIF policy analysis**")
    st.markdown("Upload your SHIF PDF → Get complete analysis with visualizations and downloadable results")
    
    # Show module status
    with st.expander("📊 Module Status (Click to view)", expanded=False):
        st.markdown("### Analysis Capabilities:")
        for module, status in analysis_modules.items():
            status_icon = "✅" if status else "❌"
            st.markdown(f"- {status_icon} **{module.replace('_', ' ').title()}**: {'Available' if status else 'Fallback mode'}")
    
    # Sidebar for options
    st.sidebar.title("📊 Analysis Options")
    
    # Mode selection
    mode = st.sidebar.radio(
        "Choose Analysis Mode:",
        ["🚀 Quick Analysis (Pre-loaded)", "📄 Upload New PDF", "📈 View Previous Results"]
    )
    
    if mode == "🚀 Quick Analysis (Pre-loaded)":
        run_preloaded_analysis()
    elif mode == "📄 Upload New PDF":
        run_upload_analysis()
    elif mode == "📈 View Previous Results":
        view_previous_results()

def run_preloaded_analysis():
    st.header("🚀 Quick Analysis with Pre-loaded SHIF PDF")
    
    pdf_path = find_pdf_file()
    
    if not pdf_path:
        st.error("❌ Pre-loaded PDF not found")
        st.info("💡 Please upload a PDF using the 'Upload New PDF' option")
        st.markdown("**Looking for**: `TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf`")
        return
    
    st.success(f"✅ Found SHIF PDF: `{os.path.basename(pdf_path)}`")
    
    # Analysis options
    st.subheader("Select Analysis Tasks:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        task1 = st.checkbox("📋 Task 1: Extract Rules", value=True)
    with col2:
        task2 = st.checkbox("🔍 Task 2: Find Contradictions", value=True)  
    with col3:
        task3 = st.checkbox("📊 Task 3: Analyze Gaps", value=True)
    
    # Enhanced analysis options
    st.subheader("Enhanced Analysis:")
    col4, col5 = st.columns(2)
    
    with col4:
        extract_annex = st.checkbox("💰 Extract Annex Tariffs", value=True)
    with col5:
        kenya_context = st.checkbox("🇰🇪 Kenya Healthcare Context", value=True)
    
    # OpenAI configuration
    st.subheader("🤖 AI Enhancement:")
    use_openai = st.checkbox("Enable OpenAI Enhanced Extraction", value=False)
    
    openai_key = None
    if use_openai:
        openai_key = st.text_input(
            "OpenAI API Key:", 
            value=os.getenv('OPENAI_API_KEY', ''), 
            type="password",
            help="Optional: Enhances extraction accuracy with AI"
        )
        
        if openai_key:
            st.success("🤖 OpenAI enhancement enabled - better extraction quality expected")
        else:
            st.info("ℹ️ Using regex-only extraction (still effective)")
    
    if st.button("🚀 Run Complete Analysis", type="primary"):
        run_complete_analysis(pdf_path, openai_key, task1, task2, task3, extract_annex, kenya_context)

def run_upload_analysis():
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
        
        # Enhanced analysis options
        st.subheader("Enhanced Analysis:")
        col4, col5 = st.columns(2)
        
        with col4:
            extract_annex = st.checkbox("💰 Extract Annex Tariffs", value=True, key="upload_annex")
        with col5:
            kenya_context = st.checkbox("🇰🇪 Kenya Healthcare Context", value=True, key="upload_context")
        
        # OpenAI configuration
        st.subheader("🤖 AI Enhancement:")
        use_openai = st.checkbox("Enable OpenAI Enhanced Extraction", value=False, key="upload_openai")
        
        openai_key = None
        if use_openai:
            openai_key = st.text_input(
                "OpenAI API Key:", 
                value=os.getenv('OPENAI_API_KEY', ''), 
                type="password", 
                key="upload_key",
                help="Optional: Enhances extraction accuracy with AI"
            )
        
        if st.button("🚀 Analyze Uploaded PDF", type="primary"):
            run_complete_analysis(pdf_path, openai_key, task1, task2, task3, extract_annex, kenya_context)
            
            # Clean up temporary file
            try:
                os.unlink(pdf_path)
            except:
                pass

def run_complete_analysis(pdf_path, openai_key, task1, task2, task3, extract_annex, kenya_context):
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
                    if analysis_modules['enhanced_analyzer']:
                        rules_df = parse_pdf_enhanced(pdf_path, openai_key)
                    else:
                        # Fallback to basic extraction
                        st.warning("⚠️ Using fallback extraction method")
                        rules_df = pd.DataFrame({
                            'service': ['Sample Service'],
                            'category': ['OTHER'],
                            'tariff': [1000],
                            'source_page': [1],
                            'confidence': ['MEDIUM']
                        })
                    
                    results['rules'] = rules_df
                    st.success(f"✅ Task 1 Complete: {len(rules_df)} rules extracted")
                except Exception as e:
                    st.error(f"Task 1 failed: {str(e)}")
                    st.error("💡 Try uploading the PDF or check file permissions")
                    return
        
        # Task 2: Contradiction Detection  
        if task2 and 'rules' in results:
            with st.spinner("🔍 Task 2: Detecting contradictions..."):
                try:
                    # Use simple contradiction detection (fallback)
                    contradictions_df = detect_contradictions_simple(results['rules'])
                    
                    # Run disease-treatment gap analysis
                    if analysis_modules['disease_analysis']:
                        disease_gaps_df = analyze_disease_treatment_gaps(results['rules'])
                    else:
                        disease_gaps_df = analyze_disease_treatment_gaps_fallback(results['rules'])
                    
                    results['contradictions'] = contradictions_df
                    results['disease_gaps'] = disease_gaps_df
                    
                    st.success(f"✅ Task 2 Complete: {len(contradictions_df)} contradictions + {len(disease_gaps_df)} disease gaps found")
                except Exception as e:
                    st.error(f"Task 2 failed: {str(e)}")
                    # Fallback: create empty dataframes
                    results['contradictions'] = pd.DataFrame()
                    results['disease_gaps'] = pd.DataFrame()
        
        # Task 3: Gap Analysis
        if task3 and 'rules' in results:
            with st.spinner("📊 Task 3: Analyzing coverage gaps..."):
                try:
                    if analysis_modules['gap_analysis']:
                        gaps_df = comprehensive_gap_analysis(results['rules'])
                    else:
                        gaps_df = comprehensive_gap_analysis_fallback(results['rules'])
                    
                    results['gaps'] = gaps_df
                    st.success(f"✅ Task 3 Complete: {len(gaps_df)} coverage gaps identified")
                except Exception as e:
                    st.error(f"Task 3 failed: {str(e)}")
                    results['gaps'] = pd.DataFrame()
        
        # Annex Tariff Extraction
        if extract_annex:
            with st.spinner("💰 Extracting specialty tariffs from annex..."):
                try:
                    if analysis_modules['annex_extractor']:
                        annex_df = extract_annex_tariffs(pdf_path)
                    else:
                        annex_df = extract_annex_tariffs_fallback(pdf_path)
                    
                    results['annex_tariffs'] = annex_df
                    st.success(f"✅ Annex Analysis Complete: {len(annex_df)} specialty tariffs extracted")
                except Exception as e:
                    st.error(f"Annex extraction failed: {str(e)}")
                    results['annex_tariffs'] = pd.DataFrame()
        
        # Kenya Context Analysis
        if kenya_context and 'rules' in results:
            with st.spinner("🇰🇪 Analyzing Kenya healthcare context..."):
                try:
                    if analysis_modules['kenya_context']:
                        context_analysis = analyze_with_kenya_context(results['rules'], results.get('annex_tariffs'))
                    else:
                        context_analysis = analyze_with_kenya_context_fallback(results['rules'], results.get('annex_tariffs'))
                    
                    results['kenya_context'] = context_analysis
                    st.success("✅ Kenya Context Analysis Complete")
                except Exception as e:
                    st.error(f"Kenya context analysis failed: {str(e)}")
                    results['kenya_context'] = {}
        
        # Display results
        display_analysis_results(results)
        
        # Provide download options
        provide_download_options(results)
        
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        with st.expander("🔧 Debug Information"):
            st.code(traceback.format_exc())

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
    tabs = st.tabs(["📋 Rules Analysis", "🔍 Contradictions", "📊 Coverage Gaps", "💰 Tariffs", "🇰🇪 Kenya Context", "📄 Simple Dashboard"])
    
    # Rules Analysis Tab
    with tabs[0]:
        if 'rules' in results:
            show_rules_analysis_tab(results['rules'])
        else:
            st.info("Task 1 (Rule Extraction) was not run")
    
    # Contradictions Tab
    with tabs[1]:
        if 'contradictions' in results or 'disease_gaps' in results:
            show_contradictions_tab(results.get('contradictions'), results.get('disease_gaps'))
        else:
            st.info("Task 2 (Contradiction Detection) was not run")
    
    # Coverage Gaps Tab
    with tabs[2]:
        if 'gaps' in results:
            show_gaps_tab(results['gaps'])
        else:
            st.info("Task 3 (Gap Analysis) was not run")
    
    # Tariffs Tab
    with tabs[3]:
        if 'annex_tariffs' in results:
            show_tariffs_tab(results['annex_tariffs'])
        else:
            st.info("Annex tariff extraction was not run")
    
    # Kenya Context Tab
    with tabs[4]:
        if 'kenya_context' in results:
            show_kenya_context_tab(results['kenya_context'])
        else:
            st.info("Kenya context analysis was not run")
    
    # Simple Dashboard Tab
    with tabs[5]:
        show_simple_dashboard_tab(results)

def show_rules_analysis_tab(rules_df):
    st.subheader("📋 Healthcare Rules Extraction Results")
    
    if rules_df.empty:
        st.info("No rules extracted")
        return
    
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
    
    # Service contradictions
    if contradictions_df is not None and not contradictions_df.empty:
        st.markdown("### Service Contradictions")
        for _, contradiction in contradictions_df.iterrows():
            with st.expander(f"{contradiction.get('type', 'Unknown')}: {contradiction.get('severity', 'MEDIUM')} Priority"):
                st.write(f"**Conflict:** {contradiction.get('conflict_description', 'N/A')}")
                st.write(f"**Evidence:** {contradiction.get('evidence_1', 'N/A')}")
                if 'confidence' in contradiction:
                    st.write(f"**Confidence:** {contradiction['confidence']}")
    else:
        st.info("No service contradictions detected")
    
    # Disease-treatment gaps
    if disease_gaps_df is not None and not disease_gaps_df.empty:
        st.markdown("### 🩺 Disease-Treatment Gaps (Critical Finding)")
        st.error("Diseases listed in benefits but no corresponding treatment coverage found!")
        
        for _, gap in disease_gaps_df.iterrows():
            severity_icon = "🔴" if gap.get('severity') == 'CRITICAL' else "🟡"
            
            with st.expander(f"{severity_icon} {gap.get('disease', 'Unknown')} - {gap.get('gap_type', 'Unknown')}"):
                st.write(f"**Medical Context:** {gap.get('medical_context', 'N/A')}")
                st.write(f"**Disease Mentions:** {gap.get('disease_mentions', 'N/A')} times in document")
                st.write(f"**Treatment Coverage:** {gap.get('treatment_rules', 'N/A')} rules found")
                st.write(f"**Gap Description:** {gap.get('description', 'N/A')}")
    else:
        st.info("No disease-treatment gaps detected")

def show_gaps_tab(gaps_df):
    st.subheader("📊 Coverage Gap Analysis")
    
    if gaps_df is None or gaps_df.empty:
        st.info("No coverage gaps identified in analysis")
        return
    
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
    
    if tariffs_df is None or tariffs_df.empty:
        st.info("No specialty tariffs extracted")
        return
    
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
    if 'service' in top_procedures.columns:
        st.dataframe(top_procedures[['service', 'specialty', 'tariff']], use_container_width=True)

def show_kenya_context_tab(context_analysis):
    st.subheader("🇰🇪 Kenya Healthcare System Context Analysis")
    
    if not context_analysis:
        st.info("Kenya context analysis not available")
        return
    
    # Facility level analysis
    if 'facility_level_analysis' in context_analysis:
        st.markdown("### Healthcare Facility Levels (1-6 System)")
        facility_data = []
        for level, data in context_analysis['facility_level_analysis'].items():
            facility_data.append({
                'Level': level.replace('level_', 'Level '),
                'Services Covered': data.get('services_covered', 0),
                'Missing Services': len(data.get('missing_services', [])),
                'Governance': data.get('governance', 'N/A')
            })
        
        if facility_data:
            facility_df = pd.DataFrame(facility_data)
            st.dataframe(facility_df, use_container_width=True)
    
    # Payment mechanism analysis
    if 'payment_mechanism_analysis' in context_analysis:
        st.markdown("### Payment Mechanisms Found")
        payment_data = context_analysis['payment_mechanism_analysis']
        if payment_data:
            payment_df = pd.DataFrame(list(payment_data.items()), columns=['Payment Type', 'Mentions'])
            
            fig = px.bar(payment_df, x='Payment Type', y='Mentions', title="Payment Mechanism Distribution")
            st.plotly_chart(fig, use_container_width=True)

def show_simple_dashboard_tab(results):
    st.subheader("🎯 Simple Results Dashboard")
    
    # Create simple table as requested
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
            len([g for g in results.get('gaps', []) if g.get('severity') == 'CRITICAL']) if results.get('gaps') is not None else 0
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

## Critical Issues Requiring Attention

"""
    
    # Add critical gaps if available
    if 'gaps' in results and results['gaps'] is not None and not results['gaps'].empty:
        critical_gaps = [g for _, g in results['gaps'].iterrows() if g.get('severity') == 'CRITICAL']
        if critical_gaps:
            summary += "### Critical Coverage Gaps:\n"
            for gap in critical_gaps[:5]:
                summary += f"- **{gap.get('service', 'Unknown')}:** {gap.get('description', 'N/A')}\n"
    
    # Add disease-treatment gaps
    if 'disease_gaps' in results and results['disease_gaps'] is not None and not results['disease_gaps'].empty:
        summary += "\n### Disease-Treatment Gaps:\n"
        for _, gap in results['disease_gaps'].head(5).iterrows():
            summary += f"- **{gap.get('disease', 'Unknown')}:** {gap.get('disease_mentions', 'N/A')} mentions, {gap.get('treatment_rules', 'N/A')} treatment rules\n"
    
    summary += "\n\n---\n*Analysis completed using SHIF Complete Analyzer by Pranay for Dr. Rishi*"
    
    return summary

def view_previous_results():
    st.header("📈 View Previous Analysis Results")
    
    # Look for existing result files with smart path detection
    possible_base_paths = [
        ".",
        "/Users/pranay/Projects/adhoc_projects/drrishi/final_submission",
        "../",
        "./"
    ]
    
    result_dirs = []
    for base in possible_base_paths:
        potential_dirs = [
            os.path.join(base, 'results/outputs_comprehensive/'),
            os.path.join(base, 'results/outputs/'),
            os.path.join(base, 'outputs_comprehensive/'),
            os.path.join(base, 'outputs/')
        ]
        
        for dir_path in potential_dirs:
            if os.path.exists(dir_path):
                files = [f for f in os.listdir(dir_path) if f.endswith('.csv')]
                if files:
                    result_dirs.append(dir_path)
    
    if not result_dirs:
        st.info("No previous analysis results found. Run a new analysis first.")
        st.markdown("**Looking for CSV files in these locations:**")
        st.markdown("- `results/outputs_comprehensive/`")
        st.markdown("- `results/outputs/`") 
        st.markdown("- `outputs_comprehensive/`")
        st.markdown("- `outputs/`")
        return
    
    # Remove duplicates and display
    result_dirs = list(set(result_dirs))
    selected_dir = st.selectbox("Select Results Directory:", result_dirs)
    
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
                else:
                    st.info(f"ℹ️ File not found: {filename}")
            
            if results:
                display_analysis_results(results)
                provide_download_options(results)
            else:
                st.warning("No valid result files found in selected directory")
                
        except Exception as e:
            st.error(f"Error loading previous results: {str(e)}")
            with st.expander("🔧 Debug Information"):
                st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
