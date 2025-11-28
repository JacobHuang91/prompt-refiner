# Deduplication Example

Remove duplicate content from RAG retrieval results.

## Scenario

Your RAG system retrieved multiple similar chunks that contain overlapping information.

## Example Code

```python
from prompt_refiner import Deduplicate

# RAG results with duplicates
rag_results = """
Python is a high-level programming language.

Python is a high level programming language.

Python supports multiple programming paradigms.
"""

pipeline = Deduplicate(similarity_threshold=0.85)
deduplicated = pipeline.run(rag_results)

print(deduplicated)
# Output: Only unique paragraphs remain
```

## Adjusting Sensitivity

```python
# More aggressive (70% similarity)
pipeline = Deduplicate(similarity_threshold=0.70)

# Sentence-level deduplication
pipeline = Deduplicate(granularity="sentence")
```

## Performance Considerations

When working with large RAG contexts, keep these performance tips in mind:

### Choosing a Similarity Method

```python
# Fast: Jaccard (word-based) - recommended for most use cases
pipeline = Deduplicate(method="jaccard")

# Precise but slower: Levenshtein (character-based)
# Only use when you need character-level accuracy
pipeline = Deduplicate(method="levenshtein")
```

### Scaling with Input Size

The deduplication algorithm compares each chunk against all previous chunks (O(n²)):

- **10-50 chunks**: Fast with either method (typical RAG use case)
- **50-200 chunks**: Use Jaccard for better performance
- **200+ chunks**: Use `granularity="paragraph"` to reduce chunk count

```python
# For large documents: use paragraph granularity
pipeline = Deduplicate(
    similarity_threshold=0.85,
    method="jaccard",
    granularity="paragraph"  # Fewer chunks = faster
)
```

## Full Example

See: [`examples/compressor/deduplication.py`](https://github.com/JacobHuang91/prompt-refiner/blob/main/examples/compressor/deduplication.py)

## Related

- [Deduplicate API Reference](../api-reference/compressor.md#deduplicate)
- [Compressor Module Guide](../modules/compressor.md)
