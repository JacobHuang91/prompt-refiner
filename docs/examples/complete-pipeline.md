# Complete Pipeline Example

A comprehensive example using all 4 modules together.

## Full Optimization Pipeline

```python
from prompt_groomer import (
    Groomer,
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

# Build complete pipeline
groomer = (
    Groomer()
    # Clean dirty data
    .pipe(StripHTML())
    .pipe(FixUnicode())
    .pipe(NormalizeWhitespace())
    # Compress
    .pipe(Deduplicate(similarity_threshold=0.85))
    .pipe(TruncateTokens(max_tokens=50, strategy="head"))
    # Secure
    .pipe(RedactPII(redact_types={"email", "phone", "ip"}))
    # Analyze
    .pipe(counter)
)

# Run pipeline
result = groomer.run(messy_input)

print("Optimized result:")
print(result)
print("\nStatistics:")
print(counter.format_stats())
```

## Full Example

See: [`examples/all_modules_demo.py`](https://github.com/JacobHuang91/prompt-groomer/blob/main/examples/all_modules_demo.py)

```bash
python examples/all_modules_demo.py
```

## Related

- [Pipeline Basics](../user-guide/pipelines.md)
- [All Modules Overview](../modules/overview.md)
