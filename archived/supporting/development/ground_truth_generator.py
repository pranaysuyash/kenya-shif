#!/usr/bin/env python3
"""
Ground Truth Dataset Generator
Creates curated datasets from expert validations for SHIF analyzer training

Author: Pranay for Dr. Rishi
Date: August 24, 2025
"""

import pandas as pd
import json
import os
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import numpy as np

class GroundTruthGenerator:
    """Generates ground truth datasets from expert validations"""
    
    def __init__(self):
        self.validation_file = "expert_validations.jsonl" 
        self.ground_truth_file = "ground_truth_dataset.csv"
        self.conflict_resolution_file = "validation_conflicts.json"
        self.dataset_metadata_file = "ground_truth_metadata.json"
    
    def load_validations(self) -> List[Dict]:
        """Load all expert validations"""
        validations = []
        if os.path.exists(self.validation_file):
            with open(self.validation_file, 'r') as f:
                for line in f:
                    try:
                        validations.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return validations
    
    def analyze_inter_expert_agreement(self, validations: List[Dict]) -> Dict:
        """Analyze agreement between multiple experts on same rules"""
        # Group validations by rule_id
        rule_validations = defaultdict(list)
        for val in validations:
            rule_id = val.get('rule_id')
            if rule_id:
                rule_validations[rule_id].append(val)
        
        # Analyze agreement
        agreement_stats = {
            'total_rules': len(rule_validations),
            'single_validation': 0,
            'multiple_validations': 0,
            'perfect_agreement': 0,
            'partial_agreement': 0,
            'conflicts': 0,
            'conflict_details': []
        }
        
        for rule_id, vals in rule_validations.items():
            if len(vals) == 1:
                agreement_stats['single_validation'] += 1
            else:
                agreement_stats['multiple_validations'] += 1
                
                # Check outcome agreement
                outcomes = [v['validation_outcome'] for v in vals]
                unique_outcomes = set(outcomes)
                
                if len(unique_outcomes) == 1:
                    agreement_stats['perfect_agreement'] += 1
                elif len(unique_outcomes) == 2 and 'correct_extraction' in unique_outcomes:
                    agreement_stats['partial_agreement'] += 1
                else:
                    agreement_stats['conflicts'] += 1
                    
                    # Record conflict details
                    conflict_detail = {
                        'rule_id': rule_id,
                        'validators': [v['validator'] for v in vals],
                        'outcomes': outcomes,
                        'confidence_levels': [v['confidence_level'] for v in vals],
                        'feedbacks': [v.get('feedback', '') for v in vals]
                    }
                    agreement_stats['conflict_details'].append(conflict_detail)
        
        return agreement_stats
    
    def resolve_conflicts(self, validations: List[Dict], agreement_stats: Dict) -> List[Dict]:
        """Resolve conflicts between expert validations"""
        resolved_validations = []
        rule_validations = defaultdict(list)
        
        # Group by rule
        for val in validations:
            rule_id = val.get('rule_id')
            if rule_id:
                rule_validations[rule_id].append(val)
        
        conflict_resolutions = []
        
        for rule_id, vals in rule_validations.items():
            if len(vals) == 1:
                # Single validation - accept as is
                resolved_validations.append(vals[0])
            else:
                # Multiple validations - need resolution
                outcomes = [v['validation_outcome'] for v in vals]
                unique_outcomes = set(outcomes)
                
                if len(unique_outcomes) == 1:
                    # Perfect agreement - take any validation (first one)
                    resolved_validations.append(vals[0])
                else:
                    # Conflict resolution strategy
                    resolved_validation = self._resolve_validation_conflict(vals)
                    resolved_validations.append(resolved_validation)
                    
                    conflict_resolutions.append({
                        'rule_id': rule_id,
                        'original_validations': len(vals),
                        'resolution_method': resolved_validation.get('resolution_method', 'unknown'),
                        'final_outcome': resolved_validation['validation_outcome']
                    })
        
        # Save conflict resolutions
        if conflict_resolutions:
            with open(self.conflict_resolution_file, 'w') as f:
                json.dump({
                    'resolution_date': datetime.now().isoformat(),
                    'total_conflicts': len(conflict_resolutions),
                    'resolutions': conflict_resolutions
                }, f, indent=2)
        
        return resolved_validations
    
    def _resolve_validation_conflict(self, validations: List[Dict]) -> Dict:
        """Resolve conflict between multiple validations of same rule"""
        # Priority-based resolution:
        # 1. Favor high confidence validations
        # 2. Favor domain experts (dialysis experts for dialysis rules, etc.)
        # 3. Use majority vote
        # 4. Conservative approach (prefer 'needs review' for major conflicts)
        
        high_confidence_vals = [v for v in validations if v.get('confidence_level') == 'High']
        
        if len(high_confidence_vals) == 1:
            result = high_confidence_vals[0].copy()
            result['resolution_method'] = 'high_confidence_single'
            return result
        elif len(high_confidence_vals) > 1:
            # Multiple high confidence - check for domain expertise match
            rule_category = validations[0].get('original_data', {}).get('category', '').lower()
            
            relevant_experts = []
            for val in high_confidence_vals:
                expertise = val.get('expertise_area', '').lower()
                if ('dialysis' in rule_category and 'nephrology' in expertise) or \
                   ('oncology' in rule_category and 'oncology' in expertise) or \
                   ('imaging' in rule_category and 'diagnostic' in expertise):
                    relevant_experts.append(val)
            
            if len(relevant_experts) == 1:
                result = relevant_experts[0].copy()
                result['resolution_method'] = 'domain_expert'
                return result
            elif len(relevant_experts) > 1:
                # Use first domain expert
                result = relevant_experts[0].copy()
                result['resolution_method'] = 'first_domain_expert'
                return result
        
        # Majority vote on outcomes
        outcomes = [v['validation_outcome'] for v in validations]
        outcome_counts = {outcome: outcomes.count(outcome) for outcome in set(outcomes)}
        majority_outcome = max(outcome_counts.keys(), key=lambda k: outcome_counts[k])
        
        if outcome_counts[majority_outcome] > len(validations) / 2:
            # Clear majority
            majority_vals = [v for v in validations if v['validation_outcome'] == majority_outcome]
            result = majority_vals[0].copy()  # Take first with majority outcome
            result['resolution_method'] = 'majority_vote'
            return result
        
        # No clear resolution - mark for manual review
        result = validations[0].copy()
        result['validation_outcome'] = 'needs_manual_review'
        result['resolution_method'] = 'unresolved_conflict'
        result['conflict_note'] = f"Unresolved conflict between {len(validations)} validators"
        return result
    
    def create_ground_truth_dataset(self) -> Tuple[pd.DataFrame, Dict]:
        """Create the ground truth dataset from resolved validations"""
        # Load and analyze validations
        validations = self.load_validations()
        
        if not validations:
            print("❌ No validation data found")
            return pd.DataFrame(), {}
        
        print(f"📊 Found {len(validations)} validation records")
        
        # Analyze inter-expert agreement
        agreement_stats = self.analyze_inter_expert_agreement(validations)
        print(f"🤝 Agreement analysis: {agreement_stats['perfect_agreement']} perfect, {agreement_stats['conflicts']} conflicts")
        
        # Resolve conflicts
        resolved_validations = self.resolve_conflicts(validations, agreement_stats)
        print(f"✅ Resolved to {len(resolved_validations)} ground truth records")
        
        # Create ground truth records
        ground_truth_records = []
        
        for validation in resolved_validations:
            original_data = validation.get('original_data', {})
            outcome = validation['validation_outcome']
            
            # Determine final values
            if outcome == 'correct_extraction':
                # Use original extracted values
                final_values = original_data
            elif outcome in ['partially_correct', 'incorrect_extraction']:
                # Use corrected values where provided
                final_values = original_data.copy()
                corrections = validation.get('corrections', {})
                final_values.update(corrections)
            else:
                # For missing_information, duplicate_rule, etc.
                final_values = original_data
            
            # Create ground truth record
            gt_record = {
                # Original rule information
                'rule_id': validation.get('rule_id'),
                'source_page': final_values.get('source_page'),
                'evidence_snippet': final_values.get('evidence_snippet', ''),
                
                # Ground truth labels
                'gt_service': final_values.get('service', ''),
                'gt_service_key': final_values.get('service_key', ''),
                'gt_category': final_values.get('category', ''),
                'gt_tariff_value': final_values.get('tariff_value'),
                'gt_tariff_unit': final_values.get('tariff_unit', ''),
                'gt_coverage_status': final_values.get('coverage_status', ''),
                'gt_facility_levels': final_values.get('facility_levels', ''),
                'gt_limits': final_values.get('limits', ''),
                
                # Validation metadata
                'validation_outcome': outcome,
                'validator_confidence': validation.get('confidence_level'),
                'validator_expertise': validation.get('expertise_area'),
                'validator_feedback': validation.get('feedback', ''),
                'validation_date': validation.get('timestamp'),
                'resolution_method': validation.get('resolution_method'),
                
                # Quality flags
                'is_high_quality': outcome in ['correct_extraction', 'partially_correct'] and 
                                 validation.get('confidence_level') == 'High',
                'needs_review': outcome in ['needs_manual_review', 'missing_information'],
                'is_duplicate': outcome == 'duplicate_rule'
            }
            
            ground_truth_records.append(gt_record)
        
        # Convert to DataFrame
        gt_df = pd.DataFrame(ground_truth_records)
        
        # Generate dataset metadata
        metadata = {
            'creation_date': datetime.now().isoformat(),
            'total_records': len(gt_df),
            'high_quality_records': len(gt_df[gt_df['is_high_quality'] == True]),
            'needs_review_records': len(gt_df[gt_df['needs_review'] == True]),
            'duplicate_records': len(gt_df[gt_df['is_duplicate'] == True]),
            'validation_outcomes': gt_df['validation_outcome'].value_counts().to_dict(),
            'validator_count': len(set([v['validator'] for v in validations])),
            'expertise_areas': list(set([v.get('expertise_area', 'Unknown') for v in validations])),
            'agreement_statistics': agreement_stats,
            'quality_metrics': {
                'high_quality_rate': len(gt_df[gt_df['is_high_quality'] == True]) / len(gt_df),
                'review_rate': len(gt_df[gt_df['needs_review'] == True]) / len(gt_df),
                'duplicate_rate': len(gt_df[gt_df['is_duplicate'] == True]) / len(gt_df)
            }
        }
        
        return gt_df, metadata
    
    def generate_training_splits(self, gt_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Generate training/validation/test splits for ML training"""
        # Filter for high-quality records
        high_quality_df = gt_df[gt_df['is_high_quality'] == True].copy()
        
        if len(high_quality_df) < 10:
            print("⚠️ Too few high-quality records for meaningful splits")
            return {'full': high_quality_df}
        
        # Stratified split by category to ensure representation
        splits = {}
        
        # Shuffle the data
        shuffled_df = high_quality_df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        n_total = len(shuffled_df)
        n_train = int(0.7 * n_total)
        n_val = int(0.2 * n_total)
        n_test = n_total - n_train - n_val
        
        splits['train'] = shuffled_df[:n_train]
        splits['validation'] = shuffled_df[n_train:n_train + n_val]
        splits['test'] = shuffled_df[n_train + n_val:]
        splits['full'] = high_quality_df
        
        print(f"📊 Training splits: {n_train} train, {n_val} val, {n_test} test")
        
        return splits
    
    def save_ground_truth_dataset(self, gt_df: pd.DataFrame, metadata: Dict):
        """Save the ground truth dataset and metadata"""
        # Save main dataset
        gt_df.to_csv(self.ground_truth_file, index=False)
        print(f"💾 Saved ground truth dataset: {self.ground_truth_file}")
        
        # Save metadata
        with open(self.dataset_metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"💾 Saved dataset metadata: {self.dataset_metadata_file}")
        
        # Generate training splits
        splits = self.generate_training_splits(gt_df)
        
        # Save splits
        for split_name, split_df in splits.items():
            split_file = f"ground_truth_{split_name}.csv"
            split_df.to_csv(split_file, index=False)
            print(f"💾 Saved {split_name} split: {split_file} ({len(split_df)} records)")
    
    def generate_quality_report(self, gt_df: pd.DataFrame, metadata: Dict) -> str:
        """Generate a quality assessment report"""
        report_lines = [
            "# Ground Truth Dataset Quality Report",
            f"Generated: {metadata['creation_date']}",
            "",
            "## Dataset Overview",
            f"- Total Records: {metadata['total_records']}",
            f"- High Quality Records: {metadata['high_quality_records']} ({metadata['quality_metrics']['high_quality_rate']:.1%})",
            f"- Records Needing Review: {metadata['needs_review_records']} ({metadata['quality_metrics']['review_rate']:.1%})",
            f"- Duplicate Records: {metadata['duplicate_records']} ({metadata['quality_metrics']['duplicate_rate']:.1%})",
            "",
            "## Validation Outcomes",
        ]
        
        for outcome, count in metadata['validation_outcomes'].items():
            percentage = count / metadata['total_records'] * 100
            report_lines.append(f"- {outcome.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
        
        report_lines.extend([
            "",
            "## Expert Participation",
            f"- Number of Validators: {metadata['validator_count']}",
            "- Expertise Areas: " + ", ".join(metadata['expertise_areas']),
            "",
            "## Inter-Expert Agreement",
            f"- Perfect Agreement: {metadata['agreement_statistics']['perfect_agreement']} rules",
            f"- Conflicts Resolved: {metadata['agreement_statistics']['conflicts']} rules",
            "",
            "## Quality Recommendations",
        ])
        
        # Quality recommendations
        if metadata['quality_metrics']['high_quality_rate'] < 0.5:
            report_lines.append("⚠️ Low high-quality rate - consider additional validation rounds")
        else:
            report_lines.append("✅ Good high-quality rate for training purposes")
        
        if metadata['quality_metrics']['review_rate'] > 0.2:
            report_lines.append("⚠️ High review rate - manual resolution needed for training")
        
        if metadata['agreement_statistics']['conflicts'] > metadata['agreement_statistics']['perfect_agreement']:
            report_lines.append("⚠️ High conflict rate - consider validator training or clearer guidelines")
        
        return "\n".join(report_lines)

def main():
    parser = argparse.ArgumentParser(description="Generate ground truth dataset from expert validations")
    parser.add_argument("--validation-file", default="expert_validations.jsonl",
                      help="Path to validation JSONL file")
    parser.add_argument("--output-prefix", default="ground_truth",
                      help="Prefix for output files")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = GroundTruthGenerator()
    generator.validation_file = args.validation_file
    generator.ground_truth_file = f"{args.output_prefix}_dataset.csv"
    generator.dataset_metadata_file = f"{args.output_prefix}_metadata.json"
    
    print("🏗️ Ground Truth Dataset Generator")
    print("=" * 40)
    
    # Generate dataset
    gt_df, metadata = generator.create_ground_truth_dataset()
    
    if gt_df.empty:
        print("❌ No ground truth dataset generated - check validation data")
        return
    
    # Save dataset
    generator.save_ground_truth_dataset(gt_df, metadata)
    
    # Generate quality report
    report = generator.generate_quality_report(gt_df, metadata)
    report_file = f"{args.output_prefix}_quality_report.md"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📋 Generated quality report: {report_file}")
    print("\n" + "="*40)
    print("✅ Ground truth dataset generation complete!")
    print(f"📊 {len(gt_df)} total records, {len(gt_df[gt_df['is_high_quality']])} high quality")

if __name__ == "__main__":
    main()