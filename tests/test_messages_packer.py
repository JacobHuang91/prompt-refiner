"""Tests for MessagesPacker (chat completion APIs)."""

import pytest

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
    Pipeline,
    StripHTML,
)


def test_messages_packer_basic():
    """Test basic message packing."""
    packer = MessagesPacker()

    packer.add("System prompt", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)
    packer.add("User query", role=ROLE_USER, priority=PRIORITY_QUERY)

    messages = packer.pack()

    assert isinstance(messages, list)
    assert len(messages) == 2
    assert messages[0] == {"role": "system", "content": "System prompt"}
    assert messages[1] == {"role": "user", "content": "User query"}


def test_messages_packer_priority_order():
    """Test that items are selected by priority."""
    packer = MessagesPacker()

    packer.add("low", role=ROLE_USER, priority=PRIORITY_LOW)
    packer.add("high", role=ROLE_USER, priority=PRIORITY_HIGH)
    packer.add("system", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)

    messages = packer.pack()

    # System and high priority should be included
    assert any(msg["content"] == "system" for msg in messages)
    assert any(msg["content"] == "high" for msg in messages)


def test_messages_packer_insertion_order():
    """Test that insertion order is preserved."""
    packer = MessagesPacker()

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
    packer = MessagesPacker()

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
    packer = MessagesPacker()

    dirty_html = "<div><p>Clean this</p></div>"
    packer.add(dirty_html, role=ROLE_USER, priority=PRIORITY_HIGH, refine_with=StripHTML())

    messages = packer.pack()

    assert "<div>" not in messages[0]["content"]
    assert "Clean this" in messages[0]["content"]


def test_messages_packer_chained_operations():
    """Test chaining multiple operations in JIT refinement."""
    packer = MessagesPacker()

    messy = "<p>  Multiple   spaces  </p>"
    packer.add(
        messy,
        role=ROLE_USER,
        priority=PRIORITY_HIGH,
        refine_with=Pipeline([StripHTML(), NormalizeWhitespace()]),
    )

    messages = packer.pack()

    assert "<p>" not in messages[0]["content"]
    assert "  " not in messages[0]["content"]
    assert "Multiple spaces" in messages[0]["content"]


def test_messages_packer_empty():
    """Test packer with no items."""
    packer = MessagesPacker()
    messages = packer.pack()

    assert messages == []


def test_messages_packer_method_chaining():
    """Test fluent API with method chaining."""
    messages = (
        MessagesPacker()
        .add("system", role=ROLE_SYSTEM, priority=PRIORITY_SYSTEM)
        .add("user", role=ROLE_USER, priority=PRIORITY_QUERY)
        .pack()
    )

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_messages_packer_reset():
    """Test resetting the packer."""
    packer = MessagesPacker()

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
    packer = MessagesPacker()

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
    packer = MessagesPacker()

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
    packer = MessagesPacker()

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
    packer = MessagesPacker()

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
    """Test that all items are included (no budget limit)."""
    packer = MessagesPacker()

    # Add many items
    for i in range(10):
        packer.add(f"Message {i}", role=ROLE_USER, priority=PRIORITY_MEDIUM)

    messages = packer.pack()

    # All items should be included
    assert len(messages) == 10


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


def test_messages_packer_smart_defaults():
    """Test smart priority defaults based on semantic roles."""
    packer = MessagesPacker()

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
    packer = MessagesPacker()

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


# Tests for new constructor-based API


def test_constructor_with_system():
    """Test constructor with system parameter."""
    packer = MessagesPacker(system="You are a helpful assistant.")

    messages = packer.pack()

    assert len(messages) == 1
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are a helpful assistant."


def test_constructor_with_context():
    """Test constructor with context parameter."""
    packer = MessagesPacker(context=["Doc 1", "Doc 2", "Doc 3"])

    messages = packer.pack()

    assert len(messages) == 3
    assert all(msg["role"] == "user" for msg in messages)
    assert messages[0]["content"] == "Doc 1"
    assert messages[1]["content"] == "Doc 2"
    assert messages[2]["content"] == "Doc 3"


def test_constructor_with_history():
    """Test constructor with history parameter."""
    packer = MessagesPacker(
        history=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ],
    )

    messages = packer.pack()

    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hi there!"


def test_constructor_with_query():
    """Test constructor with query parameter."""
    packer = MessagesPacker(query="What's the weather?")

    messages = packer.pack()

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "What's the weather?"


def test_constructor_with_all_parameters():
    """Test constructor with all parameters."""
    packer = MessagesPacker(
        system="You are helpful.",
        context=["Doc 1", "Doc 2"],
        history=[{"role": "user", "content": "Hi"}],
        query="What's the weather?",
    )

    messages = packer.pack()

    # Should have system + 2 context + 1 history + 1 query = 5 messages
    assert len(messages) == 5
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are helpful."


def test_constructor_with_system_and_refiner():
    """Test constructor with system and refiner using tuple syntax."""
    packer = MessagesPacker(system=("You    are    helpful.", Pipeline([NormalizeWhitespace()])))

    messages = packer.pack()

    assert len(messages) == 1
    assert messages[0]["content"] == "You are helpful."


def test_constructor_with_context_and_refiner():
    """Test constructor with context and refiner using tuple syntax."""
    packer = MessagesPacker(context=(["<div>Doc 1</div>", "<p>Doc 2</p>"], Pipeline([StripHTML()])))

    messages = packer.pack()

    assert len(messages) == 2
    assert messages[0]["content"] == "Doc 1"
    assert messages[1]["content"] == "Doc 2"


def test_constructor_with_history_and_refiner():
    """Test constructor with history and refiner using tuple syntax."""
    packer = MessagesPacker(
        history=(
            [{"role": "user", "content": "Hello    world"}],
            Pipeline([NormalizeWhitespace()]),
        ),
    )

    messages = packer.pack()

    assert len(messages) == 1
    assert messages[0]["content"] == "Hello world"


def test_constructor_with_query_and_refiner():
    """Test constructor with query and refiner using tuple syntax."""
    packer = MessagesPacker(query=("<div>What's the weather?</div>", Pipeline([StripHTML()])))

    messages = packer.pack()

    assert len(messages) == 1
    assert messages[0]["content"] == "What's the weather?"


def test_extract_field_with_plain_value():
    """Test _extract_field with plain value."""
    content, refiner = MessagesPacker._extract_field("Hello")

    assert content == "Hello"
    assert refiner is None


def test_extract_field_with_tuple():
    """Test _extract_field with tuple."""
    content, refiner = MessagesPacker._extract_field(("Hello", Pipeline([StripHTML()])))

    assert content == "Hello"
    assert isinstance(refiner, Pipeline)
    assert len(refiner._refiners) == 1
    assert isinstance(refiner._refiners[0], StripHTML)


def test_extract_field_with_list():
    """Test _extract_field with list value."""
    content, refiner = MessagesPacker._extract_field(["Doc1", "Doc2"])

    assert content == ["Doc1", "Doc2"]
    assert refiner is None


def test_quick_pack_basic():
    """Test quick_pack class method."""
    messages = MessagesPacker.quick_pack(system="You are helpful.", query="What's the weather?")

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are helpful."
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "What's the weather?"


def test_quick_pack_with_refiners():
    """Test quick_pack with refiners."""
    messages = MessagesPacker.quick_pack(
        system="You are helpful.",
        context=(["<div>Doc 1</div>"], Pipeline([StripHTML()])),
        query="What's the weather?",
    )

    assert len(messages) == 3
    # Check that HTML was stripped from context
    assert any(msg["content"] == "Doc 1" for msg in messages)


def test_quick_pack_with_model():
    """Test quick_pack basic usage."""
    messages = MessagesPacker.quick_pack(system="You are helpful.", query="Test")

    assert len(messages) == 2


def test_constructor_and_add_method_combined():
    """Test that constructor parameters and add() method work together."""
    packer = MessagesPacker(system="You are helpful.")

    # Add more items using traditional API
    packer.add("Additional context", role=ROLE_CONTEXT)
    packer.add("What's up?", role=ROLE_QUERY)

    messages = packer.pack()

    assert len(messages) == 3
    assert messages[0]["content"] == "You are helpful."
    assert messages[1]["content"] == "Additional context"
    assert messages[2]["content"] == "What's up?"


class TestMessagePackerWithRefiner:
    def test_constructor_with_refiner_system(self):
        """Test MessagesPacker constructor accepts Refiner for system."""
        cleaner = StripHTML() | NormalizeWhitespace()
        packer = MessagesPacker(system=("<div>  System   prompt  </div>", cleaner))
        messages = packer.pack()

        assert len(messages) == 1
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "System prompt"

    def test_constructor_with_refiner_context(self):
        """Test MessagesPacker constructor accepts Refiner for context."""
        cleaner = StripHTML() | NormalizeWhitespace()
        packer = MessagesPacker(context=(["<div>  Doc   1  </div>", "<p>  Doc   2  </p>"], cleaner))
        messages = packer.pack()

        assert len(messages) == 2
        assert messages[0]["content"] == "Doc 1"
        assert messages[1]["content"] == "Doc 2"

    def test_constructor_with_refiner_query(self):
        """Test MessagesPacker constructor accepts Refiner for query."""
        cleaner = StripHTML() | NormalizeWhitespace()
        packer = MessagesPacker(query=("<div>  What's   the   weather?  </div>", cleaner))
        messages = packer.pack()

        assert len(messages) == 1
        assert messages[0]["content"] == "What's the weather?"

    def test_constructor_with_refiner_history(self):
        """Test MessagesPacker constructor accepts Refiner for history."""
        cleaner = StripHTML() | NormalizeWhitespace()
        packer = MessagesPacker(
            history=(
                [
                    {"role": "user", "content": "<div>  Hello  </div>"},
                    {"role": "assistant", "content": "<p>  Hi   there  </p>"},
                ],
                cleaner,
            )
        )
        messages = packer.pack()

        assert len(messages) == 2
        assert messages[0]["content"] == "Hello"
        assert messages[1]["content"] == "Hi there"

    def test_quick_pack_with_refiner(self):
        """Test quick_pack accepts Refiner."""
        cleaner = StripHTML() | NormalizeWhitespace()
        messages = MessagesPacker.quick_pack(
            system=("You are helpful.", cleaner),
            context=(["<div>Doc</div>"], cleaner),
            query=("<div>Query</div>", cleaner),
        )

        assert len(messages) == 3
        assert all("<" not in msg["content"] for msg in messages)
        assert all("  " not in msg["content"] for msg in messages)

    def test_add_with_refiner(self):
        """Test add() method accepts Refiner in refine_with."""
        cleaner = StripHTML() | NormalizeWhitespace()
        packer = MessagesPacker()
        packer.add(
            "<div>  Test   content  </div>",
            role=ROLE_SYSTEM,
            refine_with=cleaner,
        )
        messages = packer.pack()

        assert len(messages) == 1
        assert messages[0]["content"] == "Test content"


class TestRefinerReuse:
    def test_refiner_can_be_reused(self):
        """Test that same Refiner can be used in multiple places."""
        cleaner = StripHTML() | NormalizeWhitespace()

        packer = MessagesPacker(
            system=("<div>System</div>", cleaner),
            context=(["<div>Context</div>"], cleaner),
            query=("<div>Query</div>", cleaner),
        )
        messages = packer.pack()

        assert len(messages) == 3
        assert all("<" not in msg["content"] for msg in messages)

    def test_different_refiners_work_independently(self):
        """Test that different Refiners work independently."""
        html_stripper = StripHTML()
        whitespace_normalizer = NormalizeWhitespace()

        packer = MessagesPacker(
            system=("<div>System</div>", html_stripper),
            query=("Query   with   spaces", whitespace_normalizer),
        )
        messages = packer.pack()

        assert messages[0]["content"] == "System"  # HTML stripped
        assert messages[1]["content"] == "Query with spaces"  # Whitespace normalized


class TestDefaultStrategies:
    """Test automatic default strategy application."""

    def test_default_strategies_applied_automatically(self):
        """Test that default strategies are applied when no explicit refiner provided."""
        packer = MessagesPacker(
            system="<p>You are helpful.</p>   ",
            context=["<div>Document   1</div>"],
            query="<span>What's the   weather?</span>",
        )
        messages = packer.pack()

        # HTML should be stripped and whitespace normalized
        # Order: system, context, query (insertion order from constructor)
        assert messages[0]["content"] == "You are helpful."
        assert messages[1]["content"] == "Document 1"
        assert messages[2]["content"] == "What's the weather?"

    def test_raw_content_via_add_method(self):
        """Test that .add() method with refine_with=None provides raw content."""
        packer = MessagesPacker()
        packer.add("<p>You are helpful.</p>   ", role="system", refine_with=None)
        packer.add("<span>What's the   weather?</span>", role="query", refine_with=None)
        packer.add("<div>Document   1</div>", role="context", refine_with=None)
        messages = packer.pack()

        # Content should be unchanged
        assert messages[0]["content"] == "<p>You are helpful.</p>   "
        assert messages[1]["content"] == "<span>What's the   weather?</span>"
        assert messages[2]["content"] == "<div>Document   1</div>"

    def test_explicit_refiner_overrides_default(self):
        """Test that explicit refiner overrides default strategy."""
        custom_refiner = StripHTML()  # Only strip HTML, don't normalize whitespace

        packer = MessagesPacker(
            system=("<p>System   with   spaces</p>", custom_refiner),
            query="<span>Query   with   spaces</span>",  # Will use default
        )
        messages = packer.pack()

        # Custom refiner only strips HTML, keeps whitespace
        assert messages[0]["content"] == "System   with   spaces"
        # Default strategy strips HTML and normalizes whitespace
        assert messages[1]["content"] == "Query with spaces"

    def test_default_strategies_with_quick_pack(self):
        """Test default strategies work with quick_pack method."""
        messages = MessagesPacker.quick_pack(
            system="<p>System</p>",
            context=["<div>Context</div>"],
            query="<span>Query</span>",
        )

        # Order: system, context, query (insertion order from constructor)
        assert messages[0]["content"] == "System"
        assert messages[1]["content"] == "Context"
        assert messages[2]["content"] == "Query"

    def test_context_uses_standard_strategy(self):
        """Test that context uses StandardStrategy (includes deduplication)."""
        # Add duplicate context documents
        packer = MessagesPacker(
            context=[
                "<p>Document A. This is a test.</p>",
                "<p>Document B. This is a test.</p>",  # Very similar to A
            ]
        )
        messages = packer.pack()

        # StandardStrategy includes Deduplicate, so similar content may be reduced
        # At minimum, HTML should be stripped
        assert all("<" not in msg["content"] for msg in messages)

    def test_history_uses_standard_strategy(self):
        """Test that history uses StandardStrategy."""
        packer = MessagesPacker(
            history=[
                {"role": "user", "content": "<p>Hello   there</p>"},
                {"role": "assistant", "content": "<p>Hi   back</p>"},
            ]
        )
        messages = packer.pack()

        # StandardStrategy strips HTML and normalizes whitespace
        assert messages[0]["content"] == "Hello there"
        assert messages[1]["content"] == "Hi back"


class TestMessagesPackerTokenTracking:
    """Tests for token tracking in MessagesPacker."""

    def test_token_tracking_enabled(self):
        """Test basic token tracking with refinement."""

        def counter(text: str) -> int:
            return len(text)

        packer = MessagesPacker(track_tokens=True, token_counter=counter)
        packer.add("<div>Hello</div>", role="user", refine_with=StripHTML())

        stats = packer.token_stats
        assert stats["raw_tokens"] == 16  # "<div>Hello</div>"
        assert stats["refined_tokens"] == 5  # "Hello"
        assert stats["saved_tokens"] == 11
        assert "68.8%" in stats["saving_percent"]

    def test_token_tracking_disabled_by_default(self):
        """Test that tracking is disabled by default."""
        packer = MessagesPacker()
        packer.add("content", role="user")

        # Should raise error when accessing stats
        with pytest.raises(ValueError, match="Token tracking is not enabled"):
            _ = packer.token_stats

    def test_token_tracking_without_refinement(self):
        """Test tracking when no refinement applied (no savings)."""

        def counter(text: str) -> int:
            return len(text)

        packer = MessagesPacker(track_tokens=True, token_counter=counter)
        packer.add("Hello World", role="user")  # No refine_with

        stats = packer.token_stats
        assert stats["raw_tokens"] == 11
        assert stats["refined_tokens"] == 11
        assert stats["saved_tokens"] == 0
        assert stats["saving_percent"] == "0.0%"

    def test_token_tracking_multiple_items(self):
        """Test tracking aggregates across multiple items."""

        def counter(text: str) -> int:
            return len(text)

        packer = MessagesPacker(track_tokens=True, token_counter=counter)
        packer.add("<div>Doc 1</div>", role="context", refine_with=StripHTML())
        packer.add("<p>Doc 2</p>", role="context", refine_with=StripHTML())
        packer.add("Clean query", role="query")  # No refinement

        stats = packer.token_stats
        # <div>Doc 1</div> = 16, <p>Doc 2</p> = 12, "Clean query" = 11
        assert stats["raw_tokens"] == 39
        # "Doc 1" = 5, "Doc 2" = 5, "Clean query" = 11
        assert stats["refined_tokens"] == 21
        assert stats["saved_tokens"] == 18

    def test_token_tracking_reset(self):
        """Test that reset clears token counters."""

        def counter(text: str) -> int:
            return len(text)

        packer = MessagesPacker(track_tokens=True, token_counter=counter)
        packer.add("<div>Test</div>", role="user", refine_with=StripHTML())

        stats = packer.token_stats
        assert stats["raw_tokens"] > 0

        # Reset should clear counters
        packer.reset()
        stats = packer.token_stats
        assert stats["raw_tokens"] == 0
        assert stats["refined_tokens"] == 0
        assert stats["saved_tokens"] == 0

    def test_token_tracking_with_pipeline(self):
        """Test tracking with pipeline refinement."""

        def counter(text: str) -> int:
            return len(text)

        pipeline = StripHTML() | NormalizeWhitespace()
        packer = MessagesPacker(track_tokens=True, token_counter=counter)
        packer.add("<div>Hello   World</div>", role="user", refine_with=pipeline)

        stats = packer.token_stats
        assert stats["raw_tokens"] == 24  # Original
        assert stats["refined_tokens"] == 11  # "Hello World"
        assert stats["saved_tokens"] == 13

    def test_token_tracking_with_different_counters(self):
        """Test with character-based and word-based counters."""
        # Character-based (1 token = 4 chars)
        from prompt_refiner import character_based_counter, word_based_counter

        packer1 = MessagesPacker(track_tokens=True, token_counter=character_based_counter)
        packer1.add("<div>Hello World</div>", role="user", refine_with=StripHTML())

        stats1 = packer1.token_stats
        assert stats1["raw_tokens"] == 6  # 22 chars / 4 = 5.5 -> 6
        assert stats1["refined_tokens"] == 3  # 11 chars / 4 = 2.75 -> 3

        # Word-based
        packer2 = MessagesPacker(track_tokens=True, token_counter=word_based_counter)
        packer2.add("<div>Hello World</div>", role="user", refine_with=StripHTML())

        stats2 = packer2.token_stats
        assert stats2["raw_tokens"] == 2  # 2 words (HTML counted as words)
        assert stats2["refined_tokens"] == 2  # 2 words

    def test_token_tracking_error_without_counter(self):
        """Test that error is raised when track_tokens=True but no counter provided."""
        with pytest.raises(ValueError, match="token_counter is required"):
            MessagesPacker(track_tokens=True)

    def test_token_tracking_with_constructor_fields(self):
        """Test tracking when using constructor fields with default strategies."""

        def counter(text: str) -> int:
            return len(text)

        packer = MessagesPacker(
            track_tokens=True,
            token_counter=counter,
            system="<div>System</div>",
            context=["<p>Doc 1</p>", "<p>Doc 2</p>"],
            query="<span>Query</span>",
        )

        packer.pack()

        # Default strategies applied: MinimalStrategy for system/query, StandardStrategy for context
        stats = packer.token_stats
        assert stats["raw_tokens"] > 0
        assert stats["refined_tokens"] > 0
        assert stats["saved_tokens"] > 0
