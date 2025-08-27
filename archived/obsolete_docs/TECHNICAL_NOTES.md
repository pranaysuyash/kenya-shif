# Technical Notes - SHIF Benefits Analyzer

## Architecture Overview

### Design Philosophy
Evidence-based analysis with validation-ready outputs. Every finding must be traceable to source.

### Core Components
1. **PDF Parser**: Extract text and tables with page tracking
2. **Rule Extractor**: Identify benefits with regex + NLP
3. **Contradiction Detector**: 4-category classification system
4. **Gap Analyzer**: Condition-based coverage assessment
5. **Evidence Tracker**: Page numbers + text snippets
6. **Export Engine**: Excel with validation fields

## Detection Algorithms

### 1. Tariff Contradiction Detection
```python
# Pattern: Same service, different KES values
def detect_tariff_conflicts(service_group):
    tariffs = extract_unique_tariffs(service_group)
    if len(tariffs) > 1:
        variance = calculate_variance(tariffs)
        return {
            'type': 'TARIFF',
            'severity': 'HIGH' if variance > 50% else 'MEDIUM',
            'evidence': extract_page_evidence(tariffs)
        }
```

### 2. Limit Contradiction Detection
```python
# Pattern: Same service, different quantities
def detect_limit_conflicts(service_group):
    limits = extract_all_limits(service_group)
    if has_different_values(limits):
        return {
            'type': 'LIMIT',
            'severity': 'HIGH' if 'dialysis' in service else 'MEDIUM',
            'evidence': extract_limit_evidence(limits)
        }
```

### 3. Coverage Contradiction Detection
```python
# Pattern: Service both included and excluded
def detect_coverage_conflicts(service_group):
    has_inclusion = any(rule.exclusion is None)
    has_exclusion = any(rule.exclusion is not None)
    if has_inclusion and has_exclusion:
        return {
            'type': 'COVERAGE',
            'severity': 'HIGH',
            'evidence': extract_inclusion_exclusion_evidence()
        }
```

### 4. Facility Contradiction Detection
```python
# Pattern: Different coverage by facility level
def detect_facility_conflicts(service_group):
    facility_levels = extract_unique_levels(service_group)
    if len(facility_levels) > 1:
        return {
            'type': 'FACILITY',
            'severity': 'MEDIUM',
            'evidence': extract_facility_evidence(levels)
        }
```

## Pattern Recognition

### Kenya-Specific Patterns

#### Money Extraction
```regex
# Kenyan Shilling formats
KES\s*[\d,]+(?:\.\d+)?
Ksh\.?\s*[\d,]+
[\d,]+\s*/\-
```

#### Facility Levels
```regex
# Kenya's 6-level system
Level\s*[1-6]
Tier\s*[1-6]
L[1-6]\s*facility
```

#### Service Limits
```regex
# Common limit patterns
(\d+)\s*sessions?\s*per\s*week
(\d+)\s*times?\s*per\s*month
up\s*to\s*(\d+)\s*days
maximum\s*(\d+)\s*visits
```

#### Exclusion Patterns
```regex
# Detecting "not covered at Level X"
not\s+covered\s+at\s+Level\s*([1-6])
excluded\s+(?:at|in)\s+Level\s*([1-6])
unavailable\s+at\s+Level\s*([1-6])
except\s+Level\s*([1-6])
```

## Fuzzy Matching Algorithm

### Service Name Matching
```python
from difflib import SequenceMatcher

def similar_services(service1, service2, threshold=0.8):
    """
    Match similar services using 80% threshold
    Handles variations like:
    - "Hemodialysis" vs "Haemodialysis"
    - "CT Scan" vs "CT scanning"
    - "C-Section" vs "Caesarean Section"
    """
    # Normalize strings
    s1 = normalize(service1)  # lowercase, remove punctuation
    s2 = normalize(service2)
    
    # Calculate similarity
    ratio = SequenceMatcher(None, s1, s2).ratio()
    
    # Apply domain-specific boosting
    if has_medical_synonym(s1, s2):
        ratio += 0.1
    
    return ratio >= threshold
```

## Evidence Chain Implementation

### Page-Level Tracking
```python
class EvidenceTracker:
    def __init__(self):
        self.evidence_chain = []
    
    def add_evidence(self, page_num, text, confidence):
        snippet = self.create_snippet(text, max_length=150)
        self.evidence_chain.append({
            'source_page': page_num,
            'evidence_snippet': snippet,
            'confidence': confidence,
            'timestamp': datetime.now()
        })
    
    def create_snippet(self, text, max_length):
        """Create evidence snippet with context"""
        cleaned = re.sub(r'\s+', ' ', text).strip()
        if len(cleaned) > max_length:
            # Try to break at word boundary
            return cleaned[:max_length-3] + "..."
        return cleaned
```

## Confidence Scoring

### Three-Tier System
```python
CONFIDENCE_LEVELS = {
    'HIGH': {
        'threshold': 0.9,
        'criteria': [
            'Exact keyword match',
            'Clear numerical values',
            'Page evidence present',
            'No ambiguous terms'
        ]
    },
    'MEDIUM': {
        'threshold': 0.75,
        'criteria': [
            'Fuzzy match > 80%',
            'Partial evidence',
            'Some context missing',
            'Minor ambiguity'
        ]
    },
    'LOW': {
        'threshold': 0.5,
        'criteria': [
            'Weak fuzzy match',
            'Limited evidence',
            'Significant ambiguity',
            'Requires validation'
        ]
    }
}
```

## Performance Optimization

### PDF Processing
- **Chunk Processing**: Process PDF in 10-page chunks for memory efficiency
- **Parallel Extraction**: Use multiprocessing for large documents
- **Cache Results**: Store parsed rules to avoid re-processing

### Matching Optimization
- **Index Services**: Create inverted index for fast lookup
- **Batch Comparisons**: Group similar services before detailed analysis
- **Early Termination**: Stop processing when confidence threshold met

## Error Handling

### Robust Extraction
```python
def safe_extract(pdf_path):
    try:
        # Primary: pdfplumber
        return extract_with_pdfplumber(pdf_path)
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}")
        try:
            # Fallback: PyPDF2
            return extract_with_pypdf2(pdf_path)
        except Exception as e2:
            logger.error(f"All extraction methods failed: {e2}")
            return pd.DataFrame()  # Empty but valid
```

### Validation Framework
```python
def validate_contradiction(contradiction):
    """Ensure finding meets minimum evidence standards"""
    required_fields = ['source_page', 'evidence_snippet', 'confidence']
    
    # Check required fields
    for field in required_fields:
        if not contradiction.get(field):
            contradiction['validation_status'] = 'incomplete'
            return False
    
    # Verify evidence quality
    if len(contradiction['evidence_snippet']) < 20:
        contradiction['validation_status'] = 'insufficient_evidence'
        return False
    
    contradiction['validation_status'] = 'ready_for_review'
    return True
```

## Data Structures

### Rule Schema
```python
RULE_SCHEMA = {
    'service': str,           # Service name (max 200 chars)
    'category': str,          # SERVICE_CATEGORIES enum
    'tariff': float,          # KES amount
    'facility_level': str,    # Level 1-6 or range
    'exclusion': str,         # Exclusion text if any
    'limits': dict,           # {limit_type: value}
    'source_page': int,       # PDF page number
    'evidence_snippet': str,  # Text excerpt (max 150)
    'raw_text': str,         # Full text (max 500)
    'source_type': str,      # 'text' or 'table_X_row_Y'
    'confidence': str        # HIGH/MEDIUM/LOW
}
```

### Contradiction Schema
```python
CONTRADICTION_SCHEMA = {
    'service': str,
    'contradiction_type': str,     # TARIFF/LIMIT/COVERAGE/FACILITY
    'type_description': str,       # Human-readable description
    'details': str,                # Specific conflict details
    'variance': str,               # Percentage or range
    'severity': str,               # HIGH/MEDIUM/LOW
    'source_page': str,            # Page references
    'evidence_snippet': str,       # Combined evidence
    'confidence': str,             # Confidence level
    'validation_status': str       # flagged/pending_review/confirmed
}
```

## Testing Strategy

### Unit Tests
```python
def test_dialysis_contradiction_detection():
    """Ensure dialysis limit conflicts are detected"""
    rules = [
        {'service': 'Hemodialysis', 'limits': {'per_week': 2}, 'page': 23},
        {'service': 'Hemodialysis', 'limits': {'per_week': 3}, 'page': 41}
    ]
    contradictions = detect_contradictions(rules)
    assert len(contradictions) > 0
    assert contradictions[0]['type'] == 'LIMIT'
    assert '2' in contradictions[0]['details']
    assert '3' in contradictions[0]['details']
```

### Integration Tests
- Full PDF processing with known contradictions
- Evidence chain validation
- Excel export verification

### Regression Tests
- Maintain test suite of known contradictions
- Verify each update doesn't break existing detection
- Performance benchmarks (30-second target)

## Deployment Considerations

### Local Deployment
```bash
# Simple local run
python shif_analyzer.py

# With monitoring
python shif_analyzer.py --verbose --log-file analysis.log
```

### Streamlit Cloud
```yaml
# .streamlit/config.toml
[server]
maxUploadSize = 100
enableCORS = false

[theme]
primaryColor = "#4B8BBE"
```

### Docker Container
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "shif_analyzer.py"]
```

## Future Enhancements

### Phase 1: Enhanced Parsing
- **Camelot Integration**: Better table extraction
- **Tabula Support**: Alternative table parser
- **OCR Pipeline**: Handle scanned documents

### Phase 2: Intelligence Layer
- **ML Classification**: Train on validated contradictions
- **NER Models**: Better service name extraction
- **Semantic Search**: Context-aware matching

### Phase 3: Platform Features
- **API Development**: RESTful endpoints
- **Real-time Monitoring**: Watch for policy updates
- **Collaborative Validation**: Multi-user review workflow

## Security Notes

### Data Protection
- No PII extraction or storage
- Local processing only (no cloud uploads)
- Temporary files auto-deleted
- No credential storage

### Access Control (Future)
```python
ROLES = {
    'viewer': ['read'],
    'analyst': ['read', 'analyze', 'export'],
    'admin': ['read', 'analyze', 'export', 'validate', 'configure']
}
```

## Performance Metrics

### Current Performance
- **PDF Processing**: ~10 seconds for 54 pages
- **Contradiction Detection**: ~15 seconds
- **Gap Analysis**: ~5 seconds
- **Total Time**: ~30 seconds

### Optimization Targets
- **Large PDFs**: Under 1 minute for 200+ pages
- **Memory Usage**: Under 500MB RAM
- **CPU Usage**: Single core sufficient

## Known Limitations

### Current Version
1. **Table Parsing**: Basic extraction, complex tables may fail
2. **Language**: English only, no Swahili support
3. **OCR**: No support for scanned documents
4. **Validation**: Manual review still required

### Mitigation Strategies
- Document limitations clearly
- Provide confidence scores
- Include evidence for validation
- Plan enhancement roadmap

---

*Technical Notes v1.0 - Evidence-Based Implementation*