#!/usr/bin/env python3
"""
Expert Validation Command Line Interface
Terminal-based validation tool for healthcare experts

Author: Pranay for Dr. Rishi  
Date: August 24, 2025
"""

import pandas as pd
import json
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Optional
from textwrap import fill

class CLIValidationWorkflow:
    """Command-line validation workflow"""
    
    def __init__(self):
        self.validation_file = "expert_validations.jsonl"
        self.progress_file = "validation_progress.json"
        self.validator_name = ""
        self.expertise_area = ""
    
    def setup_validator(self):
        """Setup validator information"""
        print("🏥 SHIF Rules Expert Validation (CLI)")
        print("=" * 50)
        
        self.validator_name = input("Enter your name/ID: ").strip()
        if not self.validator_name:
            print("❌ Validator name is required")
            sys.exit(1)
        
        print("\nExpertise Areas:")
        areas = ["General Medicine", "Dialysis/Nephrology", "Oncology", "Maternity",
                "Emergency Medicine", "Surgery", "Diagnostics/Imaging", "Other"]
        
        for i, area in enumerate(areas, 1):
            print(f"{i}. {area}")
        
        try:
            choice = int(input("\nSelect your primary expertise (1-8): "))
            self.expertise_area = areas[choice - 1]
        except (ValueError, IndexError):
            self.expertise_area = "Other"
        
        print(f"\n✅ Validator: {self.validator_name} ({self.expertise_area})")
        print("-" * 50)
    
    def load_rules(self, rules_file: str) -> pd.DataFrame:
        """Load rules from CSV"""
        try:
            df = pd.read_csv(rules_file)
            print(f"📊 Loaded {len(df)} rules from {rules_file}")
            return df
        except Exception as e:
            print(f"❌ Error loading rules: {e}")
            sys.exit(1)
    
    def load_validation_progress(self) -> Dict:
        """Load validation progress"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_validation_progress(self, progress: Dict):
        """Save validation progress"""
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def save_validation(self, validation_data: Dict):
        """Save validation to JSONL"""
        validation_data['timestamp'] = datetime.now().isoformat()
        validation_data['validator'] = self.validator_name
        validation_data['expertise_area'] = self.expertise_area
        
        with open(self.validation_file, 'a') as f:
            f.write(json.dumps(validation_data) + '\n')
    
    def display_rule(self, rule: pd.Series, rule_index: int):
        """Display rule information in formatted way"""
        print(f"\n{'='*60}")
        print(f"RULE {rule_index + 1}")
        print(f"{'='*60}")
        
        # Main information
        print(f"📋 SERVICE: {rule['service']}")
        print(f"🏷️  CATEGORY: {rule.get('category', 'N/A')}")
        print(f"💰 TARIFF: KES {rule.get('tariff_value', 'N/A')} {rule.get('tariff_unit', '')}")
        print(f"✅ COVERAGE: {rule.get('coverage_status', 'N/A')}")
        print(f"🏥 FACILITY LEVELS: {rule.get('facility_levels', 'N/A')}")
        
        if pd.notna(rule.get('limits')):
            print(f"📊 LIMITS: {rule['limits']}")
        
        print(f"📄 SOURCE PAGE: {rule.get('source_page', 'N/A')}")
        
        if pd.notna(rule.get('confidence')):
            print(f"🎯 CONFIDENCE: {rule['confidence']}")
        
        # Evidence snippet
        if pd.notna(rule.get('evidence_snippet')):
            print(f"\n📝 ORIGINAL TEXT EVIDENCE:")
            print("-" * 40)
            evidence = rule['evidence_snippet']
            # Wrap long text
            wrapped = fill(evidence, width=80)
            print(wrapped)
            print("-" * 40)
    
    def get_validation_input(self) -> Dict:
        """Get validation input from user"""
        print(f"\n{'🔍 EXPERT VALIDATION'}")
        print("-" * 30)
        
        # Validation outcome
        outcomes = [
            "correct_extraction",
            "partially_correct", 
            "incorrect_extraction",
            "missing_information",
            "duplicate_rule"
        ]
        
        print("Validation Outcomes:")
        for i, outcome in enumerate(outcomes, 1):
            print(f"{i}. {outcome.replace('_', ' ').title()}")
        
        while True:
            try:
                choice = int(input("\nSelect validation outcome (1-5): "))
                if 1 <= choice <= 5:
                    validation_outcome = outcomes[choice - 1]
                    break
                else:
                    print("❌ Please select a number between 1-5")
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Confidence level
        confidence_levels = ["High", "Medium", "Low"]
        print(f"\nConfidence Levels:")
        for i, level in enumerate(confidence_levels, 1):
            print(f"{i}. {level}")
        
        while True:
            try:
                choice = int(input("Select confidence level (1-3): "))
                if 1 <= choice <= 3:
                    confidence_level = confidence_levels[choice - 1]
                    break
                else:
                    print("❌ Please select a number between 1-3")
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Feedback
        print("\nProvide detailed feedback (press Enter twice to finish):")
        feedback_lines = []
        while True:
            line = input()
            if line == "" and feedback_lines and feedback_lines[-1] == "":
                break
            feedback_lines.append(line)
        
        feedback = "\n".join(feedback_lines).strip()
        
        validation_data = {
            'validation_outcome': validation_outcome,
            'confidence_level': confidence_level,
            'feedback': feedback
        }
        
        # Get corrections if needed
        if validation_outcome in ["partially_correct", "incorrect_extraction"]:
            print("\n🔧 PROVIDE CORRECTED INFORMATION:")
            corrected_service = input("Corrected service name (press Enter to skip): ").strip()
            
            corrected_tariff = input("Corrected tariff amount (press Enter to skip): ").strip()
            if corrected_tariff:
                try:
                    corrected_tariff = float(corrected_tariff)
                except ValueError:
                    corrected_tariff = None
            else:
                corrected_tariff = None
            
            corrected_unit = input("Corrected unit (press Enter to skip): ").strip()
            
            coverage_options = ["included", "excluded", "conditional"]
            print("\nCoverage options: 1=included, 2=excluded, 3=conditional")
            coverage_choice = input("Corrected coverage status (1-3, or Enter to skip): ").strip()
            
            corrected_coverage = None
            if coverage_choice in ["1", "2", "3"]:
                corrected_coverage = coverage_options[int(coverage_choice) - 1]
            
            corrections = {}
            if corrected_service:
                corrections['service'] = corrected_service
            if corrected_tariff is not None:
                corrections['tariff_value'] = corrected_tariff
            if corrected_unit:
                corrections['tariff_unit'] = corrected_unit
            if corrected_coverage:
                corrections['coverage_status'] = corrected_coverage
            
            if corrections:
                validation_data['corrections'] = corrections
        
        return validation_data
    
    def show_statistics(self, rules_df: pd.DataFrame):
        """Show validation statistics"""
        progress = self.load_validation_progress()
        total_rules = len(rules_df)
        validated_rules = len([k for k, v in progress.items() if v.get('status') == 'validated'])
        
        print(f"\n📈 VALIDATION STATISTICS")
        print("-" * 30)
        print(f"Total Rules: {total_rules}")
        print(f"Validated: {validated_rules}")
        print(f"Remaining: {total_rules - validated_rules}")
        print(f"Progress: {validated_rules/total_rules*100:.1f}%")
        
        # Show outcomes
        outcomes = {}
        for rule_id, data in progress.items():
            if data.get('status') == 'validated':
                outcome = data.get('validation_outcome', 'unknown')
                outcomes[outcome] = outcomes.get(outcome, 0) + 1
        
        if outcomes:
            print(f"\nValidation Outcomes:")
            for outcome, count in outcomes.items():
                print(f"  {outcome.replace('_', ' ').title()}: {count}")
    
    def run_validation(self, rules_file: str):
        """Main validation loop"""
        # Setup
        self.setup_validator()
        
        # Load data
        rules_df = self.load_rules(rules_file)
        progress = self.load_validation_progress()
        
        # Show statistics
        self.show_statistics(rules_df)
        
        # Find unvalidated rules
        unvalidated_indices = []
        for idx, row in rules_df.iterrows():
            rule_id = f"rule_{idx}"
            if rule_id not in progress or progress[rule_id].get('status') != 'validated':
                unvalidated_indices.append(idx)
        
        if not unvalidated_indices:
            print("\n🎉 All rules have been validated!")
            return
        
        print(f"\n{len(unvalidated_indices)} rules remaining for validation")
        
        # Validation loop
        for rule_index in unvalidated_indices:
            rule = rules_df.iloc[rule_index]
            rule_id = f"rule_{rule_index}"
            
            # Display rule
            self.display_rule(rule, rule_index)
            
            # Ask for action
            print(f"\nActions:")
            print("1. Validate this rule")
            print("2. Skip to next rule")
            print("3. Show statistics") 
            print("4. Quit")
            
            while True:
                try:
                    action = int(input("\nSelect action (1-4): "))
                    if 1 <= action <= 4:
                        break
                    else:
                        print("❌ Please select 1-4")
                except ValueError:
                    print("❌ Please enter a valid number")
            
            if action == 1:  # Validate
                validation_data = self.get_validation_input()
                validation_data.update({
                    'rule_index': rule_index,
                    'rule_id': rule_id,
                    'original_data': rule.to_dict()
                })
                
                # Save validation
                self.save_validation(validation_data)
                
                # Update progress
                progress[rule_id] = {
                    'status': 'validated',
                    'validation_outcome': validation_data['validation_outcome'],
                    'validator': self.validator_name
                }
                self.save_validation_progress(progress)
                
                print(f"\n✅ Validation saved for rule {rule_index + 1}")
                
            elif action == 2:  # Skip
                continue
            elif action == 3:  # Statistics
                self.show_statistics(rules_df)
            elif action == 4:  # Quit
                print("\n👋 Thank you for your validation work!")
                break
        
        # Final statistics
        print(f"\n🏁 FINAL SESSION SUMMARY")
        self.show_statistics(rules_df)

def main():
    parser = argparse.ArgumentParser(description="Expert validation CLI for SHIF rules")
    parser.add_argument("rules_file", help="Path to the rules CSV file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.rules_file):
        print(f"❌ Rules file not found: {args.rules_file}")
        sys.exit(1)
    
    workflow = CLIValidationWorkflow()
    workflow.run_validation(args.rules_file)

if __name__ == "__main__":
    main()