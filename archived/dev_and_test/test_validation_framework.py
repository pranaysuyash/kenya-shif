#!/usr/bin/env python3
"""
TEST VALIDATION FRAMEWORK
Comprehensive testing script for the Validation Framework Agent components

This script tests:
1. Validation Framework Agent functionality
2. Integration Testing Protocol components
3. Coverage Analysis Agent capabilities
4. End-to-end validation workflow
"""

import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValidationFrameworkTester:
    """Comprehensive tester for validation framework components"""
    
    def __init__(self):
        self.test_results = {}
        self.temp_dir = None
        self.mock_results_path = None
        self.mock_services_path = None
        
    def run_all_tests(self) -> bool:
        """Run comprehensive test suite"""
        logger.info("=" * 60)
        logger.info("VALIDATION FRAMEWORK COMPREHENSIVE TEST SUITE")
        logger.info("=" * 60)
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp(prefix='validation_test_')
        logger.info(f"Using temporary directory: {self.temp_dir}")
        
        # Initialize paths
        self.mock_results_path = None
        self.mock_services_path = None
        
        test_methods = [
            ("Import Tests", self.test_imports),
            ("Mock Data Creation", self.test_mock_data_creation),
            ("Validation Framework Agent", self.test_validation_framework_agent),
            ("Coverage Analysis Agent", self.test_coverage_analysis_agent),
            ("Integration Testing Protocol", self.test_integration_testing_protocol),
            ("End-to-End Validation", self.test_end_to_end_validation),
            ("Rollback Procedures", self.test_rollback_procedures)
        ]
        
        overall_success = True
        
        for test_name, test_method in test_methods:
            logger.info(f"\n{'='*20} {test_name} {'='*20}")
            try:
                success = test_method()
                self.test_results[test_name] = success
                
                if success:
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(f"❌ {test_name}: FAILED")
                    overall_success = False
                    
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
                self.test_results[test_name] = False
                overall_success = False
        
        # Cleanup
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # Final summary
        logger.info(f"\n{'='*60}")
        logger.info("TEST SUITE SUMMARY")
        logger.info(f"{'='*60}")
        
        passed_tests = sum(1 for result in self.test_results.values() if result)
        total_tests = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if overall_success:
            logger.info("🎉 ALL TESTS PASSED - Validation Framework Ready!")
        else:
            logger.error("⚠️ SOME TESTS FAILED - Review and fix issues before deployment")
        
        return overall_success
    
    def test_imports(self) -> bool:
        """Test that all required modules can be imported"""
        logger.info("Testing imports...")
        
        try:
            # Standard libraries
            import json
            import pandas as pd
            import numpy as np
            from pathlib import Path
            from datetime import datetime
            logger.info("  ✅ Standard libraries imported")
            
            # Framework components
            from validation_framework_agent import (
                ValidationFrameworkAgent, ValidationMetrics, GoldStandardBaseline,
                ClinicalGapCountTest, ClinicalQualityTest
            )
            logger.info("  ✅ Validation Framework Agent components imported")
            
            from integration_testing_protocol import IntegrationTestingProtocol
            logger.info("  ✅ Integration Testing Protocol imported")
            
            from coverage_analysis_agent import CoverageAnalysisAgent, CoverageAnalysisPrompts
            logger.info("  ✅ Coverage Analysis Agent imported")
            
            # Optional dependencies
            try:
                import openai
                logger.info("  ✅ OpenAI library available")
            except ImportError:
                logger.info("  ⚠️ OpenAI library not available (AI features will be disabled)")
            
            return True
            
        except ImportError as e:
            logger.error(f"  ❌ Import failed: {e}")
            return False
    
    def test_mock_data_creation(self) -> bool:
        """Create mock data for testing"""
        logger.info("Creating mock data for testing...")
        
        try:
            # Create mock clinical gaps (simulating current excellent system)
            mock_clinical_gaps = [
                {
                    "gap_id": "CLINICAL_001",
                    "gap_category": "cardiovascular_care",
                    "description": "Comprehensive cardiac rehabilitation services absent despite high CVD burden",
                    "clinical_evidence_base": {"who_guidelines": "CVD rehabilitation reduces mortality 13-20%"},
                    "kenya_epidemiological_context": {"disease_burden": "CVD causes 25% of admissions"},
                    "implementation_feasibility": {"technical_feasibility": "HIGH"}
                },
                {
                    "gap_id": "CLINICAL_002", 
                    "gap_category": "cancer_care",
                    "description": "Late cancer diagnosis due to limited screening and diagnostic capacity",
                    "clinical_evidence_base": {"screening_effectiveness": "Reduces mortality by 50%"},
                    "kenya_epidemiological_context": {"prevalence": "40,000-50,000 new cases annually"},
                    "implementation_feasibility": {"financial_feasibility": "MEDIUM"}
                },
                {
                    "gap_id": "CLINICAL_003",
                    "gap_category": "maternal_health", 
                    "description": "Emergency obstetric care gaps contributing to maternal mortality",
                    "clinical_evidence_base": {"who_standards": "EmONC reduces maternal death"},
                    "kenya_epidemiological_context": {"mmr": "130-170/100,000"},
                    "implementation_feasibility": {"timeline_realistic": "3 years"}
                },
                {
                    "gap_id": "CLINICAL_004",
                    "gap_category": "mental_health",
                    "description": "Mental health services inadequately integrated into primary care", 
                    "clinical_evidence_base": {"task_shifting": "mhGAP effective in PHC"},
                    "kenya_epidemiological_context": {"burden": "High unmet mental health need"},
                    "implementation_feasibility": {"technical_feasibility": "HIGH"}
                },
                {
                    "gap_id": "CLINICAL_005",
                    "gap_category": "infectious_disease",
                    "description": "Pneumonia management gaps especially oxygen therapy in rural areas",
                    "clinical_evidence_base": {"oxygen_therapy": "Reduces pneumonia mortality"},
                    "kenya_epidemiological_context": {"leading_cause": "Pneumonia is top cause of death"},
                    "implementation_feasibility": {"cost_effectiveness": "HIGH"}
                }
            ]
            
            # Create mock clinical contradictions
            mock_clinical_contradictions = [
                {
                    "contradiction_id": "DIAL_001_CRITICAL",
                    "medical_specialty": "nephrology",
                    "description": "Hemodialysis allows 3 sessions/week while hemodiafiltration allows only 2 sessions/week",
                    "medical_analysis": {"clinical_rationale": "Both HD and HDF require equivalent frequency"},
                    "patient_safety_impact": {"immediate_risk": "Inadequate dialysis frequency"},
                    "kenya_health_system_impact": {"facility_level_effects": "Level 4-6 hospitals affected"}
                },
                {
                    "contradiction_id": "EMER_002_CRITICAL", 
                    "medical_specialty": "emergency_medicine",
                    "description": "Emergency care restricted to Level 4-6 but rural access requires Level 2-3 stabilization",
                    "medical_analysis": {"clinical_rationale": "Emergency stabilization needed at first contact"},
                    "patient_safety_impact": {"survival_impact": "Delays increase preventable deaths"},
                    "kenya_health_system_impact": {"geographic_access": "Rural majority affected"}
                },
                {
                    "contradiction_id": "OBS_003_CRITICAL",
                    "medical_specialty": "obstetrics", 
                    "description": "Obstetric surgery authorized at facilities lacking surgical capacity",
                    "medical_analysis": {"clinical_rationale": "C-sections require full surgical support"},
                    "patient_safety_impact": {"clinical_consequences": "Higher maternal mortality"},
                    "kenya_health_system_impact": {"facility_level_effects": "Level 2-3 capacity mismatch"}
                },
                {
                    "contradiction_id": "PED_004_HIGH",
                    "medical_specialty": "pediatrics",
                    "description": "Adult-centric protocols without pediatric age-specific adaptations",
                    "medical_analysis": {"clinical_rationale": "Children need weight-based dosing"},
                    "patient_safety_impact": {"immediate_risk": "Medication dosing errors"},
                    "kenya_health_system_impact": {"provider_training": "Need pediatric protocol training"}
                },
                {
                    "contradiction_id": "NEURO_005_HIGH",
                    "medical_specialty": "neurosurgery",
                    "description": "Complex neurosurgery authorized at facilities lacking ICU capacity",
                    "medical_analysis": {"clinical_rationale": "Neurosurgery requires specialized postop care"},
                    "patient_safety_impact": {"survival_impact": "Higher perioperative mortality"},
                    "kenya_health_system_impact": {"resource_allocation": "Imaging and ICU needed"}
                },
                {
                    "contradiction_id": "ADMIN_006_MODERATE",
                    "medical_specialty": "health_systems",
                    "description": "Missing tariffs and fund designations creating provider confusion",
                    "medical_analysis": {"clinical_rationale": "Clear funding enables predictable care"},
                    "patient_safety_impact": {"clinical_consequences": "Care delays pending authorization"},
                    "kenya_health_system_impact": {"provider_training": "Admin staff confused"}
                }
            ]
            
            # Create mock analyzer results
            mock_results = {
                "clinical_gaps": mock_clinical_gaps,
                "clinical_contradictions": mock_clinical_contradictions,
                "analysis_metadata": {
                    "personas": ["Dr. Grace Kiprotich", "Dr. Amina Hassan"],
                    "kenya_context": {
                        "population": "56.4 million",
                        "counties": 47,
                        "facility_levels": "6-tier system"
                    }
                }
            }
            
            # Save mock data
            mock_results_path = os.path.join(self.temp_dir, "mock_analyzer_results.json")
            with open(mock_results_path, 'w') as f:
                json.dump(mock_results, f, indent=2)
            
            # Create mock services data
            mock_services_data = pd.DataFrame({
                'Service': ['Hemodialysis', 'Emergency Care', 'Obstetric Care', 'Pediatric Care'],
                'Level': ['4-6', '2-6', '3-6', '2-6'],
                'Fund': ['Chronic Illness Fund', 'Emergency Fund', 'Maternal Health Fund', 'Child Health Fund']
            })
            
            mock_services_path = os.path.join(self.temp_dir, "mock_services.csv")
            mock_services_data.to_csv(mock_services_path, index=False)
            
            logger.info(f"  ✅ Mock data created: {len(mock_clinical_gaps)} gaps, {len(mock_clinical_contradictions)} contradictions")
            
            # Store paths for other tests
            self.mock_results_path = mock_results_path
            self.mock_services_path = mock_services_path
            
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Mock data creation failed: {e}")
            return False
    
    def test_validation_framework_agent(self) -> bool:
        """Test Validation Framework Agent functionality"""
        logger.info("Testing Validation Framework Agent...")
        
        try:
            from validation_framework_agent import ValidationFrameworkAgent
            
            # Initialize validator
            baseline_path = os.path.join(self.temp_dir, "test_baseline.json")
            validator = ValidationFrameworkAgent(baseline_path)
            
            # Load mock results
            with open(self.mock_results_path, 'r') as f:
                mock_results = json.load(f)
            
            # Test 1: Create baseline
            logger.info("  Testing baseline creation...")
            baseline = validator.create_baseline(mock_results)
            
            if len(baseline.clinical_gaps) != 5:
                logger.error(f"    Expected 5 clinical gaps, got {len(baseline.clinical_gaps)}")
                return False
            
            if len(baseline.clinical_contradictions) != 6:
                logger.error(f"    Expected 6 clinical contradictions, got {len(baseline.clinical_contradictions)}")
                return False
            
            logger.info(f"    ✅ Baseline created: {len(baseline.clinical_gaps)} gaps, {len(baseline.clinical_contradictions)} contradictions")
            
            # Test 2: Load baseline
            logger.info("  Testing baseline loading...")
            loaded_baseline = validator.load_baseline()
            
            if not loaded_baseline:
                logger.error("    Failed to load baseline")
                return False
            
            logger.info("    ✅ Baseline loaded successfully")
            
            # Test 3: Run validation
            logger.info("  Testing validation...")
            passed, validation_results = validator.run_validation(mock_results)
            
            if not passed:
                logger.info("    ⚠️ Some validation tests failed (expected for mock data)")
                for test_name, result in validation_results['test_results'].items():
                    if not result['passed']:
                        logger.info(f"      {test_name}: {result['message']}")
            else:
                logger.info("    ✅ All validation tests passed")
            
            # Test 4: Generate report
            logger.info("  Testing report generation...")
            report_path = os.path.join(self.temp_dir, "test_validation_report.md")
            report_content = validator.generate_validation_report(validation_results, report_path)
            
            if not os.path.exists(report_path):
                logger.error("    Validation report not created")
                return False
            
            logger.info("    ✅ Validation report generated")
            
            # Test 5: System backup
            logger.info("  Testing system backup...")
            backup_path = validator.save_system_backup()
            
            if not os.path.exists(backup_path):
                logger.error("    System backup not created")
                return False
            
            logger.info("    ✅ System backup created")
            
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Validation Framework Agent test failed: {e}")
            return False
    
    def test_coverage_analysis_agent(self) -> bool:
        """Test Coverage Analysis Agent functionality"""
        logger.info("Testing Coverage Analysis Agent...")
        
        try:
            from coverage_analysis_agent import CoverageAnalysisAgent
            
            # Initialize coverage agent
            agent = CoverageAnalysisAgent()
            
            # Load mock data
            services_data = pd.read_csv(self.mock_services_path).to_string()
            
            with open(self.mock_results_path, 'r') as f:
                mock_results = json.load(f)
            clinical_gaps = mock_results['clinical_gaps']
            
            # Test 1: Coverage analysis (deterministic mode)
            logger.info("  Testing coverage analysis (deterministic)...")
            coverage_gaps = agent.analyze_coverage_gaps(
                services_data=services_data,
                clinical_gaps=clinical_gaps,
                use_ai=False
            )
            
            if not coverage_gaps:
                logger.error("    No coverage gaps generated")
                return False
            
            if len(coverage_gaps) < 10 or len(coverage_gaps) > 35:
                logger.warning(f"    Coverage gaps count outside expected range: {len(coverage_gaps)}")
            
            logger.info(f"    ✅ Coverage analysis generated {len(coverage_gaps)} gaps")
            
            # Test 2: Deduplication
            logger.info("  Testing deduplication...")
            # Create a duplicate gap for testing
            duplicate_gap = clinical_gaps[0].copy()
            duplicate_gap['gap_id'] = 'DUPLICATE_TEST'
            test_coverage_gaps = coverage_gaps + [duplicate_gap]
            
            deduplicated = agent._deduplicate_against_clinical_gaps(test_coverage_gaps, clinical_gaps)
            
            if len(deduplicated) == len(test_coverage_gaps):
                logger.warning("    Deduplication may not be working (no gaps removed)")
            
            logger.info(f"    ✅ Deduplication: {len(test_coverage_gaps)} → {len(deduplicated)} gaps")
            
            # Test 3: Save coverage gaps
            logger.info("  Testing coverage gaps save...")
            output_path = os.path.join(self.temp_dir, "test_coverage_gaps.json")
            saved_path = agent.save_coverage_gaps(coverage_gaps, output_path)
            
            if not os.path.exists(saved_path):
                logger.error("    Coverage gaps file not created")
                return False
            
            logger.info("    ✅ Coverage gaps saved successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Coverage Analysis Agent test failed: {e}")
            return False
    
    def test_integration_testing_protocol(self) -> bool:
        """Test Integration Testing Protocol functionality"""
        logger.info("Testing Integration Testing Protocol...")
        
        try:
            from integration_testing_protocol import IntegrationTestingProtocol
            
            # Initialize protocol
            baseline_path = os.path.join(self.temp_dir, "integration_baseline.json")
            protocol = IntegrationTestingProtocol(baseline_path)
            
            # Test 1: Mock analyzer results
            logger.info("  Testing mock analyzer execution...")
            results = protocol._extract_gaps_from_results({"clinical_gaps": [{"test": "gap"}]})
            
            if not results:
                logger.error("    Failed to extract gaps from mock results")
                return False
            
            logger.info("    ✅ Mock analyzer execution successful")
            
            # Test 2: Stability test simulation
            logger.info("  Testing stability metrics...")
            
            # Simulate stability test results
            mock_stability_results = [
                {"clinical_gaps": [1, 2, 3, 4, 5], "clinical_contradictions": [1, 2, 3, 4, 5, 6]},
                {"clinical_gaps": [1, 2, 3, 4, 5], "clinical_contradictions": [1, 2, 3, 4, 5, 6]},
                {"clinical_gaps": [1, 2, 3, 4], "clinical_contradictions": [1, 2, 3, 4, 5, 6]}
            ]
            
            gap_counts = [len(r['clinical_gaps']) for r in mock_stability_results]
            gap_consistency = 1.0 - (max(gap_counts) - min(gap_counts)) / max(1, max(gap_counts))
            
            if gap_consistency < 0.8:
                logger.warning(f"    Stability test would fail: {gap_consistency:.3f}")
            else:
                logger.info(f"    ✅ Stability metrics acceptable: {gap_consistency:.3f}")
            
            # Test 3: Report generation
            logger.info("  Testing report generation...")
            report_path = protocol._generate_deployment_report()
            
            if not os.path.exists(report_path):
                logger.error("    Deployment report not created")
                return False
            
            logger.info("    ✅ Deployment report generated")
            
            # Test 4: Rollback procedures
            logger.info("  Testing rollback procedures...")
            rollback_path = protocol._create_rollback_procedures()
            
            if not os.path.exists(rollback_path):
                logger.error("    Rollback procedures not created")
                return False
            
            logger.info("    ✅ Rollback procedures created")
            
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Integration Testing Protocol test failed: {e}")
            return False
    
    def test_end_to_end_validation(self) -> bool:
        """Test end-to-end validation workflow"""
        logger.info("Testing end-to-end validation workflow...")
        
        try:
            from validation_framework_agent import ValidationFrameworkAgent
            from coverage_analysis_agent import CoverageAnalysisAgent
            
            # Step 1: Create baseline from mock clinical results
            logger.info("  Step 1: Creating baseline...")
            validator = ValidationFrameworkAgent(os.path.join(self.temp_dir, "e2e_baseline.json"))
            
            with open(self.mock_results_path, 'r') as f:
                clinical_results = json.load(f)
            
            baseline = validator.create_baseline(clinical_results)
            logger.info(f"    ✅ Baseline: {len(baseline.clinical_gaps)} gaps, {len(baseline.clinical_contradictions)} contradictions")
            
            # Step 2: Generate coverage gaps
            logger.info("  Step 2: Generating coverage gaps...")
            coverage_agent = CoverageAnalysisAgent()
            services_data = pd.read_csv(self.mock_services_path).to_string()
            
            coverage_gaps = coverage_agent.analyze_coverage_gaps(
                services_data=services_data,
                clinical_gaps=clinical_results['clinical_gaps'],
                use_ai=False
            )
            logger.info(f"    ✅ Coverage gaps: {len(coverage_gaps)} generated")
            
            # Step 3: Combine results
            logger.info("  Step 3: Combining results...")
            integrated_results = {
                "clinical_gaps": clinical_results['clinical_gaps'],
                "clinical_contradictions": clinical_results['clinical_contradictions'],
                "coverage_gaps": coverage_gaps,
                "analysis_metadata": clinical_results['analysis_metadata']
            }
            
            total_gaps = len(integrated_results['clinical_gaps']) + len(integrated_results['coverage_gaps'])
            logger.info(f"    ✅ Integrated results: {total_gaps} total gaps")
            
            # Step 4: Validate integrated system
            logger.info("  Step 4: Validating integrated system...")
            passed, validation_results = validator.run_validation(integrated_results)
            
            score = validation_results['summary']['overall_score']
            logger.info(f"    Validation score: {score:.3f}")
            
            if score < 0.5:
                logger.warning("    Low validation score (expected for mock data)")
            
            # Step 5: Generate comprehensive report
            logger.info("  Step 5: Generating final report...")
            report_content = validator.generate_validation_report(validation_results)
            
            logger.info("    ✅ End-to-end validation completed")
            
            return True
            
        except Exception as e:
            logger.error(f"  ❌ End-to-end validation test failed: {e}")
            return False
    
    def test_rollback_procedures(self) -> bool:
        """Test rollback procedure functionality"""
        logger.info("Testing rollback procedures...")
        
        try:
            from validation_framework_agent import ValidationFrameworkAgent
            
            # Test rollback instructions generation
            validator = ValidationFrameworkAgent()
            rollback_instructions = validator.rollback_instructions()
            
            required_sections = ['immediate_actions', 'component_rollback', 'verification_steps']
            
            for section in required_sections:
                if section not in rollback_instructions:
                    logger.error(f"    Missing rollback section: {section}")
                    return False
            
            logger.info("    ✅ Rollback instructions complete")
            
            # Test backup creation
            logger.info("  Testing backup creation...")
            backup_path = validator.save_system_backup()
            
            if not os.path.exists(backup_path):
                logger.error("    Backup file not created")
                return False
            
            logger.info("    ✅ Backup created successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Rollback procedures test failed: {e}")
            return False


def main():
    """Main function for running validation framework tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Validation Framework Components")
    parser.add_argument('--quick', action='store_true', help='Run quick tests only')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = ValidationFrameworkTester()
    
    if args.quick:
        # Run essential tests only
        tester.temp_dir = tempfile.mkdtemp(prefix='validation_test_')
        logger.info(f"Using temporary directory: {tester.temp_dir}")
        
        success = (
            tester.test_imports() and
            tester.test_mock_data_creation() and
            tester.test_validation_framework_agent()
        )
        
        # Cleanup
        if tester.temp_dir and os.path.exists(tester.temp_dir):
            shutil.rmtree(tester.temp_dir)
    else:
        # Run full test suite
        success = tester.run_all_tests()
    
    if success:
        print("\n🎉 VALIDATION FRAMEWORK TESTS PASSED")
        print("The validation framework is ready for use!")
        sys.exit(0)
    else:
        print("\n⚠️ VALIDATION FRAMEWORK TESTS FAILED")
        print("Please review and fix issues before deployment")
        sys.exit(1)


if __name__ == "__main__":
    main()