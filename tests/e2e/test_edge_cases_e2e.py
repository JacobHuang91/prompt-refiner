#!/usr/bin/env python3
"""
End-to-end tests for edge cases.

Tests empty inputs, very long inputs, unicode handling, and error conditions.
"""

import sys


def test_empty_inputs():
    """Test operations with empty inputs."""
    print("\nTesting empty inputs...")
    from prompt_refiner import (
        Deduplicate,
        MessagesPacker,
        NormalizeWhitespace,
        StripHTML,
    )

    # Empty string
    operation = StripHTML()
    result = operation.process("")
    assert result == "", "Empty string should return empty string"

    operation = NormalizeWhitespace()
    result = operation.process("")
    assert result == "", "Empty string should return empty string"

    # Empty text for Deduplicate
    operation = Deduplicate()
    result = operation.process("")
    assert result == "", "Empty text should return empty text"

    # Packer with empty content
    packer = MessagesPacker(system="", query="Test")
    messages = packer.pack()
    assert len(messages) > 0, "Should handle empty system message"

    print("✓ Empty inputs handled correctly")


def test_very_long_inputs():
    """Test operations with very long inputs."""
    print("\nTesting very long inputs...")
    from prompt_refiner import NormalizeWhitespace, StripHTML, TruncateTokens

    # Very long text (10K words)
    long_text = "word " * 10000

    # Should handle without errors
    operation = NormalizeWhitespace()
    result = operation.process(long_text)
    assert len(result) > 0, "Should process long text"

    # Truncation should reduce size
    operation = TruncateTokens(max_tokens=100)
    result = operation.process(long_text)
    assert len(result) < len(long_text), "Should truncate long text"

    # Very long HTML
    long_html = "<div>" + "content " * 1000 + "</div>"
    operation = StripHTML()
    result = operation.process(long_html)
    assert "<div>" not in result, "Should strip HTML from long text"

    print("✓ Very long inputs handled correctly")


def test_unicode_edge_cases():
    """Test unicode edge cases."""
    print("\nTesting unicode edge cases...")
    from prompt_refiner import FixUnicode, NormalizeWhitespace, StripHTML

    # Emoji
    text = "Hello 👋 World 🌍"
    operation = NormalizeWhitespace()
    result = operation.process(text)
    assert "👋" in result, "Should preserve emoji"
    assert "🌍" in result, "Should preserve emoji"

    # Chinese characters
    text = "你好世界"
    operation = StripHTML()
    result = operation.process(text)
    assert "你好世界" in result, "Should preserve Chinese characters"

    # Mixed scripts
    text = "Hello مرحبا 你好"
    operation = NormalizeWhitespace()
    result = operation.process(text)
    assert "Hello" in result and "مرحبا" in result and "你好" in result, (
        "Should preserve all scripts"
    )

    # Special unicode characters
    text = "Test\u200b\u200c\u200d"  # Zero-width characters
    operation = FixUnicode()
    result = operation.process(text)
    assert "Test" in result, "Should handle zero-width characters"

    print("✓ Unicode edge cases handled correctly")


def test_malformed_inputs():
    """Test handling of malformed inputs."""
    print("\nTesting malformed inputs...")
    from prompt_refiner import JsonCleaner, StripHTML

    # Malformed HTML
    operation = StripHTML()
    malformed_html = "<div><p>Unclosed tags"
    result = operation.process(malformed_html)
    assert isinstance(result, str), "Should return string even for malformed HTML"

    # Malformed JSON (should handle gracefully)
    operation = JsonCleaner()
    malformed_json = '{"key": value'  # Missing quotes and closing brace
    try:
        result = operation.process(malformed_json)
        # Should either fix it or return as-is
        assert isinstance(result, str), "Should return string"
    except Exception:
        # It's okay to raise an exception for invalid JSON
        pass

    print("✓ Malformed inputs handled gracefully")


def test_special_characters():
    """Test handling of special characters."""
    print("\nTesting special characters...")
    from prompt_refiner import NormalizeWhitespace, StripHTML

    # HTML entities
    text = "Hello &amp; goodbye &lt;world&gt;"
    operation = StripHTML()
    result = operation.process(text)
    assert "&" in result or "amp" in result, "Should handle HTML entities"

    # Newlines and tabs
    text = "Line1\n\nLine2\t\tTab"
    operation = NormalizeWhitespace()
    result = operation.process(text)
    assert "\n\n" not in result or result.count("\n") < text.count("\n"), (
        "Should normalize newlines"
    )

    # Control characters
    text = "Hello\x00\x01\x02World"
    operation = NormalizeWhitespace()
    result = operation.process(text)
    assert isinstance(result, str), "Should handle control characters"

    print("✓ Special characters handled correctly")


def test_type_mismatches():
    """Test handling of type mismatches."""
    print("\nTesting type mismatches...")
    from prompt_refiner import Deduplicate, NormalizeWhitespace

    # Number instead of string
    operation = NormalizeWhitespace()
    try:
        result = operation.process(12345)
        # Should either convert or raise error
        assert isinstance(result, (str, int)), "Should handle number input"
    except (TypeError, AttributeError):
        # Expected - operations expect strings
        pass

    # String instead of list for Deduplicate
    operation = Deduplicate()
    try:
        result = operation.process("not a list")
        # Should handle gracefully
        assert result is not None, "Should return something"
    except (TypeError, AttributeError):
        # Expected - operation expects list
        pass

    print("✓ Type mismatches handled appropriately")


def test_boundary_conditions():
    """Test boundary conditions."""
    print("\nTesting boundary conditions...")
    from prompt_refiner import TruncateTokens

    # Truncate to 0 tokens
    operation = TruncateTokens(max_tokens=0)
    text = "Hello World"
    result = operation.process(text)
    assert result == "" or len(result) < len(text), "Should handle 0 tokens"

    # Truncate to negative tokens (should handle gracefully)
    try:
        operation = TruncateTokens(max_tokens=-10)
        result = operation.process(text)
        # Should either raise error or return empty
        assert isinstance(result, str), "Should return string"
    except ValueError:
        # Expected - negative tokens don't make sense
        pass

    # Text shorter than truncation limit
    operation = TruncateTokens(max_tokens=1000)
    short_text = "Hi"
    result = operation.process(short_text)
    assert result == short_text, "Should not truncate short text"

    print("✓ Boundary conditions handled correctly")


def main():
    """Run all edge case e2e tests."""
    print("=" * 60)
    print("Running Edge Cases E2E Tests")
    print("=" * 60)

    try:
        test_empty_inputs()
        test_very_long_inputs()
        test_unicode_edge_cases()
        test_malformed_inputs()
        test_special_characters()
        test_type_mismatches()
        test_boundary_conditions()

        print("\n" + "=" * 60)
        print("✓ All Edge Cases E2E tests passed!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
