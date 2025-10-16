# Kenya SHIF Healthcare Policy Analyzer - Reproduction Steps

## Prerequisites
- Python 3.8+
- 8GB RAM minimum
- API keys for OpenAI/Anthropic (in .env file)

## Setup Instructions
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
# Create .env file with your API keys

# 3. Launch application
streamlit run streamlit_comprehensive_analyzer.py

# 4. Run analysis
# Click "🧠 Run Integrated Analyzer (Extended AI)" in sidebar
```

## Expected Results
- Policy Services: ~922 healthcare services extracted
- AI Analysis: Clinical contradictions + comprehensive gaps  
- Exports: JSON + CSV + ZIP packages
- Validation: Deterministic checks pass

## Support
For technical issues, verify:
1. PDF file exists: "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
2. All dependencies installed
3. API keys configured correctly
4. Port 8501 available for Streamlit
