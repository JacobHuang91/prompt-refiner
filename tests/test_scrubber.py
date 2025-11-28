"""Tests for Scrubber module operations."""

from prompt_refiner import RedactPII


def test_redact_pii_email():
    """Test email redaction."""
    op = RedactPII(redact_types={"email"})
    result = op.process("Contact me at john.doe@example.com")
    assert "john.doe@example.com" not in result
    assert "[EMAIL]" in result


def test_redact_pii_phone():
    """Test phone number redaction."""
    op = RedactPII(redact_types={"phone"})
    result = op.process("Call me at 555-123-4567")
    assert "555-123-4567" not in result
    assert "[PHONE]" in result


def test_redact_pii_ip():
    """Test IP address redaction."""
    op = RedactPII(redact_types={"ip"})
    result = op.process("Server IP is 192.168.1.1")
    assert "192.168.1.1" not in result
    assert "[IP]" in result


def test_redact_pii_credit_card():
    """Test credit card redaction."""
    op = RedactPII(redact_types={"credit_card"})
    result = op.process("Card number: 4532-1234-5678-9010")
    assert "4532-1234-5678-9010" not in result
    assert "[CARD]" in result


def test_redact_pii_url():
    """Test URL redaction."""
    op = RedactPII(redact_types={"url"})
    result = op.process("Visit https://example.com")
    assert "https://example.com" not in result
    assert "[URL]" in result


def test_redact_pii_custom_keywords():
    """Test custom keyword redaction."""
    op = RedactPII(custom_keywords={"secret", "confidential"})
    result = op.process("This is secret and confidential information")
    assert "secret" not in result.lower()
    assert "confidential" not in result.lower()
    assert "[REDACTED]" in result
