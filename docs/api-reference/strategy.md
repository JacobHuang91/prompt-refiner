# Strategy Module API Reference

The Strategy module provides benchmark-tested preset strategies for token optimization. Use these when you want quick savings without manually configuring individual operations.

## Overview

**Version 0.1.5+** introduces three preset strategies optimized for different use cases.
**Version 0.2.0** refactored strategies to inherit directly from Pipeline for a simpler API.

| Strategy | Token Reduction | Quality | Use Case |
|----------|----------------|---------|----------|
| **Minimal** | 4.3% | 98.7% | Maximum quality, minimal risk |
| **Standard** | 4.8% | 98.4% | RAG contexts with duplicates |
| **Aggressive** | 15% | 96.4% | Cost optimization, long contexts |

Strategies now inherit from `Pipeline`, so you can use them directly without calling `.create_refiner()`. They're fully extensible with `.pipe()`.

## MinimalStrategy

Basic cleaning with minimal token reduction, prioritizing quality preservation.

::: prompt_refiner.strategy.MinimalStrategy
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Operations

- `StripHTML()` - Remove HTML tags
- `NormalizeWhitespace()` - Collapse excessive whitespace

### Example

```python
from prompt_refiner.strategy import MinimalStrategy

# Use strategy directly (v0.2.0+)
strategy = MinimalStrategy()
cleaned = strategy.run("<div>  Your HTML content  </div>")
# Output: "Your HTML content"

# With Markdown conversion
strategy = MinimalStrategy(strip_html_to_markdown=True)
cleaned = strategy.run("<strong>bold</strong> text")
# Output: "**bold** text"

# Extend with additional operations
from prompt_refiner import RedactPII
extended = MinimalStrategy().pipe(RedactPII(redact_types={"email"}))
cleaned = extended.run(text)
```

## StandardStrategy

Enhanced cleaning with deduplication for RAG contexts with potential duplicates.

::: prompt_refiner.strategy.StandardStrategy
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Operations

- `StripHTML()` - Remove HTML tags
- `NormalizeWhitespace()` - Collapse excessive whitespace
- `Deduplicate()` - Remove similar content (sentence-level, 0.8 threshold)

### Example

```python
from prompt_refiner.strategy import StandardStrategy

# Use strategy directly (v0.2.0+)
strategy = StandardStrategy()
text = "<div>Hello world. Hello world. Goodbye world.</div>"
cleaned = strategy.run(text)
# Output: "Hello world. Goodbye world."  (duplicate removed)

# Custom similarity threshold
strategy = StandardStrategy(deduplicate_similarity_threshold=0.7)

# Alternative deduplication method
strategy = StandardStrategy(deduplicate_method="levenshtein")
```

## AggressiveStrategy

Maximum token reduction with deduplication and truncation for cost optimization.

::: prompt_refiner.strategy.AggressiveStrategy
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Operations

- `StripHTML()` - Remove HTML tags
- `NormalizeWhitespace()` - Collapse excessive whitespace
- `Deduplicate()` - Remove similar content (sentence-level, 0.7 threshold)
- `TruncateTokens()` - Limit to max_tokens (default: 150)

### Example

```python
from prompt_refiner.strategy import AggressiveStrategy

# Use strategy directly (v0.2.0+) with default truncate_max_tokens=150
strategy = AggressiveStrategy()
long_text = "word " * 100  # 100 words
cleaned = strategy.run(long_text)
# Output: Truncated to ~150 tokens with duplicates removed

# Custom max_tokens and truncation strategy
strategy = AggressiveStrategy(
    truncate_max_tokens=200,
    truncate_strategy="tail"  # Keep last 200 tokens
)

# More aggressive deduplication
strategy = AggressiveStrategy(
    truncate_max_tokens=100,
    deduplicate_similarity_threshold=0.6  # More aggressive duplicate detection
)
```

## Creating Custom Strategies

Custom strategies can be created by inheriting from `Pipeline`:

```python
from prompt_refiner import Pipeline, StripHTML, NormalizeWhitespace, RedactPII

class CustomStrategy(Pipeline):
    def __init__(self, redact_pii: bool = True):
        operations = [StripHTML(), NormalizeWhitespace()]
        if redact_pii:
            operations.append(RedactPII(redact_types={"email", "phone"}))
        super().__init__(operations)

# Use custom strategy directly
strategy = CustomStrategy(redact_pii=True)
cleaned = strategy.run(text)
```

## Usage Patterns

### Basic Usage (v0.2.0+)

```python
from prompt_refiner.strategy import MinimalStrategy, StandardStrategy, AggressiveStrategy

# Quick start with minimal - use directly
strategy = MinimalStrategy()
cleaned = strategy.run(text)

# Standard for RAG with duplicates
strategy = StandardStrategy()
cleaned = strategy.run(rag_context)

# Aggressive for cost optimization
strategy = AggressiveStrategy(truncate_max_tokens=200)
cleaned = strategy.run(long_context)
```

### Composition with Additional Operations

Strategies inherit from `Pipeline`, so you can extend them with `.pipe()`:

```python
from prompt_refiner.strategy import MinimalStrategy
from prompt_refiner import RedactPII, Deduplicate

# Start with minimal, add PII redaction
extended = MinimalStrategy().pipe(RedactPII(redact_types={"email"}))
cleaned = extended.run(text)

# Start with standard, add more aggressive deduplication
from prompt_refiner.strategy import StandardStrategy
extended = StandardStrategy().pipe(Deduplicate(similarity_threshold=0.6))
cleaned = extended.run(text)
```

### Using .process() Method

Strategies also support the `.process()` method from the Refiner interface:

```python
from prompt_refiner.strategy import MinimalStrategy

strategy = MinimalStrategy()
cleaned = strategy.process(text)  # Equivalent to strategy.run(text)
```

## Choosing a Strategy

### Minimal Strategy
✅ **Use when:**
- Quality is paramount
- Minimal risk tolerance
- Processing structured content
- First time optimizing prompts

❌ **Avoid when:**
- Budget constraints are tight
- Dealing with very long contexts
- Content has significant duplication

### Standard Strategy
✅ **Use when:**
- RAG contexts with potential duplicates
- Balanced quality and savings needed
- Processing web-scraped content
- General-purpose optimization

❌ **Avoid when:**
- Context is already clean and unique
- Maximum quality preservation required
- Very tight token budgets

### Aggressive Strategy
✅ **Use when:**
- Cost optimization is priority
- Token budgets are tight
- Processing very long contexts
- Quality tolerance is lenient

❌ **Avoid when:**
- Quality cannot be compromised
- Context is already short
- Truncation would remove critical info

## Configuration Reference (v0.2.0+)

### MinimalStrategy Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `strip_html` | `bool` | `True` | Whether to strip HTML tags |
| `strip_html_to_markdown` | `bool` | `False` | Convert HTML to Markdown instead of stripping |

### StandardStrategy Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `strip_html` | `bool` | `True` | Whether to strip HTML tags |
| `strip_html_to_markdown` | `bool` | `False` | Convert HTML to Markdown instead of stripping |
| `deduplicate_method` | `Literal["jaccard", "levenshtein"]` | `"jaccard"` | Deduplication algorithm |
| `deduplicate_similarity_threshold` | `float` | `0.8` | Threshold for deduplication (0.0-1.0) |
| `deduplicate_granularity` | `Literal["sentence", "paragraph"]` | `"sentence"` | Deduplication granularity |

### AggressiveStrategy Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `truncate_max_tokens` | `int` | `150` | Maximum tokens to keep |
| `truncate_strategy` | `Literal["head", "tail", "middle_out"]` | `"head"` | Which part of text to keep |
| `strip_html` | `bool` | `True` | Whether to strip HTML tags |
| `strip_html_to_markdown` | `bool` | `False` | Convert HTML to Markdown instead of stripping |
| `deduplicate_method` | `Literal["jaccard", "levenshtein"]` | `"jaccard"` | Deduplication algorithm |
| `deduplicate_similarity_threshold` | `float` | `0.7` | Threshold for deduplication (0.0-1.0) |
| `deduplicate_granularity` | `Literal["sentence", "paragraph"]` | `"sentence"` | Deduplication granularity |

## See Also

- [Examples](../examples/index.md) - Comprehensive examples
- [Benchmark Results](../benchmark.md) - Performance and quality metrics
- [Refiner API](refiner.md) - Pipeline composition
