#!/usr/bin/env python3
"""
End-to-end tests for Compressor module operations.

Tests all compressor operations as a user would use them after pip install.
"""

import sys


def test_truncate_tokens():
    """Test TruncateTokens operation."""
    print("\nTesting TruncateTokens...")
    from prompt_refiner import TruncateTokens

    # Truncate with character estimation (no tiktoken required)
    operation = TruncateTokens(max_tokens=10)
    long_text = "This is a very long text that should be truncated to fit within the token limit."
    result = operation.process(long_text)

    # Result should be shorter
    assert len(result) < len(long_text), "Text should be truncated"
    assert len(result) > 0, "Result should not be empty"

    # Test with different strategies
    operation = TruncateTokens(max_tokens=20, strategy="start")
    result = operation.process(long_text)
    assert "This" in result, "Start truncation should keep beginning"

    operation = TruncateTokens(max_tokens=20, strategy="end")
    result = operation.process(long_text)
    assert "limit" in result, "End truncation should keep ending"

    print("✓ TruncateTokens works correctly")


def test_deduplicate():
    """Test Deduplicate operation."""
    print("\nTesting Deduplicate...")
    from prompt_refiner import Deduplicate

    # Test paragraph deduplication
    operation = Deduplicate(method="jaccard", granularity="paragraph")
    text = "Hello World\n\nGoodbye World\n\nHello World"  # Duplicate paragraph
    result = operation.process(text)

    # Should remove duplicate paragraph
    assert isinstance(result, str), "Should return a string"
    assert len(result) < len(text), "Should remove duplicates"

    # Fuzzy duplicates (levenshtein)
    operation = Deduplicate(method="levenshtein", similarity_threshold=0.8, granularity="paragraph")
    text = "Hello World\n\nHello World!"  # Very similar paragraphs
    result = operation.process(text)
    assert len(result) < len(text), "Should remove similar paragraphs"

    # Test sentence granularity
    operation = Deduplicate(method="jaccard", granularity="sentence", similarity_threshold=0.9)
    text = "Hello. World. Hello."  # Duplicate sentence
    result = operation.process(text)
    assert result.count("Hello.") <= 1, "Should deduplicate sentences"

    print("✓ Deduplicate works correctly")


def test_compressor_pipeline():
    """Test combining compressor operations."""
    print("\nTesting Compressor Pipeline...")
    from prompt_refiner import Deduplicate, NormalizeWhitespace, TruncateTokens

    # Create pipeline: clean, deduplicate, then truncate
    pipeline = (
        NormalizeWhitespace()
        | Deduplicate(method="jaccard", granularity="paragraph")
        | TruncateTokens(max_tokens=50)
    )

    # Test with text containing duplicates and whitespace
    text = (
        "Hello   World\n\nHello   World\n\nThis is a very long piece of text that will be truncated"
    )

    result = pipeline.process(text)

    # Verify operations applied
    assert isinstance(result, str), "Should return a string"
    assert "   " not in result, "Should normalize whitespace"
    assert len(result) < len(text), "Should deduplicate and truncate"

    print("✓ Compressor Pipeline works correctly")


def main():
    """Run all compressor e2e tests."""
    print("=" * 60)
    print("Running Compressor Module E2E Tests")
    print("=" * 60)

    try:
        test_truncate_tokens()
        test_deduplicate()
        test_compressor_pipeline()

        print("\n" + "=" * 60)
        print("✓ All Compressor E2E tests passed!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
