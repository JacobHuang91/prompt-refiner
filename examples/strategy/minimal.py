"""Example: Using the Minimal Strategy for maximum quality preservation."""

from prompt_refiner.strategy import MinimalStrategy
from prompt_refiner.cleaner import FixUnicode

print("=" * 70)
print("MINIMAL STRATEGY EXAMPLE")
print("=" * 70)
print("\nUse case: Maximum quality, minimal risk")
print("Token reduction: ~4.3% | Quality: 98.7%")
print("Operations: StripHTML + NormalizeWhitespace + FixUnicode")
print("=" * 70)

# Sample data with HTML, excessive whitespace, and Unicode issues
raw_html = """
<div class="article">
    <h1>Understanding    Large Language Models</h1>
    <p>Large  Language   Models are   powerful AI systems.</p>
    <p>They can    process natural    language efficiently.</p>
    <p>Applications include    chatbots,   translation, and   more.</p>
    <p>The technology    continues to   evolve rapidly\u2014with impressive results.</p>
</div>
"""

# Create and use the minimal strategy
print("\nProcessing RAG document with Minimal Strategy...")
print("-" * 70)

# Strategy IS a pipeline - use directly, extend with .pipe()
strategy = MinimalStrategy().pipe(FixUnicode())
cleaned = strategy.run(raw_html)

input_len = len(raw_html)
output_len = len(cleaned)
reduction = ((input_len - output_len) / input_len * 100)

print("\nBefore (raw HTML with whitespace):")
print(f"  Length: {input_len} chars")

print("\nAfter (cleaned):")
print(f"  Length: {output_len} chars")
print(f"  Reduction: {reduction:.1f}%")

print("\nCleaned text:")
print(f"  {cleaned}")

print("\n" + "=" * 70)
print("WHEN TO USE MINIMAL STRATEGY:")
print("=" * 70)
print("✓ When quality is your top priority")
print("✓ When you need minimal risk of information loss")
print("✓ For mission-critical applications")
print("✓ When latency is critical (0.05ms per 1k tokens)")
print("=" * 70)
