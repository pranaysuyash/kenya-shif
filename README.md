# Kenya SHIF Healthcare Policy Analyzer

Advanced PDF analysis tool for Kenya's Social Health Insurance Fund (SHIF) policy documents with AI-powered gap detection and contradiction analysis.

## Features

- **PDF Extraction**: Tabula-based extraction for structured healthcare policy data
- **Dynamic Text Processing**: Advanced de-gluing algorithm for handling broken text
- **AI Analysis**: OpenAI-powered gap detection and policy contradiction analysis  
- **Web Dashboard**: Streamlit interface for interactive analysis
- **Comprehensive Output**: Structured data export in CSV and JSON formats

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up API Key**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run Analysis**
   ```bash
   python integrated_comprehensive_analyzer.py
   ```

4. **Launch Web Dashboard**
   ```bash
   streamlit run streamlit_comprehensive_analyzer.py
   ```

## API Key Setup

Get your OpenAI API key from https://platform.openai.com/api-keys and add it to your `.env` file:

```
OPENAI_API_KEY=OPENAI_API_KEY_REMOVED
```

## File Structure

- `integrated_comprehensive_analyzer.py` - Main analysis engine
- `streamlit_comprehensive_analyzer.py` - Web dashboard
- `manual_exact.py` - Reference extraction implementation
- `config.py` - Environment variable management
- `requirements.txt` - Python dependencies

## Usage

Place your PDF file as `TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf` in the same directory and run the analyzer.

The tool will generate structured outputs including:
- Policy service extractions
- Healthcare contradictions
- Coverage gaps
- AI-powered analysis reports

## Security

- All API keys are loaded from environment variables
- No sensitive data is committed to git
- Use `.env` file for local development (excluded from git)

## Generated Output

The analyzer produces CSV and JSON files with comprehensive healthcare policy analysis, suitable for further processing or dashboard visualization.