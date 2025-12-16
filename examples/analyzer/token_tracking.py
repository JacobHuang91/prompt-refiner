"""
Token Tracking Demo

Shows how to use TokenTracker to measure token savings from refiners and pipelines.
"""

from prompt_refiner import (
    AggressiveStrategy,
    MinimalStrategy,
    NormalizeWhitespace,
    StandardStrategy,
    StripHTML,
    TokenTracker,
    character_based_counter,
    create_tiktoken_counter,
    word_based_counter,
)


def example_1_basic_usage():
    """Example 1: Basic usage with custom counter."""
    print("=" * 80)
    print("Example 1: Basic Token Tracking")
    print("=" * 80)

    def my_counter(text: str) -> int:
        """Simple character-based counter."""
        return len(text) // 4

    pipeline = StripHTML() | NormalizeWhitespace()
    dirty_html = "<div><p>Hello   World</p></div>"

    with TokenTracker(pipeline, my_counter) as tracker:
        clean_text = tracker.process(dirty_html)

    print(f"\nOriginal: {tracker.original_text}")
    print(f"Result:   {clean_text}")
    print(f"\nStats:")
    print(f"  Original: {tracker.stats['original_tokens']} tokens")
    print(f"  Refined:  {tracker.stats['refined_tokens']} tokens")
    print(f"  Saved:    {tracker.stats['saved_tokens']} tokens ({tracker.stats['saving_percent']})")
    print()


def example_2_built_in_counters():
    """Example 2: Using built-in counter functions."""
    print("=" * 80)
    print("Example 2: Built-in Counter Functions")
    print("=" * 80)

    text = "<div>This is a test   document   with HTML and   extra whitespace.</div>"
    pipeline = StripHTML() | NormalizeWhitespace()

    # Test with character-based counter
    print("\nCharacter-based counter:")
    with TokenTracker(pipeline, character_based_counter) as tracker:
        result = tracker.process(text)
        print(f"  Saved: {tracker.stats['saved_tokens']} tokens ({tracker.stats['saving_percent']})")

    # Test with word-based counter
    print("\nWord-based counter:")
    with TokenTracker(pipeline, word_based_counter) as tracker:
        result = tracker.process(text)
        print(f"  Saved: {tracker.stats['saved_tokens']} tokens ({tracker.stats['saving_percent']})")

    print()


def example_3_tiktoken_counter():
    """Example 3: Using tiktoken for precise counting (optional)."""
    print("=" * 80)
    print("Example 3: Precise Counting with Tiktoken")
    print("=" * 80)

    try:
        counter = create_tiktoken_counter(model="gpt-4")

        text = "<div>This is a RAG document with HTML tags and formatting.</div>"
        pipeline = StripHTML() | NormalizeWhitespace()

        with TokenTracker(pipeline, counter) as tracker:
            result = tracker.process(text)

        print("\nUsing tiktoken (precise counting):")
        print(f"  Original: {tracker.stats['original_tokens']} tokens")
        print(f"  Refined:  {tracker.stats['refined_tokens']} tokens")
        print(f"  Saved:    {tracker.stats['saved_tokens']} tokens ({tracker.stats['saving_percent']})")
        print()

    except ImportError:
        print("\nTiktoken not installed.")
        print("Install with: pip install llm-prompt-refiner[token]")
        print()


def example_4_comparing_strategies():
    """Example 4: Compare token savings across different strategies."""
    print("=" * 80)
    print("Example 4: Comparing Strategies")
    print("=" * 80)

    text = """
    <div class="article">
        <h1>RAG Document with HTML</h1>
        <p>This is a sample   document   with   extra   whitespace.</p>
        <p>This is a sample   document   with   extra   whitespace.</p>
        <p>Another paragraph with different content.</p>
        <script>console.log('tracking');</script>
    </div>
    """

    strategies = {
        "MinimalStrategy": MinimalStrategy(),
        "StandardStrategy": StandardStrategy(),
        "AggressiveStrategy": AggressiveStrategy(),
    }

    print(f"\nOriginal text: {character_based_counter(text)} tokens (estimated)")
    print("\nStrategy comparison:")

    for name, strategy in strategies.items():
        with TokenTracker(strategy, character_based_counter) as tracker:
            result = tracker.process(text)

            print(f"\n  {name}:")
            print(f"    Refined:  {tracker.stats['refined_tokens']} tokens")
            print(f"    Saved:    {tracker.stats['saved_tokens']} tokens ({tracker.stats['saving_percent']})")

    print()


def example_5_rag_workflow():
    """Example 5: Real-world RAG document cleaning workflow."""
    print("=" * 80)
    print("Example 5: RAG Document Cleaning Workflow")
    print("=" * 80)

    # Simulated RAG documents from web scraping
    documents = [
        """
        <div class="content">
            <h2>Product   Documentation</h2>
            <p>Our   product   provides   comprehensive   API   integration.</p>
            <script>analytics.track('view');</script>
            <style>.ad { display: none; }</style>
        </div>
        """,
        """
        <article>
            <h3>User   Guide</h3>
            <p>Follow   these   steps   to   get   started   quickly.</p>
            <nav><a href="#">Home</a></nav>
        </article>
        """,
        """
        <section>
            <h2>FAQ</h2>
            <p>Common   questions   and   answers   about   our   service.</p>
            <footer>Copyright 2024</footer>
        </section>
        """,
    ]

    pipeline = StripHTML() | NormalizeWhitespace()

    print("\nProcessing RAG documents:")
    total_saved = 0

    for i, doc in enumerate(documents, 1):
        with TokenTracker(pipeline, character_based_counter) as tracker:
            clean_doc = tracker.process(doc)

            print(f"\n  Document {i}:")
            print(f"    Before: {tracker.stats['original_tokens']} tokens")
            print(f"    After:  {tracker.stats['refined_tokens']} tokens")
            print(f"    Saved:  {tracker.stats['saved_tokens']} tokens")

            total_saved += tracker.stats["saved_tokens"]

    print(f"\nTotal tokens saved across all documents: {total_saved}")
    print()


def main():
    """Run all examples."""
    example_1_basic_usage()
    example_2_built_in_counters()
    example_3_tiktoken_counter()
    example_4_comparing_strategies()
    example_5_rag_workflow()


if __name__ == "__main__":
    main()
