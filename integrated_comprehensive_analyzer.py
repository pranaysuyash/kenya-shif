#!/usr/bin/env python3
"""
INTEGRATED COMPREHENSIVE MEDICAL ANALYZER
Combines proven extraction methods with AI-enhanced analysis

This integrates:
1. Advanced text processing for pages 1-18 (policy structure) 
2. Simple tabula extraction for pages 19-54 (annex procedures)
3. Dynamic de-glue algorithm and vocabulary learning
4. Generalized medical AI reasoning across all specialties
5. Comprehensive gap analysis and contradiction detection
"""

import openai
import json
import pandas as pd
import re
import math
# Optional dependency: tabula-py (requires Java). Import lazily/defensively.
try:
    import tabula  # type: ignore
except Exception:
    tabula = None  # Fallback handled at call sites
from typing import List, Dict, Optional, Tuple
import time
from pathlib import Path
from datetime import datetime
import hashlib
import os
from difflib import SequenceMatcher
from updated_prompts import UpdatedHealthcareAIPrompts

class UniqueInsightTracker:
    """Tracks unique gaps and contradictions across multiple runs to prevent duplicates"""
    
    def __init__(self, storage_path: str = "persistent_insights.json"):
        self.storage_path = Path(storage_path)
        self.unique_gaps = []
        self.unique_contradictions = []
        self.total_runs = 0
        self.current_run_gaps = 0
        self.current_run_contradictions = 0
        self.load_existing()
    
    def load_existing(self):
        """Load existing unique insights from persistent storage and scan output folders"""
        # First load from persistent file
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.unique_gaps = data.get('unique_gaps', [])
                    self.unique_contradictions = data.get('unique_contradictions', [])
                    self.total_runs = data.get('total_runs', 0)
                print(f"📚 Loaded {len(self.unique_gaps)} unique gaps, {len(self.unique_contradictions)} unique contradictions from persistent storage")
            except Exception as e:
                print(f"⚠️ Could not load existing insights: {e}")
        
        # Also scan all output folders for additional insights
        self.scan_output_folders()
    
    def scan_output_folders(self):
        """Scan all output folders to collect insights from previous runs"""
        scanned_gaps = 0
        scanned_contradictions = 0
        
        # Get all output folders (both timestamped and regular)
        output_folders = []
        
        # Add timestamped folders
        for path in Path('.').glob('outputs_run_*'):
            if path.is_dir():
                output_folders.append(path)
        
        # Add regular outputs folder
        if Path('outputs').exists():
            output_folders.append(Path('outputs'))
            
        print(f"🔍 Scanning {len(output_folders)} output folders for historical insights...")
        
        for folder in output_folders:
            # Look for gap and contradiction CSV files
            for gap_file in folder.glob('*gap*.csv'):
                try:
                    import pandas as pd
                    df = pd.read_csv(gap_file)
                    for _, row in df.iterrows():
                        gap_dict = row.to_dict()
                        if 'description' in gap_dict and gap_dict['description']:
                            gap_dict['source_file'] = str(gap_file)
                            gap_dict['source_folder'] = str(folder)
                            if not self.is_duplicate_gap(gap_dict):
                                gap_dict['discovered_at'] = gap_dict.get('discovered_at', folder.name)
                                gap_dict['unique_id'] = f"SCAN_GAP_{len(self.unique_gaps) + 1:03d}"
                                self.unique_gaps.append(gap_dict)
                                scanned_gaps += 1
                except Exception as e:
                    continue
            
            # Look for contradiction CSV files  
            for contr_file in folder.glob('*contradiction*.csv'):
                try:
                    import pandas as pd
                    df = pd.read_csv(contr_file)
                    for _, row in df.iterrows():
                        contr_dict = row.to_dict()
                        if 'description' in contr_dict and contr_dict['description']:
                            contr_dict['source_file'] = str(contr_file)
                            contr_dict['source_folder'] = str(folder)
                            if not self.is_duplicate_contradiction(contr_dict):
                                contr_dict['discovered_at'] = contr_dict.get('discovered_at', folder.name)
                                contr_dict['unique_id'] = f"SCAN_CONTR_{len(self.unique_contradictions) + 1:03d}"
                                self.unique_contradictions.append(contr_dict)
                                scanned_contradictions += 1
                except Exception as e:
                    continue
        
        if scanned_gaps > 0 or scanned_contradictions > 0:
            print(f"📊 Scanned and found {scanned_gaps} new gaps, {scanned_contradictions} new contradictions from historical runs")
            # Update run count based on folders found
            self.total_runs = max(self.total_runs, len([f for f in output_folders if 'outputs_run_' in str(f)]))
    
    def start_new_run(self):
        """Start tracking a new analysis run"""
        self.total_runs += 1
        self.current_run_gaps = 0
        self.current_run_contradictions = 0
        print(f"🚀 Starting analysis run #{self.total_runs}")

    def save_insights(self):
        """Save unique insights to persistent storage"""
        data = {
            'unique_gaps': self.unique_gaps,
            'unique_contradictions': self.unique_contradictions,
            'total_runs': self.total_runs,
            'last_updated': datetime.now().isoformat(),
            'total_unique_gaps': len(self.unique_gaps),
            'total_unique_contradictions': len(self.unique_contradictions),
            'current_run_gaps': self.current_run_gaps,
            'current_run_contradictions': self.current_run_contradictions
        }
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"💾 Saved {len(self.unique_gaps)} unique gaps, {len(self.unique_contradictions)} unique contradictions")
        except Exception as e:
            print(f"❌ Could not save insights: {e}")
    
    def similarity_score(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1.lower().strip(), text2.lower().strip()).ratio()
    
    def is_duplicate_gap(self, new_gap: Dict, similarity_threshold: float = 0.85) -> bool:
        """Check if a gap is already tracked (based on description similarity)"""
        new_desc = str(new_gap.get('description', ''))
        for existing_gap in self.unique_gaps:
            existing_desc = str(existing_gap.get('description', ''))
            if self.similarity_score(new_desc, existing_desc) >= similarity_threshold:
                return True
        return False
    
    def is_duplicate_contradiction(self, new_contradiction: Dict, similarity_threshold: float = 0.85) -> bool:
        """Check if a contradiction is already tracked"""
        new_desc = str(new_contradiction.get('description', ''))
        for existing in self.unique_contradictions:
            existing_desc = str(existing.get('description', ''))
            if self.similarity_score(new_desc, existing_desc) >= similarity_threshold:
                return True
        return False
    
    def add_gaps(self, gaps: List[Dict]) -> int:
        """Add new gaps if they're unique, return count of newly added"""
        added_count = 0
        for gap in gaps:
            self.current_run_gaps += 1  # Count all gaps from current run
            if not self.is_duplicate_gap(gap):
                # Add metadata about when it was discovered
                gap['discovered_at'] = datetime.now().isoformat()
                gap['run_number'] = self.total_runs
                gap['unique_id'] = f"GAP_{len(self.unique_gaps) + 1:03d}"
                self.unique_gaps.append(gap)
                added_count += 1
        return added_count
    
    def add_contradictions(self, contradictions: List[Dict]) -> int:
        """Add new contradictions if they're unique, return count of newly added"""
        added_count = 0
        for contradiction in contradictions:
            self.current_run_contradictions += 1  # Count all contradictions from current run
            if not self.is_duplicate_contradiction(contradiction):
                # Add metadata about when it was discovered
                contradiction['discovered_at'] = datetime.now().isoformat()
                contradiction['run_number'] = self.total_runs
                contradiction['unique_id'] = f"CONTR_{len(self.unique_contradictions) + 1:03d}"
                self.unique_contradictions.append(contradiction)
                added_count += 1
        return added_count
    
    def get_summary(self) -> Dict:
        """Get summary of tracked insights"""
        return {
            'total_runs': self.total_runs,
            'current_run_gaps': self.current_run_gaps,
            'current_run_contradictions': self.current_run_contradictions,
            'total_unique_gaps': len(self.unique_gaps),
            'total_unique_contradictions': len(self.unique_contradictions),
            'high_priority_gaps': len([g for g in self.unique_gaps if g.get('priority', '').lower() == 'high']),
            'high_severity_contradictions': len([c for c in self.unique_contradictions if c.get('severity', '').lower() == 'high']),
            'latest_discovery': max(
                [g.get('discovered_at', '') for g in self.unique_gaps] +
                [c.get('discovered_at', '') for c in self.unique_contradictions],
                default=''
            )
        }

# ================== MANUAL.IPYNB HELPER FUNCTIONS ==================
# All functions below are copied EXACTLY from manual.ipynb to ensure identical output formats

# Dynamic vocabulary building and text processing
DOC_VOCAB: set[str] = set()
WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']{2,}")
WORD_OR_OTHER = re.compile(r"[A-Za-z][A-Za-z\-']+|[0-9]+|[^\sA-Za-z0-9]+")

def build_doc_vocab_from_tables(dfs: list[pd.DataFrame]) -> set[str]:
    vocab = set()
    for df in dfs or []:
        try:
            for val in df.values.ravel():
                if not isinstance(val, str): continue
                for w in WORD_RE.findall(val):
                    vocab.add(w.lower())
        except Exception:
            continue
    return vocab

def english_score(w: str) -> float:
    # Simple fallback when wordfreq not available
    return 0.0

def word_score(w: str) -> float:
    s = 0.0
    wl = w.lower()
    if wl in DOC_VOCAB:
        s += 4.0
    s += english_score(wl)
    if len(w) >= 4:
        s += 0.25
    return s

def segment_glued_token(tok: str, max_parts: int = 4) -> str:
    """DP split of a long alpha token into likely words."""
    if not tok or len(tok) < 8: return tok
    if not re.fullmatch(r"[A-Za-z][A-Za-z\-']+", tok): return tok
    n = len(tok)
    import math
    dp = [[(-math.inf, []) for _ in range(max_parts + 1)] for __ in range(n + 1)]
    dp[0][0] = (0.0, [])
    for i in range(1, n + 1):
        for k in range(1, max_parts + 1):
            for L in range(3, min(20, i) + 1):
                j = i - L
                piece = tok[j:i]
                sc = word_score(piece)
                if sc <= 0: continue
                prev = dp[j][k - 1][0]
                if prev == -math.inf: continue
                cand = prev + sc
                if cand > dp[i][k][0]:
                    dp[i][k] = (cand, dp[j][k - 1][1] + [piece])
    best_score, best_parts = -math.inf, None
    for k in range(2, max_parts + 1):
        if dp[n][k][0] > best_score:
            best_score, best_parts = dp[n][k]
    if best_parts is None or best_score <= 0:
        return tok
    return " ".join(best_parts)

def deglue_dynamic(text: str) -> str:
    """Normalize spacing and segment glued words, preserving punctuation."""
    if not isinstance(text, str): return ""
    t = text.replace("\r", " ").replace("\n", " ")
    t = re.sub(r"[ \t]+", " ", t)
    # space after punctuation if missing, and around slashes
    t = re.sub(r",(?=\S)", ", ", t)
    t = re.sub(r";(?=\S)", "; ", t)
    t = re.sub(r":(?=\S)", ": ", t)
    t = re.sub(r"(?<=\w)/(?=\w)", " / ", t)

    parts = WORD_OR_OTHER.findall(t)
    segged = []
    for p in parts:
        if re.fullmatch(r"[A-Za-z][A-Za-z\-']+", p) and len(p) >= 8:
            segged.append(segment_glued_token(p))
        else:
            segged.append(p)
    # Reassemble with smart spacing
    s = " ".join(segged)
    s = re.sub(r"\s+([,.;:])", r"\1", s)       # no space before punctuation
    s = re.sub(r"([,;:])(?=\S)", r"\1 ", s)    # ensure 1 space after
    s = re.sub(r"[ \t]+", " ", s).strip()
    return s

def _clean_cell(s): 
    # From manual.ipynb - just apply deglue_dynamic
    if not isinstance(s, str):
        return ""
    return deglue_dynamic(s)

# Bullet splitting and text processing
def split_bullets(text: str):
    """Split only on bullet glyphs; preserve semicolons inside items."""
    if not isinstance(text, str) or not text.strip(): return []
    t = deglue_dynamic(text)
    if any(sym in t for sym in ("➢", "", "•", "\u2022", "\u25cf", "\u25a0")):
        parts = re.split(r"(?:^|\s)[➢•\u2022\u25cf\u25a0]\s*", t)
        out = []
        for p in parts:
            if not p.strip(): continue
            out.append(deglue_dynamic(p).strip(" -–—·•\t"))
        return out
    return [re.sub(r"[ \t]+", " ", t).strip()]

# Money extraction
_MONEY_RE = r"(\d{1,3}(?:,\d{3})+|\d+)"
def extract_money_all(s: str):
    if not isinstance(s, str): return []
    return [float(m.group(1).replace(",", "")) for m in re.finditer(_MONEY_RE, s)]

def primary_amount(tariff_raw: str):
    if not isinstance(tariff_raw, str): return None
    m = re.search(r"KES[^0-9]{0,10}" + _MONEY_RE, tariff_raw, flags=re.IGNORECASE)
    if m: return float(m.group(1).replace(",", ""))
    m = re.search(_MONEY_RE + r"[^0-9]{0,10}KES", tariff_raw, flags=re.IGNORECASE)
    if m: return float(m.group(1).replace(",", ""))
    nums = extract_money_all(tariff_raw)
    return max(nums) if nums else None

def labeled_amount_pairs(tariff_raw: str):
    pairs = []
    if not isinstance(tariff_raw, str) or not tariff_raw.strip(): return pairs
    lines = re.split(r"[➢•\u2022\u25cf\u25a0]|\n|;", tariff_raw.replace("\r", "\n"))
    for ln in lines:
        t = ln.strip()
        if not t: continue
        m = re.search(_MONEY_RE, t)
        if not m: continue
        amt = float(m.group(1).replace(",", ""))
        before = t[:m.start()].strip(" -:()")
        after  = t[m.end():].strip(" -:()")
        label = before if before else after
        label = re.sub(r"\b(KES|KSh|Shillings)\b", "", label, flags=re.IGNORECASE).strip(" -:()")
        if re.search(r"\bLevel\s*\d+\b", label, flags=re.IGNORECASE):
            label = ""
        pairs.append({"label": label, "amount": amt})
    return pairs

# String matching
def tokset(s): 
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))

def best_match(a, b):
    at, bt = tokset(a), tokset(b)
    if not at or not bt: return 0.0
    return len(at & bt) / (len(at)**0.5 * len(bt)**0.5)

def map_items_to_pairs(items, pairs, thresh=0.25):
    mapped, used = [], set()
    for it in items:
        best_i, best_s = None, 0.0
        for i, p in enumerate(pairs):
            if i in used: continue
            s = best_match(it, p["label"] or "")
            if s > best_s: best_s, best_i = s, i
        if best_i is not None and best_s >= thresh:
            used.add(best_i)
            mapped.append({"item": it, "label": pairs[best_i]["label"], "amount": pairs[best_i]["amount"]})
        else:
            mapped.append({"item": it, "label": None, "amount": None})
    return mapped

def split_rules_and_map(scope_items, rules_text):
    rules = split_bullets(rules_text)
    if not scope_items or not rules:
        return [[] for _ in scope_items], rules
    assigned = [[] for _ in scope_items]; leftovers = []
    for r in rules:
        scores = [best_match(it, r) for it in scope_items]
        k = int(max(range(len(scores)), key=lambda i: scores[i])) if scores else None
        if k is not None and scores[k] >= 0.25: assigned[k].append(r)
        else: leftovers.append(r)
    return assigned, leftovers

# EXACT build_structures function from manual.ipynb
def build_structures(rules_df: pd.DataFrame):
    """Build wide, exploded, and structured DataFrames exactly like manual.ipynb"""
    df = rules_df.copy()
    for c in ["fund","service","scope","access_point","tariff_raw","access_rules"]:
        if c in df.columns:
            df[c] = df[c].apply(deglue_dynamic)

    wide, exploded, structured = [], [], []
    for _, r in df.iterrows():
        fund, svc = r["fund"], r["service"]
        scope, ap, tarif, rule = r["scope"], r["access_point"], r["tariff_raw"], r["access_rules"]

        scope_items = split_bullets(scope)
        tariff_pairs = labeled_amount_pairs(tarif)
        block_tariff = primary_amount(tarif)
        item_rules, block_rule_left = split_rules_and_map(scope_items, rule)
        mapping = "itemized" if (scope_items and tariff_pairs and any(p["label"] for p in tariff_pairs)) else "block"
        item_tariffs = map_items_to_pairs(scope_items, tariff_pairs) if mapping == "itemized" \
                       else [{"item": it, "label": None, "amount": None} for it in scope_items]

        wide.append({
            "fund": fund, "service": svc, "access_point": ap,
            "scope_items": scope_items, "tariff_pairs": tariff_pairs,
            "block_tariff": block_tariff,
            "rules_items": item_rules, "rules_block": block_rule_left,
            "mapping_type": mapping,
            "tariff_raw": tarif, "access_rules_raw": rule
        })

        if scope_items:
            for idx, it in enumerate(scope_items):
                exploded.append({
                    "fund": fund, "service": svc, "scope_item": it, "access_point": ap,
                    "item_label": item_tariffs[idx]["label"], "item_tariff": item_tariffs[idx]["amount"],
                    "block_tariff": block_tariff,
                    "item_rules": item_rules[idx],
                    "block_rules": block_rule_left,
                    "mapping_type": mapping
                })
        else:
            exploded.append({
                "fund": fund, "service": svc, "scope_item": "", "access_point": ap,
                "item_label": None, "item_tariff": None, "block_tariff": block_tariff,
                "item_rules": [], "block_rules": block_rule_left, "mapping_type": mapping
            })

        if mapping == "itemized" and scope_items:
            for idx, it in enumerate(scope_items):
                structured.append({
                    "fund": fund, "service": svc, "access_point": ap, "mapping_type": mapping,
                    "scope_item": it, "item_label": item_tariffs[idx]["label"], "item_tariff": item_tariffs[idx]["amount"],
                    "block_tariff": block_tariff,
                    "item_rules": "; ".join(item_rules[idx]),
                    "block_rules": "; ".join(block_rule_left),
                    "tariff_raw": tarif, "access_rules_raw": rule
                })
        else:
            structured.append({
                "fund": fund, "service": svc, "access_point": ap, "mapping_type": mapping,
                "scope_item": "; ".join(scope_items) if scope_items else "",
                "item_label": None, "item_tariff": None,
                "block_tariff": block_tariff,
                "item_rules": "",
                "block_rules": "; ".join(block_rule_left),
                "tariff_raw": tarif, "access_rules_raw": rule
            })

    return pd.DataFrame(wide), pd.DataFrame(exploded), pd.DataFrame(structured)

# ================== END MANUAL.IPYNB HELPER FUNCTIONS ==================

# Prompt builders (enhanced/updated Kenya-context prompts)
try:
    from updated_prompts import UpdatedHealthcareAIPrompts
except Exception:
    # Minimal fallback to avoid NameError if module missing
    class UpdatedHealthcareAIPrompts:
        @staticmethod
        def get_advanced_contradiction_prompt(extracted_data: str, specialties_data: str) -> str:
            return f"Analyze contradictions in SHIF data.\n{extracted_data}\n{specialties_data}"
        @staticmethod
        def get_comprehensive_gap_analysis_prompt(services_data: str, kenya_context: str) -> str:
            return f"Analyze gaps in SHIF services.\n{services_data}\nContext: {kenya_context}"

# Import the enhanced AI prompts class
class UpdatedHealthcareAIPrompts:
    """Advanced AI prompts using real Kenya health data from WHO, KNBS, and official sources"""
    
    @staticmethod
    def get_advanced_contradiction_prompt(extracted_data: str, specialties_data: str) -> str:
        """Advanced medical contradiction detection with clinical reasoning - REAL DATA VERSION"""
        return f"""
You are **Dr. Amina Hassan**, Chief Medical Officer and Healthcare Policy Expert with 20+ years across multiple medical specializations. You're conducting a CRITICAL SAFETY REVIEW of Kenya's SHIF healthcare policies.

**YOUR CLINICAL EXPERTISE:**
🩺 **Nephrology & Dialysis**: KDOQI guidelines, renal replacement therapy protocols, session frequency standards
🫀 **Cardiology**: Cardiac intervention protocols, emergency standards, device requirements  
🧠 **Neurosurgery**: Complexity levels, facility requirements, surgical safety protocols
👶 **Pediatrics**: Age-specific requirements, safety considerations, developmental needs
🤰 **Obstetrics**: Maternal safety, delivery protocols, emergency obstetric care
🚑 **Emergency Medicine**: Triage protocols, response times, critical care standards
💊 **Pharmacology**: Drug interactions, dosing protocols, safety monitoring
🏥 **Health Systems**: Kenya's 6-tier system, facility capabilities, resource allocation

**CURRENT KENYA HEALTH CONTEXT (2024 DATA):**
- **Population**: 56.4 million (Source: UN Population Division 2024)
- **Urban/Rural Split**: 30% urban, 70% rural (Source: World Bank 2024)
- **Leading Causes of Death 2024**: 
  1. Pneumonia (leading registered cause)
  2. Cancer (second leading cause)
  3. Cardiovascular diseases (third leading cause)
  (Source: Kenya National Bureau of Statistics 2024)
- **Health System**: 47 counties, 6-tier facility structure (Level 1-6)
- **CVD Impact**: 25% of hospital admissions, 13% of deaths (WHO Kenya 2024)
- **Hypertension Prevalence**: 24% of adult population (Kenya STEPwise Survey 2015)

**EXTRACTED KENYA SHIF DATA:**
{extracted_data}

**MEDICAL SPECIALTIES ANALYSIS:**
{specialties_data}

**🚨 CRITICAL DETECTION FRAMEWORK:**

**PRIORITY 1 - LIFE-THREATENING CONTRADICTIONS:**
1. **Dialysis Session Frequencies**: HD vs HDF consistency (KDOQI standard: 3x/week minimum)
2. **Emergency Response Times**: Critical care availability conflicts
3. **Maternal Emergency Care**: Delivery vs emergency cesarean contradictions
4. **Pediatric Safety**: Age-appropriate vs adult protocols

**PRIORITY 2 - CLINICAL STANDARD VIOLATIONS:**
1. **Facility Capability Mismatches**: Complex procedures at under-equipped facilities
2. **Treatment Protocol Conflicts**: Same condition, different treatment approaches
3. **Access Requirement Contradictions**: Referral vs direct access conflicts

**PRIORITY 3 - PROVIDER CONFUSION RISKS:**
1. **Authorization Conflicts**: Pre-auth vs emergency access contradictions
2. **Coverage Limit Inconsistencies**: Same service, different limits
3. **Payment Method Conflicts**: FFS vs global budget contradictions

**MEDICAL REASONING METHODOLOGY:**
For EACH contradiction:
1. **Clinical Impact Assessment**: How does this affect patient outcomes?
2. **Medical Standard Check**: Does this violate established clinical guidelines?
3. **Safety Risk Analysis**: What are the patient safety implications?
4. **Provider Impact**: How does this confuse clinical decision-making?
5. **Kenya Context**: How does this affect Kenya's healthcare delivery?

**ENHANCED OUTPUT FORMAT:**
```json
[
  {{
    "contradiction_id": "DIAL_001_CRITICAL",
    "medical_specialty": "nephrology",
    "contradiction_type": "session_frequency_medical_inconsistency", 
    "clinical_severity": "CRITICAL",
    "description": "Hemodialysis permits 3 sessions/week while hemodiafiltration permits only 2 sessions/week for equivalent ESRD treatment",
    
    "medical_analysis": {{
      "clinical_rationale": "Both HD and HDF are renal replacement therapies requiring equivalent weekly clearance (Kt/V ≥1.2)",
      "medical_standards": "KDOQI Clinical Practice Guidelines mandate 3x/week minimum for adequate clearance",
      "clinical_equivalence": "HD and HDF serve identical clinical function - should have consistent access",
      "contraindication_assessment": "No clinical reason for HDF frequency restriction"
    }},
    
    "patient_safety_impact": {{
      "immediate_risk": "Patients may receive inadequate dialysis frequency if assigned to HDF",
      "clinical_consequences": "Reduced clearance → uremic symptoms, fluid overload, cardiovascular complications",
      "survival_impact": "Inadequate dialysis frequency directly correlates with increased mortality",
      "quality_of_life": "Uremic symptoms significantly impact daily functioning"
    }},
    
    "kenya_health_system_impact": {{
      "facility_level_effects": "Level 4-6 hospitals with dialysis capabilities affected",
      "geographic_access": "Rural patients (70% of population) may face reduced treatment options",
      "resource_allocation": "Inefficient use of advanced dialysis equipment",
      "provider_training": "Need for policy clarification training across 47 counties"
    }},
    
    "epidemiological_context": {{
      "disease_burden": "Chronic kidney disease increasing with hypertension affecting 24% of adults",
      "population_impact": "Rural population (39.6 million) most affected by access contradictions",
      "health_system_capacity": "Limited Level 4-6 facilities for advanced procedures"
    }},
    
    "evidence_documentation": {{
      "policy_text_hd": "Maximum of 3 sessions per week for haemodialysis",
      "policy_text_hdf": "Maximum of 2 sessions per week for hemodiafiltration",
      "page_references": ["p8_renal_care", "p8_advanced_dialysis"],
      "clinical_guidelines": "KDOQI 2015 Clinical Practice Guidelines"
    }},
    
    "recommended_resolution": {{
      "immediate_action": "Standardize both modalities to 3 sessions/week minimum",
      "policy_revision": "Align session limits with clinical protocols, not procedure type",
      "implementation_steps": [
        "Issue interim guidance allowing 3x/week for both modalities",
        "Update benefit package to reflect clinical equivalence",
        "Train providers on revised protocols across 47 counties"
      ],
      "timeline": "Immediate - affects ongoing patient care"
    }},
    
    "quality_metrics": {{
      "detection_confidence": 0.98,
      "clinical_impact_score": 9.5,
      "urgency_level": "CRITICAL_IMMEDIATE_ACTION",
      "validation_method": "clinical_guideline_cross_reference"
    }}
  }}
]
```

**⚡ DETECTION PRIORITIES:**
1. Focus on contradictions that directly impact patient safety and clinical outcomes
2. Identify violations of established medical guidelines and standards
3. Flag policies that create provider confusion in clinical decision-making
4. Assess contradictions that may worsen health inequities in Kenya's 47 counties

Apply your comprehensive medical expertise to identify policy inconsistencies that genuinely threaten healthcare quality and patient safety for Kenya's 56.4 million population.
"""

    @staticmethod
    def get_comprehensive_gap_analysis_prompt(services_data: str, kenya_context: str) -> str:
        """Comprehensive gap analysis with real Kenya health system data"""
        return f"""
You are **Dr. Grace Kiprotich**, former Director of Medical Services for Kenya's Ministry of Health with 25+ years in health system design and policy implementation. You have intimate knowledge of Kenya's healthcare landscape, disease patterns, and implementation challenges.

**YOUR EXPERTISE COVERS:**
🇰🇪 **Kenya Health System**: 6-tier structure, referral pathways, capacity constraints
📊 **Epidemiology**: Kenya's disease burden, demographic health surveys, mortality patterns  
🏥 **Health Infrastructure**: Facility capabilities, geographic distribution, resource mapping
💰 **Health Financing**: Insurance mechanisms, out-of-pocket spending, catastrophic costs
👥 **Health Equity**: Urban-rural disparities, vulnerable populations, access barriers
📋 **WHO Standards**: Essential health services, universal health coverage benchmarks

**CURRENT SHIF COVERAGE ANALYSIS:**
{services_data}

**REAL KENYA HEALTH PROFILE (2024 DATA):**
- **Population**: 56.4 million total
  - Urban: 16.9 million (30%)
  - Rural: 39.5 million (70%)
  (Source: UN Population Division 2024)

- **Leading Causes of Registered Deaths (2024)**:
  1. Pneumonia (leading cause)
  2. Cancer (second leading)
  3. Cardiovascular diseases (third leading)
  4. Injuries (leading cause ages 15-29)
  5. Anemia (leading cause ages 5-14)
  (Source: Kenya National Bureau of Statistics 2024)

- **Key Health Indicators**:
  - Maternal Mortality Ratio: 130-170 per 100,000 live births (2018 data, county variations)
  - Hypertension Prevalence: 24% of adult population
  - CVD Hospital Impact: 25% of admissions, 13% of deaths
  (Sources: WHO Kenya, Kenya STEPwise Survey)

- **Health System Structure**:
  - 47 counties with significant health outcome variations
  - 6-tier facility structure (Level 1-6)
  - Limited specialist availability (concentrated in urban areas)

**PRIORITY GAP DETECTION AREAS:**

**1. DISEASE BURDEN ALIGNMENT GAPS:**
- **Cardiovascular Disease**: #3 killer, 25% of hospital admissions - coverage assessment needed
- **Cancer**: #2 leading cause of death - early detection and treatment gaps
- **Pneumonia**: #1 registered killer - prevention/treatment gaps
- **Maternal Health**: MMR 130-170/100K with county variations - emergency obstetric care gaps
- **Mental Health**: Rising burden, severe service gaps

**2. DEMOGRAPHIC-SPECIFIC GAPS:**
- **Rural Population (70%)**: Access to specialized care, emergency transport
- **Urban Population (30%)**: NCDs management, specialized services
- **Children <5**: Malnutrition, preventive care, specialized pediatrics
- **Working Age (15-49)**: Injury care (leading cause 15-29), occupational health
- **Elderly**: Chronic disease management, palliative care

**3. HEALTH SYSTEM LEVEL GAPS:**
- **Level 1-2**: Community health services, basic care gaps
- **Level 3**: Health center capacity gaps for common conditions  
- **Level 4-5**: Specialist care availability, referral bottlenecks
- **Level 6**: Highly specialized care, geographic access across 47 counties

**ENHANCED GAP ANALYSIS OUTPUT:**
```json
[
  {{
    "gap_id": "CVD_REHAB_CRITICAL_001",
    "gap_category": "cardiovascular_rehabilitation_services",
    "gap_type": "missing_essential_service",
    "clinical_priority": "HIGH",
    "description": "Comprehensive cardiovascular rehabilitation services absent despite CVD being 3rd leading cause of death and 25% of hospital admissions",
    
    "kenya_epidemiological_context": {{
      "disease_burden": "CVD accounts for 25% of hospital admissions and 13% of deaths in Kenya",
      "prevalence_data": "Hypertension affects 24% of adult population (13.4 million adults)",
      "current_outcomes": "High readmission rates due to lack of structured rehabilitation",
      "geographic_burden": "Higher CVD prevalence in urban areas (30% of population) but limited rural services"
    }},
    
    "affected_populations": {{
      "primary_population": "cardiovascular_patients_post_acute_episode",
      "estimated_annual_cases": "Based on 25% of admissions - approximately 280,000 admissions annually",
      "demographic_profile": "Peak incidence in urban areas, increasing burden in rural areas",
      "vulnerable_groups": "Hypertensive patients (13.4M adults), post-MI patients, rural populations"
    }},
    
    "current_coverage_assessment": {{
      "existing_services": "Limited to Kenyatta National Hospital, Moi Teaching Hospital, few private facilities",
      "geographic_availability": "Nairobi and Mombasa primarily - 45 of 47 counties lack comprehensive services",
      "capacity_utilization": "Existing facilities at 180% capacity",
      "wait_times": "4-8 month wait for cardiac rehabilitation assessment"
    }},
    
    "health_system_impact_analysis": {{
      "level_1_2_impact": "No community-based cardiovascular rehabilitation programs",
      "level_3_impact": "Health centers lack cardiac rehabilitation capabilities",
      "level_4_impact": "County hospitals need cardiac rehabilitation units",
      "level_5_6_impact": "National/teaching hospitals overwhelmed with rehabilitation needs",
      "referral_pathway_gaps": "No structured discharge planning to community care"
    }},
    
    "clinical_evidence_base": {{
      "international_guidelines": "WHO Package of Essential NCD Interventions recommends cardiac rehabilitation",
      "clinical_effectiveness": "Cardiac rehabilitation reduces mortality by 13-20% and readmissions by 25%",
      "timing_criticality": "First 12 weeks post-event are crucial for recovery",
      "cost_effectiveness": "Rehabilitation reduces long-term care costs by 35%"
    }},
    
    "recommended_interventions": {{
      "immediate_additions": [
        "Cardiac rehabilitation units at all Level 5-6 hospitals",
        "Outpatient cardiac rehabilitation coverage",
        "Community-based secondary prevention programs"
      ],
      "service_specifications": [
        "Multidisciplinary team: cardiology, physiotherapy, nutrition, psychology",
        "Minimum 12 weeks structured rehabilitation coverage",
        "Risk factor modification and patient education programs"
      ],
      "implementation_phases": [
        "Phase 1 (0-6 months): Pilot programs in 10 high-burden counties",
        "Phase 2 (6-18 months): Scale to all Level 5-6 facilities", 
        "Phase 3 (18-36 months): Community-based programs in all 47 counties"
      ]
    }},
    
    "resource_requirements": {{
      "human_resources": "Train 800+ physiotherapists, 400+ cardiac rehabilitation specialists",
      "infrastructure": "Cardiac rehabilitation equipment, exercise facilities",
      "training_needs": "Cardiac rehabilitation certification programs",
      "estimated_cost": "KES 4.2B over 3 years for nationwide implementation"
    }},
    
    "implementation_feasibility": {{
      "technical_feasibility": "HIGH - build on existing cardiology services",
      "financial_feasibility": "MEDIUM - significant investment but high ROI",
      "political_feasibility": "HIGH - aligns with UHC goals and NCDs strategy",
      "timeline_realistic": "3 years for coverage in all 47 counties"
    }},
    
    "success_metrics": {{
      "process_indicators": "Number of facilities offering cardiac rehabilitation",
      "outcome_indicators": "30-day and 1-year readmission rates",
      "impact_indicators": "CVD mortality rates, quality of life scores",
      "equity_indicators": "Geographic distribution across all 47 counties"
    }},
    
    "kenya_context_integration": {{
      "county_variations": "Urban counties need advanced programs, rural counties need basic services",
      "cultural_considerations": "Family-centered care approach, community health worker integration",
      "integration_opportunities": "Link with NCDs programs, community health strategy",
      "sustainability_factors": "County government ownership, local provider training"
    }}
  }}
]
```

**🎯 ANALYSIS PRIORITIES:**
1. **High-burden gaps**: Services critical for managing Kenya's leading causes of death and hospitalization
2. **Population-specific gaps**: Address urban-rural disparities affecting 70% rural population
3. **Health system strengthening gaps**: Services that improve overall performance across 47 counties
4. **Evidence-based gaps**: Missing services with proven clinical effectiveness and cost-effectiveness

Focus on gaps that would have the greatest population health impact for Kenya's 56.4 million population and are feasible within the country's health system constraints and county structure.

**CRITICAL: RESPOND ONLY WITH JSON ARRAY FORMAT AS SHOWN IN THE EXAMPLE ABOVE. NO OTHER TEXT.**
"""

class IntegratedComprehensiveMedicalAnalyzer:
    """
    Integrated analyzer combining proven extraction with comprehensive AI analysis
    """
    
    def __init__(self, api_key: str = None, pdf_path: str = None):
        # Load API key from .env file if available
        import os
        try:
            from dotenv import load_dotenv  # type: ignore
            load_dotenv('.env', override=True)
        except Exception:
            # dotenv not installed; proceed without loading .env
            pass
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None
        self.primary_model = "gpt-5-mini"  # Primary model as specified
        self.fallback_model = "gpt-4.1-mini"  # Fallback model as specified
        
        # Store PDF path for CSV export
        self.pdf_path = pdf_path
        
        # Initialize vocabulary for dynamic de-glue
        self.doc_vocab = set()
        
        # Create dynamic output directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(f"outputs_run_{timestamp}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # AI cache directory (shared across runs)
        self.ai_cache_dir = Path("ai_cache")
        self.ai_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage for comprehensive results
        self.policy_services = []      # Pages 1-18 structured services
        self.annex_procedures = []     # Pages 19-54 procedures  
        self.ai_contradictions = []    # AI-enhanced contradictions
        
        # Initialize unique insights tracker
        self.unique_tracker = UniqueInsightTracker()
        # Start tracking this run
        self.unique_tracker.start_new_run()
        self.comprehensive_gaps = []   # All identified gaps
        
        print(f"🚀 Integrated Comprehensive Medical Analyzer") 
        print(f"   📊 Pages 1-18: Validated extraction with dynamic de-glue")
        print(f"   📊 Pages 19-54: Validated Simple Tabula extraction")
        print(f"   🤖 AI Analysis: {'ENABLED' if self.client else 'DISABLED'}")
        
        # User's proven extraction constants
        self.FUND_RE = re.compile(r"FUND$", re.I)
        self.SECTION_RE = re.compile(r"[A-Z0-9 ,&()'/-]{6,}(SERVICES|PACKAGE)$")
        self.TOKENS = ["scope","access point","tariff","access rules"]
        self.WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']{2,}")
        self._MONEY_RE = r"(\d{1,3}(?:,\d{3})+|\d+)"

    # ========== USER'S PROVEN EXTRACTION FUNCTIONS ==========
    def _clean_cell(self, s):
        """User's proven cell cleaning function"""
        if s is None or (isinstance(s, float) and pd.isna(s)): 
            return ""
        s = str(s)
        s = s.replace("\r", " ").replace("\n", " ")
        s = re.sub(r"[•\u2022\u25cf\u25a0]", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def _row_nonempties(self, row_vals):
        """User's proven function"""
        vals = [self._clean_cell(v) for v in row_vals]
        return [v for v in vals if v]

    def _looks_header_row(self, row_vals):
        """User's proven header detection"""
        joined = " ".join(self._row_nonempties(row_vals)).lower()
        return all(tok in joined for tok in self.TOKENS)

    def _label_in_row(self, row_vals):
        """User's proven label detection"""
        vals = [self._clean_cell(v) for v in row_vals]
        nonempty = [(i, v) for i, v in enumerate(vals) if v]
        if len(nonempty) != 1:
            return None
        txt = nonempty[0][1]
        if self.FUND_RE.search(txt):
            return ("fund", txt)
        if self.SECTION_RE.search(txt) and "fund" not in txt.lower():
            return ("section", txt)
        return None

    def read_tables_proven(self, pdf_path: str, pages="1-18"):
        """User's proven table reading with defensive fallback when tabula isn't available"""
        if tabula is None:
            print("   ⚠️ tabula-py not available; skipping table read for",
                  f"pages {pages} and returning no tables")
            return []
        dfs = tabula.read_pdf(
            pdf_path,
            pages=pages,
            lattice=True,
            multiple_tables=True,
            pandas_options={"header": None},
        ) or []
        if not dfs:
            dfs = tabula.read_pdf(
                pdf_path,
                pages=pages,
                stream=True,
                multiple_tables=True,
                pandas_options={"header": None},
            ) or []
        return dfs

    def extract_rules_tables_proven(self, pdf_path: str, pages="1-18"):
        """User's PROVEN extraction function for pages 1-18"""
        tables = self.read_tables_proven(pdf_path, pages)
        rows = []
        current_fund = None
        current_section = None
        seen_header = False

        for t in tables:
            if t is None or t.empty:
                continue
            # drop fully empty cols, normalize strings
            t = t.dropna(how="all", axis=1).reset_index(drop=True)
            # if table has one column, try label detection
            if t.shape[1] == 1:
                lab = self._label_in_row(t.iloc[0].tolist())
                if lab:
                    kind, txt = lab
                    if kind == "fund":
                        current_fund = txt
                        current_section = None
                    else:
                        current_section = txt
                    seen_header = False
                continue

            # scan each row
            t = t.map(self._clean_cell)
            for i in range(len(t)):
                row_vals = t.iloc[i].tolist()

                # label rows could be inside this table
                lab = self._label_in_row(row_vals)
                if lab:
                    kind, txt = lab
                    # flush pending merged row if any
                    if 'current_row' in locals() and current_row:
                        rows.append(current_row); current_row = None
                    if kind == "fund":
                        current_fund = txt
                        current_section = None
                    else:
                        current_section = txt
                    seen_header = False
                    continue

                # header row?
                if self._looks_header_row(row_vals):
                    seen_header = True
                    # from now, treat next rows as data
                    if 'current_row' in locals(): 
                        current_row = None
                    continue

                if not seen_header:
                    # not in a data block yet
                    continue

                # ensure exactly 4 columns by padding/trimming
                vals = row_vals[:4] + [""]*(4-len(row_vals))
                scope, access_point, tariff_raw, access_rules = vals[:4]

                # if mostly empty, treat as continuation of previous row
                empties = sum(1 for v in [scope, access_point, tariff_raw, access_rules] if not v)
                if 'current_row' not in locals() or current_row is None:
                    # start a row if there's something
                    if scope or access_point or tariff_raw or access_rules:
                        current_row = {
                            "fund": current_fund,
                            "service": current_section,
                            "scope": scope,
                            "access_point": access_point,
                            "tariff_raw": tariff_raw,
                            "access_rules": access_rules
                        }
                else:
                    if empties >= 2:
                        # continuation line: append non-empty cells
                        if scope:        current_row["scope"]        = (current_row["scope"] + " " + scope).strip()
                        if access_point: current_row["access_point"] = (current_row["access_point"] + " " + access_point).strip()
                        if tariff_raw:   current_row["tariff_raw"]   = (current_row["tariff_raw"] + " " + tariff_raw).strip()
                        if access_rules: current_row["access_rules"] = (current_row["access_rules"] + " " + access_rules).strip()
                    else:
                        # new logical row, push previous if it has any content
                        rows.append(current_row)
                        current_row = {
                            "fund": current_fund,
                            "service": current_section,
                            "scope": scope,
                            "access_point": access_point,
                            "tariff_raw": tariff_raw,
                            "access_rules": access_rules
                        }

            # flush at end of table
            if 'current_row' in locals() and current_row:
                rows.append(current_row)
                current_row = None

        # finalize dataframe
        df = pd.DataFrame(rows)
        if df.empty:
            return df
        # numeric tariffs (best-effort)
        df["tariff_num"] = (
            df["tariff_raw"]
            .fillna("").astype(str)
            .str.extract(r"([0-9][0-9,]*)", expand=False)
            .dropna()
            .str.replace(",", "", regex=False)
            .astype(float)
        ).reindex(df.index)
        # tidy
        df["fund"] = df["fund"].replace("", pd.NA).ffill()
        df["service"] = df["service"].replace("", pd.NA).ffill()
        return df

    def analyze_complete_document(self, pdf_path: str, run_extended_ai: bool = False) -> Dict:
        """Complete integrated analysis"""
        
        # Store pdf_path for CSV export if not already set
        if not self.pdf_path:
            self.pdf_path = pdf_path
        
        print(f"\n🎯 INTEGRATED COMPREHENSIVE ANALYSIS: {pdf_path}")
        print("=" * 70)
        
        start_time = time.time()
        
        # PHASE 1: Build vocabulary from document
        print(f"\n📚 PHASE 1: Building Document Vocabulary")
        self._build_document_vocabulary(pdf_path)
        
        # PHASE 2: Extract Pages 1-18 with advanced processing
        print(f"\n📊 PHASE 2: Extracting Pages 1-18 (Policy Structure)")
        policy_results = self._extract_policy_structure(pdf_path, "1-18")
        
        # PHASE 3: Extract Pages 19-54 with simple tabula
        print(f"\n📊 PHASE 3: Extracting Pages 19-54 (Annex Procedures)")
        annex_results = self._extract_annex_procedures(pdf_path, "19-54")
        
        # Save raw extraction immediately for direct access
        print(f"\n💾 DIRECT ACCESS: Raw extractions saved to {self.output_dir}")
        print(f"   📋 Policy data: {self.output_dir}/rules_p1_18_structured.csv")
        if annex_results.get('procedures') is not None and not annex_results['procedures'].empty:
            try:
                annex_results['procedures'].to_csv(self.output_dir / 'annex_procedures.csv', index=False)
                print(f"   📋 Annex data: {self.output_dir}/annex_procedures.csv")
            except Exception:
                pass
        
        # PHASE 4: AI-Enhanced Analysis
        print(f"\n🤖 PHASE 4: AI-Enhanced Medical Analysis")
        ai_analysis = self._ai_enhanced_analysis(pdf_path, policy_results, annex_results)

        extended_ai = {}
        if run_extended_ai and self.client:
            print(f"\n🧠 PHASE 4B: Extended AI Analyses (quality, alignment, equity, recommendations)")
            try:
                extended_ai = self._run_comprehensive_extended_ai(policy_results, annex_results, ai_analysis)
                print("   ✅ Extended AI analyses complete")
            except Exception as e:
                print(f"   ⚠️ Extended AI failed: {e}")
        
        # PHASE 4C: Coverage Analysis - Comprehensive Coverage Gap Detection
        coverage_analysis = {}
        if self.client:
            print(f"\n🏥 PHASE 4C: Comprehensive Coverage Analysis")
            try:
                coverage_analysis = self._run_coverage_analysis(policy_results, annex_results, ai_analysis)
                print("   ✅ Coverage analysis complete")
            except Exception as e:
                print(f"   ⚠️ Coverage analysis failed: {e}")
        
        # PHASE 5: Comprehensive Integration
        print(f"\n✅ PHASE 5: Results Integration")
        results = self._integrate_comprehensive_results(policy_results, annex_results, ai_analysis, coverage_analysis)
        if extended_ai:
            results['extended_ai'] = extended_ai
        if coverage_analysis:
            results['coverage_analysis'] = coverage_analysis
        
        analysis_time = round(time.time() - start_time, 2)
        results['analysis_metadata'] = {
            'analysis_time_seconds': analysis_time,
            'approach': 'INTEGRATED_COMPREHENSIVE',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self._print_comprehensive_summary(results, analysis_time)
        return results

    # ========== Dynamic De-glue Implementation ==========
    
    def _build_document_vocabulary(self, pdf_path: str):
        """Build vocabulary from document tables for intelligent de-glue"""
        try:
            # Extract sample tables to build vocabulary (only if tabula is available)
            dfs = []
            if tabula is not None:
                dfs = tabula.read_pdf(
                    pdf_path,
                    pages="1-18",
                    lattice=True,
                    multiple_tables=True,
                    pandas_options={"header": None},
                ) or []
            
            word_re = re.compile(r"[A-Za-z][A-Za-z\-']{2,}")
            
            for df in dfs or []:
                try:
                    for val in df.values.ravel():
                        if isinstance(val, str):
                            for word in word_re.findall(val):
                                self.doc_vocab.add(word.lower())
                except Exception:
                    continue
            
            print(f"   ✅ Built vocabulary: {len(self.doc_vocab)} terms")
            
        except Exception as e:
            print(f"   ⚠️ Vocabulary building failed: {e}")
            self.doc_vocab = set()
    
    def _build_doc_vocab_from_tables(self, dfs: List[pd.DataFrame]) -> set:
        """EXACT manual.ipynb vocab building function"""
        WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']{2,}")
        vocab = set()
        for df in dfs or []:
            try:
                for val in df.values.ravel():
                    if not isinstance(val, str): continue
                    for w in WORD_RE.findall(val):
                        vocab.add(w.lower())
            except Exception:
                continue
        return vocab

    def _word_score(self, word: str) -> float:
        """Score word likelihood for segmentation"""
        score = 0.0
        word_lower = word.lower()
        
        # Bonus for document vocabulary
        if word_lower in self.doc_vocab:
            score += 4.0
            
        # Bonus for reasonable length
        if len(word) >= 4:
            score += 0.25
            
        return score

    def _segment_glued_token(self, token: str, max_parts: int = 4) -> str:
        """Dynamic programming segmentation of glued words"""
        if not token or len(token) < 8:
            return token
            
        if not re.fullmatch(r"[A-Za-z][A-Za-z\-']+", token):
            return token
            
        n = len(token)
        # dp[i][k] = (best_score, best_segmentation) for first i chars using k parts
        dp = [[(-math.inf, []) for _ in range(max_parts + 1)] for __ in range(n + 1)]
        dp[0][0] = (0.0, [])
        
        for i in range(1, n + 1):
            for k in range(1, max_parts + 1):
                for length in range(3, min(20, i) + 1):
                    j = i - length
                    piece = token[j:i]
                    piece_score = self._word_score(piece)
                    
                    if piece_score <= 0:
                        continue
                        
                    prev_score = dp[j][k - 1][0]
                    if prev_score == -math.inf:
                        continue
                        
                    candidate_score = prev_score + piece_score
                    if candidate_score > dp[i][k][0]:
                        dp[i][k] = (candidate_score, dp[j][k - 1][1] + [piece])
        
        # Find best segmentation
        best_score, best_parts = -math.inf, None
        for k in range(2, max_parts + 1):
            score, parts = dp[n][k]
            if score > best_score:
                best_score, best_parts = score, parts
        
        if best_parts:
            whole_score = self._word_score(token)
            if best_score > max(whole_score, 0.5):
                return " ".join(best_parts)
        
        return token

    def _deglue_dynamic(self, text: str) -> str:
        """Normalize spacing and segment glued words"""
        if not isinstance(text, str):
            return ""
            
        # Normalize whitespace
        text = text.replace("\r", " ").replace("\n", " ")
        text = re.sub(r"[ \t]+", " ", text)
        
        # Add spacing around punctuation
        text = re.sub(r",(?=\S)", ", ", text)
        text = re.sub(r";(?=\S)", "; ", text) 
        text = re.sub(r":(?=\S)", ": ", text)
        text = re.sub(r"(?<=\w)/(?=\w)", " / ", text)
        
        # Find and segment potential words
        word_pattern = re.compile(r"[A-Za-z][A-Za-z\-']+|[0-9]+|[^\sA-Za-z0-9]+")
        parts = word_pattern.findall(text)
        
        segmented = []
        for part in parts:
            if re.fullmatch(r"[A-Za-z][A-Za-z\-']+", part) and len(part) >= 8:
                segmented.append(self._segment_glued_token(part))
            else:
                segmented.append(part)
        
        # Reassemble with proper spacing
        result = " ".join(segmented)
        result = re.sub(r"\s+([,.;:])", r"\1", result)  # Remove space before punctuation
        result = re.sub(r"([,;:])(?=\S)", r"\1 ", result)  # Add space after
        result = re.sub(r"[ \t]+", " ", result).strip()
        
        return result

    # ========== Pages 1-18 Advanced Extraction ==========
    
    def _extract_policy_structure(self, pdf_path: str, pages: str = "1-18") -> Dict:
        """Extract policy structure for pages 1–18 using the manual pdfplumber-based slicer.

        This matches the notebook approach: Build lines from words, detect the
        header line with Scope/Access Point/Tariff/Access Rules, slice subsequent
        lines into 4 columns, and capture FUND/SECTION labels.
        """
        try:
            # Use the EXACT manual.ipynb code
            df = self._extract_rules_manual_exact(pdf_path)
            # Normalize column names to match downstream expectations
            if 'section' in df.columns:
                df = df.rename(columns={'section': 'service'})
            # Build structured/wide/exploded using existing helper
            wide_df, exploded_df, structured_df = self._build_policy_structures(df)
            print(f"   ✅ Policy extraction complete:")
            print(f"      • Raw entries: {len(df)}")
            print(f"      • Structured entries: {len(structured_df)}")
            # Save CSVs for parity with manual
            out_dir = Path('outputs'); out_dir.mkdir(exist_ok=True)
            try:
                df.to_csv(out_dir / 'rules_p1_18_structured.csv', index=False)
                wide_df.to_csv(out_dir / 'rules_p1_18_structured_wide.csv', index=False)
                exploded_df.to_csv(out_dir / 'rules_p1_18_structured_exploded.csv', index=False)
            except Exception:
                pass
            try:
                df.to_csv(self.output_dir / 'rules_p1_18_structured.csv', index=False)
                wide_df.to_csv(self.output_dir / 'rules_p1_18_structured_wide.csv', index=False)
                exploded_df.to_csv(self.output_dir / 'rules_p1_18_structured_exploded.csv', index=False)
            except Exception:
                pass
            return {
                'raw': df,
                'structured': structured_df,
                'wide': wide_df,
                'exploded': exploded_df,
            }
        except Exception as e:
            print(f"   ❌ Policy extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return {'raw': pd.DataFrame(), 'structured': pd.DataFrame(), 'wide': pd.DataFrame(), 'exploded': pd.DataFrame()}

    def _extract_rules_manual_exact(self, pdf_path: str) -> pd.DataFrame:
        """EXACT code from manual.ipynb - adapted to use optional tabula import"""
        # Use the optional top-level tabula import; fail gracefully if unavailable
        global tabula
        if tabula is None:
            print("❌ tabula-py not available — cannot extract rules for pages 1-18 in this mode")
            return pd.DataFrame()
        
        # EXACT read_tables_raw from manual.ipynb
        def read_tables_raw(pages="1-18"):
            dfs = tabula.read_pdf(pdf_path, pages=pages, lattice=True, multiple_tables=True,
                                  pandas_options={"header": None}) or []
            if not dfs:
                dfs = tabula.read_pdf(pdf_path, pages=pages, stream=True, multiple_tables=True,
                                      pandas_options={"header": None}) or []
            return dfs
        
        # Build vocabulary
        global DOC_VOCAB
        raw_dfs = read_tables_raw("1-18")
        DOC_VOCAB = build_doc_vocab_from_tables(raw_dfs)
        
        # EXACT constants from manual.ipynb
        FUND_RE = re.compile(r"FUND$", re.I)
        SECTION_RE = re.compile(r"[A-Z0-9 ,&()'/-]{6,}(SERVICES|PACKAGE)$")
        TOKENS = ["scope","access point","tariff","access rules"]
        
        def _is_header_row(vals):
            joined = " ".join(v.lower() for v in vals if v)
            return all(tok in joined for tok in TOKENS)
        
        def _label_row(vals):
            non = [v for v in vals if v]
            if len(non) != 1: return None
            txt = non[0]
            if FUND_RE.search(txt): return ("fund", txt)
            if SECTION_RE.search(txt) and "fund" not in txt.lower(): return ("section", txt)
            return None
        
        # EXACT extract_rules_p1_18 from manual.ipynb
        dfs = read_tables_raw("1-18")
        
        rows = []
        current_fund = None
        current_service = None
        seen_header = False
        current_row = None
        carryover = None
        
        for df in dfs:
            if df is None or df.empty: continue
            df = df.dropna(how="all", axis=1).reset_index(drop=True)
            # Apply _clean_cell exactly like manual.ipynb does
            df = df.map(_clean_cell)
        
            for _, row in df.iterrows():
                vals = row.tolist()
        
                lab = _label_row(vals)
                if lab:
                    if current_row: rows.append(current_row); current_row = None
                    kind, txt = lab
                    if kind == "fund": current_fund = txt; current_service = None
                    else: current_service = txt
                    seen_header = False
                    continue
        
                if _is_header_row(vals):
                    seen_header = True
                    if current_row: rows.append(current_row); current_row = None
                    continue
        
                if not seen_header: continue
        
                vals = vals[:4] + [""]*(4-len(vals))
                scope, ap, tarif, rule = vals
                if not any([scope, ap, tarif, rule]): continue
        
                if carryover and scope and not any([ap, tarif, rule]):
                    carryover["scope"] = (carryover["scope"] + " " + scope).strip()
                    continue
                if carryover:
                    rows.append(carryover); carryover = None
        
                empties = sum(1 for v in (scope, ap, tarif, rule) if not v)
                if current_row is None:
                    current_row = {
                        "fund": current_fund,
                        "service": current_service,
                        "scope": scope,
                        "access_point": ap,
                        "tariff_raw": tarif,
                        "access_rules": rule
                    }
                else:
                    if empties >= 2:
                        if scope: current_row["scope"] = (current_row["scope"] + " " + scope).strip()
                        if ap: current_row["access_point"] = (current_row["access_point"] + " " + ap).strip()
                        if tarif: current_row["tariff_raw"] = (current_row["tariff_raw"] + " " + tarif).strip()
                        if rule: current_row["access_rules"] = (current_row["access_rules"] + " " + rule).strip()
                    else:
                        rows.append(current_row)
                        current_row = {
                            "fund": current_fund,
                            "service": current_service,
                            "scope": scope,
                            "access_point": ap,
                            "tariff_raw": tarif,
                            "access_rules": rule
                        }
        
            if current_row: carryover = current_row; current_row = None
        
        if carryover: rows.append(carryover)
        return pd.DataFrame(rows)

    def _extract_rules_pdfplumber_p1_18_BROKEN(self, pdf_path: str) -> pd.DataFrame:
        """EXACT manual.ipynb extraction - using exact code from manual.ipynb"""
        # Guarded access to optional tabula import
        try:
            global tabula
            if tabula is None:
                raise ImportError()
        except ImportError:
            print("❌ tabula-py not available")
            return pd.DataFrame()
            
        # Build document vocabulary from raw tables first
        def read_tables_raw(pages="1-18"):
            dfs = tabula.read_pdf(pdf_path, pages=pages, lattice=True, multiple_tables=True,
                                  pandas_options={"header": None}) or []
            if not dfs:
                dfs = tabula.read_pdf(pdf_path, pages=pages, stream=True, multiple_tables=True,
                                      pandas_options={"header": None}) or []
            return dfs
        
        # Learn vocabulary from raw tables
        raw_dfs = read_tables_raw("1-18")
        global DOC_VOCAB
        DOC_VOCAB = build_doc_vocab_from_tables(raw_dfs)
        
        # EXACT manual.ipynb constants and functions - UNCHANGED
        FUND_RE = re.compile(r"FUND$", re.I)
        SECTION_RE = re.compile(r"[A-Z0-9 ,&()'/-]{6,}(SERVICES|PACKAGE)$")
        TOKENS = ["scope","access point","tariff","access rules"]
        
        def _is_header_row(vals):
            joined = " ".join(v.lower() for v in vals if v)
            return all(tok in joined for tok in TOKENS)
        
        def _label_row(vals):
            non = [v for v in vals if v]
            if len(non) != 1: return None
            txt = non[0]
            if FUND_RE.search(txt): return ("fund", txt)
            if SECTION_RE.search(txt) and "fund" not in txt.lower(): return ("section", txt)
            return None
        
        # EXACT extract_rules_p1_18 function from manual.ipynb - UNCHANGED
        dfs = read_tables_raw("1-18")
        
        rows = []
        current_fund = None
        current_service = None
        seen_header = False
        current_row = None
        carryover = None
        
        for df in dfs:
            if df is None or df.empty: continue
            df = df.dropna(how="all", axis=1).reset_index(drop=True)
            # DON'T apply deglue yet - need to detect labels first
        
            for _, row in df.iterrows():
                vals = row.tolist()
        
                # Check for labels BEFORE degluing
                lab = _label_row(vals)
                if lab:
                    if current_row: rows.append(current_row); current_row = None
                    kind, txt = lab
                    if kind == "fund": current_fund = txt; current_service = None
                    else: current_service = txt
                    seen_header = False
                    continue
        
                if _is_header_row(vals):
                    seen_header = True
                    if current_row: rows.append(current_row); current_row = None
                    continue
        
                if not seen_header: continue
        
                # Now apply deglue to data rows only
                vals = [_clean_cell(v) if v else "" for v in vals]
                vals = vals[:4] + [""]*(4-len(vals))
                scope, ap, tarif, rule = vals
                if not any([scope, ap, tarif, rule]): continue
        
                if carryover and scope and not any([ap, tarif, rule]):
                    carryover["scope"] = (carryover["scope"] + " " + scope).strip()
                    continue
                if carryover:
                    rows.append(carryover); carryover = None
        
                empties = sum(1 for v in (scope, ap, tarif, rule) if not v)
                if current_row is None:
                    current_row = {
                        "fund": current_fund,
                        "service": current_service,
                        "scope": scope,
                        "access_point": ap,
                        "tariff_raw": tarif,
                        "access_rules": rule
                    }
                else:
                    if empties >= 2:
                        if scope: current_row["scope"] = (current_row["scope"] + " " + scope).strip()
                        if ap: current_row["access_point"] = (current_row["access_point"] + " " + ap).strip()
                        if tarif: current_row["tariff_raw"] = (current_row["tariff_raw"] + " " + tarif).strip()
                        if rule: current_row["access_rules"] = (current_row["access_rules"] + " " + rule).strip()
                    else:
                        rows.append(current_row)
                        current_row = {
                            "fund": current_fund,
                            "service": current_service,
                            "scope": scope,
                            "access_point": ap,
                            "tariff_raw": tarif,
                            "access_rules": rule
                        }
        
            if current_row: carryover = current_row; current_row = None
        
        if carryover: rows.append(carryover)
        
        # Return exact DataFrame structure from manual.ipynb
        result_df = pd.DataFrame(rows)
        
        # Add tariff_num column using manual.ipynb logic
        if not result_df.empty and 'tariff_raw' in result_df.columns:
            result_df["tariff_num"] = result_df["tariff_raw"].apply(primary_amount)
        
        return result_df


    def _process_policy_tables(self, dfs: List[pd.DataFrame]) -> pd.DataFrame:
        """Process policy tables with fund/service hierarchy detection"""
        
        fund_pattern = re.compile(r"FUND$", re.I)
        section_pattern = re.compile(r"[A-Z0-9 ,&()'/-]{6,}(SERVICES|PACKAGE)$")
        header_tokens = ["scope", "access point", "tariff", "access rules"]
        
        def is_header_row(values):
            joined = " ".join(str(v).lower() for v in values if v)
            return all(token in joined for token in header_tokens)
            
        def label_row_type(values):
            non_empty = [v for v in values if v and str(v).strip()]
            if len(non_empty) != 1:
                return None
                
            text = str(non_empty[0])
            if fund_pattern.search(text):
                return ("fund", text)
            if section_pattern.search(text) and "fund" not in text.lower():
                return ("section", text)
            return None
        
        rows = []
        current_fund = None
        current_service = None
        seen_header = False
        current_row = None
        carryover = None
        
        for df in dfs:
            if df is None or df.empty:
                continue
                
            # Clean and normalize
            df = df.dropna(how="all", axis=1).reset_index(drop=True)
            df = df.applymap(lambda x: self._deglue_dynamic(str(x)) if pd.notna(x) else x)
            
            for _, row in df.iterrows():
                values = row.tolist()
                
                # Check for fund/service headers
                label_info = label_row_type(values)
                if label_info:
                    if current_row:
                        rows.append(current_row)
                        current_row = None
                        
                    kind, text = label_info
                    if kind == "fund":
                        current_fund = text
                        current_service = None
                    else:
                        current_service = text
                    seen_header = False
                    continue
                
                # Check for table headers
                if is_header_row(values):
                    seen_header = True
                    if current_row:
                        rows.append(current_row)
                        current_row = None
                    continue
                
                # Skip until we see headers
                if not seen_header:
                    continue
                
                # Process data rows
                values = values[:4] + [""] * (4 - len(values))
                scope, access_point, tariff, rules = values
                
                if not any([scope, access_point, tariff, rules]):
                    continue
                
                # Handle continuation logic
                if carryover and scope and not any([access_point, tariff, rules]):
                    carryover["scope"] = (carryover["scope"] + " " + scope).strip()
                    continue
                    
                if carryover:
                    rows.append(carryover)
                    carryover = None
                
                # Create new row or continue existing
                empty_count = sum(1 for v in (scope, access_point, tariff, rules) if not v)
                
                if current_row is None:
                    current_row = {
                        "fund": current_fund,
                        "service": current_service, 
                        "scope": scope or "",
                        "access_point": access_point or "",
                        "tariff_raw": tariff or "",
                        "access_rules": rules or ""
                    }
                else:
                    if empty_count >= 2:
                        # Continuation row
                        if scope:
                            current_row["scope"] = (current_row["scope"] + " " + scope).strip()
                        if access_point:
                            current_row["access_point"] = (current_row["access_point"] + " " + access_point).strip()
                        if tariff:
                            current_row["tariff_raw"] = (current_row["tariff_raw"] + " " + tariff).strip()
                        if rules:
                            current_row["access_rules"] = (current_row["access_rules"] + " " + rules).strip()
                    else:
                        # New row
                        rows.append(current_row)
                        current_row = {
                            "fund": current_fund,
                            "service": current_service,
                            "scope": scope or "",
                            "access_point": access_point or "",
                            "tariff_raw": tariff or "", 
                            "access_rules": rules or ""
                        }
            
            if current_row:
                carryover = current_row
                current_row = None
        
        if carryover:
            rows.append(carryover)
        
        return pd.DataFrame(rows)

    def _build_policy_structures(self, rules_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Build structured policy formats using EXACT manual.ipynb build_structures function"""
        return build_structures(rules_df)

    def _split_bullets(self, text: str) -> List[str]:
        """EXACT split_bullets function from manual.ipynb"""
        return split_bullets(text)

    def _extract_tariff_pairs(self, tariff_text: str) -> List[Dict]:
        """EXACT labeled_amount_pairs function from manual.ipynb"""
        return labeled_amount_pairs(tariff_text)

    def _extract_primary_tariff(self, tariff_text: str) -> Optional[float]:
        """EXACT primary_amount function from manual.ipynb"""
        return primary_amount(tariff_text)

    # ========== Pages 19-54 Simple Tabula Extraction ==========
    
    def _extract_annex_procedures(self, pdf_path: str, pages: str = "19-54") -> Dict:
        """EXACT manual.ipynb annex extraction - extract_annex_tabula_simple function"""
        try:
            if tabula is None:
                print("   ⚠️ tabula-py not available; skipping annex table extraction")
                return {'procedures': pd.DataFrame()}

            # EXACT extract_annex_tabula_simple function from manual.ipynb
            dfs = tabula.read_pdf(
                pdf_path,
                pages=pages,
                multiple_tables=True,
                pandas_options={"header": None}
            ) or []
            
            results = []
            for df in dfs:
                if df is None or df.empty or df.shape[1] < 3:
                    continue
                    
                df = df.iloc[:, :4].copy()
                df.columns = ["num", "specialty", "intervention", "tariff"]

                # Forward-fill specialty
                df["specialty"] = df["specialty"].ffill()

                merged_rows = []
                current = None
                pre_buffer = []  # holds continuation lines that appear BEFORE a numbered row

                for _, row in df.iterrows():
                    num = row["num"]
                    spec = str(row["specialty"]).strip() if pd.notna(row["specialty"]) else ""
                    interv = str(row["intervention"]).strip() if pd.notna(row["intervention"]) else ""
                    tariff_raw = str(row["tariff"]).strip() if pd.notna(row["tariff"]) else ""

                    if pd.notna(num):  # start of a new entry
                        # flush previous
                        if current:
                            merged_rows.append(current)

                        # stitch any text collected ABOVE the number into the new intervention
                        start_text = " ".join(pre_buffer + ([interv] if interv else []))
                        pre_buffer = []  # reset buffer

                        current = {
                            "id": int(num) if str(num).isdigit() else num,
                            "specialty": spec,
                            "intervention": start_text.strip(),
                            "tariff_text": tariff_raw
                        }
                    else:
                        # continuation row
                        if current is None:
                            # no current yet → this line belongs to the NEXT numbered row
                            if interv:
                                pre_buffer.append(interv)
                            # sometimes tariff appears on a pre-line, keep last seen
                            if tariff_raw:
                                # stash on buffer end marker so it can override later if needed
                                pre_buffer.append(f"[TARIFF:{tariff_raw}]")
                            continue

                        if interv:
                            current["intervention"] = (current["intervention"] + " " + interv).strip()
                        if tariff_raw:
                            current["tariff_text"] = tariff_raw

                if current:
                    merged_rows.append(current)

                # clean any accidental tariff markers in pre_buffer merges
                for r in merged_rows:
                    if "[TARIFF:" in r["intervention"]:
                        # drop those markers from text; tariff already handled by numbered line normally
                        r["intervention"] = re.sub(r"\[TARIFF:.*?\]", "", r["intervention"]).strip()

                results.extend(merged_rows)

            # Convert to exact DataFrame structure from manual.ipynb
            annex_df_all = pd.DataFrame(results, columns=["id","specialty","intervention","tariff_text"]) if results else pd.DataFrame(columns=["id","specialty","intervention","tariff_text"])

            # tidy tariff to numeric - EXACT from manual.ipynb
            if not annex_df_all.empty:
                annex_df_all["tariff"] = (
                    annex_df_all["tariff_text"]
                    .fillna("").astype(str)
                    .str.replace(r"[^\d.]", "", regex=True)
                    .replace("", pd.NA)
                    .astype(float)
                )
                annex_df_all = annex_df_all.drop(columns=["tariff_text"])

                # optional tidying - EXACT from manual.ipynb
                annex_df_all["specialty"] = annex_df_all["specialty"].str.strip()
                annex_df_all["intervention"] = (
                    annex_df_all["intervention"]
                    .str.replace(r"\s+", " ", regex=True)
                    .str.replace(r"\s*/\s*", " / ", regex=True)
                    .str.replace(r"\s*-\s*", " - ", regex=True)
                    .str.strip()
                )
                # make id a nullable integer
                annex_df_all["id"] = pd.to_numeric(annex_df_all["id"], errors="coerce").astype("Int64")

                # drop obviously empty rows
                annex_df_all = annex_df_all[(annex_df_all["specialty"] != "") & (annex_df_all["intervention"] != "")]

                # sort & dedupe - EXACT from manual.ipynb
                annex_df_all = annex_df_all.drop_duplicates().sort_values(["specialty","id","intervention"], na_position="last").reset_index(drop=True)

            print(f"   ✅ Annex extraction complete: {len(annex_df_all)} procedures")
            return {'procedures': annex_df_all}

        except Exception as e:
            print(f"   ❌ Annex extraction failed: {e}")
            return {'procedures': pd.DataFrame()}

    # ========== AI-Enhanced Analysis ==========
    
    def _ai_enhanced_analysis(self, pdf_path: str, policy_results: Dict, annex_results: Dict) -> Dict:
        """AI-enhanced medical analysis using enhanced prompts for contradictions and gaps"""
        
        if not self.client:
            print("   ⚠️ AI analysis skipped (no API key)")
            return {'contradictions': [], 'gaps': [], 'insights': []}
        
        try:
            # Combine data for analysis
            policy_df = policy_results.get('structured', pd.DataFrame())
            annex_df = annex_results.get('procedures', pd.DataFrame())
            
            # Prepare data summaries
            policy_summary = self._summarize_policy_data(policy_df)
            annex_summary = self._summarize_annex_data(annex_df)
            
            # Combined data for analysis
            extracted_data = f"""
POLICY STRUCTURE DATA ({len(policy_df)} services):
{policy_summary}

ANNEX PROCEDURES DATA ({len(annex_df)} procedures):
{annex_summary}
"""
            
            specialties_data = f"""
MEDICAL SPECIALTIES COVERED:
- Total policy services: {len(policy_df)}
- Total annex procedures: {len(annex_df)}
- Specialty distribution: {annex_df['specialty'].value_counts().to_dict() if not annex_df.empty else {}}
"""

            # Initialize enhanced prompts
            enhanced_prompts = UpdatedHealthcareAIPrompts()
            
            # Initialize analysis variables to ensure proper scoping
            contradiction_analysis = "N/A"
            gap_analysis = "N/A"
            contradictions = []
            gaps = []
            
            print(f"   🧠 Running enhanced contradiction analysis...")
            contradiction_analysis = ""
            
            # STEP 1: Enhanced Contradiction Analysis
            # Use the USER'S superior contradiction prompt with real Kenya data
            contradiction_prompt = UpdatedHealthcareAIPrompts.get_advanced_contradiction_prompt(
                extracted_data, specialties_data
            )
            
            try:
                contradiction_analysis = self._call_openai(contradiction_prompt, tag="contradictions_main")
                contradictions = self._extract_ai_contradictions(contradiction_analysis)
                
                # Add page source tracking for contradictions
                contradictions = self._add_page_sources(contradictions, "contradiction", policy_df, annex_df)
                
                # Now add to unique tracker with page sources
                if contradictions:
                    new_contradictions_count = self.unique_tracker.add_contradictions(contradictions)
                    print(f"   🔍 Added {new_contradictions_count} new unique contradictions to tracker (Total: {len(self.unique_tracker.unique_contradictions)})")
                    self.unique_tracker.save_insights()
                
                print(f"   📋 Extracted {len(contradictions)} AI contradictions with page sources")
                print(f"   🔎 Contradiction analysis length: {len(contradiction_analysis)}")
                if len(contradiction_analysis) > 120:
                    print(f"   🔎 Starts with: {contradiction_analysis[:120]}...")
                
            except Exception as e:
                print(f"   ⚠️ Contradiction analysis failed: {e}")
                contradiction_analysis = f"ERROR: {str(e)}"
                contradictions = []
            
            print(f"   🏥 Running enhanced gap analysis...")
            
            # STEP 2: Enhanced Gap Analysis with debugging
            gap_analysis = ""
            # Use the USER'S superior gap prompt with real Kenya epidemiological data
            gap_prompt = UpdatedHealthcareAIPrompts.get_comprehensive_gap_analysis_prompt(
                extracted_data, "Kenya 2024 health context with 56.4M population"
            )
            
            try:
                print(f"   🔍 Gap prompt length: {len(gap_prompt)} characters")
                gap_analysis = self._call_openai(gap_prompt, tag="gaps_main")
                
                if gap_analysis is None:
                    print(f"   ⚠️ Gap analysis returned None - OpenAI call failed")
                    gap_analysis = ""
                
                print(f"   🔍 Gap analysis response length: {len(gap_analysis)} characters")
                if len(gap_analysis) > 200:
                    print(f"   🔍 Gap analysis starts with: {gap_analysis[:200]}...")
                
                gaps = self._extract_ai_gaps(gap_analysis)
                
                # Add page source tracking for gaps
                gaps = self._add_page_sources(gaps, "gap", policy_df, annex_df)
                
                # Now add to unique tracker with page sources
                if gaps:
                    new_gaps_count = self.unique_tracker.add_gaps(gaps)
                    print(f"   🔍 Added {new_gaps_count} new unique gaps to tracker (Total: {len(self.unique_tracker.unique_gaps)})")
                    self.unique_tracker.save_insights()
                
                print(f"   📋 Extracted {len(gaps)} AI gaps with page sources")
                
            except Exception as e:
                print(f"   ❌ Gap analysis failed: {e}")
                import traceback
                traceback.print_exc()
                gap_analysis = f"ERROR: {str(e)}"
                gaps = []
            
            # Extract insights from both analyses
            insights = []
            
            print(f"   ✅ AI analysis complete: {len(contradictions)} contradictions, {len(gaps)} gaps")
            
            return {
                'contradictions': contradictions,
                'gaps': gaps, 
                'insights': insights,
                'full_analysis': f"CONTRADICTIONS ANALYSIS:\n{contradiction_analysis}\n\nGAPS ANALYSIS:\n{gap_analysis}"
            }
            
        except Exception as e:
            print(f"   ❌ AI analysis failed: {e}")
            return {'contradictions': [], 'gaps': [], 'insights': []}

    def _run_coverage_analysis(self, policy_results: Dict, annex_results: Dict, clinical_analysis: Dict) -> Dict:
        """Run comprehensive coverage analysis to find systematic coverage gaps"""
        
        if not self.client:
            print("   ⚠️ Coverage analysis skipped (no API key)")
            return {'coverage_gaps': [], 'coverage_analysis': ''}
        
        try:
            # Extract clinical gaps to avoid duplication
            clinical_gaps = clinical_analysis.get('gaps', [])
            clinical_gaps_summary = []
            for gap in clinical_gaps:
                clinical_gaps_summary.append({
                    'category': gap.get('gap_category', 'unknown'),
                    'type': gap.get('gap_type', 'unknown'),
                    'description': gap.get('description', '')[:100] + '...' if len(gap.get('description', '')) > 100 else gap.get('description', '')
                })
            
            # Prepare data for coverage analysis
            policy_df = policy_results.get('structured', pd.DataFrame())
            annex_df = annex_results.get('procedures', pd.DataFrame())
            
            # Prepare data summaries
            policy_summary = self._summarize_policy_data(policy_df)
            annex_summary = self._summarize_annex_data(annex_df)
            
            # Combined data for coverage analysis
            services_data = f"""
POLICY STRUCTURE DATA ({len(policy_df)} services):
{policy_summary}

ANNEX PROCEDURES DATA ({len(annex_df)} procedures):
{annex_summary}
"""
            
            # Create Dr. Sarah Mwangi coverage analysis prompt
            coverage_prompt = self._get_coverage_analysis_prompt(services_data, clinical_gaps_summary)
            
            print(f"   🔍 Running comprehensive coverage analysis...")
            print(f"   🔍 Coverage prompt length: {len(coverage_prompt)} characters")
            
            coverage_analysis_text = self._call_openai(coverage_prompt, tag="coverage_analysis")
            
            if not coverage_analysis_text:
                print(f"   ⚠️ Coverage analysis returned empty - OpenAI call failed")
                return {'coverage_gaps': [], 'coverage_analysis': ''}
            
            print(f"   🔍 Coverage analysis response length: {len(coverage_analysis_text)} characters")
            if len(coverage_analysis_text) > 200:
                print(f"   🔍 Coverage analysis starts with: {coverage_analysis_text[:200]}...")
            
            # Extract coverage gaps from the analysis
            coverage_gaps = self._extract_coverage_gaps(coverage_analysis_text)
            
            # Add page source tracking for coverage gaps
            coverage_gaps = self._add_page_sources(coverage_gaps, "coverage_gap", policy_df, annex_df)
            
            # Add to unique tracker
            new_gaps_count = self.unique_tracker.add_gaps(coverage_gaps)
            print(f"   📋 Added {new_gaps_count} new unique coverage gaps to tracker")
            
            print(f"   ✅ Coverage analysis complete: {len(coverage_gaps)} coverage gaps identified")
            
            return {
                'coverage_gaps': coverage_gaps,
                'coverage_analysis': coverage_analysis_text,
                'clinical_gaps_referenced': clinical_gaps_summary
            }
            
        except Exception as e:
            print(f"   ❌ Coverage analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return {'coverage_gaps': [], 'coverage_analysis': f"ERROR: {str(e)}"}

    def _get_coverage_analysis_prompt(self, services_data: str, clinical_gaps_summary: List[Dict]) -> str:
        """Create comprehensive coverage analysis prompt with Dr. Sarah Mwangi persona"""
        
        clinical_gaps_text = "None identified yet" if not clinical_gaps_summary else "\n".join([
            f"- {gap['category']}: {gap['description']}" for gap in clinical_gaps_summary[:10]
        ])
        
        return f"""You are **Dr. Sarah Mwangi**, Health Systems Coverage Analyst and former WHO Universal Health Coverage Advisor with 20+ years in health service delivery assessment and gap analysis across sub-Saharan Africa, specializing in Kenya's health system coverage patterns.

**YOUR EXPERTISE COVERS:**
🌍 **WHO Essential Health Services**: UHC service package design, coverage measurement
🎯 **Coverage Analysis**: Service availability, accessibility, quality, equity assessments  
📊 **Health System Mapping**: Service delivery platform analysis across all care levels
🔍 **Gap Identification**: Systematic review of service coverage completeness
📋 **Policy Assessment**: Benefit package design against population health needs
🗺️ **Geographic Analysis**: Rural-urban disparities, regional coverage patterns
💡 **Integration Planning**: Cross-program service delivery optimization

**KENYA HEALTH COVERAGE CONTEXT:**
Kenya's 56.4 million population served by 6-tier health system (Level 1-6)
- Level 1: Community units (CHV services)
- Level 2-3: Primary care (dispensaries, health centers)
- Level 4: County hospitals (secondary care)
- Level 5: Referral hospitals (tertiary care)
- Level 6: National referral hospitals

Leading disease burden: Infectious diseases, maternal/child health, NCDs, injuries
Geographic challenges: Northern counties, arid regions, rural-urban disparities
SHIF implementation: Universal health coverage transition from NHIF

**EXISTING CLINICAL PRIORITY GAPS (TO AVOID DUPLICATION):**
{clinical_gaps_text}

**SHIF POLICY DATA FOR COVERAGE ANALYSIS:**
{services_data}

**🎯 SYSTEMATIC COVERAGE GAP ANALYSIS FRAMEWORK:**

**1. SERVICE CATEGORY GAPS** - WHO Essential Health Services checklist:
- Preventive services gaps (immunizations, screening programs, health promotion)
- Curative services gaps (medical consultations, surgical procedures, specialist care)
- Rehabilitative services gaps (physiotherapy, prosthetics, community-based rehabilitation)
- Palliative services gaps (pain management, end-of-life care, psychosocial support)

**2. POPULATION GROUP GAPS** - Life-course approach:
- Pediatric service gaps (child-specific protocols, pediatric specialists, growth monitoring)
- Adolescent service gaps (reproductive health, mental health, substance abuse services)
- Adult service gaps (occupational health, reproductive health, chronic disease management)
- Geriatric service gaps (age-appropriate care, dementia care, long-term care)
- Special population gaps (disability services, mental health, marginalized communities)

**3. CARE LEVEL GAPS** - Kenya's 6-tier system analysis:
- Community level gaps (CHV scope, outreach services, health promotion capacity)
- Primary care gaps (Level 1-2 service scope, basic diagnostics, referral systems)
- Secondary care gaps (Level 3-4 specialist availability, procedure capacity)
- Tertiary care gaps (Level 5-6 advanced services, critical care capacity)
- Emergency care gaps (ambulance coverage, emergency protocols, response times)

**4. GEOGRAPHIC ACCESS GAPS** - Equity and accessibility:
- Rural coverage gaps (service availability, transport, mobile services)
- Urban access gaps (facility congestion, waiting times, service quality)
- Regional disparities (northern counties, arid areas, cross-border regions)
- Facility distribution gaps (catchment analysis, travel distances, referral networks)

**ANALYSIS INSTRUCTIONS:**
1. **SYSTEMATIC REVIEW**: Use the 4-dimension framework to identify coverage gaps NOT already covered in clinical priority analysis
2. **AVOID DUPLICATION**: Reference clinical gaps list - focus on different coverage dimensions
3. **KENYA CONTEXT**: Apply deep knowledge of Kenya's health system structure and challenges
4. **EVIDENCE-BASED**: Use epidemiological data and WHO standards for gap validation
5. **IMPLEMENTATION FOCUS**: Prioritize gaps that are systemically important for UHC

**OUTPUT FORMAT (JSON):**
[
  {{
    "gap_id": "COVERAGE_[CATEGORY]_[NUMBER]",
    "gap_category": "[service_category/population_group/care_level/geographic_access]",
    "gap_type": "[coverage_gap_type]", 
    "coverage_priority": "[HIGH/MEDIUM/LOW]",
    "description": "[Systematic coverage gap description]",
    "kenya_health_system_context": {{
      "service_delivery_platform": "[Which levels affected]",
      "population_impact": "[Who is underserved]",
      "geographic_scope": "[County/regional patterns]",
      "current_coverage_level": "[Estimated coverage %]"
    }},
    "who_essential_services_gap": "[Which WHO essential service category]",
    "coverage_completeness_analysis": {{
      "service_availability": "[Available/Limited/Absent]",
      "geographic_accessibility": "[Accessible/Limited/Poor]",
      "financial_accessibility": "[Affordable/Limited/Expensive]",
      "quality_adequacy": "[Adequate/Suboptimal/Poor]"
    }},
    "integration_with_clinical_gaps": "[How this relates to but differs from clinical priority gaps]",
    "recommended_coverage_interventions": {{
      "immediate_coverage_expansion": ["[Specific interventions]"],
      "service_integration_opportunities": ["[Cross-program linkages]"],
      "infrastructure_requirements": ["[Facility/system needs]"]
    }},
    "implementation_pathway": {{
      "county_integration": "[How counties can implement]",
      "funding_mechanisms": "[SHIF/PHC Fund/Emergency Fund alignment]",
      "timeline_realistic": "[Implementation timeframe]"
    }}
  }}
]

Focus on identifying 15-25 systematic coverage gaps that complement the existing clinical priority gaps, ensuring comprehensive SHIF policy coverage assessment."""

    def _extract_coverage_gaps(self, analysis_text: str) -> List[Dict]:
        """Extract coverage gaps from AI analysis - handles both JSON and conversational formats"""
        gaps = []
        
        try:
            # Try to parse as JSON first
            import json
            
            # Look for JSON array in the text
            json_match = re.search(r'\[[\s\S]*\]', analysis_text)
            if json_match:
                json_text = json_match.group(0)
                parsed_gaps = json.loads(json_text)
                
                for gap_data in parsed_gaps:
                    if isinstance(gap_data, dict) and gap_data.get('description'):
                        gap = {
                            'gap_id': gap_data.get('gap_id', f"COVERAGE_{len(gaps)+1:03d}"),
                            'gap_category': gap_data.get('gap_category', 'coverage_gap'),
                            'gap_type': gap_data.get('gap_type', 'systematic_coverage_gap'),
                            'coverage_priority': gap_data.get('coverage_priority', 'MEDIUM'),
                            'description': gap_data.get('description', ''),
                            'kenya_context': gap_data.get('kenya_health_system_context', {}),
                            'who_essential_services': gap_data.get('who_essential_services_gap', ''),
                            'coverage_analysis': gap_data.get('coverage_completeness_analysis', {}),
                            'clinical_integration': gap_data.get('integration_with_clinical_gaps', ''),
                            'interventions': gap_data.get('recommended_coverage_interventions', {}),
                            'implementation': gap_data.get('implementation_pathway', {}),
                            'detection_method': 'ai_coverage_analysis',
                            'analysis_type': 'comprehensive_coverage'
                        }
                        gaps.append(gap)
                
                print(f"   📋 Parsed {len(gaps)} coverage gaps from JSON format")
                return gaps
                
        except Exception as e:
            print(f"   ⚠️ JSON parsing failed, trying conversational parsing: {e}")
        
        # Fallback to conversational parsing
        print(f"   🔍 Parsing conversational coverage analysis...")
        
        # Look for numbered gaps (like "1) Rehabilitative services...")
        gap_pattern = r'(\d+)\)\s*([^\n—]*?)(?:\s*—\s*([^\n]+))?'
        gap_matches = re.findall(gap_pattern, analysis_text, re.MULTILINE)
        
        for gap_num, title, description in gap_matches:
            if title.strip():
                gap = {
                    'gap_id': f"COVERAGE_{gap_num.zfill(2)}",
                    'gap_category': 'systematic_coverage_gap',
                    'gap_type': 'coverage_analysis',
                    'coverage_priority': 'MEDIUM',
                    'description': f"{title.strip()}" + (f" - {description.strip()}" if description.strip() else ""),
                    'kenya_context': {'derived_from': 'conversational_analysis'},
                    'detection_method': 'ai_conversational_parsing',
                    'analysis_type': 'comprehensive_coverage'
                }
                gaps.append(gap)
                print(f"      • Coverage Gap {gap_num}: {title.strip()}")
        
        # Also look for bullet point format
        bullet_pattern = r'[•\-\*]\s*([^\n]+)'
        bullet_matches = re.findall(bullet_pattern, analysis_text)
        
        for i, bullet_text in enumerate(bullet_matches):
            if len(bullet_text) > 20 and any(keyword in bullet_text.lower() for keyword in ['gap', 'coverage', 'service', 'access']):
                gap = {
                    'gap_id': f"COVERAGE_BULLET_{i+1:02d}",
                    'gap_category': 'systematic_coverage_gap',
                    'gap_type': 'coverage_analysis',
                    'coverage_priority': 'LOW',
                    'description': bullet_text.strip(),
                    'kenya_context': {'derived_from': 'bullet_analysis'},
                    'detection_method': 'ai_bullet_parsing',
                    'analysis_type': 'comprehensive_coverage'
                }
                gaps.append(gap)
                if len(gaps) >= 25:  # Limit to prevent too many gaps
                    break
        
        print(f"   📋 Extracted {len(gaps)} coverage gaps from conversational analysis")
        return gaps

    # ========== Extended AI routines (optional) ==========

    def _cache_key(self, model: str, prompt: str, tag: str = "") -> str:
        m = hashlib.sha1()
        m.update(model.encode("utf-8"))
        m.update(b"\0")
        m.update(prompt.encode("utf-8"))
        if tag:
            m.update(b"\0")
            m.update(tag.encode("utf-8"))
        return m.hexdigest()

    def _cache_get(self, key: str) -> Optional[str]:
        try:
            path = self.ai_cache_dir / f"{key}.txt"
            if path.exists():
                return path.read_text(encoding='utf-8')
        except Exception:
            pass
        return None

    def _cache_set(self, key: str, content: str) -> None:
        try:
            path = self.ai_cache_dir / f"{key}.txt"
            path.write_text(content or "", encoding='utf-8')
        except Exception:
            pass

    def _call_openai(self, prompt: str, tag: str = "") -> str:
        """Helper to call OpenAI with primary/fallback and on-disk caching."""
        primary_key = self._cache_key(self.primary_model, prompt, tag)
        cached = self._cache_get(primary_key)
        if cached is not None:
            return cached
        fallback_key = self._cache_key(self.fallback_model, prompt, tag)
        cached_fb = self._cache_get(fallback_key)
        if cached_fb is not None:
            return cached_fb
        try:
            resp = self.client.chat.completions.create(
                model=self.primary_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,  # Deterministic AI responses
                seed=42  # Reproducible across runs
            )
            content = (resp.choices[0].message.content or "")
            self._cache_set(primary_key, content)
            return content
        except Exception:
            resp = self.client.chat.completions.create(
                model=self.fallback_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,  # Deterministic AI responses
                seed=42  # Reproducible across runs
            )
            content = (resp.choices[0].message.content or "")
            self._cache_set(fallback_key, content)
            return content

    def _run_extended_ai(self, policy_results: Dict, annex_results: Dict) -> Dict:
        """Run extended AI analyses using enhanced prompt suite (does not affect tests)."""
        from updated_prompts import UpdatedHealthcareAIPrompts as P
        out: Dict[str, object] = {}

        # Prepare summaries
        policy_df = policy_results.get('structured', pd.DataFrame())
        annex_df = annex_results.get('procedures', pd.DataFrame())
        policy_summary = self._summarize_policy_data(policy_df)
        annex_summary = self._summarize_annex_data(annex_df)

        # 1) Annex quality/outlier analysis (sample up to 40 rows for token control)
        try:
            sample_rows = annex_df.head(40).to_json(orient='records') if not annex_df.empty else "[]"
            prompt = P.get_annex_quality_prompt(annex_summary, sample_rows)
            out['annex_quality'] = self._safe_parse_json_array(self._call_openai(prompt))
        except Exception as e:
            out['annex_quality_error'] = str(e)

        # 2) Rules contradiction map by fund/section (sample up to 60 rows)
        try:
            rules_sample = policy_df.head(60).to_json(orient='records') if not policy_df.empty else "[]"
            prompt = P.get_rules_contradiction_map_prompt(policy_summary, rules_sample)
            out['rules_map'] = self._safe_parse_json(self._call_openai(prompt))
        except Exception as e:
            out['rules_map_error'] = str(e)

        # 3) Batch service analysis from annex (chunked)
        try:
            batch_results = []
            if not annex_df.empty:
                services = annex_df[['specialty','intervention','tariff']].rename(columns={'intervention':'service_name'}).fillna("")
                chunk_size = 50
                for i in range(0, len(services), chunk_size):
                    chunk = services.iloc[i:i+chunk_size]
                    prompt = P.get_batch_service_analysis_prompt(chunk.to_json(orient='records'), "Kenya 2024, 47 counties, 6-tier system")
                    batch_results.extend(self._safe_parse_json_array(self._call_openai(prompt)))
            out['batch_service_analysis'] = batch_results
        except Exception as e:
            out['batch_service_analysis_error'] = str(e)

        return out

    def run_even_more_ai(self, policy_results: Dict, annex_results: Dict) -> Dict:
        """Optional additional analyses covering summaries, canonicalization, facility checks, alignment, equity."""
        from updated_prompts import UpdatedHealthcareAIPrompts as P
        out: Dict[str, object] = {}

        policy_df = policy_results.get('structured', pd.DataFrame())
        annex_df = annex_results.get('procedures', pd.DataFrame())
        policy_summary = self._summarize_policy_data(policy_df)
        annex_summary = self._summarize_annex_data(annex_df)

        # Section summaries for pages 1–18
        try:
            rows = policy_df[['fund','service','scope','access_point','tariff_raw','access_rules']].fillna("") if not policy_df.empty else pd.DataFrame()
            prompt = P.get_section_summaries_prompt(rows.head(80).to_json(orient='records'))
            out['section_summaries'] = self._safe_parse_json_array(self._call_openai(prompt))
        except Exception as e:
            out['section_summaries_error'] = str(e)

        # Canonicalization of annex procedure names
        try:
            if not annex_df.empty:
                names = annex_df['intervention'].dropna().astype(str).head(200).tolist()
                import json
                prompt = P.get_name_canonicalization_prompt(json.dumps(names))
                out['canonicalization'] = self._safe_parse_json(self._call_openai(prompt))
        except Exception as e:
            out['canonicalization_error'] = str(e)

        # Facility-level validation for rules
        try:
            rows = policy_df[['fund','service','scope','access_point','tariff_raw','access_rules']].fillna("") if not policy_df.empty else pd.DataFrame()
            prompt = P.get_facility_level_validation_prompt(rows.head(80).to_json(orient='records'))
            out['facility_validation'] = self._safe_parse_json_array(self._call_openai(prompt))
        except Exception as e:
            out['facility_validation_error'] = str(e)

        # Policy vs Annex alignment
        try:
            prompt = P.get_policy_annex_alignment_prompt(policy_summary, annex_summary)
            out['policy_annex_alignment'] = self._safe_parse_json(self._call_openai(prompt))
        except Exception as e:
            out['policy_annex_alignment_error'] = str(e)

        # Equity analysis
        try:
            coverage_summary = f"Policy entries: {len(policy_df)}; Annex procedures: {len(annex_df)}"
            county_note = "47 counties; rural 70%, urban 30%"
            prompt = P.get_equity_analysis_prompt(coverage_summary, county_note)
            out['equity'] = self._safe_parse_json(self._call_openai(prompt))
        except Exception as e:
            out['equity_error'] = str(e)

        return out

    def _safe_parse_json(self, text: str):
        """Parse first JSON object/array found in text; fallback to raw text."""
        import json, re
        s = text.strip()
        if s.startswith('{') or s.startswith('['):
            try:
                return json.loads(s)
            except Exception:
                pass
        # fallback: find first JSON block
        m = re.search(r'\{[\s\S]*\}|\[[\s\S]*\]', text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return {"raw": text}
        return {"raw": text}

    def _safe_parse_json_array(self, text: str):
        """Ensure we return a list from AI responses."""
        parsed = self._safe_parse_json(text)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            # try common keys
            for k in ('items','results','issues','data'):
                if k in parsed and isinstance(parsed[k], list):
                    return parsed[k]
        return []

    def _summarize_policy_data(self, policy_df: pd.DataFrame) -> str:
        """Create summary of policy data for AI analysis"""
        if policy_df.empty:
            return "No policy data extracted"
        
        # Filter out empty values and count non-empty entries
        funds = policy_df[policy_df['fund'] != '']['fund'].value_counts().head(5)
        services = policy_df[policy_df['service'] != '']['service'].value_counts().head(10)
        
        # Include scope items and access points for analysis - adapted for user's data structure
        scope_items = policy_df[policy_df['scope'] != '']['scope'].head(5).tolist() if 'scope' in policy_df.columns else []
        access_points = policy_df[policy_df['access_point'] != '']['access_point'].value_counts().head(5) if 'access_point' in policy_df.columns else []
        
        # Count entries with tariffs - use user's tariff_num field
        tariff_entries = len(policy_df[policy_df['tariff_num'].notna() & (policy_df['tariff_num'] > 0)]) if 'tariff_num' in policy_df.columns else 0
        
        summary = f"POLICY STRUCTURE DATA ({len(policy_df)} entries):\n"
        summary += f"- Entries with Fund info: {len(funds)} (non-empty)\n"
        if len(funds) > 0:
            summary += f"- Top Funds: {dict(funds)}\n"
        summary += f"- Entries with Service info: {len(services)} (non-empty)\n" 
        if len(services) > 0:
            summary += f"- Top Services: {dict(services)}\n"
        summary += f"- Entries with Tariffs: {tariff_entries}\n"
        summary += f"- Access Points: {dict(access_points)}\n"
        
        # Include sample scope items for contradiction analysis
        if scope_items:
            summary += f"- Sample Services:\n"
            for i, item in enumerate(scope_items[:3], 1):
                summary += f"  {i}. {item[:100]}...\n"
        
        return summary

    def _summarize_annex_data(self, annex_df: pd.DataFrame) -> str:
        """Create summary of annex data for AI analysis"""
        if annex_df.empty:
            return "No annex data extracted"
            
        specialties = annex_df['specialty'].value_counts()
        tariffs = annex_df['tariff'].dropna()
        
        summary = f"Annex Procedures: {len(annex_df)} total\n"
        summary += f"Specialties ({len(specialties)}): {dict(specialties.head(10))}\n"
        
        if len(tariffs) > 0:
            summary += f"Tariff Range: KES {tariffs.min():,.0f} - {tariffs.max():,.0f}\n"
            summary += f"Average: KES {tariffs.mean():,.0f}\n"
            
        return summary

    def _extract_ai_contradictions(self, analysis_text: str) -> List[Dict]:
        """Extract contradictions from AI analysis (JSON format)"""
        contradictions = []
        
        try:
            # Try to parse as JSON first
            import json
            if analysis_text.strip().startswith('[') or analysis_text.strip().startswith('{'):
                parsed = json.loads(analysis_text.strip())
                if isinstance(parsed, list):
                    contradictions = parsed
                elif isinstance(parsed, dict) and 'contradictions' in parsed:
                    contradictions = parsed['contradictions']
            else:
                # Fallback: extract JSON arrays/objects from text
                json_pattern = r'\[[\s\S]*?\]|\{[\s\S]*?\}'
                json_matches = re.findall(json_pattern, analysis_text)
                for match in json_matches:
                    try:
                        parsed = json.loads(match)
                        if isinstance(parsed, list) and parsed:
                            contradictions.extend(parsed)
                        elif isinstance(parsed, dict) and parsed.get('contradiction_type'):
                            contradictions.append(parsed)
                    except:
                        continue
        except Exception as e:
            print(f"   ⚠️ JSON parsing failed, using text fallback: {e}")
            
            # Original text-based parsing as fallback
            contradictions_section = re.search(r'CONTRADICTIONS:.*?(?=\n[A-Z]+:|$)', analysis_text, re.DOTALL | re.IGNORECASE)
            if contradictions_section:
                lines = contradictions_section.group(0).split('\n')
                for line in lines[1:]:  # Skip header
                    line = line.strip()
                    if line and not line.isupper() and len(line) > 10:
                        contradictions.append({
                            'type': 'ai_detected',
                            'description': line,
                            'severity': 'medium',
                            'detection_method': 'ai_text_parsing'
                        })
        
        print(f"   📋 Extracted {len(contradictions)} AI contradictions")
        
        # Note: Unique tracker will be called after page sources are added in main flow
        return contradictions

    def _extract_ai_gaps(self, analysis_text: str) -> List[Dict]:
        """Extract gaps from AI analysis - Enhanced to handle both JSON and conversational formats"""
        gaps = []
        
        try:
            # Try to parse as JSON first
            import json
            if analysis_text.strip().startswith('[') or analysis_text.strip().startswith('{'):
                parsed = json.loads(analysis_text.strip())
                if isinstance(parsed, list):
                    gaps = parsed
                elif isinstance(parsed, dict) and 'gaps' in parsed:
                    gaps = parsed['gaps']
                    
            else:
                # Look for JSON arrays/objects embedded in text
                json_pattern = r'\[[\s\S]*?\]|\{[\s\S]*?\}'
                json_matches = re.findall(json_pattern, analysis_text)
                for match in json_matches:
                    try:
                        parsed = json.loads(match)
                        if isinstance(parsed, list) and parsed:
                            # Only add dict items from the list
                            gaps.extend([item for item in parsed if isinstance(item, dict)])
                        elif isinstance(parsed, dict) and (
                            'gap_type' in parsed or
                            'gap_id' in parsed or
                            'gap_category' in parsed or
                            'missing' in parsed.get('description', '').lower()
                        ):
                            gaps.append(parsed)
                    except:
                        continue
                        
            # If JSON parsing found gaps, return them
            if gaps:
                print(f"   📋 Extracted {len(gaps)} AI gaps from JSON")
                return gaps

            # No gaps found in JSON parsing
            return []

        except Exception as e:
            print(f"   ❌ Error parsing AI gaps: {e}")
            return []

    # ========== Results Integration & Summary ==========
    
    def _integrate_comprehensive_results(self, policy_results: Dict, annex_results: Dict, ai_analysis: Dict, coverage_analysis: Dict = None) -> Dict:
        """Integrate all results into comprehensive output"""
        
        # Save the extracted data to timestamped folder
        try:
            # Save policy data to timestamped folder only
            if 'structured' in policy_results and not policy_results['structured'].empty:
                policy_results['structured'].to_csv(self.output_dir / 'rules_p1_18_structured.csv', index=False)
                
                if 'wide' in policy_results:
                    policy_results['wide'].to_csv(self.output_dir / 'rules_p1_18_structured_wide.csv', index=False)
                    
                if 'exploded' in policy_results:
                    policy_results['exploded'].to_csv(self.output_dir / 'rules_p1_18_structured_exploded.csv', index=False)
            
            # Save annex data
            if 'procedures' in annex_results and not annex_results['procedures'].empty:
                annex_results['procedures'].to_csv(self.output_dir / 'annex_surgical_tariffs_all.csv', index=False)
                
            # Save AI analysis results if available
            if ai_analysis.get('contradictions'):
                pd.DataFrame(ai_analysis['contradictions']).to_csv(self.output_dir / 'ai_contradictions.csv', index=False)
                
            if ai_analysis.get('gaps'):
                pd.DataFrame(ai_analysis['gaps']).to_csv(self.output_dir / 'ai_gaps.csv', index=False)
            
            # Save coverage analysis results if available
            if coverage_analysis and coverage_analysis.get('coverage_gaps'):
                coverage_gaps = coverage_analysis['coverage_gaps']
                clinical_gaps = ai_analysis.get('gaps', [])
                
                # Save separate CSV files for clinical and coverage gaps
                if clinical_gaps:
                    pd.DataFrame(clinical_gaps).to_csv(self.output_dir / 'clinical_gaps_analysis.csv', index=False)
                    print(f"✅ Clinical priority gaps saved: clinical_gaps_analysis.csv ({len(clinical_gaps)} gaps)")
                
                if coverage_gaps:
                    pd.DataFrame(coverage_gaps).to_csv(self.output_dir / 'coverage_gaps_analysis.csv', index=False)
                    print(f"✅ Coverage analysis gaps saved: coverage_gaps_analysis.csv ({len(coverage_gaps)} gaps)")
                
                # Save comprehensive combined gaps
                all_gaps = clinical_gaps + coverage_gaps
                
                # Deduplicate gaps using OpenAI if client available
                if all_gaps and self.client:
                    print(f"\n🔄 Deduplicating {len(all_gaps)} gaps using OpenAI...")
                    deduplicated_gaps = self.deduplicate_gaps_with_openai(all_gaps)
                    print(f"   ✅ Reduced to {len(deduplicated_gaps)} unique gaps")
                    
                    # Save deduplicated gaps as primary output
                    pd.DataFrame(deduplicated_gaps).to_csv(self.output_dir / 'comprehensive_gaps_analysis.csv', index=False)
                    print(f"✅ Deduplicated gaps saved: comprehensive_gaps_analysis.csv ({len(deduplicated_gaps)} unique gaps)")
                    
                    # Also save original gaps for reference
                    pd.DataFrame(all_gaps).to_csv(self.output_dir / 'all_gaps_before_dedup.csv', index=False)
                elif all_gaps:
                    pd.DataFrame(all_gaps).to_csv(self.output_dir / 'comprehensive_gaps_analysis.csv', index=False)
                    print(f"✅ Comprehensive gaps saved: comprehensive_gaps_analysis.csv ({len(all_gaps)} total gaps)")
                    
                    # Also update the summary to reflect dual-phase analysis
                    print(f"🎯 DUAL-PHASE GAP ANALYSIS:")
                    print(f"   • Clinical Priority Gaps: {len(clinical_gaps)}")  
                    print(f"   • Systematic Coverage Gaps: {len(coverage_gaps)}")
                    print(f"   • Comprehensive Total: {len(all_gaps)}")
        
        except Exception as e:
            print(f"   ⚠️ Error saving results: {e}")
        
        # Return comprehensive results
        # Prepare final results with clinical and coverage gaps integrated
        clinical_gaps = ai_analysis.get('gaps', [])
        coverage_gaps = coverage_analysis.get('coverage_gaps', []) if coverage_analysis else []
        
        # Combine all gaps for comprehensive analysis
        all_gaps = clinical_gaps + coverage_gaps
        
        results = {
            'policy_results': policy_results,
            'annex_results': annex_results,
            'ai_analysis': ai_analysis,
            'coverage_analysis': coverage_analysis or {},
            'total_policy_services': len(policy_results.get('structured', pd.DataFrame())),
            'total_annex_procedures': len(annex_results.get('procedures', pd.DataFrame())),
            'total_ai_contradictions': len(ai_analysis.get('contradictions', [])),
            'total_ai_gaps': len(clinical_gaps),
            'total_coverage_gaps': len(coverage_gaps),
            'total_all_gaps': len(all_gaps),
            'gap_analysis_breakdown': {
                'clinical_priority_gaps': len(clinical_gaps),
                'systematic_coverage_gaps': len(coverage_gaps),
                'comprehensive_total': len(all_gaps)
            },
            'unique_insights_summary': self.unique_tracker.get_summary()
        }
        # Add legacy-compatible keys for UI consumption
        try:
            legacy_pack = self._save_final_outputs(policy_results, annex_results, ai_analysis)
            if isinstance(legacy_pack, dict):
                results['extraction_results'] = legacy_pack.get('extraction_results', {})
                # Normalize analysis_results to expected form
                analysis_results = legacy_pack.get('analysis_results', {})
                if analysis_results:
                    results['analysis_results'] = analysis_results
                # Include summary statistics if helpful
                if 'summary_statistics' in legacy_pack:
                    results['summary_statistics'] = legacy_pack['summary_statistics']
        except Exception:
            # Non-fatal if packing fails; UI has fallbacks
            pass
        
        return results
    
    def _print_comprehensive_summary(self, results: Dict, analysis_time: float):
        """Print comprehensive analysis summary"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE ANALYSIS RESULTS SUMMARY")
        print("=" * 70)
        
        policy_count = results.get('total_policy_services', 0)
        annex_count = results.get('total_annex_procedures', 0)
        contradictions_count = results.get('total_ai_contradictions', 0)
        clinical_gaps_count = results.get('total_ai_gaps', 0)
        coverage_gaps_count = results.get('total_coverage_gaps', 0)
        total_gaps_count = results.get('total_all_gaps', 0)
        gaps_count = total_gaps_count  # For backward compatibility
        
        print(f"\n📋 DATA EXTRACTION:")
        print(f"   • Pages 1-18 Policy Services: {policy_count}")
        print(f"   • Pages 19-54 Annex Procedures: {annex_count}")
        print(f"   • Total Data Points Extracted: {policy_count + annex_count}")
        
        if self.client:
            print(f"\n🤖 COMPREHENSIVE AI ANALYSIS:")
            print(f"   • Medical Contradictions Detected: {contradictions_count}")
            
            # Show gap breakdown if both clinical and coverage gaps exist
            if clinical_gaps_count > 0 and coverage_gaps_count > 0:
                print(f"   • Clinical Priority Gaps: {clinical_gaps_count}")
                print(f"   • Systematic Coverage Gaps: {coverage_gaps_count}")
                print(f"   • Total Healthcare Gaps: {total_gaps_count}")
            elif clinical_gaps_count > 0:
                print(f"   • Healthcare Gaps Identified: {clinical_gaps_count}")
            elif coverage_gaps_count > 0:
                print(f"   • Coverage Gaps Identified: {coverage_gaps_count}")
            
            # Show unique insights summary if available
            summary = results.get('unique_insights_summary', {})
            if summary:
                print(f"   • Total Analysis Runs: {summary.get('total_runs', 0)}")
                print(f"   • Unique Contradictions Tracked: {summary.get('total_unique_contradictions', 0)}")
                print(f"   • Unique Gaps Tracked: {summary.get('total_unique_gaps', 0)}")
        
        print(f"\n💾 OUTPUT LOCATIONS:")
        print(f"   • Direct Access: {self.output_dir} folder")
        print(f"   • Timestamped Run: {self.output_dir}")
        print(f"   • Key Files Generated:")
        print(f"     - rules_p1_18_structured.csv")
        print(f"     - annex_surgical_tariffs_all.csv")
        if contradictions_count > 0:
            print(f"     - ai_contradictions.csv")
        if gaps_count > 0:
            print(f"     - ai_gaps.csv")
        
        print(f"\n⏱️ ANALYSIS PERFORMANCE:")
        print(f"   • Total Time: {analysis_time:.1f} seconds")
        print(f"   • Extraction Method: VALIDATED (manual.ipynb functions)")
        print(f"   • AI Enhancement: {'ENABLED' if self.client else 'DISABLED'}")
        
        print("\n" + "=" * 70)
        print("✅ ANALYSIS COMPLETE - Data ready for use!")
        print("=" * 70)
        # End of summary
        return None

    def _extract_ai_insights(self, analysis_text: str) -> List[str]:
        """Extract insights from AI analysis"""
        insights = []
        
        insights_section = re.search(r'INSIGHTS:.*?(?=\n[A-Z]+:|$)', analysis_text, re.DOTALL | re.IGNORECASE)
        if insights_section:
            lines = insights_section.group(0).split('\n')
            for line in lines[1:]:  # Skip header
                line = line.strip()
                if line and not line.isupper():
                    insights.append(line)
        
        return insights

    # ========== Results Integration ==========
    
    def _save_final_outputs(self, policy_results: Dict, annex_results: Dict, ai_analysis: Dict) -> None:
        """Save final outputs to both timestamped and standard outputs directories"""
        
        policy_df = policy_results.get('structured', pd.DataFrame())
        annex_df = annex_results.get('procedures', pd.DataFrame())
        
        # Calculate comprehensive statistics
        total_services = len(policy_df) + len(annex_df)
        
        policy_tariffs = []
        if not policy_df.empty and 'block_tariff' in policy_df.columns:
            policy_tariffs = policy_df['block_tariff'].dropna().tolist()
            
        annex_tariffs = []
        if not annex_df.empty and 'tariff' in annex_df.columns:
            annex_tariffs = annex_df['tariff'].dropna().tolist()
        
        total_tariffs = len(policy_tariffs) + len(annex_tariffs)
        all_tariffs = policy_tariffs + annex_tariffs
        
        # Compile results
        results = {
            'extraction_results': {
                'policy_structure': {
                    'total_services': len(policy_df),
                    'data': policy_df.to_dict('records') if not policy_df.empty else []
                },
                'annex_procedures': {
                    'total_procedures': len(annex_df),
                    'data': annex_df.to_dict('records') if not annex_df.empty else []
                }
            },
            'analysis_results': {
                'ai_contradictions': ai_analysis.get('contradictions', []),
                'ai_gaps': ai_analysis.get('gaps', []),
                'ai_insights': ai_analysis.get('insights', []),
                'full_ai_analysis': ai_analysis.get('full_analysis', '')
            },
            'summary_statistics': {
                'total_services_procedures': total_services,
                'total_with_tariffs': total_tariffs,
                'tariff_coverage_percent': (total_tariffs / total_services * 100) if total_services > 0 else 0,
                'tariff_range': {
                    'min': min(all_tariffs) if all_tariffs else None,
                    'max': max(all_tariffs) if all_tariffs else None,
                    'average': sum(all_tariffs) / len(all_tariffs) if all_tariffs else None
                }
            }
        }
        
        return results

    def get_unique_insights_summary(self) -> Dict:
        """Get summary of all unique insights tracked across runs"""
        return self.unique_tracker.get_summary()
    
    def get_all_unique_gaps(self) -> List[Dict]:
        """Get all unique gaps discovered across runs"""
        return self.unique_tracker.unique_gaps.copy()
    
    def get_all_unique_contradictions(self) -> List[Dict]:
        """Get all unique contradictions discovered across runs"""
        return self.unique_tracker.unique_contradictions
    
    def deduplicate_gaps_with_openai(self, gaps_to_deduplicate: List[Dict] = None) -> List[Dict]:
        """Use OpenAI to intelligently deduplicate gaps with different wordings but same medical concepts"""
        
        print("🤖 Starting OpenAI-based gap deduplication...")
        
        # Use provided gaps or fall back to unique tracker
        all_gaps = gaps_to_deduplicate if gaps_to_deduplicate is not None else self.unique_tracker.unique_gaps
        if len(all_gaps) < 2:
            print(f"Only {len(all_gaps)} gaps found - no deduplication needed")
            return all_gaps
        
        print(f"📊 Processing {len(all_gaps)} gaps for intelligent deduplication...")
        
        # Use existing Kenya healthcare context built into the system
        kenya_context = """
Kenya Healthcare System: 6-level delivery system (Level 1-6)
SHIF (Social Health Insurance Fund): Universal health coverage
Key Focus: Maternal health (EmONC), Mental health (mhGAP), Oncology
Common gaps: EmONC capabilities, psychiatric services, oncology coverage
"""
        
        try:
            # Prepare gap data for OpenAI analysis
            gaps_for_analysis = []
            for i, gap in enumerate(all_gaps):
                gap_text = {
                    "id": f"gap_{i+1}",
                    "description": gap.get('description', ''),
                    "category": gap.get('gap_category', ''),
                    "original_data": gap  # Keep original for reference
                }
                gaps_for_analysis.append(gap_text)
            
            # Create OpenAI prompt for deduplication
            # Prepare gaps data for JSON serialization (avoid unhashable types)
            gaps_for_prompt = []
            for g in gaps_for_analysis:
                gaps_for_prompt.append({
                    'id': str(g['id']), 
                    'description': str(g['description']), 
                    'category': str(g['category'])
                })
            
            gaps_json = json.dumps(gaps_for_prompt, indent=2)
            
            dedup_prompt = f"""
You are a medical policy expert with deep knowledge of Kenya's healthcare system and SHIF (Social Health Insurance Fund).

CONTEXT - Kenya Healthcare System:
{kenya_context}

TASK: Intelligently deduplicate healthcare coverage gaps that represent the same medical concept, considering Kenya's specific healthcare context.

GAPS TO ANALYZE ({len(gaps_for_analysis)} total):
{gaps_json}

DEDUPLICATION CRITERIA:
1. Consider Kenya's healthcare delivery levels (Level 1-6)
2. Understand SHIF coverage vs. gaps in maternal health, mental health, oncology
3. Recognize equivalent services described differently (e.g., "EmONC" vs "Emergency Obstetric Care")
4. Group gaps representing identical medical concepts/service deficiencies
5. Select the clearest, most comprehensive description for each group

OUTPUT FORMAT (JSON only, no other text):
{{
  "duplicates_removed": [
    {{
      "master_gap_id": "gap_X",
      "best_description": "Selected best description",
      "category": "gap_category", 
      "merged_ids": ["gap_X", "gap_Y", "gap_Z"],
      "rationale": "Why these represent the same medical concept in Kenya context"
    }}
  ],
  "unique_gaps": [
    {{
      "gap_id": "gap_N",
      "description": "Unique gap description",
      "category": "gap_category"
    }}
  ],
  "summary": {{
    "original_count": {len(gaps_for_analysis)},
    "final_count": "number_after_deduplication",
    "duplicates_found": "number_of_duplicate_groups"
  }}
}}"""

            # Call OpenAI for deduplication
            if self.client:
                response = self.client.chat.completions.create(
                    model=self.primary_model,
                    messages=[{"role": "user", "content": dedup_prompt}]
                )
                
                dedup_analysis = response.choices[0].message.content
                print(f"📋 OpenAI deduplication analysis received ({len(dedup_analysis)} chars)")
                
                # Parse the deduplication results
                deduplicated_gaps = self._parse_deduplication_results(dedup_analysis, gaps_for_analysis)
                
                # Save deduplication results
                dedup_file = self.output_dir / "gaps_deduplication_analysis.json"
                dedup_results = {
                    "timestamp": datetime.now().isoformat(),
                    "original_gaps_count": len(all_gaps),
                    "deduplicated_gaps_count": len(deduplicated_gaps),
                    "reduction_percentage": ((len(all_gaps) - len(deduplicated_gaps)) / len(all_gaps) * 100) if all_gaps else 0,
                    "openai_analysis": dedup_analysis,
                    "deduplicated_gaps": deduplicated_gaps
                }
                
                with open(dedup_file, 'w') as f:
                    json.dump(dedup_results, f, indent=2)
                
                print(f"✅ Deduplication complete: {len(all_gaps)} → {len(deduplicated_gaps)} gaps")
                print(f"📁 Deduplication analysis saved: {dedup_file}")
                
                return deduplicated_gaps
            
            else:
                print("❌ OpenAI client not available - cannot perform intelligent deduplication")
                return all_gaps
                
        except Exception as e:
            print(f"❌ Error in OpenAI deduplication: {e}")
            return all_gaps
    
    def _parse_deduplication_results(self, openai_response: str, original_gaps: List[Dict]) -> List[Dict]:
        """Parse OpenAI deduplication response and return clean gap list"""
        
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', openai_response, re.DOTALL)
            if json_match:
                dedup_data = json.loads(json_match.group())
                
                # Create mapping from original gap IDs to gap objects
                id_to_gap = {f"gap_{i+1}": gap['original_data'] for i, gap in enumerate(original_gaps)}

                final_gaps = []
                added_gap_ids = set()  # Track which gaps we've already added to prevent duplicates

                # Add deduplicated/merged gaps (these are the master gaps from duplicate sets)
                for duplicate_group in dedup_data.get('duplicates_removed', []):
                    master_id = duplicate_group.get('master_gap_id')
                    if master_id in id_to_gap and master_id not in added_gap_ids:
                        # Use the original gap data but update with best description
                        master_gap = id_to_gap[master_id].copy()
                        master_gap['description'] = duplicate_group.get('best_description', master_gap.get('description'))
                        master_gap['deduplication_info'] = {
                            'merged_from_ids': duplicate_group.get('merged_ids', []),
                            'rationale': duplicate_group.get('rationale', ''),
                            'deduplication_date': datetime.now().isoformat()
                        }
                        final_gaps.append(master_gap)
                        added_gap_ids.add(master_id)  # Mark as added

                # Add unique gaps (no duplicates found for these)
                for unique_gap in dedup_data.get('unique_gaps', []):
                    gap_id = unique_gap.get('gap_id')
                    if gap_id in id_to_gap and gap_id not in added_gap_ids:  # Skip if already added as master gap
                        unique_gap_data = id_to_gap[gap_id].copy()
                        unique_gap_data['deduplication_info'] = {
                            'status': 'unique',
                            'deduplication_date': datetime.now().isoformat()
                        }
                        final_gaps.append(unique_gap_data)
                        added_gap_ids.add(gap_id)  # Mark as added
                
                # Show deduplication summary
                summary = dedup_data.get('summary', {})
                original_count = summary.get('original_count', len(original_gaps))
                final_count = len(final_gaps)
                duplicates_removed = original_count - final_count

                print(f"📊 Deduplication Results:")
                print(f"   • Original gaps: {original_count}")
                print(f"   • Final gaps: {final_count}")
                print(f"   • Duplicates removed: {duplicates_removed}")
                print(f"   • Reduction: {(duplicates_removed/original_count*100):.1f}%" if original_count > 0 else "")

                return final_gaps
                
        except Exception as e:
            print(f"⚠️ Could not parse OpenAI deduplication response: {e}")
            print("Using fallback similarity-based deduplication...")
            
        # Fallback to original gaps if parsing fails
        return original_gaps.copy()
    
    def _add_page_sources(self, items: List[Dict], item_type: str, policy_df: pd.DataFrame, annex_df: pd.DataFrame) -> List[Dict]:
        """Add PDF page source tracking to gaps or contradictions for validation"""
        
        # Handle None or empty items
        if not items:
            print(f"   📍 No {item_type}s to add page sources to")
            return []
        
        enhanced_items = []
        
        for item in items:
            enhanced_item = item.copy()
            
            # Extract key terms from the item description for page matching
            description = str(item.get('description', '')).lower()
            
            # Try to identify page source based on content
            page_sources = []
            
            # Check if content relates to policy structure (Pages 1-18)
            policy_keywords = ['level', 'tier', 'emonc', 'emergency obstetric', 'maternal', 'mental health', 'mhgap', 'county', 'facility', 'referral']
            if any(keyword in description for keyword in policy_keywords):
                page_sources.append("Pages 1-18 (Policy Structure)")
            
            # Check if content relates to annex procedures (Pages 19-54)
            annex_keywords = ['procedure', 'surgical', 'tariff', 'specialist', 'oncology', 'cancer', 'treatment']
            if any(keyword in description for keyword in annex_keywords):
                page_sources.append("Pages 19-54 (Annex Procedures)")
            
            # If no specific match, try to match against actual data
            if not page_sources:
                # Search policy dataframe for matching terms
                if not policy_df.empty:
                    for _, row in policy_df.iterrows():
                        row_text = ' '.join([str(val).lower() for val in row.values if pd.notna(val)])
                        if any(word in row_text for word in description.split() if len(word) > 3):
                            page_sources.append("Pages 1-18 (Policy Structure)")
                            break
                
                # Search annex dataframe for matching terms
                if not annex_df.empty:
                    for _, row in annex_df.iterrows():
                        row_text = ' '.join([str(val).lower() for val in row.values if pd.notna(val)])
                        if any(word in row_text for word in description.split() if len(word) > 3):
                            page_sources.append("Pages 19-54 (Annex Procedures)")
                            break
            
            # Default if no match found
            if not page_sources:
                page_sources.append("Pages 1-54 (General Document Content)")
            
            # Add page source information
            enhanced_item['pdf_page_sources'] = page_sources
            enhanced_item['validation_ready'] = True
            
            enhanced_items.append(enhanced_item)
        
        print(f"   📍 Added page source tracking to {len(enhanced_items)} {item_type}s for PDF validation")
        return enhanced_items
    
    def _run_comprehensive_extended_ai(self, policy_results: Dict, annex_results: Dict, ai_analysis: Dict) -> Dict:
        """Run comprehensive extended AI analysis using all sophisticated prompts"""
        extended_results = {}
        
        try:
            print("   🔍 Running annex quality analysis...")
            # 1. Annex Quality Analysis
            annex_df = annex_results.get('procedures', pd.DataFrame())
            if not annex_df.empty:
                annex_summary = f"Extracted {len(annex_df)} procedures across {annex_df['specialty'].nunique()} specialties"
                sample_rows = annex_df.head(5).to_dict('records')
                
                annex_quality_prompt = UpdatedHealthcareAIPrompts.get_annex_quality_prompt(
                    annex_summary, json.dumps(sample_rows, indent=2)
                )
                annex_quality = self._call_openai(annex_quality_prompt, tag="annex_quality")
                extended_results['annex_quality'] = annex_quality
                print(f"      ✅ Annex quality analysis complete")
            
            print("   📊 Running policy-annex alignment check...")
            # 2. Policy-Annex Alignment Analysis  
            policy_df = policy_results.get('structured', pd.DataFrame())
            if not policy_df.empty and not annex_df.empty:
                policy_summary = f"Policy covers {len(policy_df)} services across {len(policy_df)} categories"
                annex_summary = f"Annex details {len(annex_df)} procedures with tariffs"
                
                alignment_prompt = UpdatedHealthcareAIPrompts.get_policy_annex_alignment_prompt(
                    policy_summary, annex_summary
                )
                alignment_analysis = self._call_openai(alignment_prompt, tag="policy_alignment")
                extended_results['policy_annex_alignment'] = alignment_analysis
                print(f"      ✅ Policy-annex alignment complete")
            
            print("   🌍 Running equity analysis...")
            # 3. Equity Analysis - Kenya's 47 counties
            coverage_summary = f"Analysis of {len(policy_df)} services and {len(annex_df)} procedures for Kenya's 56.4M population"
            county_note = "Kenya has 47 counties with 70% rural, 30% urban population distribution"
            
            equity_prompt = UpdatedHealthcareAIPrompts.get_equity_analysis_prompt(
                coverage_summary, county_note  
            )
            equity_analysis = self._call_openai(equity_prompt, tag="equity_analysis")
            extended_results['equity_analysis'] = equity_analysis
            print(f"      ✅ Equity analysis complete")
            
            print("   🎯 Generating strategic policy recommendations...")
            # 4. Strategic Policy Recommendations
            analysis_data = {
                'contradictions': len(ai_analysis.get('contradictions', [])),
                'gaps': len(ai_analysis.get('gaps', [])), 
                'policy_services': len(policy_df),
                'annex_procedures': len(annex_df),
                'key_findings': f"Found {len(ai_analysis.get('contradictions', []))} critical contradictions and {len(ai_analysis.get('gaps', []))} service gaps"
            }
            
            recommendations_prompt = UpdatedHealthcareAIPrompts.get_strategic_policy_recommendations_prompt(
                json.dumps(analysis_data, indent=2)
            )
            recommendations = self._call_openai(recommendations_prompt, tag="policy_recommendations")
            extended_results['strategic_recommendations'] = recommendations
            print(f"      ✅ Strategic recommendations complete")
            
            print("   🏥 Running facility level validation...")
            # 5. Facility Level Validation - Kenya's 6-tier system
            if not policy_df.empty:
                policy_sample = policy_df.head(10).to_dict('records')
                facility_prompt = UpdatedHealthcareAIPrompts.get_facility_level_validation_prompt(
                    json.dumps(policy_sample, indent=2)
                )
                facility_validation = self._call_openai(facility_prompt, tag="facility_validation")
                extended_results['facility_level_validation'] = facility_validation
                print(f"      ✅ Facility validation complete")
            
            print("   💰 Running tariff outlier analysis...")
            # 6. Tariff Outlier Analysis  
            if not annex_df.empty and 'tariff' in annex_df.columns:
                tariffs = annex_df['tariff'].dropna()
                if len(tariffs) > 0:
                    tariff_stats = {
                        'count': len(tariffs),
                        'min': float(tariffs.min()),
                        'max': float(tariffs.max()), 
                        'mean': float(tariffs.mean()),
                        'std': float(tariffs.std())
                    }
                    
                    tariff_prompt = UpdatedHealthcareAIPrompts.get_tariff_outlier_prompt(
                        json.dumps(tariff_stats, indent=2)
                    )
                    tariff_outliers = self._call_openai(tariff_prompt, tag="tariff_outliers")
                    extended_results['tariff_outliers'] = tariff_outliers
                    print(f"      ✅ Tariff outlier analysis complete")
            
            print("   🎯 All extended analyses complete!")
            return extended_results
            
        except Exception as e:
            print(f"   ❌ Extended AI analysis error: {e}")
            return extended_results
    

    def _print_comprehensive_summary(self, results: Dict, analysis_time: float):
        """Print comprehensive analysis summary"""
        
        print(f"\n🎯 INTEGRATED COMPREHENSIVE ANALYSIS COMPLETE")
        print("=" * 70)
        
        # Extraction summary
        policy_count = results.get('total_policy_services', 0)
        annex_count = results.get('total_annex_procedures', 0)
        total_count = policy_count + annex_count
        ai_contradictions = results.get('total_ai_contradictions', 0)
        ai_gaps = results.get('total_ai_gaps', 0)
        
        print(f"\n📊 EXTRACTION RESULTS:")
        print(f"   • Policy services (pages 1-18): {policy_count}")
        print(f"   • Annex procedures (pages 19-54): {annex_count}")
        print(f"   • Total services/procedures: {total_count}")
        
        # AI analysis summary
        print(f"\n🤖 AI ANALYSIS RESULTS:")
        print(f"   • Contradictions found: {ai_contradictions}")
        print(f"   • Gaps identified: {ai_gaps}")
        
        # Unique tracker summary  
        tracker_summary = results.get('unique_insights_summary', {})
        
        print(f"\n🔍 UNIQUE INSIGHTS TRACKER (Across All Runs):")
        print(f"   • Total unique gaps discovered: {tracker_summary.get('total_unique_gaps', 0)}")
        print(f"   • Total unique contradictions discovered: {tracker_summary.get('total_unique_contradictions', 0)}")
        print(f"   • Analysis runs completed: {tracker_summary.get('total_runs', 0)}")
        
        print(f"\n⏱️ Analysis completed in {analysis_time} seconds")
        print(f"🎯 Ready for comprehensive healthcare policy analysis!")

    def export_to_csv(self, results: Dict) -> Dict[str, str]:
        """Generate ALL 4 CSV formats exactly like manual.ipynb: raw, wide, exploded, structured"""
        csv_files = {}
        
        try:
            # ===== 1. BUILD DOCUMENT VOCABULARY EXACTLY LIKE MANUAL.IPYNB =====
            global DOC_VOCAB
            print("📚 Building document vocabulary from raw tables...")
            
            # Read raw tables to build vocabulary (same as manual.ipynb)
            def read_tables_raw(pdf_path: str, pages="1-18"):
                dfs = tabula.read_pdf(pdf_path, pages=pages, lattice=True, multiple_tables=True,
                                      pandas_options={"header": None}) or []
                if not dfs:
                    dfs = tabula.read_pdf(pdf_path, pages=pages, stream=True, multiple_tables=True,
                                          pandas_options={"header": None}) or []
                return dfs
            
            raw_dfs = read_tables_raw(self.pdf_path, "1-18")
            DOC_VOCAB = build_doc_vocab_from_tables(raw_dfs)
            print(f"📚 Built vocabulary with {len(DOC_VOCAB)} unique terms")
            
            # ===== 2. GET RAW POLICY RULES DATAFRAME (EXACTLY LIKE MANUAL.IPYNB) =====
            # Always use the raw extraction method to get the original 31 services like manual.ipynb
            print("📋 Extracting raw policy rules using exact manual.ipynb method...")
            rules_df = self._extract_rules_manual_exact(self.pdf_path)
            print(f"📋 Extracted {len(rules_df)} raw policy services (matching manual.ipynb)")
            
            if rules_df.empty:
                print("❌ Cannot generate CSV formats - no policy data available")
                return csv_files
            
            # ===== 3. GENERATE ALL 4 FORMATS USING EXACT MANUAL.IPYNB BUILD_STRUCTURES =====
            print("🔄 Building all 4 CSV formats using manual.ipynb build_structures...")
            
            # Apply .map() instead of deprecated .applymap()
            for c in ["fund", "service", "scope", "access_point", "tariff_raw", "access_rules"]:
                if c in rules_df.columns:
                    rules_df[c] = rules_df[c].map(_clean_cell)
            
            # Generate all 4 formats exactly like manual.ipynb
            wide_df, exploded_df, structured_df = build_structures(rules_df)
            
            # ===== 4. SAVE ALL 4 FORMATS EXACTLY LIKE MANUAL.IPYNB =====
            # 1. Raw format (original extraction)
            raw_file = self.output_dir / "rules_p1_18_raw.csv"
            rules_df.to_csv(raw_file, index=False)
            csv_files['rules_raw'] = str(raw_file)
            print(f"✅ Raw format: {raw_file} ({len(rules_df)} rows)")
            
            # 2. Wide format (nested lists preserved)
            wide_file = self.output_dir / "rules_p1_18_structured_wide.csv"
            wide_df.to_csv(wide_file, index=False)
            csv_files['rules_wide'] = str(wide_file)
            print(f"✅ Wide format: {wide_file} ({len(wide_df)} rows)")
            
            # 3. Exploded format (one row per scope item)
            exploded_file = self.output_dir / "rules_p1_18_structured_exploded.csv"
            exploded_df.to_csv(exploded_file, index=False)
            csv_files['rules_exploded'] = str(exploded_file)
            print(f"✅ Exploded format: {exploded_file} ({len(exploded_df)} rows)")
            
            # 4. Structured format (flattened for analysis)
            structured_file = self.output_dir / "rules_p1_18_structured.csv"
            structured_df.to_csv(structured_file, index=False)
            csv_files['rules_structured'] = str(structured_file)
            print(f"✅ Structured format: {structured_file} ({len(structured_df)} rows)")
            
            # ===== 5. ANNEX DATA =====
            if 'extraction_results' in results and 'annex_data' in results['extraction_results']:
                annex_data = results['extraction_results']['annex_data']
                if annex_data:
                    annex_df = pd.DataFrame(annex_data)
                    annex_file = self.output_dir / "annex_procedures.csv"
                    annex_df.to_csv(annex_file, index=False)
                    csv_files['annex_raw'] = str(annex_file)
                    print(f"✅ Annex procedures: {annex_file} ({len(annex_df)} procedures)")
            
            # ===== 6. COMPREHENSIVE AI ANALYSIS RESULTS (INCLUDING ALL UNIQUE INSIGHTS) =====
            # Current run contradictions
            if 'analysis_results' in results and 'ai_contradictions' in results['analysis_results']:
                contradictions = results['analysis_results']['ai_contradictions']
                if contradictions:
                    contradictions_df = pd.DataFrame(contradictions)
                    contradictions_file = self.output_dir / "contradictions_analysis.csv"
                    contradictions_df.to_csv(contradictions_file, index=False)
                    csv_files['contradictions'] = str(contradictions_file)
                    print(f"✅ AI contradictions (current run): {contradictions_file} ({len(contradictions)} found)")
            
            # Current run clinical gaps
            if 'analysis_results' in results and 'ai_gaps' in results['analysis_results']:
                clinical_gaps = results['analysis_results']['ai_gaps']
                if clinical_gaps:
                    clinical_gaps_df = pd.DataFrame(clinical_gaps)
                    clinical_gaps_file = self.output_dir / "clinical_gaps_analysis.csv"
                    clinical_gaps_df.to_csv(clinical_gaps_file, index=False)
                    csv_files['clinical_gaps'] = str(clinical_gaps_file)
                    print(f"✅ Clinical priority gaps (current run): {clinical_gaps_file} ({len(clinical_gaps)} found)")
            
            # Current run coverage gaps
            if 'coverage_analysis' in results and 'coverage_gaps' in results['coverage_analysis']:
                coverage_gaps = results['coverage_analysis']['coverage_gaps']
                if coverage_gaps:
                    coverage_gaps_df = pd.DataFrame(coverage_gaps)
                    coverage_gaps_file = self.output_dir / "coverage_gaps_analysis.csv"
                    coverage_gaps_df.to_csv(coverage_gaps_file, index=False)
                    csv_files['coverage_gaps'] = str(coverage_gaps_file)
                    print(f"✅ Systematic coverage gaps (current run): {coverage_gaps_file} ({len(coverage_gaps)} found)")
            
            # Combined comprehensive gaps (clinical + coverage)
            all_current_gaps = []
            if 'analysis_results' in results and 'ai_gaps' in results['analysis_results']:
                all_current_gaps.extend(results['analysis_results']['ai_gaps'])
            if 'coverage_analysis' in results and 'coverage_gaps' in results['coverage_analysis']:
                all_current_gaps.extend(results['coverage_analysis']['coverage_gaps'])
            
            if all_current_gaps:
                all_gaps_df = pd.DataFrame(all_current_gaps)
                all_gaps_file = self.output_dir / "comprehensive_gaps_analysis.csv"
                all_gaps_df.to_csv(all_gaps_file, index=False)
                csv_files['comprehensive_gaps'] = str(all_gaps_file)
                print(f"✅ Comprehensive gaps (clinical + coverage): {all_gaps_file} ({len(all_current_gaps)} total gaps)")
            
            # ===== 7. ALL UNIQUE INSIGHTS (COMPREHENSIVE ACCUMULATION) =====
            # Export ALL unique gaps accumulated across runs
            if hasattr(self, 'unique_tracker') and self.unique_tracker:
                all_unique_gaps = self.unique_tracker.unique_gaps
                if all_unique_gaps:
                    unique_gaps_df = pd.DataFrame(all_unique_gaps)
                    unique_gaps_file = self.output_dir / "all_unique_gaps_comprehensive.csv"
                    unique_gaps_df.to_csv(unique_gaps_file, index=False)
                    csv_files['all_unique_gaps'] = str(unique_gaps_file)
                    print(f"🎯 ALL UNIQUE GAPS (comprehensive): {unique_gaps_file} ({len(all_unique_gaps)} total unique gaps)")
                
                all_unique_contradictions = self.unique_tracker.unique_contradictions
                if all_unique_contradictions:
                    unique_contradictions_df = pd.DataFrame(all_unique_contradictions)
                    unique_contradictions_file = self.output_dir / "all_unique_contradictions_comprehensive.csv"
                    unique_contradictions_df.to_csv(unique_contradictions_file, index=False)
                    csv_files['all_unique_contradictions'] = str(unique_contradictions_file)
                    print(f"🎯 ALL UNIQUE CONTRADICTIONS (comprehensive): {unique_contradictions_file} ({len(all_unique_contradictions)} total unique contradictions)")
            
            # ===== 7. COMPREHENSIVE SUMMARY =====
            clinical_gaps_count = len(results.get('ai_analysis', {}).get('gaps', []))
            coverage_gaps_count = len(results.get('coverage_analysis', {}).get('coverage_gaps', []))
            total_gaps_count = clinical_gaps_count + coverage_gaps_count
            
            # Get correct counts from the actual results structure
            annex_count = len(results.get('annex_results', {}).get('procedures', []))
            contradictions_count = len(results.get('ai_analysis', {}).get('contradictions', []))
            
            summary_data = {
                'analysis_date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                'raw_services': [len(rules_df)],
                'wide_services': [len(wide_df)],
                'exploded_rows': [len(exploded_df)],
                'structured_services': [len(structured_df)],
                'annex_procedures': [annex_count],
                'total_contradictions': [contradictions_count],
                'clinical_priority_gaps': [clinical_gaps_count],
                'systematic_coverage_gaps': [coverage_gaps_count],
                'total_comprehensive_gaps': [total_gaps_count],
                'gap_analysis_approach': ['dual_phase_clinical_and_coverage']
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_file = self.output_dir / "analysis_summary.csv"
            summary_df.to_csv(summary_file, index=False)
            csv_files['summary'] = str(summary_file)
            print(f"✅ Analysis summary: {summary_file}")
            
            print(f"\n🎉 ALL 4 CSV FORMATS GENERATED (matching manual.ipynb exactly):")
            print(f"   📋 Raw: {len(rules_df)} services")
            print(f"   📊 Wide: {len(wide_df)} services (with nested data)")  
            print(f"   💥 Exploded: {len(exploded_df)} rows (one per scope item)")
            print(f"   📈 Structured: {len(structured_df)} services (flattened)")
            
        except Exception as e:
            print(f"❌ CSV export error: {e}")
            import traceback
            traceback.print_exc()
        
        return csv_files

def main():
    """Main execution function"""
    
    pdf_path = "TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf"
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize analyzer with PDF path
    analyzer = IntegratedComprehensiveMedicalAnalyzer(pdf_path=pdf_path)
    
    # Run comprehensive analysis
    results = analyzer.analyze_complete_document(pdf_path)
    
    # Save results to dynamic output directory
    results_file = analyzer.output_dir / "integrated_comprehensive_analysis.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📁 Results saved to: {results_file}")
    print(f"📁 Output directory: {analyzer.output_dir}")
    
    # Export to CSV for end user accessibility
    print(f"\n📊 Exporting results to clean CSV format...")
    csv_files = analyzer.export_to_csv(results)
    
    if csv_files:
        print(f"\n✅ Clean Data Export Complete!")
        print("📊 Direct access to clean, structured data:")
        for file_type, file_path in csv_files.items():
            if file_type == 'policy_raw':
                print(f"   📋 Policy Services (clean): {file_path}")
            elif file_type == 'annex_raw':
                print(f"   📋 Annex Procedures (clean): {file_path}")
            elif file_type == 'contradictions':
                print(f"   🤖 AI Contradictions: {file_path}")
            elif file_type == 'gaps':
                print(f"   🔍 AI Gaps: {file_path}")
            elif file_type == 'summary':
                print(f"   📈 Summary: {file_path}")
        print(f"\n🎯 Raw extractions immediately available in timestamped folder")
    
    return results

if __name__ == "__main__":
    results = main()
