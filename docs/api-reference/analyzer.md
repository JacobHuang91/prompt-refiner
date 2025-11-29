# Analyzer Module

The Analyzer module provides operations for measuring optimization impact and tracking metrics.

## CountTokens

Count tokens and provide before/after statistics to demonstrate optimization value.

::: prompt_refiner.analyzer.CountTokens
    options:
      show_source: true
      members_order: source
      heading_level: 3

### Token Counting Modes

!!! info "Two Counting Modes"
    CountTokens supports two modes:

    **Estimation Mode (Default)**
    - Zero dependencies, uses character-based approximation: **~1 token ≈ 4 characters**
    - Fast and lightweight, good for most use cases
    - Applies 10% safety buffer in ContextPacker to prevent overflow

    ```python
    counter = CountTokens()  # Estimation mode
    ```

    **Precise Mode (Optional)**
    - Requires `tiktoken`: `pip install llm-prompt-refiner[token]`
    - Exact token counting using OpenAI's tokenizer
    - No safety buffer needed, 100% capacity utilization
    - Opt-in by passing a `model` parameter

    ```python
    counter = CountTokens(model="gpt-4")  # Precise mode
    ```

### Examples

#### Basic Token Counting

```python
from prompt_refiner import CountTokens

counter = CountTokens()
counter.process("Hello World")

stats = counter.get_stats()
print(stats)
# {'tokens': 2}
```

#### Before/After Comparison

```python
from prompt_refiner import Refiner, StripHTML, NormalizeWhitespace, CountTokens

original_text = "<p>Hello    World   </p>"

# Initialize counter with original text
counter = CountTokens(original_text=original_text)

# Build pipeline with counter at the end
refiner = (
    Refiner()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
    .pipe(counter)
)

result = refiner.run(original_text)

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
from prompt_refiner import Refiner, StripHTML, NormalizeWhitespace, CountTokens

original_text = """Your long text here..."""
counter = CountTokens(original_text=original_text)

refiner = (
    Refiner()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
    .pipe(counter)
)

result = refiner.run(original_text)
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
from prompt_refiner import (
    Refiner, StripHTML, NormalizeWhitespace,
    Deduplicate, TruncateTokens, CountTokens
)

original_text = """Your messy input..."""
counter = CountTokens(original_text=original_text)

full_optimization = (
    Refiner()
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
from prompt_refiner import Refiner, TruncateTokens, Deduplicate, CountTokens

original_text = """Your text..."""

# Strategy A: Just truncate
counter_a = CountTokens(original_text=original_text)
strategy_a = (
    Refiner()
    .pipe(TruncateTokens(max_tokens=500))
    .pipe(counter_a)
)
strategy_a.run(original_text)

# Strategy B: Deduplicate then truncate
counter_b = CountTokens(original_text=original_text)
strategy_b = (
    Refiner()
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
from prompt_refiner import Refiner, StripHTML, CountTokens

logger = logging.getLogger(__name__)

def process_user_input(text):
    counter = CountTokens(original_text=text)

    refiner = (
        Refiner()
        .pipe(StripHTML())
        .pipe(counter)
    )

    result = refiner.run(text)
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
    refiner = (
        Refiner()
        .pipe(Operation1())
        .pipe(Operation2())
        .pipe(CountTokens(original_text=text))  # Last!
    )
    ```
