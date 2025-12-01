# Complete Pipeline Example

A comprehensive example using all 5 modules together.

## Full Optimization Pipeline

```python
from prompt_refiner import (
    # Cleaner
    StripHTML, NormalizeWhitespace, FixUnicode,
    # Compressor
    Deduplicate, TruncateTokens,
    # Scrubber
    RedactPII,
    # Analyzer
    CountTokens
)

# Messy input with HTML, PII, duplicates
messy_input = """
<div>
    <p>Contact us at support@company.com or call 555-123-4567.</p>
    <p>Contact us at support@company.com or call 555-123-4567.</p>
    <p>We provide excellent service   with   lots   of   spaces.</p>
    <p>Our IP address is 192.168.1.1 for reference.</p>
</div>
"""

# Initialize counter
counter = CountTokens(original_text=messy_input)

# Build complete pipeline using pipe operator (recommended)
pipeline = (
    # Clean dirty data
    StripHTML()
    | FixUnicode()
    | NormalizeWhitespace()
    # Compress
    | Deduplicate(similarity_threshold=0.85)
    | TruncateTokens(max_tokens=50, strategy="head")
    # Secure
    | RedactPII(redact_types={"email", "phone", "ip"})
    # Analyze
    | counter
)

# Run pipeline
result = pipeline.run(messy_input)

print("Optimized result:")
print(result)
print("\nStatistics:")
print(counter.format_stats())
```

!!! tip "Alternative: Fluent API"
    You can also use `.pipe()` method chaining:
    ```python
    from prompt_refiner import Refiner

    pipeline = (
        Refiner()
        .pipe(StripHTML())
        .pipe(FixUnicode())
        .pipe(NormalizeWhitespace())
        # ... continue with other operations
    )
    ```

## Related

- [Pipeline Basics](../user-guide/pipelines.md)
- [All Modules Overview](../modules/overview.md)
