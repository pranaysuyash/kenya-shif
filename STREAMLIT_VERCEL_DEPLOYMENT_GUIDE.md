# Deployment Guide: Streamlit + Vercel

**Date**: October 17, 2025  
**Status**: Ready for deployment  
**Main App**: `streamlit_comprehensive_analyzer.py`

---

## Part 1: Deploy to Streamlit Community Cloud (RECOMMENDED)

### Step 1: Create Streamlit Account
1. Go to https://streamlit.io/cloud
2. Click "Sign up"
3. Sign in with GitHub account (required)
4. Authorize Streamlit to access your GitHub

### Step 2: Connect Your Repository
1. In Streamlit Cloud dashboard, click "New app"
2. Select deployment method: **GitHub** (recommended)
3. Repository: `pranaysuyash/kenya-shif`
4. Branch: `main`
5. Main file path: `streamlit_comprehensive_analyzer.py`

### Step 3: Configure Secrets
1. Click on your app → Settings gear (top right)
2. Go to "Secrets"
3. Add your OpenAI API key:
```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```
4. Save

### Step 4: Deploy
1. Click "Deploy"
2. Streamlit will:
   - Pull your repo
   - Install requirements.txt
   - Start the app
   - Generate a public URL

**Result**: Your app will be available at:
```
https://kenya-shif-<random>.streamlit.app
```

---

## Part 2: Create API Backend for Vercel

Since Streamlit is not directly Vercel-compatible, create a simple Next.js or Python API wrapper:

### Option A: Using Python + FastAPI (Recommended for your setup)

#### Step 1: Create API Directory Structure
```bash
mkdir -p api
cd api
touch requirements.txt
touch index.py
```

#### Step 2: Create `api/index.py` (Main endpoint)
```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    pdf_path: str = None
    use_fresh: bool = False

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Kenya SHIF Healthcare Policy Analyzer",
        "version": "5.0",
        "endpoints": {
            "health": "/health",
            "analyze": "/api/analyze",
            "results": "/api/results"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "analyzer"}

@app.post("/api/analyze")
async def analyze(request: AnalysisRequest):
    try:
        analyzer = IntegratedComprehensiveMedicalAnalyzer()
        
        # Use existing output if available
        if not request.use_fresh:
            output_dir = analyzer.find_latest_outputs()
            if output_dir:
                # Load existing results
                contradictions = pd.read_csv(f"{output_dir}/ai_contradictions.csv")
                gaps = pd.read_csv(f"{output_dir}/comprehensive_gaps_analysis.csv")
                
                return {
                    "status": "success",
                    "source": "existing",
                    "contradictions_count": len(contradictions),
                    "gaps_count": len(gaps),
                    "contradictions": contradictions.to_dict(orient="records")[:6],
                    "gaps": gaps.to_dict(orient="records")[:10]
                }
        
        # Run fresh analysis if requested
        pdf_path = request.pdf_path or "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
        results = analyzer.analyze_complete_document(pdf_path)
        
        return {
            "status": "success",
            "source": "fresh",
            "contradictions_count": len(results.get("contradictions", [])),
            "gaps_count": len(results.get("gaps", [])),
            "data": results
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/results")
async def get_results():
    """Get latest analysis results"""
    try:
        analyzer = IntegratedComprehensiveMedicalAnalyzer()
        output_dir = analyzer.find_latest_outputs()
        
        if not output_dir:
            return {"status": "no_data", "message": "No analysis results found"}
        
        contradictions = pd.read_csv(f"{output_dir}/ai_contradictions.csv")
        gaps = pd.read_csv(f"{output_dir}/comprehensive_gaps_analysis.csv")
        
        return {
            "status": "success",
            "contradictions": {
                "count": len(contradictions),
                "data": contradictions.to_dict(orient="records")
            },
            "gaps": {
                "count": len(gaps),
                "data": gaps.to_dict(orient="records")
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# For Vercel
from fastapi.responses import FileResponse

@app.get("/api/download-results")
async def download_results():
    """Download analysis results as ZIP"""
    try:
        analyzer = IntegratedComprehensiveMedicalAnalyzer()
        output_dir = analyzer.find_latest_outputs()
        
        if not output_dir:
            raise HTTPException(status_code=404, detail="No results available")
        
        # Create ZIP file
        import zipfile
        from io import BytesIO
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in os.listdir(output_dir):
                if file.endswith('.csv'):
                    zf.write(f"{output_dir}/{file}", arcname=file)
        
        zip_buffer.seek(0)
        return FileResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=shif-analysis.zip"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
```

#### Step 3: Create `api/requirements.txt`
```
fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
pandas==2.1.0
openai==1.3.0
pydantic==2.5.0
```

#### Step 4: Create Vercel Config (`vercel.json`)
```json
{
  "buildCommand": "pip install -r api/requirements.txt",
  "outputDirectory": ".",
  "public": false,
  "functions": {
    "api/index.py": {
      "memory": 3008,
      "maxDuration": 300
    }
  }
}
```

---

## Part 2B: Using Next.js + Vercel (Alternative - Easier)

If you prefer a simple HTML dashboard, use Next.js:

### Step 1: Create Next.js App
```bash
npx create-next-app@latest shif-dashboard --typescript --tailwind
cd shif-dashboard
```

### Step 2: Create API Route (`pages/api/analyze.ts`)
```typescript
import type { NextApiRequest, NextApiResponse } from 'next';

type ResponseData = {
  status: string;
  data?: any;
  error?: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ status: 'error', error: 'Method not allowed' });
  }

  try {
    // Call Streamlit backend or load pre-computed data
    const streamlitUrl = 'https://kenya-shif-<random>.streamlit.app';
    
    return res.status(200).json({
      status: 'success',
      data: {
        contradictions: 6,
        gaps: 27,
        streamlit_link: streamlitUrl
      }
    });
  } catch (error) {
    return res.status(500).json({
      status: 'error',
      error: 'Analysis failed'
    });
  }
}
```

### Step 3: Create Dashboard Page (`pages/dashboard.tsx`)
```typescript
'use client';
import { useEffect, useState } from 'react';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/analyze')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Kenya SHIF Analysis</h1>
      <div className="grid grid-cols-2 gap-4">
        <div className="border p-4">
          <h2 className="text-2xl font-bold">6</h2>
          <p>Contradictions Found</p>
        </div>
        <div className="border p-4">
          <h2 className="text-2xl font-bold">27</h2>
          <p>Coverage Gaps Identified</p>
        </div>
      </div>
      <a 
        href="https://kenya-shif-<random>.streamlit.app" 
        className="mt-8 inline-block bg-blue-500 text-white px-6 py-2 rounded"
      >
        Open Full Analysis
      </a>
    </div>
  );
}
```

### Step 4: Deploy to Vercel
```bash
vercel login
vercel deploy
```

---

## Quick Deployment Summary

### Streamlit Cloud (Main App)
1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. New app → Select `streamlit_comprehensive_analyzer.py`
4. Add OPENAI_API_KEY to Secrets
5. Deploy
6. **Get URL**: `https://kenya-shif-<random>.streamlit.app`

### Vercel (Optional Dashboard/Proxy)
1. Create simple Next.js dashboard or FastAPI backend
2. Push to GitHub
3. Connect to Vercel
4. Deploy
5. **Get URL**: `https://shif-dashboard.vercel.app`

---

## What to Provide to Assignment Giver

### Streamlit Link (Primary):
```
https://kenya-shif-XXXXX.streamlit.app
```

### Vercel Link (Dashboard/Proxy):
```
https://shif-dashboard.vercel.app
```

### GitHub Repository:
```
https://github.com/pranaysuyash/kenya-shif
```

### Commit Hash (Latest):
```
a8a5fd4 - docs: Add DEPLOYMENT_READY summary - Production status confirmed
```

---

## Environment Variables Needed

### Streamlit Cloud:
- `OPENAI_API_KEY` - Your OpenAI API key

### Vercel (if using API):
- `OPENAI_API_KEY` - Your OpenAI API key
- `DATABASE_URL` - (optional) if storing results

---

## Troubleshooting

### Streamlit won't deploy
- Check `requirements.txt` is in root
- Verify `streamlit_comprehensive_analyzer.py` exists
- Ensure all imports are available

### API endpoint not working
- Check logs in Vercel dashboard
- Verify environment variables are set
- Test locally: `python -m uvicorn api/index.py --reload`

### Module imports failing
- Add `__init__.py` files to directories
- Update sys.path in scripts
- Check relative imports

---

## Next Steps

1. ✅ Commit deployment files to GitHub
2. ✅ Push all changes
3. ✅ Deploy to Streamlit Cloud
4. ✅ (Optional) Deploy dashboard to Vercel
5. ✅ Test both links
6. ✅ Send URLs to assignment giver

**Estimated time**: 15-30 minutes for Streamlit, 10-20 minutes for Vercel

