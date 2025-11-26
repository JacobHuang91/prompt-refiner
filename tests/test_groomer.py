"""Tests for Groomer pipeline."""

from prompt_groomer import Groomer, NormalizeWhitespace, StripHTML, TruncateTokens


def test_groomer_single_operation():
    """Test groomer with a single operation."""
    groomer = Groomer().pipe(NormalizeWhitespace())

    result = groomer.run("hello   world")
    assert result == "hello world"


def test_groomer_multiple_operations():
    """Test groomer with multiple chained operations."""
    groomer = Groomer().pipe(StripHTML()).pipe(NormalizeWhitespace())

    result = groomer.run("<div>  hello   world  </div>")
    assert result == "hello world"


def test_groomer_full_pipeline():
    """Test the full pipeline from the example."""
    groomer = (
        Groomer()
        .pipe(StripHTML())
        .pipe(NormalizeWhitespace())
        .pipe(TruncateTokens(max_tokens=10, strategy="head"))
    )

    raw_input = "<div>  User input with <b>lots</b> of   spaces... </div>"
    clean_prompt = groomer.run(raw_input)

    # Should strip HTML, normalize whitespace, and keep first 10 words
    assert "<" not in clean_prompt
    assert ">" not in clean_prompt
    assert "  " not in clean_prompt


def test_groomer_empty_pipeline():
    """Test groomer with no operations."""
    groomer = Groomer()

    result = groomer.run("unchanged")
    assert result == "unchanged"
