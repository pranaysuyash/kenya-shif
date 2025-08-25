# SHIF Analyzer - Replit Deployment Guide

## 🚀 Quick Deployment to Replit

### **1. Setup New Repl**

1. Go to [replit.com](https://replit.com) and create new Python Repl
2. Name it: `shif-analyzer-ai-enhanced`
3. Set template: Python (with web server capability)

### **2. Upload Files**

Copy these files to your Repl:
- `streamlit_app.py` (main application)
- `shif_analyzer_enhanced.py` (core engine)
- `requirements.txt` (dependencies)
- `SHIF-Benefits-Package.pdf` (sample document)

### **3. Configure Environment**

Create `.replit` file:
```toml
modules = ["python-3.11"]
run = "streamlit run streamlit_app.py --server.port 8080 --server.address 0.0.0.0"

[nix]
channel = "stable-22_11"

[deployment]
run = ["sh", "-c", "streamlit run streamlit_app.py --server.port 8080 --server.address 0.0.0.0"]
```

### **4. Environment Variables**

In Replit Secrets tab, add:
- `OPENAI_API_KEY` = `your_openai_api_key_here`

### **5. Install Dependencies**

Run in Replit console:
```bash
pip install -r requirements.txt
```

### **6. Launch Application**

Click the "Run" button or execute:
```bash
streamlit run streamlit_app.py --server.port 8080 --server.address 0.0.0.0
```

## 🔗 **Shareable Link**

Once deployed, Replit will provide a shareable URL like:
`https://shif-analyzer-ai-enhanced.your-username.repl.co`

## ⚙️ **Configuration Options**

### **Streamlit Configuration**

Create `.streamlit/config.toml`:
```toml
[server]
port = 8080
address = "0.0.0.0"
enableXsrfProtection = false
enableCORS = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### **Performance Optimization**

Add to `streamlit_app.py`:
```python
# Optimize for Replit deployment
st.set_page_config(
    page_title="SHIF Analyzer - AI Enhanced",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Port Binding Error**
   ```bash
   # Solution: Use correct port in run command
   streamlit run streamlit_app.py --server.port 8080 --server.address 0.0.0.0
   ```

2. **OpenAI API Error**
   ```bash
   # Solution: Check environment variable
   echo $OPENAI_API_KEY
   ```

3. **PDF Upload Issues**
   ```bash
   # Solution: Ensure file upload widget is configured
   uploaded_file = st.file_uploader("Upload PDF", type="pdf")
   ```

### **Memory Optimization**

Add to your app:
```python
import streamlit as st

# Clear cache periodically
if st.button("Clear Cache"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()
```

## 🔒 **Security Best Practices**

1. **API Key Security**
   - Store OpenAI API key in Replit Secrets
   - Never commit API keys to code
   - Use environment variable access

2. **File Upload Safety**
   - Limit file size (50MB max)
   - Validate file types (PDF only)
   - Clear temporary files after processing

3. **Error Handling**
   - Graceful degradation if AI fails
   - User-friendly error messages
   - Fallback to baseline analysis

## 🚀 **Production Checklist**

- [ ] Files uploaded and organized
- [ ] Requirements installed successfully
- [ ] OpenAI API key configured in secrets
- [ ] Application starts without errors
- [ ] PDF upload and processing works
- [ ] AI enhancement functional
- [ ] Results export working
- [ ] Shareable link accessible
- [ ] Performance acceptable (30-60 seconds)
- [ ] Error handling tested

## 📊 **Demo Script**

### **Live Demo Flow**

1. **Welcome & Overview** (2 minutes)
   - Show landing page
   - Explain AI-enhanced capabilities
   - Highlight business value

2. **Pre-loaded Analysis** (5 minutes)
   - Show existing SHIF analysis results
   - Navigate through contradictions
   - Demonstrate evidence tracking

3. **Live PDF Processing** (10 minutes)
   - Upload new PDF document
   - Watch real-time AI analysis
   - Show extraction progress

4. **Results Exploration** (10 minutes)
   - Browse extracted rules
   - Examine flagged contradictions
   - Review evidence snippets

5. **Export Capabilities** (3 minutes)
   - Download Excel reports
   - Show CSV data format
   - Demonstrate metadata preservation

### **Key Demo Points**

- **Speed**: 30-second analysis vs 5-day manual review
- **Accuracy**: AI-enhanced extraction with medical terminology
- **Evidence**: Full traceability with page references
- **Usability**: Non-technical user interface
- **Scalability**: Ready for additional document types

## 🔗 **Resource Links**

- [Replit Documentation](https://docs.replit.com/)
- [Streamlit Deployment Guide](https://docs.streamlit.io/knowledge-base/tutorials/deploy)
- [OpenAI API Documentation](https://platform.openai.com/docs)

---

**Ready for Immediate Deployment**: This configuration ensures smooth deployment and optimal performance on Replit platform.
