# Compressor Module

Reduce text size while preserving meaning through smart truncation and deduplication.

## Operations

### TruncateTokens

Smart text truncation respecting sentence boundaries.

```python
from prompt_groomer import TruncateTokens

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
from prompt_groomer import Deduplicate

# Remove paragraphs with 85% similarity
deduper = Deduplicate(similarity_threshold=0.85)

# Sentence-level deduplication
deduper = Deduplicate(granularity="sentence")
```

[Full API Reference →](../api-reference/compressor.md#deduplicate){ .md-button }

## Common Use Cases

### RAG Context Optimization

```python
from prompt_groomer import Groomer, Deduplicate, TruncateTokens

rag_optimizer = (
    Groomer()
    .pipe(Deduplicate())
    .pipe(TruncateTokens(max_tokens=2000))
)
```

[View Examples](../examples/deduplication.md){ .md-button }
