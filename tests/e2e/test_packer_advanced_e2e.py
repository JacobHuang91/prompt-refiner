#!/usr/bin/env python3
"""
End-to-end tests for advanced Packer features.

Tests text formats, priorities, roles, and token savings tracking.
"""

import sys


def test_text_packer_all_formats():
    """Test TextPacker with all text formats."""
    print("\nTesting TextPacker formats...")
    from prompt_refiner import TextFormat, TextPacker

    # Test RAW format
    packer = TextPacker(
        text_format=TextFormat.RAW,
        system="You are helpful.",
        context=["Doc 1", "Doc 2"],
        query="What is this?",
    )
    text = packer.pack()
    assert isinstance(text, str), "Should return string"
    assert "You are helpful." in text, "Should contain system message"
    assert "Doc 1" in text, "Should contain context"

    # Test MARKDOWN format
    packer = TextPacker(
        text_format=TextFormat.MARKDOWN,
        system="You are helpful.",
        context=["Doc 1"],
        query="What is this?",
    )
    text = packer.pack()
    assert "### INSTRUCTIONS:" in text, "Should have INSTRUCTIONS section"
    assert "### CONTEXT:" in text, "Should have CONTEXT section"
    assert "### INPUT:" in text, "Should have INPUT section"

    # Test XML format
    packer = TextPacker(
        text_format=TextFormat.XML,
        system="You are helpful.",
        context=["Doc 1"],
        query="What is this?",
    )
    text = packer.pack()
    assert "<system>" in text or "<query>" in text or "<context>" in text, (
        "Should have XML role tags"
    )
    assert "</system>" in text or "</query>" in text or "</context>" in text, (
        "Should have closing XML tags"
    )

    print("✓ All TextPacker formats work correctly")


def test_messages_packer_with_roles():
    """Test MessagesPacker with semantic roles."""
    print("\nTesting MessagesPacker with roles...")
    from prompt_refiner import (
        ROLE_ASSISTANT,
        ROLE_USER,
        MessagesPacker,
    )

    # Test with explicit roles
    packer = MessagesPacker(
        system="You are helpful.",
        context=["Doc 1", "Doc 2"],
        query="What is this?",
        history=[
            {"role": ROLE_USER, "content": "Previous question"},
            {"role": ROLE_ASSISTANT, "content": "Previous answer"},
        ],
    )

    messages = packer.pack()

    # Verify roles
    assert messages[0]["role"] == "system", "First should be system"
    assert messages[1]["role"] == "user", "Context becomes user message"
    assert any("Previous question" in msg["content"] for msg in messages), "Should include history"

    print("✓ MessagesPacker roles work correctly")


def test_packer_with_priorities():
    """Test packer with custom priorities."""
    print("\nTesting Packer with priorities...")
    from prompt_refiner import (
        MessagesPacker,
    )

    # System and query have highest priorities by default
    packer = MessagesPacker(
        system="Critical system message.",
        context=["Low priority doc"],
        query="Important query",
    )

    messages = packer.pack()

    # System should come first (highest priority)
    assert "Critical system message" in messages[0]["content"], "System should be first"
    # Query should come last as user message
    assert "Important query" in messages[-1]["content"], "Query should be last"

    print("✓ Packer priorities work correctly")


def test_packer_with_custom_refining():
    """Test packer with custom refining strategies."""
    print("\nTesting Packer with custom refining...")
    from prompt_refiner import (
        AggressiveStrategy,
        MessagesPacker,
        NormalizeWhitespace,
        StripHTML,
    )

    # Override default strategies with custom pipeline
    packer = MessagesPacker(
        system=("<p>System   message</p>", StripHTML() | NormalizeWhitespace()),
        context=(
            ["<div>Doc   1</div>", "<div>Doc   2</div>"],
            AggressiveStrategy(),
        ),
        query="What is this?",
    )

    messages = packer.pack()

    # Verify custom refining applied
    assert "<p>" not in messages[0]["content"], "HTML should be stripped"
    assert "<div>" not in messages[1]["content"], "HTML should be stripped"
    assert "   " not in messages[0]["content"], "Whitespace should be normalized"

    print("✓ Custom refining works correctly")


def test_packer_token_savings():
    """Test packer automatic refining (saves tokens)."""
    print("\nTesting Packer automatic refining...")
    from prompt_refiner import MessagesPacker

    # Test automatic refining (default behavior in v0.2.1)
    packer = MessagesPacker(
        system="<p>System   message</p>",
        context=["<div>Doc   1</div>", "<div>Doc   2</div>"],
        query="<span>Query   text</span>",
    )

    messages = packer.pack()

    # Verify automatic refining removed HTML and normalized whitespace
    system_content = messages[0]["content"]
    assert "<p>" not in system_content, "HTML should be automatically stripped from system"
    assert "   " not in system_content, "Whitespace should be automatically normalized"

    # Verify context was refined
    context_content = messages[1]["content"]
    assert "<div>" not in context_content, "HTML should be automatically stripped from context"

    # Verify query was refined
    query_content = messages[-1]["content"]
    assert "<span>" not in query_content, "HTML should be automatically stripped from query"

    print("✓ Automatic refining works correctly (saves tokens)")


def test_packer_empty_sections():
    """Test packer with empty sections."""
    print("\nTesting Packer with empty sections...")
    from prompt_refiner import MessagesPacker, TextFormat, TextPacker

    # MessagesPacker with only system and query
    packer = MessagesPacker(
        system="You are helpful.",
        query="What is this?",
    )
    messages = packer.pack()
    assert len(messages) == 2, "Should have 2 messages"
    assert messages[0]["role"] == "system", "First should be system"
    assert messages[1]["role"] == "user", "Second should be user"

    # TextPacker with only system
    packer = TextPacker(
        text_format=TextFormat.MARKDOWN,
        system="You are helpful.",
    )
    text = packer.pack()
    assert "### INSTRUCTIONS:" in text, "Should have INSTRUCTIONS"
    assert isinstance(text, str), "Should return string"

    print("✓ Empty sections handled correctly")


def main():
    """Run all advanced packer e2e tests."""
    print("=" * 60)
    print("Running Advanced Packer E2E Tests")
    print("=" * 60)

    try:
        test_text_packer_all_formats()
        test_messages_packer_with_roles()
        test_packer_with_priorities()
        test_packer_with_custom_refining()
        test_packer_token_savings()
        test_packer_empty_sections()

        print("\n" + "=" * 60)
        print("✓ All Advanced Packer E2E tests passed!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
