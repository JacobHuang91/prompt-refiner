"""Tests for Refiner pipeline."""

from prompt_refiner import Refiner, NormalizeWhitespace, StripHTML, TruncateTokens


def test_refiner_single_operation():
    """Test refiner with a single operation."""
    refiner = Refiner().pipe(NormalizeWhitespace())

    result = refiner.run("hello   world")
    assert result == "hello world"


def test_refiner_multiple_operations():
    """Test refiner with multiple chained operations."""
    refiner = Refiner().pipe(StripHTML()).pipe(NormalizeWhitespace())

    result = refiner.run("<div>  hello   world  </div>")
    assert result == "hello world"


def test_refiner_full_pipeline():
    """Test the full pipeline from the example."""
    refiner = (
        Refiner()
        .pipe(StripHTML())
        .pipe(NormalizeWhitespace())
        .pipe(TruncateTokens(max_tokens=10, strategy="head"))
    )

    raw_input = "<div>  User input with <b>lots</b> of   spaces... </div>"
    clean_prompt = refiner.run(raw_input)

    # Should strip HTML, normalize whitespace, and keep first 10 words
    assert "<" not in clean_prompt
    assert ">" not in clean_prompt
    assert "  " not in clean_prompt


def test_refiner_empty_pipeline():
    """Test refiner with no operations."""
    refiner = Refiner()

    result = refiner.run("unchanged")
    assert result == "unchanged"


def test_pipe_operator_two_operations():
    """Test pipe operator with two operations."""
    pipeline = StripHTML() | NormalizeWhitespace()

    result = pipeline.run("<div>  hello   world  </div>")
    assert result == "hello world"


def test_pipe_operator_multiple():
    """Test pipe operator with three operations chained."""
    pipeline = StripHTML() | NormalizeWhitespace() | TruncateTokens(max_tokens=3, strategy="head")

    result = pipeline.run("<div>  User input with <b>lots</b> of   spaces... </div>")
    assert result == "User input with"


def test_pipe_operator_full_pipeline():
    """Test pipe operator with realistic full pipeline."""
    pipeline = StripHTML() | NormalizeWhitespace() | TruncateTokens(max_tokens=10, strategy="head")

    raw_input = "<div>  User input with <b>lots</b> of   spaces... </div>"
    clean_prompt = pipeline.run(raw_input)

    # Should strip HTML, normalize whitespace, and keep first 10 words
    assert "<" not in clean_prompt
    assert ">" not in clean_prompt
    assert "  " not in clean_prompt
    assert len(clean_prompt) > 0
