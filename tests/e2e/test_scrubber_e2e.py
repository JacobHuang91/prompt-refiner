#!/usr/bin/env python3
"""
End-to-end tests for Scrubber module operations.

Tests all scrubber operations as a user would use them after pip install.
"""

import sys


def test_redact_pii_basic():
    """Test RedactPII operation with basic patterns."""
    print("\nTesting RedactPII (basic)...")
    from prompt_refiner import RedactPII

    # Test email redaction
    operation = RedactPII()
    text = "Contact me at john.doe@example.com for more info."
    result = operation.process(text)
    assert "john.doe@example.com" not in result, "Email should be redacted"
    assert "[EMAIL]" in result or "***" in result, "Should have redaction marker"

    # Test phone number redaction
    text = "Call me at 123-456-7890"
    result = operation.process(text)
    assert "123-456-7890" not in result or "[PHONE]" in result or "***" in result, (
        "Phone number should be redacted or masked"
    )

    # Test SSN redaction
    text = "My SSN is 123-45-6789"
    result = operation.process(text)
    assert "123-45-6789" not in result, "SSN should be redacted"

    print("✓ RedactPII (basic) works correctly")


def test_redact_pii_custom():
    """Test RedactPII with custom patterns."""
    print("\nTesting RedactPII (custom patterns)...")
    from prompt_refiner import RedactPII

    # Custom pattern for API keys
    operation = RedactPII(
        custom_patterns={
            "API_KEY": r"sk-[a-zA-Z0-9]{32}",
        }
    )

    text = "Use this API key: sk-abcd1234efgh5678ijkl9012mnop3456"
    result = operation.process(text)
    assert "sk-abcd1234efgh5678ijkl9012mnop3456" not in result, "API key should be redacted"
    assert "[API_KEY]" in result, "Should have custom redaction marker"

    print("✓ RedactPII (custom) works correctly")


def test_redact_pii_pipeline():
    """Test RedactPII in pipeline with other operations."""
    print("\nTesting RedactPII in Pipeline...")
    from prompt_refiner import NormalizeWhitespace, RedactPII, StripHTML

    # Create pipeline: clean HTML, normalize whitespace, redact PII
    pipeline = StripHTML() | NormalizeWhitespace() | RedactPII()

    text = "<p>Email   me at   user@test.com</p>"
    result = pipeline.process(text)

    # Verify all operations applied
    assert "<p>" not in result, "HTML should be stripped"
    assert "   " not in result, "Whitespace should be normalized"
    assert "user@test.com" not in result, "Email should be redacted"

    print("✓ RedactPII Pipeline works correctly")


def main():
    """Run all scrubber e2e tests."""
    print("=" * 60)
    print("Running Scrubber Module E2E Tests")
    print("=" * 60)

    try:
        test_redact_pii_basic()
        test_redact_pii_custom()
        test_redact_pii_pipeline()

        print("\n" + "=" * 60)
        print("✓ All Scrubber E2E tests passed!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
