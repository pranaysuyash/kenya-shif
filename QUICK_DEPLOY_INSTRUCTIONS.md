# QUICK START: Deploy to Streamlit + Vercel

**Time to Deploy**: ~20 minutes

---

## FASTEST PATH: Streamlit Cloud Only ✅

### 1. Go to Streamlit Cloud
```
https://streamlit.io/cloud
```

### 2. Sign In with GitHub
- Click "Sign up" or "Sign in"
- Choose "Sign in with GitHub"
- Authorize Streamlit

### 3. Deploy Your App
- Click "New app"
- Repository: `pranaysuyash/kenya-shif`
- Branch: `main`
- Main file path: `streamlit_comprehensive_analyzer.py`
- Click "Deploy"

### 4. Add Your API Key
- Wait for app to load
- Click gear icon (top right) → "Secrets"
- Add:
```
OPENAI_API_KEY = "sk-..."
```
- Save and app will reload

### 5. Get Your Link
```
Your app is now live at:
https://kenya-shif-<random>.streamlit.app
```

**Share this URL with assignment giver** ✅

---

## OPTIONAL: Dashboard on Vercel

If you also need a Vercel link:

### Option 1: Create Simple Landing Page

Create file: `index.html`

```html
<!DOCTYPE html>
<html>
<head>
  <title>Kenya SHIF Analysis Dashboard</title>
  <style>
    body { font-family: Arial; max-width: 800px; margin: 50px auto; }
    .card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }
    .stat { font-size: 24px; font-weight: bold; }
  </style>
</head>
<body>
  <h1>Kenya SHIF Healthcare Policy Analysis</h1>
  
  <div class="card">
    <div class="stat">6</div>
    <p>Contradictions Found</p>
  </div>
  
  <div class="card">
    <div class="stat">27</div>
    <p>Coverage Gaps Identified</p>
  </div>
  
  <div class="card">
    <a href="https://kenya-shif-XXXXX.streamlit.app" style="font-size: 18px; color: blue;">
      → Open Full Analysis in Streamlit
    </a>
  </div>
  
  <hr>
  <p>
    <strong>GitHub:</strong> 
    <a href="https://github.com/pranaysuyash/kenya-shif">pranaysuyash/kenya-shif</a>
  </p>
  <p>
    <strong>Latest Commit:</strong> a8a5fd4
  </p>
</body>
</html>
```

### Deploy to Vercel:
```bash
cd /Users/pranay/Projects/adhoc_projects/drrishi/final_submission

# Create vercel.json
cat > vercel.json << 'EOF'
{
  "public": true
}
EOF

# Add and commit
git add index.html vercel.json
git commit -m "Add landing page for Vercel deployment"
git push origin main

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

You'll get a URL like: `https://kenya-shif-123.vercel.app`

---

## What to Send to Assignment Giver

### Primary Submission:
```
Streamlit Link: https://kenya-shif-XXXXX.streamlit.app
GitHub Repo: https://github.com/pranaysuyash/kenya-shif
Latest Commit: a8a5fd4
```

### (Optional) Secondary Link:
```
Vercel Dashboard: https://kenya-shif-123.vercel.app
```

---

## Verify Deployment Works

### Test Streamlit:
1. Visit your Streamlit URL
2. Should see the analytics dashboard
3. Data should load from CSVs
4. Able to download results

### Test Vercel (if deployed):
1. Visit your Vercel URL
2. Should see summary stats
3. Link to Streamlit should work

---

## If Streamlit Deployment Fails

**Common Issues:**

1. **Module not found**: Check `requirements.txt` has all packages
2. **API key error**: Make sure OPENAI_API_KEY is in Secrets (not .env)
3. **Timeout**: App might be large, check if it's running locally first:
   ```bash
   streamlit run streamlit_comprehensive_analyzer.py
   ```

**Fix**:
- Ensure `requirements.txt` exists in root
- Test locally first
- Check Streamlit logs for errors

---

## Timeline

✅ **Now**: 
- Streamlit app ready
- Code committed to GitHub
- Documentation complete

⏱️ **5 min**: Deploy to Streamlit
⏱️ **5 min**: Add OPENAI_API_KEY secret
⏱️ **2 min**: Get Streamlit URL
⏱️ **Optional 5 min**: Deploy to Vercel

---

## Final Checklist

- [ ] Go to https://streamlit.io/cloud
- [ ] Sign in with GitHub (pranaysuyash)
- [ ] Create new app
- [ ] Select `streamlit_comprehensive_analyzer.py`
- [ ] Add OPENAI_API_KEY to Secrets
- [ ] Wait for deployment (2-3 minutes)
- [ ] Copy Streamlit URL
- [ ] Test it works
- [ ] Send URL to assignment giver

---

## Support

If deployment fails:
1. Check Streamlit logs (cloud dashboard)
2. Verify `requirements.txt` in root
3. Test locally: `streamlit run streamlit_comprehensive_analyzer.py`
4. Check all imports work

**Your app is production-ready.** Just need to deploy! 🚀

