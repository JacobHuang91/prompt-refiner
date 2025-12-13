"""Example: Using the Aggressive Strategy for maximum token reduction."""

from prompt_refiner.strategy import AggressiveStrategy
from prompt_refiner.cleaner import FixUnicode

print("=" * 70)
print("AGGRESSIVE STRATEGY EXAMPLE")
print("=" * 70)
print("\nUse case: Cost optimization, long contexts")
print("Token reduction: ~15% (up to 74% on very long contexts)")
print("Quality: 96.4%")
print("Operations: StripHTML + NormalizeWhitespace + Deduplicate(0.7) + Truncate + FixUnicode")
print("=" * 70)

# Sample long RAG context with duplicates, excessive content, and Unicode
long_rag_context = """
<div class="documentation">
    <h1>Comprehensive Guide to Machine Learning</h1>

    <section id="intro">
        <p>Machine learning is a subset of artificial intelligence.</p>
        <p>Machine learning is a subset of artificial intelligence.</p>
        <p>It enables systems to learn and improve from experience automatically—without explicit programming.</p>
        <p>It enables systems to learn and improve from experience automatically—without explicit programming.</p>
    </section>

    <section id="types">
        <h2>Types of Machine Learning</h2>
        <p>Supervised learning uses labeled training data to learn patterns.</p>
        <p>Unsupervised learning finds patterns in unlabeled data.</p>
        <p>Reinforcement learning trains agents through rewards.</p>
        <p>Semi-supervised learning combines labeled and unlabeled data.</p>
    </section>

    <section id="applications">
        <h2>Real-World Applications</h2>
        <p>Computer vision enables machines to interpret visual information.</p>
        <p>Natural language processing helps computers understand language.</p>
        <p>Recommendation systems suggest products based on preferences.</p>
        <p>Autonomous vehicles use ML for navigation and decision making—revolutionizing transportation.</p>
    </section>
</div>
"""

# Create and use the aggressive strategy
print("\nProcessing long RAG context with Aggressive Strategy...")
print("-" * 70)

# Strategy IS a pipeline - use directly, extend with .pipe()
strategy = AggressiveStrategy().pipe(FixUnicode())
cleaned = strategy.run(long_rag_context)

input_len = len(long_rag_context)
output_len = len(cleaned)
reduction = ((input_len - output_len) / input_len * 100)

print("\nBefore (long context with duplicates):")
print(f"  Length: {input_len} chars (~{len(long_rag_context.split())} words)")
print("  ~14 sentences")

print("\nAfter (deduplication + truncation):")
print(f"  Length: {output_len} chars (~{len(cleaned.split())} words)")
print(f"  Reduction: {reduction:.1f}%")

print("\nCleaned text:")
print(f"  {cleaned}")

# Show cost savings
print("\n" + "=" * 70)
print("COST SAVINGS EXAMPLE:")
print("=" * 70)
monthly_queries = 1000
avg_tokens = 2000
cost_per_1k = 0.0015  # GPT-4 input cost

original_cost = (monthly_queries * avg_tokens / 1000) * cost_per_1k
reduced_cost = (monthly_queries * int(avg_tokens * 0.85) / 1000) * cost_per_1k
savings = original_cost - reduced_cost

print(f"Monthly queries: {monthly_queries:,}")
print(f"Avg context: {avg_tokens:,} tokens")
print(f"Original cost: ${original_cost:.2f}/month")
print(f"With Aggressive: ${reduced_cost:.2f}/month")
print(f"Savings: ${savings:.2f}/month (15%)")

print("\n" + "=" * 70)
print("WHEN TO USE AGGRESSIVE STRATEGY:")
print("=" * 70)
print("✓ Long RAG contexts where cost is a concern")
print("✓ When slight quality loss is acceptable (96.4% quality)")
print("✓ Processing large volumes (1M+ tokens/month)")
print("✓ When context exceeds model token limits")
print("\nWHEN NOT TO USE:")
print("✗ Mission-critical applications")
print("✗ Legal or medical documents")
print("✗ When every detail matters")
print("=" * 70)
