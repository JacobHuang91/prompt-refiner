"""Tests for Pipeline."""

from prompt_refiner import NormalizeWhitespace, Pipeline, StripHTML, TruncateTokens


def test_refiner_single_operation():
    """Test refiner with a single operation."""
    refiner = Pipeline().pipe(NormalizeWhitespace())

    result = refiner.run("hello   world")
    assert result == "hello world"


def test_refiner_multiple_operations():
    """Test refiner with multiple chained operations."""
    refiner = Pipeline().pipe(StripHTML()).pipe(NormalizeWhitespace())

    result = refiner.run("<div>  hello   world  </div>")
    assert result == "hello world"


def test_refiner_full_pipeline():
    """Test the full pipeline from the example."""
    refiner = (
        Pipeline()
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
    refiner = Pipeline()

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


def test_refiner_immutability():
    """Test that pipe() creates new instances and doesn't mutate original."""
    # Create base pipeline
    base = StripHTML() | NormalizeWhitespace()
    assert len(base._refiners) == 2

    # Create two different pipelines from base
    pipeline1 = base | TruncateTokens(max_tokens=100)
    pipeline2 = base | TruncateTokens(max_tokens=200)

    # Base should still have 2 refiners
    assert len(base._refiners) == 2

    # New pipelines should have 3 refiners each
    assert len(pipeline1._refiners) == 3
    assert len(pipeline2._refiners) == 3

    # They should be different objects
    assert pipeline1 is not base
    assert pipeline2 is not base
    assert pipeline1 is not pipeline2

    # Verify refiners work independently
    text = "<div>hello   world</div>"
    assert base.run(text) == "hello world"


def test_refiner_pipe_immutability():
    """Test that .pipe() method is also immutable."""
    base = Pipeline().pipe(StripHTML())
    assert len(base._refiners) == 1

    # Add another operation
    extended = base.pipe(NormalizeWhitespace())
    assert len(extended._refiners) == 2

    # Original should still have 1
    assert len(base._refiners) == 1

    # They should be different objects
    assert extended is not base


def test_refiner_empty_constructor():
    """Test creating an empty Refiner."""
    refiner = Pipeline()
    assert len(refiner._refiners) == 0
    assert refiner.run("test") == "test"


def test_refiner_single_operation_constructor():
    """Test creating Refiner with a single operation."""
    refiner = Pipeline(StripHTML())
    assert len(refiner._refiners) == 1
    result = refiner.run("<div>test</div>")
    assert result == "test"


def test_refiner_list_of_operations_constructor():
    """Test creating Refiner with a list of operations."""
    refiner = Pipeline([StripHTML(), NormalizeWhitespace()])
    assert len(refiner._refiners) == 2
    result = refiner.run("<div>  hello   world  </div>")
    assert result == "hello world"


def test_refiner_single_operation_then_pipe():
    """Test creating Refiner with single operation and then piping more."""
    refiner = Pipeline(StripHTML())
    refiner2 = refiner.pipe(NormalizeWhitespace())

    # Original should still have 1 operation (immutability)
    assert len(refiner._refiners) == 1
    # New one should have 2
    assert len(refiner2._refiners) == 2

    result = refiner2.run("<div>  hello   world  </div>")
    assert result == "hello world"


def test_refiner_list_constructor_then_pipe():
    """Test creating Refiner with list and then piping more."""
    refiner = Pipeline([StripHTML(), NormalizeWhitespace()])
    refiner2 = refiner.pipe(TruncateTokens(max_tokens=3, strategy="head"))

    # Original should still have 2 operations
    assert len(refiner._refiners) == 2
    # New one should have 3
    assert len(refiner2._refiners) == 3

    result = refiner2.run("<div>  one two three four five  </div>")
    # Should truncate to approximately 3 tokens
    assert "one two three" in result
    assert len(result.split()) <= 4


def test_refiner_constructor_copies_list():
    """Test that constructor copies the operations list (doesn't mutate input)."""
    ops = [StripHTML(), NormalizeWhitespace()]
    refiner = Pipeline(ops)

    # Modify original list
    ops.append(StripHTML())

    # Refiner should still have only 2 operations
    assert len(refiner._refiners) == 2


def test_refiner_all_construction_methods():
    """Test all ways to construct a Refiner produce same result."""
    text = "<div>  hello   world  </div>"

    # Method 1: Pipe operator
    refiner1 = StripHTML() | NormalizeWhitespace()

    # Method 2: Empty + pipe
    refiner2 = Pipeline().pipe(StripHTML()).pipe(NormalizeWhitespace())

    # Method 3: List constructor
    refiner3 = Pipeline([StripHTML(), NormalizeWhitespace()])

    # Method 4: Single operation + pipe
    refiner4 = Pipeline(StripHTML()).pipe(NormalizeWhitespace())

    # All should produce the same result
    result1 = refiner1.run(text)
    result2 = refiner2.run(text)
    result3 = refiner3.run(text)
    result4 = refiner4.run(text)

    assert result1 == result2 == result3 == result4 == "hello world"
