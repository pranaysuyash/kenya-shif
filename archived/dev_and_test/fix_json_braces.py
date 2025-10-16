#!/usr/bin/env python3
"""
Quick fix for JSON braces in f-strings
"""
import re

def main():
    # Read the file
    with open('/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/updated_prompts.py', 'r') as f:
        content = f.read()

    # Fix JSON blocks in f-strings - find blocks starting with 'json' and ending with three backticks
    pattern = r'(```json\s*\n)(.*?)(```)'
    
    def fix_json_braces(match):
        prefix = match.group(1)
        json_content = match.group(2)
        suffix = match.group(3)
        
        # Double all single braces in the JSON content
        fixed_json = json_content.replace('{', '{{').replace('}', '}}')
        
        return prefix + fixed_json + suffix

    # Apply the fix
    original_content = content
    content = re.sub(pattern, fix_json_braces, content, flags=re.DOTALL)
    
    # Only write if changes were made
    if content != original_content:
        with open('/Users/pranay/Projects/adhoc_projects/drrishi/final_submission/updated_prompts.py', 'w') as f:
            f.write(content)
        print('✅ Fixed JSON brace escaping in f-strings')
        
        # Count fixes
        fixes = len(re.findall(pattern, original_content, flags=re.DOTALL))
        print(f'📊 Applied fixes to {fixes} JSON blocks')
    else:
        print('ℹ️ No changes needed')

if __name__ == '__main__':
    main()