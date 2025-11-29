"""Tests for Analyzer module operations."""

from prompt_refiner import CountTokens


def test_count_tokens_basic():
    """Test basic token counting."""
    op = CountTokens()
    result = op.process("hello world test")
    assert result == "hello world test"  # Should not modify text
    stats = op.get_stats()
    assert "tokens" in stats
    # "hello world test" = 16 chars → 16//4 = 4 tokens
    assert stats["tokens"] == 4


def test_count_tokens_with_comparison():
    """Test token counting with original text comparison."""
    original = "hello   world   with   lots   of   spaces"
    op = CountTokens(original_text=original)
    cleaned = "hello world with lots of spaces"
    op.process(cleaned)
    stats = op.get_stats()
    assert "original" in stats
    assert "cleaned" in stats
    assert "saved" in stats
    # original = 42 chars → 42//4 = 10 tokens
    # cleaned = 31 chars → 31//4 = 7 tokens
    assert stats["original"] == 10
    assert stats["cleaned"] == 7
    assert stats["saved"] == 3


def test_count_tokens_format():
    """Test formatted statistics output."""
    original = "one two three four five"
    op = CountTokens(original_text=original)
    cleaned = "one two three"
    op.process(cleaned)
    formatted = op.format_stats()
    assert "Original:" in formatted
    assert "Cleaned:" in formatted
    assert "Saved:" in formatted
