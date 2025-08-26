#!/usr/bin/env python3
"""
VALIDATION FRAMEWORK AGENT
Comprehensive validation framework to preserve clinical excellence while enabling Coverage Analysis integration

This framework ensures:
1. Clinical analysis excellence (5 gaps + 6 contradictions) is preserved
2. Coverage Analysis Agent can be safely integrated to reach ~30-35 total gaps
3. No regression in clinical quality or system performance
4. Automated rollback capabilities if validation fails
"""

import json
import pandas as pd
import numpy as np
import os
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ValidationMetrics:
    """Core metrics for system validation"""
    clinical_gap_count: int = 0
    clinical_contradiction_count: int = 0
    total_gap_count: int = 0
    clinical_quality_score: float = 0.0
    coverage_completeness_score: float = 0.0
    deduplication_effectiveness: float = 0.0
    prompt_stability_score: float = 0.0
    kenya_context_integration_score: float = 0.0
    validation_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'clinical_gap_count': self.clinical_gap_count,
            'clinical_contradiction_count': self.clinical_contradiction_count,
            'total_gap_count': self.total_gap_count,
            'clinical_quality_score': self.clinical_quality_score,
            'coverage_completeness_score': self.coverage_completeness_score,
            'deduplication_effectiveness': self.deduplication_effectiveness,
            'prompt_stability_score': self.prompt_stability_score,
            'kenya_context_integration_score': self.kenya_context_integration_score,
            'validation_timestamp': self.validation_timestamp.isoformat()
        }

@dataclass  
class GoldStandardBaseline:
    """Captures the gold standard clinical performance to preserve"""
    clinical_gaps: List[Dict] = field(default_factory=list)
    clinical_contradictions: List[Dict] = field(default_factory=list)
    clinical_personas: List[str] = field(default_factory=lambda: ["Dr. Grace Kiprotich", "Dr. Amina Hassan"])
    kenya_context_elements: List[str] = field(default_factory=list)
    quality_benchmarks: ValidationMetrics = field(default_factory=ValidationMetrics)
    baseline_timestamp: datetime = field(default_factory=datetime.now)
    
    def save_to_file(self, filepath: str) -> None:
        """Save baseline to JSON file"""
        data = {
            'clinical_gaps': self.clinical_gaps,
            'clinical_contradictions': self.clinical_contradictions,
            'clinical_personas': self.clinical_personas,
            'kenya_context_elements': self.kenya_context_elements,
            'quality_benchmarks': self.quality_benchmarks.to_dict(),
            'baseline_timestamp': self.baseline_timestamp.isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Gold standard baseline saved to {filepath}")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'clinical_gaps': self.clinical_gaps,
            'clinical_contradictions': self.clinical_contradictions,
            'clinical_personas': self.clinical_personas,
            'kenya_context_elements': self.kenya_context_elements,
            'quality_benchmarks': self.quality_benchmarks.to_dict(),
            'baseline_timestamp': self.baseline_timestamp.isoformat()
        }

class ValidationTest(ABC):
    """Abstract base class for validation tests"""
    
    @abstractmethod
    def run_test(self, current_results: Dict, baseline: GoldStandardBaseline) -> Tuple[bool, str, float]:
        """
        Run validation test
        Returns: (passed, message, score)
        """
        pass
    
    @abstractmethod
    def get_test_name(self) -> str:
        """Get test name"""
        pass

class ClinicalGapCountTest(ValidationTest):
    """Ensures clinical gap count remains around 5 (±2)"""
    
    def run_test(self, current_results: Dict, baseline: GoldStandardBaseline) -> Tuple[bool, str, float]:
        current_count = len(current_results.get('clinical_gaps', []))
        baseline_count = len(baseline.clinical_gaps)
        
        # Allow ±2 variation from baseline (target ~5)
        tolerance = 2
        passed = abs(current_count - baseline_count) <= tolerance
        
        score = 1.0 if passed else max(0.0, 1.0 - abs(current_count - baseline_count) / 10.0)
        
        message = f"Clinical gaps: {current_count} (baseline: {baseline_count}, tolerance: ±{tolerance})"
        
        return passed, message, score
    
    def get_test_name(self) -> str:
        return "Clinical Gap Count Preservation"

class ClinicalContradictionCountTest(ValidationTest):
    """Ensures clinical contradiction count remains around 6 (±2)"""
    
    def run_test(self, current_results: Dict, baseline: GoldStandardBaseline) -> Tuple[bool, str, float]:
        current_count = len(current_results.get('clinical_contradictions', []))
        baseline_count = len(baseline.clinical_contradictions)
        
        # Allow ±2 variation from baseline (target ~6)
        tolerance = 2
        passed = abs(current_count - baseline_count) <= tolerance
        
        score = 1.0 if passed else max(0.0, 1.0 - abs(current_count - baseline_count) / 10.0)
        
        message = f"Clinical contradictions: {current_count} (baseline: {baseline_count}, tolerance: ±{tolerance})"
        
        return passed, message, score
    
    def get_test_name(self) -> str:
        return "Clinical Contradiction Count Preservation"

class ClinicalQualityTest(ValidationTest):
    """Validates clinical quality using evidence base and Kenya context"""
    
    def run_test(self, current_results: Dict, baseline: GoldStandardBaseline) -> Tuple[bool, str, float]:
        clinical_gaps = current_results.get('clinical_gaps', [])
        clinical_contradictions = current_results.get('clinical_contradictions', [])
        
        quality_scores = []
        
        # Check clinical gaps quality
        for gap in clinical_gaps:
            score = self._assess_clinical_gap_quality(gap)
            quality_scores.append(score)
        
        # Check clinical contradictions quality  
        for contradiction in clinical_contradictions:
            score = self._assess_clinical_contradiction_quality(contradiction)
            quality_scores.append(score)
        
        overall_score = np.mean(quality_scores) if quality_scores else 0.0
        passed = overall_score >= 0.8  # Require 80% quality threshold
        
        message = f"Clinical quality score: {overall_score:.3f} (threshold: 0.8)"
        
        return passed, message, overall_score
    
    def _assess_clinical_gap_quality(self, gap: Dict) -> float:
        """Assess quality of a clinical gap"""
        score = 0.0
        
        # Check for evidence base
        if gap.get('clinical_evidence_base') and len(gap['clinical_evidence_base']) > 0:
            score += 0.3
            
        # Check for Kenya context integration
        if gap.get('kenya_context_integration') and len(gap['kenya_context_integration']) > 0:
            score += 0.3
            
        # Check for epidemiological context
        if gap.get('kenya_epidemiological_context') and len(gap['kenya_epidemiological_context']) > 0:
            score += 0.2
            
        # Check for implementation feasibility
        if gap.get('implementation_feasibility') and len(gap['implementation_feasibility']) > 0:
            score += 0.2
            
        return score
    
    def _assess_clinical_contradiction_quality(self, contradiction: Dict) -> float:
        """Assess quality of a clinical contradiction"""
        score = 0.0
        
        # Check medical analysis depth
        if contradiction.get('medical_analysis') and len(contradiction['medical_analysis']) > 0:
            score += 0.4
            
        # Check patient safety impact
        if contradiction.get('patient_safety_impact') and len(contradiction['patient_safety_impact']) > 0:
            score += 0.3
            
        # Check Kenya health system impact
        if contradiction.get('kenya_health_system_impact') and len(contradiction['kenya_health_system_impact']) > 0:
            score += 0.3
            
        return score
    
    def get_test_name(self) -> str:
        return "Clinical Quality Assessment"

class ClinicalPersonaPreservationTest(ValidationTest):
    """Ensures Dr. Grace Kiprotich and Dr. Amina Hassan personas are maintained"""
    
    def run_test(self, current_results: Dict, baseline: GoldStandardBaseline) -> Tuple[bool, str, float]:
        # Check prompts or analysis content for persona references
        analysis_content = str(current_results)
        
        persona_scores = []
        for persona in baseline.clinical_personas:
            if persona in analysis_content:
                persona_scores.append(1.0)
            else:
                persona_scores.append(0.0)
        
        overall_score = np.mean(persona_scores)
        passed = overall_score >= 1.0  # All personas must be present
        
        message = f"Clinical personas preserved: {overall_score:.1%} ({', '.join(baseline.clinical_personas)})"
        
        return passed, message, overall_score
    
    def get_test_name(self) -> str:
        return "Clinical Persona Preservation"

class KenyaContextIntegrationTest(ValidationTest):
    """Validates Kenya-specific health context integration"""
    
    def run_test(self, current_results: Dict, baseline: GoldStandardBaseline) -> Tuple[bool, str, float]:
        clinical_gaps = current_results.get('clinical_gaps', [])
        
        kenya_context_scores = []
        
        for gap in clinical_gaps:
            score = self._assess_kenya_context(gap)
            kenya_context_scores.append(score)
        
        overall_score = np.mean(kenya_context_scores) if kenya_context_scores else 0.0
        passed = overall_score >= 0.8
        
        message = f"Kenya context integration: {overall_score:.3f} (threshold: 0.8)"
        
        return passed, message, overall_score
    
    def _assess_kenya_context(self, gap: Dict) -> float:
        """Assess Kenya context integration for a gap"""
        score = 0.0
        
        # Check for 56.4M population reference
        content = str(gap)
        if "56.4" in content or "population" in content.lower():
            score += 0.2
            
        # Check for county-level considerations
        if "county" in content.lower() or "counties" in content.lower():
            score += 0.2
            
        # Check for disease burden data
        if gap.get('kenya_epidemiological_context'):
            score += 0.3
            
        # Check for health system tier references
        if "level" in content.lower() and ("facility" in content.lower() or "hospital" in content.lower()):
            score += 0.3
            
        return min(score, 1.0)
    
    def get_test_name(self) -> str:
        return "Kenya Context Integration"

class TotalGapCountTest(ValidationTest):
    """Ensures total gaps reach target range of 30-35"""
    
    def run_test(self, current_results: Dict, baseline: GoldStandardBaseline) -> Tuple[bool, str, float]:
        clinical_count = len(current_results.get('clinical_gaps', []))
        coverage_count = len(current_results.get('coverage_gaps', []))
        total_count = clinical_count + coverage_count
        
        target_min = 30
        target_max = 35
        
        if target_min <= total_count <= target_max:
            passed = True
            score = 1.0
        else:
            passed = False
            # Score decreases based on distance from target range
            if total_count < target_min:
                score = max(0.0, total_count / target_min)
            else:
                score = max(0.0, 1.0 - (total_count - target_max) / 20.0)
        
        message = f"Total gaps: {total_count} (target: {target_min}-{target_max}, clinical: {clinical_count}, coverage: {coverage_count})"
        
        return passed, message, score
    
    def get_test_name(self) -> str:
        return "Total Gap Count Target"

class DeduplicationEffectivenessTest(ValidationTest):
    """Tests that deduplication prevents duplicate insights"""
    
    def run_test(self, current_results: Dict, baseline: GoldStandardBaseline) -> Tuple[bool, str, float]:
        all_gaps = current_results.get('clinical_gaps', []) + current_results.get('coverage_gaps', [])
        all_contradictions = current_results.get('clinical_contradictions', [])
        
        # Check for duplicate descriptions (simplified similarity check)
        gap_descriptions = [gap.get('description', '') for gap in all_gaps]
        contradiction_descriptions = [c.get('description', '') for c in all_contradictions]
        
        # Simple duplicate detection
        gap_duplicates = len(gap_descriptions) - len(set(gap_descriptions))
        contradiction_duplicates = len(contradiction_descriptions) - len(set(contradiction_descriptions))
        
        total_duplicates = gap_duplicates + contradiction_duplicates
        total_items = len(gap_descriptions) + len(contradiction_descriptions)
        
        if total_items == 0:
            score = 1.0
        else:
            score = max(0.0, 1.0 - (total_duplicates / total_items))
        
        passed = total_duplicates == 0
        
        message = f"Deduplication effectiveness: {score:.3f} ({total_duplicates} duplicates out of {total_items} items)"
        
        return passed, message, score
    
    def get_test_name(self) -> str:
        return "Deduplication Effectiveness"

class ValidationFrameworkAgent:
    """Main validation framework agent"""
    
    def __init__(self, baseline_path: str = "validation_baseline.json"):
        self.baseline_path = baseline_path
        self.baseline: Optional[GoldStandardBaseline] = None
        self.test_suite: List[ValidationTest] = [
            ClinicalGapCountTest(),
            ClinicalContradictionCountTest(), 
            ClinicalQualityTest(),
            ClinicalPersonaPreservationTest(),
            KenyaContextIntegrationTest(),
            TotalGapCountTest(),
            DeduplicationEffectivenessTest()
        ]
        self.validation_history: List[Dict] = []
    
    def create_baseline(self, analyzer_results: Dict) -> GoldStandardBaseline:
        """Create gold standard baseline from current excellent results"""
        logger.info("Creating gold standard baseline from current results")
        
        baseline = GoldStandardBaseline()
        
        # Extract clinical gaps and contradictions
        baseline.clinical_gaps = analyzer_results.get('clinical_gaps', [])
        baseline.clinical_contradictions = analyzer_results.get('clinical_contradictions', [])
        
        # Extract Kenya context elements (simplified)
        kenya_elements = []
        all_content = str(analyzer_results)
        if "56.4" in all_content:
            kenya_elements.append("population_56_4_million")
        if "county" in all_content.lower():
            kenya_elements.append("county_level_analysis")
        if "level" in all_content.lower() and "facility" in all_content.lower():
            kenya_elements.append("health_facility_levels")
            
        baseline.kenya_context_elements = kenya_elements
        
        # Calculate quality benchmarks
        metrics = ValidationMetrics()
        metrics.clinical_gap_count = len(baseline.clinical_gaps)
        metrics.clinical_contradiction_count = len(baseline.clinical_contradictions)
        metrics.clinical_quality_score = 1.0  # Assume current is gold standard
        metrics.kenya_context_integration_score = 1.0
        
        baseline.quality_benchmarks = metrics
        
        # Save baseline
        baseline.save_to_file(self.baseline_path)
        self.baseline = baseline
        
        return baseline
    
    def load_baseline(self) -> Optional[GoldStandardBaseline]:
        """Load existing baseline"""
        if not os.path.exists(self.baseline_path):
            logger.warning(f"No baseline found at {self.baseline_path}")
            return None
            
        with open(self.baseline_path, 'r') as f:
            data = json.load(f)
        
        baseline = GoldStandardBaseline()
        baseline.clinical_gaps = data.get('clinical_gaps', [])
        baseline.clinical_contradictions = data.get('clinical_contradictions', [])
        baseline.clinical_personas = data.get('clinical_personas', [])
        baseline.kenya_context_elements = data.get('kenya_context_elements', [])
        
        # Load metrics
        metrics_data = data.get('quality_benchmarks', {})
        if 'validation_timestamp' in metrics_data and isinstance(metrics_data['validation_timestamp'], str):
            # Convert string back to datetime
            metrics_data['validation_timestamp'] = datetime.fromisoformat(metrics_data['validation_timestamp'])
        baseline.quality_benchmarks = ValidationMetrics(**{k: v for k, v in metrics_data.items() if k in ValidationMetrics.__dataclass_fields__})
        
        self.baseline = baseline
        logger.info(f"Loaded baseline with {len(baseline.clinical_gaps)} gaps, {len(baseline.clinical_contradictions)} contradictions")
        
        return baseline
    
    def run_validation(self, current_results: Dict) -> Tuple[bool, Dict]:
        """Run complete validation suite"""
        if not self.baseline:
            logger.error("No baseline loaded. Create baseline first.")
            return False, {}
        
        logger.info("Running validation suite...")
        
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'overall_passed': True,
            'test_results': {},
            'summary': {},
            'recommendations': []
        }
        
        all_scores = []
        failed_tests = []
        
        for test in self.test_suite:
            test_name = test.get_test_name()
            logger.info(f"Running test: {test_name}")
            
            try:
                passed, message, score = test.run_test(current_results, self.baseline)
                
                validation_results['test_results'][test_name] = {
                    'passed': passed,
                    'message': message, 
                    'score': score
                }
                
                all_scores.append(score)
                
                if not passed:
                    failed_tests.append(test_name)
                    validation_results['overall_passed'] = False
                
                logger.info(f"  {test_name}: {'PASS' if passed else 'FAIL'} (score: {score:.3f}) - {message}")
                
            except Exception as e:
                logger.error(f"Test {test_name} failed with error: {e}")
                validation_results['test_results'][test_name] = {
                    'passed': False,
                    'message': f"Error: {e}",
                    'score': 0.0
                }
                all_scores.append(0.0)
                failed_tests.append(test_name)
                validation_results['overall_passed'] = False
        
        # Calculate summary metrics
        validation_results['summary'] = {
            'overall_score': np.mean(all_scores),
            'tests_passed': len(self.test_suite) - len(failed_tests),
            'tests_total': len(self.test_suite),
            'failed_tests': failed_tests
        }
        
        # Generate recommendations
        if failed_tests:
            validation_results['recommendations'] = self._generate_recommendations(failed_tests, validation_results['test_results'])
        
        # Store in history
        self.validation_history.append(validation_results)
        
        logger.info(f"Validation complete. Overall: {'PASS' if validation_results['overall_passed'] else 'FAIL'} "
                   f"(score: {validation_results['summary']['overall_score']:.3f})")
        
        return validation_results['overall_passed'], validation_results
    
    def _generate_recommendations(self, failed_tests: List[str], test_results: Dict) -> List[str]:
        """Generate recommendations based on failed tests"""
        recommendations = []
        
        if "Clinical Gap Count Preservation" in failed_tests:
            recommendations.append("Adjust gap analysis parameters to maintain ~5 high-priority clinical gaps")
        
        if "Clinical Contradiction Count Preservation" in failed_tests:
            recommendations.append("Review contradiction detection logic to preserve ~6 clinical contradictions")
        
        if "Clinical Quality Assessment" in failed_tests:
            recommendations.append("Enhance clinical gap/contradiction quality with better evidence base and Kenya context")
        
        if "Clinical Persona Preservation" in failed_tests:
            recommendations.append("Ensure Dr. Grace Kiprotich and Dr. Amina Hassan personas are maintained in prompts")
        
        if "Kenya Context Integration" in failed_tests:
            recommendations.append("Strengthen Kenya-specific health context (population data, county analysis, facility levels)")
        
        if "Total Gap Count Target" in failed_tests:
            recommendations.append("Adjust Coverage Analysis Agent to reach target of 30-35 total gaps")
        
        if "Deduplication Effectiveness" in failed_tests:
            recommendations.append("Improve deduplication algorithms to prevent duplicate insights")
        
        return recommendations
    
    def generate_validation_report(self, validation_results: Dict, output_path: str = None) -> str:
        """Generate comprehensive validation report"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"validation_report_{timestamp}.md"
        
        report = []
        report.append("# Healthcare Policy Analysis System - Validation Report")
        report.append(f"Generated: {validation_results['timestamp']}")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        summary = validation_results['summary']
        overall_status = "✅ PASSED" if validation_results['overall_passed'] else "❌ FAILED"
        report.append(f"**Overall Status**: {overall_status}")
        report.append(f"**Overall Score**: {summary['overall_score']:.3f}/1.000")
        report.append(f"**Tests Passed**: {summary['tests_passed']}/{summary['tests_total']}")
        report.append("")
        
        if summary['failed_tests']:
            report.append("**Failed Tests**:")
            for test in summary['failed_tests']:
                report.append(f"- {test}")
            report.append("")
        
        # Detailed Test Results
        report.append("## Detailed Test Results")
        report.append("")
        
        for test_name, result in validation_results['test_results'].items():
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            report.append(f"### {test_name}")
            report.append(f"**Status**: {status}")
            report.append(f"**Score**: {result['score']:.3f}")
            report.append(f"**Details**: {result['message']}")
            report.append("")
        
        # Recommendations
        if validation_results.get('recommendations'):
            report.append("## Recommendations")
            for rec in validation_results['recommendations']:
                report.append(f"- {rec}")
            report.append("")
        
        # Baseline Information
        if self.baseline:
            report.append("## Gold Standard Baseline")
            report.append(f"**Clinical Gaps**: {len(self.baseline.clinical_gaps)}")
            report.append(f"**Clinical Contradictions**: {len(self.baseline.clinical_contradictions)}")
            report.append(f"**Clinical Personas**: {', '.join(self.baseline.clinical_personas)}")
            report.append(f"**Kenya Context Elements**: {len(self.baseline.kenya_context_elements)}")
            report.append("")
        
        report_content = "\n".join(report)
        
        with open(output_path, 'w') as f:
            f.write(report_content)
        
        logger.info(f"Validation report saved to {output_path}")
        return report_content
    
    def save_system_backup(self, backup_path: str = None) -> str:
        """Create backup of current system state"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"system_backup_{timestamp}.json"
        
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'baseline': self.baseline.to_dict() if self.baseline else None,
            'validation_history': self.validation_history
        }
        
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        logger.info(f"System backup saved to {backup_path}")
        return backup_path
    
    def rollback_instructions(self) -> Dict[str, str]:
        """Provide rollback instructions if validation fails"""
        return {
            'immediate_actions': [
                "Stop all analysis processes",
                "Restore from last known good backup",
                "Verify baseline system functionality"
            ],
            'component_rollback': [
                "Disable Coverage Analysis Agent integration",
                "Restore original clinical analysis prompts",
                "Reset deduplication parameters"
            ],
            'verification_steps': [
                "Run validation suite against restored system", 
                "Confirm clinical gap count ~5",
                "Confirm clinical contradiction count ~6",
                "Verify clinical quality metrics"
            ]
        }


def main():
    """Main function for standalone testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Healthcare Policy Analysis Validation Framework")
    parser.add_argument('--create-baseline', action='store_true', 
                       help='Create baseline from current system')
    parser.add_argument('--run-validation', action='store_true',
                       help='Run validation against current system')
    parser.add_argument('--baseline-path', default='validation_baseline.json',
                       help='Path to baseline file')
    parser.add_argument('--results-path', help='Path to current results JSON file')
    
    args = parser.parse_args()
    
    validator = ValidationFrameworkAgent(args.baseline_path)
    
    if args.create_baseline:
        if not args.results_path or not os.path.exists(args.results_path):
            print("Error: --results-path required for creating baseline")
            return
        
        with open(args.results_path, 'r') as f:
            results = json.load(f)
        
        baseline = validator.create_baseline(results)
        print(f"Baseline created with {len(baseline.clinical_gaps)} gaps and {len(baseline.clinical_contradictions)} contradictions")
    
    if args.run_validation:
        if not args.results_path or not os.path.exists(args.results_path):
            print("Error: --results-path required for validation")
            return
        
        validator.load_baseline()
        
        with open(args.results_path, 'r') as f:
            results = json.load(f)
        
        passed, validation_results = validator.run_validation(results)
        report = validator.generate_validation_report(validation_results)
        
        print(f"Validation {'PASSED' if passed else 'FAILED'}")
        print(f"Report saved to validation_report_*.md")


if __name__ == "__main__":
    main()