#!/usr/bin/env python3
"""
AI-First Contradiction Detection System
Uses OpenAI to intelligently find healthcare policy contradictions

Author: Pranay for Dr. Rishi
Date: August 25, 2025
"""

import pandas as pd
import openai
import os
from dotenv import load_dotenv
import json
import time

load_dotenv()

class AIContradictionDetector:
    """AI-powered contradiction detection for healthcare policies"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.contradictions_found = []
    
    def find_contradictions_with_ai(self, rules_df: pd.DataFrame, batch_size: int = 20) -> pd.DataFrame:
        """Use OpenAI to find contradictions in healthcare rules"""
        
        print(f"🤖 AI Contradiction Detection: Analyzing {len(rules_df)} rules...")
        
        # Process rules in batches to avoid token limits
        all_contradictions = []
        
        for i in range(0, len(rules_df), batch_size):
            batch = rules_df.iloc[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(rules_df) + batch_size - 1)//batch_size}")
            
            batch_contradictions = self._analyze_batch_with_ai(batch)
            all_contradictions.extend(batch_contradictions)
            
            # Rate limiting
            time.sleep(1)
        
        # Convert to DataFrame
        if all_contradictions:
            contradictions_df = pd.DataFrame(all_contradictions)
            print(f"✅ Found {len(contradictions_df)} contradictions using AI")
            return contradictions_df
        else:
            print("ℹ️ No contradictions detected by AI")
            return pd.DataFrame()
    
    def _analyze_batch_with_ai(self, batch_df: pd.DataFrame) -> list:
        """Analyze a batch of rules for contradictions"""
        
        # Format rules for AI analysis
        rules_text = self._format_rules_for_ai(batch_df)
        
        prompt = f"""
You are a healthcare policy expert analyzing SHIF (Social Health Insurance Fund) benefits for contradictions.

TASK: Find contradictions in these healthcare rules. Look for:

1. **TARIFF CONFLICTS**: Same/similar services with different KES amounts
2. **LIMIT CONFLICTS**: Same service with different quantity limits (e.g., 2x/week vs 3x/week)  
3. **COVERAGE CONFLICTS**: Service both included and excluded
4. **FACILITY CONFLICTS**: Different facility level restrictions for same service

RULES TO ANALYZE:
{rules_text}

RESPONSE FORMAT (JSON array):
[
  {{
    "type": "Tariff|Limit|Coverage|Facility",
    "service_1": "exact service name from rules",
    "service_2": "exact service name from rules", 
    "conflict_description": "detailed description of contradiction",
    "evidence_1": "page X evidence snippet",
    "evidence_2": "page Y evidence snippet",
    "severity": "HIGH|MEDIUM|LOW",
    "confidence": "HIGH|MEDIUM|LOW"
  }}
]

Only return contradictions you are confident about. If no contradictions found, return [].
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if result_text.startswith('[') and result_text.endswith(']'):
                contradictions = json.loads(result_text)
                return contradictions
            else:
                print(f"⚠️ AI returned non-JSON response: {result_text[:100]}...")
                return []
                
        except Exception as e:
            print(f"❌ Error in AI analysis: {e}")
            return []
    
    def _format_rules_for_ai(self, batch_df: pd.DataFrame) -> str:
        """Format rules for AI analysis"""
        rules_text = ""
        
        for _, rule in batch_df.iterrows():
            service = rule.get('service', 'Unknown')[:100]
            tariff = rule.get('tariff', 'N/A')
            unit = rule.get('tariff_unit', 'N/A')
            coverage = rule.get('coverage_status', 'N/A')
            facilities = rule.get('facility_levels', 'N/A')
            limits = rule.get('limits', 'N/A')
            page = rule.get('source_page', 'N/A')
            evidence = rule.get('evidence_snippet', '')[:150]
            
            rules_text += f"""
Service: {service}
Tariff: KES {tariff} {unit}
Coverage: {coverage}
Facility Levels: {facilities}
Limits: {limits}
Source: Page {page}
Evidence: {evidence}
---
"""
        
        return rules_text
    
    def find_service_variations(self, rules_df: pd.DataFrame) -> pd.DataFrame:
        """Use AI to find similar services that might be variations of the same thing"""
        
        print("🔍 AI Service Variation Analysis...")
        
        # Get unique services
        services = rules_df['service'].unique()[:50]  # Limit for token constraints
        
        services_text = "\n".join([f"{i+1}. {service}" for i, service in enumerate(services)])
        
        prompt = f"""
You are analyzing healthcare service names to find variations of the same service.

TASK: Group similar services that represent the same healthcare service but are named differently.

SERVICES:
{services_text}

Look for:
- Different spellings (hemodialysis vs haemodialysis)
- Different formats (CT scan vs CT imaging)
- Partial descriptions vs full descriptions
- Same medical procedure with different wording

RESPONSE FORMAT (JSON):
{{
  "service_groups": [
    {{
      "main_service": "primary service name",
      "variations": ["variation 1", "variation 2"],
      "medical_category": "dialysis|surgery|imaging|etc"
    }}
  ]
}}

Only group services you are confident are the same medical service.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            service_groups = json.loads(result)
            
            print(f"✅ AI found {len(service_groups.get('service_groups', []))} service groups")
            return service_groups
            
        except Exception as e:
            print(f"❌ Error in service variation analysis: {e}")
            return {"service_groups": []}

def main():
    """Run AI-powered contradiction detection"""
    
    print("🤖 AI-First Contradiction Detection System")
    print("=" * 50)
    
    # Load comprehensive rules
    rules_df = pd.read_csv('outputs/rules_comprehensive.csv')
    print(f"📊 Loaded {len(rules_df)} rules for analysis")
    
    # Initialize AI detector
    detector = AIContradictionDetector()
    
    # Find service variations first
    service_groups = detector.find_service_variations(rules_df)
    
    # Find contradictions
    contradictions_df = detector.find_contradictions_with_ai(rules_df)
    
    # Save results
    if not contradictions_df.empty:
        contradictions_df.to_csv('outputs/ai_contradictions.csv', index=False)
        print(f"💾 Saved {len(contradictions_df)} AI-detected contradictions")
        
        # Show sample results
        print("\n🔍 Sample AI-Detected Contradictions:")
        for _, contradiction in contradictions_df.head(3).iterrows():
            print(f"  {contradiction['type']}: {contradiction['service_1']} vs {contradiction['service_2']}")
            print(f"    -> {contradiction['conflict_description']}")
            print(f"    Confidence: {contradiction['confidence']}")
            print()
    else:
        print("ℹ️ No contradictions found by AI in this batch")
    
    print("\n✅ AI Contradiction Detection Complete")

if __name__ == "__main__":
    main()