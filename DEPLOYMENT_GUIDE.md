# SHIF Healthcare Policy Analyzer - Deployment Guide

## Overview

This app now supports **local development, cloud deployment (Replit, Vercel), and historical output management**.

### Key Features by Platform

| Feature | Local | Replit | Vercel | Streamlit Cloud |
|---------|-------|--------|--------|-----------------|
| **App Functions** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **PDF Extraction** | ✅ Deterministic | ✅ Deterministic | ✅ Deterministic | ✅ Deterministic |
| **AI Analysis** | ✅ Deterministic | ✅ Deterministic | ✅ Deterministic | ✅ Deterministic |
| **Download Results** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Local File Storage** | ✅ Persistent | ⚠️ Ephemeral* | ❌ No | ⚠️ Session-only |
| **Historical Browsing** | ✅ Yes | ⚠️ Limited* | ❌ No | ⚠️ Session-only |

*Ephemeral = Deleted after session idle or browser close

---

## 1. LOCAL DEPLOYMENT (Development)

### Setup

```bash
# Clone/enter repository
cd /Users/pranay/Projects/adhoc_projects/drrishi/final_submission

# Activate virtual environment
source .venv/bin/activate

# Run Streamlit app
streamlit run streamlit_comprehensive_analyzer.py
```

### Usage

1. **Upload PDF** → Tab 1 or 2
2. **Run Analysis** → See extracted data + AI insights
3. **View Analytics** → Tab 5 with 3 sub-tabs:
   - **📊 Analytics**: Charts and metrics
   - **📥 Downloads**: Export individual CSVs or complete ZIP
   - **📂 Historical**: Browse previous runs from `outputs/` directory

### Output Structure

```
outputs/
├── run_20251017_120000/
│   ├── policy_services.csv
│   ├── contradictions.csv
│   ├── gaps.csv
│   └── metadata.json
├── run_20251017_121500/
│   ├── policy_services.csv
│   ├── contradictions.csv
│   └── gaps.csv
```

### Key Features

✅ **Persistent Storage**: Outputs stay in `outputs/` folder indefinitely
✅ **History Browsing**: See all past runs with summaries
✅ **Path Input**: Load any directory as historical analysis
✅ **Full Determinism**: Same PDF = same output (temperature=0)

---

## 2. REPLIT DEPLOYMENT

### Setup

```bash
# In Replit terminal
git clone https://github.com/pranaysuyash/kenya-shif.git
cd final_submission

# Install dependencies
pip install -r requirements.txt

# Create .env with API key
echo "OPENAI_API_KEY=sk-..." > .env

# Set deployment environment
export DEPLOYMENT_ENV=replit

# Run Streamlit
streamlit run streamlit_comprehensive_analyzer.py
```

### Configuration

Create `.replit` file:

```toml
run = "export DEPLOYMENT_ENV=replit && streamlit run streamlit_comprehensive_analyzer.py --server.port=3000"
```

### Usage Workflow

**Local Runs ONLY** (files deleted after ~1 hour idle):

```
1. Upload PDF
2. Run Analysis
3. **IMMEDIATELY Download** ← Important!
   - Individual CSVs
   - Complete ZIP package
4. Keep downloads on your machine
5. For next session, upload the ZIP to restore
```

### Important Notes

⚠️ **Storage is Ephemeral**:
- Files deleted after ~1 hour of inactivity
- Browser close = session ends
- **Always download results before leaving**

⚠️ **To Use Historical Features**:
- Upload previously saved output directories
- Use "Load Custom Path" feature
- Or re-upload ZIP from previous session

### Recommended Workflow

```python
# Local: Save everything
results = analyzer.run(pdf)
om = OutputManager()
om.create_run_directory()
om.save_dataframe(results_df, 'results.csv')

# Replit: Download immediately
# Use st.download_button() at end of analysis
st.download_button(
    label="📥 Download Results ZIP",
    data=zip_data,
    file_name="analysis.zip"
)

# Next session: Upload previous outputs
uploaded_zip = st.file_uploader("Upload previous outputs.zip")
if uploaded_zip:
    # Extract and load
    hal.load_analysis(extract_path)
```

---

## 3. VERCEL DEPLOYMENT (Production)

### Setup

```bash
# Clone repo
git clone https://github.com/pranaysuyash/kenya-shif.git
cd final_submission

# Create vercel.json
cat > vercel.json << 'EOF'
{
  "buildCommand": "pip install -r requirements.txt",
  "env": {
    "DEPLOYMENT_ENV": "vercel",
    "OPENAI_API_KEY": "@OPENAI_API_KEY"
  }
}
EOF

# Deploy to Vercel
vercel --env OPENAI_API_KEY=sk-...
```

### Environment Variables

Set in Vercel Dashboard:

```
DEPLOYMENT_ENV = vercel
OPENAI_API_KEY = sk-proj-...
```

### Usage Workflow

**No Persistent Storage**:

```
1. Upload PDF
2. Run Analysis
3. Download Results ← Only way to save
   - Individual CSVs
   - Complete ZIP
   - JSON exports
4. Cannot access files next session
```

### Important Limitations

❌ **NO Local File Storage**:
- Serverless = no persistent filesystem
- Each session is fresh
- Cannot browse "outputs/" folder

✅ **Download-Only Model**:
- Generate all files in-memory
- User downloads to their machine
- For next session: upload ZIP or re-run

### Best Practices

```python
# Always provide download buttons
st.download_button(
    "📥 Export CSV",
    data=csv_bytes,
    file_name="results.csv"
)

# For historical data, users upload it
uploaded_file = st.file_uploader("📂 Load previous outputs.zip")
if uploaded_file:
    extract_and_display(uploaded_file)
```

---

## 4. STREAMLIT CLOUD DEPLOYMENT

### Setup

```bash
# Push to GitHub
git push origin main

# Go to https://share.streamlit.io
# Connect your GitHub repo
# Set Secrets:
OPENAI_API_KEY = sk-proj-...
DEPLOYMENT_ENV = streamlit_cloud
```

### Features

✅ **Per-Session Storage**: `/tmp` directory cleaned after session
⚠️ **Limited History**: Can see runs from current session only
✅ **Download Support**: Full download functionality

### Usage

```
1. Run analysis
2. Download results (stored in /tmp, deleted after session)
3. For next visit: upload previous ZIP to load history
```

---

## 5. KEY IMPLEMENTATION DETAILS

### Deterministic AI (All Platforms)

```python
# All API calls use temperature=0 and seed=42
resp = self.client.chat.completions.create(
    model="gpt-4-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0,  # ← Deterministic
    seed=42         # ← Reproducible
)
```

**Result**: Same PDF + same prompts = **identical output every time**

### Output Manager

```python
from output_manager import OutputManager, DownloadManager

# Automatically detects platform
om = OutputManager()
print(om.is_cloud)      # False on local, True on cloud
print(om.is_ephemeral)  # True on Replit/Vercel

# Works on all platforms
om.create_run_directory()
om.save_dataframe(df, 'results.csv')
om.get_historical_runs()
```

### Download Manager

```python
from output_manager import DownloadManager

dm = DownloadManager()

# Individual files
csv_bytes = dm.dataframe_to_bytes(df)
json_bytes = dm.dict_to_json_bytes(data)

# Complete package
files = {
    'policy_services.csv': policy_df,
    'contradictions.csv': contradiction_df,
    'analysis.json': analysis_data,
}
zip_bytes = dm.create_multi_file_zip(files)

st.download_button("📥 Download", data=zip_bytes, file_name="analysis.zip")
```

---

## 6. PLATFORM COMPARISON TABLE

| Aspect | Local | Replit | Vercel | Streamlit |
|--------|-------|--------|--------|-----------|
| **Speed** | Fast | Medium | Fast* | Medium |
| **Storage** | Persistent | Ephemeral (1hr) | None | Session-only |
| **History** | Full browsing | Upload only | Upload only | Upload only |
| **Setup** | 2 mins | 5 mins | 10 mins | 2 mins |
| **Cost** | Free | Free | Free | Free |
| **Best For** | Development | Testing | Production | Demo |

*Vercel: Fast but requires re-running analysis each session

---

## 7. TROUBLESHOOTING

### App won't start
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt

# Clear cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
rm -rf .streamlit/
```

### Download button not working
```python
# Ensure data is bytes
data = dm.dataframe_to_bytes(df)  # ← Correct
# NOT: st.download_button(..., data=df)  ← Wrong
```

### Historical folder not showing
```python
# Check if outputs/ directory exists
ls -la outputs/

# If empty, run analysis and save:
om = OutputManager()
om.create_run_directory()
om.save_dataframe(results, 'results.csv')
```

### API key issues
```bash
# Verify .env exists
cat .env | grep OPENAI_API_KEY

# Test API connection
python3 -c "from openai import OpenAI; OpenAI(api_key='sk-...')"
```

---

## 8. DEPLOYMENT CHECKLIST

### Before Deploying

- [ ] `.env` file created with `OPENAI_API_KEY`
- [ ] All dependencies in `requirements.txt`
- [ ] `output_manager.py` in root directory
- [ ] Streamlit version ≥ 1.48
- [ ] Python ≥ 3.8
- [ ] PDF test file available

### Local Deployment
```bash
✅ streamlit run streamlit_comprehensive_analyzer.py
✅ Upload PDF
✅ Run all 5 tasks
✅ Check Downloads tab
✅ Check Historical tab
```

### Cloud Deployment (Replit)
```bash
✅ Set DEPLOYMENT_ENV=replit
✅ Public URL accessible
✅ Download button works
✅ No errors in logs
```

### Production (Vercel)
```bash
✅ Environment variables set
✅ GitHub repo connected
✅ Build succeeds
✅ API responses <5 seconds
```

---

## 9. QUICK START BY PLATFORM

### Local (Fastest)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "OPENAI_API_KEY=sk-..." > .env
streamlit run streamlit_comprehensive_analyzer.py
```

### Replit (Web Browser)
```bash
1. Create Replit account
2. Click "Import from GitHub"
3. Enter: pranaysuyash/kenya-shif
4. Set environment: OPENAI_API_KEY=sk-...
5. Press Run
```

### Vercel (Production)
```bash
1. Push code to GitHub
2. Create Vercel account
3. Connect GitHub repo
4. Add environment variables
5. Deploy (automatic)
```

---

## Questions?

Check:
- `integrated_comprehensive_analyzer.py` - Core logic
- `streamlit_comprehensive_analyzer.py` - UI components
- `output_manager.py` - File handling
- `.env` - Configuration

All components deterministic and platform-agnostic! 🎉
