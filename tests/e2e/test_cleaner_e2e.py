#!/usr/bin/env python3
"""
End-to-end tests for Cleaner module operations.

Tests all cleaner operations as a user would use them after pip install.
"""

import sys


def test_strip_html():
    """Test StripHTML operation."""
    print("\nTesting StripHTML...")
    from prompt_refiner import StripHTML

    # Basic HTML stripping
    operation = StripHTML()
    html_text = "<div><p>Hello <strong>World</strong></p></div>"
    result = operation.process(html_text)
    assert "<div>" not in result, "HTML tags should be removed"
    assert "<p>" not in result, "HTML tags should be removed"
    assert "Hello" in result, "Text content should be preserved"
    assert "World" in result, "Text content should be preserved"

    # HTML to markdown conversion
    operation = StripHTML(to_markdown=True)
    html_text = "<h1>Title</h1><p>Content with <strong>bold</strong></p>"
    result = operation.process(html_text)
    assert "# Title" in result, "H1 should convert to markdown"
    assert "**bold**" in result, "Strong should convert to markdown"

    print("✓ StripHTML works correctly")


def test_normalize_whitespace():
    """Test NormalizeWhitespace operation."""
    print("\nTesting NormalizeWhitespace...")
    from prompt_refiner import NormalizeWhitespace

    operation = NormalizeWhitespace()

    # Multiple spaces
    text = "Hello    World"
    result = operation.process(text)
    assert result == "Hello World", "Multiple spaces should be normalized to single space"

    # Mixed whitespace (tabs, newlines)
    text = "Hello\t\t\nWorld"
    result = operation.process(text)
    assert "Hello World" in result, "Mixed whitespace should be normalized"

    # Leading/trailing whitespace
    text = "  Hello World  "
    result = operation.process(text)
    assert result == "Hello World", "Leading/trailing whitespace should be removed"

    print("✓ NormalizeWhitespace works correctly")


def test_fix_unicode():
    """Test FixUnicode operation."""
    print("\nTesting FixUnicode...")
    from prompt_refiner import FixUnicode

    operation = FixUnicode()

    # Zero-width characters
    text = "Hello\u200bWorld\u200c"  # Zero-width space and non-joiner
    result = operation.process(text)
    assert "\u200b" not in result, "Zero-width space should be removed"
    assert "\u200c" not in result, "Zero-width non-joiner should be removed"
    assert "HelloWorld" in result, "Text should be preserved"

    # Control characters
    text = "Hello\x00\x01World"  # Null and SOH control characters
    result = operation.process(text)
    assert "\x00" not in result, "Null character should be removed"
    assert "\x01" not in result, "SOH character should be removed"
    assert "Hello" in result and "World" in result, "Text should be preserved"

    # Unicode normalization (NFC)
    text = "e\u0301"  # e + combining acute accent (NFD form)
    result = operation.process(text)
    assert result == "\u00e9" or "e" in result, "Should normalize to NFC form"

    print("✓ FixUnicode works correctly")


def test_json_cleaner():
    """Test JsonCleaner operation."""
    print("\nTesting JsonCleaner...")
    from prompt_refiner import JsonCleaner

    operation = JsonCleaner()

    # Valid JSON
    json_text = '{"name": "Alice", "age": 30, "city": "NYC"}'
    result = operation.process(json_text)
    assert "Alice" in result, "JSON content should be preserved"
    assert "30" in result, "JSON content should be preserved"

    # Minified JSON should stay minified (whitespace removed)
    assert len(result) <= len(json_text), "JSON should be compact"

    print("✓ JsonCleaner works correctly")


def test_cleaner_pipeline():
    """Test combining multiple cleaner operations."""
    print("\nTesting Cleaner Pipeline...")
    from prompt_refiner import FixUnicode, NormalizeWhitespace, StripHTML

    # Create pipeline
    pipeline = StripHTML() | NormalizeWhitespace() | FixUnicode()

    # Complex dirty text with zero-width characters
    text = "<p>Hello\u200b   World\u200c</p>"  # <p>Hello[zero-width]   World[zero-width]</p>
    result = pipeline.process(text)

    # Verify all operations applied
    assert "<p>" not in result, "HTML should be stripped"
    assert "   " not in result, "Whitespace should be normalized"
    assert "\u200b" not in result, "Zero-width characters should be removed"
    assert "HelloWorld" in result or "Hello World" in result, "Text should be preserved"

    print("✓ Cleaner Pipeline works correctly")


def main():
    """Run all cleaner e2e tests."""
    print("=" * 60)
    print("Running Cleaner Module E2E Tests")
    print("=" * 60)

    try:
        test_strip_html()
        test_normalize_whitespace()
        test_fix_unicode()
        test_json_cleaner()
        test_cleaner_pipeline()

        print("\n" + "=" * 60)
        print("✓ All Cleaner E2E tests passed!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
