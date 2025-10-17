# Deployment Configuration for Kenya SHIF Analyzer

## Environment Setup

### For Development
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

### For Production (Streamlit Cloud)

1. **Repository Setup**
   - Fork/push to GitHub: `pranaysuyash/kenya-shif`
   - Ensure all files are committed
   - Latest commit hash: Use `git rev-parse --short HEAD`

2. **Streamlit Cloud Deployment**
   - Visit https://streamlit.io/cloud
   - Sign in with GitHub account
   - Click "New app"
   - Select repository: `pranaysuyash/kenya-shif`
   - Branch: `main`
   - Main file path: `streamlit_comprehensive_analyzer.py`
   - Click Deploy

3. **Configure Secrets**
   - After deployment, click gear icon (Settings)
   - Go to "Secrets"
   - Add your secrets in TOML format:
   ```toml
   OPENAI_API_KEY = "sk-your-openai-key-here"
   ```
   - Save (app will reload automatically)

4. **Verify Deployment**
   - App should load at: `https://kenya-shif-XXXXX.streamlit.app`
   - Check for errors in logs
   - Test core functionality

## Files Included

- `streamlit_comprehensive_analyzer.py` - Main Streamlit app
- `integrated_comprehensive_analyzer.py` - Analysis engine
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit configuration
- `.streamlit/secrets.toml.example` - Secrets template
- `vercel.json` - Vercel deployment config
- `package.json` - Project metadata
- `deploy.sh` - Automated deployment script
- `DEPLOYMENT.md` - This file

## Project Structure
```
.
├── streamlit_comprehensive_analyzer.py    # Main app (entry point)
├── integrated_comprehensive_analyzer.py   # Analysis engine
├── requirements.txt                       # Dependencies
├── .streamlit/
│   ├── config.toml                       # Streamlit settings
│   └── secrets.toml.example              # Secrets template
├── vercel.json                           # Vercel config
├── package.json                          # Project metadata
├── deploy.sh                             # Deploy script
├── TARIFFS*.pdf                          # Policy document
└── outputs_run_*/                        # Analysis results (cached)
```

## Key Features Deployed

- ✅ Complete healthcare policy analysis
- ✅ AI-powered contradiction detection (6 found)
- ✅ Coverage gap identification (27 found)
- ✅ Interactive Streamlit dashboard
- ✅ Real-time PDF analysis
- ✅ Results download capability
- ✅ Data visualization with Plotly
- ✅ Metrics logging for audit trail
- ✅ Production-ready code

## Configuration Details

### Streamlit Config (.streamlit/config.toml)
- Port: 8501
- Logger level: info
- Max upload size: 200MB
- XSRF protection enabled
- Toolbar mode: viewer

### Environment Variables
- `OPENAI_API_KEY` - Required for AI analysis (set via Streamlit Secrets)
- `PDF_PATH` - Optional, defaults to policy PDF
- `CACHE_ENABLED` - Optional, defaults to true
- `CACHE_TTL_HOURS` - Optional, defaults to 24

## Troubleshooting

### App Won't Load
1. Check Streamlit logs for errors
2. Verify all imports in requirements.txt are installed
3. Test locally: `streamlit run streamlit_comprehensive_analyzer.py`

### API Key Not Working
1. Ensure OPENAI_API_KEY is in Streamlit Secrets (not .env)
2. Verify key format: starts with "sk-"
3. Check OpenAI account has available credits

### Slow Performance
1. First load may take 30-60 seconds
2. Results are cached after first load
3. Check available server resources

### Missing Data Files
1. Ensure PDF file is in root directory
2. Output directories should have CSVs
3. Check file permissions

## Deployment Checklist

- [ ] All files committed to GitHub
- [ ] Latest commit pushed
- [ ] Streamlit account created
- [ ] Repository connected to Streamlit
- [ ] OPENAI_API_KEY added to Secrets
- [ ] App deployed successfully
- [ ] URL generated and tested
- [ ] Link sent to assignment giver

## Support & Documentation

- GitHub: https://github.com/pranaysuyash/kenya-shif
- Streamlit Docs: https://docs.streamlit.io/
- OpenAI Docs: https://platform.openai.com/docs/
- Issues: Check GitHub repository for known issues

## Version Info

- App Version: 5.0
- Python: 3.9+
- Streamlit: 1.28.0+
- OpenAI: 1.3.0+
- Last Updated: October 17, 2025
- Deployment Status: Production Ready

