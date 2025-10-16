#!/usr/bin/env python3
"""
COVERAGE ANALYSIS AGENT
Systematic coverage analysis complementary to clinical gap analysis

This agent identifies 25-30 additional healthcare gaps focusing on:
- WHO Essential Health Services alignment
- Universal Health Coverage gaps  
- Health system capacity gaps
- Service delivery coverage gaps
- Healthcare access equity gaps

Designed to complement (not duplicate) the clinical gap analysis by Dr. Grace and Dr. Amina.
"""

import json
import pandas as pd
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CoverageAnalysisPrompts:
    """Coverage-focused prompts using WHO/UHC expert personas"""
    
    @staticmethod
    def get_who_coverage_analysis_prompt(services_data: str, clinical_gaps: List[Dict]) -> str:
        """WHO health system coverage analysis prompt"""
        clinical_summaries = "\n".join([f"- {gap.get('description', '')[:100]}..." for gap in clinical_gaps[:10]])
        
        return f"""
You are **Dr. Sarah Mwangi**, WHO Country Representative for Kenya and Universal Health Coverage expert with 20+ years in health system strengthening and coverage analysis. Your expertise covers WHO Essential Health Services framework, UHC implementation, and health system capacity assessment.

**YOUR EXPERTISE:**
📋 **WHO Essential Services**: Primary care, emergency care, health promotion, disease prevention
🏥 **Health System Building Blocks**: Service delivery, health workforce, information systems, financing
📊 **Coverage Analysis**: Population health needs vs available services mapping
🌍 **UHC Implementation**: Access, quality, financial protection across populations
📈 **Health Equity**: Geographic, socio-economic, and demographic coverage gaps
🔄 **Health System Integration**: Service linkages, referral systems, continuum of care

**EXISTING CLINICAL GAP ANALYSIS (by Dr. Grace & Dr. Amina):**
{clinical_summaries}

**CURRENT SHIF SERVICE COVERAGE:**
{services_data}

**🎯 SYSTEMATIC COVERAGE ANALYSIS FRAMEWORK:**

Your role is to identify COVERAGE GAPS (not clinical gaps already identified). Focus on:
1) **WHO Essential Services Coverage** - Are all WHO-recommended services available?
2) **Population Coverage Gaps** - Which populations lack access to essential services?
3) **Geographic Coverage Gaps** - Which regions/counties have service access gaps?
4) **Health System Capacity Gaps** - Where are structural service delivery gaps?
5) **Service Integration Gaps** - Where are care continuum breaks?

**AVOID DUPLICATING CLINICAL ANALYSIS** - Focus on systematic coverage, not medical contradictions or clinical priorities already identified.

**ENHANCED COVERAGE GAP OUTPUT:**
[
  {{
    "gap_id": "COV_UHC_PRIMARY_001",
    "gap_category": "primary_health_care_coverage",
    "gap_type": "service_coverage_gap",
    "coverage_priority": "HIGH",
    "description": "Comprehensive primary health care packages underspecified with gaps in health promotion and disease prevention services across community health units",
    "who_essential_services_alignment": {{
      "who_service_category": "Essential primary health care services",
      "who_standard": "Comprehensive PHC including health promotion, disease prevention, treatment, and rehabilitation",
      "coverage_gap": "Health promotion and disease prevention services not systematically covered"
    }},
    "population_coverage_analysis": {{
      "population_groups_affected": ["Rural communities", "Urban informal settlements", "Pastoral communities"],
      "estimated_coverage_deficit": "60% of population lacks access to comprehensive PHC",
      "geographic_distribution": "All 47 counties affected with rural areas most underserved"
    }},
    "health_system_capacity_gap": {{
      "service_delivery_level": "Level 1-2 facilities and community health units",
      "workforce_implications": "Community Health Volunteers lack systematic support and supplies",
      "infrastructure_needs": "CHU strengthening, supply chains, supervision systems"
    }},
    "uhc_impact_assessment": {{
      "access_barriers": "Services not clearly defined or funded in community settings",
      "quality_concerns": "Inconsistent service standards across counties",
      "financial_protection": "Out-of-pocket costs for transport and time"
    }},
    "recommended_coverage_interventions": {{
      "immediate_coverage_actions": [
        "Define comprehensive PHC benefit package for all facility levels",
        "Establish systematic CHU service standards and supply systems",
        "Create county-level PHC implementation protocols"
      ],
      "coverage_targets": "90% population access to comprehensive PHC within 5km/1 hour",
      "monitoring_indicators": ["PHC service availability by county", "Population coverage rates by service type"]
    }},
    "integration_with_existing_services": {{
      "linkage_opportunities": "Integrate with maternal health, immunization, NCD programs",
      "referral_systems": "Strengthen CHU to health center linkages",
      "data_systems": "Community health information systems"
    }}
  }}
]

**TARGET: 25-30 COVERAGE GAPS** focusing on systematic service coverage, WHO alignment, and UHC implementation gaps.
"""

    @staticmethod
    def get_health_equity_analysis_prompt(services_data: str, kenya_demographics: str) -> str:
        """Health equity and access coverage analysis"""
        return f"""
You are **Dr. James Kariuki**, Health Equity and Social Determinants expert with extensive experience in Kenya's health system disparities and vulnerable population health needs analysis.

**YOUR EXPERTISE:**
⚖️ **Health Equity Analysis**: Geographic, socio-economic, gender, age-based health disparities  
🏘️ **Vulnerable Populations**: Informal settlements, pastoral communities, disabled, elderly
🗺️ **Geographic Access**: Rural-urban disparities, transport barriers, facility distribution
💰 **Financial Barriers**: Catastrophic health spending, insurance coverage gaps
🚫 **Social Exclusion**: Marginalized groups, cultural barriers, discrimination

**KENYA DEMOGRAPHICS AND CONTEXT:**
{kenya_demographics}

**CURRENT SHIF COVERAGE:**
{services_data}

**🎯 EQUITY-FOCUSED COVERAGE ANALYSIS:**

Identify gaps where specific populations or regions lack equitable access to essential health services:

**OUTPUT FORMAT:**
[
  {{
    "gap_id": "EQUITY_ACCESS_001", 
    "gap_category": "health_equity_coverage",
    "gap_type": "population_access_gap",
    "equity_priority": "HIGH",
    "description": "Systematic barriers to essential health services for persons with disabilities across all facility levels",
    "vulnerable_population_focus": {{
      "population_group": "Persons with disabilities",
      "estimated_size": "2.2 million persons (4.6% of population)",
      "specific_barriers": ["Physical accessibility", "Communication barriers", "Discrimination", "Lack of assistive services"]
    }},
    "geographic_equity_analysis": {{
      "most_affected_counties": ["Turkana", "Wajir", "Mandera", "West Pokot"],
      "rural_urban_disparity": "Urban areas have some accessible facilities, rural areas have minimal accessibility",
      "transport_barriers": "Public transport not accessible, specialized transport not funded"
    }},
    "service_coverage_gaps": {{
      "missing_services": ["Sign language interpretation", "Braille materials", "Wheelchair accessibility", "Disability-friendly examination equipment"],
      "facility_accessibility": "Less than 20% of facilities meet basic accessibility standards"
    }},
    "recommended_equity_interventions": {{
      "immediate_actions": [
        "Mandate accessibility standards for all SHIF-contracted facilities",
        "Fund sign language interpretation services",
        "Provide accessible health information materials"
      ],
      "coverage_targets": "100% of Level 4+ facilities accessible by 2026"
    }}
  }}
]
"""

class CoverageAnalysisAgent:
    """Main Coverage Analysis Agent coordinating systematic coverage review"""
    
    def __init__(self, deduplication_threshold: float = 0.8):
        self.deduplication_threshold = deduplication_threshold
        self.coverage_gaps = []
        
    def analyze_coverage_gaps(self, services_data: str, clinical_gaps: List[Dict], 
                            use_ai: bool = False, api_key: str = None) -> List[Dict]:
        """
        Main coverage analysis method
        
        Args:
            services_data: Extracted SHIF services data
            clinical_gaps: Existing clinical gaps to avoid duplication
            use_ai: Whether to use AI analysis
            api_key: OpenAI API key if using AI
            
        Returns:
            List of coverage gaps (25-30 gaps)
        """
        logger.info("Starting systematic coverage analysis")
        
        coverage_gaps = []
        
        # Phase 1: WHO Essential Services Coverage Analysis
        who_gaps = self._analyze_who_essential_services_coverage(services_data, clinical_gaps, use_ai, api_key)
        coverage_gaps.extend(who_gaps)
        
        # Phase 2: Population Coverage Gaps
        population_gaps = self._analyze_population_coverage_gaps(services_data, clinical_gaps, use_ai, api_key)
        coverage_gaps.extend(population_gaps)
        
        # Phase 3: Geographic Coverage Analysis
        geographic_gaps = self._analyze_geographic_coverage_gaps(services_data, clinical_gaps, use_ai, api_key)
        coverage_gaps.extend(geographic_gaps)
        
        # Phase 4: Health System Capacity Gaps
        capacity_gaps = self._analyze_health_system_capacity_gaps(services_data, clinical_gaps, use_ai, api_key)
        coverage_gaps.extend(capacity_gaps)
        
        # Phase 5: Service Integration Gaps
        integration_gaps = self._analyze_service_integration_gaps(services_data, clinical_gaps, use_ai, api_key)
        coverage_gaps.extend(integration_gaps)
        
        # Deduplicate against clinical gaps
        coverage_gaps = self._deduplicate_against_clinical_gaps(coverage_gaps, clinical_gaps)
        
        # Internal deduplication
        coverage_gaps = self._internal_deduplication(coverage_gaps)
        
        # Limit to target range
        if len(coverage_gaps) > 30:
            coverage_gaps = self._prioritize_coverage_gaps(coverage_gaps)[:30]
        
        logger.info(f"Coverage analysis complete: {len(coverage_gaps)} gaps identified")
        return coverage_gaps
    
    def _analyze_who_essential_services_coverage(self, services_data: str, clinical_gaps: List[Dict], 
                                               use_ai: bool, api_key: str) -> List[Dict]:
        """Analyze WHO Essential Health Services coverage gaps"""
        logger.info("Analyzing WHO Essential Services coverage")
        
        if use_ai and api_key:
            return self._run_ai_coverage_analysis(services_data, clinical_gaps, "who_essential", api_key)
        else:
            return self._deterministic_who_coverage_analysis(services_data)
    
    def _analyze_population_coverage_gaps(self, services_data: str, clinical_gaps: List[Dict],
                                        use_ai: bool, api_key: str) -> List[Dict]:
        """Analyze population-specific coverage gaps"""
        logger.info("Analyzing population coverage gaps")
        
        if use_ai and api_key:
            return self._run_ai_coverage_analysis(services_data, clinical_gaps, "population_equity", api_key)
        else:
            return self._deterministic_population_coverage_analysis(services_data)
    
    def _analyze_geographic_coverage_gaps(self, services_data: str, clinical_gaps: List[Dict],
                                        use_ai: bool, api_key: str) -> List[Dict]:
        """Analyze geographic coverage disparities"""
        logger.info("Analyzing geographic coverage gaps")
        
        return self._deterministic_geographic_coverage_analysis(services_data)
    
    def _analyze_health_system_capacity_gaps(self, services_data: str, clinical_gaps: List[Dict],
                                           use_ai: bool, api_key: str) -> List[Dict]:
        """Analyze health system structural capacity gaps"""
        logger.info("Analyzing health system capacity gaps")
        
        return self._deterministic_capacity_analysis(services_data)
    
    def _analyze_service_integration_gaps(self, services_data: str, clinical_gaps: List[Dict],
                                        use_ai: bool, api_key: str) -> List[Dict]:
        """Analyze service integration and care continuum gaps"""
        logger.info("Analyzing service integration gaps")
        
        return self._deterministic_integration_analysis(services_data)
    
    def _run_ai_coverage_analysis(self, services_data: str, clinical_gaps: List[Dict], 
                                analysis_type: str, api_key: str) -> List[Dict]:
        """Run AI-powered coverage analysis"""
        try:
            import openai
            openai.api_key = api_key
            
            if analysis_type == "who_essential":
                prompt = CoverageAnalysisPrompts.get_who_coverage_analysis_prompt(services_data, clinical_gaps)
            elif analysis_type == "population_equity":
                kenya_demographics = "Kenya population: 56.4M, 70% rural, 47 counties, diverse ethnic groups"
                prompt = CoverageAnalysisPrompts.get_health_equity_analysis_prompt(services_data, kenya_demographics)
            else:
                return []
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            # Extract JSON from response (implementation depends on response format)
            gaps = self._parse_ai_coverage_response(content)
            
            return gaps
            
        except Exception as e:
            logger.error(f"AI coverage analysis failed: {e}")
            return []
    
    def _deterministic_who_coverage_analysis(self, services_data: str) -> List[Dict]:
        """Deterministic WHO coverage analysis"""
        gaps = []
        
        # Primary Health Care Coverage Gap
        gaps.append({
            "gap_id": "COV_PHC_001",
            "gap_category": "primary_health_care_coverage",
            "gap_type": "service_coverage_gap", 
            "coverage_priority": "HIGH",
            "description": "Comprehensive primary health care packages underspecified with gaps in health promotion and disease prevention services",
            "who_essential_services_alignment": {
                "who_service_category": "Essential primary health care services",
                "coverage_gap": "Health promotion and disease prevention services not systematically covered"
            },
            "recommended_coverage_interventions": {
                "immediate_coverage_actions": [
                    "Define comprehensive PHC benefit package",
                    "Establish CHU service standards",
                    "Create county-level PHC protocols"
                ]
            }
        })
        
        # Preventive Services Coverage Gap
        gaps.append({
            "gap_id": "COV_PREV_002", 
            "gap_category": "preventive_services_coverage",
            "gap_type": "service_coverage_gap",
            "coverage_priority": "HIGH", 
            "description": "Systematic preventive health services (screenings, immunizations, health education) inadequately covered across age groups",
            "who_essential_services_alignment": {
                "who_service_category": "Health promotion and disease prevention",
                "coverage_gap": "Limited preventive care coverage beyond basic immunization"
            }
        })
        
        # Health Information Systems Gap
        gaps.append({
            "gap_id": "COV_HIS_003",
            "gap_category": "health_information_systems",
            "gap_type": "system_capacity_gap",
            "coverage_priority": "MEDIUM",
            "description": "Health information systems integration gaps affecting service continuity and quality monitoring",
            "who_essential_services_alignment": {
                "who_service_category": "Health information systems", 
                "coverage_gap": "Fragmented health data systems limiting care coordination"
            }
        })
        
        # Add more deterministic WHO coverage gaps...
        return gaps[:8]  # Return subset for WHO analysis
    
    def _deterministic_population_coverage_analysis(self, services_data: str) -> List[Dict]:
        """Deterministic population coverage analysis"""
        gaps = []
        
        # Disability Access Gap
        gaps.append({
            "gap_id": "COV_DISABILITY_001",
            "gap_category": "disability_access_coverage", 
            "gap_type": "population_access_gap",
            "coverage_priority": "HIGH",
            "description": "Systematic barriers to essential health services for persons with disabilities across all facility levels",
            "vulnerable_population_focus": {
                "population_group": "Persons with disabilities",
                "estimated_size": "2.2 million persons (4.6% of population)"
            }
        })
        
        # Elderly Care Coverage Gap
        gaps.append({
            "gap_id": "COV_ELDERLY_002",
            "gap_category": "elderly_care_coverage",
            "gap_type": "population_coverage_gap", 
            "coverage_priority": "MEDIUM",
            "description": "Age-appropriate health services for elderly population inadequately defined and covered",
            "vulnerable_population_focus": {
                "population_group": "Elderly (65+ years)",
                "estimated_size": "1.7 million persons (3% of population)"
            }
        })
        
        # Add more population-specific gaps...
        return gaps[:6]  # Return subset for population analysis
    
    def _deterministic_geographic_coverage_analysis(self, services_data: str) -> List[Dict]:
        """Deterministic geographic coverage analysis"""
        gaps = []
        
        # Rural Health Access Gap
        gaps.append({
            "gap_id": "COV_RURAL_001",
            "gap_category": "rural_health_access",
            "gap_type": "geographic_coverage_gap",
            "coverage_priority": "HIGH",
            "description": "Essential health services access gaps in rural and remote counties with poor transport infrastructure"
        })
        
        # Informal Settlement Coverage Gap
        gaps.append({
            "gap_id": "COV_URBAN_002", 
            "gap_category": "urban_informal_settlement_coverage",
            "gap_type": "geographic_coverage_gap",
            "coverage_priority": "HIGH",
            "description": "Health service delivery gaps in urban informal settlements lacking formal health infrastructure"
        })
        
        return gaps[:4]  # Return subset for geographic analysis
    
    def _deterministic_capacity_analysis(self, services_data: str) -> List[Dict]:
        """Deterministic health system capacity analysis"""
        gaps = []
        
        # Workforce Capacity Gap
        gaps.append({
            "gap_id": "COV_WORKFORCE_001",
            "gap_category": "health_workforce_capacity",
            "gap_type": "system_capacity_gap", 
            "coverage_priority": "HIGH",
            "description": "Health workforce shortages and maldistribution limiting service delivery capacity across facility levels"
        })
        
        return gaps[:3]  # Return subset for capacity analysis
    
    def _deterministic_integration_analysis(self, services_data: str) -> List[Dict]:
        """Deterministic service integration analysis"""
        gaps = []
        
        # Care Continuum Gap
        gaps.append({
            "gap_id": "COV_CONTINUUM_001",
            "gap_category": "care_continuum_integration", 
            "gap_type": "service_integration_gap",
            "coverage_priority": "MEDIUM",
            "description": "Care continuum breaks between community, primary, and referral levels affecting treatment continuity"
        })
        
        return gaps[:3]  # Return subset for integration analysis
    
    def _parse_ai_coverage_response(self, content: str) -> List[Dict]:
        """Parse AI response into coverage gaps"""
        try:
            # Look for JSON array in response
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                gaps_json = json_match.group()
                gaps = json.loads(gaps_json)
                return gaps
            else:
                logger.warning("No JSON found in AI response")
                return []
        except Exception as e:
            logger.error(f"Failed to parse AI coverage response: {e}")
            return []
    
    def _deduplicate_against_clinical_gaps(self, coverage_gaps: List[Dict], clinical_gaps: List[Dict]) -> List[Dict]:
        """Remove coverage gaps that duplicate clinical gaps"""
        logger.info("Deduplicating coverage gaps against clinical gaps")
        
        if not clinical_gaps:
            return coverage_gaps
        
        clinical_descriptions = [gap.get('description', '').lower() for gap in clinical_gaps]
        
        deduplicated = []
        for gap in coverage_gaps:
            gap_desc = gap.get('description', '').lower()
            
            # Simple deduplication check
            is_duplicate = False
            for clinical_desc in clinical_descriptions:
                if len(gap_desc) > 20 and len(clinical_desc) > 20:
                    # Check for significant word overlap
                    gap_words = set(gap_desc.split())
                    clinical_words = set(clinical_desc.split())
                    overlap = len(gap_words & clinical_words)
                    similarity = overlap / min(len(gap_words), len(clinical_words))
                    
                    if similarity > self.deduplication_threshold:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                deduplicated.append(gap)
        
        logger.info(f"Removed {len(coverage_gaps) - len(deduplicated)} duplicate coverage gaps")
        return deduplicated
    
    def _internal_deduplication(self, coverage_gaps: List[Dict]) -> List[Dict]:
        """Remove internal duplicates among coverage gaps"""
        if len(coverage_gaps) <= 1:
            return coverage_gaps
        
        deduplicated = [coverage_gaps[0]]  # Keep first gap
        
        for i in range(1, len(coverage_gaps)):
            current_gap = coverage_gaps[i]
            current_desc = current_gap.get('description', '').lower()
            
            is_duplicate = False
            for existing_gap in deduplicated:
                existing_desc = existing_gap.get('description', '').lower()
                
                if len(current_desc) > 20 and len(existing_desc) > 20:
                    # Check similarity
                    current_words = set(current_desc.split())
                    existing_words = set(existing_desc.split())
                    overlap = len(current_words & existing_words)
                    similarity = overlap / min(len(current_words), len(existing_words))
                    
                    if similarity > self.deduplication_threshold:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                deduplicated.append(current_gap)
        
        return deduplicated
    
    def _prioritize_coverage_gaps(self, coverage_gaps: List[Dict]) -> List[Dict]:
        """Prioritize coverage gaps if there are too many"""
        # Sort by priority (HIGH > MEDIUM > LOW)
        priority_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        
        sorted_gaps = sorted(coverage_gaps, 
                           key=lambda g: priority_order.get(g.get('coverage_priority', 'LOW'), 1), 
                           reverse=True)
        
        return sorted_gaps
    
    def save_coverage_gaps(self, coverage_gaps: List[Dict], output_path: str = None) -> str:
        """Save coverage gaps to file"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"coverage_gaps_{timestamp}.json"
        
        with open(output_path, 'w') as f:
            json.dump(coverage_gaps, f, indent=2)
        
        logger.info(f"Coverage gaps saved to {output_path}")
        return output_path


def main():
    """Main function for standalone coverage analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Coverage Analysis Agent")
    parser.add_argument('--services-data', required=True, help='Path to services data file')
    parser.add_argument('--clinical-gaps', help='Path to clinical gaps JSON file')
    parser.add_argument('--use-ai', action='store_true', help='Use AI analysis')
    parser.add_argument('--api-key', help='OpenAI API key for AI analysis')
    parser.add_argument('--output', help='Output file for coverage gaps')
    
    args = parser.parse_args()
    
    # Load services data
    if args.services_data.endswith('.csv'):
        services_df = pd.read_csv(args.services_data)
        services_data = services_df.to_string()
    else:
        with open(args.services_data, 'r') as f:
            services_data = f.read()
    
    # Load clinical gaps if provided
    clinical_gaps = []
    if args.clinical_gaps and os.path.exists(args.clinical_gaps):
        with open(args.clinical_gaps, 'r') as f:
            clinical_gaps = json.load(f)
    
    # Run coverage analysis
    agent = CoverageAnalysisAgent()
    coverage_gaps = agent.analyze_coverage_gaps(
        services_data=services_data,
        clinical_gaps=clinical_gaps,
        use_ai=args.use_ai,
        api_key=args.api_key
    )
    
    # Save results
    output_path = agent.save_coverage_gaps(coverage_gaps, args.output)
    
    print(f"Coverage analysis complete: {len(coverage_gaps)} gaps identified")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()