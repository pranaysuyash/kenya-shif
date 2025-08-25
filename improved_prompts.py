#!/usr/bin/env python3
"""
Improved Prompts for Enhanced SHIF Analysis
Addresses critical quality issues found in prompt analysis
"""

class ImprovedPrompts:
    """Enhanced prompts that should dramatically increase detection accuracy"""
    
    @staticmethod
    def get_enhanced_extraction_prompt(text_chunk: str, page_num: int) -> str:
        """Enhanced extraction prompt with medical knowledge and table preservation"""
        return f"""
You are a healthcare policy expert analyzing Kenyan SHIF benefits. Your task is to extract ALL services while preserving table relationships and identifying potential contradictions.

CRITICAL INSTRUCTIONS:
1. **PRESERVE TABLE STRUCTURE**: If services appear in the same table/section, they are related
2. **DIFFERENTIATE SIMILAR SERVICES**: Hemodialysis ≠ Hemodiafiltration ≠ Peritoneal Dialysis  
3. **EXTRACT COMPLETE ACCESS RULES**: Session limits, frequency restrictions, facility levels
4. **FLAG POTENTIAL CONFLICTS**: Note if you see conflicting information in the same section

MEDICAL KNOWLEDGE TO APPLY:
- Dialysis types are distinct services with potentially different protocols
- Same medical category services should have consistent access rules
- "Maximum X per week" creates utilization limits that can conflict

TEXT TO ANALYZE (Page {page_num}):
{text_chunk}

ENHANCED OUTPUT FORMAT:
{{
  "services": [
    {{
      "service": "exact service name including type distinctions",
      "medical_category": "DIALYSIS|SURGERY|IMAGING|CONSULTATION|etc",
      "service_subcategory": "hemodialysis|hemodiafiltration|peritoneal_dialysis|etc",
      "tariff_value": number or null,
      "tariff_unit": "per_session|per_procedure|per_day|etc",
      "limits": {{
        "per_week": number or null,
        "per_month": number or null,
        "per_year": number or null,
        "maximum_sessions": number or null
      }},
      "facility_levels": ["Level 1", "Level 2", etc],
      "coverage_status": "COVERED|NOT_COVERED|CONDITIONAL",
      "exclusions": "specific exclusions if any",
      "table_context": "other services in same table/section",
      "raw_text": "exact text snippet from document",
      "potential_conflicts": "note if you see conflicting info",
      "source_page": {page_num}
    }}
  ],
  "table_relationships": [
    {{
      "table_title": "section or table heading",
      "services_in_table": ["service1", "service2", "service3"],
      "access_rules_apply_to": "ALL|SPECIFIC services in this table"
    }}
  ],
  "extraction_notes": "important observations about document structure or conflicts"
}}

EXAMPLES OF WHAT TO CATCH:
- "Hemodialysis: Maximum 3 sessions/week" AND "Hemodiafiltration: Maximum 2 sessions/week" = POTENTIAL CONFLICT
- Same service appearing with different tariffs in different sections
- Services grouped in tables that suggest they should have similar access rules

Extract everything systematically. Be especially careful with dialysis services and session limits.
"""

    @staticmethod 
    def get_enhanced_contradiction_prompt(rules_text: str) -> str:
        """Enhanced contradiction detection with medical knowledge"""
        return f"""
You are a healthcare policy expert with deep knowledge of medical service relationships. Analyze these SHIF rules for contradictions with medical context.

ENHANCED CONTRADICTION TYPES TO DETECT:

1. **CLINICAL CONTRADICTION**: Related medical services with inconsistent access rules
   - Example: Hemodialysis (3x/week) vs Hemodiafiltration (2x/week) - both are dialysis
   
2. **TARIFF CONTRADICTION**: Same/equivalent services with different pricing
   - Look for services that are medically equivalent or substitutable
   
3. **ACCESS CONTRADICTION**: Same service with different facility/coverage rules
   - Service both included and excluded
   - Different facility level requirements for same service
   
4. **LOGICAL CONTRADICTION**: Rules that don't make medical sense
   - Higher complexity service cheaper than basic version
   - Unrealistic session limits for medical procedures

MEDICAL KNOWLEDGE TO APPLY:
- Dialysis types (Hemo/Hemodia/Peritoneal) are related but distinct services
- All should have clinically appropriate session limits
- Inconsistent limits between related services suggest errors
- More complex procedures typically cost more than basic ones

RULES TO ANALYZE:
{rules_text}

ENHANCED RESPONSE FORMAT:
[
  {{
    "type": "Clinical|Tariff|Access|Logical",
    "medical_category": "DIALYSIS|SURGERY|etc",
    "service_1": "exact service name",
    "service_2": "exact service name", 
    "conflict_description": "detailed medical context of why this is problematic",
    "clinical_impact": "how this affects patient care",
    "evidence_1": "page X evidence with full context",
    "evidence_2": "page Y evidence with full context",
    "severity": "CRITICAL|HIGH|MEDIUM|LOW",
    "confidence": "HIGH|MEDIUM|LOW",
    "medical_rationale": "why these services should/shouldn't have same rules",
    "recommendation": "specific fix needed"
  }}
]

Focus especially on dialysis services. In the provided rules, look for:
- Different session limits for dialysis types
- Inconsistent pricing for related services  
- Access rules that don't align with medical necessity

Return detailed analysis with medical reasoning. Empty array [] if no contradictions found.
"""

    @staticmethod
    def get_enhanced_service_grouping_prompt(services_list: list) -> str:
        """Enhanced service grouping with medical knowledge"""
        services_text = "\n".join([f"{i+1}. {service}" for i, service in enumerate(services_list)])
        
        return f"""
You are a medical coding expert analyzing healthcare service names for clinical relationships and potential contradictions.

ADVANCED GROUPING CRITERIA:
1. **MEDICAL EQUIVALENCE**: Services that are clinically the same
2. **CLINICAL FAMILY**: Related services that should have consistent rules
3. **PROCEDURAL VARIANTS**: Different approaches to same medical outcome
4. **NAMING INCONSISTENCIES**: Same service with different terminology

MEDICAL KNOWLEDGE BASE:
- Hemodialysis, Hemodiafiltration, Hemofiltration = Dialysis family (should have consistent access patterns)
- CT scan, CT imaging, Computed tomography = Same service
- Ultrasound, Ultrasonography, Sonography = Same service
- Different surgical approaches to same procedure = Procedural variants

SERVICES TO ANALYZE:
{services_text}

ENHANCED OUTPUT FORMAT:
{{
  "clinical_families": [
    {{
      "family_name": "Dialysis Services",
      "primary_service": "most common/standard name",
      "related_services": ["hemodialysis", "hemodiafiltration", "peritoneal dialysis"],
      "relationship_type": "CLINICAL_FAMILY|EQUIVALENT|PROCEDURAL_VARIANT",
      "expected_consistency": "access_rules|pricing|facility_levels",
      "contradiction_potential": "HIGH|MEDIUM|LOW",
      "clinical_notes": "medical rationale for grouping"
    }}
  ],
  "exact_duplicates": [
    {{
      "canonical_name": "preferred service name",
      "duplicates": ["variation 1", "variation 2"],
      "naming_issues": "spelling|abbreviation|terminology differences"
    }}
  ],
  "contradiction_alerts": [
    {{
      "services": ["service1", "service2"],
      "alert": "these clinically related services may have inconsistent rules",
      "check_for": "session_limits|tariffs|access_rules"
    }}
  ]
}}

Focus on medical relationships that could reveal policy contradictions. Group services that should logically have consistent access rules.
"""

def main():
    """Test improved prompts"""
    print("🎯 Enhanced Prompts for SHIF Analysis")
    print("These prompts incorporate:")
    print("- Medical knowledge integration")
    print("- Table structure preservation") 
    print("- Contradiction-aware extraction")
    print("- Clinical reasoning")
    print("- Specific dialysis service differentiation")

if __name__ == "__main__":
    main()