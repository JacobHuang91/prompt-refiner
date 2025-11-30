"""Tests for MessagesPacker (chat completion APIs)."""

from prompt_refiner import (
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_SYSTEM,
    PRIORITY_USER,
    MessagesPacker,
    NormalizeWhitespace,
    StripHTML,
)


def test_messages_packer_basic():
    """Test basic message packing."""
    packer = MessagesPacker(max_tokens=100)

    packer.add("System prompt", role="system", priority=PRIORITY_SYSTEM)
    packer.add("User query", role="user", priority=PRIORITY_USER)

    messages = packer.pack()

    assert isinstance(messages, list)
    assert len(messages) == 2
    assert messages[0] == {"role": "system", "content": "System prompt"}
    assert messages[1] == {"role": "user", "content": "User query"}


def test_messages_packer_priority_order():
    """Test that items are selected by priority."""
    packer = MessagesPacker(max_tokens=50)

    packer.add("low", role="user", priority=PRIORITY_LOW)
    packer.add("high", role="user", priority=PRIORITY_HIGH)
    packer.add("system", role="system", priority=PRIORITY_SYSTEM)

    messages = packer.pack()

    # System and high priority should be included
    assert any(msg["content"] == "system" for msg in messages)
    assert any(msg["content"] == "high" for msg in messages)


def test_messages_packer_insertion_order():
    """Test that insertion order is preserved."""
    packer = MessagesPacker(max_tokens=100)

    packer.add("first", role="user", priority=PRIORITY_MEDIUM)
    packer.add("second", role="user", priority=PRIORITY_MEDIUM)
    packer.add("third", role="user", priority=PRIORITY_MEDIUM)

    messages = packer.pack()

    # Should maintain insertion order
    assert messages[0]["content"] == "first"
    assert messages[1]["content"] == "second"
    assert messages[2]["content"] == "third"


def test_messages_packer_default_role():
    """Test that items without role default to 'user'."""
    packer = MessagesPacker(max_tokens=100)

    packer.add("No role specified", priority=PRIORITY_HIGH)

    messages = packer.pack()

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "No role specified"


def test_messages_packer_jit_refinement():
    """Test JIT refinement with operations."""
    packer = MessagesPacker(max_tokens=100)

    dirty_html = "<div><p>Clean this</p></div>"
    packer.add(dirty_html, role="user", priority=PRIORITY_HIGH, refine_with=StripHTML())

    messages = packer.pack()

    assert "<div>" not in messages[0]["content"]
    assert "Clean this" in messages[0]["content"]


def test_messages_packer_chained_operations():
    """Test chaining multiple operations in JIT refinement."""
    packer = MessagesPacker(max_tokens=100)

    messy = "<p>  Multiple   spaces  </p>"
    packer.add(
        messy,
        role="user",
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
        .add("system", role="system", priority=PRIORITY_SYSTEM)
        .add("user", role="user", priority=PRIORITY_USER)
        .pack()
    )

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_messages_packer_reset():
    """Test resetting the packer."""
    packer = MessagesPacker(max_tokens=100)

    packer.add("item1", role="user", priority=PRIORITY_HIGH)
    packer.add("item2", role="user", priority=PRIORITY_HIGH)

    # Reset
    packer.reset()

    messages = packer.pack()
    assert messages == []

    # Should be able to add new items after reset
    packer.add("new_item", role="user", priority=PRIORITY_HIGH)
    messages = packer.pack()
    assert len(messages) == 1
    assert messages[0]["content"] == "new_item"


def test_messages_packer_get_items():
    """Test getting item metadata."""
    packer = MessagesPacker(max_tokens=100)

    packer.add("first", role="system", priority=PRIORITY_SYSTEM)
    packer.add("second", role="user", priority=PRIORITY_USER)

    items = packer.get_items()

    assert len(items) == 2
    assert items[0]["priority"] == PRIORITY_SYSTEM
    assert items[0]["role"] == "system"
    assert items[1]["priority"] == PRIORITY_USER
    assert items[1]["role"] == "user"


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
    """Test realistic RAG scenario."""
    packer = MessagesPacker(max_tokens=200)

    # System prompt
    packer.add("You are a QA bot.", role="system", priority=PRIORITY_SYSTEM)

    # User query
    packer.add("What are the features?", role="user", priority=PRIORITY_USER)

    # RAG documents as system messages with different priorities
    packer.add("Doc 1: Core features", role="system", priority=PRIORITY_HIGH)
    packer.add("Doc 2: Additional features", role="system", priority=PRIORITY_MEDIUM)
    packer.add("Doc 3: Historical context" * 10, role="system", priority=PRIORITY_LOW)

    messages = packer.pack()

    # Should prioritize system, query, and high-priority docs
    assert any(msg["content"] == "You are a QA bot." for msg in messages)
    assert any(msg["content"] == "What are the features?" for msg in messages)


def test_messages_packer_conversation_history():
    """Test managing conversation history with priorities."""
    packer = MessagesPacker(max_tokens=100)

    # System prompt (high priority)
    packer.add("You are a chatbot.", role="system", priority=PRIORITY_SYSTEM)

    # Old conversation (low priority, may be dropped)
    packer.add("Old user message", role="user", priority=PRIORITY_LOW)
    packer.add("Old bot response", role="assistant", priority=PRIORITY_LOW)

    # Recent conversation (high priority)
    packer.add("Recent user message", role="user", priority=PRIORITY_USER)

    messages = packer.pack()

    # System and recent message should be included
    assert any(msg["content"] == "You are a chatbot." for msg in messages)
    assert any(msg["content"] == "Recent user message" for msg in messages)


def test_messages_packer_budget_enforcement():
    """Test that token budget is enforced."""
    packer = MessagesPacker(max_tokens=30)

    # Add many items
    for i in range(10):
        packer.add(f"Message {i}", role="user", priority=PRIORITY_MEDIUM)

    messages = packer.pack()

    # Should fit only some messages within budget
    assert len(messages) < 10
    assert len(messages) > 0
