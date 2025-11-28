# Compressor Module

Reduce text size while preserving meaning through smart truncation and deduplication.

## Operations

### TruncateTokens

Smart text truncation respecting sentence boundaries.

```python
from prompt_refiner import TruncateTokens

# Keep first 100 tokens
truncator = TruncateTokens(max_tokens=100, strategy="head")

# Keep last 100 tokens (for conversation history)
truncator = TruncateTokens(max_tokens=100, strategy="tail")

# Keep beginning and end, remove middle
truncator = TruncateTokens(max_tokens=100, strategy="middle_out")
```

[Full API Reference →](../api-reference/compressor.md#truncatetokens){ .md-button }

### Deduplicate

Remove duplicate or similar content chunks.

```python
from prompt_refiner import Deduplicate

# Remove paragraphs with 85% similarity
deduper = Deduplicate(similarity_threshold=0.85)

# Sentence-level deduplication
deduper = Deduplicate(granularity="sentence")
```

**Performance Considerations:**

- **Method Choice**: Use `jaccard` (default) for most cases - it's fast and works well with typical prompts. Only use `levenshtein` when you need character-level precision.
- **Complexity**: Deduplication uses O(n²) comparisons where n is the number of chunks. For 50 chunks, this is ~1,225 comparisons.
- **Large Inputs**: For 200+ chunks, use `granularity="paragraph"` to reduce chunk count and speed up processing.
- **Jaccard**: O(m) per comparison - fast even with long chunks
- **Levenshtein**: O(m₁ × m₂) per comparison - can be slow with chunks over 1000 characters

[Full API Reference →](../api-reference/compressor.md#deduplicate){ .md-button }

## Common Use Cases

### RAG Context Optimization

```python
from prompt_refiner import Deduplicate, TruncateTokens

rag_optimizer = (
    Deduplicate()
    | TruncateTokens(max_tokens=2000)
)
```

[View Examples](../examples/deduplication.md){ .md-button }
