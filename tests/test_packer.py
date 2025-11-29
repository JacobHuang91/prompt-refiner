"""Tests for Packer module operations."""

from prompt_refiner import (
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    ContextPacker,
    NormalizeWhitespace,
    StripHTML,
    TruncateTokens,
)


def test_token_packer_basic():
    """Test basic token packing with priority."""
    packer = ContextPacker(max_tokens=10)

    packer.add_item("high priority item", priority=PRIORITY_HIGH)
    packer.add_item("low priority item", priority=PRIORITY_LOW)

    result = packer.pack()

    # High priority item should be included
    assert "high priority item" in result
    # Low priority might be dropped depending on token count


def test_token_packer_priority_order():
    """Test that items are selected by priority."""
    packer = ContextPacker(max_tokens=5)

    # Add items in reverse priority order
    packer.add_item("low", priority=PRIORITY_LOW)
    packer.add_item("medium", priority=PRIORITY_MEDIUM)
    packer.add_item("high", priority=PRIORITY_HIGH)
    packer.add_item("system", priority=PRIORITY_SYSTEM)

    result = packer.pack()

    # System and high priority should be included
    assert "system" in result
    assert "high" in result


def test_token_packer_insertion_order_preserved():
    """Test that insertion order is preserved for selected items."""
    packer = ContextPacker(max_tokens=100)

    # Add items with same priority but different insertion order
    packer.add_item("first", priority=PRIORITY_MEDIUM)
    packer.add_item("second", priority=PRIORITY_MEDIUM)
    packer.add_item("third", priority=PRIORITY_MEDIUM)

    result = packer.pack(separator=" ")

    # Items should appear in insertion order
    assert result == "first second third"


def test_token_packer_budget_enforcement():
    """Test that token budget is enforced."""
    packer = ContextPacker(max_tokens=3)

    # Each word is approximately 1 token
    packer.add_item("one", priority=PRIORITY_HIGH)
    packer.add_item("two", priority=PRIORITY_HIGH)
    packer.add_item("three", priority=PRIORITY_HIGH)
    packer.add_item("four", priority=PRIORITY_HIGH)
    packer.add_item("five", priority=PRIORITY_HIGH)

    result = packer.pack(separator=" ")

    # Should fit approximately 3 items within budget
    words = result.split()
    assert len(words) <= 3


def test_token_packer_with_jit_refinement():
    """Test just-in-time refinement before adding items."""
    packer = ContextPacker(max_tokens=100)

    # Add item with HTML that needs stripping
    dirty_html = "<div><p>Clean this text</p></div>"
    packer.add_item(dirty_html, priority=PRIORITY_HIGH, refine_with=StripHTML())

    result = packer.pack()

    # HTML should be stripped
    assert "<div>" not in result
    assert "<p>" not in result
    assert "Clean this text" in result


def test_token_packer_chained_operations():
    """Test chaining multiple operations in JIT refinement."""
    packer = ContextPacker(max_tokens=100)

    dirty_text = "<p>  Multiple   spaces   here  </p>"
    packer.add_item(
        dirty_text,
        priority=PRIORITY_HIGH,
        refine_with=[StripHTML(), NormalizeWhitespace()],
    )

    result = packer.pack()

    # Should have both HTML stripped and whitespace normalized
    assert "<p>" not in result
    assert "  " not in result
    assert "Multiple spaces here" in result


def test_token_packer_empty():
    """Test packer with no items."""
    packer = ContextPacker(max_tokens=100)
    result = packer.pack()
    assert result == ""


def test_token_packer_custom_separator():
    """Test custom separator between items."""
    packer = ContextPacker(max_tokens=100)

    packer.add_item("first", priority=PRIORITY_SYSTEM)
    packer.add_item("second", priority=PRIORITY_SYSTEM)

    result = packer.pack(separator=" | ")

    assert "first | second" in result


def test_token_packer_method_chaining():
    """Test fluent API with method chaining."""
    result = (
        ContextPacker(max_tokens=100)
        .add_item("system", priority=PRIORITY_SYSTEM)
        .add_item("user", priority=PRIORITY_USER)
        .pack()
    )

    assert "system" in result
    assert "user" in result


def test_token_packer_reset():
    """Test resetting the packer."""
    packer = ContextPacker(max_tokens=100)

    packer.add_item("item1", priority=PRIORITY_HIGH)
    packer.add_item("item2", priority=PRIORITY_HIGH)

    # Reset
    packer.reset()

    result = packer.pack()
    assert result == ""

    # Should be able to add new items after reset
    packer.add_item("new_item", priority=PRIORITY_HIGH)
    result = packer.pack()
    assert "new_item" in result


def test_token_packer_get_items():
    """Test getting item metadata."""
    packer = ContextPacker(max_tokens=100)

    packer.add_item("first", priority=PRIORITY_SYSTEM)
    packer.add_item("second", priority=PRIORITY_USER)

    items = packer.get_items()

    assert len(items) == 2
    assert items[0]["priority"] == PRIORITY_SYSTEM
    # "first" = 5 chars → ceil(5/4) = 2 tokens
    assert items[0]["tokens"] == 2
    assert items[1]["priority"] == PRIORITY_USER
    # "second" = 6 chars → ceil(6/4) = 2 tokens
    assert items[1]["tokens"] == 2


def test_token_packer_priority_constants():
    """Test that priority constants have correct relative values."""
    assert PRIORITY_SYSTEM < PRIORITY_USER
    assert PRIORITY_USER < PRIORITY_HIGH
    assert PRIORITY_HIGH < PRIORITY_MEDIUM
    assert PRIORITY_MEDIUM < PRIORITY_LOW


def test_token_packer_with_truncate():
    """Test using TruncateTokens in JIT refinement."""
    packer = ContextPacker(max_tokens=50)

    long_text = "word " * 100  # Very long text
    packer.add_item(
        long_text,
        priority=PRIORITY_HIGH,
        refine_with=TruncateTokens(max_tokens=10, strategy="head"),
    )

    result = packer.pack()

    # Text should be pre-truncated
    assert len(result.split()) <= 10


def test_token_packer_mixed_priorities():
    """Test realistic scenario with mixed priorities."""
    packer = ContextPacker(max_tokens=20)

    # System prompt (must include)
    packer.add_item("System: You are helpful.", priority=PRIORITY_SYSTEM)

    # User query (must include)
    packer.add_item("User: What is X?", priority=PRIORITY_USER)

    # High priority context (should include if space)
    packer.add_item("Context: Important info.", priority=PRIORITY_HIGH)

    # Low priority context (may be dropped)
    packer.add_item("Extra: Not critical." * 10, priority=PRIORITY_LOW)

    result = packer.pack()

    # System and user should always be included
    assert "System: You are helpful." in result
    assert "User: What is X?" in result


def test_token_packer_rag_scenario():
    """Test realistic RAG scenario."""
    packer = ContextPacker(max_tokens=50)

    # System prompt
    packer.add_item("You are a QA bot.", priority=PRIORITY_SYSTEM)

    # User query
    packer.add_item("What are the features?", priority=PRIORITY_USER)

    # Retrieved documents with different relevance scores
    packer.add_item("Doc 1: Core features are A B C.", priority=PRIORITY_HIGH)

    packer.add_item("Doc 2: Additional features include D E F.", priority=PRIORITY_MEDIUM)

    packer.add_item("Doc 3: Historical context about features." * 5, priority=PRIORITY_LOW)

    result = packer.pack()

    # Should prioritize system, query, and high-priority docs
    assert "You are a QA bot." in result
    assert "What are the features?" in result


def test_token_packer_separator_token_counting():
    """Test that separator tokens are counted correctly."""
    packer = ContextPacker(max_tokens=10)

    # Add multiple short items
    packer.add_item("a", priority=PRIORITY_HIGH)
    packer.add_item("b", priority=PRIORITY_HIGH)
    packer.add_item("c", priority=PRIORITY_HIGH)

    # Use a multi-token separator
    result = packer.pack(separator=" --- ")

    # Result should account for separator tokens
    assert "a" in result
    assert "---" in result


def test_token_packer_exact_budget_fit():
    """Test behavior when items exactly fit the budget."""
    # With character-based estimation (1 token ≈ 4 chars) and ceiling:
    # "one" = 3 chars → ceil(3/4) = 1 token
    # "two" = 3 chars → ceil(3/4) = 1 token
    # "three" = 5 chars → ceil(5/4) = 2 tokens
    # separator " " = 1 char → ceil(1/4) = 1 token
    # Total needed: 1 + 1 + 1 + 2 + 1 = 6 tokens
    # With 10% safety buffer: need max_tokens = 7 (effective = 6.3 → 6)
    packer = ContextPacker(max_tokens=7)

    packer.add_item("one", priority=PRIORITY_HIGH)
    packer.add_item("two", priority=PRIORITY_HIGH)
    packer.add_item("three", priority=PRIORITY_HIGH)

    result = packer.pack(separator=" ")

    # Should fit all three items
    words = result.split()
    assert len(words) == 3


def test_token_packer_single_item():
    """Test packer with single item."""
    packer = ContextPacker(max_tokens=100)
    packer.add_item("only item", priority=PRIORITY_MEDIUM)

    result = packer.pack()
    assert result == "only item"
