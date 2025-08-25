#!/usr/bin/env python3
"""
AI-FIRST SHIF Benefits Analyzer - Streamlit Application
Enhanced with medical domain expertise and clinical reasoning

Features:
- AI-FIRST medical domain analysis
- Real-time contradiction detection with clinical impact assessment
- Kenya-specific gap analysis with health context
- Interactive visualization of policy contradictions
- Quality validation dashboard
- Comprehensive clinical reporting

Author: Enhanced for Dr. Rishi's AI-FIRST requirements
Version: 3.0 (AI-FIRST Implementation)
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
import time
from pathlib import Path

# Import AI-FIRST analyzer
sys.path.append('.')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import AI-FIRST components
ai_first_available = False
try:
    from ai_first_enhanced import EnhancedAIFirstAnalyzer
    ai_first_available = True
    st.sidebar.success("✅ AI-FIRST Enhanced Analyzer Loaded")
except ImportError as e:
    st.sidebar.error(f"❌ AI-FIRST Analyzer: {str(e)}")
    st.sidebar.info("💡 Install openai and other dependencies for full functionality")

# Streamlit page configuration
st.set_page_config(
    page_title="AI-FIRST SHIF Policy Analyzer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.metrics-container {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #007bff;
    margin: 1rem 0;
}
.contradiction-alert {
    background: #fff5f5;
    border: 1px solid #fed7d7;
    color: #c53030;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}
.success-alert {
    background: #f0fff4;
    border: 1px solid #9ae6b4;
    color: #276749;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}
.ai-insight {
    background: #edf2f7;
    border-left: 4px solid #4a5568;
    padding: 1rem;
    margin: 1rem 0;
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🩺 AI-FIRST SHIF Policy Analyzer</h1>
        <p>Medical Domain Expertise for Healthcare Policy Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    configure_sidebar()
    
    # Main application tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔬 AI-FIRST Analysis", 
        "📊 Contradiction Detection", 
        "🇰🇪 Kenya Gap Analysis",
        "📈 Visualization Dashboard",
        "📋 Clinical Report"
    ])
    
    with tab1:
        ai_first_analysis_tab()
    
    with tab2:
        contradiction_detection_tab()
    
    with tab3:
        kenya_gap_analysis_tab()
    
    with tab4:
        visualization_dashboard_tab()
    
    with tab5:
        clinical_report_tab()

def configure_sidebar():
    """Configure sidebar with AI-FIRST settings"""
    
    st.sidebar.markdown("## 🤖 AI-FIRST Configuration")
    
    # OpenAI Configuration
    openai_key = st.sidebar.text_input(
        "OpenAI API Key", 
        type="password",
        help="Required for live AI analysis. Leave empty for simulation mode."
    )
    
    # Model selection
    model_choice = st.sidebar.selectbox(
        "AI Model",
        ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        help="GPT-4o recommended for medical analysis"
    )
    
    # Analysis mode
    analysis_mode = st.sidebar.radio(
        "Analysis Mode",
        ["AI-FIRST Medical Reasoning", "Simulation (No API)", "Comparison Mode"],
        help="AI-FIRST applies medical domain expertise"
    )
    
    # Confidence threshold
    confidence_threshold = st.sidebar.slider(
        "Confidence Threshold",
        min_value=0.5,
        max_value=1.0,
        value=0.8,
        step=0.05,
        help="Minimum confidence for including results"
    )
    
    # Store in session state
    st.session_state.update({
        'openai_key': openai_key,
        'model_choice': model_choice,
        'analysis_mode': analysis_mode,
        'confidence_threshold': confidence_threshold
    })
    
    # System status
    st.sidebar.markdown("## 📊 System Status")
    if ai_first_available:
        st.sidebar.success("✅ AI-FIRST Ready")
    else:
        st.sidebar.warning("⚠️ Simulation Mode Only")
    
    # About section
    with st.sidebar.expander("ℹ️ About AI-FIRST"):
        st.markdown("""
        **AI-FIRST Approach:**
        - Medical domain expertise
        - Clinical reasoning for contradictions
        - Kenya health system context
        - Quality validation framework
        
        **Key Improvement:**
        Detects contradictions through medical knowledge instead of pattern matching.
        """)

def ai_first_analysis_tab():
    """AI-FIRST Analysis Tab"""
    
    st.markdown("## 🧠 AI-FIRST Medical Domain Analysis")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload SHIF Policy Document", 
        type=['pdf', 'txt'],
        help="Upload the healthcare policy document for AI-FIRST analysis"
    )
    
    if uploaded_file:
        # Analysis configuration
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size:,} bytes)")
        
        with col2:
            if st.button("🚀 Run AI-FIRST Analysis", type="primary"):
                run_ai_first_analysis(uploaded_file)
    
    # Sample analysis option
    st.markdown("---")
    st.markdown("### 🧪 Test with Sample Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🩺 Test Dialysis Contradiction Detection"):
            run_sample_dialysis_test()
    
    with col2:
        if st.button("📊 Run Comprehensive Demo"):
            run_comprehensive_demo()

def run_ai_first_analysis(uploaded_file):
    """Run AI-FIRST analysis on uploaded file"""
    
    if not ai_first_available:
        st.error("❌ AI-FIRST analyzer not available. Please check installation.")
        return
    
    try:
        # Initialize analyzer
        analyzer = EnhancedAIFirstAnalyzer(
            api_key=st.session_state.get('openai_key'),
            model=st.session_state.get('model_choice', 'gpt-4o')
        )
        
        # Extract text from file
        if uploaded_file.type == "application/pdf":
            # For demo purposes, use sample text
            document_text = get_sample_shif_text()
            st.warning("📝 Using sample SHIF text for demonstration")
        else:
            document_text = str(uploaded_file.read(), "utf-8")
        
        # Progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Run analysis
        with st.spinner("🧠 Applying medical domain expertise..."):
            status_text.text("Phase 1: Medical service extraction...")
            progress_bar.progress(25)
            
            results = analyzer.analyze_full_document_enhanced(
                document_text, 
                uploaded_file.name
            )
            
            progress_bar.progress(100)
            status_text.text("✅ AI-FIRST analysis complete!")
        
        # Store results in session state
        st.session_state['ai_first_results'] = results
        
        # Display immediate results
        display_analysis_results(results)
        
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        st.error("📋 Error details:")
        st.code(traceback.format_exc())

def run_sample_dialysis_test():
    """Run sample dialysis contradiction test"""
    
    st.markdown("### 🧪 Dialysis Contradiction Test")
    
    with st.expander("📋 Test Data", expanded=True):
        st.code("""
        RENAL CARE PACKAGE
        1. Haemodialysis - Maximum of 3 sessions per week - KES 10,650
        2. Hemodiafiltration - Maximum of 2 sessions per week - KES 12,000
        
        This creates a critical medical contradiction that AI-FIRST should detect.
        """)
    
    if ai_first_available:
        analyzer = EnhancedAIFirstAnalyzer(
            api_key=st.session_state.get('openai_key'),
            model=st.session_state.get('model_choice', 'gpt-4o')
        )
        
        sample_text = """
        RENAL CARE PACKAGE
        1. Haemodialysis - Maximum of 3 sessions per week - KES 10,650 per session
        2. Hemodiafiltration - Maximum of 2 sessions per week - KES 12,000 per session
        """
        
        with st.spinner("🩺 Testing dialysis contradiction detection..."):
            results = analyzer.analyze_full_document_enhanced(sample_text, "Dialysis_Test")
        
        # Check for dialysis contradiction
        dialysis_found = any('dialysis' in str(c).lower() for c in results.get('contradictions', []))
        
        if dialysis_found:
            st.markdown("""
            <div class="success-alert">
                <h4>🎯 SUCCESS: Dialysis Contradiction DETECTED!</h4>
                <p>AI-FIRST medical reasoning successfully identified the session frequency inconsistency.</p>
            </div>
            """, unsafe_allow_html=True)
            
            for contradiction in results.get('contradictions', []):
                if 'dialysis' in str(contradiction).lower():
                    st.json(contradiction)
        else:
            st.markdown("""
            <div class="contradiction-alert">
                <h4>⚠️ Contradiction not detected in test</h4>
                <p>Check API configuration or system status.</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.warning("📝 AI-FIRST analyzer not available - showing expected result:")
        st.json({
            "contradiction_type": "dialysis_session_inconsistency",
            "description": "Hemodialysis allows 3 sessions/week while hemodiafiltration allows only 2 sessions/week",
            "clinical_impact": "CRITICAL",
            "medical_rationale": "Both dialysis modalities treat ESRD and should have consistent session limits"
        })

def display_analysis_results(results):
    """Display AI-FIRST analysis results"""
    
    st.markdown("## 📊 AI-FIRST Analysis Results")
    
    # Metrics overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Services Extracted",
            len(results.get('services', [])),
            help="Services identified with medical context"
        )
    
    with col2:
        contradictions = results.get('contradictions', [])
        critical_count = len([c for c in contradictions if c.get('clinical_priority') == 'CRITICAL'])
        st.metric(
            "Critical Contradictions",
            critical_count,
            delta=critical_count if critical_count > 0 else None,
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "Policy Gaps",
            len(results.get('gaps', [])),
            help="Kenya-specific coverage gaps identified"
        )
    
    with col4:
        quality_score = results.get('quality_metrics', {}).get('overall_quality_score', 0)
        st.metric(
            "Quality Score",
            f"{quality_score:.2f}",
            help="Overall analysis quality (0-1.0)"
        )
    
    # Key findings
    if contradictions:
        st.markdown("### 🚨 Critical Contradictions Detected")
        
        for i, contradiction in enumerate(contradictions[:3], 1):
            with st.expander(f"Contradiction {i}: {contradiction.get('contradiction_type', 'Unknown')}", expanded=True):
                
                # Description
                st.markdown(f"**Description:** {contradiction.get('description', 'N/A')}")
                
                # Clinical impact
                impact = contradiction.get('impact_assessment', {})
                clinical_impact = impact.get('clinical_impact', 'Unknown')
                
                if clinical_impact == 'CRITICAL':
                    st.error(f"🚨 Clinical Impact: {clinical_impact}")
                elif clinical_impact == 'HIGH':
                    st.warning(f"⚠️ Clinical Impact: {clinical_impact}")
                else:
                    st.info(f"ℹ️ Clinical Impact: {clinical_impact}")
                
                # Medical analysis
                if 'medical_analysis' in contradiction:
                    medical = contradiction['medical_analysis']
                    st.markdown("**Medical Rationale:**")
                    st.info(medical.get('clinical_rationale', 'N/A'))
                
                # Recommendations
                if 'recommendations' in contradiction:
                    rec = contradiction['recommendations']
                    st.markdown("**Recommendations:**")
                    st.success(rec.get('immediate_action', 'N/A'))

def contradiction_detection_tab():
    """Contradiction Detection Tab"""
    
    st.markdown("## ⚕️ Medical Contradiction Detection")
    
    if 'ai_first_results' not in st.session_state:
        st.info("👆 Run AI-FIRST analysis first to see contradiction detection results")
        return
    
    results = st.session_state['ai_first_results']
    contradictions = results.get('contradictions', [])
    
    if not contradictions:
        st.success("✅ No medical contradictions detected in the policy")
        return
    
    # Contradiction analysis
    st.markdown(f"### 📊 Found {len(contradictions)} Policy Contradictions")
    
    # Severity distribution
    severity_counts = {}
    for c in contradictions:
        severity = c.get('clinical_priority', 'UNKNOWN')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Severity visualization
    if severity_counts:
        severity_df = pd.DataFrame(list(severity_counts.items()), columns=['Severity', 'Count'])
        fig_severity = px.bar(
            severity_df, 
            x='Severity', 
            y='Count',
            color='Severity',
            color_discrete_map={
                'CRITICAL': '#dc2626',
                'HIGH': '#ea580c', 
                'MEDIUM': '#ca8a04',
                'LOW': '#16a34a'
            },
            title="Contradictions by Clinical Severity"
        )
        st.plotly_chart(fig_severity, use_container_width=True)
    
    # Detailed contradiction analysis
    st.markdown("### 🔍 Detailed Contradiction Analysis")
    
    for i, contradiction in enumerate(contradictions, 1):
        with st.container():
            # Contradiction header
            priority = contradiction.get('clinical_priority', 'UNKNOWN')
            if priority == 'CRITICAL':
                st.error(f"🚨 Contradiction {i}: {contradiction.get('contradiction_type', 'Unknown')}")
            else:
                st.warning(f"⚠️ Contradiction {i}: {contradiction.get('contradiction_type', 'Unknown')}")
            
            # Tabbed details
            tab1, tab2, tab3 = st.tabs(["📋 Overview", "🩺 Clinical Analysis", "💡 Recommendations"])
            
            with tab1:
                st.markdown(f"**Description:** {contradiction.get('description', 'N/A')}")
                st.markdown(f"**Services Involved:** {', '.join(contradiction.get('services_involved', []))}")
                
                if 'evidence_documentation' in contradiction:
                    evidence = contradiction['evidence_documentation']
                    st.markdown("**Evidence:**")
                    st.code(f"Policy 1: {evidence.get('policy_text_hd', 'N/A')}")
                    st.code(f"Policy 2: {evidence.get('policy_text_hdf', 'N/A')}")
            
            with tab2:
                if 'medical_analysis' in contradiction:
                    medical = contradiction['medical_analysis']
                    st.markdown("**Clinical Rationale:**")
                    st.info(medical.get('clinical_rationale', 'N/A'))
                    
                    st.markdown("**Evidence Base:**")
                    st.text(medical.get('evidence_base', 'N/A'))
                
                if 'clinical_consequences' in contradiction:
                    consequences = contradiction['clinical_consequences']
                    st.markdown("**Clinical Consequences:**")
                    st.error(f"Immediate Risk: {consequences.get('immediate_risk', 'N/A')}")
                    st.warning(f"Long-term Impact: {consequences.get('long_term_impact', 'N/A')}")
            
            with tab3:
                if 'recommendations' in contradiction:
                    rec = contradiction['recommendations']
                    st.markdown("**Immediate Action:**")
                    st.success(rec.get('immediate_action', 'N/A'))
                    
                    st.markdown("**Policy Revision:**")
                    st.info(rec.get('policy_revision', 'N/A'))
            
            st.markdown("---")

def kenya_gap_analysis_tab():
    """Kenya-specific Gap Analysis Tab"""
    
    st.markdown("## 🇰🇪 Kenya Health System Gap Analysis")
    
    if 'ai_first_results' not in st.session_state:
        st.info("👆 Run AI-FIRST analysis first to see gap analysis results")
        return
    
    results = st.session_state['ai_first_results']
    gaps = results.get('gaps', [])
    
    if not gaps:
        st.success("✅ No significant policy gaps identified")
        return
    
    # Gap overview
    st.markdown(f"### 📊 Identified {len(gaps)} Policy Gaps")
    
    # Priority distribution
    priority_counts = {}
    for g in gaps:
        priority = g.get('priority_level', 'UNKNOWN')
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    # Priority visualization
    if priority_counts:
        priority_df = pd.DataFrame(list(priority_counts.items()), columns=['Priority', 'Count'])
        fig_priority = px.pie(
            priority_df,
            values='Count',
            names='Priority',
            color='Priority',
            color_discrete_map={
                'CRITICAL': '#dc2626',
                'HIGH': '#ea580c',
                'MEDIUM': '#ca8a04',
                'LOW': '#16a34a'
            },
            title="Policy Gaps by Priority Level"
        )
        st.plotly_chart(fig_priority, use_container_width=True)
    
    # Detailed gap analysis
    st.markdown("### 🔍 Detailed Gap Analysis")
    
    for i, gap in enumerate(gaps, 1):
        with st.expander(f"Gap {i}: {gap.get('gap_category', 'Unknown')}", expanded=True):
            
            # Gap overview
            st.markdown(f"**Description:** {gap.get('description', 'N/A')}")
            
            # Kenya health impact
            if 'kenya_health_impact' in gap:
                impact = gap['kenya_health_impact']
                st.markdown("**Kenya Health Impact:**")
                st.error(f"Disease Burden: {impact.get('disease_burden', 'N/A')}")
                st.info(f"Affected Population: {impact.get('incidence_data', 'N/A')}")
            
            # Affected populations
            if 'affected_populations' in gap:
                pop = gap['affected_populations']
                st.markdown("**Affected Population:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Estimated Numbers", f"{pop.get('estimated_numbers', 0):,}")
                with col2:
                    st.info(f"Demographics: {pop.get('demographic_profile', 'N/A')}")
            
            # Recommendations
            if 'recommended_interventions' in gap:
                interventions = gap['recommended_interventions']
                st.markdown("**Recommended Services:**")
                for service in interventions.get('service_additions', []):
                    st.write(f"• {service}")
            
            # Implementation
            if 'implementation_considerations' in gap:
                impl = gap['implementation_considerations']
                st.markdown("**Implementation:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    priority = impl.get('priority_level', 'UNKNOWN')
                    if priority == 'CRITICAL':
                        st.error(f"Priority: {priority}")
                    else:
                        st.warning(f"Priority: {priority}")
                with col2:
                    st.info(f"Feasibility: {impl.get('feasibility', 'N/A')}")
                with col3:
                    st.text(f"Timeline: {impl.get('timeline', 'N/A')}")

def visualization_dashboard_tab():
    """Visualization Dashboard Tab"""
    
    st.markdown("## 📈 AI-FIRST Analysis Dashboard")
    
    if 'ai_first_results' not in st.session_state:
        st.info("👆 Run AI-FIRST analysis first to see visualizations")
        return
    
    results = st.session_state['ai_first_results']
    
    # Analysis overview
    col1, col2 = st.columns(2)
    
    with col1:
        # Quality metrics
        quality_data = results.get('quality_metrics', {})
        if quality_data:
            st.markdown("### 📊 Analysis Quality Metrics")
            
            # Service extraction quality
            if 'service_extraction' in quality_data:
                se = quality_data['service_extraction']
                st.write(f"**Service Extraction:**")
                st.write(f"• Total services: {se.get('total_services', 0)}")
                st.write(f"• High confidence: {se.get('high_confidence_services', 0)}")
                st.write(f"• Medical categories: {se.get('medical_categories_identified', 0)}")
    
    with col2:
        # Analysis metadata
        metadata = results.get('metadata', {})
        if metadata:
            st.markdown("### ⚙️ Analysis Metadata")
            st.write(f"**Approach:** {metadata.get('approach', 'N/A')}")
            st.write(f"**Model:** {metadata.get('model_used', 'N/A')}")
            st.write(f"**Time:** {metadata.get('total_time_seconds', 0):.1f}s")
            st.write(f"**Status:** {metadata.get('completion_status', 'N/A')}")
    
    # Services visualization
    services = results.get('services', [])
    if services:
        st.markdown("### 🏥 Services by Medical Category")
        
        # Category distribution
        category_counts = {}
        for service in services:
            category = service.get('medical_category', 'other')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        if category_counts:
            category_df = pd.DataFrame(
                list(category_counts.items()), 
                columns=['Medical Category', 'Service Count']
            )
            
            fig_categories = px.treemap(
                category_df,
                path=['Medical Category'],
                values='Service Count',
                title="Services by Medical Category"
            )
            st.plotly_chart(fig_categories, use_container_width=True)

def clinical_report_tab():
    """Clinical Report Tab"""
    
    st.markdown("## 📋 Clinical Analysis Report")
    
    if 'ai_first_results' not in st.session_state:
        st.info("👆 Run AI-FIRST analysis first to generate clinical report")
        return
    
    results = st.session_state['ai_first_results']
    
    # Executive summary
    st.markdown("### 📄 Executive Summary")
    
    services_count = len(results.get('services', []))
    contradictions_count = len(results.get('contradictions', []))
    gaps_count = len(results.get('gaps', []))
    
    st.markdown(f"""
    **AI-FIRST Medical Domain Analysis Results:**
    
    • **Services Analyzed:** {services_count} healthcare services with medical context
    • **Contradictions Detected:** {contradictions_count} policy contradictions identified through clinical reasoning
    • **Coverage Gaps:** {gaps_count} Kenya-specific health system gaps identified
    
    **Analysis Approach:** Enhanced AI-FIRST implementation applying medical domain expertise 
    instead of pattern matching for healthcare policy analysis.
    """)
    
    # Key findings
    contradictions = results.get('contradictions', [])
    critical_contradictions = [c for c in contradictions if c.get('clinical_priority') == 'CRITICAL']
    
    if critical_contradictions:
        st.markdown("### 🚨 Critical Clinical Findings")
        
        for contradiction in critical_contradictions:
            st.error(f"**{contradiction.get('contradiction_type', 'Unknown')}**")
            st.write(f"Description: {contradiction.get('description', 'N/A')}")
            
            if 'clinical_consequences' in contradiction:
                consequences = contradiction['clinical_consequences']
                st.write(f"Clinical Risk: {consequences.get('immediate_risk', 'N/A')}")
    
    # Recommendations
    st.markdown("### 💡 Clinical Recommendations")
    
    if contradictions:
        st.markdown("**Immediate Actions Required:**")
        for i, contradiction in enumerate(contradictions[:3], 1):
            if 'recommendations' in contradiction:
                rec = contradiction['recommendations']
                st.write(f"{i}. {rec.get('immediate_action', 'N/A')}")
    
    # Export functionality
    st.markdown("### 📤 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate PDF Report"):
            st.info("PDF generation feature would be implemented here")
    
    with col2:
        if st.button("💾 Download JSON Results"):
            json_str = json.dumps(results, indent=2)
            st.download_button(
                label="📥 Download",
                data=json_str,
                file_name="ai_first_analysis_results.json",
                mime="application/json"
            )

def get_sample_shif_text():
    """Get sample SHIF text for demonstration"""
    return """
    --- PAGE 8 ---
    RENAL CARE PACKAGE
    
    The Social Health Insurance Fund covers the following renal replacement therapy services:
    
    1. Haemodialysis
       - Indication: Chronic kidney disease Stage 5 (eGFR <15 ml/min/1.73m²)
       - Coverage: Maximum of 3 sessions per week for adequate clearance
       - Duration: 4 hours per session minimum
       - Available at: Level 4, 5, and 6 facilities with dialysis capability
       - Tariff: KES 10,650 per session
       - Authorization: Pre-authorization required
    
    2. Hemodiafiltration (Advanced Dialysis)
       - Indication: Chronic kidney disease Stage 5 with cardiovascular complications
       - Coverage: Maximum of 2 sessions per week with enhanced clearance
       - Duration: 4 hours per session minimum
       - Available at: Level 5 and 6 facilities
       - Tariff: KES 12,000 per session
       - Authorization: Pre-authorization required
    
    --- PAGE 15 ---
    SURGICAL PROCEDURES
    
    1. Cardiac Surgery
       - Available at: Level 6 facilities only
       - Tariff: KES 150,000 per procedure
       - Authorization: Specialist referral required
    
    2. Neurosurgery
       - Available at: Level 5 and 6 facilities
       - Tariff: KES 120,000 per procedure
       - Authorization: Specialist referral required
    """

def run_comprehensive_demo():
    """Run comprehensive AI-FIRST demo"""
    
    st.markdown("### 🎯 Comprehensive AI-FIRST Demo")
    
    demo_text = get_sample_shif_text()
    
    if ai_first_available:
        analyzer = EnhancedAIFirstAnalyzer(
            api_key=st.session_state.get('openai_key'),
            model=st.session_state.get('model_choice', 'gpt-4o')
        )
        
        with st.spinner("🧠 Running comprehensive AI-FIRST analysis..."):
            results = analyzer.analyze_full_document_enhanced(demo_text, "Comprehensive_Demo")
        
        st.session_state['ai_first_results'] = results
        
        st.success("✅ Comprehensive demo complete! Check other tabs for detailed results.")
        
        # Quick summary
        st.markdown("**Quick Results:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Services", len(results.get('services', [])))
        with col2:
            st.metric("Contradictions", len(results.get('contradictions', [])))
        with col3:
            st.metric("Gaps", len(results.get('gaps', [])))
    
    else:
        st.warning("🔧 AI-FIRST analyzer not available - showing sample results structure")
        
        sample_results = {
            'services': [{'service_name': 'Hemodialysis', 'medical_category': 'renal_replacement_therapy'}],
            'contradictions': [{
                'contradiction_type': 'dialysis_session_inconsistency',
                'description': 'Different session limits for related dialysis procedures',
                'clinical_priority': 'CRITICAL'
            }],
            'gaps': [{'gap_category': 'stroke_rehabilitation', 'priority_level': 'HIGH'}],
            'metadata': {'approach': 'AI_FIRST_SIMULATION'}
        }
        
        st.session_state['ai_first_results'] = sample_results
        st.json(sample_results)

if __name__ == "__main__":
    main()