import pandas as pd
import json
import os

def validate_outputs():
    print("🔍 Validating specific requirements...")
    
    csv_files = [
        "outputs/rules_p1_18_structured.csv",
        "outputs/annex_procedures.csv"
    ]
    
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                print(f"✅ {csv_file}: {len(df)} rows")
            except Exception as e:
                print(f"⚠️ Could not read {csv_file}: {e}")
        else:
            print(f"❌ Missing: {csv_file}")
    
    latest_dirs = [d for d in os.listdir('.') if d.startswith('outputs_run_')]
    if latest_dirs:
        latest_dir = sorted(latest_dirs)[-1]
        print(f"📁 Latest run directory: {latest_dir}")
        
        key_files = [
            'integrated_comprehensive_analysis.json',
            'policy_structured.csv', 
            'annex_procedures.csv'
        ]
        
        for key_file in key_files:
            file_path = os.path.join(latest_dir, key_file)
            if os.path.exists(file_path):
                if key_file.endswith('.csv'):
                    try:
                        df = pd.read_csv(file_path)
                        print(f"✅ {key_file}: {len(df)} rows")
                    except Exception as e:
                        print(f"⚠️ Could not read {key_file}: {e}")
                else:
                    print(f"✅ {key_file}: exists")
            else:
                print(f"❌ {key_file}: missing")

if __name__ == "__main__":
    validate_outputs()
