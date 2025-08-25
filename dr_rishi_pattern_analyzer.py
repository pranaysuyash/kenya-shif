#!/usr/bin/env python3
"""
DR. RISHI PATTERN-BASED HEALTHCARE ANALYZER
Implementation of all 4 tasks using pattern-based analysis (no OpenAI quota needed)

TASK 1: Extract rules into structured format using patterns
TASK 2: Build contradiction and gap checker using pattern matching
TASK 3: Integrate Kenya/SHIF domain knowledge 
TASK 4: Dashboard/table interface for results
"""

import pandas as pd
import json
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import time
from datetime import datetime
from collections import defaultdict, Counter

class DrRishiPatternAnalyzer:
    """
    Pattern-based healthcare policy analyzer for all Dr. Rishi's requirements
    """
    
    def __init__(self):
        # Load the verified 825-service dataset
        self.policy_services = []
        self.annex_procedures = []
        self.structured_rules = []
        self.contradictions = []
        self.gaps = []
        self.kenya_context = {}
        
        # Pattern definitions
        self.facility_patterns = self._define_facility_patterns()
        self.condition_patterns = self._define_condition_patterns()
        self.exclusion_patterns = self._define_exclusion_patterns()
        self.tariff_patterns = self._define_tariff_patterns()
        
        print("🩺 DR. RISHI PATTERN-BASED HEALTHCARE ANALYZER")
        print("=" * 60)
        print("✅ TASK 1: Rule structuring with pattern matching")
        print("✅ TASK 2: Contradiction and gap detection") 
        print("✅ TASK 3: Kenya/SHIF domain knowledge integration")
        print("✅ TASK 4: Dashboard interface")

    def _define_facility_patterns(self) -> Dict:
        """Define patterns for facility level extraction"""
        return {
            'level_1': r'(?i)level\s*1|community\s*health|dispensary|health\s*post',
            'level_2': r'(?i)level\s*2|health\s*center|clinic',
            'level_3': r'(?i)level\s*3|health\s*center|sub\s*county',
            'level_4': r'(?i)level\s*4|county\s*hospital|referral',
            'level_5': r'(?i)level\s*5|teaching\s*hospital|national\s*hospital',
            'level_6': r'(?i)level\s*6|specialized\s*hospital',
            'private': r'(?i)private|accredited|designated',
            'any': r'(?i)any\s*level|all\s*levels'
        }

    def _define_condition_patterns(self) -> Dict:
        """Define patterns for medical conditions"""
        return {
            'chronic_diseases': r'(?i)diabetes|hypertension|heart\s*disease|kidney\s*disease|chronic|dialysis',
            'infectious_diseases': r'(?i)malaria|tuberculosis|HIV|AIDS|hepatitis|infection',
            'maternal_health': r'(?i)pregnancy|maternal|antenatal|delivery|cesarean|birth',
            'child_health': r'(?i)pediatric|child|infant|vaccination|immunization|KEPI',
            'emergency': r'(?i)emergency|urgent|trauma|accident|intensive\s*care',
            'surgery': r'(?i)surgery|surgical|operation|procedure|theater',
            'mental_health': r'(?i)mental|psychiatric|depression|anxiety|counseling',
            'preventive': r'(?i)screening|prevention|check\s*up|wellness|health\s*education'
        }

    def _define_exclusion_patterns(self) -> Dict:
        """Define patterns for exclusions"""
        return {
            'age_limits': r'(?i)above\s*\d+|below\s*\d+|under\s*\d+|over\s*\d+',
            'pre_existing': r'(?i)pre\s*existing|prior\s*condition|history\s*of',
            'experimental': r'(?i)experimental|investigational|trial|research',
            'cosmetic': r'(?i)cosmetic|aesthetic|elective|non\s*essential',
            'substance_abuse': r'(?i)alcohol|drug\s*abuse|addiction|substance',
            'geographical': r'(?i)outside\s*kenya|international|abroad'
        }

    def _define_tariff_patterns(self) -> Dict:
        """Define patterns for tariff structures"""
        return {
            'kes_amount': r'KES\s*(\d{1,3}(?:,\d{3})*|\d+)',
            'per_session': r'per\s*session|per\s*visit|each\s*session',
            'per_annum': r'per\s*annum|per\s*year|annually',
            'global_budget': r'global\s*budget|capitation|population\s*based',
            'fee_for_service': r'fee\s*for\s*service|per\s*procedure|per\s*service'
        }

    def load_verified_dataset(self) -> Dict:
        """Load the verified 825-service dataset"""
        
        print(f"\n📊 LOADING VERIFIED DATASET")
        
        try:
            # Load comprehensive results
            with open('outputs/integrated_comprehensive_analysis.json', 'r') as f:
                results = json.load(f)
            
            self.policy_services = results['extraction_results']['policy_structure']['data']
            self.annex_procedures = results['extraction_results']['annex_procedures']['data']
            
            total_services = len(self.policy_services) + len(self.annex_procedures)
            
            print(f"   ✅ Policy services loaded: {len(self.policy_services)}")
            print(f"   ✅ Annex procedures loaded: {len(self.annex_procedures)}")
            print(f"   ✅ Total dataset: {total_services} services/procedures")
            
            return results
            
        except Exception as e:
            print(f"   ❌ Error loading dataset: {e}")
            return {}

    # ========== TASK 1: EXTRACT RULES INTO STRUCTURED FORMAT ==========
    
    def task1_structure_rules(self) -> List[Dict]:
        """
        TASK 1: Extract rules into structured format using patterns
        """
        
        print(f"\n📋 TASK 1: STRUCTURING RULES WITH PATTERN MATCHING")
        print("-" * 40)
        
        structured_rules = []
        
        # Process policy services (pages 1-18)
        print(f"🔧 Processing {len(self.policy_services)} policy services...")
        
        for i, service in enumerate(self.policy_services):
            try:
                structured_rule = self._pattern_structure_policy_rule(service)
                structured_rules.append(structured_rule)
                
                if (i + 1) % 20 == 0:
                    print(f"   • Processed {i+1}/{len(self.policy_services)} policy services")
                    
            except Exception as e:
                print(f"   ⚠️ Error processing policy service {i+1}: {e}")
                continue
        
        # Process annex procedures (pages 19-54)
        print(f"🔧 Processing {len(self.annex_procedures)} annex procedures...")
        
        for i, procedure in enumerate(self.annex_procedures):
            try:
                structured_rule = self._pattern_structure_annex_rule(procedure)
                structured_rules.append(structured_rule)
                
                if (i + 1) % 100 == 0:
                    print(f"   • Processed {i+1}/{len(self.annex_procedures)} annex procedures")
                    
            except Exception as e:
                print(f"   ⚠️ Error processing annex procedure {i+1}: {e}")
                continue
        
        self.structured_rules = structured_rules
        
        print(f"   ✅ TASK 1 COMPLETE: {len(structured_rules)} rules structured")
        
        return structured_rules

    def _pattern_structure_policy_rule(self, service: Dict) -> Dict:
        """Use patterns to structure a policy service rule"""
        
        scope_item = str(service.get('scope_item', ''))
        access_point = str(service.get('access_point', ''))
        tariff_raw = str(service.get('tariff_raw', ''))
        access_rules_raw = str(service.get('access_rules_raw', ''))
        
        # Extract facility level
        facility_level = self._extract_facility_level(access_point + " " + access_rules_raw)
        
        # Extract conditions
        conditions = self._extract_conditions(scope_item + " " + access_rules_raw)
        
        # Extract coverage conditions
        coverage_conditions = self._extract_coverage_conditions(tariff_raw + " " + access_rules_raw)
        
        # Extract exclusions
        exclusions = self._extract_exclusions(access_rules_raw)
        
        # Extract tariff information
        tariff_info = self._extract_tariff_info(tariff_raw)
        
        return {
            "service_name": scope_item[:100] if scope_item else "Unnamed Service",
            "conditions": conditions,
            "facility_level": facility_level,
            "coverage_conditions": coverage_conditions,
            "exclusions": exclusions,
            "tariff_amount": service.get('block_tariff'),
            "payment_method": tariff_info['payment_method'],
            "rule_type": "policy",
            "fund": service.get('fund', ''),
            "service_category": service.get('service', ''),
            "raw_access_rules": access_rules_raw[:200]  # Keep first 200 chars for reference
        }

    def _pattern_structure_annex_rule(self, procedure: Dict) -> Dict:
        """Use patterns to structure an annex procedure rule"""
        
        specialty = str(procedure.get('specialty', ''))
        intervention = str(procedure.get('intervention', ''))
        tariff = procedure.get('tariff', 0)
        
        # Infer conditions from specialty and intervention
        conditions = self._infer_conditions_from_specialty(specialty, intervention)
        
        # Infer facility level from specialty and complexity
        facility_level = self._infer_facility_level_from_specialty(specialty, intervention)
        
        # Standard coverage conditions for procedures
        coverage_conditions = self._infer_procedure_coverage_conditions(intervention)
        
        # Standard exclusions for procedures
        exclusions = self._infer_procedure_exclusions(intervention)
        
        return {
            "service_name": intervention if intervention else "Unnamed Procedure",
            "conditions": conditions,
            "facility_level": facility_level,
            "coverage_conditions": coverage_conditions,
            "exclusions": exclusions,
            "tariff_amount": tariff,
            "payment_method": "fee-for-service",
            "specialty": specialty,
            "rule_type": "annex_procedure",
            "fund": "SHIF",
            "service_category": f"{specialty} Services"
        }

    def _extract_facility_level(self, text: str) -> str:
        """Extract facility level using patterns"""
        
        text_lower = text.lower()
        
        for level, pattern in self.facility_patterns.items():
            if re.search(pattern, text):
                return level.replace('_', ' ').title()
        
        return "Not specified"

    def _extract_conditions(self, text: str) -> List[str]:
        """Extract medical conditions using patterns"""
        
        conditions = []
        
        for condition_type, pattern in self.condition_patterns.items():
            if re.search(pattern, text):
                conditions.append(condition_type.replace('_', ' ').title())
        
        return conditions if conditions else ["General health conditions"]

    def _extract_coverage_conditions(self, text: str) -> List[str]:
        """Extract coverage conditions using patterns"""
        
        conditions = []
        
        # Look for frequency patterns
        if re.search(r'(?i)\d+\s*times?\s*per\s*week', text):
            matches = re.findall(r'(?i)(\d+)\s*times?\s*per\s*week', text)
            for match in matches:
                conditions.append(f"{match} times per week")
        
        # Look for eligibility patterns
        if re.search(r'(?i)registered|member|beneficiary', text):
            conditions.append("Must be registered beneficiary")
        
        # Look for referral patterns
        if re.search(r'(?i)referral|refer', text):
            conditions.append("Requires referral")
        
        # Look for authorization patterns
        if re.search(r'(?i)approval|authorization|pre.?auth', text):
            conditions.append("Requires pre-authorization")
        
        return conditions if conditions else ["Standard coverage conditions apply"]

    def _extract_exclusions(self, text: str) -> List[str]:
        """Extract exclusions using patterns"""
        
        exclusions = []
        
        for exclusion_type, pattern in self.exclusion_patterns.items():
            if re.search(pattern, text):
                exclusions.append(exclusion_type.replace('_', ' ').title())
        
        # Look for specific exclusion phrases
        if re.search(r'(?i)not\s*covered|excluded|exempt', text):
            exclusions.append("Specific exclusions apply")
        
        return exclusions

    def _extract_tariff_info(self, text: str) -> Dict:
        """Extract tariff information using patterns"""
        
        payment_method = "Not specified"
        
        if re.search(self.tariff_patterns['global_budget'], text):
            payment_method = "Global Budget"
        elif re.search(self.tariff_patterns['fee_for_service'], text):
            payment_method = "Fee for Service"
        elif re.search(self.tariff_patterns['per_session'], text):
            payment_method = "Per Session"
        elif re.search(self.tariff_patterns['per_annum'], text):
            payment_method = "Per Annum"
        
        return {"payment_method": payment_method}

    def _infer_conditions_from_specialty(self, specialty: str, intervention: str) -> List[str]:
        """Infer conditions from specialty and intervention"""
        
        specialty_lower = specialty.lower()
        intervention_lower = intervention.lower()
        
        conditions = []
        
        if any(term in specialty_lower for term in ['cardio', 'heart', 'vascular']):
            conditions.append("Cardiovascular conditions")
        
        if any(term in specialty_lower for term in ['urol', 'kidney', 'bladder']):
            conditions.append("Urological conditions")
        
        if any(term in specialty_lower for term in ['ophthal', 'eye']):
            conditions.append("Eye conditions")
        
        if any(term in specialty_lower for term in ['orthop', 'bone', 'joint']):
            conditions.append("Musculoskeletal conditions")
        
        if any(term in specialty_lower for term in ['neurosurg', 'brain', 'spine']):
            conditions.append("Neurological conditions")
        
        if any(term in intervention_lower for term in ['emergency', 'trauma']):
            conditions.append("Emergency conditions")
        
        return conditions if conditions else ["Medical conditions requiring specialist care"]

    def _infer_facility_level_from_specialty(self, specialty: str, intervention: str) -> str:
        """Infer facility level from specialty"""
        
        specialty_lower = specialty.lower()
        intervention_lower = intervention.lower()
        
        # High complexity specialties
        if any(term in specialty_lower for term in ['cardiothoracic', 'neurosurg', 'transplant']):
            return "Level 5-6 (Specialized Hospital)"
        
        # Medium complexity
        if any(term in specialty_lower for term in ['orthop', 'urol', 'maxillo']):
            return "Level 4-5 (County/Teaching Hospital)"
        
        # Lower complexity
        if any(term in specialty_lower for term in ['general', 'ophthal']):
            return "Level 3-4 (Health Center/County Hospital)"
        
        # Emergency procedures
        if any(term in intervention_lower for term in ['emergency', 'urgent']):
            return "Level 4+ (County Hospital or higher)"
        
        return "Level 4+ (County Hospital or higher)"

    def _infer_procedure_coverage_conditions(self, intervention: str) -> List[str]:
        """Infer coverage conditions for procedures"""
        
        conditions = ["Must be registered SHIF beneficiary"]
        
        intervention_lower = intervention.lower()
        
        if any(term in intervention_lower for term in ['surgery', 'operation']):
            conditions.append("Requires specialist referral")
            conditions.append("Pre-operative assessment required")
        
        if any(term in intervention_lower for term in ['emergency', 'urgent']):
            conditions.append("Emergency presentation")
        
        if any(term in intervention_lower for term in ['complex', 'major']):
            conditions.append("Requires pre-authorization")
        
        return conditions

    def _infer_procedure_exclusions(self, intervention: str) -> List[str]:
        """Infer exclusions for procedures"""
        
        exclusions = []
        
        intervention_lower = intervention.lower()
        
        if any(term in intervention_lower for term in ['cosmetic', 'aesthetic']):
            exclusions.append("Cosmetic procedures")
        
        if any(term in intervention_lower for term in ['experimental', 'trial']):
            exclusions.append("Experimental procedures")
        
        exclusions.append("Pre-existing conditions (case by case)")
        exclusions.append("Non-emergency elective procedures without referral")
        
        return exclusions

    # ========== TASK 2: BUILD CONTRADICTION AND GAP CHECKER ==========
    
    def task2_detect_contradictions_and_gaps(self) -> Tuple[List[Dict], List[Dict]]:
        """
        TASK 2: Detect contradictions and gaps using pattern analysis
        """
        
        print(f"\n🔍 TASK 2: DETECTING CONTRADICTIONS AND GAPS")
        print("-" * 40)
        
        # Detect contradictions
        print("🚨 Analyzing contradictions...")
        contradictions = self._pattern_detect_contradictions()
        
        # Detect gaps
        print("🔍 Analyzing coverage gaps...")
        gaps = self._pattern_detect_gaps()
        
        self.contradictions = contradictions
        self.gaps = gaps
        
        print(f"   ✅ TASK 2 COMPLETE: {len(contradictions)} contradictions, {len(gaps)} gaps found")
        
        return contradictions, gaps

    def _pattern_detect_contradictions(self) -> List[Dict]:
        """Detect contradictions using pattern analysis"""
        
        contradictions = []
        
        # Group rules by service name for comparison
        service_groups = defaultdict(list)
        for rule in self.structured_rules:
            service_name = rule['service_name'].lower().strip()
            service_groups[service_name].append(rule)
        
        # Check for facility level contradictions
        facility_contradictions = self._check_facility_level_contradictions(service_groups)
        contradictions.extend(facility_contradictions)
        
        # Check for tariff contradictions
        tariff_contradictions = self._check_tariff_contradictions(service_groups)
        contradictions.extend(tariff_contradictions)
        
        # Check for coverage condition contradictions
        coverage_contradictions = self._check_coverage_contradictions()
        contradictions.extend(coverage_contradictions)
        
        print(f"   • Facility contradictions: {len(facility_contradictions)}")
        print(f"   • Tariff contradictions: {len(tariff_contradictions)}")
        print(f"   • Coverage contradictions: {len(coverage_contradictions)}")
        
        return contradictions

    def _check_facility_level_contradictions(self, service_groups: Dict) -> List[Dict]:
        """Check for facility level contradictions"""
        
        contradictions = []
        
        for service_name, rules in service_groups.items():
            if len(rules) > 1:
                facility_levels = [rule['facility_level'] for rule in rules]
                unique_levels = list(set(facility_levels))
                
                if len(unique_levels) > 1:
                    contradictions.append({
                        "type": "facility_level_contradiction",
                        "description": f"Service '{service_name}' has conflicting facility level requirements",
                        "services_involved": [service_name],
                        "severity": "medium",
                        "details": f"Facility levels: {', '.join(unique_levels)}",
                        "rule_types": [rule['rule_type'] for rule in rules]
                    })
        
        return contradictions

    def _check_tariff_contradictions(self, service_groups: Dict) -> List[Dict]:
        """Check for tariff contradictions"""
        
        contradictions = []
        
        for service_name, rules in service_groups.items():
            if len(rules) > 1:
                tariffs = [rule['tariff_amount'] for rule in rules if rule['tariff_amount']]
                unique_tariffs = list(set(tariffs))
                
                if len(unique_tariffs) > 1:
                    contradictions.append({
                        "type": "tariff_contradiction",
                        "description": f"Service '{service_name}' has conflicting tariff amounts",
                        "services_involved": [service_name],
                        "severity": "high",
                        "details": f"Tariffs: KES {', '.join(str(t) for t in unique_tariffs)}",
                        "rule_types": [rule['rule_type'] for rule in rules]
                    })
        
        return contradictions

    def _check_coverage_contradictions(self) -> List[Dict]:
        """Check for coverage condition contradictions"""
        
        contradictions = []
        
        # Look for dialysis frequency contradictions (Dr. Rishi's original concern)
        dialysis_rules = [rule for rule in self.structured_rules 
                         if 'dialysis' in rule['service_name'].lower()]
        
        if len(dialysis_rules) > 1:
            frequencies = []
            for rule in dialysis_rules:
                for condition in rule.get('coverage_conditions', []):
                    if 'times per week' in condition.lower():
                        frequencies.append(condition)
            
            if len(set(frequencies)) > 1:
                contradictions.append({
                    "type": "coverage_frequency_contradiction",
                    "description": "Dialysis coverage has conflicting frequency requirements",
                    "services_involved": [rule['service_name'] for rule in dialysis_rules],
                    "severity": "high",
                    "details": f"Frequencies found: {', '.join(set(frequencies))}",
                    "rule_types": [rule['rule_type'] for rule in dialysis_rules]
                })
        
        return contradictions

    def _pattern_detect_gaps(self) -> List[Dict]:
        """Detect coverage gaps using pattern analysis"""
        
        gaps = []
        
        # Analyze specialty coverage gaps
        specialty_gaps = self._analyze_specialty_coverage_gaps()
        gaps.extend(specialty_gaps)
        
        # Analyze essential service gaps
        essential_gaps = self._analyze_essential_service_gaps()
        gaps.extend(essential_gaps)
        
        # Analyze age-specific gaps
        age_gaps = self._analyze_age_specific_gaps()
        gaps.extend(age_gaps)
        
        print(f"   • Specialty gaps: {len(specialty_gaps)}")
        print(f"   • Essential service gaps: {len(essential_gaps)}")
        print(f"   • Age-specific gaps: {len(age_gaps)}")
        
        return gaps

    def _analyze_specialty_coverage_gaps(self) -> List[Dict]:
        """Analyze gaps in specialty coverage"""
        
        gaps = []
        
        # Count procedures by specialty
        specialty_counts = Counter()
        for rule in self.structured_rules:
            if rule['rule_type'] == 'annex_procedure':
                specialty_counts[rule.get('specialty', 'Unknown')] += 1
        
        # Expected specialties with minimum coverage
        expected_specialties = {
            'Emergency Medicine': 20,
            'Pediatrics': 30,
            'Internal Medicine': 25,
            'Family Medicine': 20,
            'Psychiatry': 15,
            'Radiology': 25,
            'Pathology': 20,
            'Anesthesia': 15
        }
        
        for specialty, min_expected in expected_specialties.items():
            actual_count = specialty_counts.get(specialty, 0)
            if actual_count < min_expected:
                gaps.append({
                    "gap_type": "specialty_coverage_gap",
                    "description": f"Insufficient {specialty} coverage",
                    "impact": "high" if actual_count == 0 else "medium",
                    "affected_population": "All patients requiring this specialty",
                    "recommended_action": f"Add {min_expected - actual_count} more {specialty} procedures",
                    "current_count": actual_count,
                    "expected_count": min_expected
                })
        
        return gaps

    def _analyze_essential_service_gaps(self) -> List[Dict]:
        """Analyze gaps in essential health services"""
        
        gaps = []
        
        # WHO essential health services
        essential_services = [
            "Family planning",
            "Mental health services",  
            "Dental care",
            "Rehabilitation services",
            "Palliative care",
            "Health education",
            "Community health services",
            "Occupational health"
        ]
        
        # Check if each essential service is covered
        covered_services = set()
        for rule in self.structured_rules:
            service_name = rule['service_name'].lower()
            for essential in essential_services:
                if any(keyword in service_name for keyword in essential.lower().split()):
                    covered_services.add(essential)
        
        for essential in essential_services:
            if essential not in covered_services:
                gaps.append({
                    "gap_type": "essential_service_gap",
                    "description": f"Missing coverage for {essential}",
                    "impact": "high",
                    "affected_population": "General population",
                    "recommended_action": f"Add {essential} to benefit package"
                })
        
        return gaps

    def _analyze_age_specific_gaps(self) -> List[Dict]:
        """Analyze age-specific coverage gaps"""
        
        gaps = []
        
        # Count age-specific services
        pediatric_count = sum(1 for rule in self.structured_rules 
                            if any(term in rule['service_name'].lower() 
                                 for term in ['pediatric', 'child', 'infant']))
        
        geriatric_count = sum(1 for rule in self.structured_rules 
                            if any(term in rule['service_name'].lower() 
                                 for term in ['geriatric', 'elderly', 'senior']))
        
        if pediatric_count < 20:
            gaps.append({
                "gap_type": "age_specific_gap", 
                "description": "Insufficient pediatric services coverage",
                "impact": "high",
                "affected_population": "Children under 18",
                "recommended_action": "Add more pediatric-specific procedures"
            })
        
        if geriatric_count < 10:
            gaps.append({
                "gap_type": "age_specific_gap",
                "description": "Insufficient geriatric services coverage", 
                "impact": "medium",
                "affected_population": "Elderly population",
                "recommended_action": "Add geriatric-specific services"
            })
        
        return gaps

    # ========== TASK 3: KENYA/SHIF DOMAIN KNOWLEDGE ==========
    
    def task3_kenya_shif_context(self) -> Dict:
        """
        TASK 3: Integrate Kenya/SHIF domain knowledge
        """
        
        print(f"\n🌐 TASK 3: KENYA/SHIF DOMAIN KNOWLEDGE INTEGRATION")
        print("-" * 40)
        
        # Kenya healthcare context
        kenya_context = self._load_kenya_healthcare_context()
        
        # SHIF-specific context
        shif_context = self._load_shif_context()
        
        # Apply context to enhance analysis
        enhanced_analysis = self._apply_kenya_shif_context(kenya_context, shif_context)
        
        self.kenya_context = {
            'kenya_healthcare': kenya_context,
            'shif_context': shif_context,
            'enhanced_analysis': enhanced_analysis
        }
        
        print(f"   ✅ TASK 3 COMPLETE: Domain knowledge integrated")
        
        return self.kenya_context

    def _load_kenya_healthcare_context(self) -> Dict:
        """Load Kenya healthcare system context"""
        
        return {
            'healthcare_levels': {
                'level_1': 'Community health services, health posts',
                'level_2': 'Dispensaries and clinics', 
                'level_3': 'Health centers',
                'level_4': 'County hospitals',
                'level_5': 'National teaching and referral hospitals',
                'level_6': 'Specialized hospitals'
            },
            'common_diseases': [
                'Malaria', 'Tuberculosis', 'HIV/AIDS', 'Diabetes',
                'Hypertension', 'Respiratory infections', 'Diarrheal diseases',
                'Maternal complications', 'Road traffic injuries'
            ],
            'health_priorities': [
                'Universal Health Coverage',
                'Maternal and child health',
                'Communicable disease control', 
                'Non-communicable disease prevention',
                'Health system strengthening'
            ],
            'access_barriers': [
                'Geographic distance to facilities',
                'Financial barriers',
                'Limited specialist services',
                'Urban-rural disparities',
                'Health worker shortages'
            ]
        }

    def _load_shif_context(self) -> Dict:
        """Load SHIF-specific context"""
        
        return {
            'objectives': [
                'Achieve Universal Health Coverage',
                'Reduce out-of-pocket health expenditure',
                'Improve access to quality healthcare',
                'Strengthen health system financing'
            ],
            'transition_from_nhif': {
                'key_changes': [
                    'Expanded benefit package',
                    'Improved governance structure', 
                    'Better provider payment mechanisms',
                    'Enhanced quality assurance'
                ]
            },
            'payment_mechanisms': {
                'global_budget': 'Population-based payments to primary care networks',
                'fee_for_service': 'Per-procedure payments for specialist services',
                'capitation': 'Per-person payments for defined populations'
            },
            'implementation_challenges': [
                'Provider network adequacy',
                'Benefit package comprehensiveness',
                'Quality assurance mechanisms',
                'Financial sustainability',
                'Information systems integration'
            ]
        }

    def _apply_kenya_shif_context(self, kenya_context: Dict, shif_context: Dict) -> Dict:
        """Apply contextual knowledge to enhance analysis"""
        
        # Analyze contradictions in context
        context_enhanced_contradictions = []
        for contradiction in self.contradictions:
            enhanced = contradiction.copy()
            enhanced['kenya_context'] = self._get_kenya_context_for_contradiction(contradiction, kenya_context)
            context_enhanced_contradictions.append(enhanced)
        
        # Analyze gaps in context
        context_enhanced_gaps = []
        for gap in self.gaps:
            enhanced = gap.copy()
            enhanced['kenya_priority'] = self._assess_gap_priority_for_kenya(gap, kenya_context)
            context_enhanced_gaps.append(enhanced)
        
        return {
            'context_enhanced_contradictions': context_enhanced_contradictions,
            'context_enhanced_gaps': context_enhanced_gaps,
            'policy_recommendations': self._generate_policy_recommendations(kenya_context, shif_context)
        }

    def _get_kenya_context_for_contradiction(self, contradiction: Dict, kenya_context: Dict) -> str:
        """Get Kenya-specific context for contradictions"""
        
        if contradiction['type'] == 'facility_level_contradiction':
            return "May cause confusion in Kenya's tiered health system"
        elif contradiction['type'] == 'tariff_contradiction':
            return "Could impact financial access in Kenya's mixed health economy"
        elif 'dialysis' in contradiction.get('description', '').lower():
            return "Critical for Kenya's growing chronic kidney disease burden"
        
        return "Requires clarification for effective implementation"

    def _assess_gap_priority_for_kenya(self, gap: Dict, kenya_context: Dict) -> str:
        """Assess gap priority based on Kenya context"""
        
        gap_desc = gap.get('description', '').lower()
        
        # High priority based on Kenya's disease burden
        if any(disease.lower() in gap_desc for disease in kenya_context['common_diseases']):
            return "High - aligns with Kenya's disease burden"
        
        # High priority based on health priorities
        if any(priority.lower() in gap_desc for priority in kenya_context['health_priorities']):
            return "High - matches national health priorities"
        
        # Medium priority for access barriers
        if any(barrier.lower() in gap_desc for barrier in kenya_context['access_barriers']):
            return "Medium - addresses known access barriers"
        
        return "Medium - general improvement"

    def _generate_policy_recommendations(self, kenya_context: Dict, shif_context: Dict) -> List[str]:
        """Generate policy recommendations based on context"""
        
        recommendations = []
        
        if len(self.contradictions) > 0:
            recommendations.append(
                "Establish clear policy guidelines to resolve contradictions in facility level requirements"
            )
        
        if len(self.gaps) > 5:
            recommendations.append(
                "Conduct comprehensive benefit package review to address coverage gaps"
            )
        
        # Kenya-specific recommendations
        recommendations.extend([
            "Strengthen primary care services (Level 1-3) to improve access in rural areas",
            "Expand specialist services coverage to address referral bottlenecks", 
            "Integrate mental health services across all care levels",
            "Enhance maternal and child health benefit coverage",
            "Develop clear quality standards for contracted providers"
        ])
        
        return recommendations

    # ========== TASK 4: DASHBOARD/TABLE INTERFACE ==========
    
    def task4_create_dashboard(self) -> Dict:
        """
        TASK 4: Create dashboard/table of results
        """
        
        print(f"\n📊 TASK 4: CREATING DASHBOARD INTERFACE")
        print("-" * 40)
        
        dashboard_data = {
            'summary_statistics': self._create_summary_statistics(),
            'rules_parsed_table': self._create_rules_table(),
            'contradictions_flagged_table': self._create_contradictions_table(),
            'coverage_gaps_table': self._create_gaps_table(),
            'specialty_analysis_table': self._create_specialty_analysis_table(),
            'kenya_context_table': self._create_kenya_context_table(),
            'recommendations_table': self._create_recommendations_table(),
            'generated_timestamp': datetime.now().isoformat()
        }
        
        # Save dashboard data
        dashboard_file = Path('outputs/dr_rishi_pattern_dashboard.json')
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        
        # Create CSV tables
        self._create_csv_tables(dashboard_data)
        
        # Create summary report
        self._create_summary_report(dashboard_data)
        
        print(f"   ✅ TASK 4 COMPLETE: Dashboard saved to outputs/dr_rishi_pattern_dashboard.json")
        
        return dashboard_data

    def _create_summary_statistics(self) -> Dict:
        """Create comprehensive summary statistics"""
        
        # Rule statistics
        rule_types = Counter(rule['rule_type'] for rule in self.structured_rules)
        specialties = Counter(rule.get('specialty', 'N/A') for rule in self.structured_rules)
        facility_levels = Counter(rule['facility_level'] for rule in self.structured_rules)
        
        # Contradiction statistics
        contradiction_types = Counter(c['type'] for c in self.contradictions)
        high_severity_contradictions = sum(1 for c in self.contradictions if c.get('severity') == 'high')
        
        # Gap statistics
        gap_types = Counter(g['gap_type'] for g in self.gaps)
        high_impact_gaps = sum(1 for g in self.gaps if g.get('impact') == 'high')
        
        # Coverage statistics
        total_services = len(self.policy_services) + len(self.annex_procedures)
        services_with_tariffs = sum(1 for rule in self.structured_rules if rule.get('tariff_amount'))
        coverage_percentage = (services_with_tariffs / len(self.structured_rules)) * 100 if self.structured_rules else 0
        
        return {
            'total_services_analyzed': total_services,
            'total_rules_structured': len(self.structured_rules),
            'tariff_coverage_percentage': round(coverage_percentage, 1),
            'rule_type_distribution': dict(rule_types),
            'specialty_distribution': dict(specialties.most_common(10)),
            'facility_level_distribution': dict(facility_levels),
            'total_contradictions': len(self.contradictions),
            'high_severity_contradictions': high_severity_contradictions,
            'contradiction_type_distribution': dict(contradiction_types),
            'total_gaps': len(self.gaps),
            'high_impact_gaps': high_impact_gaps,
            'gap_type_distribution': dict(gap_types)
        }

    def _create_rules_table(self) -> List[Dict]:
        """Create structured rules table"""
        return [
            {
                'service_name': rule.get('service_name', '')[:50] + '...' if len(rule.get('service_name', '')) > 50 else rule.get('service_name', ''),
                'rule_type': rule.get('rule_type', ''),
                'specialty': rule.get('specialty', 'N/A'),
                'facility_level': rule.get('facility_level', ''),
                'tariff_amount': rule.get('tariff_amount', ''),
                'payment_method': rule.get('payment_method', ''),
                'conditions_count': len(rule.get('conditions', [])),
                'coverage_conditions_count': len(rule.get('coverage_conditions', [])),
                'exclusions_count': len(rule.get('exclusions', []))
            }
            for rule in self.structured_rules
        ]

    def _create_contradictions_table(self) -> List[Dict]:
        """Create contradictions table"""
        return [
            {
                'type': contradiction.get('type', ''),
                'description': contradiction.get('description', ''),
                'severity': contradiction.get('severity', ''),
                'services_count': len(contradiction.get('services_involved', [])),
                'details': contradiction.get('details', ''),
                'kenya_context': contradiction.get('kenya_context', 'N/A'),
                'status': 'flagged'
            }
            for contradiction in self.contradictions
        ]

    def _create_gaps_table(self) -> List[Dict]:
        """Create coverage gaps table"""
        return [
            {
                'gap_type': gap.get('gap_type', ''),
                'description': gap.get('description', ''),
                'impact': gap.get('impact', ''),
                'affected_population': gap.get('affected_population', ''),
                'recommended_action': gap.get('recommended_action', ''),
                'kenya_priority': gap.get('kenya_priority', 'Not assessed')
            }
            for gap in self.gaps
        ]

    def _create_specialty_analysis_table(self) -> List[Dict]:
        """Create specialty analysis table"""
        
        specialty_stats = defaultdict(lambda: {'count': 0, 'avg_tariff': 0, 'total_tariff': 0})
        
        for rule in self.structured_rules:
            if rule.get('specialty') and rule['rule_type'] == 'annex_procedure':
                specialty = rule['specialty']
                specialty_stats[specialty]['count'] += 1
                if rule.get('tariff_amount'):
                    specialty_stats[specialty]['total_tariff'] += rule['tariff_amount']
        
        # Calculate averages
        specialty_table = []
        for specialty, stats in specialty_stats.items():
            if stats['count'] > 0:
                avg_tariff = stats['total_tariff'] / stats['count'] if stats['count'] > 0 else 0
                specialty_table.append({
                    'specialty': specialty,
                    'procedure_count': stats['count'],
                    'average_tariff': round(avg_tariff, 2),
                    'total_value': stats['total_tariff'],
                    'coverage_adequacy': 'Adequate' if stats['count'] >= 20 else 'Limited'
                })
        
        # Sort by procedure count
        return sorted(specialty_table, key=lambda x: x['procedure_count'], reverse=True)

    def _create_kenya_context_table(self) -> List[Dict]:
        """Create Kenya context insights table"""
        
        return [
            {
                'context_area': 'Healthcare System Structure',
                'relevance': 'High',
                'key_insight': 'SHIF benefit package must align with 6-tier health system',
                'implication': 'Facility level requirements need clear mapping'
            },
            {
                'context_area': 'Disease Burden',
                'relevance': 'High', 
                'key_insight': 'High burden of communicable and non-communicable diseases',
                'implication': 'Both categories need comprehensive coverage'
            },
            {
                'context_area': 'Access Barriers',
                'relevance': 'Medium',
                'key_insight': 'Geographic and financial barriers prevalent',
                'implication': 'Need for flexible facility requirements and affordable tariffs'
            },
            {
                'context_area': 'NHIF Transition',
                'relevance': 'High',
                'key_insight': 'SHIF designed to address NHIF limitations',
                'implication': 'Benefit package should reflect lessons learned'
            }
        ]

    def _create_recommendations_table(self) -> List[Dict]:
        """Create recommendations table"""
        
        recommendations = self.kenya_context.get('enhanced_analysis', {}).get('policy_recommendations', [])
        
        return [
            {
                'priority': 'High' if i < 3 else 'Medium',
                'category': 'Policy Improvement',
                'recommendation': rec,
                'timeline': 'Short-term' if 'clear' in rec.lower() or 'establish' in rec.lower() else 'Medium-term',
                'implementation_complexity': 'Low' if 'clear' in rec.lower() else 'Medium'
            }
            for i, rec in enumerate(recommendations)
        ]

    def _create_csv_tables(self, dashboard_data: Dict):
        """Create CSV files for dashboard tables"""
        
        output_dir = Path('outputs')
        
        # Save each table as CSV
        table_mappings = {
            'rules_parsed': 'rules_parsed_table',
            'contradictions': 'contradictions_flagged_table', 
            'gaps': 'coverage_gaps_table',
            'specialties': 'specialty_analysis_table',
            'kenya_context': 'kenya_context_table',
            'recommendations': 'recommendations_table'
        }
        
        for filename, table_key in table_mappings.items():
            if dashboard_data.get(table_key):
                df = pd.DataFrame(dashboard_data[table_key])
                df.to_csv(output_dir / f'dr_rishi_{filename}.csv', index=False)

    def _create_summary_report(self, dashboard_data: Dict):
        """Create a summary report"""
        
        stats = dashboard_data['summary_statistics']
        
        report = f"""
DR. RISHI HEALTHCARE POLICY ANALYSIS REPORT
==========================================
Generated: {dashboard_data['generated_timestamp']}

EXECUTIVE SUMMARY
-----------------
• Total Services Analyzed: {stats['total_services_analyzed']}
• Rules Structured: {stats['total_rules_structured']}
• Tariff Coverage: {stats['tariff_coverage_percentage']}%
• Contradictions Found: {stats['total_contradictions']} ({stats['high_severity_contradictions']} high severity)
• Coverage Gaps Identified: {stats['total_gaps']} ({stats['high_impact_gaps']} high impact)

TOP FINDINGS
------------
• Most Common Rule Type: {max(stats['rule_type_distribution'], key=stats['rule_type_distribution'].get)}
• Largest Specialty: {max(stats['specialty_distribution'], key=stats['specialty_distribution'].get)} ({stats['specialty_distribution'][max(stats['specialty_distribution'], key=stats['specialty_distribution'].get)]} procedures)
• Most Common Gap Type: {max(stats['gap_type_distribution'], key=stats['gap_type_distribution'].get) if stats['gap_type_distribution'] else 'None'}

RECOMMENDATIONS
---------------
"""
        
        recommendations = dashboard_data.get('recommendations_table', [])
        for i, rec in enumerate(recommendations[:5], 1):
            report += f"{i}. {rec['recommendation']}\n"
        
        report += f"\nFor detailed analysis, see CSV files in outputs/ directory.\n"
        
        # Save report
        with open('outputs/dr_rishi_analysis_report.txt', 'w') as f:
            f.write(report)

    # ========== MAIN EXECUTION ==========
    
    def run_complete_analysis(self) -> Dict:
        """Run complete analysis implementing all 4 tasks"""
        
        print(f"\n🚀 RUNNING COMPLETE DR. RISHI PATTERN ANALYSIS")
        print("=" * 60)
        
        start_time = time.time()
        
        # Load verified dataset
        dataset = self.load_verified_dataset()
        
        if not dataset:
            print("❌ Failed to load dataset")
            return {}
        
        # Execute all tasks
        try:
            # TASK 1: Structure rules
            structured_rules = self.task1_structure_rules()
            
            # TASK 2: Detect contradictions and gaps
            contradictions, gaps = self.task2_detect_contradictions_and_gaps()
            
            # TASK 3: Kenya/SHIF context
            context_analysis = self.task3_kenya_shif_context()
            
            # TASK 4: Create dashboard
            dashboard = self.task4_create_dashboard()
            
            analysis_time = round(time.time() - start_time, 2)
            
            # Complete results
            complete_results = {
                'task1_structured_rules': structured_rules,
                'task2_contradictions': contradictions,
                'task2_gaps': gaps,
                'task3_context_analysis': context_analysis,
                'task4_dashboard': dashboard,
                'analysis_metadata': {
                    'total_analysis_time': analysis_time,
                    'tasks_completed': 4,
                    'dataset_size': len(self.policy_services) + len(self.annex_procedures),
                    'analysis_approach': 'pattern_based',
                    'analysis_timestamp': datetime.now().isoformat()
                }
            }
            
            # Save complete results
            results_file = Path('outputs/dr_rishi_pattern_complete_analysis.json')
            with open(results_file, 'w') as f:
                json.dump(complete_results, f, indent=2, default=str)
            
            self._print_final_summary(complete_results, analysis_time)
            
            return complete_results
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _print_final_summary(self, results: Dict, analysis_time: float):
        """Print final analysis summary"""
        
        print(f"\n🎯 DR. RISHI PATTERN ANALYSIS COMPLETE")
        print("=" * 60)
        
        rules_count = len(results.get('task1_structured_rules', []))
        contradictions_count = len(results.get('task2_contradictions', []))
        gaps_count = len(results.get('task2_gaps', []))
        high_severity_contradictions = sum(1 for c in results.get('task2_contradictions', []) if c.get('severity') == 'high')
        high_impact_gaps = sum(1 for g in results.get('task2_gaps', []) if g.get('impact') == 'high')
        
        print(f"✅ TASK 1: {rules_count} rules structured with detailed components")
        print(f"✅ TASK 2: {contradictions_count} contradictions ({high_severity_contradictions} high severity), {gaps_count} gaps ({high_impact_gaps} high impact)")
        print(f"✅ TASK 3: Kenya/SHIF domain knowledge integrated")
        print(f"✅ TASK 4: Comprehensive dashboard and analysis tables created")
        
        print(f"\n📁 OUTPUT FILES CREATED:")
        output_files = [
            "dr_rishi_pattern_complete_analysis.json - Complete analysis results",
            "dr_rishi_pattern_dashboard.json - Dashboard data",
            "dr_rishi_rules_parsed.csv - All structured rules",
            "dr_rishi_contradictions.csv - Contradiction analysis", 
            "dr_rishi_gaps.csv - Coverage gaps analysis",
            "dr_rishi_specialties.csv - Specialty breakdown",
            "dr_rishi_kenya_context.csv - Kenya context insights",
            "dr_rishi_recommendations.csv - Policy recommendations",
            "dr_rishi_analysis_report.txt - Executive summary report"
        ]
        
        for file_desc in output_files:
            print(f"   • {file_desc}")
        
        print(f"\n🎯 KEY INSIGHTS:")
        print(f"   • {contradictions_count} policy contradictions need resolution")
        print(f"   • {gaps_count} coverage gaps identified for improvement")  
        print(f"   • Analysis completed in {analysis_time} seconds")
        print(f"   • All Dr. Rishi requirements successfully implemented!")
        
        if high_severity_contradictions > 0:
            print(f"\n⚠️  URGENT: {high_severity_contradictions} high-severity contradictions require immediate attention")
        
        if high_impact_gaps > 0:
            print(f"⚠️  PRIORITY: {high_impact_gaps} high-impact coverage gaps should be addressed")

def main():
    """Main execution function"""
    
    analyzer = DrRishiPatternAnalyzer()
    results = analyzer.run_complete_analysis()
    
    return results

if __name__ == "__main__":
    results = main()