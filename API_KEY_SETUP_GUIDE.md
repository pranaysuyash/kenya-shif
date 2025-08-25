# 🔑 API Key Setup Guide - Critical Configuration

**IMPORTANT**: Quota issues are due to incorrect API key handling. Follow this guide exactly.

---

## 🚨 **CRITICAL API KEY PROCEDURE**

### **ALWAYS Follow This Sequence:**

```bash
# 1. UNSET any existing environment variable
unset OPENAI_API_KEY

# 2. USE the correct key from .env file
source .env

# 3. VERIFY the key is loaded correctly
echo "API key loaded: ${OPENAI_API_KEY:0:15}..."

# 4. THEN run the analysis
python deploy_generalized.py
```

---

## 🔧 **Troubleshooting API Quota Issues**

### **Problem**: Getting 429 quota exceeded errors
### **Solution**: Environment variable conflict

**Check current environment:**
```bash
echo $OPENAI_API_KEY
```

**If this shows an old/different key:**
1. **Unset the environment variable**
2. **Source the .env file**
3. **Verify the correct key is loaded**
4. **Run the analysis**

---

## 📝 **Correct .env File Format**

Your `.env` file should contain:
```
OPENAI_API_KEY=OPENAI_API_KEY_REMOVED
```

---

## 🎯 **Model Configuration**

The system uses:
- **Primary Model**: `gpt-5-mini`
- **Fallback Model**: `gpt-4.1-mini`

This configuration is built into the system and will automatically try the primary model first, then fall back if needed.

---

## ✅ **Verification Steps**

Before running analysis, verify:

```bash
# 1. Check API key is from .env
echo "Current key: ${OPENAI_API_KEY:0:15}..."

# 2. Test API connectivity
python -c "
import openai
from dotenv import load_dotenv
import os

load_dotenv()
client = openai.OpenAI()
try:
    response = client.chat.completions.create(
        model='gpt-5-mini',
        messages=[{'role': 'user', 'content': 'test'}],
        max_tokens=5
    )
    print('✅ API working with gpt-5-mini')
except Exception as e:
    print(f'Primary model failed: {e}')
    try:
        response = client.chat.completions.create(
            model='gpt-4.1-mini',
            messages=[{'role': 'user', 'content': 'test'}],
            max_tokens=5
        )
        print('✅ Fallback gpt-4.1-mini working')
    except Exception as e2:
        print(f'Both models failed: {e2}')
"
```

---

## 🚀 **Complete Setup Procedure**

For first-time setup or troubleshooting:

```bash
# Complete setup sequence
cd /path/to/project
unset OPENAI_API_KEY
source .venv/bin/activate
source .env
echo "Setup complete. API key: ${OPENAI_API_KEY:0:15}..."

# Run analysis
python deploy_generalized.py

# Or run Streamlit
streamlit run streamlit_generalized_medical.py
```

---

## 📋 **Documentation Updates Required**

All documentation should specify:

1. **UNSET environment variables first**
2. **SOURCE .env file for correct key**
3. **VERIFY key before running**
4. **Models are gpt-5-mini/gpt-4.1-mini**

This prevents quota issues caused by using wrong/old API keys from shell environment variables.

---

**🔑 Following this procedure eliminates quota issues and ensures the system uses your correct API key with the right model configuration.**