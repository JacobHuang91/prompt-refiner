"""
Token Tracking in Packers Demo

Shows how to use token tracking to measure the effectiveness of refinement
operations in MessagesPacker and TextPacker.
"""

from prompt_refiner import (
    AggressiveStrategy,
    MessagesPacker,
    MinimalStrategy,
    NormalizeWhitespace,
    StandardStrategy,
    StripHTML,
    TextFormat,
    TextPacker,
    character_based_counter,
    word_based_counter,
)


def example_1_messages_packer_basic():
    """Example 1: Basic token tracking with MessagesPacker."""
    print("=" * 80)
    print("Example 1: Basic Token Tracking with MessagesPacker")
    print("=" * 80)

    cleaner = StripHTML() | NormalizeWhitespace()

    # Enable tracking with opt-in parameter
    packer = MessagesPacker(track_tokens=True, token_counter=character_based_counter)

    packer.add("You are a helpful assistant.", role="system")
    packer.add("<div>RAG   document   1</div>", role="context", refine_with=cleaner)
    packer.add("<p>RAG   document   2</p>", role="context", refine_with=cleaner)
    packer.add("What's in the documents?", role="query")

    messages = packer.pack()

    # Access stats anytime
    stats = packer.token_stats
    print(f"\nOriginal tokens:  {stats['raw_tokens']}")
    print(f"Refined tokens:   {stats['refined_tokens']}")
    print(f"Tokens saved:     {stats['saved_tokens']}")
    print(f"Savings percent:  {stats['saving_percent']}")
    print(f"\nTotal messages: {len(messages)}")
    print()


def example_2_text_packer_formats():
    """Example 2: Token tracking with TextPacker and different formats."""
    print("=" * 80)
    print("Example 2: Token Tracking with TextPacker (Different Formats)")
    print("=" * 80)

    # Test with different text formats
    formats = [TextFormat.RAW, TextFormat.MARKDOWN, TextFormat.XML]

    print("\nNote: Text format affects pack() output, but NOT token savings.")
    print("Token tracking measures refinement effectiveness only.\n")

    for text_format in formats:
        packer = TextPacker(
            text_format=text_format,
            track_tokens=True,
            token_counter=character_based_counter
        )

        packer.add("<div>System instructions</div>", role="system", refine_with=StripHTML())
        packer.add("<p>Context   document</p>", role="context", refine_with=StripHTML())

        prompt = packer.pack()
        stats = packer.token_stats

        print(f"{text_format.value.upper()} format:")
        print(f"  Tokens saved: {stats['saved_tokens']} ({stats['saving_percent']})")
        print()


def example_3_comparing_strategies():
    """Example 3: Compare token savings across different strategies."""
    print("=" * 80)
    print("Example 3: Comparing Refinement Strategies")
    print("=" * 80)

    # Sample RAG documents with HTML and whitespace
    rag_documents = [
        "<div>This   is   a   RAG   document   with   HTML.</div>",
        "<p>Another   document   with   extra   whitespace.</p>",
        "<div>This   is   a   RAG   document   with   HTML.</div>",  # Duplicate
    ]

    strategies = {
        "MinimalStrategy": MinimalStrategy(),
        "StandardStrategy": StandardStrategy(),
        "AggressiveStrategy": AggressiveStrategy(),
    }

    print(f"\nProcessing {len(rag_documents)} RAG documents...\n")

    results = []
    for name, strategy in strategies.items():
        packer = MessagesPacker(track_tokens=True, token_counter=character_based_counter)

        for doc in rag_documents:
            packer.add(doc, role="context", refine_with=strategy)

        messages = packer.pack()
        stats = packer.token_stats

        results.append({
            "strategy": name,
            "raw": stats["raw_tokens"],
            "refined": stats["refined_tokens"],
            "saved": stats["saved_tokens"],
            "percent": stats["saving_percent"]
        })

    # Show comparison
    for r in results:
        print(f"{r['strategy']:20} | Saved: {r['saved']:3} tokens ({r['percent']})")

    print("\nNote: AggressiveStrategy includes deduplication, saving more tokens.")
    print()


def example_4_different_counters():
    """Example 4: Using different token counter functions."""
    print("=" * 80)
    print("Example 4: Different Token Counter Functions")
    print("=" * 80)

    text = "<div>Hello   World   from   RAG</div>"

    counters = {
        "Character-based (1 token ≈ 4 chars)": character_based_counter,
        "Word-based (1 token ≈ 1 word)": word_based_counter,
    }

    print(f'\nOriginal text: "{text}"\n')

    for name, counter in counters.items():
        packer = MessagesPacker(track_tokens=True, token_counter=counter)
        packer.add(text, role="context", refine_with=StripHTML() | NormalizeWhitespace())

        stats = packer.token_stats
        print(f"{name}:")
        print(f"  Original: {stats['raw_tokens']} tokens")
        print(f"  Refined:  {stats['refined_tokens']} tokens")
        print(f"  Saved:    {stats['saved_tokens']} tokens ({stats['saving_percent']})")
        print()


def example_5_real_world_workflow():
    """Example 5: Real-world RAG document cleaning workflow."""
    print("=" * 80)
    print("Example 5: Real-World RAG Document Cleaning Workflow")
    print("=" * 80)

    # Simulated RAG documents from web scraping
    documents = [
        """
        <div class="content">
            <h2>Product   Documentation</h2>
            <p>Our   product   provides   comprehensive   API   integration.</p>
            <script>analytics.track('view');</script>
        </div>
        """,
        """
        <article>
            <h3>User   Guide</h3>
            <p>Follow   these   steps   to   get   started   quickly.</p>
        </article>
        """,
        """
        <section>
            <h2>FAQ</h2>
            <p>Common   questions   and   answers   about   our   service.</p>
        </section>
        """,
    ]

    # Use StandardStrategy for context documents
    strategy = StandardStrategy()

    packer = MessagesPacker(track_tokens=True, token_counter=character_based_counter)
    packer.add("You are a helpful assistant.", role="system")

    for doc in documents:
        packer.add(doc, role="context", refine_with=strategy)

    packer.add("What does our product do?", role="query")

    messages = packer.pack()
    stats = packer.token_stats

    print(f"\nProcessed {len(documents)} RAG documents")
    print(f"\nToken Savings:")
    print(f"  Original tokens:  {stats['raw_tokens']}")
    print(f"  Refined tokens:   {stats['refined_tokens']}")
    print(f"  Tokens saved:     {stats['saved_tokens']}")
    print(f"  Savings:          {stats['saving_percent']}")
    print(f"\nTotal messages ready for API: {len(messages)}")
    print()


def example_6_without_tracking():
    """Example 6: Default behavior (tracking disabled)."""
    print("=" * 80)
    print("Example 6: Default Behavior (No Tracking)")
    print("=" * 80)

    # Default: tracking disabled, zero overhead
    packer = MessagesPacker()
    packer.add("Hello", role="user")
    messages = packer.pack()

    print("\nBy default, token tracking is disabled (zero overhead).")
    print("To enable tracking, pass track_tokens=True and token_counter.\n")

    # Attempting to access stats without tracking raises an error
    try:
        _ = packer.token_stats
    except ValueError as e:
        print(f"Error (expected): {e}")

    print()


def main():
    """Run all examples."""
    example_1_messages_packer_basic()
    example_2_text_packer_formats()
    example_3_comparing_strategies()
    example_4_different_counters()
    example_5_real_world_workflow()
    example_6_without_tracking()


if __name__ == "__main__":
    main()
