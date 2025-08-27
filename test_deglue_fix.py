#!/usr/bin/env python3
"""
Quick test to verify the deglue fix produces clean text
"""
import sys
sys.path.append('.')

# Test the problematic text from actual CSV (test_current_output.csv)
test_text = "Health educa tion and well ness, counsel ling, and ongoing suppo rtas needed."

print("Testing deglue fixes...")
print(f"Raw input: {test_text}")

# Import the working simple_deglue_fixed function
from integrated_comprehensive_analyzer import simple_deglue_fixed

# Test step by step
print("\nStep by step processing:")
print(f"1. Input: {repr(test_text)}")

# Apply basic cleanup
text = test_text.replace("\r", " ").replace("\n", " ")
print(f"2. After whitespace: {repr(text)}")

result = simple_deglue_fixed(test_text)
print(f"3. Final result: {repr(result)}")

# Check if it matches expected clean text from test_fixed_output.csv
expected = "Health education and wellness, counselling, and ongoing support as needed."
print(f"4. Expected: {repr(expected)}")

if result == expected:
    print("✅ SUCCESS: Text processing is now working correctly!")
else:
    print("❌ FAILED: Text still not processed correctly")
    print(f"Differences:")
    import difflib
    for line in difflib.unified_diff(expected.splitlines(), result.splitlines(), lineterm=''):
        print(line)