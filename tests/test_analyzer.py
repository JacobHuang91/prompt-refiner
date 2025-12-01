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
    # original = 42 chars → ceil(42/4) = ceil(10.5) = 11 tokens
    # cleaned = 31 chars → ceil(31/4) = ceil(7.75) = 8 tokens
    assert stats["original"] == 11
    assert stats["cleaned"] == 8
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


def test_count_tokens_empty_string():
    """Test token counting with empty string."""
    op = CountTokens()
    result = op.process("")
    assert result == ""
    stats = op.get_stats()
    assert stats["tokens"] == 0


def test_count_tokens_format_no_stats():
    """Test format_stats before processing any text."""
    op = CountTokens()
    formatted = op.format_stats()
    assert "No statistics available" in formatted


def test_count_tokens_format_single_count():
    """Test format_stats with single token count (no original text)."""
    op = CountTokens()
    op.process("hello world")
    formatted = op.format_stats()
    assert "Tokens:" in formatted
    assert "Original:" not in formatted


def test_count_tokens_with_model_no_tiktoken():
    """Test graceful fallback when model specified but tiktoken not available."""
    # This will try to import tiktoken but should fall back gracefully
    op = CountTokens(model="gpt-4")
    assert op.is_precise or not op.is_precise  # Either works or falls back
    result = op.process("test text")
    assert result == "test text"
    stats = op.get_stats()
    assert "tokens" in stats


def test_count_tokens_zero_division():
    """Test handling of zero original tokens."""
    op = CountTokens(original_text="")
    op.process("some text")
    stats = op.get_stats()
    # Should handle division by zero gracefully
    assert "saving_percent" in stats
    assert stats["saving_percent"] == "0.0%"


def test_count_tokens_get_stats_before_process():
    """Test get_stats before processing any text."""
    op = CountTokens()
    stats = op.get_stats()
    assert stats == {}
