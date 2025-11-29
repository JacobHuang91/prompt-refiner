"""
Context Packer Demo - Context Budget Management

This example demonstrates how to use ContextPacker to manage LLM context budgets
by prioritizing and packing text items into a token limit.
"""

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


def basic_example():
    """Basic example: Pack items with different priorities."""
    print("=" * 80)
    print("Basic Example: Priority-based Packing")
    print("=" * 80)

    # Create a packer with a small budget to demonstrate selection
    packer = ContextPacker(max_tokens=200)

    # Add items with different priorities
    packer.add_item(
        "You are a helpful AI assistant specialized in Python programming.",
        priority=PRIORITY_SYSTEM,
    )

    packer.add_item(
        "How do I use the ContextPacker class?", priority=PRIORITY_USER
    )

    packer.add_item(
        "ContextPacker is a context budget manager that helps you fit text within token limits. "
        "It uses a greedy algorithm based on priorities.",
        priority=PRIORITY_HIGH,
    )

    packer.add_item(
        "Additional information: The library supports various operations like HTML stripping, "
        "whitespace normalization, and PII redaction. " * 5,
        priority=PRIORITY_LOW,
    )

    # Pack and display result
    result = packer.pack()
    print("\nPacked Result:")
    print("-" * 80)
    print(result)
    print("-" * 80)
    print()


def rag_example():
    """RAG example: Pack retrieval documents with query and system prompt."""
    print("=" * 80)
    print("RAG Example: Managing Retrieved Documents")
    print("=" * 80)

    packer = ContextPacker(max_tokens=300)

    # System prompt (highest priority)
    packer.add_item(
        "You are a helpful assistant. Answer questions based on the provided context.",
        priority=PRIORITY_SYSTEM,
    )

    # User query (must include)
    packer.add_item(
        "What are the main features of prompt-refiner?",
        priority=PRIORITY_USER,
    )

    # RAG Document 1: High relevance (with HTML)
    doc1_html = """
    <div class="doc">
        <h2>Key Features</h2>
        <p>prompt-refiner offers multiple modules:</p>
        <ul>
            <li>Cleaner: Remove HTML, normalize whitespace</li>
            <li>Compressor: Deduplicate and truncate</li>
            <li>Scrubber: Redact PII</li>
            <li>Packer: Manage token budgets</li>
        </ul>
    </div>
    """
    packer.add_item(
        doc1_html,
        priority=PRIORITY_HIGH,
        refine_with=StripHTML(),  # Clean HTML before counting tokens
    )

    # RAG Document 2: Medium relevance
    doc2 = (
        "Additional context: The library is lightweight with zero dependencies "
        "and focuses on performance."
    )
    packer.add_item(doc2, priority=PRIORITY_MEDIUM)

    # RAG Document 3: Lower relevance (might get dropped)
    doc3 = (
        "Historical information: The project was initially called prompt-groomer "
        "but was renamed to prompt-refiner. It supports Python 3.9+." * 3
    )
    packer.add_item(doc3, priority=PRIORITY_LOW)

    # Pack and display
    result = packer.pack(separator="\n\n---\n\n")
    print("\nPacked RAG Context:")
    print("-" * 80)
    print(result)
    print("-" * 80)
    print()


def jit_refinement_example():
    """Demonstrate just-in-time refinement of items."""
    print("=" * 80)
    print("JIT Refinement Example: Clean Before Packing")
    print("=" * 80)

    packer = ContextPacker(max_tokens=150)

    # Example 1: Strip HTML and normalize whitespace
    dirty_html = """
    <div>
        <h1>   Product    Information   </h1>
        <p>This    is    a    great    product    with    many    features.</p>
    </div>
    """
    packer.add_item(
        dirty_html,
        priority=PRIORITY_HIGH,
        refine_with=[StripHTML(), NormalizeWhitespace()],  # Chain multiple operations
    )

    # Example 2: Truncate a long document before adding
    long_text = "This is important information. " * 50
    packer.add_item(
        long_text,
        priority=PRIORITY_MEDIUM,
        refine_with=TruncateTokens(max_tokens=30),  # Truncate before packing
    )

    # Example 3: Clean user input
    user_input = "  What   is   the   price?  "
    packer.add_item(
        user_input,
        priority=PRIORITY_USER,
        refine_with=NormalizeWhitespace(),
    )

    result = packer.pack()
    print("\nPacked Result with JIT Refinement:")
    print("-" * 80)
    print(result)
    print("-" * 80)
    print()


def chaining_example():
    """Demonstrate method chaining API."""
    print("=" * 80)
    print("Method Chaining Example")
    print("=" * 80)

    # Fluent API allows chaining add_item calls
    result = (
        ContextPacker(max_tokens=200)
        .add_item("System prompt", priority=PRIORITY_SYSTEM)
        .add_item("User query", priority=PRIORITY_USER)
        .add_item("Context document", priority=PRIORITY_HIGH)
        .pack()
    )

    print("\nPacked Result (Chained):")
    print("-" * 80)
    print(result)
    print("-" * 80)
    print()


def inspection_example():
    """Demonstrate item inspection."""
    print("=" * 80)
    print("Inspection Example: View All Items")
    print("=" * 80)

    packer = ContextPacker(max_tokens=1000)

    packer.add_item("System prompt here", priority=PRIORITY_SYSTEM)
    packer.add_item("User asks a question", priority=PRIORITY_USER)
    packer.add_item("Important context", priority=PRIORITY_HIGH)
    packer.add_item("Less important info", priority=PRIORITY_LOW)

    # Inspect items before packing
    print("\nAdded Items:")
    print("-" * 80)
    items = packer.get_items()
    for i, item in enumerate(items):
        print(
            f"  [{item['insertion_index']}] Item {i+1}: "
            f"Priority={item['priority']}, Tokens={item['tokens']}"
        )
    print("-" * 80)
    print()

    # Pack
    result = packer.pack()
    print("\nPacked Result:")
    print(result)
    print()


def main():
    """Run all examples."""
    basic_example()
    rag_example()
    jit_refinement_example()
    chaining_example()
    inspection_example()

    print("=" * 80)
    print("Examples Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
