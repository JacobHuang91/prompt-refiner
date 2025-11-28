# Analyzer Module

Track optimization impact and demonstrate value with token counting and statistics.

## CountTokens Operation

Measure token usage before and after optimization.

### Basic Usage

```python
from prompt_refiner import Refiner, StripHTML, NormalizeWhitespace, CountTokens

original_text = "<p>Hello    World</p>"
counter = CountTokens(original_text=original_text)

refiner = (
    Refiner()
    .pipe(StripHTML())
    .pipe(NormalizeWhitespace())
    .pipe(counter)
)

result = refiner.run(original_text)
print(counter.format_stats())
# Original: 6 tokens
# Cleaned: 2 tokens
# Saved: 4 tokens (66.7%)
```

### Calculate Cost Savings

```python
stats = counter.get_stats()
cost_per_token = 0.03 / 1000  # GPT-4 pricing
savings = stats['saved'] * cost_per_token
print(f"Savings: ${savings:.4f} per request")
```

[Full API Reference →](../api-reference/analyzer.md){ .md-button }
[View Examples](../examples/token-analysis.md){ .md-button }
