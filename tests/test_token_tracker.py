"""Tests for TokenTracker."""

from prompt_refiner import (
    AggressiveStrategy,
    MinimalStrategy,
    NormalizeWhitespace,
    Pipeline,
    StandardStrategy,
    StripHTML,
    TokenTracker,
)


def simple_counter(text: str) -> int:
    """Simple character-based counter for testing."""
    return len(text) // 4


def test_token_tracker_basic():
    """Test basic token tracking."""
    refiner = StripHTML()

    with TokenTracker(refiner, simple_counter) as tracker:
        result = tracker.process("<p>Hello World</p>")

    assert result == "Hello World"
    assert tracker.stats["original_tokens"] == 4  # 17 chars / 4 = 4
    assert tracker.stats["refined_tokens"] == 2  # 11 chars / 4 = 2
    assert tracker.stats["saved_tokens"] == 2
    assert "%" in tracker.stats["saving_percent"]


def test_token_tracker_with_pipeline():
    """Test token tracking with a pipeline."""
    pipeline = StripHTML() | NormalizeWhitespace()

    with TokenTracker(pipeline, simple_counter) as tracker:
        result = tracker.process("<div>Hello   World</div>")

    assert result == "Hello World"
    assert tracker.stats["saved_tokens"] > 0


def test_token_tracker_with_strategy():
    """Test token tracking with a strategy."""
    strategy = MinimalStrategy()

    with TokenTracker(strategy, simple_counter) as tracker:
        result = tracker.process("<p>Hello   World</p>")

    assert result == "Hello World"
    assert tracker.stats["saved_tokens"] > 0


def test_token_tracker_context_manager():
    """Test context manager protocol."""
    refiner = StripHTML()

    # Verify __enter__ returns self
    with TokenTracker(refiner, simple_counter) as tracker:
        assert isinstance(tracker, TokenTracker)
        tracker.process("<p>Test</p>")

    # Stats should be available after exiting context
    assert "original_tokens" in tracker.stats


def test_token_tracker_stats_before_process():
    """Test stats returns empty dict before processing."""
    refiner = StripHTML()

    with TokenTracker(refiner, simple_counter) as tracker:
        # Before calling process()
        assert tracker.stats == {}


def test_token_tracker_original_and_result():
    """Test accessing original and result text."""
    refiner = StripHTML()

    with TokenTracker(refiner, simple_counter) as tracker:
        result = tracker.process("<p>Hello World</p>")

    assert tracker.original_text == "<p>Hello World</p>"
    assert tracker.result == "Hello World"
    assert result == "Hello World"


def test_token_tracker_empty_text():
    """Test tracking with empty text."""
    refiner = StripHTML()

    with TokenTracker(refiner, simple_counter) as tracker:
        result = tracker.process("")

    assert result == ""
    assert tracker.stats["original_tokens"] == 0
    assert tracker.stats["refined_tokens"] == 0
    assert tracker.stats["saved_tokens"] == 0


def test_token_tracker_no_change():
    """Test tracking when text doesn't change."""
    refiner = StripHTML()

    with TokenTracker(refiner, simple_counter) as tracker:
        result = tracker.process("Plain text")

    assert result == "Plain text"
    assert tracker.stats["original_tokens"] == tracker.stats["refined_tokens"]
    assert tracker.stats["saved_tokens"] == 0
    assert tracker.stats["saving_percent"] == "0.0%"


def test_token_tracker_custom_counter():
    """Test with a custom counter function."""

    def custom_counter(text: str) -> int:
        """Count words instead of characters."""
        return len(text.split())

    refiner = StripHTML()

    with TokenTracker(refiner, custom_counter) as tracker:
        tracker.process("<p>Hello World Test</p>")

    # Original: 3 words, Result: 3 words
    assert tracker.stats["original_tokens"] == 3
    assert tracker.stats["refined_tokens"] == 3


def test_token_tracker_multiple_strategies():
    """Test comparing different strategies."""
    text = "<div>Hello   World</div>"
    strategies = [MinimalStrategy(), StandardStrategy(), AggressiveStrategy()]

    results = []
    for strategy in strategies:
        with TokenTracker(strategy, simple_counter) as tracker:
            tracker.process(text)
            results.append(tracker.stats["saved_tokens"])

    # All strategies should save some tokens
    assert all(saved > 0 for saved in results)


def test_token_tracker_multiple_process_calls():
    """Test that only the last process() call is tracked."""
    refiner = StripHTML()

    with TokenTracker(refiner, simple_counter) as tracker:
        tracker.process("<p>First</p>")
        tracker.process("<p>Second</p>")

    # Should only track the second call
    assert tracker.original_text == "<p>Second</p>"
    assert tracker.result == "Second"


def test_token_tracker_saving_percent_calculation():
    """Test that saving_percent is calculated correctly."""
    refiner = StripHTML()

    with TokenTracker(refiner, simple_counter) as tracker:
        tracker.process("<p>Test</p>")

    original = tracker.stats["original_tokens"]
    saved = tracker.stats["saved_tokens"]

    expected_percent = (saved / original * 100) if original > 0 else 0.0
    actual_percent = float(tracker.stats["saving_percent"].rstrip("%"))

    assert abs(expected_percent - actual_percent) < 0.1


def test_token_tracker_properties_before_process():
    """Test that properties return None before process() is called."""
    refiner = StripHTML()

    with TokenTracker(refiner, simple_counter) as tracker:
        assert tracker.original_text is None
        assert tracker.result is None
        assert tracker.stats == {}


def test_token_tracker_with_pipeline_builder():
    """Test with Pipeline created using builder pattern."""
    pipeline = Pipeline().pipe(StripHTML()).pipe(NormalizeWhitespace())

    with TokenTracker(pipeline, simple_counter) as tracker:
        result = tracker.process("<div>Hello   World</div>")

    assert result == "Hello World"
    assert tracker.stats["saved_tokens"] > 0


def test_token_tracker_with_pipeline_list():
    """Test with Pipeline created from list."""
    pipeline = Pipeline([StripHTML(), NormalizeWhitespace()])

    with TokenTracker(pipeline, simple_counter) as tracker:
        result = tracker.process("<div>Hello   World</div>")

    assert result == "Hello World"
    assert tracker.stats["saved_tokens"] > 0
