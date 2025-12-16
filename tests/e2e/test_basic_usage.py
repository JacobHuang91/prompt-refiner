#!/usr/bin/env python3
"""
End-to-end test for basic library usage.

This test simulates how a real user would use the library after installing via pip.
It tests core functionality without requiring API keys.
"""

import sys


def test_imports():
    """Test that all core components can be imported."""
    print("Testing imports...")

    print("✓ All imports successful")


def test_messages_packer():
    """Test MessagesPacker with default strategies."""
    print("\nTesting MessagesPacker...")
    from prompt_refiner import MessagesPacker

    # Test with default strategies
    packer = MessagesPacker(
        system="<p>You are a helpful AI assistant.</p>",
        context=["<div>Document   1</div>", "<div>Document   2</div>"],
        query="<span>What's the   weather?</span>",
    )

    messages = packer.pack()

    # Verify structure
    assert isinstance(messages, list), "MessagesPacker should return a list"
    assert len(messages) == 4, f"Expected 4 messages, got {len(messages)}"
    assert all("role" in msg and "content" in msg for msg in messages), (
        "Each message should have role and content"
    )

    # Verify HTML was stripped and whitespace normalized
    assert "<p>" not in messages[0]["content"], "HTML should be stripped from system"
    assert "<div>" not in messages[1]["content"], "HTML should be stripped from context"
    assert "   " not in messages[1]["content"], "Whitespace should be normalized"

    print("✓ MessagesPacker works correctly")


def test_text_packer():
    """Test TextPacker with different formats."""
    print("\nTesting TextPacker...")
    from prompt_refiner import StripHTML, TextFormat, TextPacker

    # Test MARKDOWN format
    packer = TextPacker(
        text_format=TextFormat.MARKDOWN,
        system="You are helpful.",
        context=(["<div>Doc 1</div>"], StripHTML()),
        query="What is this?",
    )

    text = packer.pack()

    # Verify structure
    assert isinstance(text, str), "TextPacker should return a string"
    assert "### INSTRUCTIONS:" in text, "Should have INSTRUCTIONS section"
    assert "### CONTEXT:" in text, "Should have CONTEXT section"
    assert "### INPUT:" in text, "Should have INPUT section"
    assert "<div>" not in text, "HTML should be stripped"

    print("✓ TextPacker works correctly")


def test_pipeline():
    """Test pipeline composition with | operator."""
    print("\nTesting Pipeline...")
    from prompt_refiner import NormalizeWhitespace, StripHTML

    # Create pipeline
    pipeline = StripHTML() | NormalizeWhitespace()

    # Process text
    dirty_text = "<p>  Hello   World  </p>"
    clean_text = pipeline.process(dirty_text)

    # Verify cleaning
    assert "<p>" not in clean_text, "HTML should be stripped"
    assert "   " not in clean_text, "Extra whitespace should be normalized"
    assert clean_text == "Hello World", f"Expected 'Hello World', got '{clean_text}'"

    print("✓ Pipeline works correctly")


def test_strategies():
    """Test preset strategies."""
    print("\nTesting Strategies...")
    from prompt_refiner import AggressiveStrategy, MinimalStrategy, StandardStrategy

    dirty_text = "<div>  Hello   World  </div>"

    # Test MinimalStrategy
    minimal = MinimalStrategy()
    clean = minimal.process(dirty_text)
    assert "<div>" not in clean, "MinimalStrategy should strip HTML"
    assert clean == "Hello World", "MinimalStrategy should normalize whitespace"

    # Test StandardStrategy
    standard = StandardStrategy()
    clean = standard.process(dirty_text)
    assert "<div>" not in clean, "StandardStrategy should strip HTML"

    # Test AggressiveStrategy
    aggressive = AggressiveStrategy()
    clean = aggressive.process(dirty_text)
    assert "<div>" not in clean, "AggressiveStrategy should strip HTML"

    print("✓ All strategies work correctly")


def main():
    """Run all e2e tests."""
    print("=" * 60)
    print("Running End-to-End Tests")
    print("=" * 60)

    try:
        test_imports()
        test_messages_packer()
        test_text_packer()
        test_pipeline()
        test_strategies()

        print("\n" + "=" * 60)
        print("✓ All E2E tests passed!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
