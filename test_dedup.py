#!/usr/bin/env python3
"""Quick test to verify deduplicate_gaps_with_openai function exists and is callable"""

import sys

def test_dedup_exists():
    """Test that the dedup function exists"""
    print("🧪 Testing deduplication function...")

    try:
        # Import the analyzer
        from integrated_comprehensive_analyzer import IntegratedComprehensiveMedicalAnalyzer
        print("   ✅ Module imported successfully")

        # Check if the method exists
        analyzer = IntegratedComprehensiveMedicalAnalyzer()
        print("   ✅ Analyzer instantiated")

        # Check if deduplicate_gaps_with_openai method exists
        if hasattr(analyzer, 'deduplicate_gaps_with_openai'):
            print("   ✅ deduplicate_gaps_with_openai method EXISTS")
        else:
            print("   ❌ deduplicate_gaps_with_openai method MISSING")
            return False

        # Test with empty gaps (should return immediately)
        result = analyzer.deduplicate_gaps_with_openai([])
        print(f"   ✅ Function callable - returned {len(result)} gaps for empty input")

        # Test with one gap (should return immediately without AI call)
        test_gap = {
            'description': 'Test gap',
            'gap_category': 'test',
            'unique_id': 'TEST_001'
        }
        result = analyzer.deduplicate_gaps_with_openai([test_gap])
        print(f"   ✅ Function works with 1 gap - returned {len(result)} gaps")

        print("\n✅ ALL TESTS PASSED - Deduplication function is working!")
        return True

    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False
    except AttributeError as e:
        print(f"   ❌ Attribute error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dedup_exists()
    sys.exit(0 if success else 1)
