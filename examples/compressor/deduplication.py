"""Example: Removing duplicate content (useful for RAG)."""

from prompt_refiner import Deduplicate, Refiner

# Simulated RAG retrieval with similar chunks
rag_results = """
Machine learning is a subset of artificial intelligence. It focuses on learning from data.

Machine learning is a subset of artificial intelligence. It emphasizes learning from data patterns.

Deep learning uses neural networks with multiple layers. This enables complex pattern recognition.

Machine learning is part of AI. It learns from data examples.

Neural networks are the foundation of deep learning. They process information in layers.
"""

print("=" * 60)
print("DEDUPLICATION EXAMPLE (for RAG)")
print("=" * 60)
print(f"\nOriginal RAG results:\n{rag_results}")

# Example 1: Deduplicate at sentence level with Jaccard similarity
print("\n" + "-" * 60)
print("Deduplication: Sentence level, Jaccard similarity (80%)")
print("-" * 60)
refiner = Pipeline().pipe(
    Deduplicate(similarity_threshold=0.8, method="jaccard", granularity="sentence")
)
deduped = refiner.run(rag_results)
print(f"Result:\n{deduped}")

# Example 2: More aggressive deduplication
print("\n" + "-" * 60)
print("Deduplication: Sentence level, Levenshtein distance (70%)")
print("-" * 60)
refiner_aggressive = Pipeline().pipe(
    Deduplicate(similarity_threshold=0.7, method="levenshtein", granularity="sentence")
)
deduped_aggressive = refiner_aggressive.run(rag_results)
print(f"Result:\n{deduped_aggressive}")

# Example 3: Paragraph level deduplication
paragraph_text = """First paragraph with some content.

First paragraph with some content.

Second paragraph with different content.

First paragraph with some content."""

print("\n" + "-" * 60)
print("Deduplication: Paragraph level")
print("-" * 60)
print(f"\nOriginal:\n{paragraph_text}")
refiner_para = Pipeline().pipe(
    Deduplicate(similarity_threshold=0.95, method="jaccard", granularity="paragraph")
)
deduped_para = refiner_para.run(paragraph_text)
print(f"\nResult:\n{deduped_para}")
