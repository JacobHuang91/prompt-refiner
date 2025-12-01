"""Tests for TextPacker (text completion APIs)."""

from prompt_refiner import (
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_QUERY,
    PRIORITY_SYSTEM,
    ROLE_ASSISTANT,
    ROLE_CONTEXT,
    ROLE_QUERY,
    ROLE_SYSTEM,
    ROLE_USER,
    NormalizeWhitespace,
    StripHTML,
    TextFormat,
    TextPacker,
)


def test_text_packer_basic():
    """Test basic text packing."""
    packer = TextPacker(max_tokens=100)

    packer.add("System prompt", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)
    packer.add("User query", role=ROLE_USER, priority=PRIORITY_QUERY)

    text = packer.pack()

    assert isinstance(text, str)
    assert "System prompt" in text
    assert "User query" in text


def test_text_packer_raw_format():
    """Test RAW format (no delimiters)."""
    packer = TextPacker(max_tokens=100, text_format=TextFormat.RAW)

    packer.add("First", role=ROLE_CONTEXT, priority=PRIORITY_HIGH)
    packer.add("Second", role=ROLE_CONTEXT, priority=PRIORITY_HIGH)

    text = packer.pack()

    assert text == "First\n\nSecond"
    assert "###" not in text
    assert "<" not in text


def test_text_packer_markdown_format():
    """Test MARKDOWN format with grouped sections."""
    packer = TextPacker(max_tokens=200, text_format=TextFormat.MARKDOWN)

    packer.add("You are helpful.", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)
    packer.add("Hello!", role=ROLE_QUERY, priority=PRIORITY_QUERY)
    packer.add("Context", role=ROLE_CONTEXT, priority=PRIORITY_HIGH)

    text = packer.pack()

    # Grouped format: INSTRUCTIONS, CONTEXT, INPUT
    assert "### INSTRUCTIONS:\nYou are helpful." in text
    assert "### CONTEXT:\nContext" in text
    assert "### INPUT:\nHello!" in text


def test_text_packer_xml_format():
    """Test XML format."""
    packer = TextPacker(max_tokens=200, text_format=TextFormat.XML)

    packer.add("You are helpful.", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)
    packer.add("Hello!", role=ROLE_USER, priority=PRIORITY_QUERY)
    packer.add("Context", role=ROLE_CONTEXT, priority=PRIORITY_HIGH)

    text = packer.pack()

    assert "<system>\nYou are helpful.\n</system>" in text
    assert "<user>\nHello!\n</user>" in text
    assert "<context>\nContext\n</context>" in text


def test_text_packer_custom_separator():
    """Test custom separator."""
    packer = TextPacker(max_tokens=100, separator=" | ")

    packer.add("first", role=ROLE_CONTEXT, priority=PRIORITY_SYSTEM)
    packer.add("second", role=ROLE_CONTEXT, priority=PRIORITY_SYSTEM)

    text = packer.pack()

    assert "first | second" in text


def test_text_packer_empty_separator():
    """Test empty separator for maximum compression."""
    packer = TextPacker(max_tokens=100, separator="")

    packer.add("First", role=ROLE_CONTEXT, priority=PRIORITY_HIGH)
    packer.add("Second", role=ROLE_CONTEXT, priority=PRIORITY_HIGH)

    text = packer.pack()

    assert text == "FirstSecond"


def test_text_packer_priority_order():
    """Test that items are selected by priority."""
    packer = TextPacker(max_tokens=50, text_format=TextFormat.RAW)

    packer.add("low", role=ROLE_CONTEXT, priority=PRIORITY_LOW)
    packer.add("high", role=ROLE_CONTEXT, priority=PRIORITY_HIGH)
    packer.add("system", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)

    text = packer.pack()

    # System and high priority should be included
    assert "system" in text
    assert "high" in text


def test_text_packer_insertion_order():
    """Test that insertion order is preserved."""
    packer = TextPacker(max_tokens=100, separator=" ")

    packer.add("first", role=ROLE_CONTEXT, priority=PRIORITY_MEDIUM)
    packer.add("second", role=ROLE_CONTEXT, priority=PRIORITY_MEDIUM)
    packer.add("third", role=ROLE_CONTEXT, priority=PRIORITY_MEDIUM)

    text = packer.pack()

    assert text == "first second third"


def test_text_packer_jit_refinement():
    """Test JIT refinement with operations."""
    packer = TextPacker(max_tokens=100)

    dirty_html = "<div><p>Clean this</p></div>"
    packer.add(dirty_html, role=ROLE_CONTEXT, priority=PRIORITY_HIGH, refine_with=StripHTML())

    text = packer.pack()

    assert "<div>" not in text
    assert "Clean this" in text


def test_text_packer_chained_operations():
    """Test chaining multiple operations."""
    packer = TextPacker(max_tokens=100)

    messy = "<p>  Multiple   spaces  </p>"
    packer.add(
        messy,
        role=ROLE_CONTEXT,
        priority=PRIORITY_HIGH,
        refine_with=[StripHTML(), NormalizeWhitespace()],
    )

    text = packer.pack()

    assert "<p>" not in text
    assert "  " not in text
    assert "Multiple spaces" in text


def test_text_packer_empty():
    """Test packer with no items."""
    packer = TextPacker(max_tokens=100)
    text = packer.pack()

    assert text == ""


def test_text_packer_method_chaining():
    """Test fluent API with method chaining."""
    text = (
        TextPacker(max_tokens=100, separator=" ")
        .add("system", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)
        .add("user", role=ROLE_USER, priority=PRIORITY_QUERY)
        .pack()
    )

    assert "system" in text
    assert "user" in text


def test_text_packer_reset():
    """Test resetting the packer."""
    packer = TextPacker(max_tokens=100)

    packer.add("item1", role=ROLE_CONTEXT, priority=PRIORITY_HIGH)
    packer.add("item2", role=ROLE_CONTEXT, priority=PRIORITY_HIGH)

    # Reset
    packer.reset()

    text = packer.pack()
    assert text == ""

    # Should be able to add new items after reset
    packer.add("new_item", role=ROLE_CONTEXT, priority=PRIORITY_HIGH)
    text = packer.pack()
    assert "new_item" in text


def test_text_packer_get_items():
    """Test getting item metadata."""
    packer = TextPacker(max_tokens=100)

    packer.add("first", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)
    packer.add("second", role=ROLE_USER, priority=PRIORITY_QUERY)

    items = packer.get_items()

    assert len(items) == 2
    assert items[0]["priority"] == PRIORITY_SYSTEM
    assert items[0]["role"] == ROLE_SYSTEM
    assert items[1]["priority"] == PRIORITY_QUERY
    assert items[1]["role"] == ROLE_USER


def test_text_packer_rag_scenario():
    """Test realistic RAG scenario with grouped markdown format."""
    packer = TextPacker(max_tokens=300, text_format=TextFormat.MARKDOWN)

    # System prompt
    packer.add("You are a QA assistant.", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)

    # RAG documents
    packer.add("Document 1: Important info", role=ROLE_CONTEXT, priority=PRIORITY_HIGH)
    packer.add("Document 2: More info", role=ROLE_CONTEXT, priority=PRIORITY_MEDIUM)

    # User query
    packer.add("What is the answer?", role=ROLE_QUERY, priority=PRIORITY_QUERY)

    text = packer.pack()

    # Check grouped structure
    assert "### INSTRUCTIONS:" in text
    assert "### CONTEXT:" in text
    assert "- Document 1: Important info" in text  # Bullet points for multiple docs
    assert "- Document 2: More info" in text
    assert "### INPUT:" in text


def test_text_packer_budget_enforcement():
    """Test that token budget is enforced."""
    packer = TextPacker(max_tokens=30, text_format=TextFormat.RAW, separator=" ")

    # Add many items
    for i in range(10):
        packer.add(f"Item{i}", role=ROLE_CONTEXT, priority=PRIORITY_MEDIUM)

    text = packer.pack()

    # Should fit only some items within budget
    words = text.split()
    assert len(words) < 10
    assert len(words) > 0


def test_text_packer_single_item():
    """Test packer with single item."""
    packer = TextPacker(max_tokens=100)
    packer.add("only item", role=ROLE_CONTEXT, priority=PRIORITY_MEDIUM)

    text = packer.pack()
    assert text == "only item"


def test_text_packer_semantic_role_grouping():
    """Test that semantic roles are properly grouped in MARKDOWN format."""
    packer = TextPacker(max_tokens=200, text_format=TextFormat.MARKDOWN)

    packer.add("System instruction", role=ROLE_SYSTEM, priority=PRIORITY_HIGH)
    packer.add("RAG document", role=ROLE_CONTEXT, priority=PRIORITY_HIGH)
    packer.add("Current query", role=ROLE_QUERY, priority=PRIORITY_HIGH)

    text = packer.pack()

    # ROLE_SYSTEM → INSTRUCTIONS section
    assert "### INSTRUCTIONS:\nSystem instruction" in text
    # ROLE_CONTEXT → CONTEXT section
    assert "### CONTEXT:\nRAG document" in text
    # ROLE_QUERY → INPUT section
    assert "### INPUT:\nCurrent query" in text


def test_text_packer_delimiter_overhead():
    """Test that delimiter overhead is accounted in budget."""
    # Use small budget to test overflow prevention
    packer_raw = TextPacker(max_tokens=50, text_format=TextFormat.RAW)
    packer_markdown = TextPacker(max_tokens=50, text_format=TextFormat.MARKDOWN)

    # Add same items to both
    for i in range(5):
        packer_raw.add(f"Item {i}", role=ROLE_USER, priority=PRIORITY_HIGH)
        packer_markdown.add(f"Item {i}", role=ROLE_USER, priority=PRIORITY_HIGH)

    text_raw = packer_raw.pack()
    text_markdown = packer_markdown.pack()

    # Markdown should have more overhead, so might fit fewer items
    items_raw = text_raw.count("Item")
    items_markdown = text_markdown.count("Item")

    assert items_markdown <= items_raw


def test_text_packer_add_messages_helper():
    """Test add_messages helper works with TextPacker."""
    packer = TextPacker(max_tokens=200, text_format=TextFormat.MARKDOWN)

    messages = [
        {"role": ROLE_SYSTEM, "content": "You are helpful."},
        {"role": ROLE_QUERY, "content": "Hello!"},
    ]

    packer.add_messages(messages, priority=PRIORITY_HIGH)

    text = packer.pack()

    # Grouped format
    assert "### INSTRUCTIONS:\nYou are helpful." in text
    assert "### INPUT:\nHello!" in text


def test_text_packer_unlimited_mode():
    """Test unlimited mode when max_tokens is None."""
    packer = TextPacker()  # No max_tokens

    # Add many items
    for i in range(20):
        packer.add(f"Document {i}", role=ROLE_CONTEXT, priority=PRIORITY_MEDIUM)

    packer.add("System prompt", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)
    packer.add("User query", role=ROLE_USER, priority=PRIORITY_QUERY)

    text = packer.pack()

    # All items should be included
    assert "Document 0" in text
    assert "Document 19" in text
    assert "System prompt" in text
    assert "User query" in text
    assert packer.effective_max_tokens is None
    assert packer.raw_max_tokens is None


def test_text_packer_smart_defaults():
    """Test smart priority defaults based on semantic roles."""
    packer = TextPacker(max_tokens=300, text_format=TextFormat.MARKDOWN)

    # Smart defaults: no priority parameter needed!
    packer.add("System instruction", role=ROLE_SYSTEM)  # Auto: PRIORITY_SYSTEM (0)
    packer.add("Current query", role=ROLE_QUERY)  # Auto: PRIORITY_QUERY (10)
    packer.add("RAG document 1", role=ROLE_CONTEXT)  # Auto: PRIORITY_HIGH (20)
    packer.add("RAG document 2", role=ROLE_CONTEXT)  # Auto: PRIORITY_HIGH (20)
    packer.add("User message", role=ROLE_USER)  # Auto: PRIORITY_LOW (40)
    packer.add("Assistant response", role=ROLE_ASSISTANT)  # Auto: PRIORITY_LOW (40)

    # Add conversation history (auto PRIORITY_LOW)
    old_messages = [
        {"role": ROLE_USER, "content": "Old question"},
        {"role": ROLE_ASSISTANT, "content": "Old answer"},
    ]
    packer.add_messages(old_messages)  # Auto: PRIORITY_LOW (40)

    # Check that priorities were inferred correctly
    items = packer.get_items()
    assert items[0]["priority"] == PRIORITY_SYSTEM  # ROLE_SYSTEM
    assert items[1]["priority"] == PRIORITY_QUERY  # ROLE_QUERY
    assert items[2]["priority"] == PRIORITY_HIGH  # ROLE_CONTEXT
    assert items[3]["priority"] == PRIORITY_HIGH  # ROLE_CONTEXT
    assert items[4]["priority"] == PRIORITY_LOW  # ROLE_USER
    assert items[5]["priority"] == PRIORITY_LOW  # ROLE_ASSISTANT
    assert items[6]["priority"] == PRIORITY_LOW  # history
    assert items[7]["priority"] == PRIORITY_LOW  # history

    text = packer.pack()

    # System, query, and context should be included
    assert "System instruction" in text
    assert "Current query" in text
    assert "RAG document 1" in text or "RAG document 2" in text


def test_text_packer_unknown_role():
    """Test that unknown roles default to PRIORITY_MEDIUM."""
    packer = TextPacker(max_tokens=500, text_format=TextFormat.RAW)

    # Add item with unknown role (not one of the semantic constants)
    packer.add("Custom content", role="custom_role")

    # Check that priority defaults to PRIORITY_MEDIUM (30)
    items = packer.get_items()
    assert len(items) == 1
    assert items[0]["priority"] == PRIORITY_MEDIUM
    assert items[0]["role"] == "custom_role"

    text = packer.pack()
    assert "Custom content" in text
