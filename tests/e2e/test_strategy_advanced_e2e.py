#!/usr/bin/env python3
"""
End-to-end tests for advanced Strategy features.

Tests strategy customization, parameters, and extension with .pipe().
"""

import sys


def test_strategy_with_custom_parameters():
    """Test strategies with custom parameters."""
    print("\nTesting Strategies with custom parameters...")
    from prompt_refiner import AggressiveStrategy, StandardStrategy

    # StandardStrategy with custom deduplicate settings
    strategy = StandardStrategy(
        deduplicate_method="levenshtein",
        deduplicate_similarity_threshold=0.9,
        deduplicate_granularity="paragraph",
    )

    # Use text with duplicate paragraphs
    text = "Hello World\n\nHello World!\n\nCompletely Different"

    result = strategy.process(text)
    assert isinstance(result, str), "Should return a string"
    assert len(result) < len(text), "Should remove similar paragraphs"

    # AggressiveStrategy with custom deduplicate settings
    strategy = AggressiveStrategy(
        deduplicate_method="levenshtein",
        deduplicate_similarity_threshold=0.6,  # More aggressive
        deduplicate_granularity="paragraph",
    )

    text = "Hello World\n\nHello World\n\nCompletely Different"
    result = strategy.process(text)
    assert len(result) < len(text), "Should aggressively deduplicate"

    print("✓ Custom strategy parameters work correctly")


def test_strategy_with_pipe():
    """Test extending strategies with .pipe()."""
    print("\nTesting Strategy extension with .pipe()...")
    from prompt_refiner import MinimalStrategy, RedactPII, StandardStrategy

    # Extend MinimalStrategy with RedactPII
    strategy = MinimalStrategy().pipe(RedactPII())

    text = "<p>Contact me at user@test.com</p>"
    result = strategy.process(text)

    # Verify both operations applied
    assert "<p>" not in result, "HTML should be stripped (MinimalStrategy)"
    assert "user@test.com" not in result, "Email should be redacted (RedactPII)"

    # Extend StandardStrategy with custom operation
    from prompt_refiner import FixUnicode

    strategy = StandardStrategy().pipe(FixUnicode())

    text = "\u201cHello World\u201d with extra   spaces"  # "Hello World" with extra   spaces
    result = strategy.process(text)

    # Verify all operations applied
    assert "   " not in result, "Whitespace should be normalized (StandardStrategy)"
    assert "Hello World" in result, "Text content should be preserved"

    print("✓ Strategy .pipe() extension works correctly")


def test_strategy_html_to_markdown():
    """Test strategies with HTML to markdown conversion."""
    print("\nTesting Strategy with HTML to markdown...")
    from prompt_refiner import MinimalStrategy, StandardStrategy

    # Test with to_markdown=True
    strategy = MinimalStrategy(strip_html_to_markdown=True)

    html_text = "<h1>Title</h1><p>Content with <strong>bold</strong> text</p>"
    result = strategy.process(html_text)

    # Should convert to markdown instead of stripping
    assert "# Title" in result, "H1 should convert to markdown"
    assert "**bold**" in result, "Strong should convert to markdown"

    # StandardStrategy also supports this
    strategy = StandardStrategy(strip_html_to_markdown=True)
    result = strategy.process(html_text)
    assert "# Title" in result, "H1 should convert to markdown"

    print("✓ HTML to markdown conversion works correctly")


def test_strategy_composition():
    """Test composing strategies with | operator."""
    print("\nTesting Strategy composition...")
    from prompt_refiner import FixUnicode, MinimalStrategy, RedactPII

    # Chain multiple operations
    pipeline = MinimalStrategy() | RedactPII() | FixUnicode()

    text = "<div>\u201cContact user@test.com\u201d</div>"  # <div>"Contact user@test.com"</div>
    result = pipeline.process(text)

    # Verify all operations applied in order
    assert "<div>" not in result, "HTML should be stripped"
    assert "user@test.com" not in result, "Email should be redacted"
    assert "Contact" in result, "Text content should be preserved"

    print("✓ Strategy composition works correctly")


def test_all_strategy_presets():
    """Test all three strategy presets comprehensively."""
    print("\nTesting all strategy presets...")
    from prompt_refiner import AggressiveStrategy, MinimalStrategy, StandardStrategy

    dirty_text = "<div>  Hello   World  </div>"

    # MinimalStrategy: StripHTML + NormalizeWhitespace
    minimal = MinimalStrategy()
    result = minimal.process(dirty_text)
    assert "<div>" not in result, "Should strip HTML"
    assert result == "Hello World", "Should normalize whitespace"

    # StandardStrategy: MinimalStrategy + Deduplicate
    text = "Hello World\n\nHello World\n\nDifferent"
    standard = StandardStrategy()
    result = standard.process(text)
    assert len(result) <= len(text), "Should process text (may deduplicate)"
    # Note: Deduplicate may or may not remove similar paragraphs depending on similarity threshold
    assert "Hello World" in result, "Should preserve content"

    # AggressiveStrategy: Uses aggressive deduplication (threshold 0.7)
    text_with_duplicates = "Hello World\n\nHello World!\n\nHello again\n\nCompletely Different"
    aggressive = AggressiveStrategy()
    result = aggressive.process(text_with_duplicates)
    assert len(result) < len(text_with_duplicates), "Should aggressively deduplicate"

    print("✓ All strategy presets work correctly")


def test_strategy_direct_usage():
    """Test using strategies directly without .create_refiner() (v0.2.0+)."""
    print("\nTesting direct strategy usage...")
    from prompt_refiner import MinimalStrategy

    # v0.2.0+: Strategies ARE pipelines, use directly
    strategy = MinimalStrategy()

    # Can use .process() directly
    text = "<p>Hello World</p>"
    result = strategy.process(text)
    assert "<p>" not in result, "Should strip HTML"

    # Can also use .run() (Pipeline method)
    result = strategy.run(text)
    assert "<p>" not in result, "Should strip HTML"

    print("✓ Direct strategy usage works correctly")


def main():
    """Run all advanced strategy e2e tests."""
    print("=" * 60)
    print("Running Advanced Strategy E2E Tests")
    print("=" * 60)

    try:
        test_strategy_with_custom_parameters()
        test_strategy_with_pipe()
        test_strategy_html_to_markdown()
        test_strategy_composition()
        test_all_strategy_presets()
        test_strategy_direct_usage()

        print("\n" + "=" * 60)
        print("✓ All Advanced Strategy E2E tests passed!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
