# Analyzer Module

The Analyzer module provides operations for measuring optimization impact and tracking metrics.

## CountTokens

Count tokens and provide before/after statistics to demonstrate optimization value.

::: prompt_groomer.analyzer.CountTokens
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Token Estimation

!!! info "Token Estimation Method"
    CountTokens uses a simple approximation: **~1 token per word**. This is fast but not as accurate as actual tokenizer libraries like `tiktoken`.

    For more accurate token counting in production, consider:

    - Using `tiktoken` for OpenAI models
    - Using model-specific tokenizers
    - Treating this as an approximation for optimization tracking

### Examples

#### Basic Token Counting

```python
from prompt_groomer import CountTokens

counter = CountTokens()
counter.process("Hello World")

stats = counter.get_stats()
print(stats)
# {'tokens': 2}
```

#### Before/After Comparison

```python
from prompt_groomer import Groomer, StripHTML, NormalizeWhitespace, CountTokens

original_text = "<p>Hello    World   </p>"

# Initialize counter with original text
counter = CountTokens(original_text=original_text)

# Build pipeline with counter at the end
groomer = (
    Groomer()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
    .pipe(counter)
)

result = groomer.run(original_text)

# Get statistics
stats = counter.get_stats()
print(stats)
# {
#   'original': 6,
#   'cleaned': 2,
#   'saved': 4,
#   'saving_percent': '66.7%'
# }

# Formatted output
print(counter.format_stats())
# Original: 6 tokens
# Cleaned: 2 tokens
# Saved: 4 tokens (66.7%)
```

#### Cost Calculation Example

```python
from prompt_groomer import Groomer, StripHTML, NormalizeWhitespace, CountTokens

original_text = """Your long text here..."""
counter = CountTokens(original_text=original_text)

groomer = (
    Groomer()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
    .pipe(counter)
)

result = groomer.run(original_text)
stats = counter.get_stats()

# Calculate cost savings
# Example: GPT-4 pricing - $0.03 per 1K tokens
cost_per_token = 0.03 / 1000
original_cost = stats['original'] * cost_per_token
cleaned_cost = stats['cleaned'] * cost_per_token
savings = original_cost - cleaned_cost

print(f"Original cost: ${original_cost:.4f}")
print(f"Cleaned cost: ${cleaned_cost:.4f}")
print(f"Savings: ${savings:.4f} per request")
```

## Common Use Cases

### ROI Demonstration

```python
from prompt_groomer import (
    Groomer, StripHTML, NormalizeWhitespace,
    Deduplicate, TruncateTokens, CountTokens
)

original_text = """Your messy input..."""
counter = CountTokens(original_text=original_text)

full_optimization = (
    Groomer()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
    .pipe(Deduplicate())
    .pipe(TruncateTokens(max_tokens=1000))
    .pipe(counter)
)

result = full_optimization.run(original_text)
print(counter.format_stats())
```

### A/B Testing Different Strategies

```python
from prompt_groomer import Groomer, TruncateTokens, Deduplicate, CountTokens

original_text = """Your text..."""

# Strategy A: Just truncate
counter_a = CountTokens(original_text=original_text)
strategy_a = (
    Groomer()
    .pipe(TruncateTokens(max_tokens=500))
    .pipe(counter_a)
)
strategy_a.run(original_text)

# Strategy B: Deduplicate then truncate
counter_b = CountTokens(original_text=original_text)
strategy_b = (
    Groomer()
    .pipe(Deduplicate())
    .pipe(TruncateTokens(max_tokens=500))
    .pipe(counter_b)
)
strategy_b.run(original_text)

print("Strategy A:", counter_a.format_stats())
print("Strategy B:", counter_b.format_stats())
```

### Monitoring and Logging

```python
import logging
from prompt_groomer import Groomer, StripHTML, CountTokens

logger = logging.getLogger(__name__)

def process_user_input(text):
    counter = CountTokens(original_text=text)

    groomer = (
        Groomer()
        .pipe(StripHTML())
        .pipe(counter)
    )

    result = groomer.run(text)
    stats = counter.get_stats()

    # Log optimization impact
    logger.info(
        f"Processed input: "
        f"original={stats['original']} tokens, "
        f"cleaned={stats['cleaned']} tokens, "
        f"saved={stats['saved']} tokens ({stats['saving_percent']})"
    )

    return result
```

## Tips

!!! tip "Always Use with Original Text"
    To see before/after comparisons, always initialize `CountTokens` with the original text:

    ```python
    counter = CountTokens(original_text=original_text)
    ```

    Otherwise, you'll only get the final token count.

!!! tip "Place at End of Pipeline"
    For accurate "after" measurements, place `CountTokens` as the last operation in your pipeline:

    ```python
    groomer = (
        Groomer()
        .pipe(Operation1())
        .pipe(Operation2())
        .pipe(CountTokens(original_text=text))  # Last!
    )
    ```
