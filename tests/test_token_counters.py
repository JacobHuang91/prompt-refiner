"""Tests for token counting helper functions."""

import pytest

from prompt_refiner import (
    character_based_counter,
    create_tiktoken_counter,
    word_based_counter,
)


def test_character_based_counter_basic():
    """Test character-based counter with basic text."""
    result = character_based_counter("Hello World")
    # 11 characters / 4 = 2.75 -> ceil = 3
    assert result == 3


def test_character_based_counter_empty():
    """Test character-based counter with empty string."""
    result = character_based_counter("")
    assert result == 0


def test_character_based_counter_long_text():
    """Test character-based counter with longer text."""
    text = "This is a longer sentence with many words and characters."
    result = character_based_counter(text)
    # 59 characters / 4 = 14.75 -> ceil = 15
    assert result == 15


def test_character_based_counter_exact_multiple():
    """Test character-based counter with exact multiple of 4."""
    text = "Test"  # 4 characters
    result = character_based_counter(text)
    assert result == 1


def test_word_based_counter_basic():
    """Test word-based counter with basic text."""
    result = word_based_counter("Hello World")
    assert result == 2


def test_word_based_counter_empty():
    """Test word-based counter with empty string."""
    result = word_based_counter("")
    assert result == 0


def test_word_based_counter_multiple_spaces():
    """Test word-based counter with multiple spaces."""
    result = word_based_counter("Hello   World   Test")
    # split() handles multiple spaces
    assert result == 3


def test_word_based_counter_newlines():
    """Test word-based counter with newlines."""
    result = word_based_counter("Hello\nWorld\nTest")
    # split() treats newlines as separators
    assert result == 3


def test_word_based_counter_punctuation():
    """Test word-based counter with punctuation."""
    result = word_based_counter("Hello, World!")
    # split() doesn't separate punctuation
    assert result == 2


def test_create_tiktoken_counter_without_tiktoken():
    """Test that create_tiktoken_counter raises ImportError without tiktoken."""
    # Try to import tiktoken
    try:
        import tiktoken  # noqa: F401

        # If tiktoken is installed, skip this test
        pytest.skip("tiktoken is installed, skipping ImportError test")
    except ImportError:
        # tiktoken is not installed, expect ImportError
        with pytest.raises(ImportError) as exc_info:
            create_tiktoken_counter()

        assert "tiktoken is required" in str(exc_info.value)
        assert "pip install llm-prompt-refiner[token]" in str(exc_info.value)


def test_create_tiktoken_counter_with_tiktoken():
    """Test create_tiktoken_counter when tiktoken is available."""
    try:
        import tiktoken  # noqa: F401
    except ImportError:
        pytest.skip("tiktoken not installed")

    # Create counter
    counter = create_tiktoken_counter(model="gpt-4")

    # Test basic usage
    assert callable(counter)
    result = counter("Hello World")
    assert isinstance(result, int)
    assert result > 0


def test_create_tiktoken_counter_empty_text():
    """Test tiktoken counter with empty text."""
    try:
        import tiktoken  # noqa: F401
    except ImportError:
        pytest.skip("tiktoken not installed")

    counter = create_tiktoken_counter()
    result = counter("")
    assert result == 0


def test_create_tiktoken_counter_unknown_model():
    """Test tiktoken counter with unknown model falls back to cl100k_base."""
    try:
        import tiktoken  # noqa: F401
    except ImportError:
        pytest.skip("tiktoken not installed")

    # Unknown model should fall back to cl100k_base
    counter = create_tiktoken_counter(model="unknown-model-12345")

    # Should still work
    result = counter("Hello World")
    assert isinstance(result, int)
    assert result > 0


def test_create_tiktoken_counter_different_models():
    """Test that different models can be specified."""
    try:
        import tiktoken  # noqa: F401
    except ImportError:
        pytest.skip("tiktoken not installed")

    # Test with different models
    models = ["gpt-4", "gpt-3.5-turbo"]

    for model in models:
        counter = create_tiktoken_counter(model=model)
        result = counter("Hello World")
        assert isinstance(result, int)
        assert result > 0


def test_counter_comparison():
    """Compare different counter implementations."""
    text = "Hello World! This is a test."

    char_count = character_based_counter(text)
    word_count = word_based_counter(text)

    # Character-based should generally be higher than word-based
    # 28 chars / 4 = 7, vs 6 words
    assert char_count == 7
    assert word_count == 6


def test_counters_with_html():
    """Test counters with HTML text."""
    html = "<p>Hello World</p>"

    char_count = character_based_counter(html)
    word_count = word_based_counter(html)

    # Character-based: 18 chars / 4 = 4.5 -> ceil = 5
    assert char_count == 5
    # Word-based: 2 tokens (splits "<p>Hello" and "World</p>")
    assert word_count == 2


def test_counters_with_unicode():
    """Test counters with Unicode text."""
    text = "Hello 世界"

    char_count = character_based_counter(text)
    word_count = word_based_counter(text)

    # Both should handle Unicode correctly
    assert char_count > 0
    assert word_count == 2
