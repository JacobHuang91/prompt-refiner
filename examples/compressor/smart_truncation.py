"""Example: Smart text truncation with sentence boundaries."""

from prompt_refiner import Pipeline, TruncateTokens

long_text = """
The quick brown fox jumps over the lazy dog. This is the first sentence about foxes.
Machine learning is transforming the world. AI systems are becoming more capable every day.
Natural language processing enables computers to understand human language. This technology is revolutionary.
Deep learning models require large amounts of data. Training these models can be computationally expensive.
The future of AI looks very promising. Many applications are being developed across industries.
"""

print("=" * 60)
print("SMART TRUNCATION EXAMPLE")
print("=" * 60)
print(f"\nOriginal text ({len(long_text.split())} words):\n{long_text}")

# Example 1: Keep the beginning (head strategy)
print("\n" + "-" * 60)
print("Strategy: HEAD (keep beginning)")
print("-" * 60)
refiner_head = Pipeline().pipe(TruncateTokens(max_tokens=20, strategy="head"))
truncated_head = refiner_head.run(long_text)
print(f"Result: {truncated_head}")

# Example 2: Keep the end (tail strategy - useful for conversation history)
print("\n" + "-" * 60)
print("Strategy: TAIL (keep end)")
print("-" * 60)
refiner_tail = Pipeline().pipe(TruncateTokens(max_tokens=20, strategy="tail"))
truncated_tail = refiner_tail.run(long_text)
print(f"Result: {truncated_tail}")

# Example 3: Keep beginning and end (middle_out strategy)
print("\n" + "-" * 60)
print("Strategy: MIDDLE_OUT (keep both ends)")
print("-" * 60)
refiner_middle = Pipeline().pipe(TruncateTokens(max_tokens=30, strategy="middle_out"))
truncated_middle = refiner_middle.run(long_text)
print(f"Result: {truncated_middle}")

# Example 4: Sentence boundary respect
print("\n" + "-" * 60)
print("With sentence boundary detection")
print("-" * 60)
refiner_sentence = Pipeline().pipe(
    TruncateTokens(max_tokens=25, strategy="head", respect_sentence_boundary=True)
)
truncated_sentence = refiner_sentence.run(long_text)
print(f"Result: {truncated_sentence}")
print("\nNotice how it keeps complete sentences!")
