"""Example: Using the Standard Strategy for RAG contexts with duplicates."""

from prompt_refiner.strategy import StandardStrategy
from prompt_refiner.cleaner import FixUnicode

print("=" * 70)
print("STANDARD STRATEGY EXAMPLE")
print("=" * 70)
print("\nUse case: RAG contexts with potential duplicates")
print("Token reduction: ~4.8% | Quality: 98.4%")
print("Operations: StripHTML + NormalizeWhitespace + Deduplicate(0.8) + FixUnicode")
print("=" * 70)

# Sample RAG context with HTML, whitespace, duplicate content, and Unicode
raw_rag_context = """
<div class="search-results">
    <article id="doc1">
        <h2>Introduction to Machine Learning</h2>
        <p>Machine learning is a subset of artificial intelligence.</p>
        <p>Machine learning is a subset of artificial intelligence.</p>
        <p>It enables computers to learn from data without explicit programming.</p>
        <p>Applications include image recognition and natural language processing—especially in modern AI.</p>
    </article>
    <article id="doc2">
        <h2>ML Applications</h2>
        <p>It enables computers to learn from data without explicit programming.</p>
        <p>Machine learning has revolutionized many industries.</p>
    </article>
</div>
"""

# Create and use the standard strategy
print("\nProcessing RAG context with Standard Strategy...")
print("-" * 70)

# Strategy IS a pipeline - use directly, extend with .pipe()
strategy = StandardStrategy().pipe(FixUnicode())
cleaned = strategy.run(raw_rag_context)

input_len = len(raw_rag_context)
output_len = len(cleaned)
reduction = ((input_len - output_len) / input_len * 100)

print("\nBefore (with duplicates across documents):")
print(f"  Length: {input_len} chars")
print("  ~7 sentences (with duplicates)")

print("\nAfter (deduplication applied):")
print(f"  Length: {output_len} chars")
print(f"  Reduction: {reduction:.1f}%")

print("\nCleaned text:")
print(f"  {cleaned}")

print("\n" + "=" * 70)
print("WHEN TO USE STANDARD STRATEGY:")
print("=" * 70)
print("✓ RAG applications with multiple document sources")
print("✓ When documents may contain duplicate information")
print("✓ When processing web-scraped content with repetition")
print("✓ Better reduction than Minimal with minimal quality loss")
print("=" * 70)
