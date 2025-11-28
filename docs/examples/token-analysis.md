# Token Analysis Example

Measure optimization impact and calculate cost savings.

## Scenario

You want to demonstrate the value of prompt optimization.

## Example Code

```python
from prompt_refiner import StripHTML, NormalizeWhitespace, CountTokens

original_text = "<p>Hello    World   from   HTML  </p>"

# Initialize counter with original text
counter = CountTokens(original_text=original_text)

pipeline = (
    StripHTML()
    | NormalizeWhitespace()
    | counter
)

result = pipeline.run(original_text)

# Show statistics
print(counter.format_stats())
# Output:
# Original: 10 tokens
# Cleaned: 4 tokens
# Saved: 6 tokens (60.0%)
```

## Calculate Cost Savings

```python
stats = counter.get_stats()

# GPT-4 pricing: $0.03 per 1K tokens
cost_per_token = 0.03 / 1000

original_cost = stats['original'] * cost_per_token
cleaned_cost = stats['cleaned'] * cost_per_token
savings_per_request = original_cost - cleaned_cost

print(f"Savings: ${savings_per_request:.4f} per request")

# Project annual savings
requests_per_day = 10000
annual_savings = savings_per_request * requests_per_day * 365
print(f"Annual savings: ${annual_savings:.2f}")
```

## Full Example

See: [`examples/analyzer/token_counting.py`](https://github.com/JacobHuang91/prompt-refiner/blob/main/examples/analyzer/token_counting.py)

## Related

- [CountTokens API Reference](../api-reference/analyzer.md)
- [Analyzer Module Guide](../modules/analyzer.md)
