"""Tests for MessagesPacker (chat completion APIs)."""

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
    MessagesPacker,
    NormalizeWhitespace,
    StripHTML,
)


def test_messages_packer_basic():
    """Test basic message packing."""
    packer = MessagesPacker(max_tokens=100)

    packer.add("System prompt", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)
    packer.add("User query", role=ROLE_USER, priority=PRIORITY_QUERY)

    messages = packer.pack()

    assert isinstance(messages, list)
    assert len(messages) == 2
    assert messages[0] == {"role": "system", "content": "System prompt"}
    assert messages[1] == {"role": "user", "content": "User query"}


def test_messages_packer_priority_order():
    """Test that items are selected by priority."""
    packer = MessagesPacker(max_tokens=50)

    packer.add("low", role=ROLE_USER, priority=PRIORITY_LOW)
    packer.add("high", role=ROLE_USER, priority=PRIORITY_HIGH)
    packer.add("system", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)

    messages = packer.pack()

    # System and high priority should be included
    assert any(msg["content"] == "system" for msg in messages)
    assert any(msg["content"] == "high" for msg in messages)


def test_messages_packer_insertion_order():
    """Test that insertion order is preserved."""
    packer = MessagesPacker(max_tokens=100)

    packer.add("first", role=ROLE_USER, priority=PRIORITY_MEDIUM)
    packer.add("second", role=ROLE_USER, priority=PRIORITY_MEDIUM)
    packer.add("third", role=ROLE_USER, priority=PRIORITY_MEDIUM)

    messages = packer.pack()

    # Should maintain insertion order
    assert messages[0]["content"] == "first"
    assert messages[1]["content"] == "second"
    assert messages[2]["content"] == "third"


def test_messages_packer_semantic_role_mapping():
    """Test that semantic roles are mapped to API-compatible roles."""
    packer = MessagesPacker(max_tokens=200)

    # Add items with semantic roles
    packer.add("System instruction", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)
    packer.add("RAG document", role=ROLE_CONTEXT, priority=PRIORITY_HIGH)
    packer.add("Current query", role=ROLE_QUERY, priority=PRIORITY_QUERY)

    messages = packer.pack()

    assert len(messages) == 3
    # ROLE_SYSTEM stays as "system"
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "System instruction"
    # ROLE_CONTEXT maps to "user" (RAG context provided by user)
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "RAG document"
    # ROLE_QUERY maps to "user" (current user question)
    assert messages[2]["role"] == "user"
    assert messages[2]["content"] == "Current query"


def test_messages_packer_jit_refinement():
    """Test JIT refinement with operations."""
    packer = MessagesPacker(max_tokens=100)

    dirty_html = "<div><p>Clean this</p></div>"
    packer.add(dirty_html, role=ROLE_USER, priority=PRIORITY_HIGH, refine_with=StripHTML())

    messages = packer.pack()

    assert "<div>" not in messages[0]["content"]
    assert "Clean this" in messages[0]["content"]


def test_messages_packer_chained_operations():
    """Test chaining multiple operations in JIT refinement."""
    packer = MessagesPacker(max_tokens=100)

    messy = "<p>  Multiple   spaces  </p>"
    packer.add(
        messy,
        role=ROLE_USER,
        priority=PRIORITY_HIGH,
        refine_with=[StripHTML(), NormalizeWhitespace()],
    )

    messages = packer.pack()

    assert "<p>" not in messages[0]["content"]
    assert "  " not in messages[0]["content"]
    assert "Multiple spaces" in messages[0]["content"]


def test_messages_packer_empty():
    """Test packer with no items."""
    packer = MessagesPacker(max_tokens=100)
    messages = packer.pack()

    assert messages == []


def test_messages_packer_method_chaining():
    """Test fluent API with method chaining."""
    messages = (
        MessagesPacker(max_tokens=100)
        .add("system", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)
        .add("user", role=ROLE_USER, priority=PRIORITY_QUERY)
        .pack()
    )

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_messages_packer_reset():
    """Test resetting the packer."""
    packer = MessagesPacker(max_tokens=100)

    packer.add("item1", role=ROLE_USER, priority=PRIORITY_HIGH)
    packer.add("item2", role=ROLE_USER, priority=PRIORITY_HIGH)

    # Reset
    packer.reset()

    messages = packer.pack()
    assert messages == []

    # Should be able to add new items after reset
    packer.add("new_item", role=ROLE_USER, priority=PRIORITY_HIGH)
    messages = packer.pack()
    assert len(messages) == 1
    assert messages[0]["content"] == "new_item"


def test_messages_packer_get_items():
    """Test getting item metadata."""
    packer = MessagesPacker(max_tokens=100)

    packer.add("first", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)
    packer.add("second", role=ROLE_USER, priority=PRIORITY_QUERY)

    items = packer.get_items()

    assert len(items) == 2
    assert items[0]["priority"] == PRIORITY_SYSTEM
    assert items[0]["role"] == ROLE_SYSTEM
    assert items[1]["priority"] == PRIORITY_QUERY
    assert items[1]["role"] == ROLE_USER


def test_messages_packer_add_messages_helper():
    """Test add_messages helper method."""
    packer = MessagesPacker(max_tokens=100)

    conversation = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there!"},
    ]

    packer.add_messages(conversation, priority=PRIORITY_HIGH)

    messages = packer.pack()

    assert len(messages) == 3
    assert messages[0]["content"] == "You are helpful."
    assert messages[1]["content"] == "Hello!"
    assert messages[2]["content"] == "Hi there!"


def test_messages_packer_rag_scenario():
    """Test realistic RAG scenario with semantic roles."""
    packer = MessagesPacker(max_tokens=200)

    # System prompt
    packer.add("You are a QA bot.", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)

    # Current user query
    packer.add("What are the features?", role=ROLE_QUERY, priority=PRIORITY_QUERY)

    # RAG documents as context with different priorities
    packer.add("Doc 1: Core features", role=ROLE_CONTEXT, priority=PRIORITY_HIGH)
    packer.add("Doc 2: Additional features", role=ROLE_CONTEXT, priority=PRIORITY_MEDIUM)
    packer.add("Doc 3: Historical context" * 10, role=ROLE_CONTEXT, priority=PRIORITY_LOW)

    messages = packer.pack()

    # Should prioritize system, query, and high-priority docs
    assert any(msg["content"] == "You are a QA bot." for msg in messages)
    assert any(msg["content"] == "What are the features?" for msg in messages)
    # RAG context should be mapped to "user" role
    assert any(msg["role"] == "user" and "Core features" in msg["content"] for msg in messages)


def test_messages_packer_conversation_history():
    """Test managing conversation history with priorities."""
    packer = MessagesPacker(max_tokens=100)

    # System prompt (high priority)
    packer.add("You are a chatbot.", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)

    # Old conversation (low priority, may be dropped)
    packer.add("Old user message", role=ROLE_USER, priority=PRIORITY_LOW)
    packer.add("Old bot response", role=ROLE_ASSISTANT, priority=PRIORITY_LOW)

    # Recent conversation (high priority)
    packer.add("Recent user message", role=ROLE_USER, priority=PRIORITY_QUERY)

    messages = packer.pack()

    # System and recent message should be included
    assert any(msg["content"] == "You are a chatbot." for msg in messages)
    assert any(msg["content"] == "Recent user message" for msg in messages)


def test_messages_packer_budget_enforcement():
    """Test that token budget is enforced."""
    packer = MessagesPacker(max_tokens=30)

    # Add many items
    for i in range(10):
        packer.add(f"Message {i}", role=ROLE_USER, priority=PRIORITY_MEDIUM)

    messages = packer.pack()

    # Should fit only some messages within budget
    assert len(messages) < 10
    assert len(messages) > 0


def test_messages_packer_unlimited_mode():
    """Test unlimited mode when max_tokens is None."""
    packer = MessagesPacker()  # No max_tokens

    # Add many items
    for i in range(20):
        packer.add(f"Message {i}", role=ROLE_USER, priority=PRIORITY_MEDIUM)

    packer.add("System prompt", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)
    packer.add("User query", role=ROLE_USER, priority=PRIORITY_QUERY)

    messages = packer.pack()

    # All items should be included
    assert len(messages) == 22
    assert packer.effective_max_tokens is None
    assert packer.raw_max_tokens is None


def test_messages_packer_smart_defaults():
    """Test smart priority defaults based on semantic roles."""
    packer = MessagesPacker(max_tokens=200)

    # Smart defaults: no priority parameter needed!
    packer.add("System instruction", role=ROLE_SYSTEM)  # Auto: PRIORITY_SYSTEM (0)
    packer.add("Current query", role=ROLE_QUERY)  # Auto: PRIORITY_QUERY (10)
    packer.add("RAG document", role=ROLE_CONTEXT)  # Auto: PRIORITY_HIGH (20)
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
    assert items[3]["priority"] == PRIORITY_LOW  # ROLE_USER
    assert items[4]["priority"] == PRIORITY_LOW  # ROLE_ASSISTANT
    assert items[5]["priority"] == PRIORITY_LOW  # history
    assert items[6]["priority"] == PRIORITY_LOW  # history

    messages = packer.pack()

    # System, query, and context should be included
    assert any(msg["content"] == "System instruction" for msg in messages)
    assert any(msg["content"] == "Current query" for msg in messages)
    assert any(msg["content"] == "RAG document" for msg in messages)


def test_messages_packer_unknown_role():
    """Test that unknown roles default to PRIORITY_MEDIUM."""
    packer = MessagesPacker(max_tokens=500)

    # Add item with unknown role (not one of the semantic constants)
    packer.add("Custom content", role="custom_role")

    # Check that priority defaults to PRIORITY_MEDIUM (30)
    items = packer.get_items()
    assert len(items) == 1
    assert items[0]["priority"] == PRIORITY_MEDIUM
    assert items[0]["role"] == "custom_role"

    messages = packer.pack()
    assert len(messages) == 1
    assert messages[0]["content"] == "Custom content"
    assert messages[0]["role"] == "custom_role"
