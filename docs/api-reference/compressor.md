# Compressor Module

The Compressor module provides operations for reducing text size through smart truncation and deduplication.

## TruncateTokens

Truncate text to a maximum number of tokens with intelligent sentence boundary detection.

::: prompt_refiner.compressor.TruncateTokens
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Truncation Strategies

- **`head`**: Keep the beginning of the text (default)
- **`tail`**: Keep the end of the text (useful for conversation history)
- **`middle_out`**: Keep beginning and end, remove middle

### Examples

```python
from prompt_refiner import TruncateTokens

# Keep first 100 tokens
truncator = TruncateTokens(max_tokens=100, strategy="head")
result = truncator.process(long_text)

# Keep last 100 tokens
truncator = TruncateTokens(max_tokens=100, strategy="tail")
result = truncator.process(long_text)

# Keep first and last 50 tokens, remove middle
truncator = TruncateTokens(max_tokens=100, strategy="middle_out")
result = truncator.process(long_text)

# Truncate at word boundaries (faster, less precise)
truncator = TruncateTokens(
    max_tokens=100,
    strategy="head",
    respect_sentence_boundary=False
)
result = truncator.process(long_text)
```

---

## Deduplicate

Remove duplicate or highly similar text chunks, useful for RAG contexts.

::: prompt_refiner.compressor.Deduplicate
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Similarity Methods

- **`jaccard`**: Jaccard similarity (word-based, faster) - default
- **`levenshtein`**: Levenshtein distance (character-based, more accurate)

### Granularity Levels

- **`paragraph`**: Deduplicate at paragraph level (split by `\n\n`) - default
- **`sentence`**: Deduplicate at sentence level (split by `.`, `!`, `?`)

### Examples

```python
from prompt_refiner import Deduplicate

# Basic deduplication (85% similarity threshold)
deduper = Deduplicate(similarity_threshold=0.85)
result = deduper.process(text_with_duplicates)

# More aggressive (70% similarity)
deduper = Deduplicate(similarity_threshold=0.70)
result = deduper.process(text_with_duplicates)

# Character-level similarity
deduper = Deduplicate(
    similarity_threshold=0.85,
    method="levenshtein"
)
result = deduper.process(text_with_duplicates)

# Sentence-level deduplication
deduper = Deduplicate(
    similarity_threshold=0.85,
    granularity="sentence"
)
result = deduper.process(text_with_duplicates)
```

## Common Use Cases

### RAG Context Optimization

```python
from prompt_refiner import Refiner, Deduplicate, TruncateTokens

rag_optimizer = (
    Refiner()
    .pipe(Deduplicate(similarity_threshold=0.85))  # Remove duplicates first
    .pipe(TruncateTokens(max_tokens=2000))        # Then fit in context window
)
```

### Conversation History Compression

```python
from prompt_refiner import Refiner, Deduplicate, TruncateTokens

conversation_compressor = (
    Refiner()
    .pipe(Deduplicate(granularity="sentence"))
    .pipe(TruncateTokens(max_tokens=1000, strategy="tail"))  # Keep recent messages
)
```

### Document Summarization Prep

```python
from prompt_refiner import Refiner, Deduplicate, TruncateTokens

summarization_prep = (
    Refiner()
    .pipe(Deduplicate(similarity_threshold=0.90))  # Remove near-duplicates
    .pipe(TruncateTokens(max_tokens=4000, strategy="middle_out"))  # Keep intro + conclusion
)
```
